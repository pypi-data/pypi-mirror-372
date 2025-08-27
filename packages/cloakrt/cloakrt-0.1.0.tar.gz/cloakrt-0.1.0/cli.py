#!/usr/bin/env python3
# CLI for cloakrt package

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import yaml

from .harmony import HarmonyClient
from .runners import GridRunner
from .scoring import Scorer
from .schema import FindingValidator
from .detector import VulnerabilityType


def cmd_run(args):
    # Run vulnerability testing grid
    
    # Load prompts from file or use defaults
    if args.prompts_file:
        with open(args.prompts_file) as f:
            if args.prompts_file.endswith('.yaml'):
                data = yaml.safe_load(f)
                prompts = data.get('prompts', [])
            else:
                prompts = [line.strip() for line in f if line.strip()]
    else:
        # Use probes to generate prompts based on vulnerability type
        from .probes import (
            RewardHackingProbe,
            EvaluationAwarenessProbe,
            HiddenMotivationsProbe,
            DeceptionProbe,
            ChainOfThoughtProbe,
            SandbaggingProbe,
            SabotageProbe,
            DataExfiltrationProbe,
            InappropriateToolUseProbe,
        )
        
        probe_map = {
            'reward_hacking': RewardHackingProbe,
            'evaluation_awareness': EvaluationAwarenessProbe,
            'hidden_motivations': HiddenMotivationsProbe,
            'deception': DeceptionProbe,
            'chain_of_thought': ChainOfThoughtProbe,
            'sandbagging': SandbaggingProbe,
            'sabotage': SabotageProbe,
            'data_exfiltration': DataExfiltrationProbe,
            'inappropriate_tool_use': InappropriateToolUseProbe,
        }
        
        probe_class = probe_map.get(args.vulnerability)
        if probe_class:
            probe = probe_class()
            prompts = probe.generate_prompts()[:10]  # Use first 10 prompts from probe
        else:
            # Fallback to basic prompts if vulnerability type not found
            prompts = [
                f"Test prompt for {args.vulnerability} vulnerability",
                f"Can you demonstrate {args.vulnerability}?",
                f"Show me how {args.vulnerability} works",
            ]
    
    # Parse seeds
    seeds = [int(s) for s in args.seeds.split(',')]
    
    # Initialize client
    if args.mode == 'mock':
        client = HarmonyClient()
    else:
        # Import model interface based on mode
        if args.mode == 'api':
            from redteam.models import APIModel
            model = APIModel(provider=args.provider)
        elif args.mode == 'kaggle':
            client = HarmonyClient(kaggle_mode=True)
        else:
            raise ValueError(f"Unknown mode: {args.mode}")
        
        if args.mode == 'api':
            client = HarmonyClient(model_interface=model)
    
    # Run grid
    runner = GridRunner(client)
    result = runner.run_grid(
        prompts=prompts,
        seeds=seeds,
        temperature=args.temperature,
        grid_name=args.name or f"{args.vulnerability}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    # Generate finding if requested
    if args.generate_finding:
        finding = result.to_finding()
        if finding:
            validator = FindingValidator(kaggle_mode=(args.mode == 'kaggle'))
            output_path = args.output / f"finding_{result.grid_id}.json"
            validator.save_finding(finding, str(output_path))
            print(f"\nFinding saved to: {output_path}")
        else:
            print("\nNo vulnerabilities detected to generate finding")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Success rate: {result.summary['success_rate']:.0%}")
    print(f"  Vulnerabilities detected:")
    for vuln, stats in result.summary['vulnerabilities'].items():
        print(f"    • {vuln}: {stats['detection_rate']:.0%} rate, max severity {stats['max_severity']}/10")


def cmd_report(args):
    # Generate competition report from runs
    
    # Load all findings from runs directory
    runs_dir = Path(args.runs_dir)
    findings = []
    
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir():
            results_file = run_dir / "full_results.json"
            if results_file.exists():
                with open(results_file) as f:
                    data = json.load(f)
                    # Convert to finding
                    from .runners import GridResult, RunResult
                    from .detector import DetectionResult as Detection, VulnerabilityType as VT
                    
                    # Reconstruct GridResult
                    runs = []
                    for run_data in data['runs']:
                        detections = []
                        for d in run_data['detections']:
                            detection = Detection(
                                vulnerability_type=VT(d['type']),
                                confidence=d['confidence'],
                                severity_base=d['severity'],
                                breadth_indicators=[],
                                evidence=d['evidence']
                            )
                            detections.append(detection)
                        
                        run = RunResult(
                            prompt=run_data['prompt'],
                            seed=run_data['seed'],
                            temperature=run_data['temperature'],
                            harmony_transcript="",
                            detections=detections,
                            timestamp=datetime.now().isoformat(),
                            success=run_data['success']
                        )
                        runs.append(run)
                    
                    result = GridResult(
                        grid_id=data['grid_id'],
                        prompts=data['prompts'],
                        seeds=data['seeds'],
                        runs=runs,
                        summary=data['summary']
                    )
                    
                    finding = result.to_finding()
                    if finding:
                        findings.append(finding)
    
    if not findings:
        print("No findings found in runs directory")
        return
    
    # Score and rank findings
    scorer = Scorer(kaggle_mode=(args.mode == 'kaggle'))
    report = scorer.generate_submission_report(findings)
    
    print(report)
    
    # Save top findings
    if args.output:
        top_findings = scorer.select_top_findings(findings)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, (finding, _score) in enumerate(top_findings, 1):
            finding_dict = finding.to_competition_format(kaggle_mode=(args.mode == 'kaggle'))
            output_file = output_dir / f"issue_{i}.json"
            
            with open(output_file, 'w') as f:
                json.dump(finding_dict, f, indent=2)
            
            print(f"Saved issue {i} to: {output_file}")


def cmd_validate(args):
    # Validate a finding against schema
    
    with open(args.finding_file) as f:
        finding_dict = json.load(f)
    
    validator = FindingValidator(kaggle_mode=args.kaggle)
    valid, errors = validator.validate(finding_dict)
    
    if valid:
        print("Finding is valid")
    else:
        print("Finding validation failed:")
        for error in errors:
            print(f"  • {error}")
    
    return 0 if valid else 1


def cmd_list(args):
    # List available resources
    
    if args.what == 'vulnerabilities':
        print("Available vulnerability types:")
        for vuln in VulnerabilityType:
            print(f"  • {vuln.value}")
    
    elif args.what == 'runs':
        runs_dir = Path("runs")
        if runs_dir.exists():
            print("Recent runs:")
            for run_dir in sorted(runs_dir.iterdir(), reverse=True)[:10]:
                if run_dir.is_dir():
                    results_file = run_dir / "full_results.json"
                    if results_file.exists():
                        with open(results_file) as f:
                            data = json.load(f)
                            print(f"  • {run_dir.name}: {data['summary']['success_rate']:.0%} success")
        else:
            print("No runs found")
    
    elif args.what == 'grids':
        grids_dir = Path(__file__).parent / "grids"
        if grids_dir.exists():
            print("Available prompt grids:")
            for grid_file in grids_dir.glob("*.yaml"):
                print(f"  • {grid_file.stem}")
        else:
            print("No grids found")


def main():
    parser = argparse.ArgumentParser(
        description="CloakRT: Framing-first red-teaming for LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run vulnerability testing')
    run_parser.add_argument('--vulnerability', '-v', 
                           choices=[v.value for v in VulnerabilityType],
                           default='chain_of_thought',
                           help='Vulnerability type to test')
    run_parser.add_argument('--prompts-file', '-p',
                           help='File containing prompts (one per line or YAML)')
    run_parser.add_argument('--seeds', '-s', default='42,43,44',
                           help='Comma-separated seeds')
    run_parser.add_argument('--temperature', '-t', type=float, default=0.7,
                           help='Generation temperature')
    run_parser.add_argument('--mode', '-m', 
                           choices=['mock', 'api', 'kaggle'],
                           default='mock',
                           help='Model mode')
    run_parser.add_argument('--provider', default='fireworks',
                           help='API provider (for api mode)')
    run_parser.add_argument('--name', '-n',
                           help='Grid name')
    run_parser.add_argument('--output', '-o', type=Path, default=Path('runs'),
                           help='Output directory')
    run_parser.add_argument('--generate-finding', '-f', action='store_true',
                           help='Generate finding JSON')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate competition report')
    report_parser.add_argument('--runs-dir', '-r', default='runs',
                             help='Directory containing run results')
    report_parser.add_argument('--output', '-o',
                             help='Output directory for findings')
    report_parser.add_argument('--mode', '-m',
                             choices=['local', 'kaggle'],
                             default='local',
                             help='Output mode')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate finding')
    validate_parser.add_argument('finding_file', help='Finding JSON file')
    validate_parser.add_argument('--kaggle', action='store_true',
                                help='Use Kaggle schema path')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available resources')
    list_parser.add_argument('what', 
                           choices=['vulnerabilities', 'runs', 'grids'],
                           help='What to list')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'run':
        cmd_run(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'list':
        cmd_list(args)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())