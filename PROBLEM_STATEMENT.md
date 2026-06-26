# Problem Statement & Evaluation Criteria

## Challenge Goal
The goal of the Intelligent Candidate Discovery & Ranking Challenge is to design and implement a high-performance candidate ranking system that matches a 100,000-candidate database against a specific Job Description (JD): **Senior AI Engineer — Founding Team** at Redrob AI.

The output must be a CSV file with exactly the top 100 candidate IDs, ordered from most relevant to least relevant, with a 1-2 sentence reasoning explaining their fit.

## Evaluation Pipeline & Metrics
Submissions are evaluated on a hidden ground truth relevance mapping across five stages:

1. **Format Validation**: Ensures columns are exactly `candidate_id,rank,score,reasoning` and the ranks are 1 to 100 with non-increasing scores.
2. **Quantitative Scoring**: The final composite score is calculated as:
   $$\text{Composite} = 0.50 \times \text{NDCG@10} + 0.30 \times \text{NDCG@50} + 0.15 \times \text{MAP} + 0.05 \times \text{P@10}$$
   - **NDCG@10**: Quality of the top 10 picks.
   - **NDCG@50**: Quality of the top 50 picks.
   - **MAP (Mean Average Precision)**: Precision across all relevance levels.
   - **P@10**: Fraction of top-10 that are relevant (tier 3+).
3. **Code Reproduction & Honeypot Check**:
   - The execution must reproduce under sandboxed CPU constraints in $\le 5$ minutes.
   - The honeypot rate in the top 100 must be $\le 10\%$.
4. **Manual Review**: High-quality, non-templated reasoning with specific facts and honest concerns.
5. **Defend-Your-Work Interview**: 30-minute code walkthrough with the Redrob engineering team.

## Dataset Traps
A core difficulty of the challenge is that the candidate pool contains synthetic noise and adversarial traps:

- **Honeypots (~80 candidates)**: Profiles that have subtly impossible features (e.g. signup date after last active date, or expert proficiency in 5+ skills with 0 months of duration). Ranging these in the top 10 or 100 indicates keyword-matching without profile verification, and leads to disqualification.
- **Keyword Stuffers**: Candidates who list all AI keywords in their skills but whose current job titles (e.g. HR Manager, Graphic Designer, Marketing Manager) indicate they do not have real engineering experience.
- **Plain-Language Tier 5s**: High-quality candidates who do not use modern buzzwords (like "RAG" or "Pinecone") in their skills list, but whose career histories show they built search, recommendation, or retrieval systems at product companies.
- **Behavioral Twins**: Near-identical profiles (matching names/experience) that differ solely on their engagement signals. A candidate who is inactive or has a 5% response rate must be down-weighted in favor of an active, responsive candidate.
- **Consulting/Services Bias**: The JD explicitly disqualifies candidates who have only worked at consulting/services firms (e.g., Infosys, TCS, Wipro). Candidates must have product-company experience.
