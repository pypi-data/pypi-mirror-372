"""Tests for Presidential Speech Records API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from data_go_mcp.presidential_speeches.api_client import PresidentialSpeechesAPIClient
from data_go_mcp.presidential_speeches.models import (
    SpeechesResponse2022, 
    SpeechesResponse2023,
    Speech2022,
    Speech2023
)


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key-123"


@pytest.fixture
def sample_response_2022():
    """Sample 2022 version API response."""
    return {
        "page": 1,
        "perPage": 10,
        "totalCount": 100,
        "currentCount": 10,
        "matchCount": 100,
        "data": [
            {
                "구분번호": 1,
                "대통령": "홍길동",
                "글제목": "취임사",
                "연설일자": "2022-05-10",
                "원문보기": "https://example.com/speech1",
                "연설장소": "국회의사당"
            },
            {
                "구분번호": 2,
                "대통령": "김철수",
                "글제목": "신년사",
                "연설일자": "2022-01-01",
                "원문보기": "https://example.com/speech2",
                "연설장소": "청와대"
            }
        ]
    }


@pytest.fixture
def sample_response_2023():
    """Sample 2023 version API response."""
    return {
        "page": 1,
        "perPage": 10,
        "totalCount": 150,
        "currentCount": 10,
        "matchCount": 150,
        "data": [
            {
                "구분번호": 101,
                "대통령": "박영희",
                "글제목": "경제정책 발표",
                "연설연도": 2023,
                "원문보기": "https://example.com/speech101",
                "연설장소": "대통령실"
            },
            {
                "구분번호": 102,
                "대통령": "이민수",
                "글제목": "외교정책 연설",
                "연설연도": 2023,
                "원문보기": "https://example.com/speech102",
                "연설장소": "외교부"
            }
        ]
    }


@pytest.mark.asyncio
async def test_client_initialization(api_key):
    """Test API client initialization."""
    client = PresidentialSpeechesAPIClient(api_key=api_key)
    assert client.api_key == api_key
    assert client.base_url == "https://api.odcloud.kr/api/15084167/v1"
    assert isinstance(client.client, httpx.AsyncClient)
    await client.client.aclose()


@pytest.mark.asyncio
async def test_client_initialization_from_env(monkeypatch, api_key):
    """Test API client initialization from environment variable."""
    monkeypatch.setenv("API_KEY", api_key)
    client = PresidentialSpeechesAPIClient()
    assert client.api_key == api_key
    await client.client.aclose()


@pytest.mark.asyncio
async def test_client_initialization_no_key():
    """Test API client initialization without API key raises error."""
    with pytest.raises(ValueError, match="API key is required"):
        PresidentialSpeechesAPIClient()


@pytest.mark.asyncio
async def test_get_speeches_2022(api_key, sample_response_2022):
    """Test getting 2022 version speeches."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_2022
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            result = await client.get_speeches_2022(page=1, per_page=10)
            
            assert isinstance(result, SpeechesResponse2022)
            assert result.page == 1
            assert result.per_page == 10
            assert result.total_count == 100
            assert len(result.data) == 2
            
            # Check first speech
            speech = result.data[0]
            assert isinstance(speech, Speech2022)
            assert speech.id == 1
            assert speech.president == "홍길동"
            assert speech.title == "취임사"
            assert speech.speech_date == "2022-05-10"
            assert speech.source_url == "https://example.com/speech1"
            assert speech.location == "국회의사당"


@pytest.mark.asyncio
async def test_get_speeches_2023(api_key, sample_response_2023):
    """Test getting 2023 version speeches."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_2023
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            result = await client.get_speeches_2023(page=1, per_page=10)
            
            assert isinstance(result, SpeechesResponse2023)
            assert result.page == 1
            assert result.per_page == 10
            assert result.total_count == 150
            assert len(result.data) == 2
            
            # Check first speech
            speech = result.data[0]
            assert isinstance(speech, Speech2023)
            assert speech.id == 101
            assert speech.president == "박영희"
            assert speech.title == "경제정책 발표"
            assert speech.speech_year == 2023
            assert speech.source_url == "https://example.com/speech101"
            assert speech.location == "대통령실"


@pytest.mark.asyncio
async def test_search_speeches_by_president(api_key, sample_response_2023):
    """Test searching speeches by president name."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_2023
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            result = await client.search_speeches(president="박영희")
            
            assert result["total_count"] == 1
            assert len(result["data"]) == 1
            assert result["data"][0].president == "박영희"


@pytest.mark.asyncio
async def test_search_speeches_by_title(api_key, sample_response_2023):
    """Test searching speeches by title."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_2023
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            result = await client.search_speeches(title="경제")
            
            assert result["total_count"] == 1
            assert len(result["data"]) == 1
            assert "경제" in result["data"][0].title


@pytest.mark.asyncio
async def test_search_speeches_by_year(api_key, sample_response_2023):
    """Test searching speeches by year."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_2023
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            result = await client.search_speeches(year=2023)
            
            assert result["total_count"] == 2
            assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_search_speeches_by_location(api_key, sample_response_2023):
    """Test searching speeches by location."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_2023
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            result = await client.search_speeches(location="대통령실")
            
            assert result["total_count"] == 1
            assert len(result["data"]) == 1
            assert result["data"][0].location == "대통령실"


@pytest.mark.asyncio
async def test_api_error_401(api_key):
    """Test handling 401 authentication error."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", 
            request=MagicMock(), 
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            with pytest.raises(ValueError, match="인증 정보가 정확하지 않습니다"):
                await client.get_speeches_2023()


@pytest.mark.asyncio
async def test_api_error_500(api_key):
    """Test handling 500 server error."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=MagicMock(),
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
            with pytest.raises(ValueError, match="API 서버에 문제가 발생했습니다"):
                await client.get_speeches_2023()


@pytest.mark.asyncio
async def test_context_manager(api_key):
    """Test async context manager."""
    async with PresidentialSpeechesAPIClient(api_key=api_key) as client:
        assert client.api_key == api_key
        assert not client.client.is_closed
    
    # Client should be closed after exiting context
    assert client.client.is_closed