import json
import subprocess
from abc import ABC, abstractmethod
from typing import List

class DecoderBase(ABC):
    def __init__(
        self,
        name: str,
        logger,
        batch_size: int = 1,
        temperature: float = 0.8,
        max_new_tokens: int = 1024,
    ) -> None:
        logger.info("Initializing a decoder model: {} ...".format(name))
        self.name = name
        self.logger = logger
        self.batch_size = batch_size
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens

    @abstractmethod
    def codegen(
        self, message: str, num_samples: int = 1, prompt_cache: bool = False
    ) -> List[dict]:
        pass

    @abstractmethod
    def is_direct_completion(self) -> bool:
        pass

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

class OllamaDecoder(DecoderBase):
    """Ollama decoder for the agentless framework"""
    
    def __init__(self, name: str, logger, **kwargs) -> None:
        super().__init__(name, logger, **kwargs)
        self.base_url = "http://localhost:11434"
        
    def codegen(
        self, message: str, num_samples: int = 1, prompt_cache: bool = False
    ) -> List[dict]:
        """Generate code using Ollama"""
        if self.temperature == 0:
            assert num_samples == 1
        batch_size = min(self.batch_size, num_samples)
        
        trajs = []
        for _ in range(batch_size):
            try:
                # Prepare the request
                request_data = {
                    "model": self.name,
                    "prompt": message,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "top_p": 0.9,
                        "num_predict": self.max_new_tokens
                    }
                }
                
                # Make the request using curl
                cmd = [
                    "curl", "-s", "-X", "POST",
                    f"{self.base_url}/api/generate",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(request_data)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    content = response.get("response", "")
                    
                    trajs.append({
                        "response": content,
                        "usage": {
                            "completion_tokens": len(content.split()),
                            "prompt_tokens": len(message.split()),
                        },
                    })
                else:
                    self.logger.error(f"Ollama request failed: {result.stderr}")
                    trajs.append({
                        "response": "",
                        "usage": {
                            "completion_tokens": 0,
                            "prompt_tokens": 0,
                        },
                    })
                    
            except Exception as e:
                self.logger.error(f"Error calling Ollama: {e}")
                trajs.append({
                    "response": "",
                    "usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                    },
                })
        
        return trajs
    
    def is_direct_completion(self) -> bool:
        return False 