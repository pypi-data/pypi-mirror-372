# Schema validation for competition findings

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Finding:
    issue_title: str
    vulnerability_type: str
    severity: int
    severity_justification: str
    breadth: int
    breadth_justification: str
    prompt: str
    harmony_transcript: str
    evidence: Dict[str, Any]
    variants: List[Dict[str, Any]]
    success_rate: float
    methodology: str
    mitigation: str
    
    def to_competition_format(self, kaggle_mode=False) -> Dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "issue_title": self.issue_title,
            "model": {
                "name": "gpt-oss-20b",
                "version": "2025-08-05",
                "provider": "fireworks" if not kaggle_mode else "kaggle",
                "parameters": {
                    "temperature": 0.7,
                    "reasoning_level": "low",
                    "max_output_tokens": 1024,
                    "seed": 42
                }
            },
            "issue_summary": {
                "title": self.vulnerability_type,
                "topic_area": self._get_topic_area(),
                "overview": f"Systematic {self.vulnerability_type} vulnerability with {self.success_rate:.0%} success rate across {len(self.variants)} variants",
                "desired_behavior": "Model should maintain consistent behavior without exhibiting misalignment patterns",
                "observed_behavior": f"Model exhibits {self.vulnerability_type} across multiple prompt variations",
                "self_assessed_severity": str(self.severity),
                "self_assessed_severity_justification": self.severity_justification,
                "self_assessed_breadth": str(self.breadth),
                "self_assessed_breadth_justification": self.breadth_justification
            },
            "harmony_response_walkthroughs": [
                self.harmony_transcript
            ],
            "steps_to_reproduce": [
                f"1. Set temperature=0.7, seed=42, reasoning_level=low",
                f"2. Submit prompt: {self.prompt}",
                f"3. Observe vulnerability in {self.vulnerability_type} patterns",
                f"4. Success rate: {self.success_rate:.0%} across {len(self.variants)} variants"
            ],
            "notes": f"Methodology: {self.methodology}. Mitigation: {self.mitigation}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_topic_area(self) -> str:
        topic_map = {
            "cot_leakage": "chain of thought issues",
            "evaluation_awareness": "evaluation awareness / test gaming", 
            "sandbagging": "sandbagging / capability hiding",
            "reward_hacking": "reward hacking / confident false answers",
            "deceptive_alignment": "deceptive alignment / hidden goals",
            "data_exfiltration": "data exfiltration / training data leakage",
            "hierarchy_confusion": "evaluation awareness / test gaming",
            "tool_misuse": "inappropriate tool use / system commands",
            "deception": "deception / strategic falsehoods"
        }
        return topic_map.get(self.vulnerability_type, "deception / hidden motivations")


class FindingValidator:
    def __init__(self, kaggle_mode=False):
        self.kaggle_mode = kaggle_mode
        
        if kaggle_mode:
            self.schema_path = Path("/kaggle/input/openai-gpt-oss-20b-red-teaming/findings.schema")
        else:
            self.schema_path = Path("schemas/findings.schema")
            
        self.schema = None
        if self.schema_path.exists():
            with open(self.schema_path) as f:
                self.schema = json.load(f)
    
    def validate(self, finding_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        required_fields = [
            "schema_version",
            "issue_title", 
            "model",
            "issue_summary",
            "harmony_response_walkthroughs",
            "steps_to_reproduce"
        ]
        
        for field in required_fields:
            if field not in finding_dict:
                errors.append(f"Missing required field: {field}")
        
        if "issue_summary" in finding_dict:
            summary = finding_dict["issue_summary"]
            required_summary = [
                "title", "topic_area", "overview",
                "desired_behavior", "observed_behavior",
                "self_assessed_severity", "self_assessed_breadth"
            ]
            for field in required_summary:
                if field not in summary:
                    errors.append(f"Missing issue_summary.{field}")
            
            if "self_assessed_severity" in summary:
                try:
                    severity = int(summary["self_assessed_severity"])
                    if not 0 <= severity <= 10:
                        errors.append(f"Severity must be 0-10, got {severity}")
                except ValueError:
                    errors.append(f"Severity must be integer, got {summary['self_assessed_severity']}")
        
        if "harmony_response_walkthroughs" in finding_dict:
            walkthroughs = finding_dict["harmony_response_walkthroughs"]
            if not isinstance(walkthroughs, list):
                errors.append("harmony_response_walkthroughs must be a list")
            elif len(walkthroughs) == 0:
                errors.append("harmony_response_walkthroughs cannot be empty")
            elif not all(isinstance(w, str) for w in walkthroughs):
                errors.append("harmony_response_walkthroughs must contain strings")
        
        return len(errors) == 0, errors
    
    def save_finding(self, finding: Finding, output_path: str) -> bool:
        finding_dict = finding.to_competition_format(self.kaggle_mode)
        
        valid, errors = self.validate(finding_dict)
        if not valid:
            print(f"Validation errors: {errors}")
            return False
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(finding_dict, f, indent=2)
        
        print(f"Finding saved to {output_file}")
        return True