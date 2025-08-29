import unittest
from unittest.mock import Mock, patch
from heaptree.client import Heaptree
from heaptree.response_wrappers import CreateNodeResponseWrapper
from heaptree.exceptions import HeaptreeAPIException

class TestCreateNodeResponseWrapper(unittest.TestCase):
    def test_single_node_access(self):
        """Test convenient access to single node ID"""
        raw_response = {
            "node_ids": ["node-123"],
            "web_access_urls": {"node-123": "https://example.com/node-123"},
            "status": "success",
            "execution_time_seconds": 45.2
        }
        
        result = CreateNodeResponseWrapper(raw_response)
        
        # Test single node access
        self.assertEqual(result.node_id, "node-123")
        self.assertEqual(result.web_access_url, "https://example.com/node-123")
        self.assertEqual(result.node_ids, ["node-123"])
        self.assertEqual(result.web_access_urls, {"node-123": "https://example.com/node-123"})
    
    def test_multiple_nodes_access(self):
        """Test access to multiple node IDs"""
        raw_response = {
            "node_ids": ["node-123", "node-456"],
            "web_access_urls": {
                "node-123": "https://example.com/node-123",
                "node-456": "https://example.com/node-456"
            },
            "status": "success",
            "execution_time_seconds": 120.5
        }
        
        result = CreateNodeResponseWrapper(raw_response)
        
        # Test multiple node access
        self.assertEqual(result.node_ids, ["node-123", "node-456"])
        expected_urls = {
            "node-123": "https://example.com/node-123",
            "node-456": "https://example.com/node-456"
        }
        self.assertEqual(result.web_access_urls, expected_urls)
    
    def test_single_node_access_error_on_multiple(self):
        """Test that accessing .node_id raises error when multiple nodes exist"""
        raw_response = {
            "node_ids": ["node-123", "node-456"],
            "web_access_urls": {
                "node-123": "https://example.com/node-123",
                "node-456": "https://example.com/node-456"
            },
            "status": "success",
            "execution_time_seconds": 60.0
        }
        
        result = CreateNodeResponseWrapper(raw_response)
        
        # Should raise ValueError when trying to access single node ID
        with self.assertRaises(ValueError) as cm:
            _ = result.node_id
        
        self.assertIn("Multiple nodes created", str(cm.exception))
        self.assertIn("Use .node_ids", str(cm.exception))
        
        # Should raise ValueError when trying to access single web URL
        with self.assertRaises(ValueError) as cm:
            _ = result.web_access_url
        
        self.assertIn("Multiple nodes created", str(cm.exception))


class TestHeaptreeSDK(unittest.TestCase):
    def setUp(self):
        self.client = Heaptree(api_key="test")

    @patch('heaptree.client.requests.post')
    def test_create_node_returns_node_creation_result(self, mock_post):
        """Test that create_node returns CreateNodeResponseWrapper instance"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "node_ids": ["node-123"],
            "web_access_urls": {"node-123": "https://example.com/node-123"},
            "status": "success",
            "execution_time_seconds": 45.2
        }
        mock_post.return_value = mock_response
        
        result = self.client.create_node(
            os="linux",
            num_nodes=1,
            node_type="ubuntu",
            node_size="t2.micro"
        )
        
        # Check that result is CreateNodeResponseWrapper instance
        self.assertIsInstance(result, CreateNodeResponseWrapper)
        self.assertEqual(result.node_id, "node-123")
        self.assertEqual(result.web_access_url, "https://example.com/node-123")

    def test_create_node_failure(self):
        """Test create_node with invalid API key"""
        client = Heaptree(api_key="invalid")
        with self.assertRaises(HeaptreeAPIException):
            client.create_node("linux", 1, "ubuntu", "t2.micro")


if __name__ == "__main__":
    unittest.main()
