def icd_clause(icd_codes: dict[str, list]):
    if icd_codes is None:
        return "1=1"
    icd9 = "1<>1"
    icd10 = "1<>1"
    if icd_codes is not None:
        if icd_codes.get("icd9", None) is not None:
            icd9_clause = " OR ".join(
                [
                    "co.CONDITION_SOURCE_VALUE LIKE '" + c + "'"
                    for c in icd_codes["icd9"]
                ]
            )
            icd9 = f"(c.vocabulary_id LIKE 'ICD9CM' AND ({icd9_clause}))"
        if icd_codes.get("icd10", None) is not None:
            icd10_clause = " OR ".join(
                [
                    "co.CONDITION_SOURCE_VALUE LIKE '" + c + "'"
                    for c in icd_codes["icd10"]
                ]
            )
            icd10 = f"(c.vocabulary_id LIKE 'ICD10CM' AND ({icd10_clause}))"
    return f"{icd9} OR {icd10}"
