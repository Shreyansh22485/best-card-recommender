from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from app.models.models import SpendInput, User
from app.utils.auth import get_current_active_user
from app.utils.recommendation import recommend_card
from app.utils.gmail_parser import (
    create_oauth_flow, build_gmail_service, get_statement_emails,
    get_email_content, parse_pdf_content, extract_transactions,
    categorize_transactions, analyze_spending, prepare_statement_data
)
from app.models.database import users_collection, preferences_collection, statements_collection
from app.routers import auth
import json
from datetime import datetime

app = FastAPI(title="Best Card Recommender API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth.router, prefix="/api")

# OAuth flow state storage (in-memory for simplicity)
# In production, use a more secure method
oauth_states = {}


@app.get("/")
def read_root():
    return {"message": "Best Card Recommender API"}


@app.post("/api/recommend")
async def recommend_best_card(
    spend_input: SpendInput,
    current_user: User = Depends(get_current_active_user)
):
    """Recommend the best credit card based on user's spending habits."""
    recommendation_result = recommend_card(spend_input.spends)
    return recommendation_result


@app.get("/api/gmail/auth")
async def gmail_auth(current_user: User = Depends(get_current_active_user)):
    """Initiate Gmail OAuth flow."""
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    # Store state for verification
    oauth_states[state] = current_user.id
    
    return {"auth_url": authorization_url}


@app.get("/api/gmail/callback")
async def gmail_callback(state: str, code: str, request: Request):
    """Handle Gmail OAuth callback."""
    # Verify state
    user_id = oauth_states.get(state)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Exchange code for token
    flow = create_oauth_flow()
    flow.fetch_token(code=code)
    
    # Get credentials
    credentials = flow.credentials
    creds_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    
    # Store credentials in database
    preferences_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "gmail_credentials": creds_dict,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )
      # Clean up state
    if state in oauth_states:
        del oauth_states[state]
    
    # Redirect to frontend with success message
    # Make sure to redirect to the frontend URL, not the backend URL
    return RedirectResponse(url="http://localhost:3000/auth-success")


@app.get("/api/gmail/parse-statement")
async def parse_gmail_statement(current_user: User = Depends(get_current_active_user)):
    """Parse a recent Gmail statement and store the data."""
    # Get user preferences with Gmail credentials
    user_prefs = preferences_collection.find_one({"user_id": current_user.id})
    if not user_prefs or "gmail_credentials" not in user_prefs:
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        # Build Gmail service
        service = build_gmail_service(user_prefs["gmail_credentials"])
        
        # Get recent statement emails
        messages = get_statement_emails(service, max_results=1)
        if not messages:
            return {"message": "No statement emails found"}
        
        # Get the most recent statement email
        email_data = get_email_content(service, messages[0]["id"])
        if not email_data:
            raise HTTPException(status_code=500, detail="Failed to get email content")
        
        # Parse PDF attachment or email body
        text_content = ""
        if email_data["attachments"]:
            for attachment in email_data["attachments"]:
                if attachment["mime_type"] == "application/pdf":
                    pdf_text = parse_pdf_content(attachment["content"])
                    if pdf_text:
                        text_content = pdf_text
                        break
        
    # If no PDF content, use email body
        if not text_content and email_data["body_text"]:
            text_content = email_data["body_text"]
        
        # Extract and categorize transactions
        transactions = extract_transactions(text_content)
        categorized_transactions = categorize_transactions(transactions)
        
        # Analyze spending patterns
        spending_analysis = analyze_spending(categorized_transactions)    # Prepare statement data for storage
        statement_data = prepare_statement_data(email_data, categorized_transactions, spending_analysis)
        statement_data["user_id"] = current_user.id
        
        # Store in database with upsert to handle duplicate email_id
        statements_collection.update_one(
            {"email_id": statement_data["email_id"], "user_id": current_user.id},
            {"$set": statement_data},
            upsert=True
        )
        
        return {
            "message": "Statement parsed successfully",
            "email_subject": email_data["subject"],
            "transaction_count": len(categorized_transactions),
            "spending_analysis": spending_analysis
        }
    except Exception as e:
        # Handle any errors during the process
        error_message = str(e)
        # Don't expose sensitive error details in production
        raise HTTPException(status_code=500, detail=f"Error processing statement: {error_message}")
