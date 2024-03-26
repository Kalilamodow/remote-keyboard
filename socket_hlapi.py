"""High-level API for simple servers"""

import socket
import threading
from typing import Callable, Any


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.handlers: list[Callable[[str], None]] = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((host, port))

    def send(self, msg: str):
        if type(msg) is not str:
            raise TypeError("msg must be a string")

        self.socket.send(msg.encode("utf-8"))

    def recv(self):
        while self.running:
            data = None

            try:
                data = self.socket.recv(1024).decode("utf-8")
            except ConnectionAbortedError:
                print("Aborted data recv gracefully")

            if not data or data.isspace():
                continue
            if data == "disconnect":
                self.stop()
                break

            for func in self.handlers:
                func(data)

    def add_handler(self, func: Callable[[str], None]):
        self.handlers.append(func)

    def start(self):
        self.running = True
        self.receiver = threading.Thread(target=self.recv)
        self.receiver.start()

        # while True:
        #     try:
        #         self.send(input('> '))
        #     except:
        #         self.stop()
        #         break

    def stop(self):
        self.running = False
        self.socket.close()
        print("exited")


class Server:
    handlers: list[Callable[[str, socket.socket], None]]

    def __init__(self, host, port) -> None:
        self.clients: list[socket.socket] = []
        self.handlers = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))

        self.socket.listen(5)
        self.socket.settimeout(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def handle_client(self, client: socket.socket):
        while self.running:
            data: bytes | None = None

            try:
                data = client.recv(1024)
            except ConnectionResetError | ConnectionAbortedError:
                self.rmclient(client)
                break

            if data is None:
                self.rmclient(client)
                break

            data_str = data.decode("utf-8")

            if not self.running:
                return

            for func in self.handlers:
                if func.__code__.co_argcount == 0:
                    func()
                elif func.__code__.co_argcount == 1:
                    func(data_str)
                else:
                    func(data_str, client)

    def rmclient(self, client: socket.socket):
        self.clients.remove(client)

    def broadcast(
        self, content, include_sender=True, sender: socket.socket | None = None
    ):
        for client in self.clients:
            if not include_sender and client == sender:
                continue

            client.send(content.encode("utf-8"))

    def handle_connections(self):
        while True:
            try:
                client, addr = self.socket.accept()
                print("connection from", addr)
                self.clients.append(client)
                threading.Thread(target=self.handle_client, args=(client,)).start()
            except socket.timeout:
                # weird workaround
                try:
                    pass
                except:
                    pass

    def add_handler(self, func: Callable[[str, socket.socket], Any]):
        self.handlers.append(func)

    def run(self):
        print("Server is running...")
        self.running = True
        try:
            self.handle_connections()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("\nStopping server")

        self.running = False
        print("Disabled new messages")

        print("Closed connection with ", end="")
        for c in self.clients:
            self.rmclient(c)
            c.send("disconnect".encode("utf-8"))
            print(f"{c.getpeername()}", end=", ")
        print(
            f"""Disconnected {len(self.clients)}
              client{"s" if len(self.clients) != 1 else ""}"""
        )

        self.socket.close()
        print("Socket closed")
        print("\nExited successfully")


class Request:
    _kv: list[tuple[str, str]] = {}

    def __init__(self, req: str | dict) -> None:
        if type(req) is str:
            self._kv = Request.load(req)
        elif type(req) is dict:
            self._kv = [(k, v) for k, v in req.items()]

        print(self._kv)

    def get(self, key):
        return [v for k, v in self._kv if k == key][0]

    def __str__(self) -> str:
        return "\n".join([f"{k}:{v}" for k, v in self._kv])

    @staticmethod
    def load(asstr: str):
        kvp_strings: list[str] = asstr.split("\n")
        kvs: list[tuple[str, str]] = [
            (k, v) for k, v in [kv.split(":") for kv in kvp_strings]
        ]
        return kvs
