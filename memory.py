from pympler import tracker,summary,muppy
import asyncio

b={"test":[1,2,3]}
def gene(obj):
    for i in obj["test"]:
        yield i
for i in gene(b):
    b["test"].append(i+10)
    print(i)
'''
async def memoryleak(id,delay=10):
    await asyncio.sleep(delay)
    return 1
loop=asyncio.get_event_loop()
async def test():
    uid=0
    memory_tracker = tracker.SummaryTracker()
    while True:
        uid+=1
        asyncio.create_task(memoryleak(uid))
        memory_tracker.print_diff()
        await asyncio.sleep(1)



loop.run_until_complete(test())
'''