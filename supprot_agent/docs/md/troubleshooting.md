# Troubleshooting & Common Errors

## 1. Error: 401 Unauthorized (`AUTH_INVALID_TOKEN`)
### Symptoms
CLI commands or API requests fail with HTTP status code `401 Unauthorized` and message `Invalid or expired authorization token`.
### Cause
- Your session token has expired after 30 days of inactivity.
- API Key was revoked or deleted in the admin dashboard.
### Resolution Steps
1. Re-authenticate your CLI by running:
   ```bash
   cloudplatform logout
   cloudplatform login --force
   ```
2. If using an API key in automated environments, generate a new secret key under **Dashboard > Developer Settings > API Keys**.
3. Verify your environment variable `CLOUDPLATFORM_API_KEY` is loaded correctly.

---

## 2. Error: 429 Too Many Requests (`RATE_LIMIT_EXCEEDED`)
### Symptoms
API returns `429 Too Many Requests`.
### Cause
You exceeded the rate limits of your plan:
- Free tier: 60 requests per minute.
- Pro tier: 600 requests per minute.
- Enterprise tier: Configurable / Unlimited.
### Resolution Steps
1. Implement exponential backoff with jitter in your client application (e.g. retry after 1s, 2s, 4s).
2. Check the `Retry-After` HTTP header returned by the API server.
3. If higher throughput is needed, upgrade your plan under **Billing > Change Plan**.

---

## 3. Error: Deployment Timeout (`DEPLOY_TIMEOUT_ERR`)
### Symptoms
Deployment hangs for more than 10 minutes and fails with `Deployment timed out waiting for healthcheck`.
### Cause
- Application failed to bind to `0.0.0.0:$PORT`.
- Health check endpoint `/healthz` returned non-200 status code.
- Heavy build step (e.g., unbounded npm build or machine learning model download).
### Resolution Steps
1. Ensure your server listens on `0.0.0.0` and uses the `$PORT` environment variable (default 8080).
2. Test your healthcheck locally:
   ```bash
   curl -I http://localhost:8080/healthz
   ```
3. Check deployment logs with:
   ```bash
   cloudplatform logs --deployment <DEPLOYMENT_ID> --tail 100
   ```

---

## 4. Resetting Your Password / Locked Account
If your account is locked due to multiple failed login attempts:
1. Go to https://cloudplatform.example.com/forgot-password
2. Enter your account email address.
3. Follow the reset link sent to your email within 30 minutes.
4. If you do not receive the email, check your spam/junk folder or contact support if your company domain has strict inbound email filters.
