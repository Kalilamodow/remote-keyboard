from typing import TypedDict
from socket_hlapi import Server
import pyautogui as gui
import json


class KeyboardData(TypedDict):
    key: str
    modifiers: list[str] | None


def main():
    server = Server("0.0.0.0", 8365)

    def onmessage(data_str: str, _):
        if len(data_str.strip()) <= 1:
            return

        try:
            data: KeyboardData = json.loads(data_str)
        except json.JSONDecodeError:
            print("JSON decode error with data:", data_str)
            return

        if data["modifiers"]:
            gui.hotkey(*data["modifiers"], data["key"])
            return

        gui.press(data["key"])

    server.add_handler(onmessage)

    server.run()


if __name__ == "__main__":
    main()
