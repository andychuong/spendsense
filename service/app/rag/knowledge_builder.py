"""Knowledge base builder for ingesting data into the RAG vector store."""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.rag.vector_store import VectorStore
from app.rag.document_schemas import (
    create_user_scenario_document,
    create_education_content_document,
    create_operator_decision_document,
    FinancialStrategyDocument,
)
from app.recommendations.catalog import EDUCATION_CATALOG, PARTNER_OFFER_CATALOG

# Try to import models from backend
try:
    from backend.app.models.user_profile import UserProfile
    from backend.app.models.recommendation import Recommendation
except ImportError:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app.models.user_profile import UserProfile
    from app.models.recommendation import Recommendation

# Import feedback model if it exists
try:
    from backend.app.models.recommendation_feedback import RecommendationFeedback
    FEEDBACK_MODEL_EXISTS = True
except ImportError:
    FEEDBACK_MODEL_EXISTS = False
    logging.warning("RecommendationFeedback model not found - skipping feedback ingestion")

logger = logging.getLogger(__name__)


class KnowledgeBaseBuilder:
    """
    Builds and maintains the RAG knowledge base.
    
    This class ingests data from multiple sources:
    - User scenarios (successful recommendations with feedback)
    - Education catalog content
    - Partner offers
    - Operator decisions (overrides and modifications)
    - Domain knowledge (financial strategies and best practices)
    
    Example:
        ```python
        from sqlalchemy.orm import Session
        from app.rag import VectorStore
        
        vector_store = VectorStore()
        builder = KnowledgeBaseBuilder(db_session, vector_store)
        
        # Build full knowledge base
        stats = builder.build_full_knowledge_base()
        print(f"Built knowledge base with {stats['total_documents']} documents")
        ```
    """
    
    def __init__(self, db_session: Session, vector_store: VectorStore):
        """
        Initialize knowledge base builder.
        
        Args:
            db_session: SQLAlchemy database session
            vector_store: Initialized VectorStore instance
        """
        self.db = db_session
        self.vector_store = vector_store
    
    async def ingest_user_scenarios(
        self,
        min_feedback_rating: int = 4,
        limit: Optional[int] = None,
    ) -> int:
        """
        Extract successful user scenarios from database.
        
        Creates documents from user profiles with approved recommendations
        and positive feedback (rating >= min_feedback_rating).
        
        Args:
            min_feedback_rating: Minimum feedback rating to include (default: 4)
            limit: Maximum number of scenarios to ingest (default: all)
        
        Returns:
            Number of scenarios ingested
        """
        logger.info("Ingesting user scenarios from database...")
        
        if not FEEDBACK_MODEL_EXISTS:
            logger.warning("Feedback model not available - skipping user scenario ingestion")
            return 0
        
        documents = []
        
        # Get users with recommendations and feedback
        query = self.db.query(UserProfile).join(
            Recommendation,
            UserProfile.user_id == Recommendation.user_id
        ).filter(
            Recommendation.status == "approved"
        )
        
        if limit:
            query = query.limit(limit)
        
        users = query.all()
        
        for user in users:
            # Get approved recommendations
            recommendations = self.db.query(Recommendation).filter(
                Recommendation.user_id == user.user_id,
                Recommendation.status == "approved"
            ).all()
            
            for rec in recommendations:
                # Try to get feedback
                try:
                    feedback = self.db.query(RecommendationFeedback).filter(
                        RecommendationFeedback.recommendation_id == rec.recommendation_id
                    ).first()
                    
                    # Only include if feedback exists and rating is high enough
                    if feedback and feedback.rating >= min_feedback_rating:
                        doc = create_user_scenario_document(user, rec, feedback)
                        documents.append(doc.to_dict())
                        
                except Exception as e:
                    logger.warning(f"Error processing recommendation {rec.recommendation_id}: {e}")
                    continue
        
        if documents:
            count = self.vector_store.add_documents(documents)
            logger.info(f"✓ Ingested {count} user scenarios")
            return count
        else:
            logger.info("No user scenarios with sufficient feedback found")
            return 0
    
    async def ingest_education_content(self) -> int:
        """
        Ingest education catalog content.
        
        Converts EDUCATION_CATALOG items into searchable documents.
        
        Returns:
            Number of education items ingested
        """
        logger.info("Ingesting education catalog content...")
        
        documents = []
        
        for item in EDUCATION_CATALOG:
            try:
                doc = create_education_content_document(item)
                documents.append(doc.to_dict())
            except Exception as e:
                logger.warning(f"Error processing education item {item.get('id')}: {e}")
                continue
        
        if documents:
            count = self.vector_store.add_documents(documents)
            logger.info(f"✓ Ingested {count} education items")
            return count
        else:
            logger.info("No education content found")
            return 0
    
    async def ingest_partner_offers(self) -> int:
        """
        Ingest partner offer catalog.
        
        Converts PARTNER_OFFER_CATALOG items into searchable documents.
        
        Returns:
            Number of partner offers ingested
        """
        logger.info("Ingesting partner offers...")
        
        documents = []
        
        for offer in PARTNER_OFFER_CATALOG:
            try:
                content = f"{offer['title']}\n\n{offer['content']}"
                
                doc = {
                    "id": offer["id"],
                    "content": content,
                    "type": "partner_offer",
                    "title": offer["title"],
                    "persona_ids": offer.get("persona_ids", []),
                    "eligibility_requirements": offer.get("eligibility_requirements", {}),
                    "tags": offer.get("tags", []),
                }
                documents.append(doc)
            except Exception as e:
                logger.warning(f"Error processing partner offer {offer.get('id')}: {e}")
                continue
        
        if documents:
            count = self.vector_store.add_documents(documents)
            logger.info(f"✓ Ingested {count} partner offers")
            return count
        else:
            logger.info("No partner offers found")
            return 0
    
    async def ingest_operator_decisions(
        self,
        limit: Optional[int] = None,
    ) -> int:
        """
        Learn from operator overrides and decisions.
        
        Extracts recommendations where operators made decisions (approve, reject, modify)
        with notes, which provides valuable learning signals.
        
        Args:
            limit: Maximum number of decisions to ingest (default: all)
        
        Returns:
            Number of operator decisions ingested
        """
        logger.info("Ingesting operator decisions...")
        
        documents = []
        
        # Find recommendations with operator notes
        query = self.db.query(Recommendation).filter(
            Recommendation.status.in_(["approved", "rejected"]),
            # Assuming operator_notes field exists or will be added
            # For now, we'll use decision_trace to identify operator involvement
        )
        
        if limit:
            query = query.limit(limit)
        
        recommendations = query.all()
        
        for rec in recommendations:
            try:
                # Check if this was manually reviewed (has decision trace with operator info)
                if rec.decision_trace:
                    # Extract operator notes if available
                    operator_notes = rec.decision_trace.get("operator_notes")
                    
                    # Create document if there's useful info
                    if operator_notes or rec.status in ["rejected", "approved"]:
                        doc = create_operator_decision_document(
                            recommendation=rec,
                            original_status="pending",
                            new_status=rec.status,
                            operator_notes=operator_notes,
                        )
                        documents.append(doc.to_dict())
                        
            except Exception as e:
                logger.warning(f"Error processing operator decision for {rec.recommendation_id}: {e}")
                continue
        
        if documents:
            count = self.vector_store.add_documents(documents)
            logger.info(f"✓ Ingested {count} operator decisions")
            return count
        else:
            logger.info("No operator decisions with notes found")
            return 0
    
    async def ingest_financial_strategies(self) -> int:
        """
        Ingest general financial strategies and domain knowledge.
        
        These are curated best practices and strategies that can be
        referenced when generating recommendations.
        
        Returns:
            Number of strategy documents ingested
        """
        logger.info("Ingesting financial strategies...")
        
        # Curated financial strategies
        strategies = [
            {
                "id": "strategy_debt_snowball",
                "strategy_name": "Debt Snowball Method",
                "category": "debt",
                "content": (
                    "Debt Snowball Method: Pay minimum payments on all debts, then focus all "
                    "extra money on the smallest balance first. When that's paid off, roll that "
                    "payment into the next smallest debt. This builds momentum and motivation "
                    "as you eliminate debts one by one. Best for: People who need motivation "
                    "and psychological wins."
                ),
                "effective_for": {"needs_motivation": True, "multiple_debts": True},
                "persona_ids": [1],  # HIGH_UTILIZATION
                "tags": ["debt", "payoff", "motivation"],
            },
            {
                "id": "strategy_debt_avalanche",
                "strategy_name": "Debt Avalanche Method",
                "category": "debt",
                "content": (
                    "Debt Avalanche Method: Pay minimum payments on all debts, then focus all "
                    "extra money on the highest interest rate debt first. This saves the most "
                    "money in interest charges over time. When the highest-rate debt is paid off, "
                    "move to the next highest rate. Best for: People who want to minimize total "
                    "interest paid and are motivated by math/efficiency."
                ),
                "effective_for": {"high_interest_debt": True, "mathematically_minded": True},
                "persona_ids": [1],  # HIGH_UTILIZATION
                "tags": ["debt", "payoff", "interest"],
            },
            {
                "id": "strategy_balance_transfer",
                "strategy_name": "Balance Transfer Strategy",
                "category": "debt",
                "content": (
                    "Balance Transfer Strategy: Transfer high-interest credit card debt to a card "
                    "with 0% APR promotional period (typically 12-18 months). This stops interest "
                    "charges temporarily, allowing you to pay down principal faster. Critical: "
                    "Pay off the balance before the promotional period ends, and avoid making new "
                    "purchases on the card. Best for: Good credit (670+), high-interest debt, "
                    "ability to pay off during promo period."
                ),
                "effective_for": {"high_interest_debt": True, "good_credit": True, "disciplined": True},
                "persona_ids": [1],  # HIGH_UTILIZATION
                "tags": ["debt", "balance transfer", "credit cards"],
            },
            {
                "id": "strategy_variable_income_buffer",
                "strategy_name": "Variable Income Buffer Strategy",
                "category": "budgeting",
                "content": (
                    "Variable Income Buffer: Create a separate 'income smoothing' account with "
                    "1-2 months of essential expenses. During high-income months, transfer excess "
                    "to the buffer. During low-income months, withdraw from buffer to cover gaps. "
                    "This creates artificial income stability. Different from emergency fund (which "
                    "is for unexpected expenses). Best for: Freelancers, contractors, commission-based "
                    "workers, seasonal income."
                ),
                "effective_for": {"variable_income": True, "income_gaps": True},
                "persona_ids": [2],  # VARIABLE_INCOME_BUDGETER
                "tags": ["budgeting", "variable income", "cash flow"],
            },
            {
                "id": "strategy_50_30_20_budget",
                "strategy_name": "50/30/20 Budget Rule",
                "category": "budgeting",
                "content": (
                    "50/30/20 Budget Rule: Allocate after-tax income as follows: 50% to needs "
                    "(rent, utilities, groceries, insurance, minimum debt payments), 30% to wants "
                    "(dining out, entertainment, hobbies), 20% to savings and debt payoff beyond "
                    "minimums. This is a starting framework - adjust percentages based on your "
                    "situation. Best for: Regular income, starting budgeting journey, simple approach."
                ),
                "effective_for": {"regular_income": True, "budgeting_beginner": True},
                "persona_ids": [5],  # BALANCED_SPENDER
                "tags": ["budgeting", "general", "framework"],
            },
            {
                "id": "strategy_subscription_audit",
                "strategy_name": "Subscription Audit Process",
                "category": "spending",
                "content": (
                    "Subscription Audit Process: (1) List all subscriptions from bank statements. "
                    "(2) Rate each as Essential, Useful, or Questionable. (3) Calculate total monthly "
                    "and annual cost. (4) Cancel anything rated Questionable. (5) Share accounts "
                    "with family when possible. (6) Use annual billing if it saves 15%+ (and you'll "
                    "use it all year). (7) Set quarterly review reminder. Best for: Multiple "
                    "subscriptions, subscription creep, forgotten subscriptions."
                ),
                "effective_for": {"multiple_subscriptions": True, "subscription_spending_high": True},
                "persona_ids": [3],  # SUBSCRIPTION_HEAVY
                "tags": ["subscriptions", "spending", "audit"],
            },
            {
                "id": "strategy_emergency_fund",
                "strategy_name": "Emergency Fund Building",
                "category": "savings",
                "content": (
                    "Emergency Fund Building: Goal is 3-6 months of essential expenses in a "
                    "high-yield savings account. Build gradually: Start with $1,000, then 1 month, "
                    "then 3 months, then 6 months. Keep separate from checking (out of sight, out "
                    "of mind). Use only for true emergencies (job loss, medical, car repair), not "
                    "planned expenses. Replenish immediately if used. Best for: Everyone, but "
                    "especially variable income or single-income households."
                ),
                "effective_for": {"low_emergency_fund": True, "building_savings": True},
                "persona_ids": [4, 2],  # SAVINGS_BUILDER, VARIABLE_INCOME_BUDGETER
                "tags": ["savings", "emergency fund", "safety net"],
            },
            {
                "id": "strategy_high_yield_savings",
                "strategy_name": "High-Yield Savings Optimization",
                "category": "savings",
                "content": (
                    "High-Yield Savings Optimization: Move savings from traditional banks (0.01% APY) "
                    "to online high-yield savings accounts (4-5% APY as of 2024). This can earn "
                    "$400-500/year on $10,000 vs $1/year at traditional banks. Look for: FDIC "
                    "insurance, no fees, no minimums, easy transfers. Top options: Ally, Marcus, "
                    "Discover, Capital One. Keep checking separate for daily use. Best for: "
                    "Anyone with savings sitting in low-yield accounts."
                ),
                "effective_for": {"has_savings": True, "low_yield_account": True},
                "persona_ids": [4],  # SAVINGS_BUILDER
                "tags": ["savings", "high-yield", "optimization"],
            },
            {
                "id": "strategy_automated_savings",
                "strategy_name": "Automated Savings Strategy",
                "category": "savings",
                "content": (
                    "Automated Savings Strategy: Set up automatic transfers from checking to savings "
                    "on payday. Start small ($25-50/paycheck) and increase gradually. Use 'set it "
                    "and forget it' approach - you'll adapt to living on less. Additional automation: "
                    "Round-up features (spare change), triggered transfers (when balance exceeds X), "
                    "split direct deposit (portion to savings automatically). Best for: Building "
                    "savings habit, overcoming willpower issues, consistent savers."
                ),
                "effective_for": {"building_savings_habit": True, "needs_discipline": True},
                "persona_ids": [4, 5],  # SAVINGS_BUILDER, BALANCED_SPENDER
                "tags": ["savings", "automation", "habits"],
            },
            {
                "id": "strategy_credit_utilization",
                "strategy_name": "Credit Utilization Management",
                "category": "credit",
                "content": (
                    "Credit Utilization Management: Credit utilization (balance/limit) makes up 30% "
                    "of credit score. Target: <30% on each card and overall, <10% is ideal. "
                    "Strategies to improve: (1) Pay down balances, (2) Request credit limit increases "
                    "(if you won't use them), (3) Pay multiple times per month to keep reported "
                    "balance low, (4) Open new card for more available credit (advanced). Track: "
                    "Check utilization weekly, set alerts at 30%. Best for: Improving credit score, "
                    "high utilization."
                ),
                "effective_for": {"high_utilization": True, "building_credit": True},
                "persona_ids": [1],  # HIGH_UTILIZATION
                "tags": ["credit", "utilization", "credit score"],
            },
        ]
        
        documents = []
        for strategy in strategies:
            try:
                doc = FinancialStrategyDocument(
                    id=strategy["id"],
                    content=strategy["content"],
                    strategy_name=strategy["strategy_name"],
                    category=strategy["category"],
                    effective_for=strategy.get("effective_for", {}),
                    persona_ids=strategy.get("persona_ids", []),
                    tags=strategy.get("tags", []),
                )
                documents.append(doc.to_dict())
            except Exception as e:
                logger.warning(f"Error processing strategy {strategy.get('id')}: {e}")
                continue
        
        if documents:
            count = self.vector_store.add_documents(documents)
            logger.info(f"✓ Ingested {count} financial strategies")
            return count
        else:
            logger.info("No financial strategies found")
            return 0
    
    async def build_full_knowledge_base(
        self,
        clear_existing: bool = False,
        include_strategies: bool = True,
    ) -> Dict[str, Any]:
        """
        Build complete knowledge base from all sources.
        
        Args:
            clear_existing: Whether to clear existing knowledge base first
            include_strategies: Whether to include financial strategies
        
        Returns:
            Dictionary with statistics about what was ingested
        """
        logger.info("=" * 80)
        logger.info("Building RAG Knowledge Base")
        logger.info("=" * 80)
        
        if clear_existing:
            logger.info("\nClearing existing knowledge base...")
            self.vector_store.clear()
        
        stats = {
            "user_scenarios": 0,
            "education_content": 0,
            "partner_offers": 0,
            "operator_decisions": 0,
            "financial_strategies": 0,
            "total_documents": 0,
        }
        
        # Ingest from all sources
        stats["education_content"] = await self.ingest_education_content()
        stats["partner_offers"] = await self.ingest_partner_offers()
        
        if include_strategies:
            stats["financial_strategies"] = await self.ingest_financial_strategies()
        
        # These depend on database having data
        try:
            stats["user_scenarios"] = await self.ingest_user_scenarios()
        except Exception as e:
            logger.warning(f"Could not ingest user scenarios: {e}")
        
        try:
            stats["operator_decisions"] = await self.ingest_operator_decisions()
        except Exception as e:
            logger.warning(f"Could not ingest operator decisions: {e}")
        
        # Calculate total
        stats["total_documents"] = sum([
            stats["user_scenarios"],
            stats["education_content"],
            stats["partner_offers"],
            stats["operator_decisions"],
            stats["financial_strategies"],
        ])
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Knowledge Base Built Successfully!")
        logger.info("=" * 80)
        logger.info(f"User Scenarios:        {stats['user_scenarios']:>6}")
        logger.info(f"Education Content:     {stats['education_content']:>6}")
        logger.info(f"Partner Offers:        {stats['partner_offers']:>6}")
        logger.info(f"Operator Decisions:    {stats['operator_decisions']:>6}")
        logger.info(f"Financial Strategies:  {stats['financial_strategies']:>6}")
        logger.info("-" * 80)
        logger.info(f"TOTAL DOCUMENTS:       {stats['total_documents']:>6}")
        logger.info("=" * 80)
        
        # Get and display vector store stats
        vector_stats = self.vector_store.get_stats()
        logger.info("\nVector Store Statistics:")
        logger.info(f"Collection: {vector_stats['collection_name']}")
        logger.info(f"Embedding Model: {vector_stats['embedding_model']}")
        logger.info(f"Embedding Dimension: {vector_stats['embedding_dimension']}")
        logger.info(f"Document Types: {', '.join(vector_stats.get('document_types', []))}")
        
        return stats
    
    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """
        Get summary of current knowledge base contents.
        
        Returns:
            Dictionary with knowledge base statistics
        """
        return self.vector_store.get_stats()

