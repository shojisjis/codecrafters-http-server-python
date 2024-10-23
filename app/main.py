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
        
        if method == 'GET':
            if target == '/':
                response = b"HTTP/1.1 200 OK\r\n\r\n"
            elif target.startswith('/echo/'):
                echo_string = target[6:]  # '/echo/' 이후의 문자열 추출
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}"
                response = response.encode()
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        
        conn.sendall(response)
        conn.close()


if __name__ == "__main__":
    main()
