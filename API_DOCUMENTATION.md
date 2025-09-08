# OmniChat - API Documentation
This document provides a detailed specification for the OmniChat backend API endpoints.
## 
**Base URL:** ```http://localhost:8000```

**Authentication**: All protected endpoints require a JWT in the ```Authorization``` header:

 ```Authorization: Bearer <your_token>```
## 1. Authentication
### POST ```/token```
- **Description:** Authenticates a user and returns a JWT access token.
- **Method:** ```POST```
- **Headers:** ```Content-Type: application/x-www-form-urlencoded```
- **Body (form-data):**
    - ```username``` (string, required): User's email.
    - ```password``` (string, required): User's password.
- **Success Response (200 OK):**
```json
{
  "access_token": "your.jwt.token",
  "token_type": "bearer"
}
```
- **Error Response (401 Unauthorized):**
```json
{ "detail": "Incorrect username or password" }
```
## 2. Users
### POST ```/users/```
- **Description:** Creates a new user.
- **Method:** ```POST```
- **Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "strongpassword"
}
```
- **Success Response (200 OK):**
```json
{
  "id": "user-uuid",
  "username": "testuser",
  "email": "test@example.com"
}
```
### GET ```/users/me/```
- **Description:** Retrieves the profile of the currently authenticated user.
- **Method:** ```GET```
- **Headers:** ```Authorization: Bearer <token>```
- **Success Response (200 OK):**
```json
{
  "id": "user-uuid",
  "username": "testuser",
  "email": "test@example.com"
}
```
### PUT ```/users/me/```
- **Description:** Updates the profile of the currently authenticated user.
- **Method:** ```PUT```
- **Headers:** ```Authorization: Bearer <token>```
- **Body:**
```json
{ "username": "new_username" }
```
- **Success Response (200 OK):**
```json
{
  "id": "user-uuid",
  "username": "new_username",
  "email": "test@example.com"
}
```
## 3. Sessions
### GET ```/sessions```
- **Description:** Gets a list of all sessions for the authenticated user.
- **Method:** ```GET```
- **Headers:** ```Authorization: Bearer <token>```
- **Success Response (200 OK):**
```json
[
  {
    "id": "session-uuid-1",
    "title": "My First Chat",
    "user_id": "user-uuid",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:05:00Z"
  }
]
```
### POST ```/sessions```
- **Description:** Creates a new chat session.
- **Method:** ```POST```
- **Headers:** ```Authorization: Bearer <token>```
- **Body:**
```json
{ "title": "New Chat Session" }
```
- **Success Response (200 OK):** Returns the newly created session object.
### GET ```/sessions/{session_id}```
- **Description:** Gets the details and message history of a specific session.
- **Method:** ```GET```
- **Headers:** ```Authorization: Bearer <token>```
- **Success Response (200 OK):**
```json
{
  "id": "session-uuid-1",
  "title": "My First Chat",
  "messages": [
    { "id": "msg-uuid-1", "role": "user", "content": "Hello!" },
    { "id": "msg-uuid-2", "role": "assistant", "content": "Hi there!" }
  ]
}
```
### PUT ```/sessions/{session_id}```
- **Description:** Updates the title of a session.
- **Method:** ```PUT```
- **Headers:** ```Authorization: Bearer <token>```
- **Body:**
```json
{ "title": "Updated Title" }
```
- **Success Response (200 OK):** Returns the updated session object.
### DELETE ```/sessions/{session_id}``
- **Description:** Deletes a session and its associated messages.
- **Method:** ```DELETE```
- **Headers:** ```Authorization: Bearer <token>```
- **Success Response:** ```204 No Content```
## 4. Chat Streaming
### POST ```/chat/stream```
- **Description:** Initiates a real-time chat response using Server-Sent Events (SSE).
- **Method:** ```POST```
- **Headers:** ```Authorization: Bearer <token>```
- **Content-Type:** ```application/json```
- **Body:**
```json
{
  "session_id": "session-uuid-1",
  "prompt": "Tell me a joke",
  "provider": "gemini",
  "model": "gemini-pro"
}
```
- **Success Response (200 OK):**
A stream of ```text/event-stream data```. Each message is a token.
```
data: {"delta": "Why"}

data: {"delta": " don't"}

data: {"delta": " scientists"}

...

data: [DONE]
```