import socket  # noqa: F401
import threading
import os
import argparse
import gzip
import io


def handle_client(conn, addr, directory):
    request = conn.recv(1024).decode('utf-8')
    print(f"연결된 클라이언트: {addr}")
    print(request)
    
    # HTTP 요청 파싱
    headers, body = request.split('\r\n\r\n', 1)
    headers = headers.split('\r\n')
    request_line = headers[0]
    method, target, _ = request_line.split(' ')
    
    # 헤더 파싱
    user_agent = ''
    content_length = 0
    accepts_gzip = False
    
    for header in headers:
        if header.lower().startswith('user-agent:'):
            user_agent = header.split(':', 1)[1].strip()
        elif header.lower().startswith('content-length:'):
            content_length = int(header.split(':', 1)[1].strip())
        elif header.lower().startswith('accept-encoding:'):
            accepts_gzip = 'gzip' in header.lower()
    
    # 요청 본문 읽기
    if content_length > 0:
        # body = conn.recv(content_length).decode('utf-8')
        pass
    
    if method == 'GET':
        if target == '/':
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif target.startswith('/echo/'):
            echo_string = target[6:]
            content = echo_string.encode()
            if accepts_gzip:
                content = gzip.compress(content)
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\nContent-Encoding: gzip\r\n\r\n".encode() + content
            else:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content
        elif target == '/user-agent':
            content = user_agent.encode()
            if accepts_gzip:
                content = gzip.compress(content)
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\nContent-Encoding: gzip\r\n\r\n".encode() + content
            else:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content
        elif target.startswith('/files/'):
            filename = target[7:]
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    content = file.read()
                if accepts_gzip:
                    content = gzip.compress(content)
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\nContent-Encoding: gzip\r\n\r\n".encode() + content
                else:
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    elif method == 'POST':
        if target.startswith('/files/'):
            filename = target[7:]
            file_path = os.path.join(directory, filename)
            with open(file_path, 'w') as file:
                file.write(body)
            response = b"HTTP/1.1 201 Created\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    else:
        response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"
    
    conn.sendall(response)
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="HTTP 서버")
    parser.add_argument("--directory", default="/tmp", help="파일을 제공할 디렉토리 경로")
    args = parser.parse_args()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print(f"서버가 시작되었습니다. localhost:4221에서 대기 중... (디렉토리: {args.directory})")
    
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, args.directory))
        client_thread.start()


if __name__ == "__main__":
    main()
