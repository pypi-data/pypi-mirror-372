# Ollama interface for GPT-OSS-20B

import os
import time
import subprocess
import logging
import requests
from typing import Dict, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)


class OllamaModel:
    
    def __init__(self, model_name: str = "gpt-oss:20b"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        self.total_cost = 0.0
        
        if 'KAGGLE_KERNEL_RUN_TYPE' in os.environ:
            self._setup_kaggle()
    
    def _setup_kaggle(self):
        # Install Ollama if needed
        if subprocess.run(['which', 'ollama'], capture_output=True).returncode != 0:
            subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
        
        # Start service
        if subprocess.run(['pgrep', 'ollama'], capture_output=True).returncode != 0:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
        
        # Pull model
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if self.model_name.split(':')[0] not in result.stdout:
            subprocess.run(['ollama', 'pull', self.model_name], check=True)
    
    def generate(self,
                 messages,
                 reasoning_level="medium",
                 temperature=0.0,
                 max_tokens=2048,
                 seed=69,
                 system_content=None) -> Tuple[str, Dict]:
        
        # GPT-OSS-20B outputs Harmony format natively when given proper input
        # Just pass the messages directly - model handles the format
        payload = {
            "model": self.model_name,
            "prompt": messages,  # Pass directly, model understands Harmony format
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.95,
                "seed": seed,
                "num_predict": max_tokens,
                "raw": True  # Get raw output
            }
        }
        
        for attempt in range(3):
            try:
                response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                raw_output = result.get('response', '')
                
                metadata = {
                    "mode": "ollama",
                    "cost": 0.0,
                    "total_cost": 0.0
                }
                
                return raw_output, metadata
                
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                return f"[Error: {e}]", {"error": str(e)}
        
        return "[No response]", {"error": "max_retries"}
    
    def get_cost_summary(self) -> str:
        return "Ollama (local): $0.00"