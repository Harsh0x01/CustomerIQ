from typing import List, Dict

class StrategyAdvisor:
    """
    Enterprise-tier analytics engine that maps statistical feature importance 
    to actionable business recovery strategies.
    
    Provides formal, prescriptive directives based on individual-level churn variance.
    """
    
    STRATEGY_MAP = {
        "balance": "Implement a liquidity-based incentive program. Offer a Tier-1 interest rate bonus for balances exceeding historical medians.",
        "is_active_member": "Re-engagement required. Initiate a formal high-touch service review or premium hospitality outreach program.",
        "num_products": "Product consolidation audit. Evaluate cross-sell fit or loyalty-based product bundling to deepen customer reliance.",
        "age": "Segment-specific service refinement. Deploy an age-appropriate digital concierge service or estate planning consultation.",
        "tenure": "Loyalty tenure recognition. Initiate a formal tenure-based grandfathering program for legacy pricing models.",
        "estimated_salary": "Affluence-targeted outreach. Transition to a private wealth management representative for tailored financial advisement.",
        "gender": "Lifestyle-aligned service adaptation. Refine communication protocol to align with established demographic engagement preferences.",
        "has_credit_card": "Credit utility exploration. Initiate a review of credit-linked reward visibility and utilization metrics."
    }

    @classmethod
    def generate_strategy(cls, churn_drivers: List[Dict]) -> List[str]:
        """
        Derives formal strategy recommendations from identified churn drivers.
        
        Args:
            churn_drivers: List of dictionaries containing "feature" and "impact" from SHAP.
            
        Returns:
            List of professional strategic directives.
        """
        if not churn_drivers:
            return ["No significant adverse factors detected. Maintain standard operational engagement protocol."]

        recommendations = []
        for driver in churn_drivers:
            feature = driver.get("feature")
            if feature in cls.STRATEGY_MAP:
                recommendations.append(cls.STRATEGY_MAP[feature])

        return recommendations
