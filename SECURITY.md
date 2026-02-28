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
2. **Updated code** to load API key from environment variable (`OPENROUTER_API_KEY`)
3. **Created `.env.example`** file with placeholder values
4. **Added `.gitignore`** to prevent future `.env` file commits
5. **Updated README.md** with security setup instructions

### Required Actions

**CRITICAL:** The exposed API key must be rotated immediately:

1. **Revoke the exposed key** at https://openrouter.ai/keys
2. **Generate a new API key**
3. **Add the new key** to your `.env` file:
   ```
   OPENROUTER_API_KEY=your_new_api_key_here
   ```
4. **Never commit** the `.env` file to version control

### Prevention

To prevent similar incidents:
- ✅ All secrets now use environment variables
- ✅ `.gitignore` configured to exclude `.env` files
- ✅ `.env.example` provides template without secrets
- ✅ README includes security setup instructions

### Best Practices

1. **Never hardcode secrets** in source code
2. **Use environment variables** for all API keys and tokens
3. **Keep `.env` files local** and never commit them
4. **Rotate keys immediately** if exposed
5. **Use `.env.example`** to document required variables
