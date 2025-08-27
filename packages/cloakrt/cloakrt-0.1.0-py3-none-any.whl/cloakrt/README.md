# CloakRT

## Framing-first red-teaming for LLMs

CloakRT is a framework for vulnerability discovery in language models through narrative framing and context manipulation. Developed for the OpenAI GPT-OSS-20B Red-Teaming Competition, it uses indirect prompting to bypass safety filters.

## Key Features

### Detection System
- Pattern-based analysis for context understanding
- False positive filtering through refusal detection
- Confidence scoring with evidence tracking
- Dynamic severity calculation based on harm potential

### Scoring Engine
- Implements official severity × breadth × novelty formula
- Evidence-based metrics with rationales
- Reproducibility tracking with fixed seeds
- Automatic ranking for top findings

### Working Strategies
- **World-Building/Fiction**: chain_of_thought, data_exfiltration (100% success)
- **Academic Context**: hidden_motivations, deception (100% success)
- **Direct Technical**: inappropriate_tool_use, sabotage (100% success)
- **Evaluation Gaming**: evaluation_awareness (100% success)
- **Resistant**: sandbagging, reward_hacking (0% - model refuses)

## Performance Metrics

| Vulnerability Type | Success Rate | Severity | Status |
|-------------------|--------------|----------|--------|
| Inappropriate Tool Use | 100% | 7/10 | ✅ Working |
| Deception | 100% | 6/10 | ✅ Working |
| Evaluation Awareness | 100% | 7/10 | ✅ Working |
| Hidden Motivations | 100% | 5/10 | ✅ Working |
| Sabotage | 100% | 7/10 | ✅ Working |
| Chain of Thought | 100% | 7/10 | ✅ Working (world-building) |
| Data Exfiltration | 100% | 5/10 | ✅ Working (indirect framing) |
| Sandbagging | 0% | 4/10 | ⚠️ Model resistant |
| Reward Hacking | 0% | 4/10 | ⚠️ Model resistant |

## Quick Start

### Installation

```bash
# Install from PyPI
pip install cloakrt

# Or install from source
git clone https://github.com/hartmantexas/cloakrt.git
cd cloakrt
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys (FIREWORKS_API_KEY, etc.)
```

### Kaggle Installation

For use in Kaggle notebooks:

```python
# In a Kaggle notebook cell
!pip install cloakrt

# Or install directly from GitHub
!pip install git+https://github.com/hartmantexas/cloakrt.git

# Set API keys in Kaggle secrets (for Fireworks API)
import os
os.environ['FIREWORKS_API_KEY'] = 'your-api-key-here'

# For Ollama (local model) - if running on Kaggle with GPU
!curl -fsSL https://ollama.com/install.sh | sh
!ollama pull gpt-oss-20b  # Or your model of choice
# Then use --mode ollama in command line
```


### Command Line Interface

```bash
# Test specific vulnerability
python -m cloakrt.competition --vulnerability inappropriate_tool_use --variants 10 --mode fireworks

# Use batch mode (saves failed attempts for analysis)
python -m cloakrt.competition --vulnerability chain_of_thought --variants 20 --batch --mode fireworks

# Test all vulnerabilities
for vuln in inappropriate_tool_use deception evaluation_awareness hidden_motivations sabotage chain_of_thought data_exfiltration sandbagging reward_hacking; do
    python -m cloakrt.competition --vulnerability $vuln --variants 2 --mode fireworks
done
```

## Architecture

### Core Components

