#!/usr/bin/env python

import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import time
from datetime import datetime, timedelta, timezone
from enum import Enum

import dotenv
import requests
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from prometheus_mcp_server.logging_config import get_logger

dotenv.load_dotenv()
mcp = FastMCP("Prometheus MCP")

# Get logger instance
logger = get_logger()

# Pydantic models for structured responses
class HealthStatus(BaseModel):
    status: str = Field(description="Overall health status")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
    timestamp: str = Field(description="ISO timestamp of health check")
    transport: Optional[str] = Field(description="Transport method")
    configuration: Dict[str, bool] = Field(description="Configuration status")
    checks: Dict[str, str] = Field(description="Individual check results")
    prometheus_connectivity: Optional[str] = Field(description="Prometheus connectivity status")
    prometheus_url: Optional[str] = Field(description="Prometheus URL if configured")
    prometheus_error: Optional[str] = Field(description="Prometheus error if any")
    error: Optional[str] = Field(description="Error message if unhealthy")

class QueryResult(BaseModel):
    query: str = Field(description="The PromQL query executed")
    time: Optional[str] = Field(description="Query execution time")
    resultType: str = Field(description="Type of query result")
    result: Any = Field(description="Query result data")
    count: int = Field(description="Number of results")
    timestamp: str = Field(description="ISO timestamp of query execution")

class RangeQueryResult(BaseModel):
    query: str = Field(description="The PromQL query executed")
    start: str = Field(description="Start time of range query")
    end: str = Field(description="End time of range query") 
    step: str = Field(description="Step interval of range query")
    resultType: str = Field(description="Type of query result")
    result: Any = Field(description="Query result data")
    count: int = Field(description="Number of results")
    timestamp: str = Field(description="ISO timestamp of query execution")

class MetricMetadata(BaseModel):
    metric: str = Field(description="Metric name")
    metadata: Dict[str, Any] = Field(description="Metadata information")
    count: int = Field(description="Number of metadata entries")
    timestamp: str = Field(description="ISO timestamp")

class TargetsInfo(BaseModel):
    activeTargets: List[Dict[str, Any]] = Field(description="Active scrape targets")
    droppedTargets: List[Dict[str, Any]] = Field(description="Dropped scrape targets")
    activeCount: int = Field(description="Number of active targets")
    droppedCount: int = Field(description="Number of dropped targets")
    totalCount: int = Field(description="Total number of targets")
    timestamp: str = Field(description="ISO timestamp")

# Health check tool for Docker containers and monitoring
@mcp.tool()
async def health_check() -> HealthStatus:
    """Return health status of the MCP server and Prometheus connection.
    
    Returns:
        Structured health status with metadata
    """
    try:
        health_data = {
            "status": "healthy",
            "service": "prometheus-mcp-server", 
            "version": "1.2.10",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transport": config.mcp_server_config.mcp_server_transport if config.mcp_server_config else "stdio",
            "configuration": {
                "prometheus_url_configured": bool(config.url),
                "authentication_configured": bool(config.username or config.token),
                "org_id_configured": bool(config.org_id)
            },
            "checks": {
                "server": "healthy",
                "prometheus": "unknown"
            }
        }
        
        # Test Prometheus connectivity if configured
        if config.url:
            try:
                # Quick connectivity test
                make_prometheus_request("query", params={"query": "up", "time": str(int(time.time()))})
                health_data["prometheus_connectivity"] = "healthy"
                health_data["prometheus_url"] = config.url
                health_data["checks"]["prometheus"] = "healthy"
            except Exception as e:
                health_data["prometheus_connectivity"] = "unhealthy"
                health_data["prometheus_error"] = str(e)
                health_data["status"] = "degraded"
                health_data["checks"]["prometheus"] = "unhealthy"
        else:
            health_data["status"] = "unhealthy"
            health_data["error"] = "PROMETHEUS_URL not configured"
            health_data["checks"]["prometheus"] = "not_configured"
        
        logger.info("Health check completed", status=health_data["status"])
        return HealthStatus(**health_data)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        error_data = {
            "status": "unhealthy",
            "service": "prometheus-mcp-server",
            "version": "1.2.10",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transport": None,
            "configuration": {},
            "checks": {
                "server": "unhealthy",
                "prometheus": "unknown"
            },
            "error": str(e)
        }
        return HealthStatus(**error_data)


