import asyncio
import os
import sys

# Fix: Add the parent directory to sys.path to allow importing 'app.db'
# This is necessary because the script is inside the 'scripts/' folder.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.db import init_db, index_document

# SCENARIO A: Internal Technical Support (Developer Platform)
# Context: Support agents use this to answer repetitive questions from external developers.

SAMPLE_DOCS = [
    (
        'Authentication Guide (OAuth 2.0)',
        'To access the API, you must authenticate using OAuth 2.0 Client Credentials flow.\n'
        '1. Get your Client ID and Client Secret from the Developer Dashboard.\n'
        '2. Send a POST request to https://api.example.com/oauth/token with body: grant_type="client_credentials".\n'
        '3. The response will contain an "access_token".\n'
        '4. Include this token in the "Authorization" header of all API requests: "Authorization: Bearer <access_token>".\n'
        'Tokens expire after 1 hour.'
    ),
    (
        'API Rate Limits & Quotas',
        'Our API enforces rate limits to ensure stability.\n'
        '- Standard Plan: 1,000 requests per minute per IP.\n'
        '- Enterprise Plan: 10,000 requests per minute.\n'
        '\n'
        'If you exceed the limit, you will receive a 429 Too Many Requests status code.\n'
        'The response headers include "Retry-After", indicating the number of seconds to wait before retrying.'
    ),
    (
        'Handling 500 Internal Server Errors',
        'A 500 Internal Server Error usually indicates a timeout in the legacy inventory subsystem (LegacySystem-X).\n'
        'Troubleshooting Steps:\n'
        '1. Do NOT retry the request immediately (this exacerbates the load).\n'
        '2. Implement an exponential backoff strategy starting at 5 seconds.\n'
        '3. If the error persists for more than 10 minutes, check the status page at status.example.com.\n'
        '4. For critical production blockers, escalate to the SRE team via PagerDuty.'
    ),
    (
        'Webhook Security (Signature Verification)',
        'We send webhooks for events like "order.created" and "payment.succeeded".\n'
        'Security: All webhooks include an "X-Webhook-Signature" header.\n'
        'You must verify this signature using HMAC-SHA256 with your Webhook Signing Secret.\n'
        'If the signature does not match, you should reject the request with a 401 Unauthorized status to prevent replay attacks.'
    ),
    (
        'Error Codes Reference',
        '- 400 Bad Request: Validation failed. Check your JSON body.\n'
        '- 401 Unauthorized: Invalid or missing API Key/Token.\n'
        '- 403 Forbidden: Token valid, but permission denied for this resource.\n'
        '- 404 Not Found: The resource ID does not exist.\n'
        '- 429 Too Many Requests: Rate limit exceeded.'
    )
]

async def main():
    print("--> Initializing Database...")
    await init_db()
    
    print(f"--> Indexing {len(SAMPLE_DOCS)} documents...")
    for title, content in SAMPLE_DOCS:
        # Insert into DB and FTS index
        rowid = await index_document(title, content)
        print(f"    [OK] Indexed ID {rowid}: '{title}'")
    
    print("\nSeed complete! You can now ask questions like:")
    print("  - 'What is the rate limit?'")
    print("  - 'How do I verify webhooks?'")
    print("  - 'What should I do if I get a 500 error?'")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")