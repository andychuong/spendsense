"""AI-powered subscription validation service using OpenAI."""

import logging
import json
from typing import Dict, List, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

# Try to import OpenAI client
try:
    from app.common.openai_client import get_openai_client
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not available - AI subscription validation disabled")


# Known subscription prices for validation
KNOWN_SUBSCRIPTIONS = {
    # Streaming Services
    "netflix": {"basic": 6.99, "standard": 15.49, "premium": 19.99},
    "hulu": {"basic": 7.99, "premium": 14.99},
    "disney+": {"basic": 7.99, "premium": 13.99},
    "disney plus": {"basic": 7.99, "premium": 13.99},
    "hbo max": {"basic": 9.99, "premium": 15.99},
    "amazon prime": {"basic": 14.99},
    "apple tv+": {"basic": 6.99},
    "paramount+": {"basic": 5.99, "premium": 11.99},
    "peacock": {"basic": 5.99, "premium": 11.99},
    
    # Music Services
    "spotify": {"basic": 10.99, "family": 16.99},
    "apple music": {"basic": 10.99, "family": 16.99},
    "youtube music": {"basic": 10.99},
    "pandora": {"basic": 4.99, "premium": 9.99},
    
    # Fitness
    "planet fitness": {"basic": 10.00, "black_card": 24.99},
    "la fitness": {"basic": 29.99, "premium": 44.99},
    "24 hour fitness": {"basic": 29.99, "premium": 49.99},
    "crunch fitness": {"basic": 10.00, "premium": 24.99},
    "orange theory": {"basic": 59.00, "unlimited": 179.00},
    "peloton": {"basic": 12.99, "premium": 44.00},
    
    # Software/Productivity
    "adobe creative cloud": {"basic": 54.99, "all_apps": 59.99},
    "microsoft 365": {"basic": 6.99, "family": 9.99},
    "dropbox": {"basic": 11.99, "premium": 19.99},
    "google one": {"basic": 1.99, "standard": 9.99},
    "github": {"pro": 4.00, "team": 4.00},
    
    # News/Media
    "new york times": {"basic": 17.00, "all_access": 25.00},
    "washington post": {"basic": 12.00},
    "wall street journal": {"basic": 38.99},
}


