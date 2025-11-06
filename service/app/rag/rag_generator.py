"""RAG-based recommendation generator."""

import logging
import json
import re
import time
from typing import Dict, List, Any, Optional
import uuid

from app.rag.vector_store import VectorStore
from app.rag.query_engine import QueryEngine
from app.rag.prompts import (
    build_system_prompt,
    build_recommendation_prompt,
    build_partner_offer_prompt,
)
from app.common.openai_client import get_openai_client

logger = logging.getLogger(__name__)


class RAGRecommendationGenerator:
    """
    RAG-based recommendation generator.
    
    Uses retrieval-augmented generation to create personalized recommendations
    based on relevant knowledge retrieved from the vector database.
    
    Example:
        ```python
        from app.rag import VectorStore
        from app.rag.rag_generator import RAGRecommendationGenerator
        
        vector_store = VectorStore()
        generator = RAGRecommendationGenerator(vector_store)
        
        recommendations = generator.generate_recommendations(
            user_id=user_id,
            personas=["HIGH_UTILIZATION"],
            signals_30d=signals_30d,
            signals_180d=signals_180d,
        )
        ```
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        use_openai: bool = True,
    ):
        """
        Initialize RAG recommendation generator.
        
        Args:
            vector_store: Initialized VectorStore instance
            use_openai: Whether to use OpenAI for generation
        """
        self.vector_store = vector_store
        self.query_engine = QueryEngine(vector_store)
        self.openai_client = get_openai_client() if use_openai else None
        self.use_openai = use_openai and self.openai_client is not None
        
        if not self.use_openai:
            logger.warning("OpenAI not available - RAG generation will use fallback mode")
    
    def generate_recommendations(
        self,
        user_id: uuid.UUID,
        personas: List[str],
        signals_30d: Dict[str, Any],
        signals_180d: Optional[Dict[str, Any]] = None,
        education_count: int = 5,
        partner_offer_count: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate RAG-based recommendations for a user.
        
        Args:
            user_id: User ID
            personas: List of user personas
            signals_30d: 30-day signals
            signals_180d: Optional 180-day signals
            education_count: Number of education recommendations
            partner_offer_count: Number of partner offers
        
        Returns:
            Dictionary with generated recommendations
        """
        logger.info(f"Generating RAG recommendations for user {user_id}")
        start_time = time.time()
        
        if not self.use_openai:
            logger.error("Cannot generate recommendations without OpenAI - use catalog fallback")
            return {
                "success": False,
                "error": "RAG generation requires OpenAI",
                "recommendations": [],
            }
        
        # Step 1: Generate search query from user profile
        query = self.query_engine.generate_query_from_profile(
            personas=personas,
            signals_30d=signals_30d,
            signals_180d=signals_180d,
        )
        
        # Step 2: Retrieve relevant context
        context = self.query_engine.retrieve_context(
            query=query,
            personas=personas,
            top_k=10,  # Get more for better context
        )
        
        # Step 3: Get similar user scenarios (if available)
        similar_scenarios = self.query_engine.retrieve_similar_scenarios(
            signals_30d=signals_30d,
            personas=personas,
            top_k=3,
        )
        
        # Add scenarios to context
        if similar_scenarios:
            context["similar_scenarios"] = similar_scenarios
        
        # Step 4: Generate education recommendations
        education_recs = self._generate_education_recommendations(
            user_context={
                "user_id": str(user_id),
                "personas": personas,
                "signals_30d": signals_30d,
                "signals_180d": signals_180d,
            },
            retrieved_context=context,
            count=education_count,
        )
        
        # Step 5: Generate partner offer recommendations
        partner_offers = self._generate_partner_offers(
            user_context={
                "user_id": str(user_id),
                "personas": personas,
                "signals_30d": signals_30d,
                "signals_180d": signals_180d,
            },
            personas=personas,
            count=partner_offer_count,
        )
        
        generation_time_ms = (time.time() - start_time) * 1000
        
        result = {
            "success": True,
            "user_id": str(user_id),
            "personas": personas,
            "education_recommendations": education_recs,
            "partner_offers": partner_offers,
            "total_recommendations": len(education_recs) + len(partner_offers),
            "generation_method": "rag",
            "context_used": {
                "query": query,
                "documents_retrieved": context.get("retrieved_count", 0),
                "similar_scenarios_found": len(similar_scenarios),
            },
            "generation_time_ms": generation_time_ms,
        }
        
        logger.info(
            f"Generated {result['total_recommendations']} RAG recommendations "
            f"in {generation_time_ms:.0f}ms"
        )
        
        return result
    
    def _generate_education_recommendations(
        self,
        user_context: Dict[str, Any],
        retrieved_context: Dict[str, Any],
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generate education recommendations using RAG.
        
        Args:
            user_context: User profile context
            retrieved_context: Retrieved documents from knowledge base
            count: Number of recommendations to generate
        
        Returns:
            List of education recommendations
        """
        logger.info("Generating education recommendations with RAG...")
        
        # Build prompt
        system_prompt = build_system_prompt()
        user_prompt = build_recommendation_prompt(
            user_context=user_context,
            retrieved_context=retrieved_context,
            recommendation_count=count,
        )
        
        # Generate with OpenAI
        try:
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=3000,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            recommendations = self._parse_llm_response(content)
            
            if recommendations:
                logger.info(f"✓ Generated {len(recommendations)} education recommendations")
                return recommendations
            else:
                logger.warning("Failed to parse recommendations from LLM response")
                return []
            
        except Exception as e:
            logger.error(f"Error generating education recommendations: {e}")
            return []
    
    def _generate_partner_offers(
        self,
        user_context: Dict[str, Any],
        personas: List[str],
        count: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generate partner offer recommendations using RAG.
        
        Args:
            user_context: User profile context
            personas: User personas
            count: Number of offers to generate
        
        Returns:
            List of partner offer recommendations
        """
        logger.info("Generating partner offers with RAG...")
        
        # Retrieve relevant partner offers
        offers_query = f"Partner offers relevant for {', '.join(personas)}"
        offers_context = self.vector_store.search(
            query=offers_query,
            top_k=count * 2,  # Get more to filter
            filters={"type": "partner_offer"},
        )
        
        if not offers_context["ids"] or not offers_context["ids"][0]:
            logger.warning("No partner offers found in knowledge base")
            return []
        
        # Convert to offer list
        retrieved_offers = []
        for doc_id, content, metadata, distance in zip(
            offers_context["ids"][0],
            offers_context["documents"][0],
            offers_context["metadatas"][0],
            offers_context["distances"][0]
        ):
            similarity = 1 / (1 + distance)
            retrieved_offers.append({
                "id": doc_id,
                "content": content,
                "metadata": metadata,
                "similarity": similarity,
            })
        
        # Take top offers
        retrieved_offers = retrieved_offers[:count]
        
        # Build prompt
        system_prompt = build_system_prompt()
        user_prompt = build_partner_offer_prompt(
            user_context=user_context,
            retrieved_offers=retrieved_offers,
            count=len(retrieved_offers),
        )
        
        # Generate with OpenAI
        try:
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            offers = self._parse_llm_response(content)
            
            if offers:
                logger.info(f"✓ Generated {len(offers)} partner offers")
                return offers
            else:
                logger.warning("Failed to parse partner offers from LLM response")
                return []
            
        except Exception as e:
            logger.error(f"Error generating partner offers: {e}")
            return []
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured recommendations.
        
        Args:
            response: Raw LLM response
        
        Returns:
            List of recommendation dictionaries
        """
        try:
            # Try to extract JSON from response
            # Look for JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                recommendations = json.loads(json_str)
                
                # Validate structure
                if isinstance(recommendations, list):
                    valid_recs = []
                    for rec in recommendations:
                        if isinstance(rec, dict) and "title" in rec and "content" in rec:
                            valid_recs.append(rec)
                    
                    return valid_recs
            
            # Try parsing entire response as JSON
            recommendations = json.loads(response)
            if isinstance(recommendations, list):
                return recommendations
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response was: {response[:500]}...")
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
        
        return []
    
    def generate_single_recommendation(
        self,
        title: str,
        user_context: Dict[str, Any],
        retrieved_context: Dict[str, Any],
        recommendation_type: str = "education",
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a single recommendation with RAG.
        
        Useful for regenerating or refining specific recommendations.
        
        Args:
            title: Recommendation title/topic
            user_context: User profile context
            retrieved_context: Retrieved documents
            recommendation_type: "education" or "partner_offer"
        
        Returns:
            Single recommendation dictionary or None
        """
        logger.info(f"Generating single {recommendation_type} recommendation: {title}")
        
        # Build focused prompt
        prompt = f"""Generate a single detailed recommendation:

Title: {title}
Type: {recommendation_type}

User Context:
{json.dumps(user_context, indent=2)}

Retrieved Knowledge:
{json.dumps([d['content'][:200] for d in retrieved_context.get('documents', [])[:3]], indent=2)}

Generate a complete recommendation with title, content (400-500 words), rationale, priority, expected_impact, and category.

Output as JSON:"""
        
        try:
            system_prompt = build_system_prompt()
            
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            recommendations = self._parse_llm_response(content)
            
            if recommendations and len(recommendations) > 0:
                return recommendations[0]
            
        except Exception as e:
            logger.error(f"Error generating single recommendation: {e}")
        
        return None
    
    def enhance_rationale(
        self,
        recommendation_title: str,
        user_data: Dict[str, Any],
        existing_rationale: str = "",
    ) -> Optional[str]:
        """
        Enhance or generate a recommendation rationale using RAG.
        
        Args:
            recommendation_title: Title of recommendation
            user_data: User data to cite
            existing_rationale: Optional existing rationale to improve
        
        Returns:
            Enhanced rationale string or None
        """
        from app.rag.prompts import build_rationale_enhancement_prompt
        
        prompt = build_rationale_enhancement_prompt(
            recommendation_title=recommendation_title,
            user_data=user_data,
            existing_rationale=existing_rationale,
        )
        
        try:
            system_prompt = "You are a financial education expert who creates clear, data-driven rationales."
            
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            rationale = response.choices[0].message.content.strip()
            
            # Clean up if it has extra formatting
            rationale = re.sub(r'^["\'`]+|["\'`]+$', '', rationale)
            
            return rationale
            
        except Exception as e:
            logger.error(f"Error enhancing rationale: {e}")
            return None

