from bs4 import BeautifulSoup


def _clean_html(value: str) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(separator=" ", strip=True)