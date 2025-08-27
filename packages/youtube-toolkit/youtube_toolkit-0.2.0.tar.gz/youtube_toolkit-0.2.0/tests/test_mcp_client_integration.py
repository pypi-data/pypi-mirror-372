"""Integration tests using MCP client to test YouTube toolkit tools

These tests use the actual MCP client protocol to test tools exactly as
MCP clients would call them, including parameter validation and type coercion.
"""
import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent


class TestYouTubeToolsViaMCPClient:
    """Test YouTube tools using actual MCP client protocol"""
    
    @pytest.fixture
    async def mcp_client(self):
        """Create MCP client connected to YouTube toolkit server"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "youtube_toolkit.server.app"],
            env={"YOUTUBE_API_KEY": "test-api-key"}  # Test API key
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    @pytest.mark.asyncio
    async def test_get_video_metadata_via_client(self):
        """Test video metadata fetching through MCP client"""
        # Mock the YouTube API
        mock_response = {
            "items": [{
                "id": "dQw4w9WgXcQ",
                "snippet": {
                    "title": "Never Gonna Give You Up",
                    "description": "The official video",
                    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
                    "channelTitle": "Rick Astley"
                },
                "statistics": {
                    "viewCount": "1000000000",
                    "likeCount": "10000000"
                }
            }]
        }
        
        with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI') as mock_api:
            mock_instance = MagicMock()
            mock_api.return_value = mock_instance
            mock_instance.videos.return_value.list.return_value.execute.return_value = mock_response
            
            # Use actual MCP client to call the tool
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "youtube_toolkit.server.app"],
                env={"YOUTUBE_API_KEY": "test-api-key"}
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Call the tool through MCP protocol
                    result = await session.call_tool(
                        "youtube_get_video_metadata",
                        arguments={
                            "video_id": "dQw4w9WgXcQ",
                            "include_statistics": True
                        }
                    )
                    
                    # Verify response
                    assert len(result.content) == 1
                    content = result.content[0]
                    assert isinstance(content, TextContent)
                    
                    # Parse JSON response
                    data = json.loads(content.text)
                    assert data["video_id"] == "dQw4w9WgXcQ"
                    assert data["title"] == "Never Gonna Give You Up"
                    assert "statistics" in data
                    assert data["statistics"]["viewCount"] == 1000000000
    
    @pytest.mark.asyncio
    async def test_parameter_validation_via_client(self):
        """Test that MCP client properly validates parameters"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "youtube_toolkit.server.app"],
            env={"YOUTUBE_API_KEY": "test-api-key"}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test with missing required parameter
                with pytest.raises(Exception) as exc_info:
                    await session.call_tool(
                        "youtube_get_video_metadata",
                        arguments={}  # Missing video_id
                    )
                
                # Should get MCP protocol error about missing parameter
                assert "video_id" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_type_coercion_via_client(self):
        """Test MCP type coercion through client"""
        with patch('youtube_toolkit.tools.youtube_search.YouTubeAPI'):
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "youtube_toolkit.server.app"],
                env={"YOUTUBE_API_KEY": "test-api-key"}
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Test with string instead of int for max_results
                    result = await session.call_tool(
                        "youtube_search_videos",
                        arguments={
                            "query": "python tutorial",
                            "max_results": "5"  # String, should be coerced to int
                        }
                    )
                    
                    # Should succeed with type coercion
                    assert len(result.content) == 1
                    assert isinstance(result.content[0], TextContent)
    
    @pytest.mark.asyncio
    async def test_tool_discovery_via_client(self):
        """Test that all tools are discoverable through MCP client"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "youtube_toolkit.server.app"],
            env={"YOUTUBE_API_KEY": "test-api-key"}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List all tools
                tools = await session.list_tools()
                
                # Verify expected tools
                tool_names = [tool.name for tool in tools.tools]
                expected_tools = [
                    "youtube_get_video_metadata",
                    "youtube_get_video_transcript",
                    "youtube_get_channel_videos",
                    "youtube_search_videos",
                    "youtube_get_channel_metadata"
                ]
                
                for expected in expected_tools:
                    assert expected in tool_names
                
                # Verify tool has proper schema
                video_tool = next(t for t in tools.tools if t.name == "youtube_get_video_metadata")
                assert video_tool.inputSchema is not None
                assert video_tool.inputSchema["type"] == "object"
                assert "video_id" in video_tool.inputSchema["properties"]
                assert "include_statistics" in video_tool.inputSchema["properties"]
    
    @pytest.mark.asyncio
    async def test_error_handling_via_client(self):
        """Test error handling through MCP client"""
        with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI') as mock_api:
            # Simulate API error
            mock_api.side_effect = Exception("API quota exceeded")
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "youtube_toolkit.server.app"],
                env={"YOUTUBE_API_KEY": "test-api-key"}
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(
                        "youtube_get_video_metadata",
                        arguments={"video_id": "test123"}
                    )
                    
                    # Should get error response
                    assert len(result.content) == 1
                    content = result.content[0]
                    assert isinstance(content, TextContent)
                    
                    data = json.loads(content.text)
                    assert "error" in data
                    assert "API quota exceeded" in str(data["error"])


# Alternative approach using subprocess for more isolation
class TestYouTubeToolsSubprocess:
    """Test YouTube tools by spawning server as subprocess"""
    
    @pytest.mark.asyncio
    async def test_real_subprocess_integration(self):
        """Test with actual subprocess server for complete isolation"""
        import subprocess
        import time
        
        # Start server as subprocess
        server_process = subprocess.Popen(
            ["python", "-m", "youtube_toolkit.server.app"],
            env={"YOUTUBE_API_KEY": "test-api-key"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            # Give server time to start
            time.sleep(1)
            
            # Mock at module level before client connects
            with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI'):
                server_params = StdioServerParameters(
                    command="python",
                    args=["-m", "youtube_toolkit.server.app"],
                    env={"YOUTUBE_API_KEY": "test-api-key"}
                )
                
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        # Verify server info
                        # This tests the complete server startup and initialization
                        tools = await session.list_tools()
                        assert len(tools.tools) == 5
        
        finally:
            server_process.terminate()
            server_process.wait(timeout=5)