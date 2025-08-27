"""MCP Server Integration Tests

These tests validate the MCP server behavior including:
- Tool registration and discovery
- Parameter validation through MCP protocol
- Response formatting
- Error handling at the MCP layer
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastmcp import Client
from youtube_toolkit.server.app import create_mcp_server
from youtube_toolkit.config import ServerConfig


@pytest.fixture
def test_config():
    """Create test configuration with mocked API key"""
    return ServerConfig(
        name="test-youtube-toolkit",
        youtube_api_key="test-api-key",
        transcript_cache_dir="/tmp/test-cache",
        log_level="DEBUG"
    )


@pytest.fixture
def mcp_server(test_config):
    """Create MCP server instance for testing"""
    return create_mcp_server(test_config)


class TestMCPServerTools:
    """Test MCP server tool registration and execution"""
    
    @pytest.mark.asyncio
    async def test_tool_discovery(self, mcp_server):
        """Test that all tools are properly registered and discoverable"""
        async with Client(mcp_server) as client:
            # List all available tools
            tools = await client.list_tools()
            
            # Verify expected tools are registered
            tool_names = [tool.name for tool in tools]
            expected_tools = [
                "youtube_get_video_metadata",
                "youtube_get_video_transcript", 
                "youtube_get_channel_videos",
                "youtube_search_videos",
                "youtube_get_channel_metadata"
            ]
            
            for expected in expected_tools:
                assert expected in tool_names, f"Tool {expected} not found in registered tools"
            
            # Verify tool descriptions are present
            for tool in tools:
                assert tool.description, f"Tool {tool.name} missing description"
                assert "Parameters:" in tool.description
                assert "Returns:" in tool.description


class TestMCPVideoTools:
    """Test video-related MCP tools through the protocol"""
    
    @pytest.mark.asyncio
    async def test_get_video_metadata_via_mcp(self, mcp_server):
        """Test video metadata fetching through MCP protocol"""
        # Mock the YouTube API response
        mock_response = {
            "items": [{
                "id": "test123",
                "snippet": {
                    "title": "Test Video",
                    "description": "Test Description",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel"
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100"
                }
            }]
        }
        
        with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI') as mock_api:
            mock_instance = MagicMock()
            mock_api.return_value = mock_instance
            mock_instance.videos.return_value.list.return_value.execute.return_value = mock_response
            
            async with Client(mcp_server) as client:
                # Call tool through MCP protocol
                result = await client.call_tool(
                    "youtube_get_video_metadata",
                    {"video_id": "test123", "include_statistics": True}
                )
                
                # Verify response structure
                assert len(result) == 1
                assert hasattr(result[0], 'text')
                
                # Parse and validate response content
                data = json.loads(result[0].text)
                assert data["video_id"] == "test123"
                assert data["title"] == "Test Video"
                assert "statistics" in data
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, mcp_server):
        """Test that MCP validates required parameters"""
        async with Client(mcp_server) as client:
            # Test missing required parameter
            with pytest.raises(Exception) as exc_info:
                await client.call_tool("youtube_get_video_metadata", {})
            
            # The error should indicate missing required parameter
            assert "video_id" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_type_coercion(self, mcp_server):
        """Test MCP type coercion for parameters"""
        with patch('youtube_toolkit.tools.youtube_search.YouTubeAPI'):
            async with Client(mcp_server) as client:
                # Test that string numbers are coerced to integers
                result = await client.call_tool(
                    "youtube_search_videos",
                    {
                        "query": "test",
                        "max_results": "5"  # String instead of int
                    }
                )
                # Should not raise an error - MCP should handle type coercion


class TestMCPChannelTools:
    """Test channel-related MCP tools"""
    
    @pytest.mark.asyncio
    async def test_get_channel_videos_with_defaults(self, mcp_server):
        """Test channel videos with default parameters"""
        mock_response = {
            "items": [{
                "id": {"videoId": "vid1"},
                "snippet": {"title": "Video 1"}
            }]
        }
        
        with patch('youtube_toolkit.tools.youtube_channel.YouTubeAPI') as mock_api:
            mock_instance = MagicMock()
            mock_api.return_value = mock_instance
            mock_instance.search.return_value.list.return_value.execute.return_value = mock_response
            mock_instance.channels.return_value.list.return_value.execute.return_value = {
                "items": [{"snippet": {"title": "Test Channel"}}]
            }
            
            async with Client(mcp_server) as client:
                # Call with only required parameter
                result = await client.call_tool(
                    "youtube_get_channel_videos",
                    {"channel_id": "UC123"}
                )
                
                data = json.loads(result[0].text)
                assert "channel" in data
                assert "videos" in data
                # Verify defaults were applied
                assert len(data["videos"]) <= 10  # default max_results


class TestMCPErrorHandling:
    """Test error handling through MCP protocol"""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, mcp_server):
        """Test how API errors are handled and formatted by MCP"""
        with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI') as mock_api:
            # Simulate API error
            mock_api.side_effect = Exception("API quota exceeded")
            
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "youtube_get_video_metadata",
                    {"video_id": "test123"}
                )
                
                # MCP should return error in structured format
                data = json.loads(result[0].text)
                assert "error" in data
                assert "API quota exceeded" in str(data["error"])


class TestMCPSearchTools:
    """Test search functionality through MCP"""
    
    @pytest.mark.asyncio
    async def test_search_with_optional_params(self, mcp_server):
        """Test search with optional parameters"""
        mock_response = {"items": []}
        
        with patch('youtube_toolkit.tools.youtube_search.YouTubeAPI') as mock_api:
            mock_instance = MagicMock()
            mock_api.return_value = mock_instance
            mock_instance.search.return_value.list.return_value.execute.return_value = mock_response
            
            async with Client(mcp_server) as client:
                # Test with all optional parameters
                result = await client.call_tool(
                    "youtube_search_videos",
                    {
                        "query": "python tutorial",
                        "max_results": 5,
                        "order": "date",
                        "published_after": "2024-01-01T00:00:00Z"
                    }
                )
                
                # Verify call was successful
                data = json.loads(result[0].text)
                assert "query" in data
                assert data["query"] == "python tutorial"


@pytest.mark.asyncio
async def test_concurrent_tool_calls(mcp_server):
    """Test multiple concurrent tool calls through MCP"""
    with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI'), \
         patch('youtube_toolkit.tools.youtube_search.YouTubeAPI'):
        
        async with Client(mcp_server) as client:
            # Make concurrent calls
            import asyncio
            tasks = [
                client.call_tool("youtube_get_video_metadata", {"video_id": "vid1"}),
                client.call_tool("youtube_search_videos", {"query": "test"}),
                client.call_tool("youtube_get_video_metadata", {"video_id": "vid2"})
            ]
            
            results = await asyncio.gather(*tasks)
            assert len(results) == 3
            # All should return valid responses
            for result in results:
                assert len(result) == 1
                assert hasattr(result[0], 'text')


@pytest.mark.asyncio 
async def test_tool_timeout_handling(mcp_server):
    """Test handling of long-running operations"""
    import asyncio
    
    async def slow_api_call(*args, **kwargs):
        await asyncio.sleep(5)
        return {"items": []}
    
    with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI') as mock_api:
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        mock_instance.videos.return_value.list.return_value.execute = slow_api_call
        
        # Create client with short timeout
        async with Client(mcp_server, timeout=1) as client:
            with pytest.raises(asyncio.TimeoutError):
                await client.call_tool(
                    "youtube_get_video_metadata",
                    {"video_id": "test"}
                )