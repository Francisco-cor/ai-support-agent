import os
from google import genai
from google.genai import types

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = os.getenv('LLM_MODEL', 'gemini-1.5-flash')

# Initialize Client
# We check for the key to avoid crashing immediately if it's missing,
# allowing the app to start but failing gracefully during chat.
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini Client: {e}")

async def query_llm(system_instruction, user_query, context_text):
    """
    Queries the Google Gemini API using the google-genai SDK.
    
    Args:
        system_instruction (str): The persona and strict rules for the AI.
        user_query (str): The specific question asked by the user.
        context_text (str): The retrieved documents to use as reference.
        
    Returns:
        str: The AI's response or an error message.
    """
    if not client:
        return "Configuration Error: GEMINI_API_KEY is missing or invalid in .env file."

    # Construct the full prompt structure
    # We explicitly separate context from instructions to prevent prompt injection
    # and ensure the model focuses on the provided data.
    full_prompt = f"""
    CONTEXT INFORMATION:
    {context_text}
    
    USER QUESTION:
    {user_query}
    
    INSTRUCTIONS:
    - Answer the question using ONLY the context provided above.
    - If the answer is not in the context, say you don't know.
    - Keep the tone professional and concise.
    """

    try:
        # Call Gemini API
        # We use the synchronous generate_content here. 
        # In a high-load production env, this should be run in a threadpool 
        # or using the SDK's async methods if available/stable.
        response = client.models.generate_content(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1, # Low temperature = more deterministic/factual
                max_output_tokens=1024
            ),
            contents=[full_prompt]
        )
        
        # Extract text safely
        if response.text:
            return response.text
        else:
            return "The model generated an empty response."

    except Exception as e:
        print(f"LLM API Error: {e}")
        # Return a friendly error to the UI
        return f"I encountered an issue connecting to the AI provider. (Error: {str(e)})"