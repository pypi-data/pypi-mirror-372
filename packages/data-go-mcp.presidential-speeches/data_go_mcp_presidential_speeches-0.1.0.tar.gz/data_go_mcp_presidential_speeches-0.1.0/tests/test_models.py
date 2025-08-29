"""Tests for Presidential Speech Records data models."""

import pytest
from data_go_mcp.presidential_speeches.models import (
    Speech2022,
    Speech2023,
    SpeechesResponse2022,
    SpeechesResponse2023
)


def test_speech_2022_model():
    """Test Speech2022 model."""
    data = {
        "구분번호": 1,
        "대통령": "홍길동",
        "글제목": "취임사",
        "연설일자": "2022-05-10",
        "원문보기": "https://example.com/speech1",
        "연설장소": "국회의사당"
    }
    
    speech = Speech2022(**data)
    
    assert speech.id == 1
    assert speech.president == "홍길동"
    assert speech.title == "취임사"
    assert speech.speech_date == "2022-05-10"
    assert speech.source_url == "https://example.com/speech1"
    assert speech.location == "국회의사당"


def test_speech_2023_model():
    """Test Speech2023 model."""
    data = {
        "구분번호": 101,
        "대통령": "박영희",
        "글제목": "경제정책 발표",
        "연설연도": 2023,
        "원문보기": "https://example.com/speech101",
        "연설장소": "대통령실"
    }
    
    speech = Speech2023(**data)
    
    assert speech.id == 101
    assert speech.president == "박영희"
    assert speech.title == "경제정책 발표"
    assert speech.speech_year == 2023
    assert speech.source_url == "https://example.com/speech101"
    assert speech.location == "대통령실"


def test_speeches_response_2022():
    """Test SpeechesResponse2022 model."""
    data = {
        "page": 1,
        "perPage": 10,
        "totalCount": 100,
        "currentCount": 2,
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
    
    response = SpeechesResponse2022(**data)
    
    assert response.page == 1
    assert response.per_page == 10
    assert response.total_count == 100
    assert response.current_count == 2
    assert response.match_count == 100
    assert len(response.data) == 2
    
    # Check first speech
    assert response.data[0].id == 1
    assert response.data[0].president == "홍길동"
    assert response.data[0].title == "취임사"


def test_speeches_response_2023():
    """Test SpeechesResponse2023 model."""
    data = {
        "page": 1,
        "perPage": 10,
        "totalCount": 150,
        "currentCount": 2,
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
    
    response = SpeechesResponse2023(**data)
    
    assert response.page == 1
    assert response.per_page == 10
    assert response.total_count == 150
    assert response.current_count == 2
    assert response.match_count == 150
    assert len(response.data) == 2
    
    # Check first speech
    assert response.data[0].id == 101
    assert response.data[0].president == "박영희"
    assert response.data[0].title == "경제정책 발표"
    assert response.data[0].speech_year == 2023


def test_speech_2022_with_english_keys():
    """Test Speech2022 model can handle both Korean and English field names."""
    data = {
        "id": 1,
        "president": "홍길동",
        "title": "취임사",
        "speech_date": "2022-05-10",
        "source_url": "https://example.com/speech1",
        "location": "국회의사당"
    }
    
    speech = Speech2022(**data)
    
    assert speech.id == 1
    assert speech.president == "홍길동"
    assert speech.title == "취임사"
    assert speech.speech_date == "2022-05-10"
    assert speech.source_url == "https://example.com/speech1"
    assert speech.location == "국회의사당"


def test_speech_2023_with_english_keys():
    """Test Speech2023 model can handle both Korean and English field names."""
    data = {
        "id": 101,
        "president": "박영희",
        "title": "경제정책 발표",
        "speech_year": 2023,
        "source_url": "https://example.com/speech101",
        "location": "대통령실"
    }
    
    speech = Speech2023(**data)
    
    assert speech.id == 101
    assert speech.president == "박영희"
    assert speech.title == "경제정책 발표"
    assert speech.speech_year == 2023
    assert speech.source_url == "https://example.com/speech101"
    assert speech.location == "대통령실"


def test_empty_response_data():
    """Test response models with empty data list."""
    data = {
        "page": 1,
        "perPage": 10,
        "totalCount": 0,
        "currentCount": 0,
        "matchCount": 0,
        "data": []
    }
    
    response_2022 = SpeechesResponse2022(**data)
    assert response_2022.total_count == 0
    assert len(response_2022.data) == 0
    
    response_2023 = SpeechesResponse2023(**data)
    assert response_2023.total_count == 0
    assert len(response_2023.data) == 0