class TransportType(str, Enum):
    """Supported MCP server transport types."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"

    @classmethod
    def values(cls) -> list[str]:
        """Get all valid transport values."""
        return [transport.value for transport in cls]

@dataclass
class MCPServerConfig:
    """Global Configuration for MCP."""
    mcp_server_transport: TransportType = None
    mcp_bind_host: str = None
    mcp_bind_port: int = None

    def __post_init__(self):
        """Validate mcp configuration."""
        if not self.mcp_server_transport:
            raise ValueError("MCP SERVER TRANSPORT is required")
        if not self.mcp_bind_host:
            raise ValueError(f"MCP BIND HOST is required")
        if not self.mcp_bind_port:
            raise ValueError(f"MCP BIND PORT is required")

@dataclass
class PrometheusConfig:
    url: str
    # Optional credentials
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    # Optional Org ID for multi-tenant setups
    org_id: Optional[str] = None
    # Optional Custom MCP Server Configuration
    mcp_server_config: Optional[MCPServerConfig] = None

config = PrometheusConfig(
    url=os.environ.get("PROMETHEUS_URL", ""),
    username=os.environ.get("PROMETHEUS_USERNAME", ""),
    password=os.environ.get("PROMETHEUS_PASSWORD", ""),
    token=os.environ.get("PROMETHEUS_TOKEN", ""),
    org_id=os.environ.get("ORG_ID", ""),
    mcp_server_config=MCPServerConfig(
        mcp_server_transport=os.environ.get("PROMETHEUS_MCP_SERVER_TRANSPORT", "stdio").lower(),
        mcp_bind_host=os.environ.get("PROMETHEUS_MCP_BIND_HOST", "127.0.0.1"),
        mcp_bind_port=int(os.environ.get("PROMETHEUS_MCP_BIND_PORT", "8080"))
    )
)

def get_prometheus_auth():
    """Get authentication for Prometheus based on provided credentials."""
    if config.token:
        return {"Authorization": f"Bearer {config.token}"}
    elif config.username and config.password:
        return requests.auth.HTTPBasicAuth(config.username, config.password)
    return None

def make_prometheus_request(endpoint, params=None):
    """Make a request to the Prometheus API with proper authentication and headers."""
    if not config.url:
        logger.error("Prometheus configuration missing", error="PROMETHEUS_URL not set")
        raise ValueError("Prometheus configuration is missing. Please set PROMETHEUS_URL environment variable.")

    url = f"{config.url.rstrip('/')}/api/v1/{endpoint}"
    auth = get_prometheus_auth()
    headers = {"User-Agent": "prometheus-mcp-server/1.2.10"}

    if isinstance(auth, dict):  # Token auth is passed via headers
        headers.update(auth)
        auth = None  # Clear auth for requests.get if it's already in headers
    
    # Add OrgID header if specified
    if config.org_id:
        headers["X-Scope-OrgID"] = config.org_id

    try:
        logger.debug("Making Prometheus API request", endpoint=endpoint, url=url, params=params)
        
        # Make the request with appropriate headers, auth, and timeout
        response = requests.get(
            url, 
            params=params, 
            auth=auth, 
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result["status"] != "success":
            error_msg = result.get('error', 'Unknown error')
            logger.error("Prometheus API returned error", endpoint=endpoint, error=error_msg, status=result["status"])
            raise ValueError(f"Prometheus API error: {error_msg}")
        
        data_field = result.get("data", {})
        if isinstance(data_field, dict):
            result_type = data_field.get("resultType")
        else:
            result_type = "list"
        logger.debug("Prometheus API request successful", endpoint=endpoint, result_type=result_type)
        return result["data"]
    
    except requests.exceptions.Timeout as e:
        logger.error("Request timed out", endpoint=endpoint, url=url, timeout="30s")
        raise ValueError(f"Prometheus server at {config.url} is not responding (timeout after 30s)")
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection failed", endpoint=endpoint, url=url, error=str(e))
        raise ValueError(f"Cannot connect to Prometheus server at {config.url}")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        logger.error("HTTP error", endpoint=endpoint, url=url, status_code=status_code, error=str(e))
        if status_code == 401:
            raise ValueError("Authentication failed. Please check your Prometheus credentials.")
        elif status_code == 403:
            raise ValueError("Access forbidden. Please check your Prometheus permissions.")
        else:
            raise ValueError(f"HTTP {status_code} error from Prometheus server")
    except requests.exceptions.RequestException as e:
        logger.error("HTTP request to Prometheus failed", endpoint=endpoint, url=url, error=str(e), error_type=type(e).__name__)
        raise ValueError(f"Request failed: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Prometheus response as JSON", endpoint=endpoint, url=url, error=str(e))
        raise ValueError(f"Invalid JSON response from Prometheus: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error during Prometheus request", endpoint=endpoint, url=url, error=str(e), error_type=type(e).__name__)
        raise ValueError(f"Unexpected error: {str(e)}")

@mcp.tool()
async def execute_query(query: str, time: Optional[str] = None) -> QueryResult:
    """Execute an instant query against Prometheus.
    
    Args:
        query: PromQL query string
        time: Optional RFC3339 or Unix timestamp (default: current time)
        
    Returns:
        Structured query result with metadata
    """
    params = {"query": query}
    if time:
        params["time"] = time
    
    logger.info("Executing instant query", query=query, time=time)
    data = make_prometheus_request("query", params=params)
    
    result_data = {
        "query": query,
        "time": time,
        "resultType": data["resultType"],
        "result": data["result"],
        "count": len(data["result"]) if isinstance(data["result"], list) else 1,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info("Instant query completed", 
                query=query, 
                result_type=data["resultType"], 
                result_count=len(data["result"]) if isinstance(data["result"], list) else 1)
    
    return QueryResult(**result_data)

@mcp.tool()
async def execute_range_query(query: str, start: str, end: str, step: str) -> RangeQueryResult:
    """Execute a range query against Prometheus.
    
    Args:
        query: PromQL query string
        start: Start time as RFC3339 or Unix timestamp
        end: End time as RFC3339 or Unix timestamp
        step: Query resolution step width (e.g., '15s', '1m', '1h')
        
    Returns:
        Structured range query result with metadata
    """
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": step
    }
    
    logger.info("Executing range query", query=query, start=start, end=end, step=step)
    data = make_prometheus_request("query_range", params=params)
    
    result_data = {
        "query": query,
        "start": start,
        "end": end,
        "step": step,
        "resultType": data["resultType"],
        "result": data["result"],
        "count": len(data["result"]) if isinstance(data["result"], list) else 1,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info("Range query completed", 
                query=query, 
                result_type=data["resultType"], 
                result_count=len(data["result"]) if isinstance(data["result"], list) else 1)
    
    return RangeQueryResult(**result_data)

@mcp.tool()
async def list_metrics() -> List[str]:
    """Retrieve a list of all metric names available in Prometheus.
    
    Returns:
        List of available metric names
    """
    logger.info("Listing available metrics")
    data = make_prometheus_request("label/__name__/values")
    logger.info("Metrics list retrieved", metric_count=len(data))
    
    # Return just the raw list without any wrapper
    return data

@mcp.tool()
async def get_metric_metadata(metric: str) -> MetricMetadata:
    """Get metadata about a specific metric.
    
    Args:
        metric: The name of the metric to retrieve metadata for
        
    Returns:
        Dictionary containing metadata and metric information
    """
    logger.info("Retrieving metric metadata", metric=metric)
    params = {"metric": metric}
    data = make_prometheus_request("metadata", params=params)
    logger.info("Metric metadata retrieved", metric=metric, metadata_count=len(data["metadata"]))
    
    result_data = {
        "metric": metric,
        "metadata": data["metadata"],
        "count": len(data["metadata"]),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return MetricMetadata(**result_data)

@mcp.tool()
async def get_targets() -> TargetsInfo:
    """Get information about all Prometheus scrape targets.
    
    Returns:
        Structured targets information with metadata
    """
    logger.info("Retrieving scrape targets information")
    data = make_prometheus_request("targets")
    
    result_data = {
        "activeTargets": data["activeTargets"],
        "droppedTargets": data["droppedTargets"],
        "activeCount": len(data["activeTargets"]),
        "droppedCount": len(data["droppedTargets"]),
        "totalCount": len(data["activeTargets"]) + len(data["droppedTargets"]),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info("Scrape targets retrieved", 
                active_targets=len(data["activeTargets"]), 
                dropped_targets=len(data["droppedTargets"]))
    
    return TargetsInfo(**result_data)

if __name__ == "__main__":
    logger.info("Starting Prometheus MCP Server", mode="direct")
    mcp.run(transport="stdio")