class AISubscriptionValidator:
    """Validates subscription detections using OpenAI AI."""
    
    def __init__(self):
        """Initialize AI subscription validator."""
        self.openai_client = get_openai_client() if OPENAI_AVAILABLE else None
    
    def validate_subscription(
        self,
        merchant_name: str,
        amount: float,
        cadence_type: str,
        transaction_count: int
    ) -> Dict[str, Any]:
        """
        Validate if a detected recurring transaction is truly a subscription.
        
        Args:
            merchant_name: Name of the merchant
            amount: Transaction amount
            cadence_type: weekly or monthly
            transaction_count: Number of transactions detected
        
        Returns:
            Dictionary with validation results:
            - is_valid_subscription: bool
            - confidence: float (0.0-1.0)
            - service_name: str (cleaned name)
            - expected_price_range: dict
            - price_anomaly: bool
            - reasoning: str
        """
        if not self.openai_client:
            # Fallback to rule-based validation
            return self._rule_based_validation(merchant_name, amount, cadence_type)
        
        try:
            return self._ai_validation(merchant_name, amount, cadence_type, transaction_count)
        except Exception as e:
            logger.error(f"AI validation failed: {e}, falling back to rule-based")
            return self._rule_based_validation(merchant_name, amount, cadence_type)
    
    def _ai_validation(
        self,
        merchant_name: str,
        amount: float,
        cadence_type: str,
        transaction_count: int
    ) -> Dict[str, Any]:
        """
        Use OpenAI to validate subscription.
        
        Args:
            merchant_name: Name of the merchant
            amount: Transaction amount
            cadence_type: weekly or monthly
            transaction_count: Number of transactions
        
        Returns:
            Validation results dictionary
        """
        prompt = f"""Analyze this recurring transaction to determine if it's a legitimate subscription service:

Merchant: {merchant_name}
Amount: ${amount:.2f}
Frequency: {cadence_type}
Transaction Count: {transaction_count}

Please determine:
1. Is this a subscription service (vs a bill, utility, or irregular purchase)?
2. What is the actual service name (cleaned up)?
3. What is the expected price range for this service?
4. Is the detected amount anomalous compared to typical pricing?
5. Confidence level (0.0-1.0) in your assessment

Known subscription services include:
- Streaming: Netflix ($6.99-$19.99), Hulu ($7.99-$14.99), Disney+ ($7.99)
- Music: Spotify ($10.99), Apple Music ($10.99)
- Fitness: Planet Fitness ($10-$24.99), LA Fitness ($29.99-$44.99)
- Software: Adobe Creative Cloud ($54.99), Microsoft 365 ($6.99-$9.99)

Return JSON format:
{{
  "is_valid_subscription": true/false,
  "confidence": 0.0-1.0,
  "service_name": "Clean service name",
  "expected_price_min": X.XX,
  "expected_price_max": X.XX,
  "price_anomaly": true/false,
  "reasoning": "Brief explanation"
}}

Examples:
- "NETFLIX.COM" $15.49 monthly → valid subscription
- "AT&T WIRELESS" $80 monthly → NOT a subscription (utility bill)
- "PLANET FITNESS" $10 monthly → valid subscription
- "AMAZON.COM" $50 monthly → NOT a subscription (irregular purchases)
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a financial data analyst specializing in subscription service identification. Provide accurate, structured responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "is_valid_subscription": result.get("is_valid_subscription", True),
                "confidence": result.get("confidence", 0.5),
                "service_name": result.get("service_name", merchant_name),
                "expected_price_range": {
                    "min": result.get("expected_price_min", amount * 0.8),
                    "max": result.get("expected_price_max", amount * 1.2)
                },
                "price_anomaly": result.get("price_anomaly", False),
                "reasoning": result.get("reasoning", "AI validation completed"),
                "validation_method": "ai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI validation error: {e}")
            raise
    
    def _rule_based_validation(
        self,
        merchant_name: str,
        amount: float,
        cadence_type: str
    ) -> Dict[str, Any]:
        """
        Fallback rule-based validation using known subscription database.
        
        Args:
            merchant_name: Name of the merchant
            amount: Transaction amount
            cadence_type: weekly or monthly
        
        Returns:
            Validation results dictionary
        """
        merchant_lower = merchant_name.lower()
        
        # Check against known subscriptions
        for service_name, pricing in KNOWN_SUBSCRIPTIONS.items():
            if service_name in merchant_lower:
                price_values = list(pricing.values())
                min_price = min(price_values)
                max_price = max(price_values)
                
                # Check if amount is within expected range (with 20% tolerance)
                is_in_range = (min_price * 0.8) <= amount <= (max_price * 1.2)
                
                return {
                    "is_valid_subscription": True,
                    "confidence": 0.9 if is_in_range else 0.6,
                    "service_name": service_name.title(),
                    "expected_price_range": {
                        "min": min_price,
                        "max": max_price
                    },
                    "price_anomaly": not is_in_range,
                    "reasoning": f"Matched known subscription: {service_name.title()}",
                    "validation_method": "rule_based"
                }
        
        # Unknown subscription - use heuristics
        # Reject if amount is too high for typical subscription
        if amount > 200:
            return {
                "is_valid_subscription": False,
                "confidence": 0.7,
                "service_name": merchant_name,
                "expected_price_range": {"min": 0, "max": 200},
                "price_anomaly": True,
                "reasoning": "Amount too high for typical subscription",
                "validation_method": "rule_based"
            }
        
        # Accept as subscription with lower confidence
        return {
            "is_valid_subscription": True,
            "confidence": 0.5,
            "service_name": merchant_name,
            "expected_price_range": {
                "min": amount * 0.8,
                "max": amount * 1.2
            },
            "price_anomaly": False,
            "reasoning": "Unknown subscription, assumed valid",
            "validation_method": "rule_based"
        }
    
    def validate_subscription_list(
        self,
        subscriptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate a list of detected subscriptions.
        
        Args:
            subscriptions: List of subscription dictionaries
        
        Returns:
            List of subscriptions with validation results added
        """
        validated_subscriptions = []
        
        for sub in subscriptions:
            validation = self.validate_subscription(
                merchant_name=sub.get("merchant_name", ""),
                amount=sub.get("average_amount", 0),
                cadence_type=sub.get("cadence_type", "monthly"),
                transaction_count=sub.get("transaction_count", 0)
            )
            
            # Add validation results to subscription
            sub["validation"] = validation
            
            # Only include if validated as subscription with decent confidence
            if validation["is_valid_subscription"] and validation["confidence"] >= 0.3:
                validated_subscriptions.append(sub)
            else:
                logger.info(
                    f"Excluded subscription: {sub['merchant_name']} "
                    f"(confidence: {validation['confidence']:.2f}, "
                    f"reason: {validation['reasoning']})"
                )
        
        return validated_subscriptions

