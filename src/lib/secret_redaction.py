"""Mask credentials that scanned government pages expose in URLs.

Government sites embed client-side API keys in the resources they load, for
example ``https://maps.googleapis.com/maps/api/js?key=AIza...``.  The scanners
record those URLs, and anything they record can reach the metadata database
artifact, the published JSON/CSV data files or a committed report.  The keys
are already public on the source site, but republishing them adds a copy this
project has no reason to hold, and it raises GitHub secret-scanning alerts.

Two rules apply, with different scopes:

* :func:`redact_url` masks the value of any query-string or fragment parameter
  whose *name* signals a credential (``key``, ``token``, ``access_token`` ...).
  Use it on resource URLs harvested from page content, such as script ``src``
  values.  Do not use it on seed page URLs: some government pages are addressed
  by parameters such as ``?key=SiteNotices_CookiesPolicy``, and masking those
  would break the link.
* :func:`redact_known_formats` masks strings that match the published shape of
  a common credential (Google API key, GitHub token, AWS access key ID and so
  on) wherever they appear.  False positives are rare, so it is safe to run
  over any published file as a final backstop.

The value is replaced by ``REDACTED`` rather than the parameter being dropped,
so a reader can see that the source URL carried a credential and that this
dataset altered it.

Credential formats follow the token prefixes the issuers document, as listed
in GitHub's secret-scanning supported patterns and the gitleaks rule set.
"""

from __future__ import annotations

import re

REDACTED = "REDACTED"

# Parameter names whose values are credentials.  Matched case-insensitively,
# and only as a whole parameter name directly after ``?``, ``&``, ``#`` or
# ``;`` (``;`` covers HTML-escaped ``&amp;``), so ``monkey=`` is not touched.
_SENSITIVE_PARAM_NAMES: tuple[str, ...] = (
    r"key",
    r"api[-_]?key",
    r"token",
    r"access[-_]?token",
    r"auth",
    r"auth[-_]?token",
    r"authorization",
    r"client[-_]?secret",
    r"secret",
    r"password",
    r"passwd",
    r"sig",
    r"signature",
    r"x[-_]amz[-_](?:credential|signature|security[-_]token)",
    r"x[-_]goog[-_](?:credential|signature)",
)

_VALUE_END = r"&#;\s\"'<>"

_SENSITIVE_PARAM_RE = re.compile(
    r"(?P<name>[?&#;](?:" + "|".join(_SENSITIVE_PARAM_NAMES) + r")=)"
    # Skip values that are already masked so repeated runs report nothing.
    rf"(?!{REDACTED}(?:[{_VALUE_END}]|$))"
    rf"[^{_VALUE_END}]+",
    re.IGNORECASE,
)

# Published credential shapes.  The surrounding lookarounds stop a match from
# starting or ending inside a longer token, which keeps false positives rare.
_CREDENTIAL_FORMATS: tuple[str, ...] = (
    r"AIza[0-9A-Za-z_-]{35}",  # Google API key
    r"gh[pousr]_[0-9A-Za-z]{36,}",  # GitHub classic tokens
    r"github_pat_[0-9A-Za-z_]{22,}",  # GitHub fine-grained token
    r"(?:AKIA|ASIA)[0-9A-Z]{16}",  # AWS access key ID
    r"xox[abposr]-[0-9A-Za-z-]{10,}",  # Slack token
    r"(?:sk|rk)_live_[0-9A-Za-z]{16,}",  # Stripe live secret key
    r"(?:pk|sk|tk)\.eyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}",  # Mapbox token
    r"eyJ[0-9A-Za-z_-]{10,}\.eyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}",  # JWT
)

_CREDENTIAL_FORMAT_RE = re.compile(
    r"(?<![0-9A-Za-z_-])(?:" + "|".join(_CREDENTIAL_FORMATS) + r")(?![0-9A-Za-z_-])"
)


def redact_known_formats(text: str) -> tuple[str, int]:
    """Mask every substring of *text* that matches a known credential format.

    Args:
        text: Any text, such as a URL or the contents of a JSON or CSV file.

    Returns:
        The masked text and the number of credentials replaced.
    """
    return _CREDENTIAL_FORMAT_RE.subn(REDACTED, text)


def redact_url(url: str) -> str:
    """Mask credential parameters and known credential formats in *url*.

    Other parameters are left byte-for-byte unchanged, so encodings such as
    ``libraries=places,geometry`` survive.  The function is idempotent.

    Args:
        url: A resource URL harvested from page content.

    Returns:
        The URL with credential values replaced by ``REDACTED``.
    """
    if not url:
        return url
    masked = _SENSITIVE_PARAM_RE.sub(lambda m: m.group("name") + REDACTED, url)
    return redact_known_formats(masked)[0]
