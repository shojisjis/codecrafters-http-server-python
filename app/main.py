import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept()  # wait for client
    conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    conn.close()


if __name__ == "__main__":
    main()
