# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this project, please report it by creating a private security advisory on GitHub.

## Security Incident - API Key Exposure

**Date:** February 28, 2026  
**Severity:** Critical  
**Status:** Resolved

### Issue
An OpenRouter API key was hardcoded in `todoist_tools.py` (line 22, commit 6d67d28a) and exposed in the public repository.

### Impact
The exposed API key could have been used by unauthorized parties to:
- Make API calls to OpenRouter
- Incur charges on the account
- Access AI services without authorization

### Remediation Steps Taken

1. **Removed hardcoded API key** from source code
2. **Updated code** to load API key from `environments.json` via `auth_manager`
3. **Added `get_openrouter_key()` method** to `AuthManager` class for centralized credential management
4. **Updated `TodoistTools`** to retrieve key from `auth_manager` instead of hardcoding
5. **Created `.env.example`** file documenting the `environments.json` structure
6. **Added `.gitignore`** to prevent future credential file commits
7. **Updated README.md** with security setup instructions

### Required Actions

**CRITICAL:** The exposed API key must be rotated immediately:

1. **Revoke the exposed key** at https://openrouter.ai/keys
2. **Generate a new API key**
3. **Add the new key** to your `environments.json` file:
   ```json
   {
     "environments": {
       "openrouter": {
         "credentials": {
           "apiKey": "your_new_api_key_here"
         }
       }
     }
   }
   ```
4. **Never commit** the `environments.json` file to version control

### Prevention

To prevent similar incidents:
- ✅ All secrets now loaded from `environments.json` via centralized `AuthManager`
- ✅ `.gitignore` configured to exclude `environments.json` and `config.json`
- ✅ `.env.example` provides template documenting required configuration
- ✅ README includes security setup instructions
- ✅ Credentials managed through single source of truth (`auth_manager`)

### Best Practices

1. **Never hardcode secrets** in source code
2. **Use centralized credential management** (like `AuthManager`) for all API keys and tokens
3. **Store credentials in `environments.json`** which is excluded from version control
4. **Keep credential files local** and never commit them
5. **Rotate keys immediately** if exposed
6. **Use `.env.example`** to document required configuration structure
