from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceTarget:
    identifier: str
    company: str


# These are public careers boards only. Replace or extend them in .data/settings.json.
DEFAULT_GREENHOUSE_BOARDS = (
    SourceTarget("cloudflare", "Cloudflare"),
    SourceTarget("datadog", "Datadog"),
    SourceTarget("figma", "Figma"),
    SourceTarget("hashicorp", "HashiCorp"),
    SourceTarget("stripe", "Stripe"),
)

DEFAULT_LEVER_SITES = (
    SourceTarget("Flex", "Flex"),
    SourceTarget("coderpad", "CoderPad"),
    SourceTarget("360learning", "360Learning"),
    SourceTarget("sysdig", "Sysdig"),
)
