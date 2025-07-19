import asyncio
import json
from pathlib import Path
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakCharacteristicNotFoundError
from cleaner import clean_ds_store, poo

def load_config():
    config_path = Path(__file__).parent / "config.json"
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

async def run_ble_listener():
    config = load_config()
    target_name = config["ble"].get("name")
    char_uuid = config["ble"]["characteristic_uuid"]
    target = None

    while target is None:
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover(timeout=5)

        for d in devices:
            if d.name and target_name and d.name == target_name:
                target = d
                break

        if not target:
            print("No matching BLE device found. Retrying in 10 seconds...")
            await asyncio.sleep(10)

    print(f"Connecting to: {target.name} ({target.address})")

    try:
        async with BleakClient(target) as client:
            print("Connected.")
            services = client.services
            if services is None:
                print("No services found on the device.")
                return

            async def notification_handler(_, data):
                message = data.decode(errors="ignore").strip()
                print(f"Received BLE message: {message}")
                if message == "clean":
                    clean_ds_store()
                if message == "poo":
                    poo()

            try:
                await client.start_notify(char_uuid, notification_handler)
            except BleakCharacteristicNotFoundError:
                print(f"ERROR: Characteristic {char_uuid} not found on the device.")
                print("Please verify that the UUID matches what your ESP32 firmware is advertising.")
                return

            print("Listening for BLE notifications. Press Ctrl+C to stop.")
            while True:
                await asyncio.sleep(1)

    except Exception as e:
        print(f"Failed to connect to BLE device: {e}")