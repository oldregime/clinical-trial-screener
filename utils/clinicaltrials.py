import requests
from typing import Optional

BASE_URL = "https://clinicaltrials.gov/api/v2"

def search_trials(query: str, max_results: int = 10, status: str = "RECRUITING") -> list[dict]:
    """Search ClinicalTrials.gov API v2 for clinical trials."""
    try:
        params = {
            "query.cond": query,
            "filter.overallStatus": status,
            "pageSize": min(max_results, 20),
            "fields": "NCTId,BriefTitle,OverallStatus,Phase,Condition,EligibilityCriteria,LocationCity,LocationState,LocationCountry",
            "sort": "@relevance",
        }
        response = requests.get(f"{BASE_URL}/studies", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        trials = []
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            id_module = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            design_module = protocol.get("designModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            eligibility_module = protocol.get("eligibilityModule", {})
            contacts_module = protocol.get("contactsLocationsModule", {})
            
            # Extract locations
            locations = []
            for loc in contacts_module.get("locations", [])[:5]:
                city = loc.get("city", "")
                state = loc.get("state", "")
                country = loc.get("country", "")
                parts = [p for p in [city, state, country] if p]
                if parts:
                    locations.append(", ".join(parts))
            
            phases = design_module.get("phases", [])
            
            trial = {
                "nct_id": id_module.get("nctId", ""),
                "title": id_module.get("briefTitle", ""),
                "status": status_module.get("overallStatus", ""),
                "phase": ", ".join(phases) if phases else "N/A",
                "conditions": conditions_module.get("conditions", []),
                "eligibility_criteria": eligibility_module.get("eligibilityCriteria", ""),
                "locations": locations,
            }
            trials.append(trial)
        
        return trials
    except requests.RequestException as e:
        print(f"Error searching ClinicalTrials.gov: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
