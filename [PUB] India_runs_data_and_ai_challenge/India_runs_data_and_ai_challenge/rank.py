#!/usr/bin/env python3
"""
Redrob Hackathon Ranker
Produces a high-quality candidate ranking based on JD fit and behavioral signals.
"""

import argparse
import json
import csv
import math
from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def score_candidate(c):
    profile = c.get('profile', {})
    career = c.get('career_history', [])
    skills = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    
    # ----------------------------------------------------
    # 1. HONEYPOT / DISQUALIFICATION FILTERS
    # ----------------------------------------------------
    # Contradiction: Signup date > Last active date
    signup = parse_date(signals.get('signup_date'))
    last_active = parse_date(signals.get('last_active_date'))
    if signup and last_active and signup > last_active:
        return None, "Honeypot: signup_date > last_active_date"
        
    # Contradiction: Expert skills with 0 duration
    expert_0_dur = 0
    for s in skills:
        if s.get('proficiency') == 'expert' and s.get('duration_months', 0) == 0:
            expert_0_dur += 1
    if expert_0_dur >= 1:
        return None, "Honeypot: expert skill with 0 duration"
        
    # Services-only career history (Disqualified per JD)
    services_firms = {
        "Infosys", "Wipro", "TCS", "Capgemini", "HCL", 
        "Mindtree", "Accenture", "Cognizant", "Tech Mahindra", "Mphasis"
    }
    all_services = True
    for job in career:
        if job.get('company') not in services_firms:
            all_services = False
            break
    if all_services and len(career) > 0:
        return None, "Disqualified: services-only experience"
        
    # Non-tech titles (Marketing, HR, etc. are disqualified per JD)
    non_tech_titles = {
        "Business Analyst", "HR Manager", "Mechanical Engineer", "Accountant",
        "Project Manager", "Customer Support", "Operations Manager", "Content Writer",
        "Sales Executive", "Civil Engineer", "Graphic Designer", "Marketing Manager"
    }
    title = profile.get('current_title', '')
    if title in non_tech_titles:
        return None, "Disqualified: non-tech current title"
        
    # Country check: must be India (no work visa sponsorship)
    country = profile.get('country', '')
    if country != 'India':
        return None, "Disqualified: country is not India"
        
    # ----------------------------------------------------
    # 2. EXPERIENCE SCORING (5-9 years is target)
    # ----------------------------------------------------
    exp = profile.get('years_of_experience', 0)
    if 5.0 <= exp <= 9.0:
        exp_score = 1.0
    elif 4.0 <= exp < 5.0:
        exp_score = 0.7 + 0.3 * (exp - 4.0)
    elif 9.0 < exp <= 12.0:
        exp_score = 1.0 - 0.1 * (exp - 9.0)
    else:
        # Too junior or too senior
        return None, f"Disqualified: experience {exp} outside range [4, 12]"
        
    # ----------------------------------------------------
    # 3. TITLE MATCH SCORING
    # ----------------------------------------------------
    title_lower = title.lower()
    title_score = 0.1
    if "senior ai engineer" in title_lower or "lead ai engineer" in title_lower or "staff machine learning engineer" in title_lower or "senior machine learning engineer" in title_lower:
        title_score = 1.0
    elif "applied ml engineer" in title_lower or "machine learning engineer" in title_lower or "ml engineer" in title_lower or "ai engineer" in title_lower or "ai research engineer" in title_lower:
        title_score = 0.9
    elif "senior software engineer (ml)" in title_lower or "computer vision engineer" in title_lower or "nlp engineer" in title_lower or "senior nlp engineer" in title_lower or "ai specialist" in title_lower or "senior applied scientist" in title_lower:
        title_score = 0.8
    elif "data scientist" in title_lower or "senior data scientist" in title_lower:
        title_score = 0.75
    elif "junior ml engineer" in title_lower:
        title_score = 0.6
    elif "data engineer" in title_lower or "senior data engineer" in title_lower or "analytics engineer" in title_lower:
        title_score = 0.5
    elif "backend engineer" in title_lower or "senior software engineer" in title_lower or "software engineer" in title_lower:
        title_score = 0.4
    elif "full stack developer" in title_lower or "cloud engineer" in title_lower or "devops engineer" in title_lower or "java developer" in title_lower or ".net developer" in title_lower:
        title_score = 0.2
        
    # ----------------------------------------------------
    # 4. SKILLS MATCH SCORING WITH TRUST MULTIPLIER
    # ----------------------------------------------------
    # Skill keywords from the JD
    high_value_skills = {
        "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss", # vector search / db
        "sentence-transformers", "embeddings", "vector search", "retrieval", "information retrieval", # retrieval
        "rag", "fine-tuning llms", "lora", "qlora", "peft", "llm", "llms", # LLMs / fine-tuning
        "ranking", "learning to rank", # ranking
    }
    
    medium_value_skills = {
        "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
        "pytorch", "tensorflow", "weights & biases", "mlflow", "xgboost", "scikit-learn", "python",
        "databricks", "spark", "hadoop", "flink", "beam", "kafka", "airflow"
    }
    
    skills_score = 0.0
    for s in skills:
        sname = s.get('name', '').lower()
        sprof = s.get('proficiency', 'beginner')
        sdur = s.get('duration_months', 0)
        send = s.get('endorsements', 0)
        
        weight = 0.0
        if any(hvs in sname for hvs in high_value_skills):
            weight = 2.0
        elif any(mvs in sname for mvs in medium_value_skills):
            weight = 1.0
            
        if weight > 0:
            # Proficiency multiplier
            prof_mult = {"expert": 1.0, "advanced": 0.8, "intermediate": 0.6, "beginner": 0.3}.get(sprof, 0.3)
            # Trust multiplier to protect against keyword stuffers (require endorsements & duration)
            trust_mult = math.log1p(send) * math.log1p(sdur)
            skills_score += weight * prof_mult * trust_mult
            
    # Normalize skills score to a 0-1 range
    skills_score = min(skills_score / 30.0, 1.0)
    
    # ----------------------------------------------------
    # 5. CAREER HISTORY TEXT SEARCH (For plain-language Tier 5s)
    # ----------------------------------------------------
    career_score = 0.0
    ai_startups = {
        "Glance", "Rephrase.ai", "Aganitha", "Niramai", "Saarthi.ai", 
        "Sarvam AI", "Mad Street Den", "Observe.AI", "Krutrim", "Wysa", "Haptik"
    }
    product_startups = {
        "Swiggy", "Razorpay", "CRED", "Zomato", "Flipkart", "Meesho", "Nykaa", "InMobi", "Zoho",
        "Freshworks", "PhonePe", "Paytm", "Ola", "Pied Piper", "Hooli"
    }
    
    has_ai_startup = False
    has_product_startup = False
    
    for job in career:
        comp = job.get('company', '')
        if comp in ai_startups:
            has_ai_startup = True
        elif comp in product_startups:
            has_product_startup = True
            
        # Text match in description for ranking/retrieval project work
        desc = job.get('description', '').lower()
        desc_keywords = [
            "recommendation system", "recommender", "ranking", "search engine", 
            "vector search", "embeddings", "retrieval", "rag system", "semantic search",
            "fine-tuning", "llm pipeline", "neural search", "learning to rank"
        ]
        for kw in desc_keywords:
            if kw in desc:
                career_score += 0.25 # boost for each match
                
    if has_ai_startup:
        career_score += 0.5
    elif has_product_startup:
        career_score += 0.25
        
    career_score = min(career_score, 1.0)
    
    # ----------------------------------------------------
    # 6. BEHAVIORAL SIGNALS MULTIPLIER
    # ----------------------------------------------------
    # Recruiter response rate
    resp_rate = signals.get('recruiter_response_rate', 0.0)
    resp_factor = 0.5 + 0.5 * resp_rate
    
    # Days since last active (relative to June 2026)
    last_act_str = signals.get('last_active_date', '')
    last_act_date = parse_date(last_act_str)
    curr_date = datetime(2026, 6, 26)
    if last_act_date:
        days_inactive = (curr_date - last_act_date).days
        if days_inactive <= 30:
            act_factor = 1.0
        elif days_inactive <= 90:
            act_factor = 0.9
        elif days_inactive <= 180:
            act_factor = 0.7
        else:
            act_factor = 0.4
    else:
        act_factor = 0.4
        
    # Open to work flag
    open_to_work = signals.get('open_to_work_flag', False)
    otw_factor = 1.05 if open_to_work else 0.95
    
    # Interview completion rate
    int_rate = signals.get('interview_completion_rate', 0.0)
    int_factor = 0.7 + 0.3 * int_rate
    
    # Notice period days
    notice_days = signals.get('notice_period_days', 60)
    if notice_days <= 30:
        notice_factor = 1.0
    elif notice_days <= 60:
        notice_factor = 0.9
    elif notice_days <= 90:
        notice_factor = 0.8
    else:
        notice_factor = 0.5
        
    behavior_mult = resp_factor * act_factor * otw_factor * int_factor * notice_factor
    
    # ----------------------------------------------------
    # 7. TOTAL SCORE COMBINATION
    # ----------------------------------------------------
    tech_score = 0.3 * title_score + 0.1 * exp_score + 0.35 * skills_score + 0.25 * career_score
    final_score = tech_score * behavior_mult
    
    return final_score, "Passed"

