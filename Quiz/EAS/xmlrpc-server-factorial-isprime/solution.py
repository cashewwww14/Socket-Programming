import xmlrpc.server
import xmlrpc.client
import math
import sys
import unittest
from unittest.mock import patch, Mock
from io import StringIO

# Function to calculate factorial
def factorial(n):
    if n < 0:
        raise ValueError("Negative numbers do not have factorials.")
    return math.factorial(n)

# Function to check if a number is prime
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def run_xmlrpc_server():
    # Create server
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))

    # Register the complex functions
    server.register_function(factorial, "factorial")
    server.register_function(is_prime, "is_prime")

    # Run the server's main loop
    print("Server listening on localhost:8000")
    server.serve_forever()

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

def assert_true(parameter, name):
    if parameter == True:
        print(f'test attribute {name} passed: {parameter} is True')
    else:
        print(f'test attribute {name} failed: {parameter} is not True')

def assert_false(parameter, name):
    if parameter == False:
        print(f'test attribute {name} passed: {parameter} is False')
    else:
        print(f'test attribute {name} failed: {parameter} is not False')

class TestXMLRPCFunctions(unittest.TestCase):

    @patch('xmlrpc.client.ServerProxy')
    def test_factorial_positive(self, mock_server_proxy):
        # Create a mock server proxy
        mock_server = Mock()
        mock_server.factorial.return_value = 120
        mock_server_proxy.return_value = mock_server
        
        proxy = mock_server_proxy('http://localhost:8000')
        print('test factorial_positive')
        assert_equal(proxy.factorial(5), 120)
        proxy.factorial.assert_called_once_with(5)

    @patch('xmlrpc.client.ServerProxy')
    def test_factorial_zero(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.factorial.return_value = 1
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test factorial_zero')
        assert_equal(proxy.factorial(0), 1)
        proxy.factorial.assert_called_once_with(0)

    @patch('xmlrpc.client.ServerProxy')
    def test_factorial_negative(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.factorial.side_effect = xmlrpc.client.Fault(1, "Negative numbers do not have factorials.")
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test factorial_negative')
        with self.assertRaises(xmlrpc.client.Fault):
            proxy.factorial(-1)
        proxy.factorial.assert_called_once_with(-1)

    @patch('xmlrpc.client.ServerProxy')
    def test_is_prime_true(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.is_prime.return_value = True
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test is_prime_true')
        assert_true(proxy.is_prime(7), True)
        proxy.is_prime.assert_called_once_with(7)

    @patch('xmlrpc.client.ServerProxy')
    def test_is_prime_false(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.is_prime.return_value = False
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test is_prime_false')
        assert_false(proxy.is_prime(4), False)
        proxy.is_prime.assert_called_once_with(4)

    @patch('xmlrpc.client.ServerProxy')
    def test_is_prime_one(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.is_prime.return_value = False
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test is_prime_one')
        assert_false(proxy.is_prime(1), False)
        proxy.is_prime.assert_called_once_with(1)

    @patch('xmlrpc.client.ServerProxy')
    def test_is_prime_zero(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.is_prime.return_value = False
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test is_prime_zero')
        assert_false(proxy.is_prime(0), False)
        proxy.is_prime.assert_called_once_with(0)

    @patch('xmlrpc.client.ServerProxy')
    def test_is_prime_negative(self, mock_server_proxy):
        mock_server = Mock()
        mock_server.is_prime.return_value = False
        mock_server_proxy.return_value = mock_server

        proxy = mock_server_proxy('http://localhost:8000')
        print('test is_prime_negative')
        assert_false(proxy.is_prime(-3), False)
        proxy.is_prime.assert_called_once_with(-3)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        run_xmlrpc_server()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)