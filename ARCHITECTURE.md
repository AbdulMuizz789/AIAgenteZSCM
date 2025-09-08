# OmniChat - System Architecture
This document outlines the architecture of the OmniChat application, including the system design, database schema, and data flow.
## 1. System Architecture Diagram
The application follows a decoupled, client-server architecture. The React frontend is a Single Page Application (SPA) that communicates with a FastAPI backend. A PostgreSQL database handles data persistence, and the backend communicates with external AI provider APIs.

[Placeholder for a System Architecture Diagram. The diagram should show: User -> React Client (Browser) -> (REST for Auth/Data, SSE for Chat) -> FastAPI Backend -> PostgreSQL DB. And FastAPI Backend -> External AI APIs (OpenAI, Gemini, etc).]
### Components:
- **Client (React SPA):** A static application responsible for rendering the UI and managing client-side state with Redux. It is hosted on a static file server like S3.
- **Backend (FastAPI):** A Python-based API server that handles all business logic, user authentication, database interactions, and communication with AI providers.
- **Database (PostgreSQL):** A relational database for storing user, session, and message data.
- **AI Providers:** Third-party APIs that provide the generative AI models.
## 2. Database Entity-Relationship (ER) Diagram
The database is designed with three core tables: ```users```, ```sessions```, and ```messages```, following a normalized structure.

[Placeholder for a Database ER Diagram. The diagram should show the users, sessions, and messages tables with their columns and relationships (User has many Sessions, Session has many Messages).]

### Relationships:
- **```users``` to ```sessions```:** One-to-Many. A single user can have multiple chat sessions.
- **```sessions``` to ```messages```:** One-to-Many. A single session contains a history of multiple messages.
## 3. API Flow Diagrams
### a) User Authentication Flow
[Placeholder for an Auth Flow Diagram (Sequence Diagram). It should show the user entering credentials, the React client sending a request to /token, FastAPI validating, creating a JWT, and returning it to the client, which stores it.]
### b) Real-Time Chat (SSE) Flow
[Placeholder for an SSE Flow Diagram (Sequence Diagram). It should show the React client sending an initial POST request to /chat/stream, FastAPI establishing the connection, forwarding the prompt to an AI provider, receiving a stream of tokens back, and pushing each token to the client as a data: event over the open SSE connection.]
## 4. Frontend Component Interaction
The React frontend is structured with a clear separation of concerns, managed by Redux.

[Placeholder for a Component Interaction Diagram. It should show the main App component, which manages the Auth state. The ChatApp component contains the Sidebar and the main chat view. The Sidebar lists sessions. Clicking a session updates the Redux state, causing the ChatArea to re-render with the new messages.]
### State Flow:
1) User actions (e.g., sending a message, creating a session) dispatch actions to the Redux store.
2) Thunks handle asynchronous API calls to the FastAPI backend.
1) The Redux state is updated with the new data.
1) React components subscribed to the state re-render automatically.