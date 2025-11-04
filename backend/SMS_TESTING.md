# SMS Testing Guide - AWS SNS Sandbox

This guide explains how to test SMS functionality locally using AWS SNS sandbox mode.

## Prerequisites

1. **AWS Account** with access to SNS
2. **AWS Credentials** configured locally
3. **Redis** running locally (for code storage)
4. **PostgreSQL** database set up
5. **Backend server** running

## Step 1: Set Up AWS SNS Sandbox

### 1.1 Enable SMS in Your AWS Account

**IMPORTANT:** If you get the error "No origination entities available to send", you need to enable SMS capabilities first.

1. Go to [AWS SNS Console](https://console.aws.amazon.com/sns/v3/home)
2. Select your region (e.g., `us-west-1`)
3. Navigate to **Text messaging (SMS)** in the left sidebar
4. Click on **"Text messaging preferences"** or **"Account preferences"**
5. Look for **"SMS sandbox"** or **"SMS preferences"** section
6. Enable SMS functionality for your account

**Alternative: Enable via AWS CLI**
```bash
aws sns set-sms-attributes --attributes DefaultSMSType=Transactional --region us-west-1
```

**Note:** Some AWS accounts may require you to request SMS activation first. If SMS is not available, you may need to:
- Contact AWS Support to enable SMS for your account
- Use a different AWS account that has SMS enabled
- For development, consider using a mock SMS service (see Alternative Solutions below)

### 1.2 Access AWS SNS Console

1. Go to [AWS SNS Console](https://console.aws.amazon.com/sns/v3/home)
2. Select your region (e.g., `us-west-1`)
3. Navigate to **Text messaging (SMS)** in the left sidebar

### 1.3 Verify Phone Numbers

AWS SNS Sandbox mode requires you to verify phone numbers before you can send SMS to them.

1. Click on **"Sandbox"** tab (if not already selected)
2. Click **"Add phone number"** or **"Add destination"**
3. Enter your phone number in E.164 format (e.g., `+1234567890`)
4. Select **"Verify new phone number"**
5. AWS will send a verification code to your phone
6. Enter the verification code to complete verification

**Note:** You can verify up to 10 phone numbers in sandbox mode.

**Troubleshooting:** If you get "No origination entities available to send":
- Check if SMS is enabled in your account (see Step 1.1)
- Try using a different AWS region (e.g., `us-east-1`)
- Some AWS accounts may need SMS activation request approval first

### 1.3 Verify Phone Number Format

The phone number must be in **E.164 format**:
- US: `+1XXXXXXXXXX` (e.g., `+14155551234`)
- UK: `+44XXXXXXXXXX` (e.g., `+447911123456`)
- Include country code with `+` prefix
- No spaces, dashes, or parentheses

## Step 2: Configure Local Environment

### 2.1 Set Up Environment Variables

Edit your `.env` file in the `backend/` directory:

```bash
# AWS Configuration
AWS_REGION=us-west-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# SMS Configuration (AWS SNS)
SNS_REGION=us-west-1

# Redis Configuration (required for code storage)
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=postgresql://spendsense_user:spendsense_password@localhost:5432/spendsense_db
```

### 2.2 Verify AWS Credentials

Test your AWS credentials:

```bash
aws sns publish --phone-number "+1234567890" --message "Test" --region us-west-1
```

If you get an error about unverified numbers, that's expected in sandbox mode - just verify your number first in the console.

### 2.3 Start Required Services

**Start Redis:**
```bash
# macOS (Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:7.1
```

**Start PostgreSQL:**
```bash
# macOS (Homebrew)
brew services start postgresql@15

# Linux
sudo systemctl start postgresql
```

**Start Backend Server:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 3: Test SMS Endpoints

### 3.1 Request Verification Code

Send a POST request to request an SMS verification code:

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/phone/request" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/auth/phone/request`
3. Click "Try it out"
4. Enter your verified phone number: `{"phone": "+1234567890"}`
5. Click "Execute"

**Expected Response:**
```json
{
  "message": "Verification code sent successfully",
  "phone": "+1234567890"
}
```

**What Happens:**
- Phone number is validated and normalized to E.164 format
- Rate limiting is checked (5 SMS/hour, 10 SMS/day)
- 6-digit verification code is generated
- Code is stored in Redis with 10-minute expiration
- SMS is sent via AWS SNS to your verified phone number

### 3.2 Verify Code and Register/Login

Send a POST request to verify the code:

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/phone/verify" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "code": "123456"}'
```

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/auth/phone/verify`
3. Click "Try it out"
4. Enter phone number and the code you received via SMS:
   ```json
   {
     "phone": "+1234567890",
     "code": "123456"
   }
   ```
5. Click "Execute"

**Expected Response (New User):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+1234567890",
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "is_new_user": true
}
```

**Expected Response (Existing User):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+1234567890",
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "is_new_user": false
}
```

## Step 4: Testing Scenarios

### 4.1 Test Rate Limiting

Try sending more than 5 SMS requests in an hour:

1. Send 5 requests to `/api/v1/auth/phone/request`
2. On the 6th request, you should get an error:
   ```json
   {
     "detail": "Too many SMS requests. Please try again in an hour."
   }
   ```

### 4.2 Test Code Expiration

1. Request a verification code
2. Wait 10 minutes (code expiration time)
3. Try to verify with any code
4. You should get an error:
   ```json
   {
     "detail": "Invalid or expired verification code"
   }
   ```

### 4.3 Test Max Attempts

1. Request a verification code
2. Try to verify with wrong code 3 times
3. On the 4th attempt, you should get an error:
   ```json
   {
     "detail": "Maximum verification attempts exceeded. Please request a new code."
   }
   ```

### 4.4 Test Invalid Phone Number

Send a request with an invalid phone number:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/phone/request" \
  -H "Content-Type: application/json" \
  -d '{"phone": "invalid"}'
```

Expected error:
```json
{
  "detail": "Invalid phone number format: ..."
}
```

### 4.5 Test Unverified Phone Number

Try to send SMS to a phone number that's not verified in AWS SNS sandbox:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/phone/request" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1987654321"}'
```

Expected error:
```json
{
  "detail": "AWS SNS error (OptedOut): ..."
}
```

**Solution:** Verify the phone number in AWS SNS Console first.

## Step 5: Troubleshooting

### Issue: "No origination entities available to send"

**This is a common error that occurs when SMS is not enabled for your AWS account.**

**Solutions:**

1. **Enable SMS in Account Preferences:**
   - Go to AWS SNS Console → Text messaging (SMS) → Text messaging preferences
   - Enable SMS functionality
   - Set default SMS type to "Transactional" or "Promotional"

2. **Enable via AWS CLI:**
   ```bash
   # Enable SMS with default type
   aws sns set-sms-attributes --attributes DefaultSMSType=Transactional --region us-west-1
   
   # Check current SMS attributes
   aws sns get-sms-attributes --region us-west-1
   ```

3. **Request SMS Activation:**
   - Some AWS accounts require explicit activation
   - Go to AWS Support Center
   - Create a support case to enable SMS
   - Or contact AWS Support to enable SMS for your account

4. **Try Different Region:**
   - Some regions may have SMS enabled by default
   - Try `us-east-1` instead of `us-west-1`
   - Update your `.env` file: `SNS_REGION=us-east-1`

5. **Alternative: Use Mock SMS Service (Development Only):**
   - See "Alternative Solutions" section below for development workarounds

### Issue: "AWS credentials not found"

**Solution:** Make sure your `.env` file has:
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
```

Or use AWS CLI:
```bash
aws configure
```

### Issue: "Redis connection failed"

**Solution:** Make sure Redis is running:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it:
brew services start redis  # macOS
# or
sudo systemctl start redis  # Linux
```

### Issue: "Phone number not verified"

**Solution:** 
1. Go to AWS SNS Console
2. Navigate to Text messaging (SMS) → Sandbox
3. Verify your phone number

**Note:** You must first resolve the "No origination entities" error before you can verify phone numbers.

### Issue: "Invalid phone number format"

**Solution:** Use E.164 format:
- ❌ `(415) 555-1234`
- ❌ `415-555-1234`
- ❌ `4155551234`
- ✅ `+14155551234`

### Issue: "Rate limit exceeded"

**Solution:** Wait for the rate limit window to reset:
- Hourly limit: 5 SMS per phone per hour
- Daily limit: 10 SMS per phone per day

You can check Redis keys to see current rate limits:
```bash
redis-cli
> KEYS *sms_rate_limit*
> GET sms_rate_limit_hour:+1234567890
```

## Step 6: Production Access

To send SMS to any phone number (not just verified ones), you need to request production access:

1. Go to AWS SNS Console
2. Navigate to **Text messaging (SMS)** → **Text messaging preferences**
3. Click **"Request production access"**
4. Fill out the form:
   - Use case description
   - Monthly message volume
   - Message content examples
   - Opt-out mechanism
5. Submit and wait for approval (usually 24-48 hours)

**Note:** Sandbox mode is perfect for development and testing. Production access is only needed when deploying to production.

## Alternative Solutions (Development Only)

If you're unable to enable SMS in your AWS account, here are alternative approaches for development:

### Option 1: Mock SMS Service (Recommended for Local Development)

Create a mock SMS service that logs codes instead of sending them:

1. Create a development flag in your `.env`:
   ```bash
   SMS_MOCK_MODE=true  # Set to true to use mock SMS
   ```

2. Modify `sms_service.py` to check this flag:
   ```python
   # In send_sms function, add:
   if settings.sms_mock_mode:
       print(f"[MOCK SMS] To: {phone}, Message: {message}")
       return True, None
   ```

3. Check console output for verification codes instead of receiving SMS

### Option 2: Use Twilio (Alternative SMS Provider)

If AWS SNS is not available, you can integrate Twilio as an alternative:

1. Sign up for Twilio (free trial available)
2. Get a phone number and API credentials
3. Modify `sms_service.py` to support Twilio as an alternative provider

### Option 3: Use AWS SES Email (Alternative)

For development, you could use email instead of SMS:

1. Use AWS SES to send verification codes via email
2. Modify the verification flow to use email addresses
3. This requires email verification instead of phone verification

### Option 4: Request AWS Support

If you need SMS functionality:

1. Contact AWS Support
2. Request SMS activation for your account
3. Explain your use case (development/testing)
4. They may enable it for your account

**For now, the mock SMS service (Option 1) is the quickest solution for development.**

## Testing Checklist

- [ ] AWS credentials configured
- [ ] Phone number verified in AWS SNS sandbox
- [ ] Redis running locally
- [ ] PostgreSQL database running
- [ ] Backend server running
- [ ] Successfully requested verification code
- [ ] Received SMS with verification code
- [ ] Successfully verified code and got tokens
- [ ] Tested rate limiting (optional)
- [ ] Tested code expiration (optional)
- [ ] Tested max attempts (optional)

## Example Test Flow

```bash
# 1. Start services
redis-server &
# (in another terminal)
uvicorn app.main:app --reload

# 2. Request verification code
curl -X POST "http://localhost:8000/api/v1/auth/phone/request" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+14155551234"}'

# 3. Check your phone for the SMS code (e.g., "123456")

# 4. Verify the code
curl -X POST "http://localhost:8000/api/v1/auth/phone/verify" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+14155551234", "code": "123456"}'

# 5. Use the access_token for authenticated requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Additional Resources

- [AWS SNS SMS Documentation](https://docs.aws.amazon.com/sns/latest/dg/sms_publish-to-phone.html)
- [AWS SNS Sandbox Mode](https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html)
- [E.164 Phone Number Format](https://en.wikipedia.org/wiki/E.164)

