from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "exports"


def _ensure_export_dir() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _find_browser() -> str:
    candidates = [
        os.getenv("CHROME_BIN"),
        os.getenv("GOOGLE_CHROME_BIN"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise RuntimeError("当前环境没有可用的 Chrome / Chromium，暂时无法生成 PNG 海报。")


def export_dataframe(frame: pd.DataFrame, slug: str, title: str) -> dict[str, str]:
    _ensure_export_dir()
    stamp = _timestamp()
    csv_path = EXPORT_DIR / f"{slug}_{stamp}.csv"
    html_path = EXPORT_DIR / f"{slug}_{stamp}.html"

    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      font-family: "Noto Sans CJK SC", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Heiti SC", sans-serif;
      background: #f8fafc;
      color: #111827;
      margin: 0;
      padding: 32px;
    }}
    .wrap {{
      max-width: 1200px;
      margin: 0 auto;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 20px;
      padding: 28px;
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
    }}
    p {{
      color: #6b7280;
      margin: 0 0 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      border: 1px solid #e5e7eb;
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }}
    th {{
      background: #eff6ff;
      color: #1d4ed8;
    }}
    tr:nth-child(even) td {{
      background: #fafafa;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{title}</h1>
    <p>导出时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    {frame.to_html(index=False, border=0)}
  </div>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
    return {"csv": str(csv_path), "html": str(html_path)}


def export_competitor_poster(frame: pd.DataFrame, title: str = "竞品动态海报") -> dict[str, str]:
    _ensure_export_dir()
    stamp = _timestamp()
    html_path = EXPORT_DIR / f"competitor_poster_{stamp}.html"
    png_path = EXPORT_DIR / f"competitor_poster_{stamp}.png"

    top = frame.head(6).copy()
    card_count = len(top)
    grid_columns = 1 if card_count <= 1 else 2
    poster_height = min(max(980, 700 + ((card_count + 1) // 2) * 340), 2200)
    cards = []
    for _, row in top.iterrows():
        cards.append(
            f"""
            <div class="card">
              <div class="meta">
                <span class="platform">{row['platform']}</span>
                <span class="status">{row['status']}</span>
                <span class="score">重要性 {int(row['importance'])}</span>
              </div>
              <div class="headline">{row['title']}</div>
              <div class="summary">{row['summary']}</div>
              <div class="footer">{row['source_name']} · {row['event_date']} · {row.get('date_quality', '监控日期')}</div>
            </div>
            """
        )
    if not cards:
        cards.append(
            """
            <div class="card empty">
              <div class="headline">今日暂无可展示动态</div>
              <div class="summary">当前没有满足海报口径的竞品动态，建议稍后刷新或查看能力监控列表。</div>
              <div class="footer">系统提示 · 当前导出为空海报</div>
            </div>
            """
        )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      font-family: "Noto Sans CJK SC", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Heiti SC", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(245,158,11,0.24), transparent 24%),
        radial-gradient(circle at top right, rgba(6,182,212,0.18), transparent 20%),
        linear-gradient(180deg, #0f172a 0%, #1f2937 100%);
      color: #fff;
    }}
    .poster {{
      width: 1400px;
      min-height: {poster_height}px;
      margin: 0 auto;
      padding: 56px 54px 64px;
      box-sizing: border-box;
      position: relative;
      overflow: hidden;
    }}
    .kicker {{
      font-size: 18px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: #fbbf24;
      font-weight: 700;
    }}
    h1 {{
      margin: 12px 0 12px;
      font-size: 58px;
      line-height: 1.08;
      letter-spacing: -0.03em;
      font-family: "Noto Sans CJK SC", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Heiti SC", sans-serif;
    }}
    .desc {{
      max-width: 980px;
      color: #d1d5db;
      font-size: 24px;
      line-height: 1.6;
      margin-bottom: 28px;
    }}
    .topline {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
      margin-bottom: 28px;
    }}
    .topbox {{
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 24px;
      padding: 20px 22px;
      backdrop-filter: blur(8px);
    }}
    .topbox .label {{
      color: #cbd5e1;
      font-size: 18px;
      margin-bottom: 8px;
    }}
    .topbox .value {{
      font-size: 34px;
      font-weight: 800;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat({grid_columns}, minmax(0, 1fr));
      gap: 18px;
    }}
    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.92) 100%);
      color: #111827;
      border-radius: 26px;
      padding: 22px 24px;
      min-height: 220px;
      box-shadow: 0 18px 40px rgba(15,23,42,0.16);
    }}
    .card.empty {{
      min-height: 160px;
    }}
    .meta {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }}
    .meta span {{
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 700;
    }}
    .platform {{ background: #fff7ed; color: #b45309; }}
    .status {{ background: #ecfeff; color: #0f766e; }}
    .score {{ background: #eff6ff; color: #1d4ed8; }}
    .headline {{
      font-size: 28px;
      line-height: 1.35;
      font-weight: 800;
      margin-bottom: 12px;
    }}
    .summary {{
      color: #4b5563;
      font-size: 19px;
      line-height: 1.65;
      min-height: 88px;
    }}
    .footer {{
      color: #6b7280;
      font-size: 16px;
      margin-top: 18px;
    }}
  </style>
</head>
<body>
  <div class="poster">
    <div class="kicker">Gaode Competitive Watch</div>
    <h1>{title}</h1>
    <div class="desc">基于抖音开放平台、美团新闻中心等权威源生成，优先展示发布日期明确的动态，并按和高德本地生活/到店业务的相关重要性排序。</div>
    <div class="topline">
      <div class="topbox"><div class="label">高优先级动态</div><div class="value">{int((frame['importance'] >= 85).sum())} 条</div></div>
      <div class="topbox"><div class="label">覆盖平台</div><div class="value">{frame['platform'].nunique()} 个</div></div>
      <div class="topbox"><div class="label">导出时间</div><div class="value" style="font-size:24px;">{datetime.now().strftime("%Y-%m-%d %H:%M")}</div></div>
    </div>
    <div class="grid">
      {"".join(cards)}
    </div>
  </div>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")

    chrome = _find_browser()
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size=1400,{poster_height}",
            f"--screenshot={png_path}",
            html_path.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return {"png": str(png_path)}
