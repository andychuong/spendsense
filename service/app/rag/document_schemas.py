"""Document schemas for the RAG knowledge base."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class DocumentSchema:
    """Base schema for knowledge base documents."""
    id: str
    content: str
    type: str
    created_at: str = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for vector store."""
        return asdict(self)


@dataclass
class UserScenarioDocument(DocumentSchema):
    """Schema for user scenario documents (successful cases)."""
    type: str = "user_scenario"
    persona: Optional[str] = None
    persona_ids: Optional[List[int]] = None
    signals_summary: Optional[Dict[str, Any]] = None
    recommendation_title: Optional[str] = None
    recommendation_type: Optional[str] = None
    feedback_rating: Optional[int] = None
    action_taken: Optional[bool] = None
    user_id: Optional[str] = None
    recommendation_id: Optional[str] = None


@dataclass
class EducationContentDocument(DocumentSchema):
    """Schema for education content documents."""
    type: str = "education_content"
    title: Optional[str] = None
    topic: Optional[str] = None
    persona_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    engagement_metrics: Optional[Dict[str, float]] = None


@dataclass
class PartnerOfferDocument(DocumentSchema):
    """Schema for partner offer documents."""
    type: str = "partner_offer"
    title: Optional[str] = None
    offer_category: Optional[str] = None
    persona_ids: Optional[List[int]] = None
    eligibility_requirements: Optional[Dict[str, Any]] = None
    engagement_metrics: Optional[Dict[str, float]] = None


@dataclass
class OperatorDecisionDocument(DocumentSchema):
    """Schema for operator decision documents (learning from overrides)."""
    type: str = "operator_decision"
    scenario_description: Optional[str] = None
    original_recommendation: Optional[str] = None
    operator_action: Optional[str] = None  # "approved", "rejected", "modified"
    reasoning: Optional[str] = None
    approved_alternative: Optional[str] = None
    operator_id: Optional[str] = None
    recommendation_id: Optional[str] = None


@dataclass
class FinancialStrategyDocument(DocumentSchema):
    """Schema for general financial strategy/domain knowledge documents."""
    type: str = "financial_strategy"
    strategy_name: Optional[str] = None
    category: Optional[str] = None  # "debt", "savings", "budgeting", "credit"
    effective_for: Optional[Dict[str, Any]] = None
    persona_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None


@dataclass
class FeedbackInsightDocument(DocumentSchema):
    """Schema for aggregated feedback insights."""
    type: str = "feedback_insight"
    insight_type: Optional[str] = None  # "positive_pattern", "negative_pattern", "improvement"
    pattern_description: Optional[str] = None
    affected_personas: Optional[List[str]] = None
    recommendation_types: Optional[List[str]] = None
    sample_size: Optional[int] = None
    avg_rating: Optional[float] = None


