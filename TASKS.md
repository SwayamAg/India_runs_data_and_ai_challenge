# India Runs AI & Data Challenge Tasks

## Checklist

- [x] **Phase 1: Exploration & Initial Setup**
  - [x] Read all README and documentation files (`README.docx`, `job_description.docx`, `redrob_signals_doc.docx`, `submission_spec.docx`).
  - [x] Understand candidate JSON schema (`candidate_schema.json`) and sample candidate files.
  - [x] Create Python virtual environment `.venv`.
- [x] **Phase 2: Design & Prototyping**
  - [x] Write script to detect honeypots (signup dates discrepancy, 0-duration expert skills).
  - [x] Write script to identify "behavioral twins" and analyze services-only consulting companies in the pool.
  - [x] Design technical scoring function with experience, title, and skill-trust weighting.
  - [x] Design behavioral multiplier to weigh availability (response rate, notice period, active recency).
- [x] **Phase 3: Ranker Script Implementation**
  - [x] Implement main ranker script [rank.py](file:///c:/SWAYAMs/PROJ/India_Runs/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/rank.py) with command-line argument support.
  - [x] Build programmatic 1-2 sentence reasoning generator matching candidate profile facts.
  - [x] Ensure deterministic tie-breaking by `candidate_id` ascending.
- [x] **Phase 4: Validation & Formatting**
  - [x] Round scores to 4 decimal places before sorting to align Python sort with output CSV precision.
  - [x] Run ranker script to generate [submission.csv](file:///c:/SWAYAMs/PROJ/India_Runs/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/submission.csv).
  - [x] Verify submission using the official format validator [validate_submission.py](file:///c:/SWAYAMs/PROJ/India_Runs/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py).
- [x] **Phase 5: Documentation & Presentation**
  - [x] Create [README.md](file:///c:/SWAYAMs/PROJ/India_Runs/README.md) for project setup and running instructions.
  - [x] Create [PROBLEM_STATEMENT.md](file:///c:/SWAYAMs/PROJ/India_Runs/PROBLEM_STATEMENT.md) for constraints and dataset trap details.
  - [x] Create [WORKFLOW.md](file:///c:/SWAYAMs/PROJ/India_Runs/WORKFLOW.md) for architecture and key design decisions.
  - [x] Create [TASKS.md](file:///c:/SWAYAMs/PROJ/India_Runs/TASKS.md) to track todo items.
  - [x] Summarize understanding and suggest solution ideas to the user.

## Current Progress
We have implemented the ranker end-to-end, generated a valid submission CSV, and successfully verified it with the official validator. Documentation is complete.

## Next Steps
- [ ] Receive feedback from the USER on the current ranking logic and suggestions.
- [ ] If required, adjust scoring weights or add more advanced features.
