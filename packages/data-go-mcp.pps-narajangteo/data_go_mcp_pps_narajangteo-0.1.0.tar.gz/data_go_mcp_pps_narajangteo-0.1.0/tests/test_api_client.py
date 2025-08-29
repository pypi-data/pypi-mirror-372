"""Tests for PpsNarajangteoAPIClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json
import httpx

from data_go_mcp.pps_narajangteo.api_client import PpsNarajangteoAPIClient


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock API key."""
    monkeypatch.setenv("API_KEY", "test-api-key")
    return "test-api-key"


@pytest.fixture
def client(mock_api_key):
    """Create API client instance."""
    return PpsNarajangteoAPIClient()


@pytest.fixture
def sample_bid_announcement_response():
    """Sample bid announcement API response."""
    return {
        "header": {
            "resultCode": "00",
            "resultMsg": "정상"
        },
        "body": {
            "items": {
                "item": [
                    {
                        "bidNtceNo": "R25BK00933743",
                        "bidNtceOrd": "000",
                        "ppsNtceYn": "Y",
                        "bidNtceNm": "2025년 경기미 가공저장시설 스마트화 지원사업",
                        "bidNtceSttusNm": "일반공고",
                        "bidNtceDate": "2025-07-01",
                        "bidNtceBgn": "07:49",
                        "bsnsDivNm": "물품",
                        "elctrnBidYn": "Y",
                        "cntrctCnclsSttusNm": "총액계약",
                        "cntrctCnclsMthdNm": "제한경쟁",
                        "ntceInsttNm": "신김포농업협동조합",
                        "dmndInsttNm": "신김포농업협동조합",
                        "opengDate": "2025-07-08",
                        "opengTm": "16:00",
                        "opengPlce": "국가종합전자조달시스템(나라장터)",
                        "dataBssDate": "2025-08-07"
                    }
                ]
            },
            "numOfRows": 10,
            "pageNo": 1,
            "totalCount": 1
        }
    }


@pytest.fixture
def sample_successful_bid_response():
    """Sample successful bid API response."""
    return {
        "header": {
            "resultCode": "00",
            "resultMsg": "정상"
        },
        "body": {
            "items": {
                "item": {
                    "bidNtceNo": "R25BK00925778",
                    "bidNtceOrd": "000",
                    "bidNtceNm": "[부여]국도40호 가탑삼거리 교차로개선사업",
                    "bsnsDivNm": "공사",
                    "cntrctCnclsSttusNm": "총액계약",
                    "cntrctCnclsMthdNm": "수의계약",
                    "ntceInsttNm": "충청남도 건설본부",
                    "dmndInsttNm": "충청남도 건설본부",
                    "opengDate": "2025-07-01",
                    "opengTm": "10:00",
                    "opengRsltDivNm": "개찰완료",
                    "fnlSucsfAmt": "122845000",
                    "fnlSucsfCorpNm": "대륜건설(주)",
                    "dataBssDate": "2025-08-08"
                }
            },
            "numOfRows": 10,
            "pageNo": 1,
            "totalCount": 1
        }
    }


@pytest.fixture
def sample_contract_response():
    """Sample contract API response."""
    return {
        "header": {
            "resultCode": "00",
            "resultMsg": "정상"
        },
        "body": {
            "items": {
                "item": {
                    "cntrctNo": "R25TA00247713",
                    "cntrctOrd": "00",
                    "cntrctNm": "2025년 시내버스 노후LED 전광판 교체사업",
                    "bsnsDivNm": "물품",
                    "cntrctCnclsSttusNm": "총액계약",
                    "cntrctCnclsMthdNm": "지명경쟁",
                    "cntrctCnclsDate": "2025-03-05",
                    "cntrctPrd": "2025.03.05.",
                    "cntrctAmt": "214345450",
                    "cntrctInsttDivNm": "지방자치단체",
                    "cntrctInsttNm": "충청남도 천안시",
                    "dmndInsttDivNm": "지방자치단체",
                    "dmndInsttNm": "충청남도 천안시",
                    "rprsntCorpNm": "주식회사 티이케이",
                    "dataBssDate": "2025-08-05"
                }
            },
            "numOfRows": 10,
            "pageNo": 1,
            "totalCount": 1
        }
    }


