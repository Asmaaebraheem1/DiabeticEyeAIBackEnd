# Retinal Image Analysis API

Flask backend for retinal image analysis and contact form management with admin panel.

Features:
- Analyze retinal images (JPG/PNG)
- Process PDF documents (extract first page)
- Handle image URLs
- Contact form submission system
- Admin dashboard for managing submissions

## Quick Start

### Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export FLASK_APP=app
export FLASK_ENV=development
```

## Running the Server

```bash
flask run
```

## API Endpoints

### Public Endpoints

**POST /api/analyze**
- Accepts:
  - Image file (JPG/PNG)
  - PDF file (first page will be analyzed)
  - Image URL
- Returns:
  ```json
  {
    "prediction": "string",
    "confidence": 0.95,
    "extracted_image": "filename.jpg" // only for PDFs
  }
  ```
- Errors:
  - 400: Invalid file/URL
  - 500: Analysis failed

**POST /api/contact**
- Accepts JSON: `{"name": "string", "email": "string", "message": "string"}`
- Returns: `{"message": "Submitted successfully"}` on success (201)
- Validation:
  - All fields required
  - Email must be valid format
  - Name must be at least 2 characters
  - Message must be at least 10 characters

### Admin Endpoints (Require Authentication)

**GET /api/admin/contacts**
- Returns: List of all contacts
- Authentication: Basic Auth or session cookie

**DELETE /api/admin/contacts/:id**
- Deletes contact with specified ID
- Returns: `{"message": "Contact deleted successfully"}` on success
- Errors:
  - 404 if contact not found
  - 401 if not authenticated

**PUT /api/admin/contacts/:id**
- Accepts JSON: `{"name": "string", "email": "string", "message": "string"}`
- Updates contact with specified ID
- Returns: `{"message": "Contact updated successfully"}` on success
- Validation: Same as POST endpoint
- Errors:
  - 404 if contact not found
  - 400 if validation fails
  - 401 if not authenticated

## Database

SQLite database will be created at `app.db` on first run.

## Complete API Documentation

### Authentication
- Basic Auth: `Authorization: Basic base64(username:password)`
- Session cookies for admin panel
- JWT support coming in v2.0

### Error Codes
- 400: Bad Request (validation failed)
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

### Request/Response Examples
```json
// POST /api/contact
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello, I have a question"
}

// Response
{
  "id": 123,
  "created_at": "2025-04-25T19:15:00Z",
  "message": "Submitted successfully"
}
```

## Advanced Setup

### Configuration
- Copy `.env.example` to `.env`
- Set `SECRET_KEY` for production
- Configure database URI if not using SQLite

### Database Setup
```bash
flask db init  # First time only
flask db migrate -m "initial migration"
flask db upgrade
```


## Architecture Overview

The application follows a layered architecture with clear separation of concerns:

### Repository Pattern
- `repository.py` handles all database operations
- Provides abstraction between database and service layer
- Implements CRUD operations for all models

### Service Layer
- `services.py` contains business logic
- Validates inputs before passing to repository
- Handles data transformation and error handling

### Use Cases
1. Image Analysis
   - File/URL validation → Image processing → Model prediction → Results formatting
2. Contact Form Submission
   - Validate input → Save to database → Send confirmation
2. Admin Operations
   - Authentication → CRUD operations → Audit logging

### Data Flow
1. Request → Routes → Services → Repository → Database
2. Response ← Repository ← Services ← Routes

## Testing

```bash
python -m pytest tests/
```
- Coverage report: `pytest --cov=app tests/`
- With HTML report: `pytest --cov=app --cov-report=html tests/`

## Migration Commands
- Create new migration: `flask db migrate -m "description of changes"`
- Apply migrations: `flask db upgrade`
- Rollback migration: `flask db downgrade`
- Show migration history: `flask db history`
