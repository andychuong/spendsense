"""Content generation service using OpenAI with fallback to pre-generated templates."""

import logging
from typing import Dict, List, Any, Optional
import uuid

from app.common.openai_client import get_openai_client
from app.recommendations.catalog import (
    EDUCATION_CATALOG,
    PARTNER_OFFER_CATALOG,
    REGULATORY_DISCLAIMER,
)

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Service for generating educational content using OpenAI with template fallback."""

    def __init__(self):
        """Initialize content generator."""
        self.openai_client = get_openai_client()

    def _build_persona_context(self, persona_id: int, signals: Dict[str, Any]) -> str:
        """
        Build context string for persona and signals.

        Args:
            persona_id: Persona ID (1-5)
            signals: Behavioral signals dictionary

        Returns:
            Context string for prompt
        """
        persona_names = {
            1: "High Utilization",
            2: "Variable Income Budgeter",
            3: "Subscription-Heavy",
            4: "Savings Builder",
            5: "Custom Persona",
        }

        persona_name = persona_names.get(persona_id, "Custom Persona")

        context_parts = [
            f"User persona: {persona_name} (Persona {persona_id})",
        ]

        # Add signal summaries
        if signals:
            if "subscriptions" in signals:
                sub_signals = signals["subscriptions"]
                if sub_signals.get("recurring_merchant_count", 0) > 0:
                    context_parts.append(
                        f"- {sub_signals['recurring_merchant_count']} recurring subscriptions detected, "
                        f"monthly recurring spend: ${sub_signals.get('monthly_recurring_spend_30d', 0):.2f}"
                    )

            if "savings" in signals:
                sav_signals = signals["savings"]
                if sav_signals.get("net_inflow_30d", 0) > 0:
                    context_parts.append(
                        f"- Savings net inflow: ${sav_signals.get('net_inflow_30d', 0):.2f}/month, "
                        f"emergency fund coverage: {sav_signals.get('emergency_fund_coverage_30d', 0):.1f} months"
                    )

            if "credit" in signals:
                credit_signals = signals["credit"]
                high_util = credit_signals.get("high_utilization_cards_30d", [])
                if high_util:
                    context_parts.append(
                        f"- {len(high_util)} credit card(s) with utilization ≥50%"
                    )

            if "income" in signals:
                income_signals = signals["income"]
                if income_signals.get("payment_frequency_30d"):
                    context_parts.append(
                        f"- Income pattern: {income_signals.get('payment_frequency_30d')}, "
                        f"cash flow buffer: {income_signals.get('cash_flow_buffer_30d', 0):.1f} months"
                    )

        return "\n".join(context_parts)

    def _build_education_prompt(
        self,
        template_item: Dict[str, Any],
        persona_id: int,
        signals: Dict[str, Any],
    ) -> str:
        """
        Build prompt for generating educational content.

        Args:
            template_item: Template education item from catalog
            persona_id: Persona ID
            signals: Behavioral signals

        Returns:
            Prompt string
        """
        context = self._build_persona_context(persona_id, signals)

        prompt = f"""Generate personalized educational content for a financial recommendation.

Context:
{context}

Topic: {template_item['title']}

Template content (use as reference but personalize based on context):
{template_item['content']}

Requirements:
- Write in plain, friendly language (avoid financial jargon)
- Cite specific data points from the context when relevant
- Keep it empowering and educational (not judgmental)
- Make it actionable with clear steps
- Length: 300-500 words

