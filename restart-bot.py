import asyncio
import subprocess


async def main():
    subp = None
    while True:
        try:
            subp = subprocess.Popen(
                ["python", "bot.py"]
            )  # ,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            await asyncio.sleep(12 * 3600)
            subp.terminate()
            pass
        except KeyboardInterrupt:
            subp.kill()
        except Exception as e:
            print(e)


asyncio.get_event_loop().run_until_complete(main())
