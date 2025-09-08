# Chatity
Chatity is a sophisticated, full-stack AI chatbot application featuring real-time streaming responses, multi-provider AI model support (OpenAI, Anthropic, Google Gemini, Ollama), and a professional-grade, persistent user interface.

---

## 📦 Project Structure
```
chatity-app/
├─ frontend/
|  └─ frontend.html          # React frontend
├─ backend/
|  ├─ crud.py                   # Database Operations
|  ├─ database.py               # Database configuration
|  ├─ main.py                   # Main FastAPI with Endpoints
|  ├─ models.py                 # SQLAlchemy database models
|  ├─ schemas.py                # Pydantic validation
|  └─ security.py               # Authenticator
├─README.md                  # Comprehensive setup guide
├─ env.example               # example of .env
└─ requirements.txt          # Python dependencies
```
## 🛠️ Technology Stack
| Area     | Technology                             |
|----------|----------------------------------------|
| **Frontend** | React.js, Redux Toolkit, Tailwind CSS  |
| **Backend**  | FastAPI (Python 3.8+), Uvicorn         |
| **Database** | PostgreSQL                             |
| **API**      | REST & Server-Sent Events (SSE)        |
| **Auth**     | JWT (JSON Web Tokens)                  |
| **ORM**      | SQLAlchemy with Alembic for migrations |
## ✨ Features
- **Real-Time Streaming:** ChatGPT-like live typing effect for instant feedback.
- **Multi-Provider Support:** Seamlessly switch between models from OpenAI, Google, Anthropic, and local Ollama instances.
- **Persistent Sessions:** Full session and message history saved to a PostgreSQL database.
- **User Authentication:** Secure JWT-based user registration and login system.
- **Modern UI:** A sleek, responsive, and intuitive interface built with React and custom components.
- **Full Session Management:** Create, rename, search, and delete chat sessions.
- **Editable User Profiles:** Users can update their profile information.
- **Collapsible Sidebar:** A flexible and responsive layout for all screen sizes.
## 📥 Download
[chatity-app.zip](https://github.com/AbdulMuizz789/AIAgenteZSCM/archive/refs/heads/main.zip) - Ready to use!

## 🚀 Getting Started
### Prerequisites
- Python 3.8+ and ```pip```
- Node.js and ```npm``` (only to serve the frontend, not required for development as it's a single HTML file)
- PostgreSQL database server
- Git
###
#### 1. Download and Extract the zip file
Go to the extracted folder ```chatity-app```
#### 2. Backend Setup:
```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```
Now, edit the ```.env``` file with your database URL and AI provider API keys.

```.env``` file:
```
DATABASE_URL="postgresql+asyncpg://user:password@localhost/chatitydb"
SECRET_KEY="your_super_secret_key_for_jwt"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# --- AI Provider API Keys ---
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."
ANTHROPIC_API_KEY="..."
```
#### 3. Database Migration:
Initialize and apply the database migrations using Alembic.
```bash
alembic init alembic
```
Go to alembic.ini and set the sqlalchemy.url to your postgresql database
```ini
sqlalchemy.url = postgresql+asyncpg://user:password@localhost/dbname
```
Then run the commands to migrate the database
```bash
# alembic revision --autogenerate -m "Initialize DB"
alembic upgrade head
```
#### 4. Run the Backend Server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The backend API will be available at http://localhost:8000.
#### 5. Frontend Setup:
The frontend is a single index.html file located in the frontend/ directory. You can open it directly in your browser, but for the best experience (avoiding CORS issues), serve it with a simple HTTP server.
```bash
# Install a simple server (if you don't have one)
npm install -g serve

# Navigate to the frontend directory
cd frontend

# Start the server
serve -s .
```
The application will be accessible at http://localhost:3000 (or another port specified by serve).
## 🎯 Assignment Coverage
This project satisfies these mandatory requirements: 
- ✅ **Provider/Model Switching** (20 marks) - Multi-provider support 
- ✅ **Persistence + Restore** (20 marks) - Session management 
- ✅ **UI/UX Polish** (10 marks) - Modern ChatGPT-like interface 
- ✅ **Repo/Docs Hygiene** (10 marks) - Professional structure
<!-- - ✅ **Error Handling + Limits** (10 marks) - Rate limiting, token caps  -->
<!-- - ✅ **SSE Streaming** (30 marks) - Real-time token-by-token responses  -->

## 🔬 API Testing (SSE Example)
You can test the real-time streaming endpoint using ```curl```.
1) First, log in through the UI or use the /token endpoint to get a JWT token.
1) Export the token as an environment variable:
```
export JWT_TOKEN="your_long_jwt_token_here"
```
3) Make the request to the streaming endpoint (replace ```your_session_id```):
```bash
curl -N -X POST http://localhost:8000/chat/stream \
-H "Authorization: Bearer $JWT_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "session_id": "your_session_id",
    "prompt": "Hello, world!",
    "provider": "gemini",
    "model": "gemini-pro"
}'
```
You will see the token-by-token response streamed directly to your terminal.
## 🖼️ Screenshots
Placeholder for a screenshot of the login screen.

Placeholder for a screenshot of the main chat interface.

Placeholder for a screenshot of the profile editing modal.
## 👥 Team & Contributions
| Member | Role | Contributions |
| ---- | ---- | ---- |
| Abdul Muizz | Full-Stack Lead | Project architecture, backend, frontend, deployment |
| Jampala Swathvik | Backend Developer | API development, database schema, debugging, and testing |
<!-- 
# Chatity - A Multi-Provider AI Chatbot Platform

Follow these instructions to set up and run the project locally.
### Prerequisites
- Python 3.8+ and ```pip```
- Node.js and ```npm``` (only to serve the frontend, not required for development as it's a single HTML file)
- PostgreSQL database server
- Git
### Installation & Setup
#### 1. Clone the repository:
```bash
git clone [https://github.com/](https://github.com/)[Your-Username]/omnichat.git
cd omnichat
```
 -->