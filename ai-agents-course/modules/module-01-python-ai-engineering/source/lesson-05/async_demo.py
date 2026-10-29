# async_demo.py: wait for many slow things at the same time
import asyncio
import time


async def call_model(task: str, seconds: float) -> str:
    await asyncio.sleep(seconds)            # stands in for waiting on a network reply
    return f"{task} done"


async def one_by_one() -> None:
    for task in ["summary", "keywords", "title"]:
        print(await call_model(task, 1.0))


async def all_at_once() -> None:
    results = await asyncio.gather(
        call_model("summary", 1.0), call_model("keywords", 1.0), call_model("title", 1.0)
    )
    print(results)


for label, job in [("sequential", one_by_one), ("concurrent", all_at_once)]:
    start = time.perf_counter()
    asyncio.run(job())
    print(f"{label}: {time.perf_counter() - start:.1f} seconds")
