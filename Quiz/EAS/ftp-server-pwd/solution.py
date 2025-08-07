import socket
import select
import zlib
import os
import sys
import unittest
from unittest import mock
from io import StringIO

class FTPServer:
    def __init__(self, host='127.0.0.1', port=2000):
        """Create a new FTP server listening on the specified host and port."""
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        self.inputs = [self.sock]
        self.client_data = {}
        print(f"Listening on {host}:{port}")

    def start(self):
        while True:
            readable, _, _ = select.select(self.inputs, [], [])
            for s in readable:
                if s is self.sock:
                    # Accept new client connection
                    client_sock, addr = s.accept()
                    self.inputs.append(client_sock)
                    # Send welcome message
                    welcome_msg = zlib.compress(b'220 Welcome to the FTP server\r\n')
                    client_sock.sendall(welcome_msg)
                else:
                    # Handle existing client
                    try:
                        data = s.recv(1024)
                        if data:
                            self.client_data[s] = data
                            self.handle_client(s)
                        else:
                            # Client disconnected
                            self.inputs.remove(s)
                            if s in self.client_data:
                                del self.client_data[s]
                            s.close()
                    except:
                        # Error handling
                        self.inputs.remove(s)
                        if s in self.client_data:
                            del self.client_data[s]
                        s.close()

    def handle_client(self, client_sock):
        """Handle a new client connection."""
        # Read the data from the client socket and decompress
        compressed_data = self.client_data.get(client_sock)
        if compressed_data:
            try:
                decompressed_data = zlib.decompress(compressed_data)
                command = decompressed_data.decode('ascii').strip()
                print(f"Received command: {command}")
                
                # Handle the FTP command
                if command.startswith('USER'):
                    response = zlib.compress(b'331 Username OK, need password\r\n')
                    client_sock.sendall(response)
                elif command.startswith('PASS'):
                    response = zlib.compress(b'230 User logged in\r\n')
                    client_sock.sendall(response)
                elif command == 'PWD':
                    current_dir = os.getcwd()
                    response_msg = f'257 "{current_dir}"\r\n'.encode('ascii')
                    response = zlib.compress(response_msg)
                    client_sock.sendall(response)
                elif command == 'QUIT':
                    response = zlib.compress(b'221 Goodbye\r\n')
                    client_sock.sendall(response)
                    # Remove client from inputs and client_data
                    if client_sock in self.inputs:
                        self.inputs.remove(client_sock)
                    if client_sock in self.client_data:
                        del self.client_data[client_sock]
                    client_sock.close()
                else:
                    # Unknown command
                    response = zlib.compress(b'502 Command not implemented\r\n')
                    client_sock.sendall(response)
                    
            except Exception as e:
                # Error in decompression or processing
                response = zlib.compress(b'500 Internal server error\r\n')
                client_sock.sendall(response)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestFTPServer(unittest.TestCase):
    def setUp(self):
        self.server = FTPServer()

    def tearDown(self):
        self.server.sock.close()

    def test_handle_client_user(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'USER valid_username\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'331 Username OK, need password\r\n'))

    def test_handle_client_pass(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'PASS valid_password\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'230 User logged in\r\n'))

    def test_handle_client_pwd(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'PWD\r\n')}
        with mock.patch('os.getcwd', return_value='/mock/directory'):
            self.server.handle_client(client_sock)
            client_sock.sendall.assert_called_with(zlib.compress(b'257 "/mock/directory"\r\n'))

    def test_handle_client_quit(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'QUIT\r\n')}
        self.server.inputs.append(client_sock)
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'221 Goodbye\r\n'))
        self.assertEqual(self.server.inputs, [self.server.sock])
        self.assertNotIn(client_sock, self.server.client_data)
        client_sock.close.assert_called_once()

    def test_handle_client_unknown_command(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'UNKNOWN_COMMAND\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'502 Command not implemented\r\n'))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_server = FTPServer()
        ftp_server.start()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)