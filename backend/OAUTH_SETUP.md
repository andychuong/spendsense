# OAuth Setup Guide
## SpendSense Platform - Backend Layer

This guide provides step-by-step instructions for setting up OAuth providers for SpendSense.

---

## Google OAuth 2.0 Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **"New Project"**
4. Enter project details:
   - **Project name**: `SpendSense` (or your preferred name)
   - **Organization**: Select your organization (if applicable)
   - **Location**: Select your organization or leave as "No organization"
5. Click **"Create"**

### Step 2: Enable Google+ API / OAuth 2.0 API

1. In the Google Cloud Console, go to **"APIs & Services"** > **"Library"**
2. Search for **"Google+ API"** or **"People API"**
3. Click on the API (either works for OAuth)
4. Click **"Enable"**

**Note**: Google+ API is deprecated but still works. For newer projects, use **"People API"** or **"Google Identity API"**.

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** > **"OAuth consent screen"**
2. Select **"External"** (unless you have a Google Workspace account)
3. Click **"Create"**
4. Fill in the required information:
   - **App name**: `SpendSense` (or your app name)
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
   - Click **"Save and Continue"**
5. **Scopes** (Step 2):
   - Click **"Add or Remove Scopes"**
   - Add the following scopes:
     - `email`
     - `profile`
     - `openid`
   - Click **"Update"** then **"Save and Continue"**
6. **Test users** (Step 3):
   - If your app is in "Testing" mode, add test user emails
   - Click **"Save and Continue"**
7. **Summary** (Step 4):
   - Review the information
   - Click **"Back to Dashboard"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"+ Create Credentials"** > **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen first (see Step 3)
4. Select **"Web application"** as the application type
5. Fill in the details:
   - **Name**: `SpendSense Backend` (or your preferred name)
   - **Authorized JavaScript origins**:
     - For development: `http://localhost:8000`
     - For production: `https://api.spendsense.example.com` (replace with your domain)
   - **Authorized redirect URIs**:
     - For development: `http://localhost:8000/api/v1/auth/oauth/google/callback`
     - For production: `https://api.spendsense.example.com/api/v1/auth/oauth/google/callback`
     - **Important**: Add both development and production URLs if needed
6. Click **"Create"**
7. **Copy the credentials**:
   - **Client ID**: Copy this value (e.g., `123456789-abcdefghijklmnop.apps.googleusercontent.com`)
   - **Client Secret**: Copy this value (e.g., `GOCSPX-abcdefghijklmnopqrstuvwxyz`)
   - **Note**: The Client Secret is only shown once! Save it securely.

### Step 5: Configure Environment Variables

Add the Google OAuth credentials to your `.env` file:

```bash
# Google OAuth Configuration
OAUTH_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
OAUTH_GOOGLE_CLIENT_SECRET=your-client-secret-here
```

**Example:**
```bash
OAUTH_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
OAUTH_GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

### Step 6: Verify Setup

1. Start your FastAPI server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Test the OAuth endpoint:
   ```bash
   curl "http://localhost:8000/api/v1/auth/oauth/google/authorize?redirect_uri=http://localhost:3000/callback"
   ```

3. You should receive a response with an `authorize_url` that redirects to Google's OAuth consent screen.

### Important Notes

- **Development vs Production**:
  - Use different redirect URIs for development and production
  - Google requires exact match of callback URLs

- **Callback URL Format**:
  - Development: `http://localhost:8000/api/v1/auth/oauth/google/callback`
  - Production: `https://api.spendsense.example.com/api/v1/auth/oauth/google/callback`

- **Security**:
  - Never commit Client Secret to version control
  - Store credentials in environment variables or AWS Secrets Manager
  - Use `.env` file for local development (add to `.gitignore`)

- **OAuth Consent Screen**:
  - Apps in "Testing" mode are limited to test users
  - Submit for verification to allow all users (required for production)
  - Verification can take several days to weeks

- **Scopes**:
  - Only request scopes you actually need
  - More scopes = more user consent required
  - Current scopes: `email`, `profile`, `openid`

### Troubleshooting

**Error: "redirect_uri_mismatch"**
- Ensure the redirect URI in Google Console exactly matches your callback URL
- Check for trailing slashes, http vs https, port numbers

**Error: "invalid_client"**
- Verify Client ID and Client Secret are correct
- Check that credentials are properly set in environment variables

**Error: "access_denied"**
- User denied consent
- Check OAuth consent screen configuration
- Ensure test users are added if app is in "Testing" mode

