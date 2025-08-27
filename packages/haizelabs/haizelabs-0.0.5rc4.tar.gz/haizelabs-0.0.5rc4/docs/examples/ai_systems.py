"""
How to:
1. Create AI systems (third-party and self-hosted)
2. Read/retrieve AI systems
3. Update AI systems
4. Handle errors gracefully
"""

import asyncio
import logging

from haizelabs import AsyncHaize, HaizeAPIError
from haizelabs.models.ai_system import (
    TogetherConfig,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("haizelabs").setLevel(logging.DEBUG)


async def main():
    async with AsyncHaize() as haize:
        ai_system = await haize.ai_systems.upsert_by_name(
            name="example_assistant",
            model="openai/gpt-4o-mini",
            system_prompt="You are a helpful assistant",
            system_config={"temperature": 0.7, "max_tokens": 1000},
        )
        print(f"Created AI system: {ai_system.model_dump_json(indent=2)}")

        together_config = TogetherConfig(model_id="meta-llama/Llama-2-7b-chat-hf")
        try:
            self_hosted_system_id = await haize.ai_systems.create(
                name="my llama",
                self_hosted_config=together_config,
                api_key="your_together_api_key",
                system_prompt="You are a helpful assistant",
                system_config={"temperature": 0.5, "max_tokens": 500},
            )
            print(f"Created self-hosted system: {self_hosted_system_id}")
        except HaizeAPIError as e:
            # This happens if you call create with a name that already exists
            print(f"API error: {e.message} (status: {e.status_code})")

        upserted_system = await haize.ai_systems.upsert_by_name(
            name="example_assistant",
            model="openai/gpt-4o",
            system_prompt="You are an expert assistant with deep knowledge",
        )
        print(f"Upserted system: {upserted_system.model_dump_json(indent=2)}")

        retrieved_system = await haize.ai_systems.get(ai_system.id)
        print(f"Retrieved system: {retrieved_system.model_dump_json(indent=2)}")

        # fetch available supported models
        models = await haize.ai_systems.get_supported_models()
        print(f"Available models: {models}")


if __name__ == "__main__":
    asyncio.run(main())
