# API Documentation

## Overview

This document describes the API endpoints and usage for the Telegram Bot application.

## Base URL

```
http://localhost:8080
```

## Authentication

All API requests require authentication via a Bearer token in the Authorization header:

```
Authorization: Bearer <your-api-token>
```

## Endpoints

### Health Check

Check if the API is running.

```
GET /health
```

**Response:**
```json
{
    "status": "ok",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Send Message

Send a message to a Telegram chat.

```
POST /api/send-message
```

**Request Body:**
```json
{
    "chat_id": 123456789,
    "text": "Hello, World!",
    "parse_mode": "HTML"
}
```

**Parameters:**
- `chat_id` (integer, required): Telegram chat ID
- `text` (string, required): Message text
- `parse_mode` (string, optional): Parse mode (HTML, Markdown, MarkdownV2)

**Response:**
```json
{
    "success": true,
    "message_id": 12345
}
```

### Get Chat History

Retrieve chat history from the database.

```
GET /api/chat-history?chat_id=123456789&limit=50&offset=0
```

**Query Parameters:**
- `chat_id` (integer, required): Telegram chat ID
- `limit` (integer, optional, default: 50): Number of messages to retrieve
- `offset` (integer, optional, default: 0): Offset for pagination

**Response:**
```json
{
    "messages": [
        {
            "id": 1,
            "chat_id": 123456789,
            "role": "user",
            "content": "Hello",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "limit": 50,
    "offset": 0
}
```

### Analyze Code Repository

Analyze a GitHub repository using OpenAI.

```
POST /api/analyze-repo
```

**Request Body:**
```json
{
    "repo_url": "https://github.com/username/repository",
    "analysis_type": "code_review"
}
```

**Parameters:**
- `repo_url` (string, required): GitHub repository URL
- `analysis_type` (string, required): Type of analysis (code_review, security, performance)

**Response:**
```json
{
    "success": true,
    "analysis_id": "uuid-here",
    "summary": "Analysis summary text",
    "findings": [
        {
            "severity": "high",
            "file": "src/main.py",
            "line": 42,
            "description": "Potential security vulnerability"
        }
    ]
}
```

### Get Analysis Results

Retrieve analysis results by ID.

```
GET /api/analysis/{analysis_id}
```

**Path Parameters:**
- `analysis_id` (string, required): UUID of the analysis

**Response:**
```json
{
    "analysis_id": "uuid-here",
    "status": "completed",
    "repo_url": "https://github.com/username/repository",
    "analysis_type": "code_review",
    "summary": "Analysis summary text",
    "findings": [],
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:01:00Z"
}
```

### List Analyses

List all analyses for a repository.

```
GET /api/analyses?repo_url=https://github.com/username/repository&limit=10&offset=0
```

**Query Parameters:**
- `repo_url` (string, optional): Filter by repository URL
- `limit` (integer, optional, default: 10): Number of analyses to retrieve
- `offset` (integer, optional, default: 0): Offset for pagination

**Response:**
```json
{
    "analyses": [
        {
            "analysis_id": "uuid-here",
            "repo_url": "https://github.com/username/repository",
            "analysis_type": "code_review",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 5,
    "limit": 10,
    "offset": 0
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Bad Request",
    "message": "Invalid chat_id parameter",
    "code": 400
}
```

### 401 Unauthorized
```json
{
    "error": "Unauthorized",
    "message": "Invalid or missing authentication token",
    "code": 401
}
```

### 404 Not Found
```json
{
    "error": "Not Found",
    "message": "Analysis not found",
    "code": 404
}
```

### 429 Too Many Requests
```json
{
    "error": "Rate Limit Exceeded",
    "message": "Too many requests, please try again later",
    "code": 429,
    "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal Server Error",
    "message": "An unexpected error occurred",
    "code": 500
}
```

## Rate Limiting

- 100 requests per minute per IP address
- 1000 requests per hour per API token
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Webhooks

### Register Webhook

Register a webhook for receiving events.

```
POST /api/webhooks
```

**Request Body:**
```json
{
    "url": "https://example.com/webhook",
    "events": ["message_sent", "analysis_completed"],
    "secret": "your-webhook-secret"
}
```

**Parameters:**
- `url` (string, required): Webhook endpoint URL
- `events` (array, required): List of events to subscribe to
- `secret` (string, optional): Secret for webhook signature verification

**Response:**
```json
{
    "success": true,
    "webhook_id": "uuid-here",
    "url": "https://example.com/webhook",
    "events": ["message_sent", "analysis_completed"]
}
```

### Delete Webhook

Delete a registered webhook.

```
DELETE /api/webhooks/{webhook_id}
```

**Path Parameters:**
- `webhook_id` (string, required): UUID of the webhook

**Response:**
```json
{
    "success": true,
    "message": "Webhook deleted successfully"
}
```

## Data Types

### Message Object
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Message ID |
| chat_id | integer | Telegram chat ID |
| role | string | Message role (user, assistant, system) |
| content | string | Message content |
| timestamp | string | ISO 8601 timestamp |

### Analysis Object
| Field | Type | Description |
|-------|------|-------------|
| analysis_id | string | UUID of the analysis |
| repo_url | string | GitHub repository URL |
| analysis_type | string | Type of analysis |
| status | string | Analysis status (pending, processing, completed, failed) |
| summary | string | Analysis summary |
| findings | array | Array of finding objects |
| created_at | string | ISO 8601 timestamp |
| completed_at | string | ISO 8601 timestamp |

### Finding Object
| Field | Type | Description |
|-------|------|-------------|
| severity | string | Severity level (low, medium, high, critical) |
| file | string | File path |
| line | integer | Line number |
| description | string | Finding description |

## Changelog

### v1.0.0 (2024-01-01)
- Initial API release
- Basic message sending and history retrieval
- GitHub repository analysis
- Webhook support