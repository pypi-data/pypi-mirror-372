"""
Email Template Review MCP Server

Main server implementation for the Model Context Protocol.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)
from pydantic import AnyUrl

from .client import EmailTemplateClient
from .review_rules import get_review_rules


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("email-template-review")

# Initialize email template client with configuration from environment variables
# All configuration must be provided via environment variables
base_url = os.getenv("EMAIL_TEMPLATE_BASE_URL")
username = os.getenv("EMAIL_TEMPLATE_USERNAME")
password = os.getenv("EMAIL_TEMPLATE_PASSWORD")

if not base_url:
    logger.error("EMAIL_TEMPLATE_BASE_URL environment variable is required")
    raise ValueError("EMAIL_TEMPLATE_BASE_URL environment variable is required")
if not username:
    logger.error("EMAIL_TEMPLATE_USERNAME environment variable is required")
    raise ValueError("EMAIL_TEMPLATE_USERNAME environment variable is required")
if not password:
    logger.error("EMAIL_TEMPLATE_PASSWORD environment variable is required")
    raise ValueError("EMAIL_TEMPLATE_PASSWORD environment variable is required")

email_client = EmailTemplateClient(
    base_url=base_url,
    username=username,
    password=password
)


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_email_template_info",
                description="获取邮件模版信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "邮件模板ID，例如 1345、2133、2344"
                        }
                    },
                    "required": ["id"]
                }
            ),
            Tool(
                name="update_email_template_status",
                description="更新邮件模版状态（是否审核通过）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_template_id": {
                            "type": "integer",
                            "description": "邮件模板ID"
                        },
                        "subject": {
                            "type": "string",
                            "description": "邮件标题"
                        },
                        "text_body": {
                            "type": "string",
                            "description": "邮件正文（纯文本，支持 {{变量}}）"
                        },
                        "html_body": {
                            "type": "string",
                            "description": "邮件正文（HTML 格式，支持 {{变量}}）"
                        },
                        "is_public": {
                            "type": "integer",
                            "description": "是否公开：0=否，1=是",
                            "default": 0
                        },
                        "remark": {
                            "type": "string",
                            "description": "备注信息",
                            "default": ""
                        },
                        "status": {
                            "type": "integer",
                            "description": "模板状态：1=审核通过，0=审核不通过",
                            "default": 1
                        }
                    },
                    "required": ["email_template_id", "subject", "text_body", "html_body"]
                }
            ),
            Tool(
                name="fetch_review_rules",
                description="获取审核规则",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    )


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    
    if name == "get_email_template_info":
        template_id = arguments.get("id")
        if not template_id:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="错误：缺少必需的参数 'id'"
                )]
            )
        
        try:
            template_info = email_client.get_email_template(int(template_id))
            if template_info:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(template_info, ensure_ascii=False, indent=2)
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"错误：无法获取模板ID {template_id} 的信息"
                    )]
                )
        except Exception as e:
            logger.error(f"Error getting template info: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"错误：{str(e)}"
                )]
            )
    
    elif name == "update_email_template_status":
        try:
            # Prepare update data
            update_data = {
                "email_template_id": arguments.get("email_template_id"),
                "subject": arguments.get("subject"),
                "text_body": arguments.get("text_body"),
                "html_body": arguments.get("html_body"),
                "is_public": arguments.get("is_public", 0),
                "remark": arguments.get("remark", ""),
                "status": arguments.get("status", 1)
            }
            
            # Validate required fields
            required_fields = ["email_template_id", "subject", "text_body", "html_body"]
            missing_fields = [field for field in required_fields if not update_data.get(field)]
            
            if missing_fields:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"错误：缺少必需的参数: {', '.join(missing_fields)}"
                    )]
                )
            
            # Update template
            success = email_client.update_email_template(update_data)
            
            if success:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": "邮件模板更新成功"
                        }, ensure_ascii=False, indent=2)
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "message": "邮件模板更新失败"
                        }, ensure_ascii=False, indent=2)
                    )]
                )
                
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"错误：{str(e)}"
                )]
            )
    
    elif name == "fetch_review_rules":
        try:
            rules = get_review_rules()
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(rules, ensure_ascii=False, indent=2)
                )]
            )
        except Exception as e:
            logger.error(f"Error fetching review rules: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"错误：{str(e)}"
                )]
            )
    
    else:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"未知的工具: {name}"
            )]
        )


async def main():
    """Main function to run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="email-template-review",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


def cli():
    """CLI entry point."""
    asyncio.run(main())

if __name__ == "__main__":
    cli()