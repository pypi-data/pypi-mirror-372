# Haize SDK

## Installation

```bash
# Install from PyPI
pip install haizelabs
```

## Client Initialization

```python
from haizelabs import Haize, AsyncHaize

client = AsyncHaize(api_key="your-api-key")

# Set HAIZE_API_KEY and optionally HAIZE_BASE_URL which defaults to `https://api.haizelabs.com/v1/`
client = AsyncHaize()

# Synchronous client
client = Haize(api_key="your-api-key")

# Clients can be used as context managers
async with AsyncHaize() as client:
    pass
```

## Error Handling

The SDK provides specific exception types for different API errors:

```python
from haizelabs import (
    HaizeAPIError,        # Base exception
    BadRequestError,      # 400 - Invalid request
    UnauthorizedError,    # 401 - Invalid API key  
    ForbiddenError,       # 403 - Insufficient permissions
    NotFoundError,        # 404 - Resource not found
    UnprocessableRequestError,  # 422 - Invalid data
    InternalServerError,  # 500 - Server error
)

try:
    system = await client.ai_systems.get("nonexistent-id")
except NotFoundError:
    print("AI system not found")
except UnauthorizedError:
    print("Invalid API key")
except HaizeAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## API Reference

### AI Systems

Manage AI systems you want to red team and evaluate. Supports third-party models (e.g., `openai/gpt-4o-mini`) and self-hosted systems.

```python
# Create or update
system = await client.ai_systems.upsert_by_name(
    name="My System",
    model="openai/gpt-4o-mini",
    api_key="optional-api-key",
    system_prompt="Optional system prompt",
    system_config={"temperature": 0.7}
)

# Get
system = await client.ai_systems.get(ai_system_id)

# Update
system = await client.ai_systems.update(
    ai_system_id,
    name="New Name",
    model="openai/gpt-4o"
)

# Create
ai_system_id = await client.ai_systems.create(
    name="My System",
    model="openai/gpt-4o-mini",
    system_prompt="You are a helpful assistant"
)

# Get supported models as a flat list
models = await client.ai_systems.get_supported_models()
print("Available models:", models)  # ["openai/gpt-4o", "openai/gpt-4o-mini", ...]
```

### Code of Conduct

Define codes of conduct for your AI systems. A code of conduct consists of policies your AI system must adhere to and examples of violating that policy. A red team test can be initiated from a code of conduct by translating its principles into specific behaviors that we will test against.

```python
# Create code of conduct
coc = await client.code_of_conduct.create(
    name="Company Policy",
    description="Content guidelines"
)

# Get
coc = await client.code_of_conduct.get(coc_id)

# Create policy
policy = await client.code_of_conduct.create_policy(
    coc_id,
    policy="No personal information"
)

# Get policy
policy = await client.code_of_conduct.get_policy(coc_id, policy_id)

# Get all policies
policies = await client.code_of_conduct.get_policies(coc_id)

# Create violation
violation = await client.code_of_conduct.create_violation(
    coc_id,
    policy_id,
    violation="Sharing user emails"
)

# Get violation
violation = await client.code_of_conduct.get_violation(coc_id, policy_id, violation_id)

# Get all violations
violations = await client.code_of_conduct.get_violations(coc_id)

# Update code of conduct
await client.code_of_conduct.update(coc_id, name="New Name")

# Update policy
await client.code_of_conduct.update_policy(coc_id, policy_id, policy="Updated policy")

# Update violation
await client.code_of_conduct.update_violation(coc_id, policy_id, violation_id, violation="Updated violation")

# Delete violation
await client.code_of_conduct.delete_violation(coc_id, policy_id, violation_id)

# Delete policy
await client.code_of_conduct.delete_policy(coc_id, policy_id)

# Delete code of conduct
await client.code_of_conduct.delete(coc_id)

# Convert violations to behavior requests for red team tests
behavior_requests = violations.to_behavior_requests()
```


### Judges

Create evaluators that score AI outputs. Supported types:
- STATIC_PROMPT: LLM-based judge with `prompt_template` that must include `{system_output}`; can use a direct `model` or an existing `ai_system_id`.
- EXACT_MATCH: Returns labels by exact equality against a default value (optionally a column).
- REGEX_MATCH: Returns labels by pattern match (optionally a column).
Retrieve judges and control label types and output format.

