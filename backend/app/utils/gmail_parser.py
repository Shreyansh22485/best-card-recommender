import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import io
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def create_oauth_flow():
    """Create and return an OAuth flow instance."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    return flow


def build_gmail_service(credentials_dict):
    """Build and return a Gmail service instance."""
    credentials = Credentials(
        token=credentials_dict.get("token"),
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    return build("gmail", "v1", credentials=credentials)


def get_statement_emails(service, query="statement OR estatement OR e-statement", max_results=5):
    """Search for statement emails in Gmail."""
    try:
        results = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        
        messages = results.get("messages", [])
        return messages
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def get_email_content(service, msg_id):
    """Get the content of a specific email."""
    try:
        message = service.users().messages().get(userId="me", id=msg_id).execute()
        
        email_data = {
            "id": msg_id,
            "subject": "",
            "from": "",
            "date": "",
            "body_text": "",
            "attachments": []
        }
        
        headers = message.get("payload", {}).get("headers", [])
        for header in headers:
            name = header.get("name", "").lower()
            if name == "subject":
                email_data["subject"] = header.get("value", "")
            elif name == "from":
                email_data["from"] = header.get("value", "")
            elif name == "date":
                email_data["date"] = header.get("value", "")
        
        # Process the message parts
        parts = message.get("payload", {}).get("parts", [])
        if not parts:
            # Handle single part message
            data = message.get("payload", {}).get("body", {}).get("data", "")
            if data:
                email_data["body_text"] = base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            # Handle multipart message
            extract_parts(service, parts, email_data, msg_id)
        
        return email_data
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def extract_parts(service, parts, email_data, msg_id, part_index=None):
    """Recursively extract parts of the email."""
    for i, part in enumerate(parts):
        part_id = part_index + "." + str(i) if part_index else str(i)
        
        mime_type = part.get("mimeType", "")
        
        # If it's a text part
        if mime_type == "text/plain" or mime_type == "text/html":
            data = part.get("body", {}).get("data", "")
            if data:
                decoded_data = base64.urlsafe_b64decode(data).decode("utf-8")
                if mime_type == "text/plain":
                    email_data["body_text"] = decoded_data
        
        # If it's a PDF attachment
        elif mime_type == "application/pdf":
            attachment = {
                "id": part_id,
                "filename": part.get("filename", ""),
                "mime_type": mime_type
            }
            email_data["attachments"].append(attachment)
            
            # Get attachment content
            attachment_id = part.get("body", {}).get("attachmentId")
            if attachment_id:
                attachment_data = service.users().messages().attachments().get(
                    userId="me", messageId=msg_id, id=attachment_id
                ).execute()
                
                attachment["content"] = attachment_data.get("data", "")
        
        # Recursively handle nested parts
        if "parts" in part:
            extract_parts(service, part.get("parts", []), email_data, msg_id, part_id)


def parse_pdf_content(pdf_data):
    """Parse PDF content from base64 data."""
    try:
        decoded_data = base64.urlsafe_b64decode(pdf_data)
        pdf_reader = PdfReader(io.BytesIO(decoded_data))
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""


def extract_transactions(text):
    """
    Extract transactions from statement text.
    This is a simplified example - in a real app, you'd have more 
    sophisticated parsing based on the format of the specific bank's statement.
    """
    transactions = []
    
    # This is a simple pattern matching - real implementation would be more robust
    pattern = r"(\d{1,2}/\d{1,2})\s+(\d{1,2}/\d{1,2})\s+(.+?)\s+(\$?\d+\.\d{2})"
    matches = re.findall(pattern, text)
    
    for match in matches:
        post_date, trans_date, description, amount = match
        transactions.append({
            "post_date": post_date,
            "transaction_date": trans_date,
            "description": description.strip(),
            "amount": float(amount.replace("$", ""))
        })
    
    return transactions


def categorize_transactions(transactions):
    """
    Categorize transactions based on keywords.
    This is simplified - a real implementation would use more sophisticated methods.
    """
    categories = {
        "Dining": ["restaurant", "cafe", "dinner", "lunch", "food", "doordash", "ubereats", "grubhub"],
        "Grocery": ["grocery", "supermarket", "market", "food", "whole foods", "trader"],
        "Travel": ["airline", "hotel", "airbnb", "flight", "travel", "uber", "lyft", "taxi"],
        "Entertainment": ["movie", "theater", "netflix", "spotify", "disney", "hulu", "amazon prime"],
        "Shopping": ["amazon", "walmart", "target", "store", "shop", "purchase"],
        "Gas": ["gas", "shell", "exxon", "mobil", "chevron", "petroleum"],
        "Utilities": ["utility", "electric", "water", "gas", "internet", "phone", "bill"],
        "Healthcare": ["doctor", "pharmacy", "medical", "health", "dental", "hospital"]
    }
    
    categorized = []
    
    for transaction in transactions:
        description = transaction["description"].lower()
        assigned_category = "Other"
        
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                assigned_category = category
                break
                
        transaction["category"] = assigned_category
        categorized.append(transaction)
    
    return categorized


def analyze_spending(transactions):
    """Analyze spending patterns by category."""
    category_totals = {}
    
    for transaction in transactions:
        category = transaction.get("category", "Other")
        amount = transaction.get("amount", 0)
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    return category_totals


def prepare_statement_data(email_data, transactions, spending_analysis):
    """Prepare statement data for storage in MongoDB."""
    return {
        "email_id": email_data["id"],
        "subject": email_data["subject"],
        "from_address": email_data["from"],
        "date": datetime.strptime(email_data["date"], "%a, %d %b %Y %H:%M:%S %z"),
        "content": {
            "body_text": email_data.get("body_text", ""),
            "transactions": transactions,
            "spending_analysis": spending_analysis
        },
        "created_at": datetime.utcnow()
    }
