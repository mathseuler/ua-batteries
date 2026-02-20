"""Tests for file download and parsing functionality."""
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from ua_batteries.utils.get_file import download_file, get_file


class TestDownloadFile:
    """Test download_file function."""

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_successful_download(self, mock_post):
        """Test successful file download."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": "<table><tr><th>Дата</th>"
            + "".join([f"<th>{i}</th>" for i in range(1, 25)])
            + "</tr>"
            + "<tr><td>01.02.2026</td>"
            + "".join(["<td>1000.0</td>" for _ in range(24)])
            + "</tr></table>"
        }
        mock_post.return_value = mock_response

        with patch("ua_batteries.utils.get_file.os.makedirs"):
            with patch("os.path.join", side_effect=lambda *args: "/".join(args)):
                with patch("builtins.open", create=True):
                    download_file(month_year="02.2026")

        # Verify request was made
        mock_post.assert_called_once()

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_failed_request(self, mock_post):
        """Test handling of failed HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(Exception):
            get_file(month_year="02.2026")


class TestGetFile:
    """Test get_file function."""

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_returns_dataframe(self, mock_post):
        """Test that get_file returns a pandas DataFrame."""
        # Create mock response with valid HTML table
        html_content = (
            """
        <table>
            <tr><th>Дата</th>"""
            + "".join([f"<th>{i}</th>" for i in range(1, 25)])
            + """</tr>
            <tr><td>01.02.2026</td>"""
            + "".join(["<td>1000.0</td>" for _ in range(24)])
            + """</tr>
        </table>
        """
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": html_content}
        mock_post.return_value = mock_response

        result = get_file(month_year="02.2026")

        assert isinstance(result, pd.DataFrame)

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_dataframe_has_columns(self, mock_post):
        """Test that returned dataframe has expected columns."""
        html_content = (
            """
        <table>
            <tr><th>Дата</th>"""
            + "".join([f"<th>{i}</th>" for i in range(1, 25)])
            + """</tr>
            <tr><td>01.02.2026</td>"""
            + "".join(["<td>1000.0</td>" for _ in range(24)])
            + """</tr>
        </table>
        """
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": html_content}
        mock_post.return_value = mock_response

        result = get_file(month_year="02.2026")

        # Should have columns for 24 hours (check at least some columns exist)
        assert len(result.columns) >= 24

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_http_error_raises_exception(self, mock_post):
        """Test that non-200 status code raises exception."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            get_file(month_year="02.2026")

        assert "HTTP" in str(exc_info.value) or "Failed" in str(exc_info.value)

    def test_get_file_requires_valid_response(self):
        """Test that get_file handles malformed responses."""
        with patch("ua_batteries.utils.get_file.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"content": "invalid html"}
            mock_post.return_value = mock_response

            # Should raise an error for invalid HTML
            with pytest.raises(Exception):
                get_file(month_year="02.2026")
