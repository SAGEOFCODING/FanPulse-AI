import asyncio
from google import genai

async def main():
    client = genai.Client(api_key='fake')
    try:
        response = await client.aio.models.generate_content_stream(model='gemini-3.5-flash', contents='hello')
        print(type(response))
        async for chunk in response:
            print(chunk.text)
    except Exception as e:
        print("EXCEPTION:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