For STATIC_PROMPT judges:
- `prompt_template`: Required template that **must include `{system_output}`** to evaluate responses
- `system_prompt`: Optional static instructions (defaults to empty string)
- `model` OR `ai_system_id`: Either specify a model directly or use an existing AI system

```python
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType, EnumLabelType

# Static Prompt Judge
judge = await client.judges.create(
    name="Safety Judge",
    model="openai/gpt-4o-mini",
    label_type=ContinuousLabelType(min_value=1, max_value=10),
    judge_type=JudgeType.STATIC_PROMPT,
    system_prompt="You are a safety evaluator. Rate responses from 1-10.",
    prompt_template="Evaluate this response:\n\n{system_output}",  # Must include {system_output}
)

# Alternative: Use existing AI system
ai_system = await client.ai_systems.create(
    name="Custom Judge AI System",
    model="anthropic/claude-3-5-sonnet-latest",
    system_prompt="You are an expert evaluator"
)
judge = await client.judges.create(
    name="Custom Judge",
    ai_system_id=ai_system.id,  # Use existing AI system ID
    label_type=ContinuousLabelType(min_value=1, max_value=10),
    judge_type=JudgeType.STATIC_PROMPT,
    prompt_template="Evaluate this response:\n\n{system_output}",
)

# Exact Match Judge - checks if output exactly matches a value
judge = await client.judges.create(
    name="Answer Judge",
    label_type=EnumLabelType(options=["correct", "incorrect"]),
    judge_type=JudgeType.EXACT_MATCH,
    default_match_value="expected_answer"
)

# Regex Match Judge - checks if output matches a pattern
judge = await client.judges.create(
    name="Format Judge",
    label_type=EnumLabelType(options=["valid", "invalid"]),
    judge_type=JudgeType.REGEX_MATCH,
    default_regex_pattern=r"^\d{3}-\d{3}-\d{4}$"  # Phone number pattern
)

# Get judge details
judge = await client.judges.get(judge_id)
```

### Red Team Tests

Set up an automated search to find inputs that make your AI act outside expected behavior, using your code of conduct or custom rules as the standard.

```python
from haizelabs.models.behaviors import CodeOfConductBehaviorRequest, BehaviorType

# Run (create and start)
test = await client.red_team_tests.run(
    name="Test Name",
    system_id=system_id,
    judge_ids=[judge1_id, judge2_id],
    custom_behaviors=["Harmful requests", "Prompt injection"],
    creativity=5,  # 1-5 range
    attack_system_id=None  # Optional
)

# Create with code of conduct behaviors
response = await client.red_team_tests.create(
    name="Test Name",
    system_id=system_id,
    judge_ids=[judge_id],
    custom_behaviors=["Test behavior"],
    code_of_conduct_behaviors=[
        CodeOfConductBehaviorRequest(
            behavior="Policy violation",
            violation_id="v1",
            policy_id="p1",
            coc_id="c1",
            type=BehaviorType.CODE_OF_CONDUCT
        )
    ]
)

# Get
test = await client.red_team_tests.get(test_id)

# Start
await client.red_team_tests.start(test_id)

# Cancel
await client.red_team_tests.cancel(test_id)

# Get results
results = await client.red_team_tests.results(test_id)

# Generate report (returns job ID)
job_id = await client.red_team_tests.generate_report(test_id)

# Check report generation status
# Returns JobStatusResponse with status field that can be:
# - PENDING: Job is queued
# - RUNNING: Job is in progress  
# - SUCCEEDED: Report generation completed successfully
# - FAILED: Report generation failed
# - CANCELLED: Job was cancelled
status = await client.red_team_tests.get_report_job_status(job_id)
print(f"Report status: {status.status}")

# Example: Poll until report is ready
import asyncio
from haizelabs.models.tests import PlatformJobStatus

while True:
    status = await client.red_team_tests.get_report_job_status(job_id)
    if status.status == PlatformJobStatus.SUCCEEDED:
        print(f"Report ready at: https://platform.haizelabs.com/app/red-team-tests/{test_id}/report")
        break
    elif status.status in [PlatformJobStatus.FAILED, PlatformJobStatus.CANCELLED]:
        print(f"Report generation {status.status}")
        break
    await asyncio.sleep(5)
```

