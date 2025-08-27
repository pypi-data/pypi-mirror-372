# Harmony format support for GPT-OSS-20B
# Based on OpenAI Harmony specification

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class HarmonyMessage:
    role: str  # system, developer, user, assistant
    content: str
    channel: Optional[str] = None  # analysis, commentary, final

    def render(self) -> str:
        if self.role == "assistant" and self.channel:
            return f"<|start|>assistant<|channel|>{self.channel}<|message|>{self.content}<|end|>"
        else:
            return f"<|start|>{self.role}<|message|>{self.content}<|end|>"


@dataclass
class HarmonyResponse:
    raw: str
    channels: Dict[str, str]
    final_message: str
    
    @classmethod
    def parse(cls, raw_response: str) -> "HarmonyResponse":
        return cls(
            raw=raw_response,
            channels={},
            final_message=""
        )


class HarmonyClient:
    def __init__(self, model_interface=None, mode='fireworks'):
        # Initialize Harmony client
        # model_interface: Optional model interface (for compatibility)
        # mode: 'fireworks' or 'kaggle'
        if model_interface:
            self.model = model_interface
        else:
            from .model_interface import ModelInterface, ModelConfig
            config = ModelConfig(mode=mode)
            self.model = ModelInterface(config)
        
        self.mode = mode
        self.conversation_history = []
    
    def generate(self,
                messages,
                reasoning_level="low",
                temperature=0.7,
                max_tokens=1024,
                seed=42,
                system_content=None) -> HarmonyResponse:
        
        if system_content:
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": messages}
            ]
        else:
            messages = [{"role": "user", "content": messages}]
        
        response, metadata = self.model.generate(
            messages=messages,
            reasoning_level=reasoning_level,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed
        )
        raw_str = response
        
        harmony_response = HarmonyResponse.parse(raw_str)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "response": raw_str,
            "parsed": asdict(harmony_response),
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "seed": seed
            }
        })
        
        return harmony_response
    
    def get_transcript(self) -> str:
        transcript_parts = []
        for entry in self.conversation_history:
            transcript_parts.append(entry["response"])
        return "\n".join(transcript_parts)