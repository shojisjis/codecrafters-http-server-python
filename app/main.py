import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn, addr = server_socket.accept()  # 클라이언트 대기
        
        request = conn.recv(1024).decode('utf-8')
        print(request)
        
        # HTTP 요청 파싱
        request_line = request.split('\n')[0]
        method, target, _ = request_line.split(' ')
        
        if method == 'GET' and target == '/':
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        
        conn.sendall(response)
        conn.close()


if __name__ == "__main__":
    main()
