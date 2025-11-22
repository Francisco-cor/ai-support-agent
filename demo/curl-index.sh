#!/bin/bash
# Test the Indexing Endpoint (requires secret)
curl -X POST http://localhost:8000/api/docs/index \
  -H 'Content-Type: application/json' \
  -H 'X-WEBHOOK-SECRET: changeme_secret' \
  -d '{"title":"New Feature","content":"This is a test document about the new feature."}'