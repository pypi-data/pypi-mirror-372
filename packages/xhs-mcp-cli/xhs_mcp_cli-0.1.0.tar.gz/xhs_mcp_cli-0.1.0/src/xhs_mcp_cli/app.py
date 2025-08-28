import logging
import os
from datetime import datetime
from typing import Any, Dict, Literal, Optional, cast
from urllib.parse import parse_qs, urlparse

import typer
from mcp.server.fastmcp import FastMCP
from rich.logging import RichHandler

from xhs_mcp_cli.api.xhs_api import XhsApi

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True, show_time=False),
    ],
)
logger = logging.getLogger(__name__)


def get_nodeid_token(
    url: Optional[str] = None, note_ids: Optional[str] = None
) -> Dict[str, Optional[str]]:
    """解析 note_id 和 xsec_token"""
    if note_ids is not None:
        return {"note_id": note_ids[:24], "xsec_token": note_ids[24:]}
    if url is None:
        return {"note_id": None, "xsec_token": None}

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    note_id = parsed_url.path.split("/")[-1]
    xsec_token = query_params.get("xsec_token", [None])[0]
    return {"note_id": note_id, "xsec_token": xsec_token}


def _format_notes_list(items: list[Dict[str, Any]]) -> str:
    """统一格式化笔记列表输出"""
    result = "搜索结果：\n\n"
    for i, item in enumerate(items):
        note_card = item.get("note_card")
        if note_card and "display_title" in note_card:
            title = note_card["display_title"]
            liked_count = note_card["interact_info"]["liked_count"]
            url = f"https://www.xiaohongshu.com/explore/{item['id']}?xsec_token={item['xsec_token']}"
            result += f"{i}. {title}\n  点赞数: {liked_count}\n  链接: {url}\n\n"
    return result


@app.command()
def cli(
    port: int = typer.Option(8809, help="服务端口"),
    transport: str = typer.Option(
        "stdio",
        help="传输方式，可选: stdio, sse, streamable-http",
        case_sensitive=False,
    ),
):
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise typer.BadParameter("transport 必须是 stdio/sse/streamable-http 之一")

    mcp = FastMCP("小红书", port=port)
    xhs_api = XhsApi(cookie=os.getenv("XHS_COOKIE"))

    @mcp.tool()
    async def check_cookie() -> str:
        """检测 cookie 是否失效"""
        try:
            data = await xhs_api.get_me()
            return "cookie有效" if data.get("success") else "cookie已失效"
        except Exception:
            logger.exception("检测 cookie 失败")
            return "cookie已失效"

    @mcp.tool()
    async def home_feed() -> str:
        """获取首页推荐笔记"""
        data = await xhs_api.home_feed()
        items = data.get("data", {}).get("items", [])
        return _format_notes_list(items) if items else await check_cookie()

    @mcp.tool()
    async def search_notes(keywords: str) -> str:
        """根据关键词搜索笔记"""
        data = await xhs_api.search_notes(keywords)
        items = data.get("data", {}).get("items", [])
        return (
            _format_notes_list(items)
            if items
            else f'未找到与 "{keywords}" 相关的笔记'
            if "有效" in await check_cookie()
            else await check_cookie()
        )

    @mcp.tool()
    async def get_note_content(url: str) -> str:
        """获取笔记内容"""
        params = get_nodeid_token(url=url)
        note_id = params.get("note_id")
        xsec_token = params.get("xsec_token")
        if not note_id or not xsec_token:
            return "无法解析 note_id 或 xsec_token，请检查输入的链接或参数。"
        data = await xhs_api.get_note_content(note_id=note_id, xsec_token=xsec_token)
        items = data.get("data", {}).get("items", [])

        if not items:
            return await check_cookie()

        note_card = items[0].get("note_card", {})
        user = note_card.get("user", {})
        cover = note_card.get("image_list", [{}])[0].get("url_pre", "")
        dt = datetime.fromtimestamp(note_card.get("time", 0) / 1000)

        return (
            f"标题: {note_card.get('title', '')}\n"
            f"作者: {user.get('nickname', '')}\n"
            f"发布时间: {dt}\n"
            f"点赞数: {note_card.get('interact_info', {}).get('liked_count', 0)}\n"
            f"评论数: {note_card.get('interact_info', {}).get('comment_count', 0)}\n"
            f"收藏数: {note_card.get('interact_info', {}).get('collected_count', 0)}\n"
            f"链接: https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}\n\n"
            f"内容:\n{note_card.get('desc', '')}\n"
            f"封面:\n{cover}"
        )

    @mcp.tool()
    async def get_note_comments(url: str) -> str:
        """获取笔记评论"""
        params = get_nodeid_token(url=url)
        note_id = params.get("note_id")
        xsec_token = params.get("xsec_token")
        if not note_id or not xsec_token:
            return "无法解析 note_id 或 xsec_token，请检查输入的链接或参数。"
        data = await xhs_api.get_note_comments(note_id=note_id, xsec_token=xsec_token)
        comments = data.get("data", {}).get("comments", [])

        if not comments:
            return await check_cookie()

        return "\n\n".join(
            f"{i}. {c['user_info']['nickname']}（{datetime.fromtimestamp(c['create_time'] / 1000)}）: {c['content']}"
            for i, c in enumerate(comments)
        )

    @mcp.tool()
    async def post_comment(comment: str, note_id: str) -> str:
        """发布评论"""
        response = await xhs_api.post_comment(note_id, comment)
        if response.get("success"):
            return "回复成功"
        return (
            await check_cookie() if "有效" not in await check_cookie() else "回复失败"
        )

    logger.info("xhs-mcp start")
    mcp.run(transport=cast(Literal["stdio", "sse", "streamable-http"], transport))


if __name__ == "__main__":
    app()
