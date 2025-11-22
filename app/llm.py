import os, httpx, json

LLM_PROVIDER_URL = os.getenv('LLM_PROVIDER_URL', 'https://api.openai.com/v1/chat/completions')
LLM_API_KEY = os.getenv('LLM_API_KEY', '')

async def query_llm(messages, max_tokens=512, temperature=0.0):
    headers = {'Authorization': f'Bearer {LLM_API_KEY}', 'Content-Type': 'application/json'}
    payload = {'model':'gpt-4o-mini','messages':messages,'max_tokens':max_tokens,'temperature':temperature}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(LLM_PROVIDER_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        if 'choices' in data and len(data['choices'])>0:
            return data['choices'][0].get('message', {}).get('content') or data['choices'][0].get('text')
        return json.dumps(data)
