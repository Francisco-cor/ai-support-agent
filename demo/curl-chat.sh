#!/bin/bash
# Test the Chat Endpoint
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the rate limit?"}'