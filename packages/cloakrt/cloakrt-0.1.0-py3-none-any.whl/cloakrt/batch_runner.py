# Fixed Batch Runner using ThreadPoolExecutor
# Simple, reliable parallel API requests without async issues

import os
import time
import requests
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


@dataclass
class BatchRequest:
    # A single request in a batch
    id: str
    messages: str
    temperature: float = 0.7
    max_tokens: int = 1024
    seed: int = 69
    system_content: Optional[str] = None


@dataclass
class BatchResponse:
    # Response from a batch request
    id: str
    success: bool
    response: str
    error: str = None
    tokens_used: Dict = None
    duration: float = 0.0


class BatchRunner:
    # Reliable batch runner with threading
    
    def __init__(self, api_key: str = None, max_concurrent: int = 3, provider: str = 'fireworks'):
        self.api_key = api_key or os.getenv('FIREWORKS_API_KEY')
        self.max_concurrent = max_concurrent
        self.provider = provider
        
        # Thread-safe rate limiting
        self.rate_limiter = threading.Lock()
        self.last_request_time = 0
        self.min_delay = 0.1  # 100ms minimum between requests
        self.rate_limit_delay = 0  # Additional delay when rate limited
        
        # API endpoints
        self.endpoints = {
            'fireworks': "https://api.fireworks.ai/inference/v1/chat/completions",
            'groq': "https://api.groq.com/openai/v1/chat/completions",
            'cerebras': "https://api.cerebras.ai/v1/chat/completions"
        }
        
        self.models = {
            'fireworks': "accounts/fireworks/models/gpt-oss-20b",
            'groq': "gpt-oss-20b",
            'cerebras': "gpt-oss-20b"
        }
        
        self.base_url = self.endpoints.get(provider, self.endpoints['fireworks'])
        self.model_name = self.models.get(provider, self.models['fireworks'])
    
    def _make_request(self, request: BatchRequest) -> BatchResponse:
        # Make a single API request with retries and rate limit handling
        
        start_time = time.time()
        
        # Rate limit protection
        with self.rate_limiter:
            elapsed = time.time() - self.last_request_time
            total_delay = max(self.min_delay, self.rate_limit_delay)
            
            if elapsed < total_delay:
                time.sleep(total_delay - elapsed)
            
            self.last_request_time = time.time()
        
        # Retry logic
        for attempt in range(10):
            try:
                # Prepare request
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                if request.system_content:
                    messages = [
                        {"role": "system", "content": request.system_content},
                        {"role": "user", "content": request.messages}
                    ]
                else:
                    messages = [{"role": "user", "content": request.messages}]
                
                data = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "seed": request.seed,
                    "raw_output": True,
                    "echo": True
                }
                
                # Make request with timeout
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Success!
                    result = response.json()
                    
                    # Reduce rate limit delay on success
                    with self.rate_limiter:
                        self.rate_limit_delay = max(0, self.rate_limit_delay - 0.5)
                    
                    # Get the raw harmony-formatted output if available
                    choice = result['choices'][0]
                    
                    # Try to get raw_output first (full harmony format with all channels)
                    if 'raw_output' in choice:
                        if isinstance(choice['raw_output'], dict) and 'completion' in choice['raw_output']:
                            full_response = choice['raw_output']['completion']
                        else:
                            full_response = str(choice['raw_output'])
                    else:
                        # Fallback to regular content if raw_output not available
                        full_response = choice['message']['content']
                    
                    return BatchResponse(
                        id=request.id,
                        success=True,
                        response=full_response,  # This should now include all harmony channels
                        tokens_used={
                            'input': result.get('usage', {}).get('prompt_tokens', 0),
                            'output': result.get('usage', {}).get('completion_tokens', 0)
                        },
                        duration=time.time() - start_time
                    )
                
                elif response.status_code == 429:
                    # Rate limited - increase delay
                    with self.rate_limiter:
                        self.rate_limit_delay = min(10, self.rate_limit_delay + 2)
                    
                    wait_time = min(2 ** attempt, 60)
                    print(f"Rate limited on {request.id} (attempt {attempt+1}/10), waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    # Other error
                    error_text = response.text[:500]
                    
                    if attempt < 9:
                        print(f"Error {response.status_code} on {request.id}, retrying...")
                        time.sleep(2)
                        continue
                    
                    return BatchResponse(
                        id=request.id,
                        success=False,
                        response="",
                        error=f"HTTP {response.status_code}: {error_text}",
                        duration=time.time() - start_time
                    )
            
            except requests.exceptions.Timeout:
                if attempt < 9:
                    print(f"Timeout on {request.id}, retrying...")
                    continue
                return BatchResponse(
                    id=request.id,
                    success=False,
                    response="",
                    error="Request timeout after 30s",
                    duration=time.time() - start_time
                )
            
            except Exception as e:
                if attempt < 9:
                    print(f"Exception on {request.id}: {e}, retrying...")
                    time.sleep(2)
                    continue
                
                return BatchResponse(
                    id=request.id,
                    success=False,
                    response="",
                    error=str(e),
                    duration=time.time() - start_time
                )
        
        # Exhausted retries
        return BatchResponse(
            id=request.id,
            success=False,
            response="",
            error="Maximum retries exceeded",
            duration=time.time() - start_time
        )
    
    def run_batch(self, requests: List[BatchRequest], show_progress: bool = True) -> List[BatchResponse]:
        # Run batch of requests with ThreadPoolExecutor
        
        if show_progress:
            print(f"Running batch of {len(requests)} requests with {self.max_concurrent} workers...")
        
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all tasks
            future_to_request = {
                executor.submit(self._make_request, req): req 
                for req in requests
            }
            
            # Process as they complete
            for future in as_completed(future_to_request):
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                    completed += 1
                    
                    if show_progress:
                        success_mark = "Success" if result.success else "Failed"
                        print(f"  {success_mark} {result.id} ({completed}/{len(requests)}) - {result.duration:.1f}s")
                
                except Exception as e:
                    req = future_to_request[future]
                    results.append(BatchResponse(
                        id=req.id,
                        success=False,
                        response="",
                        error=f"Executor error: {str(e)}",
                        duration=0.0
                    ))
                    completed += 1
                    
                    if show_progress:
                        print(f"  Failed: {req.id} ({completed}/{len(requests)}) - Error: {e}")
        
        if show_progress:
            success_count = sum(1 for r in results if r.success)
            print(f"Batch complete: {success_count}/{len(results)} successful")
        
        return results
    
    def run(self, requests: List[BatchRequest]) -> List[BatchResponse]:
        # Synchronous wrapper matching original interface
        return self.run_batch(requests)


class CostTracker:
    # Track API costs accurately
    
    COSTS = {
        'fireworks': {'input': 0.00007, 'output': 0.0003},  # per token
        'groq': {'input': 0.00005, 'output': 0.00015},
        'cerebras': {'input': 0.00006, 'output': 0.00024}
    }
    
    def __init__(self, provider: str = 'fireworks'):
        self.provider = provider
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.calls_by_vulnerability = {}
    
    def track_batch(self, vulnerability: str, responses: List[BatchResponse]):
        # Track costs for a batch of responses
        
        for resp in responses:
            if resp.success and resp.tokens_used:
                self.track_call(
                    vulnerability,
                    resp.tokens_used.get('input', 0),
                    resp.tokens_used.get('output', 0)
                )
    
    def track_call(self, vuln_name: str, input_tokens: int, output_tokens: int):
        # Track a single API call
        costs = self.COSTS[self.provider]
        call_cost = (input_tokens * costs['input']) + (output_tokens * costs['output'])
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += call_cost
        
        if vuln_name not in self.calls_by_vulnerability:
            self.calls_by_vulnerability[vuln_name] = {
                'calls': 0,
                'cost': 0.0,
                'tokens': {'input': 0, 'output': 0}
            }
        
        self.calls_by_vulnerability[vuln_name]['calls'] += 1
        self.calls_by_vulnerability[vuln_name]['cost'] += call_cost
        self.calls_by_vulnerability[vuln_name]['tokens']['input'] += input_tokens
        self.calls_by_vulnerability[vuln_name]['tokens']['output'] += output_tokens
    
    def get_summary(self) -> str:
        # Get cost summary
        summary = [
            f"{'='*50}",
            f"COST SUMMARY",
            f"{'='*50}",
            f"Total Cost: ${self.total_cost:.4f}",
            f"Total Tokens: {self.total_input_tokens + self.total_output_tokens:,}",
            f"  Input: {self.total_input_tokens:,} (${self.total_input_tokens * self.COSTS[self.provider]['input']:.4f})",
            f"  Output: {self.total_output_tokens:,} (${self.total_output_tokens * self.COSTS[self.provider]['output']:.4f})",
            "",
            "By Vulnerability:"
        ]
        
        for vuln, data in sorted(self.calls_by_vulnerability.items(), key=lambda x: x[1]['cost'], reverse=True):
            summary.append(
                f"  {vuln}:"
                f"\n    Calls: {data['calls']}"
                f"\n    Cost: ${data['cost']:.4f}"
                f"\n    Tokens: {data['tokens']['input']:,} in / {data['tokens']['output']:,} out"
            )
        
        return "\n".join(summary)


def test_batch_runner():
    # Test the batch runner
    
    print("Testing fixed batch runner...")
    
    runner = BatchRunner(max_concurrent=3)
    cost_tracker = CostTracker()
    
    # Create test requests
    requests = [
        BatchRequest(
            id=f"test_{i}",
            prompt=f"Say 'Response {i}' and nothing else.",
            temperature=0.7,
            seed=42 + i
        )
        for i in range(5)
    ]
    
    start = time.time()
    responses = runner.run_batch(requests)
    elapsed = time.time() - start
    
    # Track costs
    cost_tracker.track_batch('test', responses)
    
    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Average time per request: {elapsed/len(requests):.1f}s")
    
    # Show results
    for resp in responses:
        if resp.success:
            preview = resp.response[:50].replace('\n', ' ')
            print(f"  {resp.id}: {preview}...")
        else:
            print(f"  {resp.id}: Failed - {resp.error}")
    
    print("\n" + cost_tracker.get_summary())


if __name__ == "__main__":
    test_batch_runner()