def generate_reasoning(c, score, rank):
    p = c.get('profile', {})
    skills = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    career = c.get('career_history', [])
    
    title = p.get('current_title', 'Engineer')
    exp = p.get('years_of_experience', 0.0)
    location = p.get('location', 'India')
    resp_rate = int(signals.get('recruiter_response_rate', 0.0) * 100)
    notice = signals.get('notice_period_days', 30)
    
    # Extract matching skills
    core_ai_skills = {
        "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss",
        "sentence-transformers", "embeddings", "vector search", "retrieval",
        "rag", "fine-tuning llms", "lora", "qlora", "peft", "llm", "llms",
        "ranking", "learning to rank", "pytorch", "tensorflow", "nlp", "natural language processing"
    }
    
    matched_skills = []
    for s in skills:
        sname = s.get('name', '')
        if sname.lower() in core_ai_skills:
            matched_skills.append(sname)
            
    if not matched_skills:
        matched_skills = [s.get('name', '') for s in skills[:3]]
        
    skills_str = ", ".join(matched_skills[:2]) if matched_skills else "applied ML"
    
    # Extract unique companies
    companies = []
    for job in career:
        comp = job.get('company', '')
        if comp and comp not in companies:
            companies.append(comp)
    comp_str = " and ".join(companies[:2]) if companies else "product firms"
    
    # Dynamic templates based on rank
    if rank <= 10:
        s1 = f"Stellar {title} with {exp:.1f} years of experience, possessing deep expertise in {skills_str}."
        if companies:
            s1 += f" Proven track record of shipping ML systems at {comp_str}."
    elif rank <= 50:
        s1 = f"Highly qualified {title} with {exp:.1f} years of experience, skilled in {skills_str}."
        if companies:
            s1 += f" Demonstrated strong software and ML engineering competency at {comp_str}."
    else:
        s1 = f"Solid {title} with {exp:.1f} years of experience, familiar with {skills_str}."
        if companies:
            s1 += f" Background includes relevant engineering roles at {comp_str}."
            
    # Availability / location details
    if notice > 90:
        s2 = f"Based in {location} with {resp_rate}% response rate, though the {notice}-day notice period is a minor concern."
    elif notice <= 30:
        s2 = f"Excellent availability with {resp_rate}% response rate and quick {notice}-day notice period, based in {location}."
    else:
        s2 = f"Strong engagement ({resp_rate}% response rate, {notice}-day notice), located in {location}."
        
    return f"{s1} {s2}"

def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Senior AI Engineer JD.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl file.")
    parser.add_argument("--out", required=True, help="Path to save submission.csv.")
    args = parser.parse_args()
    
    scored_candidates = []
    
    with open(args.candidates, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            score, reason = score_candidate(c)
            if score is not None:
                scored_candidates.append((round(score, 4), c))
                
    # Sort by score descending, tie-break by candidate_id ascending
    scored_candidates.sort(key=lambda x: (-x[0], x[1]['candidate_id']))
    
    # Take top 100
    top_100 = scored_candidates[:100]
    
    # Write to CSV
    with open(args.out, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank, (score, c) in enumerate(top_100, 1):
            cid = c['candidate_id']
            reasoning = generate_reasoning(c, score, rank)
            writer.writerow([cid, rank, f"{score:.4f}", reasoning])
            
    print(f"Successfully wrote top 100 rankings to {args.out}")

if __name__ == '__main__':
    main()
