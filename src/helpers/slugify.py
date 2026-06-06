"""Turn arbitrary text into a filename-safe slug."""

import re
import unicodedata


def slugify(text):
    """Lowercase ASCII slug with hyphens, safe for filenames."""
    ascii_text = (unicodedata.normalize("NFKD", text)
                  .encode("ascii", "ignore").decode("ascii"))
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
