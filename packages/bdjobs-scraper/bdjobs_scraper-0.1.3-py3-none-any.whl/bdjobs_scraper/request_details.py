import requests
import json

def _request_details(id):
    try:
        url = f"https://gateway.bdjobs.com/ActtivejobsTest/api/JobSubsystem/jobDetails?jobId={id}"
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise ValueError(response.status_code)
    except Exception as e:
            return {"error": f"Failed to fetch.", "desc": str(e)}
