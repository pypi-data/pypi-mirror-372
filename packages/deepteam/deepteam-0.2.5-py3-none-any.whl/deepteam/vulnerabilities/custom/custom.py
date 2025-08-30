from typing import List, Optional
from enum import Enum

from deepteam.vulnerabilities import BaseVulnerability
from deepteam.metrics import BaseRedTeamingMetric


class CustomVulnerability(BaseVulnerability):
    """
    Custom vulnerability class that allows users to define their own vulnerability types.
    """

    def __init__(
        self,
        name: str,
        criteria: str,
        types: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None,
        metric: Optional[BaseRedTeamingMetric] = None,
    ):
        self.name = name

        if types:
            self.types = Enum(
                f"CustomVulnerabilityType", {t.upper(): t for t in types}
            )

        self.custom_prompt = custom_prompt
        self.metric = metric
        self.criteria = criteria.strip()
        super().__init__(self.types)

    def get_name(self) -> str:
        return self.name

    def get_custom_prompt(self) -> Optional[str]:
        return self.custom_prompt

    def get_metric(self) -> Optional[BaseRedTeamingMetric]:
        return self.metric

    def get_criteria(self) -> str:
        return self.criteria
