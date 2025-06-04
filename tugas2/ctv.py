# Deskripsi: Client terhubung ke server di localhost:12345 dan mengirim pesan "Hello, Server!".
# Input: Tidak ada input langsung; komunikasi melalui socket.
# Output:
#   - Server mencetak: Hello, Server!
#   - Client mencetak:
#       connect called with: call(('127.0.0.1', 12345))
#       send called with: call(b'Hello, Server!')
#       close called with: call()

import socket
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

# Server functionality
def server_program():
    host = '127.0.0.1'
    port = 12345
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    conn, addr = server_socket.accept()
    message = conn.recv(1024).decode()
    print(f"Received message: {message}")
    
    conn.close()
    server_socket.close()

# Client functionality
def client_program():
    host = '127.0.0.1'
    port = 12345
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    message = "Hello, Server!".encode()
    client_socket.send(message)
    
    client_socket.close()

# Unit test for the client code
class TestClient(unittest.TestCase):
    @patch('socket.socket')  # Mock the socket object
    def test_client_program(self, mock_socket):
        # Create a mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Call the function under test
        client_program()

        # Assert that connect was called with the right address
        mock_socket_instance.connect.assert_called_once_with(('127.0.0.1', 12345))
        print(f"connect called with: {mock_socket_instance.connect.call_args}")

        # Assert that send was called with the right message
        mock_socket_instance.send.assert_called_once_with(b'Hello, Server!')
        print(f"send called with: {mock_socket_instance.send.call_args}")

        # Assert that close was called
        mock_socket_instance.close.assert_called_once()
        print(f"close called with: {mock_socket_instance.close.call_args}")

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

if __name__ == '__main__':
    # Run unittest with a custom runner that suppresses output
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

    # Uncomment this to run the server and client
    # import threading
    # server_thread = threading.Thread(target=server_program, daemon=True)
    # server_thread.start()
    # client_program()
