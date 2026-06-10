def score_job(parsed_jd: dict, your_skills: list, your_exp: int) -> dict:
    required = set(s.lower() for s in parsed_jd.get("required_skills", []))
    yours    = set(s.lower() for s in your_skills)

    if not required:
        return {
            "score": 0, "matched": [], "missing": [],
            "exp_ok": True, "should_apply": False
        }

    matched   = required & yours
    match_pct = round(len(matched) / len(required) * 100)
    
    # safely handle None experience_years
    jd_exp    = parsed_jd.get("experience_years") or 0
    exp_ok    = your_exp >= jd_exp

    return {
        "score":        match_pct,
        "matched":      list(matched),
        "missing":      list(required - yours),
        "exp_ok":       exp_ok,
        "should_apply": match_pct >= 10    # ← changed to 10%
    }