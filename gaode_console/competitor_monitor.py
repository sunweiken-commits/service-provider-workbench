from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import requests

from gaode_console.storage import append_record, load_data


HEADERS = {"User-Agent": "Mozilla/5.0"}

DOUYIN_DOC_SOURCES = [
    {
        "platform": "抖音",
        "source_name": "抖音开放平台-生活服务商家应用概述",
        "item_type": "能力文档",
        "url": "https://developer.open-douyin.com/docs/resource/zh-CN/local-life/introduction/overview",
        "importance_base": 90,
    },
    {
        "platform": "抖音",
        "source_name": "抖音开放平台-服务商平台概述",
        "item_type": "能力文档",
        "url": "https://developer.open-douyin.com/docs/resource/zh-CN/thirdparty/overview/platform-intro/",
        "importance_base": 88,
    },
    {
        "platform": "抖音",
        "source_name": "抖音开放平台-生活服务代运营服务商接入",
        "item_type": "接入文档",
        "url": "https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/open-capacity/Industry/life/partner/partner-landing-guide",
        "importance_base": 92,
    },
    {
        "platform": "抖音",
        "source_name": "抖音开放平台-来客IM客服",
        "item_type": "能力文档",
        "url": "https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/open-capacity/operation/private-account/customer-service/douyin-laike-im-service",
        "importance_base": 80,
    },
    {
        "platform": "抖音",
        "source_name": "抖音开放平台-行业角色认证",
        "item_type": "规则文档",
        "url": "https://developer.open-douyin.com/docs/resource/zh-CN/developer/join/Role",
        "importance_base": 86,
    },
]

MEITUAN_NEWS_URL = "https://www.meituan.com/news/"
AUTHORITATIVE_SOURCES = [
    {"平台": "抖音", "来源": "抖音开放平台-生活服务与服务商文档", "类型": "官方能力文档 / 接入规则", "口径": "每日监控能力与接入变化", "稳定性": "高"},
    {"平台": "抖音", "来源": "抖音开放平台-行业角色认证", "类型": "官方规则文档", "口径": "每日监控服务商准入与角色规则变化", "稳定性": "高"},
    {"平台": "美团", "来源": "美团新闻中心", "类型": "官方新闻 / 生态动作", "口径": "仅在存在明确官方日期时纳入动态", "稳定性": "高"},
    {"平台": "政策辅助", "来源": "国家市场监督管理总局", "类型": "监管政策", "口径": "用于人工复核平台相关政策变化", "稳定性": "高"},
    {"平台": "公告辅助", "来源": "港交所披露易（美团）", "类型": "上市公司公告", "口径": "用于人工复核财报与重大公告", "稳定性": "高"},
]


def _fetch(url: str) -> str:
    return requests.get(url, headers=HEADERS, timeout=20).text


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_title(html_text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if match:
        return _strip_html(match.group(1))
    match = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', html_text, re.IGNORECASE)
    if match:
        return _strip_html(match.group(1))
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.IGNORECASE | re.DOTALL)
    if match:
        return _strip_html(match.group(1))
    return "未知标题"


def _extract_meta_description(html_text: str) -> str:
    match = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html_text, re.IGNORECASE)
    if not match:
        match = re.search(r"<meta[^>]+content=\"([^\"]+)\"[^>]+name=\"description\"", html_text, re.IGNORECASE)
    return _strip_html(match.group(1)) if match else ""


def _extract_explicit_date(html_text: str) -> tuple[str, str]:
    metadata_patterns = [
        (r'"updated_at":"(20\d{2}-\d{2}-\d{2})T', "页面元数据日期"),
        (r'"saved_time":"(20\d{2}-\d{2}-\d{2})T', "页面元数据日期"),
        (r'"created_at":"(20\d{2}-\d{2}-\d{2})T', "页面元数据日期"),
        (r'"published_at":"(20\d{2}-\d{2}-\d{2})T', "页面元数据日期"),
    ]
    for pattern, label in metadata_patterns:
        match = re.search(pattern, html_text)
        if not match:
            continue
        candidate = match.group(1)
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
            return candidate, label
        except ValueError:
            continue
    return "", "监控日期"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _doc_fingerprint(page: str) -> str:
    title = _extract_title(page)
    summary = _extract_meta_description(page)
    related_links = sorted(set(re.findall(r"/docs/resource/zh-CN/[^\"']+", page)))[:20]
    return _content_hash(" | ".join([title, summary, *related_links]))


def _importance_from_text(base: int, text: str) -> int:
    score = base
    keywords = {
        "服务商": 8,
        "商家": 6,
        "规则": 7,
        "政策": 7,
        "开放平台": 7,
        "接入": 6,
        "团购": 5,
        "本地生活": 7,
        "到店": 7,
        "经营": 6,
        "IM": 4,
        "支付": 4,
    }
    for word, bonus in keywords.items():
        if word in text:
            score += bonus
    return min(score, 100)


def _snapshot_exists(item_id: str, content_hash: str, event_date: str, source_name: str) -> bool:
    data = load_data()
    snapshots = data["competitor_snapshots"]
    if snapshots.empty:
        return False
    mask = (
        (snapshots["item_id"] == item_id)
        & (snapshots["source_name"] == source_name)
        & (snapshots["event_date"] == event_date)
    )
    if content_hash:
        mask = mask & (snapshots["content_hash"] == content_hash)
    return bool(mask.any())


