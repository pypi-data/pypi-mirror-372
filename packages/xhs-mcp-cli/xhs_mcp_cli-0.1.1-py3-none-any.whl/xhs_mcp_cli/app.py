import json
import logging
import os
from datetime import datetime
from typing import Any, Literal, Optional, cast
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
) -> dict[str, Optional[str]]:
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


def _format_notes_list(items: list[dict[str, Any]]) -> dict[str, Any]:
    """将笔记列表转换为结构化数据"""
    notes = []
    for item in items:
        note_card = item.get("note_card")
        if note_card and "display_title" in note_card:
            note_data = {
                "id": item.get("id"),
                "title": note_card.get("display_title", ""),
                "interact_info": {
                    "liked_count": note_card.get("interact_info", {}).get(
                        "liked_count", 0
                    ),
                    "comment_count": note_card.get("interact_info", {}).get(
                        "comment_count", 0
                    ),
                    "collected_count": note_card.get("interact_info", {}).get(
                        "collected_count", 0
                    ),
                },
                "url": f"https://www.xiaohongshu.com/explore/{item['id']}?xsec_token={item.get('xsec_token', '')}",
                "xsec_token": item.get("xsec_token", ""),
                "user": {
                    "nickname": note_card.get("user", {}).get("nickname", ""),
                    "user_id": note_card.get("user", {}).get("user_id", ""),
                },
                "type": note_card.get("type", ""),
                "desc": note_card.get("desc", "")[:100] + "..."
                if len(note_card.get("desc", "")) > 100
                else note_card.get("desc", ""),
            }
            notes.append(note_data)

    return {"success": True, "total_count": len(notes), "notes": notes}


def _format_note_content(
    items: list[dict[str, Any]], note_id: str, xsec_token: str
) -> dict[str, Any]:
    """将笔记内容转换为结构化数据"""
    if not items:
        return {"success": False, "message": "未找到笔记内容", "data": None}

    note_card = items[0].get("note_card", {})
    user = note_card.get("user", {})
    images = [img.get("url_pre", "") for img in note_card.get("image_list", [])]
    publish_time = datetime.fromtimestamp(note_card.get("time", 0) / 1000).isoformat()

    return {
        "success": True,
        "data": {
            "note_id": note_id,
            "xsec_token": xsec_token,
            "title": note_card.get("title", ""),
            "desc": note_card.get("desc", ""),
            "type": note_card.get("type", ""),
            "publish_time": publish_time,
            "url": f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}",
            "user": {
                "user_id": user.get("user_id", ""),
                "nickname": user.get("nickname", ""),
                "avatar": user.get("avatar", ""),
            },
            "interact_info": {
                "liked_count": note_card.get("interact_info", {}).get("liked_count", 0),
                "comment_count": note_card.get("interact_info", {}).get(
                    "comment_count", 0
                ),
                "collected_count": note_card.get("interact_info", {}).get(
                    "collected_count", 0
                ),
                "share_count": note_card.get("interact_info", {}).get("share_count", 0),
            },
            "images": images,
            "cover_image": images[0] if images else "",
            "tag_list": note_card.get("tag_list", []),
        },
    }