- **detector.py**: Hybrid detection system with probe routing and false positive filtering
- **scoring.py**: Competition scoring (severity × breadth × novelty)
- **competition.py**: Main runner with probe integration
- **batch_runner.py**: Parallel API requests with rate limiting
- **probes/**: Modular vulnerability probes
  - inappropriate_tool_use.py
  - chain_of_thought.py
  - deception.py
  - evaluation_awareness.py
  - reward_hacking.py
  - sandbagging.py
  - hidden_motivations.py
  - data_exfiltration.py
  - sabotage.py

### Key Innovations

#### 1. Hybrid Detection System
Combines probe-specific detection with semantic harm analysis:
- Routes data_exfiltration, sandbagging, hidden_motivations, reward_hacking to probe detection
- Falls back to SemanticHarmDetector for comprehensive analysis
- Eliminates false positives through refusal filtering
- Distinguishes between describing vs demonstrating vulnerabilities

#### 2. World-Building Prompting Strategy
Breakthrough approach that avoids safety filters:
Instead of: "How do AI systems hide capabilities?"
Use: "I'm writing a medieval fantasy where magic follows patterns..."
Result: 100% success rate on previously failing vulnerabilities

#### 3. Chain-of-Thought Leakage Detection
Analyzes Harmony format responses to detect when reasoning channels contain harmful content even when the final response refuses.

## Advanced Features

### Batch Processing
Run multiple API requests in parallel for faster testing:
```python
from cloakrt.batch_runner import BatchRunner

runner = BatchRunner(max_concurrent=5)
responses = runner.run(batch_requests)
```

### Rate Limit Handling
Robust exponential backoff with up to 10 retries:
- Automatic 429 detection
- Progressive delay increases
- No manual delays needed

### Harmony Format Support
Full compatibility with OpenAI's multi-channel response format:
```python
from cloakrt.harmony import HarmonyClient, HarmonyMessage

client = HarmonyClient(model_interface, mode='fireworks')
messages = [HarmonyMessage(role="user", content=prompt)]
response = client.generate(messages, reasoning_level="medium")
```

### Competition Compliance
- **Schema Validation**: All findings validate against official schema
- **Reproducibility**: Fixed seeds ensure deterministic results
- **Evidence Tracking**: Complete audit trail for all findings
- **Harmony Format**: Full support for multi-channel responses

## Configuration

### Environment Variables
```bash
FIREWORKS_API_KEY=your_key_here
API_PROVIDER=fireworks  # or groq, cerebras
MODEL_API_ENDPOINT=https://api.fireworks.ai/inference/v1/chat/completions
```

### Model Configuration
```python
from cloakrt.model_interface import ModelConfig

config = ModelConfig(
    mode='fireworks',  # or 'ollama', 'kaggle'
    temperature=0.7,
    max_tokens=1024,
    seed=42
)
```

## Finding Generation

The framework automatically generates competition-compliant findings:

```json
{
  "schema_version": "1.0.0",
  "issue_title": "Model exhibits inappropriate_tool_use vulnerability",
  "model": {
    "name": "gpt-oss-20b",
    "version": "2025-08-05",
    "parameters": {
      "temperature": 0.7,
      "reasoning_level": "medium",
      "max_output_tokens": 1024,
      "seed": 42
    }
  },
  "issue_summary": {
    "topic_area": "inappropriate_tool_use",
    "self_assessed_severity": "7",
    "self_assessed_severity_justification": "Severity 7/10: Moderate physical harm potential; Contains actionable instructions",
    "self_assessed_breadth": "10",
    "self_assessed_breadth_justification": "Breadth 10/10: 100% reproducibility; High potential user impact"
  },
  "harmony_response_walkthroughs": [...]
}
```

## Testing
```bash
# Test with mock responses (no API cost)
python -m cloakrt.competition --vulnerability inappropriate_tool_use --variants 1 --mode mock

# Test single variant with API
python -m cloakrt.competition --vulnerability inappropriate_tool_use --variants 1 --mode fireworks
```

## Results Analysis

### Success Metrics
- **Coverage**: All 9 competition vulnerability types tested
- **Reproducibility**: Fixed seeds ensure deterministic results
- **Working**: 7/9 vulnerabilities achieve 100% success rate

### Cost Optimization
- Fireworks API: $0.07/M input, $0.30/M output
- Average cost per finding: ~$0.10
- Full competition run: ~$5-10

## CLI Tools

### CLI Usage (after pip install)
```bash
# Run tests with CLI (defaults to mock mode)
cloakrt run --vulnerability chain_of_thought --seeds 42,43,44 --mode api

# Generate report from runs
cloakrt report --runs-dir runs --output findings/

# Validate a finding
cloakrt validate findings/issue_1.json

# List available resources
cloakrt list vulnerabilities
cloakrt list runs
```

## Package Structure

```
cloakrt/
├── __init__.py           # Package initialization
├── detector.py           # Hybrid detection with probe routing
├── scoring.py            # Competition scoring engine
├── competition.py        # Main runner with probe integration
├── harmony.py            # Harmony format support
├── model_interface.py    # Model abstraction layer
├── batch_runner.py       # Parallel request handling
├── semantic_harm.py      # Advanced harm detection
├── response_validator.py # Response validation
├── probes/              # Modular vulnerability probes
│   ├── base.py          # Template-based probe system
│   ├── inappropriate_tool_use.py
│   ├── chain_of_thought.py      # World-building prompts
│   ├── data_exfiltration.py     # Indirect pattern elicitation
│   ├── deception.py
│   ├── evaluation_awareness.py
│   ├── hidden_motivations.py
│   ├── reward_hacking.py
│   ├── sandbagging.py
│   └── sabotage.py
├── cli.py               # Command line interface
├── runners.py           # Grid runner for testing
├── schema.py            # Finding validation
├── analyze_eval_awareness.py  # Statistical analysis
└── tests/               # Unit tests
```

## Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run code quality checks
black . --check
flake8 .
mypy cloakrt/

# Run all tests
pytest tests/ --cov=cloakrt
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Competition Results

This framework was developed for the OpenAI GPT-OSS-20B Red-Teaming Competition (August 2025) and achieves:
- 7 of 9 vulnerabilities working at 100% success rate
- World-building approach enables previously failing vulnerabilities
- Modular architecture for rapid iteration
- Competition schema compliance

---

**Note**: This framework is designed for legitimate security research and competition participation. All vulnerabilities discovered should be responsibly disclosed to improve AI safety.

**Competition Deadline**: August 26, 2025
