from pydantic import BaseModel
from typing import List

from deepteam.frameworks.utils import (
    _get_owasp_attacks,
    _get_owasp_vulnerabilities,
)
from deepteam.vulnerabilities import (
    BaseVulnerability,
)


from deepteam.attacks import BaseAttack


class AISafetyFramework(BaseModel):
    name: str
    description: str
    vulnerabilities: List[BaseVulnerability]
    attacks: List[BaseAttack]

    class Config:
        arbitrary_types_allowed = True


class OWASPTop10(AISafetyFramework):
    def __init__(self):
        super().__init__(
            name="OWASP",
            description="The OWASP Top 10 for LLMs 2025",
            vulnerabilities=_get_owasp_vulnerabilities(),
            attacks=_get_owasp_attacks(),
        )
