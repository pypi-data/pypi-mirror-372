from typing import List

from deepteam.vulnerabilities import (
    BaseVulnerability,
    Bias,
    Toxicity,
    Misinformation,
    IllegalActivity,
    PromptLeakage,
    PIILeakage,
    ExcessiveAgency,
    Robustness,
    IntellectualProperty,
    Competition,
    GraphicContent,
    PersonalSafety,
    RBAC,
    BOLA,
    BFLA,
    SSRF,
    DebugAccess,
    ShellInjection,
    SQLInjection,
)

from deepteam.attacks import BaseAttack
from deepteam.attacks.single_turn import (
    Base64,
    GrayBox,
    Leetspeak,
    MathProblem,
    Multilingual,
    PromptInjection,
    PromptProbing,
    Roleplay,
    ROT13,
)

from deepteam.attacks.multi_turn import (
    CrescendoJailbreaking,
    LinearJailbreaking,
    TreeJailbreaking,
    SequentialJailbreak,
    BadLikertJudge,
)


def _get_owasp_vulnerabilities() -> List[BaseVulnerability]:
    """
    Get vulnerabilities based on OWASP Top 10 for LLMs 2025.

    Reference: docs/red-teaming-owasp-top-10-for-llms.mdx
    """
    return [
        # 1. Prompt Injection - Handled by attacks, not vulnerabilities
        # 2. Sensitive Information Disclosure
        PIILeakage(
            types=[
                "direct disclosure",
                "api and database access",
                "session leak",
                "social manipulation",
            ]
        ),
        PromptLeakage(
            types=[
                "secrets and credentials",
                "instructions",
                "guard exposure",
                "permissions and roles",
            ]
        ),
        IntellectualProperty(
            types=[
                "imitation",
                "copyright violations",
                "trademark infringement",
                "patent disclosure",
            ]
        ),
        # 3. Supply Chain - Not directly testable via attacks
        # 4. Data and Model Poisoning
        Bias(types=["race", "gender", "religion", "politics"]),
        Toxicity(types=["profanity", "insults", "threats", "mockery"]),
        Misinformation(
            types=[
                "factual errors",
                "unsupported claims",
                "expertize misrepresentation",
            ]
        ),
        IllegalActivity(
            types=[
                "cybercrime",
                "violent crimes",
                "non violent crimes",
                "illegal drugs",
            ]
        ),
        GraphicContent(
            types=["sexual content", "graphic content", "pornographic content"]
        ),
        PersonalSafety(
            types=[
                "bullying",
                "self-harm",
                "unsafe practices",
                "dangerous challenges",
            ]
        ),
        # 5. Improper Output Handling - Not directly testable via attacks
        # 6. Excessive Agency
        ExcessiveAgency(types=["functionality", "permissions", "autonomy"]),
        # 7. System Prompt Leakage (covered under Sensitive Information Disclosure)
        # 8. Vector and Embedding Weaknesses - Not directly testable via attacks
        # 9. Misinformation (already covered above)
        Competition(types=["discreditation"]),
        # 10. Unbounded Consumption - Not directly testable via attacks
        # Additional OWASP-related vulnerabilities
        RBAC(
            types=[
                "role bypass",
                "privilege escalation",
                "unauthorized role assumption",
            ]
        ),
        DebugAccess(
            types=[
                "debug_mode_bypass",
                "development_endpoint_access",
                "administrative_interface_exposure",
            ]
        ),
        ShellInjection(
            types=[
                "command_injection",
                "system_command_execution",
                "shell_escape_sequences",
            ]
        ),
        SQLInjection(
            types=[
                "blind_sql_injection",
                "union_based_injection",
                "error_based_injection",
            ]
        ),
        BFLA(
            types=[
                "privilege_escalation",
                "function_bypass",
                "authorization_bypass",
            ]
        ),
        BOLA(
            types=[
                "object_access_bypass",
                "cross_customer_access",
                "unauthorized_object_manipulation",
            ]
        ),
        SSRF(
            types=[
                "internal_service_access",
                "cloud_metadata_access",
                "port_scanning",
            ]
        ),
        Robustness(types=["hijacking", "input overreliance"]),
    ]


def _get_owasp_attacks() -> List[BaseAttack]:
    """
    Get attacks relevant for OWASP Top 10 for LLMs testing.
    """
    return [
        # Core injection attacks
        PromptInjection(weight=3),
        # Encoding-based attacks for bypassing filters
        Base64(weight=2),
        ROT13(weight=2),
        Leetspeak(weight=2),
        # Social engineering attacks
        Roleplay(
            weight=2,
            role="learned gentleman of natural philosophy",
            persona="1600s Shakespearean scholar",
        ),
        PromptProbing(weight=2),
        # Multilingual and obfuscation attacks
        Multilingual(weight=2),
        MathProblem(weight=1),
        # Gray box attacks for known vulnerabilities
        GrayBox(weight=2),
        # Multi-turn sophisticated attacks
        CrescendoJailbreaking(weight=2),
        LinearJailbreaking(weight=2),
        TreeJailbreaking(weight=1),
        SequentialJailbreak(weight=2),
        BadLikertJudge(weight=1),
    ]
