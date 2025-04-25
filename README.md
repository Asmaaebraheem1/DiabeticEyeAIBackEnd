# Contact Form API

Flask backend for handling contact form submissions.

## Setup

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
