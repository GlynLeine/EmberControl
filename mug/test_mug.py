from mug import Mug
import asyncio

loop = asyncio.get_event_loop()
new_mug = Mug("F")


async def print_vals():
    while True:
        try:
            await new_mug.getCurrentBattery()
            await new_mug.getCurrentTemp()
            await asyncio.sleep(3)
        except:
            print("Trying again in 10 seconds")
            await asyncio.sleep(10)


async def main():
    task1 = loop.create_task(new_mug.connectToMug())
    task2 = loop.create_task(print_vals())
    await asyncio.gather(task1, task2)


try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.close()
