"""
config.py — Chameha user profile and boot state
Profile is NodeID-bound — each device has its own identity
"""

import json
import os
from identity import DeviceIdentity

CONFIG_DIR = "/opt/sorabbyngo/chameha"
CONFIG_FILE = os.path.join(CONFIG_DIR, "user.json")

class UserConfig:
    def __init__(self, identity: DeviceIdentity):
        self.identity = identity
        self.data = self._load()

    def _load(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                # Verify config belongs to this device
                if data.get("node_id") != self.identity.node_id:
                    return self._default()
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return self._default()

    def _default(self):
        return {
            "node_id": self.identity.node_id,
            "name": None,
            "boots": 0,
            "first_boot_complete": False,
            "locale": "en",
            "region": "KE"
        }

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def is_first_boot(self):
        return not self.data.get("first_boot_complete", False)

    def complete_first_boot(self, name: str):
        self.data["name"] = name
        self.data["first_boot_complete"] = True
        self.data["boots"] = 1
        self.save()

    def increment_boot(self):
        self.data["boots"] = self.data.get("boots", 0) + 1
        self.save()

    @property
    def name(self):
        return self.data.get("name") or "friend"

    @property
    def boots(self):
        return self.data.get("boots", 0)

    @property
    def region(self):
        return self.data.get("region", "KE")
