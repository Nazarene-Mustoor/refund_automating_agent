from agno.agent import Agent
import os
import json
from excess_refund_driver import driver


def load_refund_file(filename: str):
    file_path = os.path.join("test_cases", filename)
    with open(file_path, "r") as f:
        return json.load(f)


def process_excess_refund(refund_data: dict):
    return driver(refund_data)


class RefundAgent(Agent):
    def run(self, filename: str):
        refund_data = load_refund_file(filename)
        result = process_excess_refund(refund_data)
        return result

# running single file
# def run_single():
#     agent = RefundAgent(name="RefundAgent")

#     result = agent.run("P2W90JK334455.json")

#     print("\nEligibility Result:")
#     print(result)

# if __name__ == "__main__":
#     run_single()

#running all files
def run_batch():
    agent = RefundAgent(name="RefundAgent")

    print("\nRunning all refund cases...\n")

    for filename in os.listdir("test_cases"):
        if not filename.endswith(".json"):
            continue

        try:
            result = agent.run(filename)

            print(f"{filename}")
            print(f"Eligible: {result['eligible']}")
            print(f"Reason: {result['reason']}")
            print("-" * 40)

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            print("-" * 40)


if __name__ == "__main__":
    run_batch()
