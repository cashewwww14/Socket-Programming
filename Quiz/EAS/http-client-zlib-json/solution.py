import socket
import json
import zlib
import sys
import unittest
from unittest.mock import patch
from io import StringIO

def get_first_length(data):
    """Get the length of the first part of the response, including the header and the content if Content-Length is present."""
    header_end = data.find('\r\n\r\n')
    if header_end == -1:
        header_length = len(data)
        content_length = 0
    else:
        header_length = header_end  # Just the header part without '\r\n\r\n'
        
        # Look for Content-Length header
        header_section = data[:header_end]
        content_length = 0
        for line in header_section.split('\r\n'):
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':')[1].strip())
                break
    
    return header_length + int(content_length)  

def create_socket():
    """Create a client socket and connect to the server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    return client_socket

def client():
    """Send a GET request to the server and print the response."""
    # Create socket and Send the request
    client_socket = create_socket()
    request = "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    client_socket.send(request.encode())

    # Receive the response
    response = b""
    while True:
        # Receive data
        data = client_socket.recv(1024)

        # Break if no more data
        if not data:
            break
        
        response += data

    # Decode and Print the response
    response_str = response.decode()
    print(response_str)

    # Get the status code
    status_line = response_str.split('\r\n')[0]
    status_code = int(status_line.split()[1])

    # Print the status code
    if status_code == 200:
        print("Success: Resource found")
    elif status_code == 404:
        print("Error: Resource not found")
    elif status_code == 500:
        print("Error: Internal server error")

    # Close the socket 
    client_socket.close()

    # Decompress and parse JSON content
    header_end = response_str.find('\r\n\r\n')
    if header_end != -1:
        body = response_str[header_end + 4:]
        if body:
            try:
                # Decompress the body
                compressed_body = body.encode('latin-1')
                decompressed_body = zlib.decompress(compressed_body)
                json_data = json.loads(decompressed_body.decode())
                print(f"Status: {json_data['status']}")
                print(f"Message: {json_data['message']}")
            except:
                print("Failed to decompress or parse JSON")

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

class TestHttpClient(unittest.TestCase):
    def test_get_first_length_no_content_length(self):
        print('Testing get_first_length_no_content_length ...')
        data = "HTTP/1.1 200 OK\r\nServer: TestServer\r\n\r\n"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]))

    def test_get_first_length_with_content_length(self):
        print('Testing get_first_length_with_content_length ...')
        data = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]) + 5)

    @patch('socket.socket')
    def test_create_socket(self, mock_socket):
        print('Testing create_socket ...')
        create_socket()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        instance = mock_socket.return_value
        instance.connect.assert_called_once_with(('localhost', 8080))
        print(f"connect called with: {instance.connect.call_args}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        client()

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)