**Error: "OAuth provider google is not configured"**
- Check that `OAUTH_GOOGLE_CLIENT_ID` and `OAUTH_GOOGLE_CLIENT_SECRET` are set
- Restart the FastAPI server after adding environment variables

---

## GitHub OAuth 2.0 Setup

### Step 1: Create a GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"New OAuth App"** (or **"Register a new application"**)
3. Fill in the application details:
   - **Application name**: `SpendSense` (or your preferred name)
   - **Homepage URL**: `https://spendsense.example.com` (or your homepage)
   - **Authorization callback URL**:
     - For development: `http://localhost:8000/api/v1/auth/oauth/github/callback`
     - For production: `https://api.spendsense.example.com/api/v1/auth/oauth/github/callback`
4. Click **"Register application"**

### Step 2: Get Client ID and Secret

1. After creating the app, you'll see:
   - **Client ID**: Copy this value
   - **Client Secret**: Click **"Generate a new client secret"** (keep this secure!)
2. **Copy the credentials**:
   - **Client ID**: e.g., `Iv1.abcdefghijklmnop`
   - **Client Secret**: e.g., `abcdefghijklmnopqrstuvwxyz1234567890`

### Step 3: Configure Environment Variables

Add to your `.env` file:

```bash
# GitHub OAuth Configuration
OAUTH_GITHUB_CLIENT_ID=your-github-client-id
OAUTH_GITHUB_CLIENT_SECRET=your-github-client-secret
```

---

## Facebook Login Setup

### Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"My Apps"** > **"Create App"**
3. Select **"Consumer"** as the app type
4. Fill in the app details:
   - **App name**: `SpendSense` (or your preferred name)
   - **App contact email**: Your email address
5. Click **"Create App"**

### Step 2: Add Facebook Login Product

1. In your app dashboard, click **"Add Product"**
2. Find **"Facebook Login"** and click **"Set Up"**
3. Select **"Web"** as the platform

### Step 3: Configure OAuth Settings

1. Go to **"Facebook Login"** > **"Settings"**
2. Add **Valid OAuth Redirect URIs**:
   - For development: `http://localhost:8000/api/v1/auth/oauth/facebook/callback`
   - For production: `https://api.spendsense.example.com/api/v1/auth/oauth/facebook/callback`
3. Click **"Save Changes"**

### Step 4: Get App ID and App Secret

1. Go to **"Settings"** > **"Basic"**
2. Copy the **App ID** and **App Secret**:
   - **App ID**: e.g., `1234567890123456`
   - **App Secret**: Click **"Show"** to reveal (keep this secure!)

### Step 5: Configure Environment Variables

Add to your `.env` file:

```bash
# Facebook OAuth Configuration
OAUTH_FACEBOOK_CLIENT_ID=your-facebook-app-id
OAUTH_FACEBOOK_CLIENT_SECRET=your-facebook-app-secret
```

**Note**: Facebook apps start in "Development" mode. Add test users or submit for review to allow all users.

---

## Apple Sign In Setup

### Step 1: Create an App ID in Apple Developer Portal

1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Navigate to **"Certificates, Identifiers & Profiles"**
3. Click **"Identifiers"** > **"+"** to create a new identifier
4. Select **"App IDs"** > **"Continue"**
5. Select **"App"** > **"Continue"**
6. Fill in:
   - **Description**: `SpendSense`
   - **Bundle ID**: `com.spendsense.app` (or your bundle ID)
7. Enable **"Sign In with Apple"** capability
8. Click **"Continue"** > **"Register"**

### Step 2: Create a Service ID

1. In **"Identifiers"**, click **"+"** to create a new identifier
2. Select **"Services IDs"** > **"Continue"**
3. Fill in:
   - **Description**: `SpendSense Web Service`
   - **Identifier**: `com.spendsense.service` (must be unique)
4. Enable **"Sign In with Apple"** > **"Configure"**
5. Configure:
   - **Primary App ID**: Select your App ID from Step 1
   - **Website URLs**:
     - **Domains and Subdomains**: `api.spendsense.example.com`
     - **Return URLs**:
       - For development: `http://localhost:8000/api/v1/auth/oauth/apple/callback`
       - For production: `https://api.spendsense.example.com/api/v1/auth/oauth/apple/callback`
6. Click **"Save"** > **"Continue"** > **"Register"**

### Step 3: Create a Key for Sign In with Apple

1. Go to **"Keys"** > **"+"** to create a new key
2. Fill in:
   - **Key Name**: `SpendSense Sign In with Apple`
   - Enable **"Sign In with Apple"**
