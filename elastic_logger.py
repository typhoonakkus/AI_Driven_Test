import requests
from datetime import datetime

def log_to_elastic(analysis_data, test_name):
    url = "http://localhost:9200/test_metrics/_doc"
    payload = {
        "@timestamp": datetime.now().isoformat(),
        "test_name": test_name,
        "classification": analysis_data.get("classification"),
        "root_cause": analysis_data.get("root_cause"),
        "solution": analysis_data.get("solution_suggestion"),
        "environment": "UAT-Demo"
    }
    try:
        requests.post(url, json=payload, timeout=2)
    except:
        print("⚠️ Elastic bağlantısı kurulamadı, veri gönderilemedi.")