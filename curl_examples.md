## Best Card API - cURL Examples

### Authentication

#### Register a new user:
```bash
curl -k -X POST https://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_secure_password"
  }'
```

#### Login and get access token:
```bash
curl -k -X POST https://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_secure_password"
```

The response will include an access token that you should use in subsequent requests:
```json
{
  "access_token": "your_jwt_token_here",
  "token_type": "bearer"
}
```

### Card Recommendation

#### Get card recommendation based on spending:
```bash
curl -k -X POST https://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token_here" \
  -d '{
    "spends": [
      {"category": "Dining", "amount": 350},
      {"category": "Grocery", "amount": 450},
      {"category": "Travel", "amount": 200},
      {"category": "Entertainment", "amount": 100},
      {"category": "Gas", "amount": 150}
    ]
  }'
```

Example response:
```json
{
  "recommended_card": "Travel Elite Card",
  "score": 37.0,
  "comparison": {
    "Cash Rewards Card": 35.0,
    "Travel Elite Card": 37.0,
    "Premium Rewards Card": 10.0
  }
}
```

### Gmail Integration

#### Initiate Gmail OAuth flow:
```bash
curl -k https://localhost:8000/api/gmail/auth \
  -H "Authorization: Bearer your_jwt_token_here"
```

The response will include an authentication URL that you should open in a browser:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

#### Parse a recent e-statement:
```bash
curl -k https://localhost:8000/api/gmail/parse-statement \
  -H "Authorization: Bearer your_jwt_token_here"
```

Example response:
```json
{
  "message": "Statement parsed successfully",
  "email_subject": "Your Monthly Statement is Ready",
  "transaction_count": 15,
  "spending_analysis": {
    "Dining": 320.45,
    "Grocery": 425.12,
    "Travel": 180.25,
    "Entertainment": 95.75,
    "Other": 253.67
  }
}
```

Note: All examples use `-k` flag to ignore SSL certificate verification since we're using self-signed certificates for development. In production, use proper SSL certificates and remove this flag.
