"""
Dataset Operations Example

Demonstrates the dataset API operations: create, get, update
"""

import asyncio

from haizelabs import AsyncHaize


async def main():
    haize = AsyncHaize()

    dataset = await haize.datasets.create(
        name="qa_dataset",
        data=[
            {"question": "What is 2+2?", "context": "Basic arithmetic", "answer": "4"},
            {
                "question": "Capital of France?",
                "context": "Geography",
                "answer": "Paris",
            },
        ],
        description="Initial Q&A dataset",
    )
    print("Created dataset:")
    print(dataset.model_dump_json(indent=2))

    # Get dataset (latest version by default)
    retrieved = await haize.datasets.get(dataset.dataset_id)
    print("Retrieved dataset: ", retrieved.model_dump_json(indent=2))

    result = await haize.datasets.add_rows(
        dataset_id=dataset.dataset_id,
        dataset_version=retrieved.dataset_info.version,
        data=[
            {
                "question": "What is the speed of light?",
                "context": "Physics",
                "answer": "299,792,458 m/s",
            },
            {
                "question": "Who wrote Romeo and Juliet?",
                "context": "Literature",
                "answer": "Shakespeare",
            },
        ],
    )
    print(f"Added rows: {result.model_dump_json(indent=2)}")

    updated = await haize.datasets.update(
        dataset_id=dataset.dataset_id,
        name="qa_dataset_v2",
        data=[
            {
                "question": "What is 2+2?",
                "context": "Math",
                "answer": "4",
                "difficulty": "easy",
            },
            {
                "question": "Capital of France?",
                "context": "Geography",
                "answer": "Paris",
                "difficulty": "easy",
            },
            {
                "question": "Explain quantum computing",
                "context": "Physics",
                "answer": "Complex topic",
                "difficulty": "hard",
            },
        ],
        description="Updated Q&A dataset with difficulty levels",
    )
    print("Updated dataset: ", updated.model_dump_json(indent=2))

    # Get updated version
    updated_dataset = await haize.datasets.get(
        dataset.dataset_id, version=updated.dataset_version
    )
    print(f"Updated dataset: {updated_dataset.model_dump_json(indent=2)}")

    await haize.close()


if __name__ == "__main__":
    asyncio.run(main())
