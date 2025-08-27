"""
How to:
1. Create Static Prompt judges with direct model selection
2. Create Exact Match and Regex Match judges
3. Retrieve judges by ID
"""

import asyncio
import logging

from haizelabs import AsyncHaize
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType, EnumLabelType

logging.basicConfig(level=logging.INFO)
logging.getLogger("haizelabs").setLevel(logging.DEBUG)


async def main():
    async with AsyncHaize() as haize:
        # Create judges directly with model selection
        quality_judge = await haize.judges.create(
            name="quality_judge",
            model="openai/gpt-4o-mini",
            system_prompt="Rate the quality of this response from 1 to 10",
            prompt_template="Rate the quality of this response from 1 to 10: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
        )

        print(f"✓ Created quality judge (ID: {quality_judge.id})")

        exact_match_judge = await haize.judges.create(
            name="exact_answer_judge",
            label_type=EnumLabelType(options=["correct", "incorrect"]),
            judge_type=JudgeType.EXACT_MATCH,
            default_match_value="Paris",
            description="Checks if the answer is exactly 'Paris'",
        )

        regex_match_judge = await haize.judges.create(
            name="email_format_judge",
            label_type=EnumLabelType(options=["valid", "invalid"]),
            judge_type=JudgeType.REGEX_MATCH,
            default_regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            description="Validates email format using regex",
        )

        print(f"✓ Created exact match judge (ID: {exact_match_judge.id})")
        print(f"✓ Created regex match judge (ID: {regex_match_judge.id})")

        # Retrieve a judge
        retrieved_judge = await haize.judges.get(quality_judge.id)
        print(f"✓ Retrieved judge: {retrieved_judge.name} (ID: {retrieved_judge.id})")


if __name__ == "__main__":
    asyncio.run(main())