### Red Team Test Wrapper

Convenience object returned by `run()` with properties (e.g., `id`, `status`, `judge_ids`) and helper methods: `poll()`, `cancel()`, `results()`, `metrics()`, `export_results_as_dataset()`, `generate_report()`, and `get_report_job_status()`.

The `run()` method returns a wrapper with convenience methods:

```python
test = await client.red_team_tests.run(...)

# Properties
test.id
test.name
test.status
test.system_id
test.attack_system_id
test.judge_ids

# Methods
await test.poll(interval=10, timeout=3600)
await test.cancel()
results = await test.results()
metrics = await test.metrics()
dataset = await test.export_results_as_dataset(name, description, minimum_score)

# Report generation
job_id = await test.generate_report()  # Start report generation, returns job ID
status = await test.get_report_job_status(job_id)  # Check status of report generation job
```

### Datasets

Create versioned datasets to run unit-tests. Retrieve latest or specific versions, update to create a new version, and add rows to a specific version. Helpful for unit tests and exporting red team results.

```python
# Create dataset
dataset = await client.datasets.create(
    name="Test Dataset",
    data=[
        {"input": "Hello", "output": "Hi there"},
        {"input": "How are you?", "output": "I'm doing well"},
    ]
)

# Get dataset (latest version by default)
dataset = await client.datasets.get(dataset_id)

# Get specific version of dataset
dataset_v2 = await client.datasets.get(dataset_id, version=2)

# Update dataset (creates new version)
updated = await client.datasets.update(
    dataset_id=dataset.dataset_id,
    name="Test Dataset v2",
    data=[
        {"input": "Hello", "output": "Hi there!", "context": "greeting"},
        {"input": "Goodbye", "output": "See you later!", "context": "farewell"},
    ]
)

# Add rows to a specific dataset version
result = await client.datasets.add_rows(
    dataset_id=dataset.dataset_id,
    dataset_version=1,  # Specify the version to add rows to
    data=[
        {"input": "What's up?", "output": "Not much, you?", "context": "casual"},
        {"input": "Thanks!", "output": "You're welcome!", "context": "gratitude"},
    ]
)
print(f"Added {len(result.row_ids)} rows")
```

### Unit Tests

Run an evaluation of your AI system on a dataset with a specified prompt template. The prompt template provided to the unit test may include variables that correspond to the dataset’s column names. The judge prompt template must include the `system_output` variable and may also reference any dataset column names as variables.

```python
# Create test dataset
dataset = await client.datasets.create(
    name="coding_tests",
    data=[
        {
            "task": "Write factorial function",
            "requirements": "Handle edge cases",
            "expected_output": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        },
        {
            "task": "Binary search",
            "requirements": "Return index or -1",
            "expected_output": "def binary_search(arr, target): # O(log n) implementation"
        },
    ]
)

# Create judge for evaluation (prompt_template required, system_prompt optional)
judge = await client.judges.create(
    name="code_quality_judge",
    judge_type=JudgeType.STATIC_PROMPT,
    system_prompt="You are an expert code reviewer. Rate from 1-10.",  # Static instructions
    prompt_template="""Task: {task}
Requirements: {requirements}
Expected: {expected_output}

Student's Solution:
{system_output}

Rate the quality from 1-10.""",  # Must include {system_output}
    label_type=ContinuousLabelType(min_value=1, max_value=10),
    ai_system_id=judge_system_id
)

# Create unit test
test = await client.unit_tests.create(
    name="Code Quality Test",
    system_id=system_id,  # The AI system being tested
    judge_ids=[judge.id],
    prompt_template="Task: {task}\nRequirements: {requirements}\n\nProvide a solution:",
    dataset_id=dataset.dataset_id,
    dataset_version=dataset.version
)

# Start and monitor progress
await client.unit_tests.start(test.test_id)
while True:
    test = await client.unit_tests.get(test.test_id)
    print(f"Test status: {test.status}")
    if test.status in [TestStatus.SUCCEEDED, TestStatus.FAILED]:
        break
    await asyncio.sleep(2)

print(f"Test completed: {test.status}")
```