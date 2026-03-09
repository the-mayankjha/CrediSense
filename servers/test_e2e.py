import requests
import json

def run_e2e_test():
    print("--- Step 1: Ingesting Document (paytm_report.pdf) ---")
    url_ingest = "http://127.0.0.1:8000/api/v1/ingest/document"
    try:
        with open("paytm_report.pdf", "rb") as f:
            files = {"file": ("paytm_report.pdf", f, "application/pdf")}
            resp_ingest = requests.post(url_ingest, files=files)
            resp_ingest.raise_for_status()
            ingest_data = resp_ingest.json().get("data", {})
            print("Successfully extracted data from PDF!")
    except FileNotFoundError:
        print("Error: paytm_report.pdf not found. Please run generate_paytm_pdf.py first.")
        return
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ingest API: {e}")
        return

    print("\n--- Step 2: Researching Company (Paytm) ---")
    url_research = "http://127.0.0.1:8000/api/v1/research/company/Paytm"
    try:
        resp_research = requests.get(url_research)
        resp_research.raise_for_status()
        research_data = resp_research.json().get("data", {})
        print("Successfully researched company online!")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Research API: {e}")
        return

    print("\n--- Step 3: Generating CAM ---")
    url_cam = "http://127.0.0.1:8000/api/v1/engine/generate-cam"
    payload = {
        "application_id": "APP-PAYTM-001",
        "company_data": ingest_data,
        "research_data": research_data,
        "primary_insights": "The company has a highly resilient merchant base despite recent setbacks. They hold substantial cash reserves and are quickly onboarding alternate banking partners."
    }
    
    try:
        resp_cam = requests.post(url_cam, json=payload)
        resp_cam.raise_for_status()
        print("\n================ FINAL CAM OUTPUT ================\n")
        print(json.dumps(resp_cam.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error calling Engine API: {e}")
        try:
            print("Server response:", resp_cam.text)
        except:
            pass

if __name__ == "__main__":
    run_e2e_test()
