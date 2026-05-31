"""
네이버 프리미엄콘텐츠(네프콘) MCP 서버

Claude Code에서 네이버 프리미엄콘텐츠의 게시글을 읽고 분석할 수 있도록
MCP(Model Context Protocol) 도구를 제공합니다.

제공 도구:
- list_nepcon_posts: 채널의 게시글 목록 조회
- read_nepcon_post: 특정 게시글 전문 읽어오기
- search_nepcon_posts: 채널 내 키워드 검색

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

app = Server("naver-nepcon")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_nepcon_posts",
            description=(
                "네이버 프리미엄콘텐츠(네프콘) 채널의 최신 게시글 목록을 가져옵니다. "
                "채널 URL과 최대 개수를 지정할 수 있습니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_url": {
                        "type": "string",
                        "description": "채널 URL (예: https://contents.premium.naver.com/son/stockson/contents)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "반환할 최대 게시글 개수 (기본값: 20)",
                        "default": 20,
                    },
                },
                "required": ["channel_url"],
            },
        ),
        types.Tool(
            name="read_nepcon_post",
            description=(
                "특정 네프콘 게시글의 전문을 읽어옵니다. "
                "제목, 본문, 게시 날짜 등 모든 정보를 반환합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "post_url": {
                        "type": "string",
                        "description": "게시글 URL (https://contents.premium.naver.com/...)",
                    },
                },
                "required": ["post_url"],
            },
        ),
        types.Tool(
            name="search_nepcon_posts",
            description=(
                "특정 네프콘 채널 내에서 키워드로 게시글을 검색합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_url": {
                        "type": "string",
                        "description": "채널 URL",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "검색 키워드",
                    },
                },
                "required": ["channel_url", "keyword"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    from nepcon_browser import NaverNepconBrowser

    try:
        async with NaverNepconBrowser() as browser:
            if name == "list_nepcon_posts":
                channel_url = arguments["channel_url"]
                limit = arguments.get("limit", 20)
                posts = await browser.list_nepcon_posts(channel_url, limit)

                if not posts:
                    text = "채널에서 게시글을 찾을 수 없습니다."
                else:
                    lines = [f"채널 최신 게시글 ({len(posts)}개):"]
                    for i, post in enumerate(posts, 1):
                        title = post.get("title", "(제목 없음)")
                        url = post.get("url", "")
                        lines.append(f"{i}. {title}")
                        if url:
                            lines.append(f"   URL: {url}")
                    text = "\n".join(lines)
                return [types.TextContent(type="text", text=text)]

            elif name == "read_nepcon_post":
                post_url = arguments["post_url"]
                post_data = await browser.read_nepcon_post(post_url)

                lines = [
                    f"제목: {post_data.get('title', '(제목 없음)')}",
                    f"날짜: {post_data.get('date', '(날짜 없음)')}",
                    f"URL: {post_data.get('url', '')}",
                    "\n--- 본문 ---\n",
                    post_data.get("content", "(본문 없음)")
                ]
                text = "\n".join(lines)
                return [types.TextContent(type="text", text=text)]

            elif name == "search_nepcon_posts":
                channel_url = arguments["channel_url"]
                keyword = arguments["keyword"]
                posts = await browser.search_nepcon_posts(channel_url, keyword)

                if not posts:
                    text = f"'{keyword}' 검색 결과가 없습니다."
                else:
                    lines = [f"'{keyword}' 검색 결과 ({len(posts)}개):"]
                    for i, post in enumerate(posts, 1):
                        title = post.get("title", "(제목 없음)")
                        url = post.get("url", "")
                        lines.append(f"{i}. {title}")
                        if url:
                            lines.append(f"   URL: {url}")
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
