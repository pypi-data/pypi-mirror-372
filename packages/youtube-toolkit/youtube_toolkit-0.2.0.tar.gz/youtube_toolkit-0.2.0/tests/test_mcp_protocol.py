"""MCP Protocol-level Tests

These tests validate the MCP protocol implementation including:
- Tool schema validation
- Parameter type definitions
- Response format compliance
- Protocol-level error handling
"""
import pytest
import json
from fastmcp import Client
from youtube_toolkit.server.app import create_mcp_server
from youtube_toolkit.config import ServerConfig


@pytest.fixture
def test_config():
    """Create test configuration"""
    return ServerConfig(
        name="test-youtube-toolkit",
        youtube_api_key="test-api-key",
        transcript_cache_dir="/tmp/test-cache"
    )


@pytest.fixture
def mcp_server(test_config):
    """Create MCP server instance"""
    return create_mcp_server(test_config)


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance and schema validation"""
    
    @pytest.mark.asyncio
    async def test_tool_schema_structure(self, mcp_server):
        """Validate tool schemas follow MCP specification"""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            
            for tool in tools:
                # Validate required fields
                assert hasattr(tool, 'name'), f"Tool missing 'name' field"
                assert hasattr(tool, 'description'), f"Tool {tool.name} missing 'description'"
                
                # If tool has parameters, validate schema
                if hasattr(tool, 'inputSchema'):
                    schema = tool.inputSchema
                    assert 'type' in schema
                    assert schema['type'] == 'object'
                    
                    if 'properties' in schema:
                        # Validate each parameter
                        for param_name, param_schema in schema['properties'].items():
                            assert 'type' in param_schema, f"Parameter {param_name} missing type"
                    
                    # Check required parameters are listed
                    if 'required' in schema:
                        assert isinstance(schema['required'], list)
                        for required_param in schema['required']:
                            assert required_param in schema['properties']
    
    @pytest.mark.asyncio
    async def test_parameter_types(self, mcp_server):
        """Test that parameter types are correctly defined"""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            
            # Find specific tools and validate their parameter types
            tools_dict = {tool.name: tool for tool in tools}
            
            # Test video metadata tool
            video_tool = tools_dict.get("youtube_get_video_metadata")
            assert video_tool is not None
            
            if hasattr(video_tool, 'inputSchema'):
                props = video_tool.inputSchema.get('properties', {})
                assert props['video_id']['type'] == 'string'
                assert props['include_statistics']['type'] == 'boolean'
                
                # Verify video_id is required
                assert 'video_id' in video_tool.inputSchema.get('required', [])
    
    @pytest.mark.asyncio
    async def test_response_format(self, mcp_server):
        """Test that responses follow MCP TextContent format"""
        from unittest.mock import patch, MagicMock
        
        mock_response = {"items": [{"id": "test", "snippet": {"title": "Test"}}]}
        
        with patch('youtube_toolkit.tools.youtube_video.YouTubeAPI') as mock_api:
            mock_instance = MagicMock()
            mock_api.return_value = mock_instance
            mock_instance.videos.return_value.list.return_value.execute.return_value = mock_response
            
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "youtube_get_video_metadata",
                    {"video_id": "test"}
                )
                
                # Validate MCP response structure
                assert len(result) == 1
                response = result[0]
                
                # Check it's a TextContent response
                assert hasattr(response, 'text')
                assert isinstance(response.text, str)
                
                # Validate it's valid JSON
                data = json.loads(response.text)
                assert isinstance(data, dict)


class TestMCPParameterHandling:
    """Test parameter handling edge cases"""
    
    @pytest.mark.asyncio
    async def test_optional_parameter_defaults(self, mcp_server):
        """Test that optional parameters use correct defaults"""
        from unittest.mock import patch, MagicMock
        
        with patch('youtube_toolkit.tools.youtube_search.YouTubeAPI') as mock_api:
            mock_instance = MagicMock()
            mock_api.return_value = mock_instance
            
            # Capture the actual API call parameters
            search_mock = MagicMock()
            mock_instance.search.return_value.list = search_mock
            search_mock.return_value.execute.return_value = {"items": []}
            
            async with Client(mcp_server) as client:
                # Call with minimal parameters
                await client.call_tool(
                    "youtube_search_videos",
                    {"query": "test"}
                )
                
                # Verify defaults were applied
                call_args = search_mock.call_args[1]
                assert call_args['maxResults'] == 10  # default
                assert call_args['order'] == 'relevance'  # default
    
    @pytest.mark.asyncio
    async def test_null_vs_missing_parameters(self, mcp_server):
        """Test handling of null vs missing optional parameters"""
        from unittest.mock import patch
        
        with patch('youtube_toolkit.tools.youtube_channel.YouTubeAPI'):
            async with Client(mcp_server) as client:
                # Test with explicit None/null
                result1 = await client.call_tool(
                    "youtube_get_channel_videos",
                    {
                        "channel_id": "UC123",
                        "delay_seconds": None  # Explicit null
                    }
                )
                
                # Test with parameter omitted
                result2 = await client.call_tool(
                    "youtube_get_channel_videos",
                    {"channel_id": "UC123"}  # delay_seconds omitted
                )
                
                # Both should succeed
                assert len(result1) == 1
                assert len(result2) == 1


class TestMCPErrorProtocol:
    """Test error handling at protocol level"""
    
    @pytest.mark.asyncio
    async def test_malformed_parameters(self, mcp_server):
        """Test handling of malformed parameter types"""
        async with Client(mcp_server) as client:
            # Test with wrong parameter type
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "youtube_search_videos",
                    {
                        "query": "test",
                        "max_results": "not_a_number"  # Invalid type
                    }
                )
            
            # Should indicate type error
            error_msg = str(exc_info.value).lower()
            assert "type" in error_msg or "invalid" in error_msg
    
    @pytest.mark.asyncio
    async def test_unknown_tool_error(self, mcp_server):
        """Test calling non-existent tool"""
        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool("non_existent_tool", {})
            
            assert "unknown tool" in str(exc_info.value).lower() or \
                   "not found" in str(exc_info.value).lower()


class TestMCPMetadata:
    """Test metadata and capability reporting"""
    
    @pytest.mark.asyncio
    async def test_server_info(self, mcp_server):
        """Test server metadata reporting"""
        async with Client(mcp_server) as client:
            # Get server info through initialization
            assert client.server is not None
            
            # Server should report its name
            if hasattr(client.server, 'name'):
                assert client.server.name == "test-youtube-toolkit"
    
    @pytest.mark.asyncio
    async def test_tool_metadata(self, mcp_server):
        """Test that tools include proper metadata"""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            
            # Check YouTube-specific metadata in descriptions
            video_tool = next((t for t in tools if t.name == "youtube_get_video_metadata"), None)
            assert video_tool is not None
            assert "API quota cost:" in video_tool.description
            assert "3 units" in video_tool.description