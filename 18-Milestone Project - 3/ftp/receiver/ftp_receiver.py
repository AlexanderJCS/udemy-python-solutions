import socket

HEADERSIZE = 10
PORT = 9850


class Sender:
    def __init__(self, client_socket: socket.socket):
        self.client_socket = client_socket

    def send(self, message) -> bool:
        """
        :param message: The message to send
        :return: True if the message was sent successfully, False otherwise
        """

        message = message.encode("utf-8")
        header_info = f"{len(message):<{HEADERSIZE}}".encode("utf-8")

        try:
            self.client_socket.send(header_info)
            self.client_socket.send(message)
            return True

        except ConnectionResetError:
            print("Sender disconnected")
            return False

    def receive(self) -> str | None:
        """
        :return: The message if it was received, otherwise None
        """

        try:
            header = self.client_socket.recv(HEADERSIZE)

            if header == b"":
                print("Sender disconnected")
                return None

            message_length = int(header.decode('utf-8').strip())

            return self.client_socket.recv(message_length).decode("utf-8")

        except (ConnectionResetError, ConnectionAbortedError):
            print("Sender disconnected")
            return None

def setup_client_socket(ip) -> socket.socket:
    client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, PORT))

    return client_socket


def main():
    ip = input("IP: ")

    client_socket: socket.socket = setup_client_socket(ip)

    print("Connected. Waiting for sender's approval...")

    sender = Sender(client_socket)
    filename = sender.receive()
    filesize = sender.receive()

    if filename is None or filesize is None:
        print("The sender disconnected. Exiting program.")
        return

    print(f"The sender wants to send you a file titled {filename}. Its size is {filesize} bytes.")
    accepted = input("Do you want to accept? (y/n): ").lower() == "y"
    sender.send("y" if accepted else "n")

    if not accepted:
        print("You did not accept. Exiting program")
        client_socket.close()
        return

    file_contents = sender.receive()

    if file_contents is None:
        print("Sender unexpectedly disconnected. Exiting program.")
        return

    with open(filename, "w") as f:
        f.write(file_contents)


if __name__ == "__main__":
    main()