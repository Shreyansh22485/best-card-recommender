import yaml
import json
import os
from typing import List, Dict, Any
from app.models.models import CreditCard, Spend


def load_credit_cards():
    """Load credit card data from a YAML file."""
    cards_file = os.path.join(os.path.dirname(__file__), "../data/credit_cards.yaml")
    
    if os.path.exists(cards_file):
        with open(cards_file, "r") as file:
            cards_data = yaml.safe_load(file)
            return [CreditCard(**card) for card in cards_data]
    else:
        # Fallback to hardcoded cards if file doesn't exist
        return [
            CreditCard(
                name="Cash Rewards Card",
                annual_fee=0,
                rewards={
                    "Grocery": 0.03,
                    "Dining": 0.03,
                    "Gas": 0.03,
                    "Other": 0.01
                },
                welcome_bonus={
                    "spend": 500,
                    "timeframe_months": 3,
                    "reward": 200
                }
            ),
            CreditCard(
                name="Travel Elite Card",
                annual_fee=95,
                rewards={
                    "Travel": 0.05,
                    "Dining": 0.03,
                    "Other": 0.015
                },
                welcome_bonus={
                    "spend": 3000,
                    "timeframe_months": 3,
                    "reward": 750,
                    "reward_type": "points"
                }
            ),
            CreditCard(
                name="Premium Rewards Card",
                annual_fee=550,
                rewards={
                    "Travel": 0.05,
                    "Dining": 0.04,
                    "Entertainment": 0.04,
                    "Grocery": 0.02,
                    "Other": 0.02
                },
                welcome_bonus={
                    "spend": 6000,
                    "timeframe_months": 6,
                    "reward": 1500,
                    "reward_type": "points"
                }
            )
        ]


def calculate_rewards(card: CreditCard, spends: List[Spend]) -> float:
    """Calculate reward value for a card based on spending categories."""
    total_reward = 0
    
    for spend in spends:
        category = spend.category
        amount = spend.amount
        
        # Get the reward rate for this category, default to "Other" if not specified
        reward_rate = card.rewards.get(category, card.rewards.get("Other", 0))
        
        # Calculate reward for this spend
        reward = amount * reward_rate
        total_reward += reward
    
    # Subtract annual fee from the total reward
    total_reward -= card.annual_fee
    
    return total_reward


def recommend_card(spends: List[Spend]) -> Dict[str, Any]:
    """Recommend the best card based on spending patterns."""
    cards = load_credit_cards()
    card_scores = {}
    
    for card in cards:
        score = calculate_rewards(card, spends)
        card_scores[card.name] = score
    
    # Find the card with the highest score
    best_card = max(card_scores, key=card_scores.get)
    best_score = card_scores[best_card]
    
    return {
        "recommended_card": best_card,
        "score": best_score,
        "comparison": card_scores
    }
