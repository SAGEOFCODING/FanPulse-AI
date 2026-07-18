import asyncio
from google import genai
from google.genai import types

async def main():
    client = genai.Client(api_key='fake')
    try:
        config = types.GenerateContentConfig(
            system_instruction="Hello world"
        )
        response = await client.aio.models.generate_content_stream(model='gemini-3.1-flash', contents='hello', config=config)
        async for chunk in response:
            print(chunk.text)
    except Exception as e:
        print("EXCEPTION:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
