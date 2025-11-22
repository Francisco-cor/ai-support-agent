import asyncio
from app.db import init_db, index_document

SAMPLE_DOCS = [
    ('Onboarding Flow','When a user signs up, create a profile, send welcome email, and assign to onboarding stage.'),
    ('Refund Policy','Refunds are processed within 7 business days after approval. Refunds require order id and reason.'),
    ('API Rate Limits','Clients are allowed 1000 requests per day. 429 returned when limit exceeded.'),
]

async def main():
    await init_db()
    for t,c in SAMPLE_DOCS:
        await index_document(t,c)
    print('seeded docs')

if __name__ == "__main__":
    asyncio.run(main())
