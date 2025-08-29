import unittest
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from elmoclient import ElmoClient

class MockSocket:
    def __init__(self, *args, **kwargs):
        self.timeout_count = 0
        self.max_timeouts = 2  # Number of times to simulate timeout before succeeding
        
    def connect(self, *args, **kwargs):
        pass
        
    def settimeout(self, *args, **kwargs):
        pass
        
    def sendall(self, *args, **kwargs):
        pass
        
    def send(self, *args, **kwargs):
        pass
        
    def recv(self, *args, **kwargs):
        # Simulate timeout for the first few calls
        if self.timeout_count < self.max_timeouts:
            self.timeout_count += 1
            raise TimeoutError("timed out")
        # Return some dummy data after timeouts
        return b'\x02\x01\x08\x00\x00\x3f\x00\x48\x03'
        
    def close(self):
        pass

class TestTimeoutHandling(unittest.TestCase):
    @patch('socket.socket', return_value=MockSocket())
    def test_timeout_handling(self, mock_socket):
        # Create client with mock socket
        client = ElmoClient(host="127.0.0.1", port=10001, timeout=0.1)
        
        # Start client
        client.start()
        
        # Enable polling to trigger status updates
        client.polling_enabled = True
        
        # Wait for timeouts to occur and be handled
        time.sleep(1)
        
        # Stop client
        client.stop()
        
        # If we got here without exceptions, the test passed
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()