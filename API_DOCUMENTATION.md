# Standard API Design Format

All new APIs built for this project should strictly follow this standardized format for consistency in design and documentation.

## Response Structure

Responses must always include an HTTP Status `code`, a boolean `status`, a `message` string, and a JSON `body` dictionary.

### 1. Success Response Template
```json
{
  "code": 200,
  "status": true,
  "message": "Action completed successfully.",
  "body": {
    "key": "value"
  }
}
```

### 2. Error Response Template
```json
{
  "code": 400,
  "status": false,
  "message": "Specific error message explaining what failed.",
  "body": {}
}
```
