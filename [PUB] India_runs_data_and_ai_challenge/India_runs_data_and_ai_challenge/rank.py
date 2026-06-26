#!/usr/bin/env python3
import argparse
import json
import csv
from datetime import datetime

def parse_date(date_str):
    try: return datetime.strptime(date_str, "%Y-%m-%d")
    except: return None

def score_candidate(c):
    profile = c.get('profile', {})
    signals = c.get('redrob_signals', {})
    
    # Honeypot filter
    signup = parse_date(signals.get('signup_date'))
    last_active = parse_date(signals.get('last_active_date'))
    if signup and last_active and signup > last_active:
        return None
        
    # Basic score based on years of experience
    exp = profile.get('years_of_experience', 0)
    score = 0.5
    if 5.0 <= exp <= 9.0:
        score = 1.0
    return score

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    scored = []
    with open(args.candidates, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            c = json.loads(line)
            sc = score_candidate(c)
            if sc is not None:
                scored.append((sc, c))
                
    scored.sort(key=lambda x: (-x[0], x[1]['candidate_id']))
    
    with open(args.out, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (score, c) in enumerate(scored[:100], 1):
            writer.writerow([c['candidate_id'], rank, score, "Basic rank based on experience"])

if __name__ == '__main__':
    main()
