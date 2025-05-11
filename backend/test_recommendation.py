import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import SpendInput, Spend
from app.utils.recommendation import recommend_card

client = TestClient(app)

def test_recommendation_engine():
    """Test the card recommendation engine functionality"""
    # Test with sample spending data
    spends = [
        Spend(category="Dining", amount=350),
        Spend(category="Grocery", amount=450),
        Spend(category="Travel", amount=200)
    ]
    
    spend_input = SpendInput(spends=spends)
    result = recommend_card(spend_input.spends)
    
    # Verify the result structure
    assert "recommended_card" in result
    assert "score" in result
    assert "comparison" in result
    
    # Verify that all three cards are included in the comparison
    assert len(result["comparison"]) == 3
    assert "Cash Rewards Card" in result["comparison"]
    assert "Travel Elite Card" in result["comparison"]
    assert "Premium Rewards Card" in result["comparison"]
    
    print("Recommendation engine test passed!")
    
if __name__ == "__main__":
    # Run the tests
    test_recommendation_engine()
