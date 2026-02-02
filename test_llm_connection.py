import os
import types

# Reusing the logic from generate_user_data.py
USE_API = os.getenv("USE_API", "false").lower() == "true"
BACKEND = os.getenv("LLM_BACKEND", "openai").lower()  # azure | openai | dummy

class _DummyChoice:
    def __init__(self, content: str):
        self.message = types.SimpleNamespace(content=content)

class _DummyChatCompletions:
    def create(self, model=None, messages=None, **kwargs):
        return types.SimpleNamespace(choices=[_DummyChoice("Success! (Dummy Response)")])

class DummyLLM:
    def __init__(self):
        self.chat = types.SimpleNamespace(completions=_DummyChatCompletions())

def get_llm_client():
    if USE_API:
        print(f"--- Attempting to connect to {BACKEND.upper()} API ---")
        if BACKEND == "azure":
            from openai import AzureOpenAI
            return AzureOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
            )
        elif BACKEND == "openai":
            from openai import OpenAI
            print(os.environ["OPENAI_API_KEY"],os.getenv("OPENAI_API_BASE") )
            return OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.getenv("OPENAI_API_BASE"))
    
    print("--- Using DUMMY offline client (Set USE_API=true for real APIs) ---")
    return DummyLLM()

DEPLOYMENT = (
    os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o") if BACKEND == "azure"
    else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
)

def test_connectivity():
    client = get_llm_client()
    print(f"Model/Deployment: {DEPLOYMENT}")
    
    try:
        print("Sending test prompt...")
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a connectivity test bot."},
                {"role": "user", "content": "Hello! If you can read this, respond with exactly: 'LLM Connection Verified.'"}
            ],
            stream=False,
            extra_body={"enable_thinking": False},
            temperature=0.0,
            max_tokens=50
        )
        
        result = response.choices[0].message.content.strip()
        print("\n" + "="*30)
        print(f"RESPONSE: {result}")
        print("="*30 + "\n")
        
        if "Verified" in result or "Success" in result:
            print("✅ TEST PASSED: The LLM client is working correctly.")
        else:
            print("⚠️ TEST COMPLETED: Received a response, but it didn't match the expected format.")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\nMake sure your environment variables (API Key, Endpoint, etc.) are set correctly.")

if __name__ == "__main__":
    test_connectivity()
