from datetime import datetime
from json import dumps

import keyboard as kb

from server import KeyboardData
from socket_hlapi import Client


def time():
    currentTime = datetime.now()
    minute = currentTime.minute
    second = currentTime.second

    return f"{minute:02}:{second:02}"


def translate_name(n: str | None = None) -> str | None:
    if n is None:
        return None

    if len(n) == 1:
        return n

    others = {
        "tab": "    ",
        "enter": "\n",
        "space": " ",
        "backspace": "\b",
    }

    if n in others:
        return others[n]

    return None


ctrl_key = False


def main():
    client = Client("10.0.0.235", 8365)
    paused = False

    def send(evt: kb.KeyboardEvent):
        if paused:
            return

        global ctrl_key

        if evt.event_type == kb.KEY_DOWN:
            if evt.name == "ctrl":
                ctrl_key = True
                return

            if (name := translate_name(evt.name)) is not None:
                if ctrl_key:
                    modifiers = ["ctrl"]
                else:
                    modifiers = []

                data: KeyboardData = {
                    "key": name,
                    "modifiers": modifiers,
                }

                client.send(dumps(data))

        elif evt.event_type == kb.KEY_UP:
            if evt.name == "ctrl":
                ctrl_key = False

    kb.hook(send)
    print("ready!\n")

    try:
        while True:
            if kb.is_pressed("esc"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        kb.unhook_all()

    client.stop()


if __name__ == "__main__":
    main()
