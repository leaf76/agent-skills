"""
Test Template for Python (pytest)

Usage:
    pytest tests/test_<module>.py -v
    pytest tests/test_<module>.py::TestClassName::test_method -v
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import your module
# from myapp.module import MyClass, my_function


class TestMyFunction:
    """Tests for my_function"""

    def test_basic_usage(self):
        """Test normal expected behavior"""
        # Arrange
        input_data = "test"
        expected = "expected_output"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == expected

    def test_edge_case_empty_input(self):
        """Test with empty input"""
        result = my_function("")
        assert result is None  # or whatever expected

    def test_edge_case_none_input(self):
        """Test with None input"""
        with pytest.raises(ValueError):
            my_function(None)

    def test_large_input(self):
        """Test with large input"""
        large_input = "x" * 10000
        result = my_function(large_input)
        assert len(result) <= 10000

    @pytest.mark.parametrize("input_val,expected", [
        ("a", "A"),
        ("hello", "HELLO"),
        ("123", "123"),
    ])
    def test_multiple_inputs(self, input_val, expected):
        """Test multiple input/output combinations"""
        assert my_function(input_val) == expected


class TestMyClass:
    """Tests for MyClass"""

    @pytest.fixture
    def instance(self):
        """Create a fresh instance for each test"""
        return MyClass(name="test")

    @pytest.fixture
    def mock_dependency(self):
        """Mock external dependency"""
        with patch("myapp.module.external_service") as mock:
            mock.return_value = {"status": "ok"}
            yield mock

    def test_initialization(self, instance):
        """Test class initialization"""
        assert instance.name == "test"
        assert instance.created_at is not None

    def test_method_success(self, instance, mock_dependency):
        """Test method with mocked dependency"""
        result = instance.do_something()
        
        assert result["success"] is True
        mock_dependency.assert_called_once()

    def test_method_failure(self, instance, mock_dependency):
        """Test method when dependency fails"""
        mock_dependency.side_effect = ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            instance.do_something()


class TestIntegration:
    """Integration tests"""

    @pytest.fixture
    def db_session(self):
        """Setup test database"""
        # Setup
        session = create_test_session()
        yield session
        # Teardown
        session.rollback()
        session.close()

    @pytest.mark.integration
    def test_full_workflow(self, db_session):
        """Test complete user workflow"""
        # Create
        user = User(name="test")
        db_session.add(user)
        db_session.commit()

        # Read
        found = db_session.query(User).filter_by(name="test").first()
        assert found is not None
        assert found.name == "test"


# Async tests (pytest-asyncio)
class TestAsyncFunctions:
    """Tests for async functions"""

    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async function"""
        result = await async_fetch_data()
        assert result is not None


# Fixtures for common test data
@pytest.fixture
def sample_user():
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }


@pytest.fixture
def sample_config():
    return {
        "debug": True,
        "database_url": "sqlite:///:memory:"
    }
