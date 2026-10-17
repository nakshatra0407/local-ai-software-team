# FastAPI Guidelines

## API Design

Use FastAPI for building Python web APIs.

Define routes using FastAPI decorators.

Use clear HTTP methods such as GET, POST, PUT, and DELETE.

## Request Validation

Use Pydantic models to validate structured request data.

Validate incoming data before processing it.

Return appropriate HTTP status codes.

## Project Structure

Keep API routes organized.

Separate API logic from business logic when the project becomes larger.

## Security

Do not expose secrets in API responses.

Validate user-controlled input.

Do not trust client-provided data automatically.