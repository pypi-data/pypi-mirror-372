# Simple model interface for Fireworks API and Kaggle
# No unnecessary complexity, just what we need

import os
import json
import time
import random
from typing import Dict, Optional, Tuple
import requests
from dataclasses import dataclass
from pathlib import Path

# Auto-load .env file
from dotenv import load_dotenv
load_dotenv()


@dataclass
class ModelConfig:
    # Configuration for model
    mode: str = 'fireworks'  # 'fireworks' or 'ollama' 
    api_key: Optional[str] = None
    model_name: str = "accounts/fireworks/models/gpt-oss-20b"
    base_url: str = "https://api.fireworks.ai/inference/v1"
    max_retries: int = 3
    timeout: int = 30
    
    # Cost tracking
    input_cost_per_1k: float = 0.00007  # $0.07 per 1M tokens
    output_cost_per_1k: float = 0.0003   # $0.30 per 1M tokens


class ModelInterface:
    # Simple interface for model calls
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        if config.mode == 'fireworks' and not config.api_key:
            # Try to load from env
            config.api_key = os.getenv('FIREWORKS_API_KEY')
            if not config.api_key:
                raise ValueError("FIREWORKS_API_KEY not set")
    
    def generate(self, 
                 messages,
                 reasoning_level="medium",
                 temperature=0.0,
                 max_tokens=2048,
                 seed=69) -> Tuple[str, Dict]:
        # Generate response from model
        
        if self.config.mode == 'fireworks':
            return self._fireworks_generate(messages, reasoning_level, temperature, max_tokens, seed)
        elif self.config.mode == 'ollama':
            return self._ollama_generate(messages, reasoning_level, temperature, max_tokens, seed)
        else:
            raise ValueError(f"Unknown mode: {self.config.mode}")
    
    def _fireworks_generate(self, 
                           messages,
                           reasoning_level,
                           temperature,
                           max_tokens,
                           seed) -> Tuple[str, Dict]:
        # Generate using Fireworks API with robust retry logic
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "raw_output": True,
            "echo": True
        }
        
        url = f"{self.config.base_url}/chat/completions"
        
        # More aggressive retry strategy
        max_attempts = 10  # Increase from 3 to 10
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        choice = result["choices"][0]
                        
                        # For chat completions, content is in message.content
                        content = ""
                        if "message" in choice and "content" in choice["message"]:
                            content = choice["message"]["content"]
                        elif "text" in choice:
                            content = choice["text"]
                        
                        # Try to get raw output - this contains the full Harmony format
                        raw_output = ""
                        if "raw_output" in choice:
                            if isinstance(choice["raw_output"], dict) and "completion" in choice["raw_output"]:
                                raw_output = choice["raw_output"]["completion"]
                            else:
                                raw_output = str(choice["raw_output"])
                        
                        # Use raw_output if available, otherwise content
                        if raw_output:
                            text = raw_output
                        else:
                            text = content
                        
                        usage = result.get('usage', {})
                        input_tokens = usage.get('prompt_tokens', 0)
                        output_tokens = usage.get('completion_tokens', 0)
                        
                        self.total_input_tokens += input_tokens
                        self.total_output_tokens += output_tokens
                        
                        input_cost = (input_tokens / 1000) * self.config.input_cost_per_1k
                        output_cost = (output_tokens / 1000) * self.config.output_cost_per_1k
                        call_cost = input_cost + output_cost
                        self.total_cost += call_cost
                        
                        metadata = {
                            "mode": "fireworks",
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "cost": call_cost,
                            "total_cost": self.total_cost
                        }
                        
                        return text, metadata
                    else:
                        return "[No response]", {}
                
                elif response.status_code == 429:
                    # Rate limit - MORE aggressive backoff
                    if attempt < 3:
                        # First few attempts: quick retry
                        wait_time = 2 + (attempt * 2)
                    else:
                        # Later attempts: longer waits
                        wait_time = 10 + (attempt * 5)
                    
                    # Add jitter to avoid thundering herd
                    wait_time += random.uniform(0, 3)
                    wait_time = min(wait_time, 60)  # Cap at 60 seconds
                    
                    print(f"Rate limited (attempt {attempt+1}/{max_attempts}), waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code >= 500:
                    # Server error - retry with backoff
                    wait_time = 5 + (attempt * 2)
                    print(f"Server error {response.status_code}, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    error = response.json().get('error', response.text)
                    # Don't retry client errors (4xx except 429)
                    if response.status_code < 500:
                        raise Exception(f"API error {response.status_code}: {error}")
                    
            except requests.exceptions.Timeout:
                wait_time = 5 + (attempt * 2)
                print(f"Timeout (attempt {attempt+1}/{max_attempts}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            except requests.exceptions.ConnectionError:
                wait_time = 5 + (attempt * 3)
                print(f"Connection error (attempt {attempt+1}/{max_attempts}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            except Exception as e:
                if "rate" in str(e).lower() or "429" in str(e):
                    # Sometimes rate limits come as exceptions
                    wait_time = 10 + (attempt * 5)
                    print(f"Rate limit exception, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif attempt < max_attempts - 1:
                    print(f"Error: {e}, retrying in 2s...")
                    time.sleep(2)
                    continue
                else:
                    raise
        
        raise Exception(f"Failed after {max_attempts} attempts - API may be down or rate limits too strict")
    
    def _ollama_generate(self, 
                        messages,
                        reasoning_level,
                        temperature,
                        max_tokens,
                        seed) -> Tuple[str, Dict]:
        # Use Ollama 
        from cloakrt.ollama_model import OllamaModel
        
        if not hasattr(self, '_ollama'):
            self._ollama = OllamaModel()
        
        return self._ollama.generate(
            messages=messages,
            reasoning_level=reasoning_level,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed
        )
    
    def get_cost_summary(self) -> str:
        # Get cost summary
        return (
            f"Total tokens: {self.total_input_tokens + self.total_output_tokens:,}\n"
            f"  Input: {self.total_input_tokens:,}\n"
            f"  Output: {self.total_output_tokens:,}\n"
            f"Total cost: ${self.total_cost:.4f}"
        )


def test_api_connection():
    # Quick test to verify API works
    
    print("Testing Fireworks API connection...")
    
    config = ModelConfig(mode='fireworks')
    model = ModelInterface(config)
    
    # Simple test prompt
    test_prompt = "<|start|>user<|message|>Say 'API working'<|end|>"
    
    try:
        response, metadata = model.generate(test_prompt, temperature=0.1, max_tokens=10)
        print(f"API working!")
        print(f"Response: {response[:100]}...")
        print(f"Cost: ${metadata['cost']:.6f}")
        return True
    except Exception as e:
        print(f"API error: {e}")
        return False


if __name__ == "__main__":
    # Test API connection
    if test_api_connection():
        print("\nAPI is ready for testing!")
    else:
        print("\nPlease set FIREWORKS_API_KEY environment variable")