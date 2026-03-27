from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-cream: #f8f6f1;
            --ink: #111827;
            --muted: #6b7280;
            --card: rgba(255,255,255,0.88);
            --line: rgba(226,232,240,0.95);
            --amber: #d97706;
            --teal: #0f766e;
            --slate: #334155;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(245, 158, 11, 0.18), transparent 26%),
                radial-gradient(circle at 80% 0%, rgba(8, 145, 178, 0.12), transparent 22%),
                linear-gradient(180deg, #faf7f0 0%, #eef3f8 46%, #f7fafc 100%);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1440px;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }
        div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
            gap: 0.7rem;
        }
        div[data-testid="column"] > div {
            height: 100%;
        }
        div[data-testid="stMarkdown"] {
            margin-bottom: 0.15rem;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fff8ef 0%, #f7fafc 100%);
            border-right: 1px solid #eceff5;
            min-width: 310px;
            max-width: 310px;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0.55rem;
        }
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stSelectbox label {
            font-weight: 600;
        }
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.26rem;
        }
        section[data-testid="stSidebar"] .stButton button {
            justify-content: flex-start;
            text-align: left;
            min-height: 38px;
            border-radius: 11px;
            padding: 0.28rem 0.8rem;
            font-size: 0.96rem;
        }
        section[data-testid="stSidebar"] .stButton {
            margin-top: 0;
            margin-bottom: 0.12rem;
        }
        section[data-testid="stSidebar"] .stButton button p {
            white-space: normal;
            overflow: visible;
            text-overflow: clip;
            line-height: 1.25;
            width: 100%;
        }
        section[data-testid="stSidebar"] .stMarkdown p {
            margin-bottom: 0.25rem;
            font-size: 0.9rem;
            line-height: 1.35;
        }
        section[data-testid="stSidebar"] .stMarkdown strong {
            font-size: 0.88rem;
            color: #475569;
        }
        section[data-testid="stSidebar"] .sidebar-group-label {
            font-size: 0.84rem;
            font-weight: 700;
            color: #7c8594;
            letter-spacing: 0.02em;
            margin: 1rem 0 0.7rem;
            padding-left: 0.15rem;
            line-height: 1.2;
        }
        section[data-testid="stSidebar"] .stSelectbox label {
            font-size: 0.92rem;
        }
        section[data-testid="stSidebar"] .stSelectbox > div[data-baseweb="select"] > div {
            min-height: 40px;
            border-radius: 11px;
        }
        section[data-testid="stSidebar"] hr {
            margin: 0.55rem 0 0.65rem;
        }
        section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
            background: rgba(255,255,255,0.72);
        }
        section[data-testid="stSidebar"] .stButton button[kind="primary"] {
            box-shadow: 0 10px 20px rgba(15,23,42,0.08);
        }
        h1, h2, h3 {
            letter-spacing: -0.02em;
        }
        h1 {
            margin-top: 0.25rem;
            margin-bottom: 0.35rem;
            line-height: 1.18;
        }
        h1 + div[data-testid="stMarkdownContainer"] p {
            margin-top: 0.1rem;
            margin-bottom: 0.65rem;
        }
        p, li {
            line-height: 1.65;
        }
        div[data-testid="stMarkdownContainer"] ul {
            padding-left: 1.15rem;
            margin-bottom: 0.25rem;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(249,250,251,0.94) 100%);
            border: 1px solid rgba(226,232,240,0.95);
            padding: 11px 14px;
            border-radius: 18px;
            box-shadow: 0 10px 22px rgba(15,23,42,0.04);
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
        }
        div[data-testid="stMetricValue"] {
            line-height: 1.05;
        }
        .stButton button,
        .stDownloadButton button {
            width: 100%;
            min-height: 40px;
            border-radius: 12px;
            border: 1px solid #d7deea;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            color: #0f172a;
            font-weight: 700;
            box-shadow: 0 6px 16px rgba(15,23,42,0.04);
        }
        .stButton, .stDownloadButton {
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
        }
        .stButton button:hover,
        .stDownloadButton button:hover {
            border-color: #c6d0df;
            background: linear-gradient(180deg, #fffefc 0%, #f1f5f9 100%);
        }
        div[data-testid="stTabs"] button {
            border-radius: 12px 12px 0 0;
            font-weight: 700;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #0f172a;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(226,232,240,0.95);
            border-radius: 18px;
            overflow: hidden;
            background: rgba(255,255,255,0.78);
            box-shadow: 0 10px 24px rgba(15,23,42,0.04);
        }
        div[data-testid="stAlert"] {
            border-radius: 18px;
        }
        hr {
            border: 0;
            border-top: 1px solid rgba(226,232,240,0.95);
            margin: 0.8rem 0 1rem;
        }
        div[data-testid="stForm"] {
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(226,232,240,0.9);
            border-radius: 22px;
            padding: 0.75rem 0.85rem 0.2rem;
            margin-top: 0.4rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stSelectbox"],
        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stSlider"] {
            margin-bottom: 0.15rem;
        }
        [data-testid="stSelectbox"] > div,
        [data-testid="stTextInput"] > div,
        [data-testid="stNumberInput"] > div {
            border-radius: 14px;
        }
        .hero-card {
            position: relative;
            overflow: hidden;
            padding: 24px 24px 20px;
            border-radius: 24px;
            background:
                radial-gradient(circle at top right, rgba(250, 204, 21, 0.18), transparent 24%),
                linear-gradient(135deg, #0f172a 0%, #1e293b 52%, #334155 100%);
            color: #fff;
            box-shadow: 0 18px 34px rgba(17,24,39,0.15);
            margin-top: 0.15rem;
            margin-bottom: 18px;
        }
        .hero-card::after {
            content: "";
            position: absolute;
            inset: auto -6% -32% auto;
            width: 260px;
            height: 260px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(56,189,248,0.22) 0%, rgba(56,189,248,0) 70%);
        }
        .hero-kicker {
            color: #fdba74;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.8rem;
            display: block;
            line-height: 1.4;
            padding-top: 0.1rem;
            margin-bottom: 0.1rem;
        }
        .hero-title { font-size: 1.9rem; font-weight: 800; margin: 0.22rem 0 0.45rem; }
        .hero-desc { color: #dbe4ee; max-width: 860px; font-size: 0.94rem; }
        .hero-stats {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-top: 0.8rem;
            position: relative;
            z-index: 1;
        }
        .hero-stat {
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            backdrop-filter: blur(6px);
        }
        .hero-stat-label {
            color: #cbd5e1;
            font-size: 0.78rem;
            margin-bottom: 0.2rem;
        }
        .hero-stat-value {
            font-size: 1.05rem;
            font-weight: 800;
        }
        .panel {
            background: rgba(255,255,255,0.9);
            border: 1px solid rgba(226,232,240,0.95);
            padding: 14px 16px;
            border-radius: 18px;
            box-shadow: 0 8px 18px rgba(15,23,42,0.04);
            margin-bottom: 10px;
        }
        .panel-title { font-weight: 800; font-size: 1.05rem; margin-bottom: 0.35rem; color: #111827; }
        .panel-subtitle { color: #6b7280; font-size: 0.92rem; margin-bottom: 0.9rem; }
        .section-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.78) 0%, rgba(255,255,255,0.58) 100%);
            border: 1px solid rgba(229,231,235,0.9);
            border-radius: 22px;
            padding: 14px 14px 10px;
            margin-top: 8px;
            margin-bottom: 16px;
            box-shadow: 0 10px 22px rgba(15,23,42,0.035);
        }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 0.55rem;
        }
        .section-title {
            font-size: 1.02rem;
            font-weight: 800;
            color: var(--ink);
        }
        .section-note {
            color: var(--muted);
            font-size: 0.84rem;
            max-width: 720px;
        }
        .insight-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 26px;
        }
        .insight-card {
            background: linear-gradient(180deg, #fffdfa 0%, #ffffff 100%);
            border: 1px solid #f1e8d8;
            border-radius: 18px;
            padding: 13px 14px;
            box-shadow: 0 8px 18px rgba(15,23,42,0.03);
        }
        .insight-card.teal {
            border-color: #c7f0ea;
            background: linear-gradient(180deg, #f4fffd 0%, #ffffff 100%);
        }
        .insight-card.slate {
            border-color: #dce6f2;
            background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
        }
        .insight-kicker {
            color: var(--muted);
            font-size: 0.78rem;
            margin-bottom: 0.25rem;
        }
        .insight-value {
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--ink);
            margin-bottom: 0.35rem;
        }
        .insight-body {
            color: #4b5563;
            font-size: 0.88rem;
            line-height: 1.5;
        }
        .split-callout {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 10px;
        }
        .callout-dark {
            border-radius: 18px;
            padding: 14px 16px;
            color: #fff;
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
            box-shadow: 0 12px 24px rgba(17,24,39,0.1);
        }
        .callout-dark .muted {
            color: #d1d5db;
        }
        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 0.8rem;
        }
        .tag {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: #fff7ed;
            color: #9a3412;
            font-size: 0.8rem;
            margin-right: 0.3rem;
            border: 1px solid #fed7aa;
        }
        .section-caption { font-size: 0.86rem; color: #6b7280; margin-top: -0.25rem; margin-bottom: 0.75rem; }
        .funnel-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin: 0.2rem 0 0.55rem;
        }
        .funnel-step {
            background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.94) 100%);
            border: 1px solid rgba(226,232,240,0.95);
            border-radius: 16px;
            padding: 11px 12px;
            min-height: 76px;
        }
        .funnel-label {
            color: #64748b;
            font-size: 0.8rem;
            margin-bottom: 0.3rem;
        }
        .funnel-value {
            color: #0f172a;
            font-size: 1.45rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        .funnel-meta {
            color: #475569;
            font-size: 0.82rem;
        }
        .rank-list {
            display: flex;
            flex-direction: column;
            gap: 9px;
            margin-top: 0.1rem;
        }
        .rank-row {
            display: grid;
            grid-template-columns: 108px 1fr 58px;
            gap: 12px;
            align-items: center;
        }
        .rank-label {
            font-size: 0.88rem;
            color: #1f2937;
            font-weight: 600;
        }
        .rank-track {
            position: relative;
            height: 8px;
            border-radius: 999px;
            background: #e5edf6;
            overflow: hidden;
        }
        .rank-fill {
            position: absolute;
            inset: 0 auto 0 0;
            border-radius: 999px;
            background: linear-gradient(90deg, #f59e0b 0%, #0ea5a4 100%);
        }
        .rank-value {
            text-align: right;
            font-size: 0.85rem;
            color: #475569;
            font-weight: 700;
        }
        @media (max-width: 960px) {
            .hero-stats,
            .split-callout {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">每日经营看板</div>
            <div class="hero-title">先看重点客户，再看今天要推进的事</div>
            <div class="hero-desc">
                这里把找客户、出方案、跟进服务、推进续费这些常用动作放到了一起。
                你可以先处理高意向客户和高风险续费，再回头看批量任务和行业变化。
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-label">今天先看</div>
                    <div class="hero-stat-value">高意向客户</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">重点动作</div>
                    <div class="hero-stat-value">方案推进与回访</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">适合场景</div>
                    <div class="hero-stat-value">销售和客户管理</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
