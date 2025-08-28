import pytest

from mm_web3 import random_node


class TestRandomNode:
    """Test cases for the random_node function."""

    def test_handles_single_string_and_slash_removal(self):
        """Should return string as-is and handle slash removal."""
        # Test without slash
        assert random_node("https://node.com") == "https://node.com"

        # Test with slash removal (default)
        assert random_node("https://node.com/") == "https://node.com"

        # Test keeping slash
        assert random_node("https://node.com/", remove_slash=False) == "https://node.com/"

    def test_handles_sequences_and_empty_cases(self):
        """Should work with sequences and raise errors for empty inputs."""
        # Single item list
        assert random_node(["https://node.com/"]) == "https://node.com"

        # Multiple items - just verify it returns one of them
        nodes = ["https://node1.com", "https://node2.com", "https://node3.com"]
        result = random_node(nodes)
        assert result in nodes

        # Empty inputs should raise ValueError
        with pytest.raises(ValueError, match="No nodes provided"):
            random_node([])

        with pytest.raises(ValueError, match="No nodes provided"):
            random_node(())
