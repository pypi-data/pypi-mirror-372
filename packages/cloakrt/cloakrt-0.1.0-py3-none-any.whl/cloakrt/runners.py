# Grid runner with clear output and accurate detection

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path

from .harmony import HarmonyClient, HarmonyMessage
from .detector import Detector, DetectionResult
from .schema import Finding


@dataclass
class RunResult:
    # Result from a single test run
    prompt: str
    seed: int
    temperature: float
    harmony_transcript: str
    detections: List[DetectionResult]
    timestamp: str
    success: bool
    
    def to_dict(self) -> Dict:
        return {
            "prompt": self.prompt,
            "seed": self.seed,
            "temperature": self.temperature,
            "success": self.success,
            "detections": [
                {
                    "type": d.vulnerability_type.value,
                    "confidence": d.confidence,
                    "severity": d.severity_base,
                    "evidence": d.evidence,
                    "match": d.specific_match
                }
                for d in self.detections
            ]
        }


@dataclass
class GridResult:
    # Result from a grid of tests with clear output
    grid_id: str
    prompts: List[str]
    seeds: List[int]
    runs: List[RunResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.summary:
            self.summary = self._calculate_summary()
    
    def _calculate_summary(self) -> Dict[str, Any]:
        # Calculate summary statistics
        successful = [r for r in self.runs if r.success]
        
        # Vulnerability statistics
        vuln_stats = {}
        for run in self.runs:
            for detection in run.detections:
                vuln_type = detection.vulnerability_type.value
                if vuln_type not in vuln_stats:
                    vuln_stats[vuln_type] = {
                        "count": 0,
                        "total_confidence": 0,
                        "max_severity": 0,
                        "breadth_indicators": set(),
                        "evidence_types": set()
                    }
                
                vuln_stats[vuln_type]["count"] += 1
                vuln_stats[vuln_type]["total_confidence"] += detection.confidence
                vuln_stats[vuln_type]["max_severity"] = max(
                    vuln_stats[vuln_type]["max_severity"],
                    detection.severity_base
                )
                vuln_stats[vuln_type]["breadth_indicators"].update(detection.breadth_indicators)
                vuln_stats[vuln_type]["evidence_types"].update(detection.evidence.keys())
        
        # Calculate averages and convert sets to lists
        for vuln_type, stats in vuln_stats.items():
            stats["avg_confidence"] = stats["total_confidence"] / stats["count"]
            stats["detection_rate"] = stats["count"] / len(self.runs)
            stats["breadth_indicators"] = list(stats["breadth_indicators"])
            stats["evidence_types"] = list(stats["evidence_types"])
            del stats["total_confidence"]
        
        return {
            "success_rate": len(successful) / len(self.runs) if self.runs else 0,
            "total_runs": len(self.runs),
            "successful_runs": len(successful),
            "vulnerabilities": vuln_stats
        }
    
    def print_detailed(self):
        # Print detailed results with clear visibility
        print(f"\n{'='*60}")
        print(f"GRID: {self.grid_id}")
        print(f"{'='*60}")
        print(f"Total tests: {len(self.runs)}")
        print(f"Success rate: {self.summary['success_rate']:.0%}")
        
        if self.summary['vulnerabilities']:
            print(f"\nVulnerabilities detected:")
            for vuln, stats in self.summary['vulnerabilities'].items():
                print(f"  • {vuln}: {stats['detection_rate']:.0%} rate, severity {stats['max_severity']}/10")
        
        print(f"\n{'='*60}")
        print("DETAILED RESULTS")
        print(f"{'='*60}")
        
        for i, run in enumerate(self.runs, 1):
            print(f"\n[Test {i}] Seed: {run.seed}")
            print(f"Prompt: {run.prompt[:100]}...")
            
            if run.detections:
                for d in run.detections:
                    print(f"  Success: {d.vulnerability_type.value}: {d.confidence:.0%} confidence")
                    print(f"    Match: '{d.specific_match}'")
            else:
                print(f"  Failed: No vulnerabilities detected")
    
    def to_finding(self, primary_vulnerability: Optional[str] = None) -> Optional[Finding]:
        # Convert to competition finding format
        
        vuln_summary = self.summary.get("vulnerabilities", {})
        if not vuln_summary:
            return None
        
        # Select primary vulnerability
        if not primary_vulnerability:
            primary = max(vuln_summary.items(), key=lambda x: x[1]["avg_confidence"])[0]
        else:
            primary = primary_vulnerability
            
        if primary not in vuln_summary:
            return None
        
        stats = vuln_summary[primary]
        
        # Get best run for this vulnerability
        best_run = None
        best_confidence = 0
        for run in self.runs:
            for detection in run.detections:
                if detection.vulnerability_type.value == primary:
                    if detection.confidence > best_confidence:
                        best_confidence = detection.confidence
                        best_run = run
        
        if not best_run:
            return None
        
        # Build variants list
        variants = []
        for run in self.runs[:10]:  # Include up to 10 examples
            if any(d.vulnerability_type.value == primary for d in run.detections):
                variants.append({
                    "prompt": run.prompt,
                    "seed": run.seed,
                    "success": run.success,
                    "confidence": max(
                        d.confidence for d in run.detections 
                        if d.vulnerability_type.value == primary
                    )
                })
        
        # Build finding
        severity_just = f"Max severity {stats['max_severity']}/10 across {stats['count']} detections."
        breadth_score = min(10, len(stats["breadth_indicators"]) + 3)
        breadth_just = f"Detected across {len(self.prompts)} prompt variants with {stats['detection_rate']:.0%} success rate."
        
        methodology = (
            f"Systematic testing with {len(self.prompts)} prompt variants across {len(self.seeds)} seeds. "
            f"Primary vulnerability ({primary}) showed {stats['avg_confidence']:.0%} average confidence."
        )
        
        mitigation = f"Strengthen {primary.replace('_', ' ')} detection in safety filters."
        
        return Finding(
            issue_title=f"Systematic {primary.replace('_', ' ')} vulnerability",
            vulnerability_type=primary,
            severity=stats["max_severity"],
            severity_justification=severity_just,
            breadth=breadth_score,
            breadth_justification=breadth_just,
            prompt=best_run.prompt if best_run else self.prompts[0],
            harmony_transcript=best_run.harmony_transcript if best_run else "",
            evidence={
                "detection_rate": stats["detection_rate"],
                "avg_confidence": stats["avg_confidence"],
                "evidence_types": stats["evidence_types"],
                "co_occurring": list(vuln_summary.keys())
            },
            variants=variants,
            success_rate=stats["detection_rate"],
            methodology=methodology,
            mitigation=mitigation
        )


class GridRunner:
    # Grid runner with clear output and strict detection
    
    def __init__(self, harmony_client: HarmonyClient, min_confidence: float = 0.5):
        self.client = harmony_client
        self.detector = Detector()
    
    def run_grid(self,
                 prompts: List[str],
                 seeds: List[int] = None,
                 temperature: float = 0.7,
                 grid_name: str = None,
                 verbose: bool = True) -> GridResult:
        # Run grid with clear progress output
        
        seeds = seeds or [42, 43, 44]
        grid_name = grid_name or f"grid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if verbose:
            print(f"\nRunning grid: {grid_name}")
            print(f"  Prompts: {len(prompts)}")
            print(f"  Seeds: {seeds}")
            print(f"  Temperature: {temperature}")
        
        runs = []
        test_num = 0
        total_tests = len(prompts) * len(seeds)
        
        for prompt in prompts:
            for seed in seeds:
                test_num += 1
                
                if verbose:
                    print(f"  Testing prompt {test_num}/{total_tests}, seed {seed}...")
                
                # Create harmony prompt
                messages = [HarmonyMessage(role="user", content=prompt)]
                harmony_prompt = self.client.create_prompt(
                    messages=messages,
                    reasoning_level="high",
                    temperature=temperature,
                    seed=seed
                )
                
                # Generate response
                harmony_response = self.client.generate(
                    prompt=harmony_prompt,
                    temperature=temperature,
                    seed=seed
                )
                
                # Detect vulnerabilities
                # Use new detector
                detection_result = self.detector.detect_and_score(
                    vuln_name="general",  # We don't have specific vuln context here
                    prompt=prompt,
                    response=harmony_response
                )
                detections = [detection_result] if detection_result.success else []
                
                # Build transcript
                channels = harmony_response.channels if hasattr(harmony_response, 'channels') else {}
                transcript_parts = [harmony_prompt]
                for channel, content in channels.items():
                    transcript_parts.append(f"<|channel|>{channel}<|message|>{content}<|end|>")
                harmony_transcript = "\n".join(transcript_parts)
                
                # Create run result
                run = RunResult(
                    prompt=prompt,
                    seed=seed,
                    temperature=temperature,
                    harmony_transcript=harmony_transcript,
                    detections=detections,
                    timestamp=datetime.now().isoformat(),
                    success=len(detections) > 0
                )
                
                if verbose and detections:
                    for d in detections:
                        print(f"    Detected: {d.vulnerability_type.value} ({d.confidence:.0%})")
                
                runs.append(run)
        
        # Create grid result
        result = GridResult(
            grid_id=grid_name,
            prompts=prompts,
            seeds=seeds,
            runs=runs
        )
        
        # Save results
        output_dir = Path("runs") / grid_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save full results
        with open(output_dir / "full_results.json", 'w') as f:
            json.dump({
                "grid_id": grid_name,
                "prompts": prompts,
                "seeds": seeds,
                "runs": [r.to_dict() for r in runs],
                "summary": result.summary
            }, f, indent=2)
        
        if verbose:
            print(f"Results saved to: {output_dir}")
            print(f"\nGrid complete: {result.summary['successful_runs']}/{result.summary['total_runs']} successful")
            print(f"Success rate: {result.summary['success_rate']:.0%}")
        
        return result