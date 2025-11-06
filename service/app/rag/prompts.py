"""Prompt templates for RAG-based recommendation generation."""

from typing import Dict, Any, List
import json


def build_system_prompt() -> str:
    """
    Build system prompt for recommendation generation.
    
    Returns:
        System prompt string
    """
    return """You are a financial education advisor helping users improve their financial health.

Your role is to:
- Provide clear, actionable financial education (NOT financial advice)
- Use plain language without jargon
- Be empowering and supportive (never judgmental or shaming)
- Cite specific data points from the user's situation
- Base recommendations on proven strategies and similar success cases
- Include clear "because" rationales explaining why each recommendation is relevant

Important guidelines:
- This is EDUCATION, not financial advice
- Never tell users what to do - provide information to help them decide
- Use empowering language: "You could consider..." not "You should..."
- Avoid shame-based language about debt or spending
- Focus on actionable steps and concrete strategies
- Reference similar user success stories when available

Always include this disclaimer: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
"""


def build_recommendation_prompt(
    user_context: Dict[str, Any],
    retrieved_context: Dict[str, Any],
    recommendation_count: int = 5,
) -> str:
    """
    Build prompt for generating recommendations with retrieved context.
    
    Args:
        user_context: User profile information (personas, signals)
        retrieved_context: Retrieved documents from knowledge base
        recommendation_count: Number of recommendations to generate
    
    Returns:
        Complete prompt for LLM
    """
    # Extract user information
    personas = user_context.get("personas", [])
    signals_30d = user_context.get("signals_30d", {})
    signals_180d = user_context.get("signals_180d", {})
    
    # Build user situation summary
    situation_parts = []
    
    if personas:
        situation_parts.append(f"**User Personas**: {', '.join(personas)}")
    
    # Credit situation
    if "credit" in signals_30d:
        credit = signals_30d["credit"]
        if credit.get("avg_utilization"):
            situation_parts.append(f"- Credit utilization: {credit['avg_utilization']:.0%}")
        if credit.get("cards_with_interest"):
            situation_parts.append(f"- Paying interest on {len(credit['cards_with_interest'])} card(s)")
        if credit.get("total_credit_balance"):
            situation_parts.append(f"- Total credit card balance: ${credit['total_credit_balance']:,.0f}")
    
    # Subscription situation
    if "subscriptions" in signals_30d:
        subs = signals_30d["subscriptions"]
        if subs.get("subscription_count"):
            situation_parts.append(f"- Active subscriptions: {subs['subscription_count']}")
        if subs.get("total_recurring_spend"):
            situation_parts.append(f"- Monthly recurring spend: ${subs['total_recurring_spend']:,.0f}")
    
    # Savings situation
    if "savings" in signals_30d:
        savings = signals_30d["savings"]
        if savings.get("emergency_fund_coverage_months") is not None:
            situation_parts.append(f"- Emergency fund coverage: {savings['emergency_fund_coverage_months']:.1f} months")
        if savings.get("total_savings_balance"):
            situation_parts.append(f"- Total savings: ${savings['total_savings_balance']:,.0f}")
    
    # Income situation
    if "income" in signals_30d:
        income = signals_30d["income"]
        if income.get("payment_frequency"):
            situation_parts.append(f"- Income pattern: {income['payment_frequency']}")
        if income.get("cash_flow_buffer_months") is not None:
            situation_parts.append(f"- Cash flow buffer: {income['cash_flow_buffer_months']:.1f} months")
    
    user_situation = "\n".join(situation_parts)
    
    # Build retrieved context summary
    context_summary = []
    
    if retrieved_context.get("documents"):
        context_summary.append(f"**Retrieved Knowledge** ({len(retrieved_context['documents'])} relevant items):\n")
        
        for i, doc in enumerate(retrieved_context["documents"][:5], 1):
            doc_type = doc["metadata"].get("type", "unknown")
            similarity = doc["similarity"]
            
            context_summary.append(f"{i}. [{doc_type.upper()}] (relevance: {similarity:.2f})")
            context_summary.append(f"   {doc['content'][:300]}...")
            context_summary.append("")
    
    retrieved_knowledge = "\n".join(context_summary)
    
    # Build the full prompt
    prompt = f"""# Task: Generate Personalized Financial Education Recommendations

## User Situation
{user_situation}

## Retrieved Relevant Knowledge
{retrieved_knowledge}

## Your Task
Based on the user's situation and the retrieved knowledge above, generate {recommendation_count} personalized financial education recommendations.

For EACH recommendation, provide:

1. **title**: Clear, actionable title (50-80 characters)
2. **content**: Detailed educational content (300-500 words)
   - Explain the concept clearly
   - Provide specific, actionable steps
   - Reference relevant information from the retrieved knowledge
   - Use empowering, supportive language
3. **rationale**: "Because" explanation citing specific user data (2-3 sentences)
   - Start with "Because..."
   - Cite specific numbers, percentages, or timeframes from user situation
   - Explain why this is relevant NOW for THIS user
4. **priority**: "high", "medium", or "low" based on urgency
5. **expected_impact**: What outcome this could achieve (1-2 sentences)
6. **category**: One of: "debt", "savings", "budgeting", "credit", "subscriptions", "income"

## Output Format
Return a JSON array with this exact structure:

```json
[
  {{
    "title": "Clear, Actionable Title",
    "content": "Detailed educational content explaining the concept, providing specific steps, and referencing relevant knowledge. Use plain language, be supportive, focus on empowerment...",
    "rationale": "Because [cite specific user data], [explain relevance], [connect to outcome].",
    "priority": "high",
    "expected_impact": "This could help you [specific outcome] within [timeframe].",
    "category": "debt"
  }}
]
```

## Important Guidelines
- Make content specific to THIS user's situation using the data provided
- Reference numbers, percentages, timeframes from their actual situation
- Connect recommendations to the retrieved knowledge when relevant
- Use empowering language: "you could", "consider", "one approach is"
- Avoid prescriptive language: "you should", "you must", "you need to"
- Focus on education and information, not directives
- Be supportive and non-judgmental about their current situation

## Remember
End each recommendation content with: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."

Generate {recommendation_count} recommendations now:"""
    
    return prompt


