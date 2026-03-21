"""Tests for file download and parsing functionality."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

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
        """Test handling of failed request."""
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert "HTTP Error occurred" in str(exc_info.value)


class TestGetFile:
    """Test get_file function."""

    def test_get_file_rejects_unsupported_language(self):
        """Test unsupported language."""
        with pytest.raises(ValueError) as exc_info:
            get_file(month_year="02.2026", lang="German")

        assert "Unsupported language" in str(exc_info.value)

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
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert isinstance(exc_info.value, RuntimeError)

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_get_file_requires_content_key(self, mock_post):
        """Test that get_file rejects responses missing the content key."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert "missing 'content'" in str(exc_info.value)

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_get_file_requires_table_in_html(self, mock_post):
        """Test that get_file rejects HTML without a table."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": "<html><body>No table here</body></html>"}
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert "no table found" in str(exc_info.value)

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_get_file_requires_date_column(self, mock_post):
        """Test that get_file rejects table without Дата column."""
        html_content = (
            "<table><tr>"
            + "".join([f"<th>{i}</th>" for i in range(1, 25)])
            + "</tr><tr>"
            + "".join(["<td>1000.0</td>" for _ in range(24)])
            + "</tr></table>"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"content": html_content}
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert "missing 'Дата' column" in str(exc_info.value)

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_get_file_requires_all_hour_columns(self, mock_post):
        """Test that get_file rejects table with missing hour columns."""
        html_content = (
            "<table><tr><th>Дата</th>"
            + "".join([f"<th>{i}</th>" for i in range(1, 11)])
            + "</tr><tr><td>01.02.2026</td>"
            + "".join(["<td>1000.0</td>" for _ in range(10)])
            + "</tr></table>"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"content": html_content}
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert "missing hour columns" in str(exc_info.value)

    @patch("ua_batteries.utils.get_file.requests.post")
    def test_get_file_requires_valid_json_body(self, mock_post):
        """Test that get_file rejects responses with invalid JSON body."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            get_file(month_year="02.2026")

        assert "response body is not a valid JSON" in str(exc_info.value)
