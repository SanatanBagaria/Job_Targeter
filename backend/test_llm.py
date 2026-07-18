import os
from dotenv import load_dotenv
import litellm

load_dotenv()
model_name = os.getenv("LLM_MODEL", "gemini/gemini-flash-latest")
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing model: {model_name}")
print(f"API Key start: {api_key[:10] if api_key else 'None'}")

try:
    response = litellm.completion(
        model=model_name,
        messages=[{"role": "user", "content": "Hello, write a 3-word response."}],
        api_key=api_key
    )
    print("Response received successfully!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error calling LLM: {str(e)}")
