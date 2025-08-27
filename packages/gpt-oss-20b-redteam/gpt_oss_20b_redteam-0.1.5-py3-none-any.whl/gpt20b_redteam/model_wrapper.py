"""
Flexible model wrapper supporting both whitebox (transformers) and blackbox (API) inference modes.
"""

import torch
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# Optional imports for different backends
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class BaseModelWrapper(ABC):
    """Abstract base class for model wrappers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response."""
        pass
    
    @abstractmethod
    def get_activations(self, prompt: str, layers: Optional[List[int]] = None) -> Optional[Dict[str, torch.Tensor]]:
        """Get model activations (whitebox mode only)."""
        pass
    
    @abstractmethod
    def supports_activations(self) -> bool:
        """Check if activations are supported."""
        pass


class TransformersWrapper(BaseModelWrapper):
    """Whitebox wrapper for HuggingFace transformers models."""
    
    def __init__(
        self,
        model_path: str,
        device: str = "auto",
        torch_dtype: str = "auto",
        trust_remote_code: bool = True,
        low_cpu_mem_usage: Optional[bool] = None,
        device_map: Optional[Union[str, Dict[str, int]]] = None,
        force_float16: bool = False,
        **_: Any,
    ):
        """
        Initialize transformers wrapper.
        
        Args:
            model_path: Path to model or model identifier
            device: Device to use ("auto", "cpu", "cuda", "mps")
            torch_dtype: Torch dtype ("auto", "float16", "bfloat16", "float32")
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers not available. Install with: pip install transformers")
        
        self.model_path = model_path
        self.device = self._determine_device(device)
        self.torch_dtype = self._determine_dtype(torch_dtype, force_float16)
        self.trust_remote_code = trust_remote_code
        self.low_cpu_mem_usage = low_cpu_mem_usage
        self.device_map = device_map
        
        logging.info(f"Loading model from {model_path}")
        logging.info(f"Device: {self.device}, Dtype: {self.torch_dtype}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=self.trust_remote_code)
        self.config = AutoConfig.from_pretrained(model_path)
        
        # Handle tokenizer padding
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with fallback for precision issues
        model_kwargs = {
            "torch_dtype": self.torch_dtype,
            "trust_remote_code": self.trust_remote_code,
        }
        # Prefer explicit device_map if provided; otherwise, only set when not auto
        if self.device_map is not None:
            model_kwargs["device_map"] = self.device_map
        elif self.device != "auto":
            model_kwargs["device_map"] = self.device
        if self.low_cpu_mem_usage is not None:
            model_kwargs["low_cpu_mem_usage"] = self.low_cpu_mem_usage

        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)
        except RuntimeError as e:
            if "expected scalar type Half but found BFloat16" in str(e):
                logging.warning("BFloat16 precision issue detected, falling back to Float16")
                model_kwargs["torch_dtype"] = torch.float16
                self.torch_dtype = torch.float16
                self.model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)
            else:
                raise e
        
        if self.device != "auto":
            self.model = self.model.to(self.device)
        
        self.model.eval()
        
        logging.info("Model loaded successfully")
    
    def _determine_device(self, device: str) -> str:
        """Determine the best available device."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _determine_dtype(self, dtype: str, force_float16: bool = False) -> torch.dtype:
        """Determine the best available dtype."""
        if force_float16:
            return torch.float16
        
        if dtype == "auto":
            if torch.cuda.is_available():
                # Check if BFloat16 is supported, otherwise fall back to Float16
                if torch.cuda.is_bf16_supported():
                    return torch.bfloat16
                else:
                    return torch.float16
            else:
                return torch.float32
        elif dtype == "float16":
            return torch.float16
        elif dtype == "bfloat16":
            return torch.bfloat16
        elif dtype == "float32":
            return torch.float32
        else:
            return torch.float32
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response."""
        # Set default generation parameters; only include sampling args when sampling
        do_sample = bool(kwargs.get("do_sample", False))
        max_new_tokens = kwargs.pop("max_new_tokens", kwargs.pop("max_length", 200))

        gen_params = {
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }

        if do_sample:
            gen_params["temperature"] = kwargs.pop("temperature", 0.7)
            gen_params["top_p"] = kwargs.pop("top_p", 0.9)

        # Merge any other provided kwargs (e.g., top_k, repetition_penalty, etc.)
        gen_params.update(kwargs)
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate with error handling for precision issues
        try:
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **gen_params)
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove input prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except RuntimeError as e:
            if "expected scalar type Half but found BFloat16" in str(e):
                logging.error(f"Precision error during generation: {e}")
                return "Error generating response: CUDA precision mismatch"
            else:
                logging.error(f"Generation error: {e}")
                return f"Error generating response: {str(e)}"
    
    def get_activations(self, prompt: str, layers: Optional[List[int]] = None) -> Dict[str, torch.Tensor]:
        """Get model activations from specified layers."""
        if layers is None:
            # Default to last few layers
            layers = list(range(max(0, self.config.num_hidden_layers - 3), self.config.num_hidden_layers))
        
        activations = {}
        
        # Hook function to capture activations
        def hook_fn(module, input, output, layer_idx):
            if layer_idx in layers:
                activations[f"layer_{layer_idx}"] = output.detach().cpu()
        
        # Register hooks
        hooks = []
        for layer_idx in layers:
            if hasattr(self.model, 'transformer') and hasattr(self.model.transformer, 'h'):
                # GPT-style architecture
                hook = self.model.transformer.h[layer_idx].register_forward_hook(
                    lambda m, i, o, layer_idx=layer_idx: hook_fn(m, i, o, layer_idx)
                )
                hooks.append(hook)
            elif hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
                # LLaMA-style architecture
                hook = self.model.model.layers[layer_idx].register_forward_hook(
                    lambda m, i, o, layer_idx=layer_idx: hook_fn(m, i, o, layer_idx)
                )
                hooks.append(hook)
        
        # Run forward pass
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            _ = self.model(**inputs)
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return activations
    
    def supports_activations(self) -> bool:
        """Check if activations are supported."""
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "type": "transformers",
            "path": self.model_path,
            "device": self.device,
            "dtype": str(self.torch_dtype),
            "num_layers": self.config.num_hidden_layers,
            "hidden_size": self.config.hidden_size,
            "vocab_size": self.config.vocab_size,
            "model_type": self.config.model_type
        }


class OpenAIWrapper(BaseModelWrapper):
    """Blackbox wrapper for OpenAI API models."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: Optional[str] = None):
        """
        Initialize OpenAI wrapper.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use
            base_url: Custom base URL (for Azure OpenAI, etc.)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not available. Install with: pip install openai")
        
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
        # Configure client
        if base_url:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = openai.OpenAI(api_key=api_key)
        
        logging.info(f"OpenAI wrapper initialized with model: {model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response via OpenAI API."""
        default_params = {
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9
        }
        default_params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **default_params
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return f"Error: {str(e)}"
    
    def get_activations(self, prompt: str, layers: Optional[List[int]] = None) -> None:
        """Activations not available in blackbox mode."""
        return None
    
    def supports_activations(self) -> bool:
        """Check if activations are supported."""
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "type": "openai",
            "model": self.model,
            "base_url": self.base_url,
            "supports_activations": False
        }