class TestPpsNarajangteoAPIClient:
    """Test cases for PpsNarajangteoAPIClient."""
    
    def test_init_with_api_key(self, mock_api_key):
        """Test client initialization with API key."""
        client = PpsNarajangteoAPIClient(api_key="custom-key")
        assert client.api_key == "custom-key"
        assert client.base_url == "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService"
    
    def test_init_without_api_key(self):
        """Test client initialization without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            PpsNarajangteoAPIClient()
    
    def test_parse_response_json(self, client):
        """Test parsing JSON response."""
        json_str = '{"test": "value"}'
        result = client._parse_response(json_str, "json")
        assert result == {"test": "value"}
    
    def test_parse_response_xml(self, client):
        """Test parsing XML response."""
        xml_str = '<?xml version="1.0"?><response><test>value</test></response>'
        result = client._parse_response(xml_str, "xml")
        assert result == {"test": "value"}
    
    @pytest.mark.asyncio
    async def test_get_bid_announcements(self, client, sample_bid_announcement_response):
        """Test getting bid announcements."""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_bid_announcement_response
            
            result = await client.get_bid_announcements(
                bid_notice_begin_dt="202507010000",
                bid_notice_end_dt="202507012359"
            )
            
            assert result == sample_bid_announcement_response
            mock_request.assert_called_once_with(
                "getDataSetOpnStdBidPblancInfo",
                {
                    "bidNtceBgnDt": "202507010000",
                    "bidNtceEndDt": "202507012359",
                    "numOfRows": 10,
                    "pageNo": 1
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_successful_bids(self, client, sample_successful_bid_response):
        """Test getting successful bids."""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_successful_bid_response
            
            result = await client.get_successful_bids(
                business_div_code="3",
                opening_begin_dt="202507010000",
                opening_end_dt="202507012359"
            )
            
            assert result == sample_successful_bid_response
            mock_request.assert_called_once_with(
                "getDataSetOpnStdScsbidInfo",
                {
                    "bsnsDivCd": "3",
                    "opengBgnDt": "202507010000",
                    "opengEndDt": "202507012359",
                    "numOfRows": 10,
                    "pageNo": 1
                }
            )
    
    @pytest.mark.asyncio
    async def test_get_contracts(self, client, sample_contract_response):
        """Test getting contracts."""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = sample_contract_response
            
            result = await client.get_contracts(
                contract_begin_date="20250305",
                contract_end_date="20250305",
                institution_div_code="1",
                institution_code="4490000"
            )
            
            assert result == sample_contract_response
            mock_request.assert_called_once_with(
                "getDataSetOpnStdCntrctInfo",
                {
                    "cntrctCnclsBgnDate": "20250305",
                    "cntrctCnclsEndDate": "20250305",
                    "insttDivCd": "1",
                    "insttCd": "4490000",
                    "numOfRows": 10,
                    "pageNo": 1
                }
            )
    
    @pytest.mark.asyncio
    async def test_request_with_error_response(self, client):
        """Test handling error response from API."""
        error_response = {
            "header": {
                "resultCode": "30",
                "resultMsg": "등록되지 않은 서비스키"
            }
        }
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.text = json.dumps(error_response)
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="API 오류: 등록되지 않은 서비스키"):
                await client._request("test_endpoint")
    
    @pytest.mark.asyncio
    async def test_request_http_error(self, client):
        """Test handling HTTP error."""
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=MagicMock(status_code=404)
            )
            
            with pytest.raises(httpx.HTTPStatusError):
                await client._request("test_endpoint")
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_api_key):
        """Test async context manager."""
        async with PpsNarajangteoAPIClient() as client:
            assert client.api_key == mock_api_key
            assert client.client is not None