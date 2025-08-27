MOCK_RESPONSES = {
    "antibody_A": "AGCTAGCTAGGCTAATGCATCG",
    "antibody_B": "TGCATGCTAGCTAGCTAACGTA",
    "antibody_C": "CGTAGCTAGCTGATCGTACGTA",
}

def get_mock_response(key: str) -> str:
    return MOCK_RESPONSES.get(key, "Unknown antibody sequence")