def _latest_snapshot_map() -> dict[str, pd.Series]:
    data = load_data()
    snapshots = data["competitor_snapshots"]
    if snapshots.empty:
        return {}
    snapshots = snapshots.sort_values("checked_at", ascending=False)
    latest: dict[str, pd.Series] = {}
    for _, row in snapshots.iterrows():
        key = str(row["item_id"])
        if key not in latest:
            latest[key] = row
    return latest


def _record_snapshot(row: dict[str, Any]) -> None:
    if _snapshot_exists(str(row["item_id"]), str(row["content_hash"]), str(row["event_date"]), str(row["source_name"])):
        return
    append_record(
        "competitor_snapshots",
        {
            "snapshot_id": f"CSN-{abs(hash(str(row['item_id']) + str(row['checked_at']))) % 1000000}",
            **row,
        },
    )


def _extract_meituan_news() -> list[dict[str, Any]]:
    html_text = _fetch(MEITUAN_NEWS_URL)
    matches = re.findall(r'<a[^>]+href="(/news/NN\d+)"[^>]*>(.*?)</a>', html_text, re.DOTALL)
    rows: list[dict[str, Any]] = []
    cutoff = datetime.now() - timedelta(days=30)
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for href, block in matches[:12]:
        title_match = re.search(r"<h2[^>]*>(.*?)</h2>", block, re.DOTALL)
        desc_match = re.search(r'opacity-65[^>]*>(.*?)</div>', block, re.DOTALL)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", block)
        category_match = re.search(r"<span[^>]*>(.*?)</span>", block, re.DOTALL)
        if not date_match:
            continue
        event_date = date_match.group(1)
        try:
            if datetime.strptime(event_date, "%Y-%m-%d") < cutoff:
                continue
        except ValueError:
            continue
        title = _strip_html(title_match.group(1)) if title_match else "美团新闻动态"
        summary = _strip_html(desc_match.group(1)) if desc_match else "官方新闻动态"
        category = _strip_html(category_match.group(1)) if category_match else "官方新闻"
        url = f"https://www.meituan.com{href}"
        rows.append(
            {
                "platform": "美团",
                "item_type": "官方新闻",
                "item_id": url,
                "title": title,
                "url": url,
                "event_date": event_date,
                "importance": _importance_from_text(72, f"{title} {summary} {category}"),
                "summary": f"{category} · {summary}",
                "content_hash": "",
                "status": "近30天动态",
                "checked_at": checked_at,
                "source_name": "美团新闻中心",
                "date_quality": "明确日期",
            }
        )
    return rows


def seed_last_30_days_baseline() -> pd.DataFrame:
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows: list[dict[str, Any]] = []

    for source in DOUYIN_DOC_SOURCES:
        page = _fetch(source["url"])
        title = _extract_title(page)
        summary = _extract_meta_description(page) or "近30天能力基线，用于持续观察抖音生活服务与服务商相关能力变化。"
        row = {
            "platform": source["platform"],
            "item_type": f"{source['item_type']}-基线",
            "item_id": source["url"],
            "title": title,
            "url": source["url"],
            "event_date": checked_at[:10],
            "importance": _importance_from_text(source["importance_base"], f"{title} {summary}"),
            "summary": summary,
            "content_hash": _doc_fingerprint(page),
            "status": "近30天能力基线",
            "checked_at": checked_at,
            "source_name": source["source_name"],
            "date_quality": "监控日期",
        }
        rows.append(row)
        _record_snapshot(row)

    for row in _extract_meituan_news():
        rows.append(row)
        _record_snapshot(row)

    frame = pd.DataFrame(rows)
    return frame.sort_values(["importance", "event_date"], ascending=[False, False], kind="stable") if not frame.empty else frame


def refresh_competitor_updates() -> pd.DataFrame:
    latest = _latest_snapshot_map()
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows: list[dict[str, Any]] = []

    for source in DOUYIN_DOC_SOURCES:
        page = _fetch(source["url"])
        title = _extract_title(page)
        summary = _extract_meta_description(page) or "官方能力页监控，用于观察平台能力和接入规则变化。"
        content_hash = _doc_fingerprint(page)
        item_id = source["url"]
        previous = latest.get(item_id)
        status = "发现变更" if previous is None or str(previous["content_hash"]) != content_hash else "已监控"
        importance = _importance_from_text(source["importance_base"], f"{title} {summary}")
        explicit_date, date_quality = _extract_explicit_date(page)
        row = {
            "platform": source["platform"],
            "item_type": source["item_type"],
            "item_id": item_id,
            "title": title,
            "url": source["url"],
            "event_date": explicit_date or checked_at[:10],
            "importance": importance,
            "summary": summary,
            "content_hash": content_hash,
            "status": status,
            "checked_at": checked_at,
            "source_name": source["source_name"],
            "date_quality": date_quality if explicit_date else "监控日期",
        }
        rows.append(row)
        if status == "发现变更":
            _record_snapshot(row)

    for baseline_row in _extract_meituan_news():
        item_id = baseline_row["item_id"]
        previous = latest.get(item_id)
        status = "新增动态" if previous is None else "已收录"
        row = {
            **baseline_row,
            "status": status,
            "checked_at": checked_at,
        }
        rows.append(row)
        if status == "新增动态":
            _record_snapshot(row)

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    result = result.sort_values(["importance", "event_date"], ascending=[False, False], kind="stable")
    return result
