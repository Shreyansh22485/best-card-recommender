# Best Card Recommender

A proof-of-concept application that recommends the best credit card based on spending patterns, parses Gmail e-statements, and stores user data in MongoDB.

## Features

- Credit card recommendation engine that calculates the best card based on spending categories
- Gmail OAuth integration for e-statement parsing
- User authentication with JWT
- MongoDB data storage for user profiles, preferences, and parsed statements
- Secure HTTPS with self-signed certificates for development

## Tech Stack

### Backend
- FastAPI
- MongoDB
- JWT authentication
- Google OAuth and Gmail API integration
- PyPDF2 for PDF parsing

### Frontend
- React
- React Router for navigation
- Axios for API requests

## Project Structure

```
best-card/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── data/          # Credit card data
│   │   ├── models/        # Database models
│   │   ├── routers/       # API routes
│   │   └── utils/         # Utility functions
│   ├── .env               # Environment variables (create from .env.example)
│   ├── generate_cert.py   # Script to generate SSL certificates
│   ├── requirements.txt   # Python dependencies
│   └── run.py             # Server startup script
└── frontend/              # React frontend
    ├── public/
    ├── src/
    │   ├── components/    # React components
    │   └── ...
    └── package.json       # NPM dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8+ and pip
- Node.js 14+ and npm
- MongoDB running locally or accessible via connection string
- Google Cloud Platform account with Gmail API enabled

### Quick Setup (Windows)

For the easiest setup experience, run the setup script:

```powershell
.\setup.ps1
```

This script will:
1. Check all prerequisites (Python, Node.js, MongoDB)
2. Install all dependencies for both frontend and backend
3. Generate SSL certificates
4. Create a `.env` file from the template
5. Create test data with a sample user

After running the setup script, you can start the application:

```powershell
.\start.ps1
```

### Quick Start (Windows)

If you've already set up the project and just want to run it:

```powershell
.\start.ps1
```

This script will:
1. Generate SSL certificates if needed
2. Check MongoDB connection
3. Create test data (email: test@example.com, password: password123)
4. Start both backend and frontend servers in separate terminal windows

### Manual Setup

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your configuration:
   - Set a strong `SECRET_KEY` for JWT authentication
   - Configure MongoDB connection details
   - Add your Google OAuth credentials

5. Generate SSL certificates for HTTPS:
   ```
   python generate_cert.py
   ```

6. Start the FastAPI server:
   ```
   python run.py
   ```
   The API will be available at https://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install NPM dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```
   The frontend will be available at http://localhost:3000

### Google OAuth Setup

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Gmail API
3. Create OAuth credentials (Web application type)
4. Add redirect URI: `https://localhost:8000/api/gmail/callback`
5. Copy the Client ID and Client Secret to your `.env` file

## API Examples

Detailed cURL examples can be found in the [curl_examples.md](curl_examples.md) file.

### Get Card Recommendation

```bash
curl -X POST https://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "spends": [
      {"category": "Dining", "amount": 350},
      {"category": "Grocery", "amount": 450},
      {"category": "Travel", "amount": 200}
    ]
  }'
```

### Connect Gmail Account

```bash
curl https://localhost:8000/api/gmail/auth \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Notes

- The application uses self-signed certificates for development. In production, use proper SSL certificates.
- Environment variables are used to store sensitive information. Never commit the `.env` file to version control.
- The frontend uses HTTPS for secure communication with the backend API.

## Troubleshooting

### Python Dependency Issues

If you encounter issues with packages that require Rust compilation (like pydantic):

1. Try installing packages with the `--only-binary=:all:` flag:
   ```
   python -m pip install -r requirements.txt --only-binary=:all:
   ```

2. If that doesn't work, install packages individually:
   ```
   python -m pip install fastapi uvicorn pymongo --only-binary=:all:
   python -m pip install pydantic==2.3.0 --only-binary=:all:
   ```

3. Use the setup.ps1 script which handles many common installation issues automatically.

### SSL Certificate Generation

If the default certificate generation doesn't work:

1. Try the alternative script:
   ```
   python backend/generate_cert_alt.py
   ```

2. Ensure you have either pyOpenSSL or cryptography installed:
   ```
   python -m pip install pyopenssl cryptography --only-binary=:all:
   ```

### MongoDB Connection

If you're having issues connecting to MongoDB:

1. Verify MongoDB is running:
   ```
   Get-Service MongoDB
   ```

2. Check the connection string in your `.env` file
3. Try connecting with MongoDB Compass to test your connection
