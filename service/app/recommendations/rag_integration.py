"""Integration layer for RAG-based recommendations with catalog fallback."""

import logging
import uuid
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.rag import VectorStore, RAGConfig, RAGRecommendationGenerator
from app.rag.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class EnhancedRecommendationGenerator:
    """
    Enhanced recommendation generator with RAG support and catalog fallback.
    
    This class integrates RAG-based recommendation generation with the existing
    catalog-based system, providing seamless fallback and A/B testing support.
    
    Example:
        ```python
        from sqlalchemy.orm import Session
        
        generator = EnhancedRecommendationGenerator(
            db_session=db,
            use_rag=True,  # Enable RAG mode
            use_openai=True
        )
        
        result = generator.generate_recommendations(
            user_id=user_id,
            personas=["HIGH_UTILIZATION"],
            signals_30d=signals_30d,
            signals_180d=signals_180d,
        )
        ```
    """
    
    def __init__(
        self,
        db_session: Session,
        use_rag: bool = False,
        use_openai: bool = True,
        rag_config: Optional[RAGConfig] = None,
    ):
        """
        Initialize enhanced recommendation generator.
        
        Args:
            db_session: SQLAlchemy database session
            use_rag: Whether to use RAG generation (default: False for safety)
            use_openai: Whether to use OpenAI for generation
            rag_config: Optional RAG configuration (uses env defaults if not provided)
        """
        self.db = db_session
        self.use_rag = use_rag
        self.use_openai = use_openai
        
        # Initialize RAG components if enabled
        self.rag_generator = None
        self.vector_store = None
        
        if use_rag:
            try:
                config = rag_config or RAGConfig.from_env()
                self.vector_store = VectorStore(config=config)
                self.rag_generator = RAGRecommendationGenerator(
                    vector_store=self.vector_store,
                    use_openai=use_openai,
                )
                logger.info("✓ RAG components initialized")
            except Exception as e:
                logger.error(f"Failed to initialize RAG components: {e}")
                logger.warning("Falling back to catalog-based generation")
                self.use_rag = False
        
        # Import catalog-based generator for fallback
        from app.recommendations.generator import RecommendationGenerator
        self.catalog_generator = RecommendationGenerator(
            db_session=db_session,
            use_openai=use_openai
        )
    
    def generate_recommendations(
        self,
        user_id: uuid.UUID,
        personas: Optional[List[str]] = None,
        signals_30d: Optional[Dict[str, Any]] = None,
        signals_180d: Optional[Dict[str, Any]] = None,
        force_rag: bool = False,
        force_catalog: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate recommendations using RAG or catalog (with fallback).
        
        Args:
            user_id: User ID
            personas: Optional list of persona names (fetched if not provided)
            signals_30d: Optional 30-day signals (fetched if not provided)
            signals_180d: Optional 180-day signals (fetched if not provided)
            force_rag: Force RAG generation (fail if RAG not available)
            force_catalog: Force catalog generation (skip RAG)
        
        Returns:
            Dictionary with recommendations and metadata
        """
        logger.info(f"Generating recommendations for user {user_id}")
        
        # Fetch data if not provided
        if personas is None or signals_30d is None:
            profile_data = self._fetch_user_profile_data(user_id)
            personas = personas or profile_data.get("personas", [])
            signals_30d = signals_30d or profile_data.get("signals_30d", {})
            signals_180d = signals_180d or profile_data.get("signals_180d", {})
        
        # Decide which generator to use
        use_rag = self._should_use_rag(force_rag, force_catalog)
        
        if use_rag:
            logger.info("Using RAG generation")
            try:
                result = self._generate_with_rag(
                    user_id=user_id,
                    personas=personas,
                    signals_30d=signals_30d,
                    signals_180d=signals_180d,
                )
                
                if result.get("success"):
                    return result
                else:
                    logger.warning("RAG generation failed, falling back to catalog")
                    # Fall through to catalog generation
                    
            except Exception as e:
                logger.error(f"RAG generation error: {e}, falling back to catalog")
                # Fall through to catalog generation
        
        # Use catalog generation (fallback or forced)
        logger.info("Using catalog generation")
        return self._generate_with_catalog(
            user_id=user_id,
            signals_30d=signals_30d,
            signals_180d=signals_180d,
        )
    
    def _should_use_rag(self, force_rag: bool, force_catalog: bool) -> bool:
        """
        Determine whether to use RAG generation.
        
        Args:
            force_rag: Force RAG generation
            force_catalog: Force catalog generation
        
        Returns:
            True if should use RAG, False for catalog
        """
        if force_catalog:
            return False
        
        if force_rag:
            if not self.use_rag or not self.rag_generator:
                raise RuntimeError("RAG generation forced but not available")
            return True
        
        # Use RAG if enabled and available
        return self.use_rag and self.rag_generator is not None
    
    def _fetch_user_profile_data(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Fetch user profile data from database.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with persona and signals data
        """
        try:
            from backend.app.models.user_profile import UserProfile
            from backend.app.models.user_persona_assignment import UserPersonaAssignment
        except ImportError:
            import sys
            import os
            backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            from app.models.user_profile import UserProfile
            from app.models.user_persona_assignment import UserPersonaAssignment
        
        # Get profile
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            return {
                "personas": [],
                "signals_30d": {},
                "signals_180d": {},
            }
        
        # Get personas
        persona_assignments = self.db.query(UserPersonaAssignment).filter(
            UserPersonaAssignment.user_id == user_id
        ).all()
        
        personas = [p.persona.name for p in persona_assignments] if persona_assignments else []
        
        return {
            "personas": personas,
            "signals_30d": profile.signals_30d or {},
            "signals_180d": profile.signals_180d or {},
        }
    
    def _generate_with_rag(
        self,
        user_id: uuid.UUID,
        personas: List[str],
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate recommendations using RAG.
        
        Args:
            user_id: User ID
            personas: List of persona names
            signals_30d: 30-day signals
            signals_180d: 180-day signals
        
        Returns:
            RAG generation result
        """
        return self.rag_generator.generate_recommendations(
            user_id=user_id,
            personas=personas,
            signals_30d=signals_30d,
            signals_180d=signals_180d,
            education_count=5,
            partner_offer_count=3,
        )
    
    def _generate_with_catalog(
        self,
        user_id: uuid.UUID,
        signals_30d: Dict[str, Any],
        signals_180d: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate recommendations using catalog-based system.
        
        Args:
            user_id: User ID
            signals_30d: 30-day signals
            signals_180d: 180-day signals
        
        Returns:
            Catalog generation result
        """
        result = self.catalog_generator.generate_recommendations(
            user_id=user_id,
            signals_30d=signals_30d,
            signals_180d=signals_180d,
        )
        
        # Add generation method metadata
        if isinstance(result, dict):
            result["generation_method"] = "catalog"
        
        return result
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about recommendation generation.
        
        Returns:
            Dictionary with stats
        """
        stats = {
            "rag_enabled": self.use_rag,
            "rag_available": self.rag_generator is not None,
            "openai_enabled": self.use_openai,
        }
        
        if self.vector_store:
            vector_stats = self.vector_store.get_stats()
            stats["knowledge_base"] = {
                "total_documents": vector_stats["total_documents"],
                "document_types": vector_stats.get("document_types", []),
            }
        
        return stats


def create_recommendation_generator(
    db_session: Session,
    enable_rag: bool = None,
    use_openai: bool = True,
) -> EnhancedRecommendationGenerator:
    """
    Factory function to create recommendation generator with proper configuration.
    
    Args:
        db_session: Database session
        enable_rag: Enable RAG mode (reads from env if None)
        use_openai: Enable OpenAI
    
    Returns:
        EnhancedRecommendationGenerator instance
    """
    # Read RAG enable flag from env if not specified
    if enable_rag is None:
        config = RAGConfig.from_env()
        enable_rag = config.enable_rag
    
    generator = EnhancedRecommendationGenerator(
        db_session=db_session,
        use_rag=enable_rag,
        use_openai=use_openai,
    )
    
    logger.info(
        f"Created recommendation generator: RAG={'enabled' if enable_rag else 'disabled'}, "
        f"OpenAI={'enabled' if use_openai else 'disabled'}"
    )
    
    return generator

