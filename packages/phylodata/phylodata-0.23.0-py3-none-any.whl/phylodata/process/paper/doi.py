import re

DOI_REGEX = r"^https?:\/\/(?:www\.)?(?:dx\.)?doi\.org\/10\.\d{4,}\/[^\s]+$"


def is_doi(doi: str) -> bool:
    """Checks whether the given string is a valid DOI URL."""
    pattern = re.compile(DOI_REGEX)
    return bool(pattern.match(doi))
