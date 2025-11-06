"""AI-powered income pattern interpretation service using OpenAI."""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date

logger = logging.getLogger(__name__)

# Try to import OpenAI client
try:
    from app.common.openai_client import get_openai_client
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not available - AI income interpretation disabled")


class AIIncomeInterpreter:
    """Interprets income patterns using OpenAI AI to provide human-readable descriptions."""
    
    def __init__(self):
        """Initialize AI income interpreter."""
        self.openai_client = get_openai_client() if OPENAI_AVAILABLE else None
    
    def interpret_income_pattern(
        self,
        payroll_deposits: List[Dict[str, Any]],
        payment_frequency: Dict[str, Any],
        payment_variability: Dict[str, Any],
        variable_income_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate human-readable interpretation of income pattern.
        
        Args:
            payroll_deposits: List of payroll deposit transactions
            payment_frequency: Payment frequency analysis results
            payment_variability: Payment variability analysis results
            variable_income_pattern: Variable income pattern detection results
        
        Returns:
            Dictionary with:
            - description: Human-readable description
            - pattern_type: classified pattern type
            - reliability_score: 0.0-1.0
            - recommendations: List of recommendations
        """
        if not self.openai_client:
            # Fallback to rule-based interpretation
            return self._rule_based_interpretation(
                payroll_deposits,
                payment_frequency,
                payment_variability,
                variable_income_pattern
            )
        
        try:
            return self._ai_interpretation(
                payroll_deposits,
                payment_frequency,
                payment_variability,
                variable_income_pattern
            )
        except Exception as e:
            logger.error(f"AI interpretation failed: {e}, falling back to rule-based")
            return self._rule_based_interpretation(
                payroll_deposits,
                payment_frequency,
                payment_variability,
                variable_income_pattern
            )
    
    def _ai_interpretation(
        self,
        payroll_deposits: List[Dict[str, Any]],
        payment_frequency: Dict[str, Any],
        payment_variability: Dict[str, Any],
        variable_income_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use OpenAI to interpret income pattern.
        
        Returns:
            Interpretation results dictionary
        """
        # Prepare deposit summary
        if len(payroll_deposits) == 0:
            deposit_summary = "No income deposits detected"
        else:
            deposits_str = "\n".join([
                f"  - {d['date']}: ${d['amount']:.2f}"
                for d in payroll_deposits[:10]  # Limit to 10 for prompt
            ])
            if len(payroll_deposits) > 10:
                deposits_str += f"\n  ... and {len(payroll_deposits) - 10} more"
            deposit_summary = f"Recent deposits:\n{deposits_str}"
        
        prompt = f"""Analyze this user's income pattern and provide a clear, human-readable description:

{deposit_summary}

Payment Frequency Analysis:
- Median gap between deposits: {payment_frequency.get('median_gap_days', 'N/A')} days
- Frequency type: {payment_frequency.get('frequency_type', 'unknown')}
- Number of deposits: {payment_frequency.get('deposit_count', 0)}

Payment Variability:
- Mean amount: ${payment_variability.get('mean_amount', 0):.2f}
- Standard deviation: ${payment_variability.get('std_deviation', 0):.2f}
- Min/Max: ${payment_variability.get('min_amount', 0):.2f} / ${payment_variability.get('max_amount', 0):.2f}
- Variability level: {payment_variability.get('variability_level', 'unknown')}

Variable Income Pattern:
- Is variable: {variable_income_pattern.get('is_variable_income', False)}
- Reasons: {', '.join(variable_income_pattern.get('reasons', []))}

Please provide:
1. A clear, single-sentence description of the income pattern (suitable for dashboard display)
2. Pattern classification: regular_salary, biweekly_salary, irregular_freelance, commission_based, mixed_income, or insufficient_data
3. Reliability score (0.0-1.0) - how predictable is this income?
4. 2-3 brief recommendations for managing this income pattern

Return JSON format:
{{
  "description": "Concise description suitable for dashboard",
  "pattern_type": "regular_salary/biweekly_salary/irregular_freelance/commission_based/mixed_income/insufficient_data",
  "reliability_score": 0.0-1.0,
  "recommendations": ["rec1", "rec2", "rec3"]
}}

Examples:
- Weekly salary: "Paid weekly on Fridays with consistent amounts"
- Irregular freelance: "Variable freelance income, 2-4 payments per month ranging $1,200-$3,500"
- Biweekly + commission: "Biweekly salary ($2,500) plus variable monthly commission ($500-$2,000)"
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in income pattern analysis. Provide clear, actionable insights for everyday users."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "description": result.get("description", "Income pattern analysis in progress"),
                "pattern_type": result.get("pattern_type", "unknown"),
                "reliability_score": result.get("reliability_score", 0.5),
                "recommendations": result.get("recommendations", []),
                "interpretation_method": "ai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI interpretation error: {e}")
            raise
    
    def _rule_based_interpretation(
        self,
        payroll_deposits: List[Dict[str, Any]],
        payment_frequency: Dict[str, Any],
        payment_variability: Dict[str, Any],
        variable_income_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback rule-based interpretation.
        
        Returns:
            Interpretation results dictionary
        """
        if len(payroll_deposits) < 2:
            return {
                "description": "Insufficient income data for pattern analysis",
                "pattern_type": "insufficient_data",
                "reliability_score": 0.0,
                "recommendations": [
                    "Connect more accounts to track income",
                    "Wait for more transactions to establish pattern"
                ],
                "interpretation_method": "rule_based"
            }
        
        median_gap = payment_frequency.get('median_gap_days', 0)
        frequency_type = payment_frequency.get('frequency_type', 'unknown')
        variability_level = payment_variability.get('variability_level', 'unknown')
        is_variable = variable_income_pattern.get('is_variable_income', False)
        mean_amount = payment_variability.get('mean_amount', 0)
        
        # Determine pattern type and description
        if frequency_type == 'weekly' and variability_level in ['low', 'stable']:
            pattern_type = "regular_salary"
            description = f"Paid weekly with consistent amounts around ${mean_amount:.2f}"
            reliability_score = 0.9
            recommendations = [
                "Set up automatic savings transfers weekly",
                "Budget can be based on predictable weekly income"
            ]
        
        elif frequency_type == 'biweekly' and variability_level in ['low', 'stable']:
            pattern_type = "biweekly_salary"
            description = f"Paid every {median_gap:.0f} days (biweekly) with consistent amounts"
            reliability_score = 0.9
            recommendations = [
                "Plan for 2-3 paychecks per month",
                "Set aside portion of 3-paycheck months"
            ]
        
        elif frequency_type == 'monthly' and variability_level in ['low', 'stable']:
            pattern_type = "regular_salary"
            description = f"Paid monthly with consistent amounts around ${mean_amount:.2f}"
            reliability_score = 0.85
            recommendations = [
                "Create monthly budget aligned with pay date",
                "Build 1-month cash flow buffer for emergencies"
            ]
        
        elif is_variable and variability_level in ['moderate', 'high']:
            pattern_type = "irregular_freelance"
            min_amt = payment_variability.get('min_amount', 0)
            max_amt = payment_variability.get('max_amount', 0)
            description = f"Variable income pattern: ${min_amt:.0f}-${max_amt:.0f}, paid {len(payroll_deposits)} times in analysis period"
            reliability_score = 0.4
            recommendations = [
                "Budget based on minimum expected income",
                "Build 3-6 month emergency fund for income gaps",
                "Track income trends to anticipate slow periods"
            ]
        
        elif frequency_type == 'irregular':
            pattern_type = "mixed_income"
            description = f"Irregular income pattern with variable timing (median {median_gap:.0f} days between payments)"
            reliability_score = 0.5
            recommendations = [
                "Use cash flow buffer to smooth irregular income",
                "Consider averaging last 3 months for budgeting"
            ]
        
        else:
            pattern_type = "unknown"
            description = f"Complex income pattern requiring more analysis ({frequency_type} frequency)"
            reliability_score = 0.3
            recommendations = [
                "Monitor income pattern over next few months",
                "Consider consulting with financial advisor"
            ]
        
        return {
            "description": description,
            "pattern_type": pattern_type,
            "reliability_score": reliability_score,
            "recommendations": recommendations,
            "interpretation_method": "rule_based"
        }

