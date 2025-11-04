# OAuth Testing Guide
## Quick Test Instructions

## Current Status

✅ **Google OAuth**: Configured and working  
❌ **GitHub OAuth**: Not configured  
❌ **Facebook OAuth**: Not configured  
❌ **Apple Sign In**: Not configured  

## Testing OAuth Endpoints

### Test Google OAuth (Already Configured)

1. **Get Authorization URL**:
   ```bash
   curl "http://localhost:8000/api/v1/auth/oauth/google/authorize?redirect_uri=http://localhost:3000/callback"
   ```

2. **Response**:
   ```json
   {
     "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
     "state": "Sr89xDRq4F8DC0rL5BSOzePMQmCW-JdDyHi4aXbtdGA"
   }
   ```

3. **Open the `authorize_url` in your browser**:
   - Copy the `authorize_url` from the response
   - Open it in a browser
   - You'll be redirected to Google's OAuth consent screen
   - Sign in with your Google account
   - Grant permissions

4. **After granting permissions**, Google will redirect to:
   ```
   http://localhost:3000/callback?code=...&state=...
   ```

5. **Test the callback** (if you have a frontend):
   - The callback should hit: `http://localhost:8000/api/v1/auth/oauth/google/callback?code=...&state=...`
   - This will exchange the code for tokens and create/login the user

### Test Other Providers

**GitHub**:
```bash
curl "http://localhost:8000/api/v1/auth/oauth/github/authorize?redirect_uri=http://localhost:3000/callback"
```
Expected: Error - "OAuth provider github is not configured"

**Facebook**:
```bash
curl "http://localhost:8000/api/v1/auth/oauth/facebook/authorize?redirect_uri=http://localhost:3000/callback"
```
Expected: Error - "OAuth provider facebook is not configured"

**Apple**:
```bash
curl "http://localhost:8000/api/v1/auth/oauth/apple/authorize?redirect_uri=http://localhost:3000/callback"
```
Expected: Error - "OAuth provider apple is not configured"

## Full OAuth Flow Test

### Step 1: Get Authorization URL

```bash
# Google OAuth
curl "http://localhost:8000/api/v1/auth/oauth/google/authorize?redirect_uri=http://localhost:3000/callback" \
  | python3 -m json.tool
```

### Step 2: Open URL in Browser

1. Copy the `authorize_url` from the response
2. Open it in your browser
3. Sign in with Google
4. Grant permissions

### Step 3: Handle Callback

After Google redirects, you'll get:
```
http://localhost:3000/callback?code=AUTHORIZATION_CODE&state=STATE_VALUE
```

**Note**: The callback URL (`http://localhost:3000/callback`) should be handled by your frontend. If you don't have a frontend yet, you can:

1. Test manually by copying the `code` and `state` from the URL
2. Call the callback endpoint directly:
   ```bash
   curl "http://localhost:8000/api/v1/auth/oauth/google/callback?code=CODE&state=STATE&redirect_uri=http://localhost:3000/callback"
   ```

### Step 4: Verify Response

The callback should return:
- **If redirect_uri is a URL**: Redirects to frontend with tokens in hash fragment
- **If redirect_uri is not a URL**: Returns JSON with tokens

Example JSON response:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "access_token": "jwt_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer",
  "is_new_user": true,
  "provider": "google"
}
```

## Testing with Postman or Browser

### Using Browser:

1. Visit:
   ```
   http://localhost:8000/api/v1/auth/oauth/google/authorize?redirect_uri=http://localhost:3000/callback
   ```

2. You'll get a JSON response with `authorize_url`

3. Copy the `authorize_url` and open it in a new tab

4. Complete the OAuth flow

5. After redirect, extract the `code` from the URL:
   ```
   http://localhost:3000/callback?code=4/0Aean...&state=...
   ```

6. Test the callback endpoint:
   ```
   http://localhost:8000/api/v1/auth/oauth/google/callback?code=4/0Aean...&state=...&redirect_uri=http://localhost:3000/callback
   ```

### Using curl:

```bash
# 1. Get authorize URL
AUTH_RESPONSE=$(curl -s "http://localhost:8000/api/v1/auth/oauth/google/authorize?redirect_uri=http://localhost:3000/callback")
AUTH_URL=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['authorize_url'])")
STATE=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['state'])")

echo "Authorize URL: $AUTH_URL"
echo "State: $STATE"
echo ""
echo "Open the URL in your browser, then use the code from the redirect to test the callback:"
echo "curl 'http://localhost:8000/api/v1/auth/oauth/google/callback?code=CODE&state=$STATE&redirect_uri=http://localhost:3000/callback'"
```

## Quick Test Script

Run the test script:
```bash
cd backend
python3 test_oauth.py
```

## Troubleshooting

### "OAuth provider X is not configured"
- **Cause**: OAuth credentials not set in environment variables
- **Solution**: Add credentials to `.env` file (see `OAUTH_SETUP.md`)

### "redirect_uri_mismatch"
- **Cause**: Redirect URI doesn't match what's configured in OAuth provider console
- **Solution**: Ensure callback URL matches exactly in Google Console

### "invalid_client"
- **Cause**: Client ID or Secret is incorrect
- **Solution**: Verify credentials in `.env` file

### "access_denied"
- **Cause**: User denied consent or app is in testing mode
- **Solution**: Add test users in Google Console or submit app for verification

## Next Steps

1. **Set up other providers** (see `OAUTH_SETUP.md`):
   - GitHub OAuth
   - Facebook Login
   - Apple Sign In

2. **Test full OAuth flow**:
   - Create a simple frontend to handle callbacks
   - Test end-to-end user authentication

3. **Production deployment**:
   - Store OAuth credentials in AWS Secrets Manager
   - Use production callback URLs
   - Submit apps for verification (if needed)

