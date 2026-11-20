from typing import NamedTuple

from app.models.security import WafDetection


class WafSignature(NamedTuple):
    name: str
    headers: tuple[str, ...]
    cookies: tuple[str, ...]
    markers: tuple[str, ...]


SIGNATURES = (
    WafSignature(
        "Cloudflare",
        ("cf-ray", "cf-cache-status", "cf-connecting-ip"),
        ("__cf", "_cf_bm"),
        ("cloudflare",),
    ),
    WafSignature(
        "AWS CloudFront/WAF",
        ("x-amz-cf-id", "x-amzn-waf-action", "x-amzn-requestid"),
        ("aws-waf-token",),
        ("cloudfront", "aws waf"),
    ),
    WafSignature(
        "Akamai",
        ("x-akamai-transformed", "x-akamai-config-log-detail"),
        ("ak_bmsc", "bm_sz", "bm_sv"),
        ("akamaighost", "akamai"),
    ),
    WafSignature(
        "Imperva",
        ("x-imperva-waf", "x-iinfo"),
        ("incap_ses_", "visid_incap_", "nlbi_"),
        ("imperva",),
    ),
    WafSignature(
        "Sucuri",
        ("x-sucuri-id", "x-sucuri-cache"),
        ("sucuri_cloudproxy_uuid_",),
        ("sucuri", "cloudproxy"),
    ),
)


def detect_waf(
    headers: dict[str, str],
    cookies: list[dict[str, object]],
) -> list[WafDetection]:
    normalized_headers = {str(key).lower(): str(value) for key, value in headers.items()}
    header_blob = " ".join(
        f"{key}={value}" for key, value in normalized_headers.items()
    ).lower()
    cookie_names = {
        str(cookie.get("name") or "").lower()
        for cookie in cookies
        if isinstance(cookie, dict)
    }

    detections: list[WafDetection] = []
    for signature in SIGNATURES:
        evidence: list[str] = []

        for key in signature.headers:
            if key in normalized_headers:
                evidence.append(f"{key}={normalized_headers[key][:80]}")

        for prefix in signature.cookies:
            matched = next((name for name in cookie_names if name.startswith(prefix)), None)
            if matched:
                evidence.append(f"cookie:{matched}")

        if any(marker in header_blob for marker in signature.markers):
            evidence.append("cabecera coincidente")

        if evidence:
            detections.append(
                WafDetection(
                    name=signature.name,
                    evidence="; ".join(dict.fromkeys(evidence))[:300],
                )
            )

    return detections
