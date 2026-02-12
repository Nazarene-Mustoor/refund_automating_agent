import json
import os
from unittest import result 
from excess_refund_driver import driver


def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
    
def main():
    print("Running excess refund checks...\n")

    for filename in os.listdir("test_cases"):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join("test_cases", filename)
        statementOfAccount = load_json(file_path)

        result = driver(statementOfAccount)

        print(f"{filename}")
        print(f" Eligible: {result['eligible']}")
        print(f" Reason: {result['reason']}")
        if "unadjusted_amount" in result:
            print(f"Unadjusted Amount: {result['unadjusted_amount']}")
        print("-"*40)

if __name__ == "__main__":
    main()