"""Tests for Presidential Speech Records MCP server."""

import pytest
from unittest.mock import patch, AsyncMock
from data_go_mcp.presidential_speeches.server import (
    mcp,
    list_speeches,
    search_speeches,
    get_recent_speeches
)
from data_go_mcp.presidential_speeches.models import (
    Speech2022,
    Speech2023,
    SpeechesResponse2022,
    SpeechesResponse2023
)


class TestMCPServer:
    """MCP 서버 테스트."""
    
    def test_server_initialization(self):
        """서버 초기화 테스트."""
        assert mcp.name == "Presidential Speech Records"


@pytest.fixture
def mock_speeches_2022():
    """Mock 2022 version speeches."""
    return SpeechesResponse2022(
        page=1,
        perPage=10,
        totalCount=100,
        currentCount=2,
        matchCount=100,
        data=[
            Speech2022(
                구분번호=1,
                대통령="홍길동",
                글제목="취임사",
                연설일자="2022-05-10",
                원문보기="https://example.com/speech1",
                연설장소="국회의사당"
            ),
            Speech2022(
                구분번호=2,
                대통령="김철수",
                글제목="신년사",
                연설일자="2022-01-01",
                원문보기="https://example.com/speech2",
                연설장소="청와대"
            )
        ]
    )


@pytest.fixture
def mock_speeches_2023():
    """Mock 2023 version speeches."""
    return SpeechesResponse2023(
        page=1,
        perPage=10,
        totalCount=150,
        currentCount=2,
        matchCount=150,
        data=[
            Speech2023(
                구분번호=101,
                대통령="박영희",
                글제목="경제정책 발표",
                연설연도=2023,
                원문보기="https://example.com/speech101",
                연설장소="대통령실"
            ),
            Speech2023(
                구분번호=102,
                대통령="이민수",
                글제목="외교정책 연설",
                연설연도=2023,
                원문보기="https://example.com/speech102",
                연설장소="외교부"
            )
        ]
    )


@pytest.mark.asyncio
async def test_list_speeches_2023_version(mock_speeches_2023):
    """Test listing speeches with 2023 version."""
    with patch("data_go_mcp.presidential_speeches.server.PresidentialSpeechesAPIClient") as MockClient:
        mock_instance = MockClient.return_value.__aenter__.return_value
        mock_instance.get_speeches_2023 = AsyncMock(return_value=mock_speeches_2023)
        
        result = await list_speeches(page=1, per_page=10, use_2023_version=True)
        
        assert result["total_count"] == 150
        assert result["page"] == 1
        assert result["per_page"] == 10
        assert len(result["data"]) == 2
        
        # Check first speech
        speech = result["data"][0]
        assert speech["id"] == 101
        assert speech["president"] == "박영희"
        assert speech["title"] == "경제정책 발표"
        assert speech["year"] == 2023
        assert speech["source_url"] == "https://example.com/speech101"
        assert speech["location"] == "대통령실"


@pytest.mark.asyncio
async def test_list_speeches_2022_version(mock_speeches_2022):
    """Test listing speeches with 2022 version."""
    with patch("data_go_mcp.presidential_speeches.server.PresidentialSpeechesAPIClient") as MockClient:
        mock_instance = MockClient.return_value.__aenter__.return_value
        mock_instance.get_speeches_2022 = AsyncMock(return_value=mock_speeches_2022)
        
        result = await list_speeches(page=1, per_page=10, use_2023_version=False)
        
        assert result["total_count"] == 100
        assert result["page"] == 1
        assert result["per_page"] == 10
        assert len(result["data"]) == 2
        
        # Check first speech
        speech = result["data"][0]
        assert speech["id"] == 1
        assert speech["president"] == "홍길동"
        assert speech["title"] == "취임사"
        assert speech["date"] == "2022-05-10"
        assert speech["source_url"] == "https://example.com/speech1"
        assert speech["location"] == "국회의사당"


@pytest.mark.asyncio
async def test_search_speeches_by_president(mock_speeches_2023):
    """Test searching speeches by president."""
    with patch("data_go_mcp.presidential_speeches.server.PresidentialSpeechesAPIClient") as MockClient:
        mock_instance = MockClient.return_value.__aenter__.return_value
        mock_instance.search_speeches = AsyncMock(return_value={
            "total_count": 1,
            "page": 1,
            "per_page": 10,
            "data": [mock_speeches_2023.data[0]]
        })
        
        result = await search_speeches(president="박영희")
        
        assert result["total_count"] == 1
        assert len(result["data"]) == 1
        assert result["data"][0]["president"] == "박영희"


@pytest.mark.asyncio
async def test_get_recent_speeches(mock_speeches_2023):
    """Test getting recent speeches."""
    with patch("data_go_mcp.presidential_speeches.server.PresidentialSpeechesAPIClient") as MockClient:
        mock_instance = MockClient.return_value.__aenter__.return_value
        mock_instance.get_speeches_2023 = AsyncMock(return_value=mock_speeches_2023)
        
        result = await get_recent_speeches(limit=2)
        
        assert result["count"] == 2
        assert len(result["data"]) == 2
        
        # Check speeches are in the expected format
        for speech in result["data"]:
            assert "id" in speech
            assert "president" in speech
            assert "title" in speech
            assert "year" in speech
            assert "source_url" in speech
            assert "location" in speech


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in tools."""
    with patch("data_go_mcp.presidential_speeches.server.PresidentialSpeechesAPIClient") as MockClient:
        mock_instance = MockClient.return_value.__aenter__.return_value
        mock_instance.get_speeches_2023 = AsyncMock(side_effect=Exception("API Error"))
        
        result = await list_speeches()
        
        assert "error" in result
        assert result["error"] == "API Error"
        assert result["total_count"] == 0
        assert result["data"] == []