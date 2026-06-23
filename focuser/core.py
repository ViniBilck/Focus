import json
import os
import threading
import time

import serial


class FocuserController:
    def __init__(self, port, baudrate=115200):
        self.config_file = "focuser_config.json"
        self.config = self._load_config()
        self.min_limit = self.config.get("min_limit", 0)
        self.max_limit = self.config.get("max_limit", 2343)
        self.current_position = self.config.get("last_position", 0)

        self.running = True
        self.ser = serial.Serial(port, baudrate, timeout=1)

        self.listener_thread = threading.Thread(target=self._listen_to_arduino)
        self.listener_thread.daemon = True
        self.listener_thread.start()

        print("Initializing connection to Arduino...")
        time.sleep(2)

        print(f"Syncing hardware to last known position: {self.current_position}")
        self.ser.write(f"SETPOS {self.current_position}\n".encode())
        time.sleep(0.5)

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        else:
            return {"last_position": 0, "min_limit": 0, "max_limit": 2343}

    def _save_state(self):
        self.config["last_position"] = self.current_position
        self.config["min_limit"] = self.min_limit
        self.config["max_limit"] = self.max_limit
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def _listen_to_arduino(self):
        while self.running:
            if self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode("utf-8").strip()
                    if line.startswith("POS:"):
                        self.current_position = int(line.split(":")[1])
                        print(
                            f"\r[Moving] Position: {self.current_position}    ",
                            end="",
                            flush=True,
                        )

                    elif line.startswith("CALL:"):
                        self.current_position = int(line.split(":")[1])
                        print(
                            f"\n[Status] Motor call the stop at {self.current_position}."
                        )

                    elif line.startswith("POSNOW:"):
                        self.current_position = int(line.split(":")[1])
                        print(
                            f"\n[Status] Position now: {self.current_position}. Saving state."
                        )
                        self._save_state()

                except Exception:
                    pass
            time.sleep(0.01)

    def set_limits(self, min_val, max_val):
        self.min_limit = min_val
        self.max_limit = max_val
        self._save_state()
        print(f"\n[Config] Limits updated: Min {self.min_limit}, Max {self.max_limit}")

    def go_to(self, target):
        if target < self.min_limit:
            print(
                f"\n[WARNING] Target {target} is below minimum limit ({self.min_limit}). Clipping to minimum."
            )
            target = self.min_limit
        elif target > self.max_limit:
            print(
                f"\n[WARNING] Target {target} exceeds maximum limit ({self.max_limit}). Clipping to maximum."
            )
            target = self.max_limit

        print(f"\n[Command] GOTO {target}...")
        self.ser.write(f"GOTO {target}\n".encode())

    def stop(self):
        self.ser.write(b"STOP\n")
        time.sleep(0.5)
        self._save_state()

    def close(self):
        self._save_state()
        self.running = False
        self.ser.close()

    def status(self):
        print(f"\n[Status] Position now: {self.current_position}.")
        print(f"\n[Status] Max limit: {self.max_limit}. Min limit: {self.min_limit}.")
