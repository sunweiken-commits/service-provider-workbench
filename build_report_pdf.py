from __future__ import annotations

import re
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "高德服务商赋能体系可视化分析.md"
HTML_OUT = ROOT / "高德服务商赋能体系可视化分析.html"


def convert_mermaid_blocks(text: str) -> str:
    pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        content = match.group(1).strip()
        return f'\n<div class="mermaid">\n{content}\n</div>\n'

    return pattern.sub(repl, text)


def build_html(markdown_text: str) -> str:
    markdown_text = convert_mermaid_blocks(markdown_text)

    body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        output_format="html5",
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>高德服务商赋能体系可视化分析</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: "neutral",
      securityLevel: "loose",
      flowchart: {{ useMaxWidth: true, htmlLabels: true }},
      themeVariables: {{
        primaryColor: "#fff4e5",
        primaryTextColor: "#1f2937",
        primaryBorderColor: "#f59e0b",
        lineColor: "#9ca3af",
        secondaryColor: "#ecfeff",
        tertiaryColor: "#f8fafc"
      }}
    }});
  </script>
  <style>
    @page {{
      size: A4;
      margin: 16mm 14mm 16mm 14mm;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      background: #f5f7fb;
      color: #1f2937;
      font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.65;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    .page {{
      max-width: 980px;
      margin: 0 auto;
      background: #ffffff;
      padding: 28px 32px 40px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 28px;
      line-height: 1.25;
      color: #111827;
    }}
    h2 {{
      margin-top: 34px;
      padding: 10px 14px;
      font-size: 22px;
      background: linear-gradient(90deg, #fff3e0 0%, #fff9f0 100%);
      border-left: 5px solid #f59e0b;
      border-radius: 8px;
      page-break-after: avoid;
    }}
    h3 {{
      margin-top: 24px;
      font-size: 18px;
      color: #92400e;
      page-break-after: avoid;
    }}
    p, li, blockquote {{
      font-size: 13.5px;
    }}
    ul, ol {{
      padding-left: 22px;
    }}
    blockquote {{
      margin: 14px 0;
      padding: 10px 14px;
      background: #fffbeb;
      border-left: 4px solid #f59e0b;
      color: #78350f;
      border-radius: 8px;
    }}
    hr {{
      border: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, #d1d5db, transparent);
      margin: 28px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0 20px;
      table-layout: fixed;
      page-break-inside: auto;
    }}
    th, td {{
      border: 1px solid #dbe3ef;
      padding: 8px 10px;
      vertical-align: top;
      text-align: left;
      font-size: 12px;
      word-break: break-word;
    }}
    th {{
      background: #eef6ff;
      color: #1e3a8a;
      font-weight: 700;
    }}
    tr:nth-child(even) td {{
      background: #fafcff;
    }}
    code {{
      background: #f3f4f6;
      border-radius: 4px;
      padding: 1px 4px;
      font-size: 12px;
    }}
    pre {{
      background: #0f172a;
      color: #e5e7eb;
      border-radius: 10px;
      padding: 14px;
      overflow: auto;
      font-size: 12px;
    }}
    .meta {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin: 18px 0 20px;
    }}
    .meta-card {{
      background: linear-gradient(180deg, #fff8ef 0%, #fffdf8 100%);
      border: 1px solid #f8d7a5;
      border-radius: 12px;
      padding: 12px 14px;
    }}
    .meta-card strong {{
      display: block;
      margin-bottom: 4px;
      font-size: 12px;
      color: #92400e;
    }}
    .meta-card span {{
      font-size: 13px;
      color: #374151;
    }}
    .cover {{
      padding: 18px 0 26px;
      border-bottom: 1px solid #e5e7eb;
      margin-bottom: 10px;
    }}
    .cover p {{
      margin: 8px 0 0;
      color: #4b5563;
    }}
    .toc {{
      margin: 18px 0 26px;
      padding: 16px 18px;
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
    }}
    .toc ul {{
      margin: 8px 0 0;
    }}
    .mermaid {{
      margin: 18px auto 24px;
      padding: 8px;
      background: #fcfcfd;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      page-break-inside: avoid;
    }}
    a {{
      color: #1d4ed8;
      text-decoration: none;
    }}
    .small {{
      color: #6b7280;
      font-size: 12px;
    }}
    @media print {{
      body {{
        background: #fff;
      }}
      .page {{
        max-width: none;
        margin: 0;
        padding: 0;
      }}
      h2, h3, table, blockquote, .mermaid {{
        page-break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="cover">
      <h1>高德服务商赋能体系可视化分析</h1>
      <p>聚焦“平台如何赋能服务商拓商、促付费、做交付、带续费”的完整分析稿</p>
      <div class="meta">
        <div class="meta-card"><strong>适用场景</strong><span>平台策略讨论、产品规划、服务商生态设计、商业化推进</span></div>
        <div class="meta-card"><strong>版本日期</strong><span>2026-03-27</span></div>
        <div class="meta-card"><strong>核心定位</strong><span>把服务商建设成高德的本地商家增长伙伴</span></div>
      </div>
      <div class="toc">
        <strong>目录</strong>
        <div class="small">以下内容包含平台对比、服务商工具体系、服务体系、商业产品、KPI 与阶段建议。</div>
      </div>
    </section>
    {body}
  </div>
</body>
</html>
"""


def main() -> None:
    markdown_text = SOURCE.read_text(encoding="utf-8")
    html = build_html(markdown_text)
    HTML_OUT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
