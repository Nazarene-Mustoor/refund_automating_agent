# Refund Automation Agent

## Overview

This project automates refund eligibility determination using an agent-based workflow.

The system processes refund case JSON files and determines eligibility for **Excess Refund** using deterministic business logic wrapped inside an agent abstraction.

Two agent orchestration approaches are demonstrated:

- CrewAI (LLM-driven orchestration)
- Agno (deterministic workflow orchestration)

---

## Architecture

### 1. Deterministic Business Logic
- `excess_refund_driver.py`
- Contains validation checks and eligibility logic
- No AI or probabilistic reasoning involved

### 2. Standalone Execution
- `run_driver.py`
- Runs the driver directly without any agent layer

### 3. CrewAI Agent Version
- `run_agent.py`
- Uses tool-based orchestration
- LLM-driven agent calls tools to:
  - Load refund JSON
  - Execute excess refund logic
- Requires OpenAI API key

### 4. Agno Agent Version
- `run_agno_agent.py`
- Deterministic agent orchestration
- No LLM required
- Sequential workflow execution

---

## Project Structure

excess_refund_driver.py
run_driver.py
run_agent.py
run_agno_agent.py
requirements.txt

## How to Run

### 1. Install Dependencies

pip install -r requirements.txt

---
### 2. Run Deterministic Driver

python run_driver.py

---

### 3. Run CrewAI Agent Version

Set your OpenAI API key:

**Windows**
set OPENAI_API_KEY=your_key_here

Then run:

python run_agent.py

---

### 4. Run Agno Agent Version

python run_agno_agent.py

---

## Design Decisions

- Deterministic business logic is kept independent of orchestration.
- Agent layer handles workflow control, not decision logic.
- Modular design allows extension to multiple refund types.
- Architecture supports adding a classification layer in future.

---

## Future Improvements

- Add refund type classifier layer
- Introduce routing for multiple refund categories
- Add structured logging / audit trail
- Integrate retry and escalation workflows
- Expand into production-ready orchestration system

---

## Notes

- No sensitive data is included in this repository.
- API keys must be set as environment variables.