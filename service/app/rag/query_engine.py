"""Query engine for intelligent query generation and retrieval."""

import logging
from typing import List, Dict, Any, Optional
import json

from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class QueryEngine:
    """
    Intelligent query generation and retrieval system.
    
    Converts user profiles and signals into effective semantic queries,
    retrieves relevant context from the knowledge base, and ranks results.
    
    Example:
        ```python
        query_engine = QueryEngine(vector_store)
        
        # Generate query from user profile
        query = query_engine.generate_query_from_profile(
            personas=["HIGH_UTILIZATION"],
            signals_30d={"credit": {"avg_utilization": 0.68}}
        )
        
        # Retrieve relevant context
        context = query_engine.retrieve_context(
            query=query,
            personas=["HIGH_UTILIZATION"],
            top_k=5
        )
        ```
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize query engine.
        
        Args:
            vector_store: Initialized VectorStore instance
        """
        self.vector_store = vector_store
    
    def generate_query_from_profile(
        self,
        personas: List[str],
        signals_30d: Dict[str, Any],
        signals_180d: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate semantic search query from user profile.
        
        Creates a rich query that captures the user's financial situation
        for effective semantic search.
        
        Args:
            personas: List of persona names (e.g., ["HIGH_UTILIZATION"])
            signals_30d: 30-day signals
            signals_180d: Optional 180-day signals
        
        Returns:
            Search query string
        """
        query_parts = []
        
        # Add persona context
        if personas:
            persona_desc = ", ".join(personas)
            query_parts.append(f"Financial situation: {persona_desc}")
        
        # Extract key signals from 30-day data
        if signals_30d:
            # Credit signals
            if "credit" in signals_30d:
                credit = signals_30d["credit"]
                
                if credit.get("avg_utilization") and credit["avg_utilization"] > 0.3:
                    util_pct = credit["avg_utilization"] * 100
                    query_parts.append(f"high credit card utilization ({util_pct:.0f}%)")
                
                if credit.get("cards_with_interest"):
                    query_parts.append("paying interest charges on credit cards")
                
                if credit.get("minimum_payment_only_cards"):
                    query_parts.append("making minimum payments only")
                
                if credit.get("overdue_cards"):
                    query_parts.append("overdue credit card accounts")
            
            # Subscription signals
            if "subscriptions" in signals_30d:
                subs = signals_30d["subscriptions"]
                
                if subs.get("subscription_count", 0) >= 3:
                    count = subs["subscription_count"]
                    query_parts.append(f"multiple subscriptions ({count} active)")
                
                if subs.get("total_recurring_spend", 0) >= 50:
                    spend = subs["total_recurring_spend"]
                    query_parts.append(f"high recurring subscription spending (${spend:.0f}/month)")
            
            # Savings signals
            if "savings" in signals_30d:
                savings = signals_30d["savings"]
                
                if savings.get("emergency_fund_coverage_months") is not None:
                    coverage = savings["emergency_fund_coverage_months"]
                    if coverage < 1.0:
                        query_parts.append(f"low emergency fund coverage ({coverage:.1f} months)")
                    elif coverage >= 3.0:
                        query_parts.append(f"building emergency fund ({coverage:.1f} months)")
                
                if savings.get("savings_growth_rate_percent") and savings["savings_growth_rate_percent"] > 0:
                    query_parts.append("growing savings consistently")
            
            # Income signals
            if "income" in signals_30d:
                income = signals_30d["income"]
                
                if income.get("payment_frequency") == "irregular":
                    query_parts.append("variable irregular income")
                
                if income.get("cash_flow_buffer_months") is not None:
                    buffer = income["cash_flow_buffer_months"]
                    if buffer < 1.0:
                        query_parts.append(f"low cash flow buffer ({buffer:.1f} months)")
        
        # Combine into natural language query
        if query_parts:
            query = "Financial education and strategies for user with: " + ", ".join(query_parts)
        else:
            query = f"General financial education for {personas[0] if personas else 'user'}"
        
        logger.info(f"Generated query: {query[:100]}...")
        return query
    
    def retrieve_context(
        self,
        query: str,
        personas: Optional[List[str]] = None,
        top_k: int = 5,
        include_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context from knowledge base.
        
        Args:
            query: Search query
            personas: Optional list of personas to filter by
            top_k: Number of results to retrieve
            include_types: Optional document types to include
        
        Returns:
            Dictionary with retrieved documents and metadata
        """
        # Build filters
        filters = {}
        
        if include_types:
            if len(include_types) == 1:
                filters["type"] = include_types[0]
            else:
                filters["type"] = {"$in": include_types}
        
        # Search
        results = self.vector_store.search(
            query=query,
            top_k=top_k,
            filters=filters if filters else None,
        )
        
        # Package results
        context = {
            "query": query,
            "retrieved_count": len(results["ids"][0]) if results["ids"] else 0,
            "documents": [],
        }
        
        if results["ids"] and results["ids"][0]:
            for i, (doc_id, content, metadata, distance) in enumerate(zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                similarity = 1 / (1 + distance)
                
                context["documents"].append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata,
                    "similarity": similarity,
                    "rank": i + 1,
                })
        
        logger.info(
            f"Retrieved {context['retrieved_count']} documents "
            f"(avg similarity: {sum(d['similarity'] for d in context['documents']) / len(context['documents']):.3f})"
            if context['documents'] else "Retrieved 0 documents"
        )
        
        return context
    
    def retrieve_multi_context(
        self,
        queries: List[str],
        top_k_per_query: int = 3,
    ) -> Dict[str, Any]:
        """
        Retrieve context from multiple queries (multi-query retrieval).
        
        Useful for complex scenarios requiring different types of knowledge.
        
        Args:
            queries: List of search queries
            top_k_per_query: Results per query
        
        Returns:
            Combined context from all queries
        """
        all_documents = []
        seen_ids = set()
        
        for query in queries:
            results = self.vector_store.search(query=query, top_k=top_k_per_query)
            
            if results["ids"] and results["ids"][0]:
                for i, (doc_id, content, metadata, distance) in enumerate(zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Deduplicate
                    if doc_id not in seen_ids:
                        similarity = 1 / (1 + distance)
                        
                        all_documents.append({
                            "id": doc_id,
                            "content": content,
                            "metadata": metadata,
                            "similarity": similarity,
                            "query": query,
                        })
                        seen_ids.add(doc_id)
        
        # Sort by similarity
        all_documents.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Add ranks
        for i, doc in enumerate(all_documents, 1):
            doc["rank"] = i
        
        context = {
            "queries": queries,
            "retrieved_count": len(all_documents),
            "documents": all_documents,
        }
        
        logger.info(f"Multi-query retrieval: {len(queries)} queries → {len(all_documents)} unique documents")
        
        return context
    
    def retrieve_similar_scenarios(
        self,
        signals_30d: Dict[str, Any],
        personas: List[str],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Find similar user scenarios from the knowledge base.
        
        Looks for users with similar financial situations who received
        recommendations and had positive outcomes.
        
        Args:
            signals_30d: Current user's signals
            personas: Current user's personas
            top_k: Number of similar scenarios to retrieve
        
        Returns:
            List of similar scenario documents
        """
        # Build query focused on scenario matching
        query_parts = ["Similar user case:"]
        
        # Add key matching criteria
        if "credit" in signals_30d:
            credit = signals_30d["credit"]
            if credit.get("avg_utilization"):
                util = credit["avg_utilization"]
                if util >= 0.5:
                    query_parts.append("high credit utilization")
                elif util >= 0.3:
                    query_parts.append("moderate credit utilization")
        
        if "subscriptions" in signals_30d:
            subs = signals_30d["subscriptions"]
            if subs.get("subscription_count", 0) >= 3:
                query_parts.append("multiple subscriptions")
        
        query = " ".join(query_parts)
        
        # Search for user scenarios
        results = self.vector_store.search(
            query=query,
            top_k=top_k,
            filters={"type": "user_scenario"},
        )
        
        scenarios = []
        if results["ids"] and results["ids"][0]:
            for doc_id, content, metadata, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 / (1 + distance)
                
                scenarios.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata,
                    "similarity": similarity,
                })
        
        logger.info(f"Found {len(scenarios)} similar user scenarios")
        return scenarios
    
    def retrieve_by_category(
        self,
        category: str,
        personas: List[str],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents by category (debt, savings, budgeting, etc.).
        
        Args:
            category: Category name (e.g., "debt", "savings", "budgeting")
            personas: User personas for filtering
            top_k: Number of results
        
        Returns:
            List of documents in category
        """
        # Create category-focused query
        query_map = {
            "debt": "debt paydown strategies, credit card utilization, interest reduction",
            "savings": "emergency fund, savings strategies, high-yield accounts",
            "budgeting": "budgeting methods, expense tracking, income management",
            "credit": "credit score improvement, credit utilization, credit management",
            "subscriptions": "subscription management, recurring expenses, cancellation",
            "income": "variable income, cash flow, income stability",
        }
        
        query = query_map.get(category, f"{category} financial strategies")
        
        # Search
        results = self.vector_store.search(
            query=query,
            top_k=top_k,
        )
        
        documents = []
        if results["ids"] and results["ids"][0]:
            for doc_id, content, metadata, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 / (1 + distance)
                
                documents.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata,
                    "similarity": similarity,
                })
        
        logger.info(f"Retrieved {len(documents)} documents for category '{category}'")
        return documents
    
    def get_relevant_strategies(
        self,
        user_situation: Dict[str, Any],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get relevant financial strategies for a user's situation.
        
        Args:
            user_situation: Dictionary describing user situation
            top_k: Number of strategies to retrieve
        
        Returns:
            List of relevant financial strategy documents
        """
        # Build query from situation
        query_parts = []
        
        if user_situation.get("has_high_debt"):
            query_parts.append("debt reduction strategies")
        
        if user_situation.get("variable_income"):
            query_parts.append("variable income budgeting")
        
        if user_situation.get("low_emergency_fund"):
            query_parts.append("emergency fund building")
        
        if user_situation.get("many_subscriptions"):
            query_parts.append("subscription management")
        
        query = " and ".join(query_parts) if query_parts else "general financial strategies"
        
        # Search for strategies
        results = self.vector_store.search(
            query=query,
            top_k=top_k,
            filters={"type": "financial_strategy"},
        )
        
        strategies = []
        if results["ids"] and results["ids"][0]:
            for doc_id, content, metadata, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 / (1 + distance)
                
                strategies.append({
                    "id": doc_id,
                    "strategy_name": metadata.get("strategy_name"),
                    "category": metadata.get("category"),
                    "content": content,
                    "metadata": metadata,
                    "similarity": similarity,
                })
        
        logger.info(f"Found {len(strategies)} relevant strategies")
        return strategies

