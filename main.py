import asyncio
from ble_client import run_ble_listener

if __name__ == "__main__":
    try:
        asyncio.run(run_ble_listener())
    except KeyboardInterrupt:
        print("Program terminated.")