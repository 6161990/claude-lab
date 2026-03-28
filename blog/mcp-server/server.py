"""
네이버 블로그 MCP 서버

Claude Code에서 네이버 블로그를 직접 운영할 수 있도록 MCP(Model Context Protocol) 도구를 제공합니다.

제공 도구:
- post_blog: 블로그에 새 글 발행
- save_draft: 임시저장
- list_drafts: 임시저장 목록 조회
- get_categories: 카테고리 목록 조회

설치 방법:
    pip install -r requirements.txt
    playwright install chromium

실행 방법:
    python server.py
    (Claude Code에서 MCP 서버로 자동 실행됩니다)
"""

import asyncio
import json
import os
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv()

BLOG_ID = os.getenv("NAVER_BLOG_ID", "kong__home")

app = Server("naver-blog")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="post_blog",
            description=(
                "네이버 블로그(콩콩이대작전)에 새 포스팅을 발행합니다. "
                "Playwright 브라우저 자동화로 스마트에디터에 글을 작성하고 발행합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "포스팅 제목 (SEO를 고려한 자연스러운 한국어 제목)",
                    },
                    "content": {
                        "type": "string",
                        "description": "포스팅 본문 내용 (일반 텍스트)",
                    },
                    "category": {
                        "type": "string",
                        "description": "카테고리 이름 (예: 일상이야기, 여행일기, 맛집탐방, 카페투어)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "태그 목록 (최대 10개)",
                    },
                    "publish_now": {
                        "type": "boolean",
                        "default": True,
                        "description": "즉시 발행 여부. false이면 임시저장",
                    },
                },
                "required": ["title", "content"],
            },
        ),
        types.Tool(
            name="save_draft",
            description="네이버 블로그 포스팅을 임시저장합니다. 검토 후 나중에 발행할 때 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "포스팅 제목"},
                    "content": {"type": "string", "description": "포스팅 본문"},
                    "category": {"type": "string", "description": "카테고리 이름 (선택)"},
                },
                "required": ["title", "content"],
            },
        ),
        types.Tool(
            name="list_drafts",
            description="임시저장된 포스팅 목록을 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="get_categories",
            description="블로그에 설정된 카테고리 목록을 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    from naver_browser import NaverBlogBrowser
    from smart_editor import SmartEditorAutomation

    try:
        async with NaverBlogBrowser() as browser:
            if name == "post_blog":
                editor = SmartEditorAutomation(browser.page, BLOG_ID)
                result = await editor.write_post(
                    title=arguments["title"],
                    content=arguments["content"],
                    category=arguments.get("category"),
                    tags=arguments.get("tags"),
                    publish_now=arguments.get("publish_now", True),
                )
                action = "발행" if result["action"] == "published" else "임시저장"
                message = f"포스팅 {action} 완료!"
                if result.get("url"):
                    message += f"\n포스팅 URL: {result['url']}"
                return [types.TextContent(type="text", text=message)]

            elif name == "save_draft":
                editor = SmartEditorAutomation(browser.page, BLOG_ID)
                result = await editor.write_post(
                    title=arguments["title"],
                    content=arguments["content"],
                    category=arguments.get("category"),
                    publish_now=False,
                )
                return [types.TextContent(type="text", text="임시저장 완료! 나중에 검토 후 발행하세요.")]

            elif name == "list_drafts":
                drafts = await browser.list_drafts()
                if not drafts:
                    text = "임시저장된 포스팅이 없습니다."
                else:
                    lines = ["임시저장 포스팅 목록:"]
                    for i, d in enumerate(drafts, 1):
                        lines.append(f"{i}. {d.get('title', '(제목 없음)')} - {d.get('date', '')}")
                    text = "\n".join(lines)
                return [types.TextContent(type="text", text=text)]

            elif name == "get_categories":
                categories = await browser.get_categories()
                if not categories:
                    text = "카테고리 정보를 가져올 수 없습니다."
                else:
                    lines = ["블로그 카테고리 목록:"]
                    for cat in categories:
                        lines.append(f"- {cat.get('name', '')}")
                    text = "\n".join(lines)
                return [types.TextContent(type="text", text=text)]

            else:
                return [types.TextContent(type="text", text=f"알 수 없는 도구: {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"오류 발생: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
