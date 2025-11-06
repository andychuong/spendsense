"""Helper functions for recommendation API endpoints."""

from typing import Dict, Any, List, Optional


def extract_explanation_from_recommendation(recommendation: Any) -> Optional[Dict[str, Any]]:
    """
    Extract explanation data from a recommendation's decision_trace.
    
    This formats RAG context data into a user-friendly explanation of why
    the recommendation was generated.
    
    Args:
        recommendation: Recommendation model instance
    
    Returns:
        Dictionary with explanation data or None
    """
    if not recommendation.decision_trace:
        return None
    
    trace = recommendation.decision_trace
    explanation = {}
    
    # Extract data citations (specific user data points)
    data_citations = []
    
    # From detected signals
    if "detected_signals" in trace:
        signals = trace["detected_signals"]
        
        # Credit signals
        if "credit" in signals:
            credit = signals["credit"]
            if "avg_utilization" in credit:
                util = credit["avg_utilization"]
                data_citations.append(f"Your credit utilization: {util*100:.0f}%")
            if "total_credit_balance" in credit:
                balance = credit["total_credit_balance"]
                data_citations.append(f"Total credit balance: ${balance:,.2f}")
            if "interest_charges_30d" in credit:
                interest = credit["interest_charges_30d"]
                data_citations.append(f"Interest charges last month: ${interest:,.2f}")
        
        # Income signals
        if "income" in signals:
            income = signals["income"]
            if "payment_frequency" in income:
                freq = income["payment_frequency"]
                data_citations.append(f"Income frequency: {freq}")
            if "median_pay_gap_days" in income:
                gap = income["median_pay_gap_days"]
                data_citations.append(f"Typical pay gap: {gap} days")
        
        # Savings signals
        if "savings" in signals:
            savings = signals["savings"]
            if "net_inflow_monthly" in savings:
                inflow = savings["net_inflow_monthly"]
                data_citations.append(f"Monthly savings: ${inflow:,.2f}")
            if "emergency_fund_coverage_months" in savings:
                coverage = savings["emergency_fund_coverage_months"]
                data_citations.append(f"Emergency fund: {coverage:.1f} months")
        
        # Subscription signals
        if "subscriptions" in signals:
            subs = signals["subscriptions"]
            if "subscription_count" in subs:
                count = subs["subscription_count"]
                data_citations.append(f"Active subscriptions: {count}")
            if "total_recurring_spend" in subs:
                spend = subs["total_recurring_spend"]
                data_citations.append(f"Subscription spending: ${spend:,.2f}/month")
    
    if data_citations:
        explanation["data_citations"] = data_citations
    
    # Extract persona information
    if "persona_assignment" in trace:
        persona = trace["persona_assignment"]
        if "persona_name" in persona:
            explanation["persona"] = persona["persona_name"]
    
    # Extract similar scenarios (if available from RAG)
    if "similar_scenarios" in trace:
        explanation["similar_scenarios"] = trace["similar_scenarios"]
    
    # Extract context used (from RAG generation)
    if "context_used" in trace:
        context = trace["context_used"]
        if "documents_retrieved" in context:
            explanation["context_retrieved"] = context["documents_retrieved"]
        if "similar_users_found" in context:
            explanation["similar_users"] = context["similar_users_found"]
    
    # Extract generation metadata
    if "generation_method" in trace:
        explanation["generation_method"] = trace["generation_method"]
    
    # Extract confidence score (if available)
    if "confidence_score" in trace:
        explanation["confidence"] = trace["confidence_score"]
    
    return explanation if explanation else None


def enrich_recommendation_with_explanation(recommendation_dict: Dict[str, Any], 
                                          recommendation_model: Any) -> Dict[str, Any]:
    """
    Enrich recommendation dictionary with explanation data.
    
    Args:
        recommendation_dict: Dictionary representation of recommendation
        recommendation_model: Original recommendation model instance
    
    Returns:
        Enriched recommendation dictionary
    """
    explanation = extract_explanation_from_recommendation(recommendation_model)
    if explanation:
        recommendation_dict["explanation"] = explanation
    
    return recommendation_dict