Generate personalized content that matches the user's persona and behavioral signals:"""

        return prompt

    def _build_partner_offer_prompt(
        self,
        template_offer: Dict[str, Any],
        persona_id: int,
        signals: Dict[str, Any],
    ) -> str:
        """
        Build prompt for generating partner offer content.

        Args:
            template_offer: Template partner offer from catalog
            persona_id: Persona ID
            signals: Behavioral signals

        Returns:
            Prompt string
        """
        context = self._build_persona_context(persona_id, signals)

        prompt = f"""Generate personalized partner offer content for a financial recommendation.

Context:
{context}

Offer: {template_offer['title']}

Template content (use as reference but personalize based on context):
{template_offer['content']}

Requirements:
- Write in plain, friendly language (avoid financial jargon)
- Cite specific data points from the context when relevant
- Keep it empowering and educational (not judgmental)
- Highlight why this offer is relevant to the user's situation
- Include eligibility information if relevant
- Length: 200-400 words

Generate personalized content that matches the user's persona and behavioral signals:"""

        return prompt

    def generate_education_content(
        self,
        template_item: Dict[str, Any],
        persona_id: int,
        signals: Dict[str, Any],
        use_openai: bool = True,
    ) -> str:
        """
        Generate education content using OpenAI or fallback to template.

        Args:
            template_item: Template education item from catalog
            persona_id: Persona ID
            signals: Behavioral signals dictionary
            use_openai: Whether to attempt OpenAI generation (default: True)

        Returns:
            Generated content (from OpenAI or template)
        """
        # Try OpenAI generation if enabled and available
        if use_openai and self.openai_client:
            prompt = self._build_education_prompt(template_item, persona_id, signals)

            generated_content = self.openai_client.generate_content(
                prompt=prompt,
                persona_id=persona_id,
                signals=signals,
                use_cache=True,
            )

            if generated_content:
                logger.info(f"Generated education content using OpenAI for item: {template_item['id']}")
                # Add regulatory disclaimer
                return f"{generated_content}\n\n{REGULATORY_DISCLAIMER}"

        # Fallback to template
        logger.info(f"Using template content for education item: {template_item['id']}")
        return f"{template_item['content']}\n\n{REGULATORY_DISCLAIMER}"

    def generate_partner_offer_content(
        self,
        template_offer: Dict[str, Any],
        persona_id: int,
        signals: Dict[str, Any],
        use_openai: bool = True,
    ) -> str:
        """
        Generate partner offer content using OpenAI or fallback to template.

        Args:
            template_offer: Template partner offer from catalog
            persona_id: Persona ID
            signals: Behavioral signals dictionary
            use_openai: Whether to attempt OpenAI generation (default: True)

        Returns:
            Generated content (from OpenAI or template)
        """
        # Try OpenAI generation if enabled and available
        if use_openai and self.openai_client:
            prompt = self._build_partner_offer_prompt(template_offer, persona_id, signals)

            generated_content = self.openai_client.generate_content(
                prompt=prompt,
                persona_id=persona_id,
                signals=signals,
                use_cache=True,
            )

            if generated_content:
                logger.info(f"Generated partner offer content using OpenAI for offer: {template_offer['id']}")
                # Add regulatory disclaimer
                return f"{generated_content}\n\n{REGULATORY_DISCLAIMER}"

        # Fallback to template
        logger.info(f"Using template content for partner offer: {template_offer['id']}")
        return f"{template_offer['content']}\n\n{REGULATORY_DISCLAIMER}"

    def generate_rationale_content(
        self,
        recommendation: Dict[str, Any],
        persona_id: int,
        signals: Dict[str, Any],
        use_openai: bool = True,
    ) -> Optional[str]:
        """
        Generate rationale content using OpenAI (optional enhancement).

        Note: This is optional and can enhance existing rationale generation.
        The main rationale generation is handled by RationaleGenerator.

        Args:
            recommendation: Recommendation item (education or partner offer)
            persona_id: Persona ID
            signals: Behavioral signals dictionary
            use_openai: Whether to attempt OpenAI generation (default: True)

        Returns:
            Generated rationale enhancement or None
        """
        if not use_openai or not self.openai_client:
            return None

        context = self._build_persona_context(persona_id, signals)

        prompt = f"""Generate a brief, personalized "because" rationale for a financial recommendation.

Context:
{context}

Recommendation: {recommendation.get('title', 'N/A')}

Requirements:
- Write in plain language (avoid financial jargon)
- Cite specific data points (account names, amounts, percentages, dates)
- Keep it empowering and educational (not judgmental)
- Length: 2-3 sentences
- Start with "Because" to explain why this recommendation is relevant

Generate a personalized rationale:"""

        generated_rationale = self.openai_client.generate_content(
            prompt=prompt,
            persona_id=persona_id,
            signals=signals,
            use_cache=True,
        )

        if generated_rationale:
            logger.info("Generated rationale enhancement using OpenAI")
            return generated_rationale

        return None



