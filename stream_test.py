import asyncio
import time

from core.voice import kokoro


async def main():
    t = time.time()

    stream = kokoro.create_stream(
        "Good evening sir. Systems are online and ready.",
        voice="am_onyx",
        speed=1.0,
        lang="en-us",
    )

    async for chunk in stream:
        print("FIRST CHUNK:", round(time.time() - t, 3), "s")
        print("CHUNK TYPE:", type(chunk))
        print("CHUNK:", len(chunk))
        break


asyncio.run(main())
