"""HTTP utilities for the Nekuda SDK."""

from typing import Optional
from urllib.parse import urlparse, urlunparse


def normalize_url(url: Optional[str]) -> str:
    """Normalize a URL by adding protocol if missing and removing trailing slashes.

    Args:
        url: The URL to normalize

    Returns:
        Normalized URL string

    Raises:
        ValueError: If URL is None, empty, or invalid
    """
    if url is None:
        raise ValueError("URL cannot be None")

    if not url:
        raise ValueError("URL cannot be empty")

    # Strip whitespace
    url = url.strip()

    # Check for obviously invalid URLs (containing spaces after stripping)
    if " " in url:
        raise ValueError("Invalid URL: URLs cannot contain spaces")

    # Add https:// if no protocol specified
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")

    # Validate that we have at least a netloc
    if not parsed.netloc:
        raise ValueError("Invalid URL: no host specified")

    # Additional validation for netloc
    # Check if netloc has valid format (basic check)
    if (
        not parsed.netloc.replace(".", "")
        .replace(":", "")
        .replace("-", "")
        .replace("_", "")
        .replace("[", "")
        .replace("]", "")
        .isalnum()
    ):
        raise ValueError("Invalid URL: invalid host format")

    # Remove trailing slashes from path
    path = parsed.path.rstrip("/")

    # Reconstruct the URL
    normalized = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )

    return normalized
