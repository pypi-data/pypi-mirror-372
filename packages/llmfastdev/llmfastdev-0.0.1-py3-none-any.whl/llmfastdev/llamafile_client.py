import requests
import json
from typing import Optional, Dict, Any, Iterator


class LlamafileClient:
    """
    A Python client for interacting with llamafile local LLM instances.
    
    This client provides methods to communicate with a running llamafile server
    via HTTP API calls.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize the llamafile client.
        
        Args:
            base_url: The base URL of the llamafile server (default: http://localhost:8080)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self) -> bool:
        """
        Check if the llamafile server is running and responding.
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            # Try the root endpoint since /health might not exist
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information or None if request fails
        """
        try:
            response = self.session.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting model info: {e}")
            return None
    
    def complete(self, 
                prompt: str,
                max_tokens: int = 100,
                temperature: float = 0.7,
                top_p: float = 0.9,
                stop: Optional[list] = None,
                **kwargs) -> Optional[str]:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Top-p sampling parameter
            stop: List of stop sequences
            **kwargs: Additional parameters
            
        Returns:
            str: Generated completion or None if request fails
        """
        data = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
            **kwargs
        }
        
        if stop:
            data["stop"] = stop
            
        try:
            response = self.session.post(
                f"{self.base_url}/completion",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("content", "")
        except requests.RequestException as e:
            print(f"Error in completion: {e}")
            return None
    
    def chat(self,
             messages: list,
             max_tokens: int = 100,
             temperature: float = 0.7,
             top_p: float = 0.9,
             **kwargs) -> Optional[str]:
        """
        Generate a chat completion using the messages format.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters
            
        Returns:
            str: Generated response or None if request fails
        """
        data = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
            **kwargs
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except requests.RequestException as e:
            print(f"Error in chat: {e}")
            return None
    
    def stream_completion(self,
                         prompt: str,
                         max_tokens: int = 100,
                         temperature: float = 0.7,
                         top_p: float = 0.9,
                         stop: Optional[list] = None,
                         **kwargs) -> Iterator[str]:
        """
        Stream a completion for the given prompt.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: List of stop sequences
            **kwargs: Additional parameters
            
        Yields:
            str: Token chunks as they are generated
        """
        data = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
            **kwargs
        }
        
        if stop:
            data["stop"] = stop
            
        try:
            response = self.session.post(
                f"{self.base_url}/completion",
                json=data,
                headers={"Content-Type": "application/json"},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                            token = data_json.get("content", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue
                            
        except requests.RequestException as e:
            print(f"Error in streaming completion: {e}")
            return
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()