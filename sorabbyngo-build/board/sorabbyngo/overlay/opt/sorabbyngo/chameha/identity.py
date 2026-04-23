"""
identity.py — Chameha OS identity layer
Reads NodeID from kernel driver at /proc/sorabbyngo/nodeid
Seals every Chameha session to this specific device
"""

NODE_ID_PATH = "/proc/sorabbyngo/nodeid"

class DeviceIdentity:
    def __init__(self):
        self.node_id = self._read_node_id()
        self.sealed = self.node_id is not None

    def _read_node_id(self):
        try:
            with open(NODE_ID_PATH, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
        except PermissionError:
            return None

    def short_id(self):
        """First 12 chars of NodeID for display"""
        if self.node_id:
            return self.node_id[:12]
        return "unknown"

    def assert_sealed(self):
        """Call at boot — fails loud if NodeID is missing"""
        if not self.sealed:
            raise RuntimeError(
                "FATAL: NodeID not found at /proc/sorabbyngo/nodeid\n"
                "Chameha cannot run without a sealed device identity.\n"
                "Ensure the sorabbyngo kernel module is loaded."
            )

    def __repr__(self):
        return f"DeviceIdentity(node_id={self.short_id()}..., sealed={self.sealed})"
