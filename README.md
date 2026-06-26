# India Runs AI & Data Challenge — Intelligent Candidate Discovery & Ranking

Welcome to the India Runs AI & Data Challenge repository. This project focuses on building a high-quality candidate discovery and ranking system that evaluates candidate profiles against a complex "Senior AI Engineer — Founding Team" job description (JD) at Redrob.

## Project Overview

Our ranker operates on a candidate pool of **100,000 resumes** and retrieves the **top 100 candidates**, ranked from best-fit (Rank 1) to 100th-best-fit (Rank 100). The ranker evaluates technical competence (roles, skills, and product-focused experience), checks for subtle profile traps (honeypots and keyword stuffers), and factors in real-time platform engagement (behavioral signals).

### Key Features
- **Honeypot Filter**: Successfully detects and removes candidates with contradictory profiles (e.g. signup date after last active date, or "expert" skills with 0 months of duration).
- **Keyword Stuffer Protection**: Implements an "endorsement-and-duration" trust multiplier for skills, filtering out candidates who merely list buzzwords without matching experience.
- **Plain-Language Matcher**: Searches career descriptions for key projects (e.g., "recommendation systems", "vector search", "retrieval") to bubble up candidates who match the JD's semantic meaning rather than just keyword tags.
- **Availability Weighting**: Scores candidates based on their notice periods, active login dates, and recruiter response rates.
- **Valid and Fast**: Generates the CSV submission in under **10 seconds** on a standard CPU, passing all official validation checks.

## Repository Structure

- `[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/` - Contains official challenge files:
  - [rank.py](file:///c:/SWAYAMs/PROJ/India_Runs/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/rank.py) - Main candidate ranking execution script.
  - [submission.csv](file:///c:/SWAYAMs/PROJ/India_Runs/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/submission.csv) - Validated top 100 candidate ranking output.
  - [validate_submission.py](file:///c:/SWAYAMs/PROJ/India_Runs/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py) - Official submission format validator.
- [PROBLEM_STATEMENT.md](file:///c:/SWAYAMs/PROJ/India_Runs/PROBLEM_STATEMENT.md) - Deep dive into challenge constraints, evaluation metric, and dataset traps.
- [WORKFLOW.md](file:///c:/SWAYAMs/PROJ/India_Runs/WORKFLOW.md) - Proposed architecture, scoring methodology, and key design decisions.
- [TASKS.md](file:///c:/SWAYAMs/PROJ/India_Runs/TASKS.md) - Actionable task tracking and project checklist.

## Quick Start (How to Run)

Ensure you have a Python virtual environment set up and activated:

```bash
# 1. Set up virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Run the ranker
python "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/rank.py" --candidates "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" --out "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/submission.csv"

# 3. Validate the submission
python "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/submission.csv"
```
