from urllib.parse import urlparse, parse_qs
def _parse_id(url):
    parsed_url = urlparse(url)
    try:
        if not parsed_url.netloc.endswith('bdjobs.com'):
            raise ValueError("Not a bdjobs.com URL")
        if not parsed_url.path.startswith('/jobdetails'):
            raise ValueError("Not a job details URL")
        query_params = parse_qs(parsed_url.query)
        id = query_params.get("id", [None])[0]
        if id is None:
            raise ValueError("Missing 'id' query parameter")
        return {"id": id, "error": None}
    except Exception as e:
        return {"id": None, "error": str(e)}