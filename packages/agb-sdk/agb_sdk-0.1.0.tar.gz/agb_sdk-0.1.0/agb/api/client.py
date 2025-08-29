# -*- coding: utf-8 -*-
"""
AGB API client implementation using HTTP client
"""

from typing import Dict, Optional, Union, List, Any
from agb.api.models import (
    CreateSessionResponse,
    CallMcpToolResponse,
    ListMcpToolsResponse,
    GetMcpResourceResponse,
    ReleaseSessionResponse,
    CreateSessionRequest,
    ReleaseSessionRequest,
    CallMcpToolRequest,
    ListMcpToolsRequest,
    GetMcpResourceRequest,
)
from .http_client import HTTPClient

class Client:
    """
    AGB API client that uses HTTP client
    """

    def __init__(self, config=None):
        """
        Initialize the client

        Args:
            config: Configuration object for HTTP client
        """
        self.config = config
        self._http_client = None

    def _get_http_client(self, api_key: str) -> HTTPClient:
        """
        Get HTTP client instance, creating a new one for each request

        Args:
            api_key: API key for authentication

        Returns:
            HTTPClient: HTTP client instance
        """
        # Always create a new HTTP client for each request
        return HTTPClient(api_key=api_key, cfg=self.config)

    def create_mcp_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        """
        Create MCP session using HTTP client
        """
        # Extract API key from authorization header
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.create_session(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def release_mcp_session(self, request: ReleaseSessionRequest) -> ReleaseSessionResponse:
        """
        Release MCP session using HTTP client
        """
        if not request.session_id:
            raise ValueError("session_id is required")

        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.release_session(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def call_mcp_tool(self, request: CallMcpToolRequest) -> CallMcpToolResponse:
        """
        Call MCP tool using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.call_mcp_tool(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def list_mcp_tools(self, request: ListMcpToolsRequest) -> ListMcpToolsResponse:
        """
        List MCP tools using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.list_mcp_tools(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_mcp_resource(self, request: GetMcpResourceRequest) -> GetMcpResourceResponse:
        """
        Get MCP resource using HTTP client
        """
        if not request.session_id:
            raise ValueError("session_id is required")

        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_mcp_resource(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