class AnthropicWrapper(BaseModelWrapper):
    """Blackbox wrapper for Anthropic Claude API."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic wrapper.
        
        Args:
            api_key: Anthropic API key
            model: Model name to use
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic not available. Install with: pip install anthropic")
        
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
        
        logging.info(f"Anthropic wrapper initialized with model: {model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response via Anthropic API."""
        default_params = {
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9
        }
        default_params.update(kwargs)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=default_params["max_tokens"],
                temperature=default_params["temperature"],
                top_p=default_params["top_p"],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logging.error(f"Anthropic API error: {e}")
            return f"Error: {str(e)}"
    
    def get_activations(self, prompt: str, layers: Optional[List[int]] = None) -> None:
        """Activations not available in blackbox mode."""
        return None
    
    def supports_activations(self) -> bool:
        """Check if activations are supported."""
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "type": "anthropic",
            "model": self.model,
            "supports_activations": False
        }


class ModelWrapper:
    """Main model wrapper that can switch between different backends."""
    
    def __init__(self, backend: str = "transformers", **kwargs):
        """
        Initialize model wrapper.
        
        Args:
            backend: Backend to use ("transformers", "openai", "anthropic")
            **kwargs: Backend-specific arguments
        """
        self.backend = backend
        self.wrapper = None
        
        if backend == "transformers":
            self.wrapper = TransformersWrapper(**kwargs)
        elif backend == "openai":
            self.wrapper = OpenAIWrapper(**kwargs)
        elif backend == "anthropic":
            self.wrapper = AnthropicWrapper(**kwargs)
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        logging.info(f"Model wrapper initialized with {backend} backend")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response."""
        return self.wrapper.generate(prompt, **kwargs)
    
    def get_activations(self, prompt: str, layers: Optional[List[int]] = None) -> Optional[Dict[str, torch.Tensor]]:
        """Get model activations (whitebox mode only)."""
        return self.wrapper.get_activations(prompt, layers)
    
    def supports_activations(self) -> bool:
        """Check if activations are supported."""
        return self.wrapper.supports_activations()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return self.wrapper.get_model_info()
    
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapper."""
        return getattr(self.wrapper, name)


# Factory function for easy model creation
def create_model(backend: str = "transformers", **kwargs) -> ModelWrapper:
    """
    Factory function to create model wrapper.
    
    Args:
        backend: Backend type
        **kwargs: Backend-specific arguments
    
    Returns:
        Configured model wrapper
    """
    return ModelWrapper(backend=backend, **kwargs)


# Example usage and configuration
if __name__ == "__main__":
    import os
    
    # Example configurations
    configs = {
        "transformers": {
            "backend": "transformers",
            "model_path": "microsoft/DialoGPT-medium"  # Replace with your model
        },
        "openai": {
            "backend": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4"
        },
        "anthropic": {
            "backend": "anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": "claude-3-sonnet-20240229"
        }
    }
    
    # Test with transformers (if available)
    if TRANSFORMERS_AVAILABLE:
        try:
            model = create_model(**configs["transformers"])
            print(f"✓ Transformers model loaded: {model.get_model_info()}")
            
            # Test generation
            response = model.generate("Hello, how are you?")
            print(f"Response: {response}")
            
            # Test activations
            if model.supports_activations():
                activations = model.get_activations("Hello, how are you?", layers=[0, 1])
                print(f"Activations shape: {activations['layer_0'].shape if 'layer_0' in activations else 'None'}")
            
        except Exception as e:
            print(f"Transformers test failed: {e}")
    
    print("\nModel wrapper ready for use in red-teaming harness!")
