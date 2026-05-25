import asyncio
import httpx
import os

GEMINI_API_KEY = "AIzaSyBmc1FMheNshRy0ZNfzuuneutUHXL3s988"
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
GEMINI_GEN_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

async def test_embed():
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [{"text": "Hello world"}]
        },
        "output_dimensionality": 768
    }
    async with httpx.AsyncClient() as client:
        try:
            print("Testing Embedding API...")
            response = await client.post(GEMINI_EMBED_URL, headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

async def test_gen():
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [{"text": "Say hello in one word."}]
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        try:
            print("\nTesting Generation API...")
            response = await client.post(GEMINI_GEN_URL, headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    await test_embed()
    await test_gen()

if __name__ == "__main__":
    asyncio.run(main())
