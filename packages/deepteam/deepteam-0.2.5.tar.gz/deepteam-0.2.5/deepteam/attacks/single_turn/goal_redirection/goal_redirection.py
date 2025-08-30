import random

from deepteam.attacks import BaseAttack
from deepteam.attacks.single_turn.goal_redirection.template import (
    GoalRedirectionTemplate,
)


class GoalRedirection(BaseAttack):
    def __init__(self, weight: int = 1, max_retries: int = 3):
        self.weight = weight
        self.max_retries = max_retries

    def enhance(self, attack: str) -> str:
        """
        Enhance the given attack with goal redirection techniques.
        Uses max_retries to attempt different redirection methods if enhancement fails.
        """
        enhancement_methods = [
            GoalRedirectionTemplate.enhance_ambiguous_framing,
            GoalRedirectionTemplate.enhance_operational_alignment,
            GoalRedirectionTemplate.enhance_constraint_confusion,
            GoalRedirectionTemplate.enhance_goal_drift,
            GoalRedirectionTemplate.enhance_scope_expansion,
            GoalRedirectionTemplate.enhance_operational_alignment,
        ]

        for _ in range(self.max_retries):
            try:
                # Randomly select an enhancement method
                method = random.choice(enhancement_methods)
                enhanced_attack = method(attack)

                # Basic validation - ensure the enhancement actually modified the attack
                if enhanced_attack and len(enhanced_attack.strip()) > len(
                    attack.strip()
                ):
                    return enhanced_attack

            except Exception:
                # If enhancement fails, try again with a different method
                continue

        # If all retries fail, return the original attack
        return attack

    def get_name(self) -> str:
        return "Goal Redirection"
