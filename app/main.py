import socket  # noqa: F401
import threading
import os
import argparse


def handle_client(conn, addr, directory):
    request = conn.recv(1024).decode('utf-8')
    print(f"연결된 클라이언트: {addr}")
    print(request)
    
    # HTTP 요청 파싱
    headers = request.split('\r\n')
    request_line = headers[0]
    method, target, _ = request_line.split(' ')
    
    # User-Agent 헤더 찾기 (대소문자 구분 없이)
    user_agent = ''
    for header in headers:
        if header.lower().startswith('user-agent:'):
            user_agent = header.split(':', 1)[1].strip()
            break
    
    if method == 'GET':
        if target == '/':
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif target.startswith('/echo/'):
            echo_string = target[6:]  # '/echo/' 이후의 문자열 추출
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_string)}\r\n\r\n{echo_string}"
            response = response.encode()
        elif target == '/user-agent':
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
            response = response.encode()
        elif target.startswith('/files/'):
            filename = target[7:]  # '/files/' 이후의 문자열 추출
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                file_size = len(file_content)
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {file_size}\r\n\r\n".encode()
                response += file_content
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    
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
