# API Reference and Integration Guide

## Base URL
All REST API requests should be sent to:
```
https://api.cloudplatform.example.com/v1
```

## Authentication
Authenticate all requests using the `Authorization` Bearer token header:
```http
Authorization: Bearer YOUR_API_SECRET_KEY
```

## Endpoints

### 1. List Projects
- **Method**: `GET /projects`
- **Query Parameters**:
  - `limit` (integer, optional, default: 20, max: 100)
  - `status` (string, optional: `active`, `archived`)
- **Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "proj_99812",
      "name": "ecommerce-backend",
      "status": "active",
      "created_at": "2026-01-15T09:00:00Z"
    }
  ]
}
```

### 2. Trigger Deployment
- **Method**: `POST /projects/{project_id}/deploy`
- **Request Body**:
```json
{
  "branch": "main",
  "commit_sha": "a1b2c3d4",
  "environment": "production"
}
```
- **Response**:
```json
{
  "status": "success",
  "deployment_id": "dep_456789",
  "build_url": "https://dashboard.cloudplatform.example.com/deployments/dep_456789"
}
```

## Webhooks
You can register webhooks to receive real-time notifications for deployment events:
- Events supported: `deployment.started`, `deployment.succeeded`, `deployment.failed`.
- Webhook payloads include HMAC-SHA256 signature in `X-CloudPlatform-Signature` header for verification.