def _format_comments(comments: list[dict[str, Any]]) -> dict[str, Any]:
    """将评论列表转换为结构化数据"""
    formatted_comments = []
    for comment in comments:
        comment_time = datetime.fromtimestamp(
            comment.get("create_time", 0) / 1000
        ).isoformat()
        comment_data = {
            "comment_id": comment.get("id", ""),
            "content": comment.get("content", ""),
            "create_time": comment_time,
            "like_count": comment.get("like_count", 0),
            "user": {
                "user_id": comment.get("user_info", {}).get("user_id", ""),
                "nickname": comment.get("user_info", {}).get("nickname", ""),
                "avatar": comment.get("user_info", {}).get("image", ""),
            },
            "sub_comments": comment.get("sub_comments", []),
            "sub_comment_count": len(comment.get("sub_comments", [])),
        }
        formatted_comments.append(comment_data)

    return {
        "success": True,
        "total_count": len(formatted_comments),
        "comments": formatted_comments,
    }


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
        """检测 cookie 是否失效，返回JSON格式结果"""
        try:
            data = await xhs_api.get_me()
            result = {
                "success": True,
                "valid": bool(data.get("success")),
                "message": "cookie有效" if data.get("success") else "cookie已失效",
            }
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.exception("检测 cookie 失败")
            result = {
                "success": False,
                "valid": False,
                "message": "cookie检测失败",
                "error": str(e),
            }
            return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    async def home_feed() -> str:
        """获取首页推荐笔记，返回JSON格式结果"""
        try:
            data = await xhs_api.home_feed()
            items = data.get("data", {}).get("items", [])

            if items:
                result = _format_notes_list(items)
                result["message"] = "成功获取首页推荐"
            else:
                cookie_check = json.loads(await check_cookie())
                if not cookie_check.get("valid"):
                    result = {
                        "success": False,
                        "message": "cookie已失效，请更新cookie",
                        "notes": [],
                    }
                else:
                    result = {
                        "success": True,
                        "message": "暂无推荐内容",
                        "total_count": 0,
                        "notes": [],
                    }

            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.exception("获取首页推荐失败")
            result = {
                "success": False,
                "message": "获取首页推荐失败",
                "error": str(e),
                "notes": [],
            }
            return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    async def search_notes(keywords: str) -> str:
        """根据关键词搜索笔记，返回JSON格式结果"""
        try:
            data = await xhs_api.search_notes(keywords)
            items = data.get("data", {}).get("items", [])

            if items:
                result = _format_notes_list(items)
                result["message"] = f"成功搜索到 {len(items)} 条相关笔记"
                result["keywords"] = keywords
            else:
                cookie_check = json.loads(await check_cookie())
                if not cookie_check.get("valid"):
                    result = {
                        "success": False,
                        "message": "cookie已失效，请更新cookie",
                        "keywords": keywords,
                        "notes": [],
                    }
                else:
                    result = {
                        "success": True,
                        "message": f"未找到与 '{keywords}' 相关的笔记",
                        "keywords": keywords,
                        "total_count": 0,
                        "notes": [],
                    }

            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.exception("搜索笔记失败")
            result = {
                "success": False,
                "message": "搜索笔记失败",
                "keywords": keywords,
                "error": str(e),
                "notes": [],
            }
            return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    async def get_note_content(url: str) -> str:
        """获取笔记内容，返回JSON格式结果"""
        try:
            params = get_nodeid_token(url=url)
            note_id = params.get("note_id")
            xsec_token = params.get("xsec_token")

            if not note_id or not xsec_token:
                result = {
                    "success": False,
                    "message": "无法解析 note_id 或 xsec_token，请检查输入的链接",
                    "data": None,
                }
                return json.dumps(result, ensure_ascii=False)

            data = await xhs_api.get_note_content(
                note_id=note_id, xsec_token=xsec_token
            )
            items = data.get("data", {}).get("items", [])

            if not items:
                cookie_check = json.loads(await check_cookie())
                if not cookie_check.get("valid"):
                    result = {
                        "success": False,
                        "message": "cookie已失效，请更新cookie",
                        "data": None,
                    }
                else:
                    result = {
                        "success": False,
                        "message": "笔记内容获取失败或笔记不存在",
                        "data": None,
                    }
            else:
                result = _format_note_content(items, note_id, xsec_token)
                result["message"] = "成功获取笔记内容"

            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.exception("获取笔记内容失败")
            result = {
                "success": False,
                "message": "获取笔记内容失败",
                "error": str(e),
                "data": None,
            }
            return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    async def get_note_comments(url: str) -> str:
        """获取笔记评论，返回JSON格式结果"""
        try:
            params = get_nodeid_token(url=url)
            note_id = params.get("note_id")
            xsec_token = params.get("xsec_token")

            if not note_id or not xsec_token:
                result = {
                    "success": False,
                    "message": "无法解析 note_id 或 xsec_token，请检查输入的链接",
                    "comments": [],
                }
                return json.dumps(result, ensure_ascii=False)

            data = await xhs_api.get_note_comments(
                note_id=note_id, xsec_token=xsec_token
            )
            comments = data.get("data", {}).get("comments", [])

            if not comments:
                cookie_check = json.loads(await check_cookie())
                if not cookie_check.get("valid"):
                    result = {
                        "success": False,
                        "message": "cookie已失效，请更新cookie",
                        "comments": [],
                    }
                else:
                    result = {
                        "success": True,
                        "message": "该笔记暂无评论",
                        "total_count": 0,
                        "comments": [],
                    }
            else:
                result = _format_comments(comments)
                result["message"] = f"成功获取 {len(comments)} 条评论"
                result["note_id"] = note_id

            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.exception("获取笔记评论失败")
            result = {
                "success": False,
                "message": "获取笔记评论失败",
                "error": str(e),
                "comments": [],
            }
            return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    async def post_comment(comment: str, note_id: str) -> str:
        """发布评论，返回JSON格式结果"""
        try:
            response = await xhs_api.post_comment(note_id, comment)

            if response.get("success"):
                result = {
                    "success": True,
                    "message": "评论发布成功",
                    "note_id": note_id,
                    "comment": comment,
                }
            else:
                cookie_check = json.loads(await check_cookie())
                if not cookie_check.get("valid"):
                    result = {
                        "success": False,
                        "message": "cookie已失效，请更新cookie",
                        "note_id": note_id,
                        "comment": comment,
                    }
                else:
                    result = {
                        "success": False,
                        "message": "评论发布失败",
                        "note_id": note_id,
                        "comment": comment,
                        "error": response.get("msg", "未知错误"),
                    }

            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.exception("发布评论失败")
            result = {
                "success": False,
                "message": "发布评论失败",
                "note_id": note_id,
                "comment": comment,
                "error": str(e),
            }
            return json.dumps(result, ensure_ascii=False)

    logger.info("xhs-mcp start")
    mcp.run(transport=cast(Literal["stdio", "sse", "streamable-http"], transport))


if __name__ == "__main__":
    app()
