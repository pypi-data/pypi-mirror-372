"""
Complete Unit Testing Example

This example demonstrates all key features of unit testing:
1. Creating a dataset with test cases
2. Configuring a judge
3. Running a unit test
"""

import asyncio
import os

from haizelabs import AsyncHaize
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType
from haizelabs.models.tests import TestStatus


async def main():
    api_key = os.environ.get("HAIZE_API_KEY")
    if not api_key:
        raise ValueError("Please set HAIZE_API_KEY environment variable")

    haize = AsyncHaize(api_key=api_key)

    ai_system = await haize.ai_systems.upsert_by_name(
        name="Python Coding Assistant",
        model="openai/gpt-4o-mini",
        system_prompt="You are an expert Python developer. Write clean, efficient, and well-documented code.",
    )
    print("✓ Created AI system to test:")
    print(ai_system.model_dump_json(indent=2))

    dataset = await haize.datasets.create(
        name="python_coding_tests",
        data=[
            {
                "task": "Write a function to calculate factorial",
                "requirements": "Handle edge cases (0, negative numbers), use recursion",
                "difficulty": "easy",
                "expected_output": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
            },
            {
                "task": "Implement a binary search function",
                "requirements": "Must work on sorted lists, return index or -1",
                "difficulty": "medium",
                "expected_output": "def binary_search(arr, target): # O(log n) implementation",
            },
            {
                "task": "Create a decorator for function timing",
                "requirements": "Should print execution time, work with any function",
                "difficulty": "hard",
                "expected_output": "import time; def timer(func): # decorator implementation",
            },
        ],
        description="Python coding challenges of varying difficulty",
    )
    print("✓ Created dataset:")
    print(dataset.model_dump_json(indent=2))

    judge_ai = await haize.ai_systems.upsert_by_name(
        name="Judge Model",
        model="openai/gpt-4o",
    )
    print("✓ Created AI system for judges:")
    print(judge_ai.model_dump_json(indent=2))

    quality_judge = await haize.judges.create(
        name="code_quality_judge",
        judge_type=JudgeType.STATIC_PROMPT,
        system_prompt="""You are an expert code reviewer.
        Rate from 1-10 where:
        1-3: Major issues, doesn't work
        4-6: Works but has problems
        7-8: Good with minor issues
        9-10: Excellent, production-ready""",
        prompt_template="""Evaluate this Python code submission:

        Task: {task}
        Requirements: {requirements}
        Difficulty: {difficulty}

        Expected Solution Pattern:
        {expected_output}

        Student's Solution:
        {system_output}""",
        label_type=ContinuousLabelType(min_value=1, max_value=10),
        ai_system_id=judge_ai.id,
    )
    print("✓ Created judge:")
    print(quality_judge.model_dump_json(indent=2))

    ai_prompt_template = """You have a {difficulty} Python coding task:

Task: {task}
Requirements: {requirements}

Please provide a complete, working implementation with proper error handling and comments."""

    unit_test = await haize.unit_tests.create(
        name="python_coding_test_comprehensive",
        system_id=ai_system.id,
        judge_ids=[quality_judge.id],
        prompt_template=ai_prompt_template,
        dataset_id=dataset.dataset_id,
        dataset_version=dataset.dataset_version,
    )
    print("✓ Created unit test:")
    print(unit_test.model_dump_json(indent=2))

    await haize.unit_tests.start(unit_test.test_id)
    print("✓ Test started, monitoring progress...")

    while True:
        test = await haize.unit_tests.get(unit_test.test_id)
        print(f"  Status: {test.status.value}")

        if test.status in [TestStatus.SUCCEEDED, TestStatus.FAILED]:
            break

        await asyncio.sleep(2)

    print(f"Test completed: {test.model_dump_json(indent=2)}")
    await haize.close()


if __name__ == "__main__":
    test_id = asyncio.run(main())
