"""
-- FTP Program --
Transfer files from one computer to another!

This file is designed to send a file to a receiver.

WARNING: this program has several security vulernabilities. Do not use it for anything serious:
- The file size that is said may not reflect the actual file size of the data being sent if the FTP sender file has malicious modifications.
- Excessive file sizes may slow down computers with low memory
- The file may overwrite another file on the receiver's computer with the same filename
- Probably more that I'm unaware of
"""

import socket
import os.path


IP = socket.gethostbyname(socket.gethostname())
PORT = 9850

HEADERSIZE = 10


class Receiver:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def send_bytes(self, message: bytes):
        """
        :return: Whether the message was successfully sent
        """

        message = message
        header_info = f"{len(message):<{HEADERSIZE}}".encode("utf-8")

        try:
            self.client_socket.send(header_info)
            self.client_socket.send(message)
            return True

        except (ConnectionResetError, ConnectionAbortedError):
            return False

    def send(self, message: str) -> bool:
        return self.send_bytes(message.encode("utf-8"))

    def receive(self) -> str | None:
        """
        :return: The data received, or None if the message could not be received.
        """

        try:
            header = self.client_socket.recv(HEADERSIZE)

            if header == b"":
                print("Client disconnected.")
                return None

            message_length = int(header.decode('utf-8').strip())
            return self.client_socket.recv(message_length).decode("utf-8")

        except (ConnectionResetError, ConnectionAbortedError):
            print("Connection reset or connection aborted error: socket disconnected")
            return None


def setup_server_socket() -> socket.socket:
    server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((IP, PORT))
    print(f"Bound to {IP}:{PORT}")
    server_socket.listen(1)

    return server_socket


def select_file():
    while True:
        file = input("Select a file to send: ")

        if os.path.isfile(file):
            return file

        print("Invalid filepath!")


def main():
    file_to_send = select_file()
    file_size = os.path.getsize(file_to_send)

    server_socket: socket.socket = setup_server_socket()

    while True:
        client_socket, addr = server_socket.accept()
        receiver = Receiver(client_socket)

        print(f"\nAccepted socket connection with IP address {addr[0]}")
        send_file = input("Do you want to send the file to this IP? (y/n): ")

        if send_file == "y":
            receiver.send("accept")
            break

        receiver.send("reject")
        print("\nContinuing to search for connections...")

    if not receiver.send(os.path.basename(file_to_send)):
        print("\nClient unexpectedly disconnected. Exiting program.")
        return

    if not receiver.send(str(file_size)):
        print("\nClient unexpectedly disconnected. Exiting program.")
        return

    print("\nWaiting for receiver's approval...")

    accept = receiver.receive()

    receiver_accepted_file_transfer = accept == "y"
    if not receiver_accepted_file_transfer:
        print("Receiver did not accept the file transfer. Exiting program.")
        client_socket.close()
        return

    print("Receiver accepted the file transfer.")
    print("\nSending...")
    with open(file_to_send, "rb") as f:
        receiver.send_bytes(f.read())
    print("File sent!")


if __name__ == "__main__":
    main()
