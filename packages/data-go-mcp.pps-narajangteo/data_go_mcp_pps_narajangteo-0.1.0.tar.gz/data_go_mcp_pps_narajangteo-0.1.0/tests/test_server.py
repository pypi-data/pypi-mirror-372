"""Tests for MCP server."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import os

from data_go_mcp.pps_narajangteo.server import (
    format_datetime_for_api,
    parse_business_type,
    search_bid_announcements,
    search_successful_bids,
    search_contracts,
    get_bid_detail,
    main,
    mcp
)


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_format_datetime_for_api_default(self):
        """Test default datetime formatting."""
        with patch('data_go_mcp.pps_narajangteo.server.datetime') as mock_dt:
            mock_now = datetime(2025, 7, 1, 10, 30)
            mock_dt.now.return_value = mock_now
            
            # Test default (no date provided)
            result = format_datetime_for_api()
            assert result == "202507010000"
            
            # Test end date default
            result = format_datetime_for_api(is_end=True)
            assert result == "202507012359"
    
    def test_format_datetime_for_api_with_date(self):
        """Test datetime formatting with provided date."""
        # Test YYYY-MM-DD format
        result = format_datetime_for_api("2025-07-01")
        assert result == "202507010000"
        
        result = format_datetime_for_api("2025-07-01", is_end=True)
        assert result == "202507012359"
        
        # Test YYYYMMDD format
        result = format_datetime_for_api("20250701")
        assert result == "202507010000"
        
        # Test YYYYMMDDHHMM format
        result = format_datetime_for_api("202507011430")
        assert result == "202507011430"
    
    def test_format_datetime_for_api_invalid(self):
        """Test invalid datetime format."""
        with pytest.raises(ValueError, match="잘못된 날짜/시간 형식"):
            format_datetime_for_api("2025-7-1")  # Wrong format
    
    def test_parse_business_type(self):
        """Test business type parsing."""
        assert parse_business_type("물품") == "1"
        assert parse_business_type("외자") == "2"
        assert parse_business_type("공사") == "3"
        assert parse_business_type("용역") == "5"
        assert parse_business_type("1") == "1"
        assert parse_business_type("unknown") == "unknown"


class TestMCPServer:
    """MCP 서버 테스트."""
    
    def test_server_initialization(self):
        """서버 초기화 테스트."""
        assert mcp.name == "나라장터 공공데이터개방표준서비스"


class TestMCPTools:
    """Test MCP tool functions."""
    
    @pytest.mark.asyncio
    async def test_search_bid_announcements_success(self):
        """Test successful bid announcement search."""
        mock_response = {
            "body": {
                "items": {
                    "item": [
                        {
                            "bidNtceNo": "R25BK00933743",
                            "bidNtceNm": "Test Bid",
                            "opengDate": "2025-07-08"
                        }
                    ]
                },
                "totalCount": 1,
                "pageNo": 1,
                "numOfRows": 10
            }
        }
        
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_bid_announcements = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await search_bid_announcements(
                start_date="2025-07-01",
                end_date="2025-07-01"
            )
            
            assert result["success"] is True
            assert len(result["items"]) == 1
            assert result["items"][0]["bidNtceNo"] == "R25BK00933743"
            assert result["total_count"] == 1
    
    @pytest.mark.asyncio
    async def test_search_bid_announcements_error(self):
        """Test bid announcement search with error."""
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_bid_announcements = AsyncMock(side_effect=Exception("API Error"))
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await search_bid_announcements()
            
            assert result["success"] is False
            assert "API Error" in result["error"]
            assert result["items"] == []
    
    @pytest.mark.asyncio
    async def test_search_successful_bids_success(self):
        """Test successful bid search."""
        mock_response = {
            "body": {
                "items": {
                    "item": {
                        "bidNtceNo": "R25BK00925778",
                        "fnlSucsfCorpNm": "Test Corp",
                        "fnlSucsfAmt": "100000000"
                    }
                },
                "totalCount": 1,
                "pageNo": 1,
                "numOfRows": 10
            }
        }
        
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_successful_bids = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await search_successful_bids(
                business_type="공사",
                start_date="2025-07-01"
            )
            
            assert result["success"] is True
            assert len(result["items"]) == 1
            assert result["items"][0]["bidNtceNo"] == "R25BK00925778"
            assert result["business_type"] == "공사"
    
    @pytest.mark.asyncio
    async def test_search_contracts_success(self):
        """Test contract search."""
        mock_response = {
            "body": {
                "items": {
                    "item": {
                        "cntrctNo": "R25TA00247713",
                        "cntrctNm": "Test Contract",
                        "cntrctAmt": "200000000"
                    }
                },
                "totalCount": 1,
                "pageNo": 1,
                "numOfRows": 10
            }
        }
        
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await search_contracts(
                start_date="2025-03-05",
                institution_type="1",
                institution_code="4490000"
            )
            
            assert result["success"] is True
            assert len(result["items"]) == 1
            assert result["items"][0]["cntrctNo"] == "R25TA00247713"
            assert result["institution_filter"]["type"] == "1"
            assert result["institution_filter"]["code"] == "4490000"
    
    @pytest.mark.asyncio
    async def test_get_bid_detail_found(self):
        """Test getting bid detail when found."""
        mock_response = {
            "body": {
                "items": {
                    "item": [
                        {
                            "bidNtceNo": "R25BK00933743",
                            "bidNtceNm": "Target Bid",
                            "opengDate": "2025-07-08"
                        },
                        {
                            "bidNtceNo": "R25BK00933744",
                            "bidNtceNm": "Other Bid",
                            "opengDate": "2025-07-09"
                        }
                    ]
                }
            }
        }
        
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_bid_announcements = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await get_bid_detail("R25BK00933743")
            
            assert result["success"] is True
            assert result["data"]["bidNtceNo"] == "R25BK00933743"
            assert result["data"]["bidNtceNm"] == "Target Bid"
    
    @pytest.mark.asyncio
    async def test_get_bid_detail_not_found(self):
        """Test getting bid detail when not found."""
        mock_response = {
            "body": {
                "items": {
                    "item": [
                        {
                            "bidNtceNo": "R25BK00933744",
                            "bidNtceNm": "Other Bid"
                        }
                    ]
                }
            }
        }
        
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_bid_announcements = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            result = await get_bid_detail("R25BK00933743")
            
            assert result["success"] is False
            assert "찾을 수 없습니다" in result["error"]
            assert result["data"] is None
    
    @pytest.mark.asyncio
    async def test_search_with_default_dates(self):
        """Test search with default date handling."""
        mock_response = {
            "body": {
                "items": [],
                "totalCount": 0,
                "pageNo": 1,
                "numOfRows": 10
            }
        }
        
        with patch('data_go_mcp.pps_narajangteo.server.PpsNarajangteoAPIClient') as MockClient:
            mock_client = AsyncMock()
            mock_client.get_bid_announcements = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__.return_value = mock_client
            
            # Test without providing dates (should use today)
            result = await search_bid_announcements()
            
            assert result["success"] is True
            # Verify that get_bid_announcements was called
            mock_client.get_bid_announcements.assert_called_once()
            call_args = mock_client.get_bid_announcements.call_args[1]
            # Check that dates are today's date
            assert len(call_args["bid_notice_begin_dt"]) == 12  # YYYYMMDDHHMM
            assert len(call_args["bid_notice_end_dt"]) == 12


class TestMain:
    """Test main function."""
    
    def test_main_without_api_key(self, capsys):
        """Test main function without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('data_go_mcp.pps_narajangteo.server.mcp') as mock_mcp:
                main()
                
                captured = capsys.readouterr()
                assert "Warning: API_KEY environment variable is not set" in captured.out
                assert "https://www.data.go.kr" in captured.out
                mock_mcp.run.assert_called_once()
    
    def test_main_with_api_key(self, capsys):
        """Test main function with API key."""
        with patch.dict(os.environ, {"API_KEY": "test-key"}):
            with patch('data_go_mcp.pps_narajangteo.server.mcp') as mock_mcp:
                main()
                
                captured = capsys.readouterr()
                assert "Warning" not in captured.out
                mock_mcp.run.assert_called_once()