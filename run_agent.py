import os 
import json 
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
# from langchain_ollama import OllamaLLM
from excess_refund_driver import driver

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY is not set. Please set it as an environment variable.")

# llm = LLM(model="openai/gpt-4o-mini")

def run_excess_refund(input_data: dict):
    return driver(input_data)


@tool
def load_refund_file(path: str) -> dict:
    """
    Load a refund case JSON file from the test_cases directory.

    Args:
        path (str): The filename of the JSON case.

    Returns:
        dict: Parsed JSON data.
    """
    file_path = os.path.join("test_cases", path)
    with open(file_path, "r") as f:
        data = json.load(f)

    print("LOADED FILE DATA:", data)
    return data

@tool
def process_excess_refund(input_data: dict) -> dict:
    """
    Process an excess refund case deterministically.

    Args:
        input_data (dict): The complete refund case JSON data.

    Returns:
        dict: A JSON response indicating refund eligibility and reason.
    """
    print("TYPE RECEIVED:", type(input_data))
    result = driver(input_data)
    print("DRIVER RESULT:", result)
    return result

llm = LLM(model="ollama/llama3")

refund_agent = Agent(
    role="Refund Processing Agent",
    goal="Determine refund eligibility using tools only.",
    backstory="You MUST call tools using proper tool format. Do not output JSON directly.",
    tools=[load_refund_file, process_excess_refund],
    llm=llm,
    max_iter=2,
    verbose=True,
)

# def create_task(filename):
#     return Task(
#         # description=f"""
#         # Process the refund case file: {filename}.

#         # Step 1:
#         # Call load_refund_file with:
#         # {{
#         #   "path": "{filename}"
#         # }}

#         # Step 2:
#         # Take the returned JSON and pass it EXACTLY as received to process_excess_refund as:
#         # {{
#         #   "input_data": <returned JSON>
#         # }}

#         # Do NOT wrap arguments inside 'properties'.
#         # Do NOT modify the JSON.
#         # """,
#         # description = f"""
#         #     Load file {filename} using tool load_refund_file.
#         #     Then pass the returned JSON to process_excess_refund.

#         #     Do NOT modify the JSON.
#         # """,
#         description=f"""
#             Use tools only.

#             1) load_refund_file with {{"path": "{filename}"}}
#             2) process_excess_refund with {{"input_data": <tool_output>}}

#             Do NOT modify JSON.
#         """,
#         agent=refund_agent,
#         expected_output="Final JSON indicating eligibility and reason."
#     )

def create_task(filename):
    return Task(
        description=f"""
        Call load_refund_file with path "{filename}".
        Then call process_excess_refund with the result.
        Do NOT output anything manually.
        """,
        agent=refund_agent,
        expected_output="Tool-based execution only."
    )

#loop through all test cases in the test_cases directory
# def run_batch():
#     results = []

#     for filename in os.listdir("test_cases"):
#         if not filename.endswith(".json"):
#             continue

#         task = create_task(filename)

#         crew = Crew(
#             agents = [refund_agent], #only one agent
#             tasks = [task], #one task
#             verbose = True
#         )

#         result = crew.kickoff() #triggers execution

#         print(f"\n {filename}")
#         print("FINAL RESULT (Agent Execution):")
#         print(result)
#         print("-"*40)

#         results.append((filename, result))

#     return results

# if __name__ == "__main__":
#     run_batch()

#running only one test case for now:
def run_single():
    filename = "P2W90JK334455.json"

    task = create_task(filename)

    crew = Crew(
        agents=[refund_agent],
        tasks=[task],
        verbose= True
    )

    result = crew.kickoff()

    print("\nFINAL RESULT (Agent Execution):")
    print(result)

if __name__ == "__main__":
    run_single()