def create_user_scenario_document(
    user_profile: Any,
    recommendation: Any,
    feedback: Optional[Any] = None,
) -> UserScenarioDocument:
    """
    Create a user scenario document from database models.
    
    Args:
        user_profile: UserProfile model instance
        recommendation: Recommendation model instance
        feedback: RecommendationFeedback model instance (optional)
    
    Returns:
        UserScenarioDocument
    """
    # Get persona information
    personas = []
    persona_ids = []
    if hasattr(user_profile, 'persona_assignments'):
        for assignment in user_profile.persona_assignments:
            personas.append(assignment.persona.name)
            persona_ids.append(assignment.persona_id)
    
    primary_persona = personas[0] if personas else None
    
    # Summarize signals
    signals_summary = {}
    if user_profile.signals_30d:
        signals_30d = user_profile.signals_30d
        
        # Credit signals
        if "credit" in signals_30d:
            credit = signals_30d["credit"]
            if credit.get("avg_utilization"):
                signals_summary["credit_utilization"] = f"{credit['avg_utilization']:.0%}"
            if credit.get("cards_with_interest"):
                signals_summary["interest_charges"] = len(credit["cards_with_interest"])
        
        # Subscription signals
        if "subscriptions" in signals_30d:
            subs = signals_30d["subscriptions"]
            if subs.get("subscription_count"):
                signals_summary["subscriptions"] = subs["subscription_count"]
                signals_summary["subscription_spend"] = f"${subs.get('total_recurring_spend', 0):.0f}/mo"
        
        # Savings signals
        if "savings" in signals_30d:
            savings = signals_30d["savings"]
            if savings.get("emergency_fund_coverage_months") is not None:
                signals_summary["emergency_fund"] = f"{savings['emergency_fund_coverage_months']:.1f} months"
        
        # Income signals
        if "income" in signals_30d:
            income = signals_30d["income"]
            if income.get("payment_frequency"):
                signals_summary["income_pattern"] = income["payment_frequency"]
    
    # Build content description
    content_parts = [f"User scenario: {recommendation.title}"]
    
    # Add persona context
    if personas:
        content_parts.append(f"Personas: {', '.join(personas)}")
    
    # Add signal details
    if signals_summary:
        signal_strs = [f"{k}: {v}" for k, v in signals_summary.items()]
        content_parts.append("Signals: " + ", ".join(signal_strs))
    
    # Add recommendation
    content_parts.append(f"Recommendation: {recommendation.title}")
    if recommendation.rationale:
        content_parts.append(f"Rationale: {recommendation.rationale[:200]}...")
    
    # Add feedback if available
    if feedback:
        content_parts.append(f"User feedback: {feedback.rating}/5 stars")
        if feedback.comments:
            content_parts.append(f"Comments: {feedback.comments}")
        content_parts.append(f"Action taken: {'Yes' if feedback.helpful else 'No'}")
    
    content = "\n".join(content_parts)
    
    return UserScenarioDocument(
        id=f"scenario_{user_profile.user_id}_{recommendation.recommendation_id}",
        content=content,
        persona=primary_persona,
        persona_ids=persona_ids,
        signals_summary=signals_summary,
        recommendation_title=recommendation.title,
        recommendation_type=recommendation.type,
        feedback_rating=feedback.rating if feedback else None,
        action_taken=feedback.helpful if feedback else None,
        user_id=str(user_profile.user_id),
        recommendation_id=str(recommendation.recommendation_id),
    )


def create_education_content_document(catalog_item: Dict[str, Any]) -> EducationContentDocument:
    """
    Create an education content document from catalog item.
    
    Args:
        catalog_item: Education item from EDUCATION_CATALOG
    
    Returns:
        EducationContentDocument
    """
    content = f"{catalog_item['title']}\n\n{catalog_item['content']}"
    
    return EducationContentDocument(
        id=catalog_item["id"],
        content=content,
        title=catalog_item["title"],
        topic=catalog_item.get("topic"),
        persona_ids=catalog_item.get("persona_ids", []),
        tags=catalog_item.get("tags", []),
    )


def create_operator_decision_document(
    recommendation: Any,
    original_status: str,
    new_status: str,
    operator_notes: Optional[str] = None,
) -> OperatorDecisionDocument:
    """
    Create an operator decision document from recommendation override.
    
    Args:
        recommendation: Recommendation model instance
        original_status: Original recommendation status
        new_status: New status after operator action
        operator_notes: Operator's notes/reasoning
    
    Returns:
        OperatorDecisionDocument
    """
    # Determine action
    action = "approved" if new_status == "approved" else "rejected" if new_status == "rejected" else "modified"
    
    # Build scenario description from decision trace
    scenario_parts = []
    if recommendation.decision_trace:
        trace = recommendation.decision_trace
        
        if "persona_assignment" in trace:
            persona_info = trace["persona_assignment"]
            scenario_parts.append(f"Persona: {persona_info.get('persona_name', 'Unknown')}")
            
            if "criteria_met" in persona_info:
                criteria = persona_info["criteria_met"]
                scenario_parts.append(f"Criteria: {', '.join(criteria)}")
    
    scenario_parts.append(f"Recommendation: {recommendation.title}")
    if recommendation.rationale:
        scenario_parts.append(f"Original rationale: {recommendation.rationale[:150]}...")
    
    scenario_description = "\n".join(scenario_parts)
    
    # Build content
    content_parts = [
        f"Operator Decision: {action.upper()}",
        f"Scenario: {scenario_description}",
    ]
    
    if operator_notes:
        content_parts.append(f"Operator reasoning: {operator_notes}")
    
    content = "\n".join(content_parts)
    
    return OperatorDecisionDocument(
        id=f"operator_decision_{recommendation.recommendation_id}",
        content=content,
        scenario_description=scenario_description,
        original_recommendation=recommendation.title,
        operator_action=action,
        reasoning=operator_notes,
        recommendation_id=str(recommendation.recommendation_id),
    )

