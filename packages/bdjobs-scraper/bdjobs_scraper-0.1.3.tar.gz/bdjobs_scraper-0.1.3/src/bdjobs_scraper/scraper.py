from .parse_id import _parse_id
from .request_details import _request_details
from .clean_html import _clean_html

def scrape_by_url(url:str)-> str:
    try:
        parsed = _parse_id(url)
        if parsed["error"]:
            raise ValueError(parsed["error"])

        job_id = parsed["id"]
        job_details = _request_details(job_id)
        if job_details.get("statuscode") == "0" and job_details.get("data"):
            fields_to_clean = [
                "JobDescription",
                "EducationRequirements",
                "experience",
                "AdditionJobRequirements",
                "JobOtherBenifits",
                "JobKeyPoints",
                "ApplyInstruction",
            ]

            first_job = job_details["data"][0]

            for field in fields_to_clean:
                if field in first_job and first_job[field]:
                    first_job[field] = _clean_html(str(first_job[field]))
            return first_job
        else:
            raise ValueError(f"Failed to retrieve job details for ID {job_id}")
    except Exception as e:
        return {"error": e}
