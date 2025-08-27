"""
How to:
1. Create Code of Conduct, policies, and violations
2. Read/retrieve CoCs, policies, and violations
3. Update CoCs, policies, and violations
4. Delete CoCs, policies, and violations
"""

import asyncio
import logging

from haizelabs import AsyncHaize

logging.basicConfig(level=logging.INFO)
logging.getLogger("haizelabs").setLevel(logging.DEBUG)


async def main():
    haize = AsyncHaize()

    # Create Code of Conduct
    coc = await haize.code_of_conduct.create(
        name="Company Ethics Guidelines",
        description="Comprehensive ethical guidelines for all employees",
    )
    print(f"Created CoC:\n{coc.model_dump_json(indent=2)}")

    # Create policy
    policy = await haize.code_of_conduct.create_policy(
        coc_id=coc.coc_id,
        policy="Maintain confidentiality of customer and company data",
    )
    print(f"Created policy:\n{policy.model_dump_json(indent=2)}")

    # Create violation for the policy
    violation = await haize.code_of_conduct.create_violation(
        coc_id=coc.coc_id,
        policy_id=policy.policy_id,
        violation="Share customer data without authorization",
    )
    print(f"Created violation:\n{violation.model_dump_json(indent=2)}")

    # Get Code of Conduct
    retrieved_coc = await haize.code_of_conduct.get(coc.coc_id)
    print(f"Retrieved CoC:\n{retrieved_coc.model_dump_json(indent=2)}")

    # Get all policies for a CoC
    policies = await haize.code_of_conduct.get_policies(coc.coc_id)
    print(f"Found policies:\n{policies.model_dump_json(indent=2)}")

    # Get all violations for a CoC
    violations = await haize.code_of_conduct.get_violations(coc.coc_id)
    print(f"Found violations:\n{violations.model_dump_json(indent=2)}")

    # Convert violations to behavior requests for red team testing
    behavior_requests = violations.to_behavior_requests()
    print(
        f"Converted to behavior requests:\n{[br.model_dump() for br in behavior_requests]}"
    )

    # Get specific policy
    retrieved_policy = await haize.code_of_conduct.get_policy(
        coc_id=coc.coc_id, policy_id=policy.policy_id
    )
    print(f"Retrieved policy:\n{retrieved_policy.model_dump_json(indent=2)}")

    # Modify Code of Conduct
    await haize.code_of_conduct.update(
        coc_id=coc.coc_id,
        name="Updated Ethics Guidelines",
        description="Revised comprehensive ethical guidelines",
    )
    print("Updated CoC successfully")

    # Modify policy
    await haize.code_of_conduct.update_policy(
        coc_id=coc.coc_id,
        policy_id=policy.policy_id,
        policy="Protect all confidential information and intellectual property",
    )
    print("Updated policy successfully")

    # Modify violation
    await haize.code_of_conduct.update_violation(
        coc_id=coc.coc_id,
        policy_id=policy.policy_id,
        violation_id=violation.violation_id,
        violation="Disclose confidential data without proper authorization",
    )
    print("Updated violation successfully")

    # Delete violation
    success = await haize.code_of_conduct.delete_violation(
        coc_id=coc.coc_id,
        policy_id=policy.policy_id,
        violation_id=violation.violation_id,
    )
    print(f"Deleted violation: {success}")

    # Delete policy (will also delete its violations)
    success = await haize.code_of_conduct.delete_policy(
        coc_id=coc.coc_id, policy_id=policy.policy_id
    )
    print(f"Deleted policy: {success}")

    # Delete entire Code of Conduct
    success = await haize.code_of_conduct.delete(coc.coc_id)
    print(f"Deleted CoC: {success}")

    await haize.close()


if __name__ == "__main__":
    asyncio.run(main())
