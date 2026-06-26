# Workflow, Architecture & Key Decisions

## Proposed Solution Architecture

Our solution follows a high-efficiency **Two-Stage Ranking Architecture** designed to execute on 100,000 candidates in under 10 seconds on a single CPU.

```mermaid
graph TD
    A[100,000 Candidates Pool] --> B[Stage 1: Fast Filters]
    B -->|Remove Honeypots| C[Clean Pool]
    B -->|Remove Non-Tech / Services-only| C
    B -->|Remove Country != India / Experience outside [4,12]| C
    C -->|~13,300 Candidates| D[Stage 2: Technical Scoring]
    D -->|Title Fit, Experience Fit, Skill Trust, Career Match| E[Raw Technical Score]
    E --> F[Behavioral Signals Multiplier]
    F -->|Availability, Recency, Response Rate, Notice Period| G[Final Score]
    G --> H[Sort & Tie-break by candidate_id]
    H --> I[Take Top 100]
    I --> J[Generate Dynamic 1-2 Sentence Reasonings]
    J --> K[submission.csv Output]
```

### Stage 1: Fast Filters
We run a series of strict rule-based filters to eliminate noise, adversarial honeypots, and clearly non-matching profiles:
1. **Honeypot Detector**: Excludes profiles with `signup_date > last_active_date` or `duration_months == 0` for any `expert` skill.
2. **Title Filter**: Discards non-tech roles (e.g. HR Manager, Graphic Designer, Accountant).
3. **Product-Experience Filter**: Discards candidates who have only worked at consulting/services firms (e.g. Infosys, Wipro, TCS).
4. **Geography Filter**: Discards profiles located outside of India.
5. **Experience Filter**: Discards profiles with total years of experience outside the range $[4.0, 12.0]$.

### Stage 2: Scoring Model
We calculate a technical score and modify it with a behavioral multiplier.

#### Technical Score (0.0 to 1.0)
- **Title Score (30%)**: Scores target titles higher (e.g. `Senior AI Engineer` = 1.0, `Data Scientist` = 0.75, `Software Engineer` = 0.4).
- **Experience Score (10%)**: Peak score for the target range of 5–9 years; tapers off linearly down to 4 and up to 12.
- **Skill Score (35%)**: Checks for key AI/retrieval skills. Incorporates a **Trust Multiplier**:
  $$\text{Trust} = \ln(1 + \text{endorsements}) \times \ln(1 + \text{duration\_months})$$
  This captures real experience and filters out lazy keyword stuffing.
- **Career Score (25%)**: Searches career descriptions for key projects (e.g. recommendation systems, vector search, retrieval, RAG). Grants a bonus for experience at top-tier AI startups (e.g. Sarvam AI, Observe.AI) and tech product companies (e.g. Swiggy, Razorpay).

#### Behavioral Multiplier
To ensure availability and active status, the technical score is multiplied by:
- **Response Rate Factor**: $0.5 + 0.5 \times \text{response\_rate}$
- **Activity Recency Factor**: $1.0$ (active within 30 days) to $0.4$ (inactive over 180 days).
- **Notice Period Factor**: $1.0$ (notice $\le 30$ days) to $0.5$ (notice $> 90$ days).
- **Open-to-work Factor**: $1.05$ (flagged) or $0.95$ (not flagged).
- **Interview Completion Factor**: $0.7 + 0.3 \times \text{completion\_rate}$.

---

## Key Decisions

1. **Rejecting Services-only Engineers**: The JD was extremely clear: "People who have only worked at consulting firms... in their entire career [are a bad fit]". We implemented a strict check to ensure at least one company in the career history is a product/startup firm.
2. **Protecting Against Keyword Stuffers**: The "endorsement-and-duration" log multiplier on skills prevents candidates who just copy-pasted buzzwords from scoring high. They must have substantial duration or endorsements to back it up.
3. **Dynamic Reasoning Generation**: We programmatically build 1-2 sentence reasonings for each candidate using their actual profile facts (years of experience, current title, matched skills, specific companies, location, response rate, notice period). This ensures **zero hallucination** and high variation, while matching rank tone.
4. **Rounding Before Sorting**: We round the score to 4 decimal places in Python *before* sorting, so the deterministic tie-breaking (`candidate_id` ascending) matches the precision of the output CSV and satisfies the official validator.