def build_partner_offer_prompt(
    user_context: Dict[str, Any],
    retrieved_offers: List[Dict[str, Any]],
    count: int = 3,
) -> str:
    """
    Build prompt for generating partner offer recommendations.
    
    Args:
        user_context: User profile information
        retrieved_offers: Retrieved partner offers from knowledge base
        count: Number of offers to generate
    
    Returns:
        Prompt for partner offer generation
    """
    personas = user_context.get("personas", [])
    signals_30d = user_context.get("signals_30d", {})
    
    # Build user situation
    situation_parts = []
    if personas:
        situation_parts.append(f"User personas: {', '.join(personas)}")
    
    # Key financial indicators
    if "credit" in signals_30d:
        credit = signals_30d["credit"]
        if credit.get("avg_utilization"):
            situation_parts.append(f"Credit utilization: {credit['avg_utilization']:.0%}")
    
    if "savings" in signals_30d:
        savings = signals_30d["savings"]
        if savings.get("emergency_fund_coverage_months") is not None:
            situation_parts.append(f"Emergency fund: {savings['emergency_fund_coverage_months']:.1f} months")
    
    user_situation = "\n".join(situation_parts)
    
    # Format retrieved offers
    offers_text = []
    for i, offer in enumerate(retrieved_offers[:count], 1):
        offers_text.append(f"{i}. {offer['metadata'].get('title', 'Offer')}")
        offers_text.append(f"   {offer['content'][:200]}...")
        offers_text.append("")
    
    offers_summary = "\n".join(offers_text)
    
    prompt = f"""# Task: Generate Partner Offer Recommendations

## User Situation
{user_situation}

## Available Partner Offers
{offers_summary}

## Your Task
For each of the {count} most relevant partner offers above, generate a personalized recommendation that:

1. **title**: Offer title (use the original title)
2. **content**: Why this offer is relevant to this user (150-250 words)
   - Explain how it addresses their specific situation
   - Cite specific user data points
   - Highlight key benefits for their situation
   - Include eligibility information
3. **rationale**: "Because" explanation (2-3 sentences)
   - Cite specific numbers from user situation
   - Explain why this offer matches their needs
4. **priority**: "high", "medium", or "low"
5. **expected_impact**: Potential benefit (1-2 sentences with estimates if possible)

## Output Format
JSON array format (same as education recommendations).

## Guidelines
- Match offers to user's actual financial situation
- Be specific about how the offer helps
- Include eligibility requirements
- Estimate potential savings or benefits when possible
- Use supportive, informative language

Generate {count} partner offer recommendations:"""
    
    return prompt


def build_rationale_enhancement_prompt(
    recommendation_title: str,
    user_data: Dict[str, Any],
    existing_rationale: str = "",
) -> str:
    """
    Build prompt for enhancing recommendation rationales.
    
    Args:
        recommendation_title: Title of the recommendation
        user_data: User data to cite
        existing_rationale: Optional existing rationale to enhance
    
    Returns:
        Prompt for rationale enhancement
    """
    prompt = f"""# Task: Generate a Clear, Data-Driven Rationale

## Recommendation
{recommendation_title}

## User Data Available
{json.dumps(user_data, indent=2)}

## Current Rationale (if any)
{existing_rationale or "None - need to create from scratch"}

## Your Task
Generate a compelling "because" rationale that:
- Starts with "Because..."
- Cites specific numbers, percentages, or timeframes from user data
- Explains why this recommendation is relevant NOW
- Is 2-3 sentences maximum
- Uses concrete data points (not vague statements)

## Example Good Rationales
- "Because your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit), you're paying $87/month in interest charges. Reducing utilization below 30% could improve your credit score and save you over $1,000 annually."
- "Because you have 8 active subscriptions totaling $127/month (15% of your spending), and haven't used 3 of them in the past 30 days, a subscription audit could free up $40-60/month for your emergency fund."
- "Because your income arrives every 45-60 days but your cash flow buffer is only 0.8 months of expenses, building a 1-2 month buffer would smooth out the gaps between payments."

## Example Bad Rationales
- "Because you have high credit utilization." (not specific)
- "Because you might benefit from this." (no data cited)
- "Because experts recommend this approach." (not personalized)

Generate a specific, data-driven rationale:"""
    
    return prompt

