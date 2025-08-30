import random

from deepteam.attacks import BaseAttack
from deepteam.attacks.single_turn.semantic_manipulation.template import (
    LinguisticConfusionTemplate,
)


class LinguisticConfusion(BaseAttack):
    def __init__(self, weight: int = 1, max_retries: int = 3):
        self.weight = weight
        self.max_retries = max_retries

    def enhance(self, attack: str) -> str:
        """
        Enhance the given attack with linguistic confusion techniques.
        Uses max_retries to attempt different confusion methods if enhancement fails.
        """
        enhancement_methods = [
            LinguisticConfusionTemplate.enhance_semantic_ambiguity,
            LinguisticConfusionTemplate.enhance_syntactic_variation,
            LinguisticConfusionTemplate.enhance_contextual_reframing,
            LinguisticConfusionTemplate.enhance_obfuscation_decoding,
            LinguisticConfusionTemplate.enhance_pragmatic_inference,
            LinguisticConfusionTemplate.enhance_universal_translation,
        ]

        for attempt in range(self.max_retries):
            try:
                method = random.choice(enhancement_methods)
                enhanced_attack = method(attack)
                if enhanced_attack and len(enhanced_attack.strip()) > len(
                    attack.strip()
                ):
                    return enhanced_attack

            except Exception:
                continue

        return attack

    def get_name(self) -> str:
        return "Linguistic Confusion"