3. Click **"Continue"** > **"Register"**
4. **Download the key** (`.p8` file) - you can only download once!
5. Note the **Key ID** (e.g., `ABCD1234EF`)

### Step 4: Get Team ID

1. In the top right of Apple Developer Portal, click your account
2. Note your **Team ID** (e.g., `ABC123DEF4`)

### Step 5: Configure Environment Variables

Add to your `.env` file:

```bash
# Apple Sign In Configuration
OAUTH_APPLE_CLIENT_ID=com.spendsense.service  # Your Service ID
OAUTH_APPLE_KEY_ID=ABCD1234EF  # Your Key ID
OAUTH_APPLE_TEAM_ID=ABC123DEF4  # Your Team ID
OAUTH_APPLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----  # Contents of .p8 file
```

**Important**:
- The `OAUTH_APPLE_PRIVATE_KEY` should contain the entire contents of the `.p8` file
- Include the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines
- Use `\n` for newlines if storing as a single line

**Example**:
```bash
OAUTH_APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...\n-----END PRIVATE KEY-----"
```

---

## Testing OAuth Setup

### Test Google OAuth

1. Start your FastAPI server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Test the authorize endpoint:
   ```bash
   curl "http://localhost:8000/api/v1/auth/oauth/google/authorize?redirect_uri=http://localhost:3000/callback"
   ```

3. You should receive a JSON response with `authorize_url` and `state`.

4. Open the `authorize_url` in a browser to test the OAuth flow.

### Test GitHub OAuth

```bash
curl "http://localhost:8000/api/v1/auth/oauth/github/authorize?redirect_uri=http://localhost:3000/callback"
```

### Test Facebook OAuth

```bash
curl "http://localhost:8000/api/v1/auth/oauth/facebook/authorize?redirect_uri=http://localhost:3000/callback"
```

### Test Apple Sign In

```bash
curl "http://localhost:8000/api/v1/auth/oauth/apple/authorize?redirect_uri=http://localhost:3000/callback"
```

---

## Production Deployment

### AWS Secrets Manager

For production, store OAuth credentials in AWS Secrets Manager:

1. Create a secret in AWS Secrets Manager:
   ```json
   {
     "OAUTH_GOOGLE_CLIENT_ID": "your-client-id",
     "OAUTH_GOOGLE_CLIENT_SECRET": "your-client-secret",
     "OAUTH_GITHUB_CLIENT_ID": "your-client-id",
     "OAUTH_GITHUB_CLIENT_SECRET": "your-client-secret",
     "OAUTH_FACEBOOK_CLIENT_ID": "your-client-id",
     "OAUTH_FACEBOOK_CLIENT_SECRET": "your-client-secret",
     "OAUTH_APPLE_CLIENT_ID": "your-service-id",
     "OAUTH_APPLE_KEY_ID": "your-key-id",
     "OAUTH_APPLE_TEAM_ID": "your-team-id",
     "OAUTH_APPLE_PRIVATE_KEY": "your-private-key"
   }
   ```

2. Update your application to read from Secrets Manager in production.

### Environment Variables

Alternatively, set environment variables in your deployment:
- ECS Task Definition
- Docker Compose
- Kubernetes Secrets
- CI/CD pipeline secrets

---

## Security Best Practices

1. **Never commit credentials to version control**
   - Use `.env` file for local development (add to `.gitignore`)
   - Use AWS Secrets Manager for production

2. **Use different OAuth apps for development and production**
   - Separate Client IDs/Secrets for each environment
   - Different redirect URIs

3. **Rotate credentials regularly**
   - Change Client Secrets periodically
   - Revoke and regenerate if compromised

4. **Limit OAuth scopes**
   - Only request scopes you actually need
   - Review scopes regularly

5. **Monitor OAuth usage**
   - Set up alerts for unusual activity
   - Review OAuth logs regularly

---

## Troubleshooting Common Issues

### "redirect_uri_mismatch" Error
- **Cause**: Redirect URI doesn't match exactly what's configured
- **Solution**: Check callback URLs in provider console match exactly (including protocol, port, path)

### "invalid_client" Error
- **Cause**: Client ID or Secret is incorrect
- **Solution**: Verify credentials are correct and properly set in environment variables

### "access_denied" Error
- **Cause**: User denied consent or app is in testing mode
- **Solution**: Add test users or submit app for verification

### OAuth Provider Not Configured
- **Cause**: Environment variables not set or server not restarted
- **Solution**: Check `.env` file, restart server, verify variable names

---

**Last Updated**: 2025-01-XX
**Version**: 1.0

