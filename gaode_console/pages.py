from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from gaode_console.competitor_monitor import AUTHORITATIVE_SOURCES, DOUYIN_DOC_SOURCES, refresh_competitor_updates, seed_last_30_days_baseline
from gaode_console.exports import export_competitor_poster, export_dataframe
from gaode_console.storage import append_operation_log, append_record, update_record
from gaode_console.styles import render_hero


PAGES = ["首页总览", "平台首页", "任务中心", "统一时间线", "操作日志", "导出中心", "拓商工具", "销售工具", "商家与交付", "沟通协同", "批量交付", "续费工具", "平台管理台", "竞品动态", "MVP 架构说明"]
PAGE_LABELS = {
    "首页总览": "我的工作台",
    "平台首页": "平台概览",
    "任务中心": "今日待办",
    "统一时间线": "跟进记录",
    "操作日志": "变更记录",
    "导出中心": "报表导出",
    "拓商工具": "找客户",
    "销售工具": "方案报价",
    "商家与交付": "客户服务",
    "沟通协同": "沟通记录",
    "批量交付": "批量任务",
    "续费工具": "续费跟进",
    "平台管理台": "服务商管理",
    "竞品动态": "行业动态",
    "MVP 架构说明": "系统说明",
}

ROLE_LABELS = ["平台运营", "服务商运营", "BD", "客户成功", "只读访客"]

ROLE_PAGE_ACCESS = {
    "平台运营": PAGES,
    "服务商运营": ["首页总览", "任务中心", "统一时间线", "导出中心", "拓商工具", "销售工具", "商家与交付", "沟通协同", "批量交付", "续费工具", "竞品动态", "MVP 架构说明"],
    "BD": ["首页总览", "平台首页", "任务中心", "统一时间线", "导出中心", "拓商工具", "销售工具", "沟通协同", "平台管理台", "竞品动态", "MVP 架构说明"],
    "客户成功": ["首页总览", "平台首页", "任务中心", "统一时间线", "导出中心", "商家与交付", "沟通协同", "续费工具", "竞品动态", "MVP 架构说明"],
    "只读访客": ["首页总览", "平台首页", "统一时间线", "导出中心", "竞品动态", "MVP 架构说明"],
}

ROLE_ACTION_ACCESS = {
    "平台运营": {"edit_lead", "edit_merchant", "edit_partner", "edit_communication", "add_communication", "edit_complaint", "edit_visit", "add_visit", "add_platform_action", "export"},
    "服务商运营": {"edit_lead", "edit_merchant", "edit_communication", "add_communication", "export"},
    "BD": {"edit_lead", "add_visit", "edit_visit", "add_platform_action", "export"},
    "客户成功": {"edit_merchant", "edit_communication", "add_communication", "add_platform_action", "export"},
    "只读访客": set(),
}


def panel(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="panel">
          <div class="panel-title">{title}</div>
          <div style="color:#4b5563;margin-top:0.35rem;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_open(title: str, note: str = "") -> None:
    note_html = f'<div class="section-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="section-shell">
          <div class="section-header">
            <div>
              <div class="section-title">{title}</div>
              {note_html}
            </div>
          </div>
        """,
        unsafe_allow_html=True,
    )


def section_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def priority_sort_key(series: pd.Series) -> pd.Series:
    order = {"高": 0, "中": 1, "低": 2}
    return series.map(order).fillna(9)


def show_table_or_empty(frame: pd.DataFrame, empty_message: str, *, use_container_width: bool = True, hide_index: bool = True) -> None:
    if frame.empty:
        st.info(empty_message)
        return
    st.dataframe(frame, use_container_width=use_container_width, hide_index=hide_index)


def prepare_display_frame(frame: pd.DataFrame, specs: list[tuple]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=[spec[1] for spec in specs])
    display: dict[str, pd.Series] = {}
    for spec in specs:
        source = spec[0]
        label = spec[1]
        formatter = spec[2] if len(spec) > 2 else None
        series = frame[source]
        if formatter:
            series = series.map(formatter)
        display[label] = series
    return pd.DataFrame(display)


def render_stage_cards(stages: list[dict[str, str | int]]) -> None:
    html = ['<div class="funnel-grid">']
    for stage in stages:
        meta = stage.get("meta", "")
        html.append(
            f'<div class="funnel-step"><div class="funnel-label">{stage["label"]}</div><div class="funnel-value">{stage["value"]}</div><div class="funnel-meta">{meta}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_rank_bars(rows: list[dict[str, float | int | str]], max_value: float = 100.0) -> None:
    html = ['<div class="rank-list">']
    safe_max = max(max_value, 1)
    for row in rows:
        value = float(row["value"])
        width = min(max((value / safe_max) * 100, 0), 100)
        html.append(
            f'<div class="rank-row"><div class="rank-label">{row["label"]}</div><div class="rank-track"><div class="rank-fill" style="width:{width:.1f}%"></div></div><div class="rank-value">{row["display"]}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_insight_cards(cards: list[dict[str, str]]) -> None:
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        tone = card.get("tone", "")
        with col:
            st.markdown(
                f"""
                <div class="insight-card {tone}">
                  <div class="insight-kicker">{card['label']}</div>
                  <div class="insight-value">{card['value']}</div>
                  <div class="insight-body">{card['body']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


@st.dialog("海报预览", width="large")
def show_competitor_poster_dialog(png_path: str) -> None:
    st.image(png_path, caption="行业动态海报", use_container_width=True)
    with open(png_path, "rb") as file:
        st.download_button("下载 PNG 海报", data=file.read(), file_name=Path(png_path).name, mime="image/png", use_container_width=True)
    if st.button("关闭海报", use_container_width=True):
        st.session_state["show_competitor_poster_dialog"] = False
        st.rerun()


def render_competitor_markdown_list(frame: pd.DataFrame, date_label: str, empty_message: str) -> None:
    if frame.empty:
        st.info(empty_message)
        return
    for _, row in frame.iterrows():
        st.markdown(
            "\n".join(
                [
                    f"#### {row['platform']} | {row['title']}",
                    f"- {date_label}：`{row['event_date']}`",
                    f"- 状态：`{row['status']}`",
                    f"- 重要性：`{int(row['importance'])}`",
                    f"- 摘要：{row['summary']}",
                    f"- 来源：[{row['source_name']}]({row['url']})",
                ]
            )
        )
        st.divider()


def render_unified_competitor_summary(yesterday_updates: pd.DataFrame, yesterday_priority: pd.DataFrame, monitored_updates: pd.DataFrame, yesterday: str) -> None:
    st.markdown("### 今日摘要")
    if yesterday_updates.empty:
        st.markdown(f"- `{yesterday}` 没有抓到发布日期明确的竞品动态。")
    else:
        focus = yesterday_priority if not yesterday_priority.empty else yesterday_updates.head(3)
        st.markdown(f"- `{yesterday}` 共抓到 `{len(yesterday_updates)}` 条明确日期动态，优先关注以下内容。")
        for _, row in focus.iterrows():
            st.markdown(f"- `{row['platform']}`：**{row['title']}**。{row['summary']} [查看来源]({row['url']})")

    if monitored_updates.empty:
        st.markdown("- 当前没有确认到可信的能力监控变更。")
    else:
        st.markdown(f"- 另有 `{len(monitored_updates)}` 条可信监控变更，建议同步关注规则或能力页变化。")
        for _, row in monitored_updates.head(2).iterrows():
            st.markdown(f"- `{row['platform']}`监控变更：**{row['title']}**。状态 `{row['status']}`。 [查看来源]({row['url']})")


def set_default_selection(data: dict[str, pd.DataFrame]) -> None:
    st.session_state.setdefault("selected_lead", data["leads"]["merchant"].iloc[0])
    st.session_state.setdefault("selected_merchant", data["merchants"]["merchant"].iloc[0])
    st.session_state.setdefault("selected_partner", data["partners"]["partner"].iloc[0])
    st.session_state.setdefault("current_role", "平台运营")


def jump_to(page: str, **kwargs: str) -> None:
    st.session_state["nav_page"] = page
    for key, value in kwargs.items():
        st.session_state[key] = value


def current_role() -> str:
    return st.session_state.get("current_role", "平台运营")


def can_access_page(page: str) -> bool:
    return page in ROLE_PAGE_ACCESS.get(current_role(), [])


def can_do(action: str) -> bool:
    return action in ROLE_ACTION_ACCESS.get(current_role(), set())


def permission_hint(action: str) -> None:
    if not can_do(action):
        st.info(f"当前角色：{current_role()}。此操作需要更高权限。")


def build_timeline(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []

    for _, row in data["lead_activity"].iterrows():
        merchant = data["leads"].loc[data["leads"]["lead_id"] == row["lead_id"], "merchant"]
        rows.append(
            {
                "time": str(row["date"]),
                "type": "线索跟进",
                "entity": merchant.iloc[0] if not merchant.empty else str(row["lead_id"]),
                "owner": str(row["actor"]),
                "status": str(row["stage"]),
                "summary": str(row["note"]),
            }
        )

    for _, row in data["communications"].iterrows():
        rows.append(
            {
                "time": str(row["last_time"]),
                "type": "沟通记录",
                "entity": str(row["merchant"]),
                "owner": str(row["owner"]),
                "status": str(row["status"]),
                "summary": f"{row['channel']} / {row['direction']} / {row['summary']}",
            }
        )

    for _, row in data["complaints"].iterrows():
        rows.append(
            {
                "time": str(row["created_at"]),
                "type": "客诉工单",
                "entity": str(row["merchant"]),
                "owner": str(row["partner"]),
                "status": str(row["status"]),
                "summary": f"{row['issue_type']} / 优先级 {row['priority']}",
            }
        )

    for _, row in data["joint_visits"].iterrows():
        rows.append(
            {
                "time": str(row["visit_date"]),
                "type": "联合拜访",
                "entity": str(row["merchant"]),
                "owner": str(row["owner"]),
                "status": str(row["status"]),
                "summary": f"{row['partner']} / {row['city']}",
            }
        )

    for _, row in data["renewal"].iterrows():
        rows.append(
            {
                "time": str(row["expiry_date"]),
                "type": "续费预警",
                "entity": str(row["merchant"]),
                "owner": "系统",
                "status": str(row["risk_level"]),
                "summary": f"{row['risk_reason']} / 下一步：{row['next_action']}",
            }
        )

    if "platform_actions" in data:
        for _, row in data["platform_actions"].iterrows():
            rows.append(
                {
                    "time": str(row["action_time"]),
                    "type": "平台动作",
                    "entity": str(row["target"]),
                    "owner": str(row["owner"]),
                    "status": str(row["action_type"]),
                    "summary": str(row["summary"]),
                }
            )

    timeline = pd.DataFrame(rows)
    return timeline.sort_values("time", ascending=False, kind="stable") if not timeline.empty else timeline


def build_tasks(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []

    for _, row in data["leads"].iterrows():
        if row["status"] != "已签约":
            rows.append(
                {
                    "task_type": "线索跟进",
                    "entity": str(row["merchant"]),
                    "owner": str(row["owner"]),
                    "priority": "高" if int(row["intent_score"]) >= 90 else "中",
                    "status": str(row["status"]),
                    "next_step": "更新诊断/报价并继续推进",
                }
            )

    for _, row in data["communications"].iterrows():
        if row["status"] in ["待回访", "处理中"]:
            rows.append(
                {
                    "task_type": "沟通回访",
                    "entity": str(row["merchant"]),
                    "owner": str(row["owner"]),
                    "priority": "高" if row["channel"] == "电话" else "中",
                    "status": str(row["status"]),
                    "next_step": "尽快完成回访并更新摘要",
                }
            )

    for _, row in data["complaints"].iterrows():
        if row["status"] != "已关闭":
            rows.append(
                {
                    "task_type": "客诉处理",
                    "entity": str(row["merchant"]),
                    "owner": str(row["partner"]),
                    "priority": str(row["priority"]),
                    "status": str(row["status"]),
                    "next_step": "推进判责、复盘或关闭工单",
                }
            )

    for _, row in data["joint_visits"].iterrows():
        if row["status"] != "已完成":
            rows.append(
                {
                    "task_type": "联合拜访",
                    "entity": str(row["merchant"]),
                    "owner": str(row["owner"]),
                    "priority": "高",
                    "status": str(row["status"]),
                    "next_step": "确认拜访计划并准备方案",
                }
            )

    for _, row in data["renewal"].iterrows():
        rows.append(
            {
                "task_type": "续费推进",
                "entity": str(row["merchant"]),
                "owner": "客户成功",
                "priority": "高" if row["risk_level"] == "高" else "中",
                "status": str(row["risk_level"]),
                "next_step": str(row["next_action"]),
            }
        )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["priority_rank"] = priority_sort_key(frame["priority"])
    frame = frame.sort_values(["priority_rank", "task_type", "entity"], ascending=[True, True, True], kind="stable")
    return frame.drop(columns=["priority_rank"])


def render_home(data: dict[str, pd.DataFrame]) -> None:
    leads = data["leads"]
    merchants = data["merchants"]
    renewal = data["renewal"]

    render_hero()
    render_insight_cards(
        [
            {"label": "增长焦点", "value": f"{len(leads)} 条潜在线索", "body": "先把高意向线索转成可成交诊断，再推进首充。"},
            {"label": "经营规模", "value": f"{len(merchants)} 家已服务商家", "body": "当前后台已覆盖服务商从拓商到续费的主要链路。", "tone": "slate"},
            {"label": "续费风险", "value": f"{int((renewal['risk_level'] == '高').sum())} 家高风险", "body": "优先组织复盘会，展示到店归因和预算建议。", "tone": "teal"},
        ]
    )
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("潜在线索数", len(leads), "+12%")
    col2.metric("已服务商家数", len(merchants), "+3")
    col3.metric("本月预计投放预算", f"{merchants['monthly_budget'].sum():,}", "+18%")
    col4.metric("高风险续费商家", int((renewal["risk_level"] == "高").sum()), "-1")

    section_open("今天先处理什么", "先把最可能成交和最需要续费跟进的客户挑出来。")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="panel-title">客户推进进度</div><div class="section-caption">先把最值得推进的客户挑出来。</div>', unsafe_allow_html=True)
        render_stage_cards(
            [
                {"label": "潜在线索", "value": 58, "meta": "今天可继续筛选"},
                {"label": "已沟通", "value": 34, "meta": "等待继续推进"},
                {"label": "方案中", "value": 19, "meta": "适合催确认"},
                {"label": "已签约", "value": 11, "meta": "进入服务阶段"},
                {"label": "续费意向", "value": 6, "meta": "优先安排复盘"},
            ]
        )
        st.markdown('<div class="panel-title">城市机会分布</div>', unsafe_allow_html=True)
        city_scores = leads.groupby("city", as_index=False)["intent_score"].mean().sort_values("intent_score", ascending=False)
        render_rank_bars(
            [{"label": row["city"], "value": row["intent_score"], "display": f"{row['intent_score']:.0f}"} for _, row in city_scores.iterrows()],
            max_value=100,
        )
    with right:
        st.markdown(
            """
            <div class="split-callout">
              <div class="callout-dark">
                <div class="panel-title" style="color:#fff;">今天建议优先处理</div>
                <div class="muted">优先跟进“安心口腔门诊”，用电话留资和预约组件做首单切入。</div>
                <div class="chip-row">
                  <span class="tag">高意向</span>
                  <span class="tag">医疗行业</span>
                  <span class="tag">适合联合拜访</span>
                </div>
              </div>
              <div class="panel">
                <div class="panel-title">下一步建议</div>
                <div style="color:#4b5563;">高风险续费客户优先安排复盘会，用到店表现和竞对差异推动续费。</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    section_close()

    section_open("常用入口", "把最常用的页面放在这里，减少来回找。")
    c1, c2, c3 = st.columns(3)
    if c1.button("去看重点客户", use_container_width=True):
        jump_to("拓商工具", selected_lead="安心口腔门诊")
        st.rerun()
    if c2.button("去看客户服务", use_container_width=True):
        jump_to("商家与交付", selected_merchant="悦己丽人皮肤管理")
        st.rerun()
    if c3.button("去看服务商管理", use_container_width=True):
        jump_to("平台管理台", selected_partner="沪上增长伙伴")
        st.rerun()
    section_close()


def render_platform_home(data: dict[str, pd.DataFrame]) -> None:
    partners = data["partners"]
    complaints = data["complaints"]
    incentives = data["partner_incentives"]
    communications = data["communications"]
    leads = data["leads"]
    merchants = data["merchants"]

    st.title("平台概览")
    st.caption("这里更适合平台管理同学看整体服务商情况、风险和协同效率。")
    render_insight_cards(
        [
            {"label": "服务商生态", "value": f"{len(partners)} 家活跃服务商", "body": "看认证通过率、等级分布和重点城市覆盖。"},
            {"label": "治理压力", "value": f"{int((complaints['status'] == '待处理').sum())} 单待处理客诉", "body": "先处理高优先级工单，避免影响商家体验。", "tone": "slate"},
            {"label": "协同效率", "value": f"{int((communications['status'].isin(['待回访','处理中'])).sum())} 条待推进沟通", "body": "电话、企业微信和平台 IM 需要统一留痕和回访。", "tone": "teal"},
        ]
    )
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("活跃服务商", len(partners))
    c2.metric("待处理客诉", int((complaints["status"] == "待处理").sum()))
    c3.metric("本月激励支出", f"{int(incentives['total_bonus'].sum()):,}")
    c4.metric("待回访沟通", int((communications["status"].isin(["待回访", "处理中"])).sum()))

    section_open("平台重点", "先看服务商生态，再看风险和协同事项。")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="panel-title">平台核心经营面板</div>', unsafe_allow_html=True)
        render_stage_cards(
            [
                {"label": "潜在线索", "value": len(leads), "meta": "等待继续跟进"},
                {"label": "服务中客户", "value": int(merchants["service_status"].isin(["服务中", "投放中"]).sum()), "meta": "需要稳定交付"},
                {"label": "高风险续费", "value": int((merchants["renewal_risk"] == "高").sum()), "meta": "适合优先复盘"},
                {"label": "已认证服务商", "value": int((partners["cert_status"] == "已认证").sum()), "meta": "可正常承接业务"},
            ]
        )
    with right:
        st.markdown(
            """
            <div class="callout-dark">
              <div class="panel-title" style="color:#fff;">平台今日关注</div>
              <div class="muted">优先盯 3 件事：高客单行业联合拜访、待处理客诉、待回访沟通。</div>
              <div class="chip-row">
                <span class="tag">联合拜访</span>
                <span class="tag">客诉治理</span>
                <span class="tag">沟通效率</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        panel("为什么要盯这里", "沟通是否顺畅，往往会直接影响成交推进和后续续费。")
    section_close()

    section_open("最近协同情况", "最近的沟通和跟进记录，能帮助判断哪些客户需要平台一起介入。")
    recent_communications = communications.sort_values("last_time", ascending=False)
    show_table_or_empty(
        prepare_display_frame(
            recent_communications,
            [
                ("merchant", "客户"),
                ("partner", "服务商"),
                ("channel", "渠道"),
                ("status", "状态"),
                ("owner", "负责人"),
                ("last_time", "最近时间"),
                ("summary", "沟通摘要"),
            ],
        ),
        "最近还没有协同记录。",
    )
    section_close()


def render_task_center(data: dict[str, pd.DataFrame]) -> None:
    tasks = build_tasks(data)
    st.title("今日待办")
    st.caption("把今天要跟进的客户、沟通、客诉、拜访和续费事项放到一起。")

    c1, c2, c3 = st.columns(3)
    task_type = c1.selectbox("任务类型", ["全部"] + sorted(tasks["task_type"].unique().tolist()))
    priority = c2.selectbox("优先级", ["全部"] + sorted(tasks["priority"].unique().tolist()))
    owner = c3.selectbox("负责人", ["全部"] + sorted(tasks["owner"].unique().tolist()))

    filtered = tasks.copy()
    if task_type != "全部":
        filtered = filtered[filtered["task_type"] == task_type]
    if priority != "全部":
        filtered = filtered[filtered["priority"] == priority]
    if owner != "全部":
        filtered = filtered[filtered["owner"] == owner]

    render_insight_cards(
        [
            {"label": "当前待办", "value": f"{len(filtered)} 条", "body": "按优先级和负责人切开后，先处理最影响成交和续费的任务。"},
            {"label": "高优先级", "value": f"{int((filtered['priority'] == '高').sum())} 条", "body": "高优先级通常来自高意向线索、客诉和联合拜访。", "tone": "slate"},
            {"label": "处理中", "value": f"{int(filtered['status'].isin(['处理中', '待处理', '待回访']).sum())} 条", "body": "这部分适合做每日运营晨会和跟进复盘。", "tone": "teal"},
        ]
    )
    section_open("待办列表", "适合早会排期和日常追踪，优先把高优先级和处理中事项拉出来。")
    show_table_or_empty(
        prepare_display_frame(
            filtered,
            [
                ("task_type", "事项类型"),
                ("entity", "对象"),
                ("owner", "负责人"),
                ("priority", "优先级"),
                ("status", "当前状态"),
                ("next_step", "下一步"),
            ],
        ),
        "当前筛选条件下没有待办。",
    )
    section_close()
    c1, c2 = st.columns(2)
    if c1.button("查看跟进来龙去脉", use_container_width=True):
        jump_to("统一时间线")
        st.rerun()
    if c2.button("查看谁改过什么", use_container_width=True):
        jump_to("操作日志")
        st.rerun()


def render_timeline(data: dict[str, pd.DataFrame]) -> None:
    timeline = build_timeline(data)
    st.title("跟进记录")
    st.caption("把客户、沟通、拜访、续费这些事情放到一条时间线上，方便回看。")

    c1, c2 = st.columns(2)
    event_type = c1.selectbox("事件类型", ["全部"] + sorted(timeline["type"].unique().tolist()))
    entity = c2.selectbox("对象", ["全部"] + sorted(timeline["entity"].unique().tolist()))

    filtered = timeline.copy()
    if event_type != "全部":
        filtered = filtered[filtered["type"] == event_type]
    if entity != "全部":
        filtered = filtered[filtered["entity"] == entity]

    show_table_or_empty(
        prepare_display_frame(
            filtered,
            [
                ("time", "时间"),
                ("type", "记录类型"),
                ("entity", "对象"),
                ("owner", "负责人"),
                ("status", "状态"),
                ("summary", "内容"),
            ],
        ),
        "当前筛选条件下没有跟进记录。",
    )


def render_operation_logs(data: dict[str, pd.DataFrame]) -> None:
    logs = data["operation_logs"].sort_values("time", ascending=False)
    st.title("变更记录")
    st.caption("这里记录谁改了什么、什么时候改的，适合排查和复盘。")

    c1, c2 = st.columns(2)
    target_type = c1.selectbox("对象类型", ["全部"] + sorted(logs["target_type"].unique().tolist()))
    actor = c2.selectbox("操作人", ["全部"] + sorted(logs["actor"].unique().tolist()))

    filtered = logs.copy()
    if target_type != "全部":
        filtered = filtered[filtered["target_type"] == target_type]
    if actor != "全部":
        filtered = filtered[filtered["actor"] == actor]

    show_table_or_empty(
        prepare_display_frame(
            filtered,
            [
                ("time", "时间"),
                ("actor", "操作人"),
                ("target_type", "对象类型"),
                ("target", "对象"),
                ("action", "动作"),
                ("detail", "说明"),
            ],
        ),
        "当前筛选条件下没有变更记录。",
    )


def render_exports(data: dict[str, pd.DataFrame]) -> None:
    st.title("报表导出")
    st.caption("把常用结果导出来，方便发给同事、老板或客户。")

    task_frame = build_tasks(data)
    timeline_frame = build_timeline(data)
    merchant_report = data["merchant_monthly_report"].copy()
    partner_report = data["partners"].copy()

    tabs = st.tabs(["任务中心", "统一时间线", "商家月报", "服务商评估"])

    with tabs[0]:
        show_table_or_empty(task_frame, "当前没有可导出的待办。")
        if st.button("导出任务中心", use_container_width=True):
            paths = export_dataframe(task_frame, "task_center", "高德服务商增长工作台-任务中心")
            st.success(f"已导出：CSV {paths['csv']} ｜ HTML {paths['html']}")

    with tabs[1]:
        show_table_or_empty(timeline_frame, "当前没有可导出的跟进记录。")
        if st.button("导出统一时间线", use_container_width=True):
            paths = export_dataframe(timeline_frame, "timeline", "高德服务商增长工作台-统一时间线")
            st.success(f"已导出：CSV {paths['csv']} ｜ HTML {paths['html']}")

    with tabs[2]:
        show_table_or_empty(
            prepare_display_frame(
                merchant_report,
                [
                    ("merchant", "客户"),
                    ("month", "月份"),
                    ("exposure", "曝光", lambda value: f"{int(value):,}"),
                    ("clicks", "点击", lambda value: f"{int(value):,}"),
                    ("calls", "电话", lambda value: f"{int(value):,}"),
                    ("navigations", "导航", lambda value: f"{int(value):,}"),
                    ("arrivals", "到店", lambda value: f"{int(value):,}"),
                    ("roi", "ROI", lambda value: f"{float(value):.2f}"),
                ],
            ),
            "当前没有可导出的商家月报。",
        )
        if st.button("导出商家月报", use_container_width=True):
            paths = export_dataframe(merchant_report, "merchant_report", "高德服务商增长工作台-商家月报")
            st.success(f"已导出：CSV {paths['csv']} ｜ HTML {paths['html']}")

    with tabs[3]:
        show_table_or_empty(
            prepare_display_frame(
                partner_report,
                [
                    ("partner", "服务商"),
                    ("type", "类型"),
                    ("level", "等级"),
                    ("cert_status", "认证状态"),
                    ("city_scope", "服务城市"),
                    ("active_merchants", "服务中客户"),
                    ("monthly_revenue", "月收入", lambda value: f"{int(value):,}"),
                    ("complaint_rate", "客诉率"),
                ],
            ),
            "当前没有可导出的服务商评估。",
        )
        if st.button("导出服务商评估", use_container_width=True):
            paths = export_dataframe(partner_report, "partner_assessment", "高德服务商增长工作台-服务商评估")
            st.success(f"已导出：CSV {paths['csv']} ｜ HTML {paths['html']}")


def render_leads(data: dict[str, pd.DataFrame]) -> None:
    leads = data["leads"].copy()
    activities = data["lead_activity"]
    st.title("找客户")
    st.caption("先找到更值得跟进的客户，再决定怎么聊、怎么报方案。")
    leads["priority_rank"] = 100 - leads["intent_score"]
    leads = leads.sort_values(["priority_rank", "status", "city"], ascending=[True, True, True], kind="stable").drop(columns=["priority_rank"])

    section_open("先筛一遍", "先收窄范围，再看值得跟进的客户。")
    c1, c2, c3 = st.columns(3)
    selected_city = c1.selectbox("城市", ["全部"] + sorted(leads["city"].unique().tolist()))
    selected_status = c2.selectbox("跟进状态", ["全部"] + sorted(leads["status"].unique().tolist()))
    min_score = c3.slider("最低意向分", 60, 100, 80)
    if selected_city != "全部":
        leads = leads[leads["city"] == selected_city]
    if selected_status != "全部":
        leads = leads[leads["status"] == selected_status]
    leads = leads[leads["intent_score"] >= min_score]
    section_close()

    section_open("候选客户", "先从列表里挑出今天要推进的人。")
    show_table_or_empty(
        prepare_display_frame(
            leads,
            [
                ("merchant", "客户"),
                ("city", "城市"),
                ("industry", "行业"),
                ("status", "跟进状态"),
                ("intent_score", "意向分", lambda value: f"{int(value)}"),
                ("owner", "负责人"),
                ("opportunity", "机会点"),
                ("budget_band", "预算区间"),
            ],
        ),
        "当前筛选条件下没有合适的客户。",
    )
    options = leads["merchant"].tolist() if not leads.empty else data["leads"]["merchant"].tolist()
    if st.session_state.get("selected_lead") not in options:
        st.session_state["selected_lead"] = options[0]
    merchant = st.selectbox("选择线索商家", options, key="selected_lead")
    section_close()
    selected = data["leads"][data["leads"]["merchant"] == merchant].iloc[0]
    selected_activity = activities[activities["lead_id"] == selected["lead_id"]].sort_values("date", ascending=False)

    section_open("客户详情", "看清楚机会点和下一步动作。")
    left, right = st.columns([1.1, 1])
    with left:
        panel(
            selected["merchant"],
            f"{selected['city']} · {selected['district']} · {selected['industry']}<br><br><strong>核心商机：</strong>{selected['opportunity']}<br><strong>建议下一步：</strong>先输出诊断，再结合 ROI 预估发起首轮报价。",
        )
    with right:
        render_rank_bars(
            [
                {"label": "门店完整度", "value": 56, "display": "56"},
                {"label": "素材质量", "value": 48, "display": "48"},
                {"label": "评论活跃度", "value": 35, "display": "35"},
                {"label": "竞对覆盖", "value": 81, "display": "81"},
                {"label": "首单概率", "value": 74, "display": "74"},
            ]
        )
    show_table_or_empty(selected_activity, "这位客户还没有跟进记录。")
    section_close()

    section_open("跟进与操作", "看完后直接更新或继续推进。")
    st.markdown('<div class="panel-title">这位客户的跟进记录</div>', unsafe_allow_html=True)
    lead_timeline = build_timeline(data)
    lead_timeline = lead_timeline[lead_timeline["entity"] == selected["merchant"]]
    show_table_or_empty(lead_timeline, "这位客户暂时还没有更多过程记录。")

    st.markdown('<div class="panel-title">更新客户跟进情况</div>', unsafe_allow_html=True)
    if can_do("edit_lead"):
        with st.form(f"lead_form_{selected['lead_id']}"):
            col1, col2, col3 = st.columns(3)
            new_status = col1.selectbox("跟进状态", ["待跟进", "已沟通", "方案中", "已签约"], index=["待跟进", "已沟通", "方案中", "已签约"].index(selected["status"]))
            new_owner = col2.selectbox("负责人", ["王晨", "李娜", "赵宇", "陈蕾", "周航"], index=["王晨", "李娜", "赵宇", "陈蕾", "周航"].index(selected["owner"]))
            new_note = col3.text_input("新增跟进记录", value="")
            submitted = st.form_submit_button("保存更新", use_container_width=True)
            if submitted:
                update_record("leads", "lead_id", selected["lead_id"], {"status": new_status, "owner": new_owner})
                if new_note.strip():
                    append_record(
                        "lead_activity",
                        {
                            "lead_id": selected["lead_id"],
                            "date": date.today().isoformat(),
                            "stage": new_status,
                            "actor": new_owner,
                            "note": new_note.strip(),
                        },
                    )
                append_operation_log(
                    actor=new_owner,
                    target_type="线索",
                    target=selected["merchant"],
                    action="更新线索状态",
                    detail=f"状态改为 {new_status}，负责人改为 {new_owner}",
                    time_str=f"{date.today().isoformat()} 12:40",
                )
                st.success("线索状态已保存。")
                st.rerun()
    else:
        permission_hint("edit_lead")

    c1, c2 = st.columns(2)
    if c1.button("去做方案报价", use_container_width=True):
        jump_to("销售工具", selected_lead=merchant)
        st.rerun()
    if c2.button("申请一起拜访客户", use_container_width=True):
        jump_to("平台管理台", selected_partner="沪上增长伙伴")
        st.rerun()
    section_close()


def render_sales(data: dict[str, pd.DataFrame]) -> None:
    packages = data["packages"]
    keyword_insights = data["keyword_insights"]
    default_name = st.session_state.get("selected_lead", "安心口腔门诊")

    st.title("方案报价")
    st.caption("把客户能听懂、销售好推进的方案和报价放在一起。")
    section_open("先定预算和方案", "先看适合的套餐，再调整预算和折扣。")
    left, right = st.columns([1, 1.2])
    with left:
        st.dataframe(packages, use_container_width=True, hide_index=True)
        budget = st.slider("月预算", 3000, 30000, 12000, step=1000)
        industry = st.selectbox("行业", ["汽车服务", "餐饮", "丽人", "医疗", "运动健身"])
        factor = {"汽车服务": 1.0, "餐饮": 0.9, "丽人": 1.1, "医疗": 1.25, "运动健身": 1.05}[industry]
        estimated_leads = int((budget / 120) * factor)
        c1, c2 = st.columns(2)
        c1.metric("预计月线索量", estimated_leads)
        c2.metric("预计到店量", int(estimated_leads * 0.38))
    with right:
        st.dataframe(keyword_insights, use_container_width=True, hide_index=True)
        merchant_name = st.text_input("商家名称", default_name)
        selected_package = st.selectbox("推荐套餐", packages["package"].tolist())
        selected_price = int(packages.loc[packages["package"] == selected_package, "price"].iloc[0])
        discount = st.slider("折扣率", 70, 100, 90)
        quote = int(selected_price * discount / 100)
        panel("当前报价", f"<strong>商家：</strong>{merchant_name}<br><strong>套餐：</strong>{selected_package}<br><strong>成交价：</strong>{quote:,} 元 / 月<br>建议搭配首充扶持和 30 天复盘说明，一起讲清楚。")
        if st.button("去看客户服务情况", use_container_width=True):
            jump_to("商家与交付", selected_merchant=merchant_name if merchant_name in data["merchants"]["merchant"].tolist() else data["merchants"]["merchant"].iloc[0])
            st.rerun()
    section_close()


def render_delivery(data: dict[str, pd.DataFrame]) -> None:
    merchants = data["merchants"].copy()
    monthly_report = data["merchant_monthly_report"]
    st.title("客户服务")
    st.caption("把客户当前表现、服务状态和下一步动作放在一页里。")
    risk_order = {"高": 0, "中": 1, "低": 2}
    merchants["risk_rank"] = merchants["renewal_risk"].map(risk_order).fillna(9)
    merchants = merchants.sort_values(["risk_rank", "monthly_budget", "arrivals"], ascending=[True, False, False], kind="stable").drop(columns=["risk_rank"])

    section_open("先选客户", "先按负责人过滤，再打开重点客户。")
    selected_owner = st.selectbox("服务商负责人", ["全部"] + sorted(merchants["owner"].unique().tolist()))
    if selected_owner != "全部":
        merchants = merchants[merchants["owner"] == selected_owner]
    show_table_or_empty(
        prepare_display_frame(
            merchants,
            [
                ("merchant", "客户"),
                ("city", "城市"),
                ("service_status", "服务状态"),
                ("package", "当前套餐"),
                ("monthly_budget", "月预算", lambda value: f"{int(value):,}"),
                ("arrivals", "到店"),
                ("renewal_risk", "续费风险"),
                ("owner", "负责人"),
            ],
        ),
        "当前筛选条件下没有客户。",
    )

    options = merchants["merchant"].tolist()
    if st.session_state.get("selected_merchant") not in options:
        st.session_state["selected_merchant"] = options[0]
    merchant = st.selectbox("选择商家查看详情", options, key="selected_merchant")
    section_close()
    selected = merchants[merchants["merchant"] == merchant].iloc[0]
    report_row = monthly_report[monthly_report["merchant"] == merchant].iloc[0]

    section_open("服务表现", "先看结果，再决定下一步。")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("曝光", f"{int(selected['exposure']):,}")
    c2.metric("点击", f"{int(selected['clicks']):,}")
    c3.metric("电话", f"{int(selected['calls']):,}")
    c4.metric("到店", f"{int(selected['arrivals']):,}")

    left, right = st.columns(2)
    with left:
        panel("当前服务情况", f"<strong>商家：</strong>{merchant}<br><strong>当前套餐：</strong>{selected['package']}<br><strong>服务状态：</strong>{selected['service_status']}<br><strong>估算 ROI：</strong>{report_row['roi']}")
    with right:
        exposure = max(int(selected["exposure"]), 1)
        render_stage_cards(
            [
                {"label": "曝光", "value": f"{int(selected['exposure']):,}", "meta": "看到门店的人次"},
                {"label": "点击", "value": f"{int(selected['clicks']):,}", "meta": f"点击率 {selected['clicks'] / exposure:.1%}"},
                {"label": "电话/导航", "value": f"{int(selected['calls'] + selected['navigations']):,}", "meta": "进入咨询或到店决策"},
                {"label": "到店", "value": f"{int(selected['arrivals']):,}", "meta": f"到店转化 {selected['arrivals'] / exposure:.1%}"},
            ]
        )
    panel("本月小结", f"{merchant} 在 {report_row['month']} 形成电话 {int(report_row['calls'])}、导航 {int(report_row['navigations'])}、到店 {int(report_row['arrivals'])}。建议{'推进续费或升级' if report_row['roi'] >= 1 else '先优化词包、素材和承接链路，再考虑加预算'}。")
    section_close()

    section_open("服务记录与下一步", "更新状态、看历史、继续推进。")
    st.markdown('<div class="panel-title">这位客户的服务记录</div>', unsafe_allow_html=True)
    merchant_timeline = build_timeline(data)
    merchant_timeline = merchant_timeline[merchant_timeline["entity"] == merchant]
    show_table_or_empty(merchant_timeline, "这位客户暂时还没有更多服务记录。")

    st.markdown('<div class="panel-title">更新客户服务状态</div>', unsafe_allow_html=True)
    if can_do("edit_merchant"):
        with st.form(f"merchant_form_{selected['merchant_id']}"):
            col1, col2, col3 = st.columns(3)
            new_service_status = col1.selectbox("服务状态", ["待认领", "待首充", "方案待确认", "服务中", "投放中"], index=["待认领", "待首充", "方案待确认", "服务中", "投放中"].index(selected["service_status"]))
            new_package = col2.selectbox("服务套餐", data["packages"]["package"].tolist(), index=data["packages"]["package"].tolist().index(selected["package"]))
            new_risk = col3.selectbox("续费风险", ["低", "中", "高"], index=["低", "中", "高"].index(selected["renewal_risk"]))
            submitted = st.form_submit_button("保存状态", use_container_width=True)
            if submitted:
                update_record(
                    "merchants",
                    "merchant_id",
                    selected["merchant_id"],
                    {"service_status": new_service_status, "package": new_package, "renewal_risk": new_risk},
                )
                append_operation_log(
                    actor=selected["owner"],
                    target_type="商家",
                    target=merchant,
                    action="更新商家服务状态",
                    detail=f"服务状态={new_service_status}，套餐={new_package}，风险={new_risk}",
                    time_str=f"{date.today().isoformat()} 12:45",
                )
                st.success("商家服务状态已保存。")
                st.rerun()
    else:
        permission_hint("edit_merchant")

    c1, c2 = st.columns(2)
    if c1.button("去看批量任务", use_container_width=True):
        jump_to("批量交付")
        st.rerun()
    if c2.button("去看续费跟进", use_container_width=True):
        jump_to("续费工具", selected_merchant=merchant)
        st.rerun()
    section_close()


def render_communications(data: dict[str, pd.DataFrame]) -> None:
    comms = data["communications"].copy()
    status_order = {"待回访": 0, "处理中": 1, "已跟进": 2, "已完成": 3}
    comms["status_rank"] = comms["status"].map(status_order).fillna(9)
    comms = comms.sort_values(["status_rank", "last_time"], ascending=[True, False], kind="stable").drop(columns=["status_rank"])
    st.title("沟通记录")
    st.caption("把和客户的电话、微信、平台消息、拜访记录集中放在这里。")

    section_open("先筛沟通记录", "先按客户、渠道和状态过滤，再处理最需要回访的沟通。")
    c1, c2, c3 = st.columns(3)
    merchant_filter = c1.selectbox("按商家筛选", ["全部"] + sorted(comms["merchant"].unique().tolist()), key="comm_merchant_filter")
    channel_filter = c2.selectbox("按渠道筛选", ["全部"] + sorted(comms["channel"].unique().tolist()), key="comm_channel_filter")
    status_filter = c3.selectbox("按状态筛选", ["全部"] + sorted(comms["status"].unique().tolist()), key="comm_status_filter")

    filtered = comms.copy()
    if merchant_filter != "全部":
        filtered = filtered[filtered["merchant"] == merchant_filter]
    if channel_filter != "全部":
        filtered = filtered[filtered["channel"] == channel_filter]
    if status_filter != "全部":
        filtered = filtered[filtered["status"] == status_filter]
    section_close()

    section_open("查看与更新", "左边看记录，右边看沟通建议，下面可以直接更新。")
    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="panel-title">最近沟通情况</div>', unsafe_allow_html=True)
        show_table_or_empty(
            prepare_display_frame(
                filtered,
                [
                    ("merchant", "客户"),
                    ("channel", "渠道"),
                    ("direction", "方向"),
                    ("status", "状态"),
                    ("owner", "负责人"),
                    ("last_time", "最近时间"),
                    ("summary", "沟通摘要"),
                ],
            ),
            "当前筛选条件下没有沟通记录。",
        )
    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">日常最常见的沟通方式</div>
                <div style="color:#4b5563;margin-top:0.35rem;">
                    现在服务商和商家最常见还是通过 4 种方式沟通：
                    <br><strong>1. 电话：</strong>最快，适合首触达、催跟进、线索承接。
                    <br><strong>2. 企业微信 / 微信：</strong>适合发方案、报价、日常协同。
                    <br><strong>3. 平台IM：</strong>适合沉淀在线沟通和留痕，但很多平台还不够强。
                    <br><strong>4. 线下拜访：</strong>适合高客单、连锁总部、需要官方背书的客户。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        panel("小建议", "先把关键沟通记清楚，后面复盘和续费会轻松很多。")
    section_close()

    section_open("处理这条沟通", "先更新当前沟通，再补充新的跟进内容。")
    st.markdown('<div class="panel-title">更新这条沟通记录</div>', unsafe_allow_html=True)
    options = filtered["comm_id"].tolist() if not filtered.empty else comms["comm_id"].tolist()
    comm_id = st.selectbox("选择沟通记录", options, key="comm_detail")
    selected = comms[comms["comm_id"] == comm_id].iloc[0]
    if can_do("edit_communication"):
        with st.form(f"comm_form_{comm_id}"):
            col1, col2, col3 = st.columns(3)
            new_channel = col1.selectbox("沟通渠道", ["电话", "企业微信", "平台IM", "线下拜访"], index=["电话", "企业微信", "平台IM", "线下拜访"].index(selected["channel"]))
            new_status = col2.selectbox("沟通状态", ["待回访", "处理中", "已跟进", "已完成"], index=["待回访", "处理中", "已跟进", "已完成"].index(selected["status"]))
            new_summary = col3.text_input("沟通摘要", value=selected["summary"])
            submitted = st.form_submit_button("保存记录", use_container_width=True)
            if submitted:
                update_record("communications", "comm_id", comm_id, {"channel": new_channel, "status": new_status, "summary": new_summary})
                append_operation_log(
                    actor=selected["owner"],
                    target_type="沟通",
                    target=selected["merchant"],
                    action="更新沟通记录",
                    detail=f"渠道={new_channel}，状态={new_status}",
                    time_str=f"{date.today().isoformat()} 12:50",
                )
                st.success("沟通记录已保存。")
                st.rerun()
    else:
        permission_hint("edit_communication")

    st.markdown('<div class="panel-title">新增一条沟通记录</div>', unsafe_allow_html=True)
    if can_do("add_communication"):
        with st.form("new_comm_form"):
            col1, col2, col3 = st.columns(3)
            merchant = col1.selectbox("商家", sorted(data["merchants"]["merchant"].unique().tolist()))
            partner = col2.selectbox("服务商", sorted(data["partners"]["partner"].unique().tolist()))
            channel = col3.selectbox("渠道", ["电话", "企业微信", "平台IM", "线下拜访"])
            col4, col5, col6 = st.columns(3)
            direction = col4.selectbox("方向", ["外呼", "商家发起", "双向沟通", "联合拜访"])
            status = col5.selectbox("状态", ["待回访", "处理中", "已跟进", "已完成"])
            owner = col6.selectbox("负责人", ["王晨", "李娜", "赵宇", "陈蕾", "周航"])
            summary = st.text_input("沟通摘要")
            submitted = st.form_submit_button("新增记录", use_container_width=True)
            if submitted:
                next_id = f"CM-{400 + len(comms) + 1}"
                append_record(
                    "communications",
                    {
                        "comm_id": next_id,
                        "merchant": merchant,
                        "partner": partner,
                        "channel": channel,
                        "direction": direction,
                        "status": status,
                        "owner": owner,
                        "last_time": f"{date.today().isoformat()} 12:00",
                        "summary": summary or "待补充",
                    },
                )
                append_operation_log(
                    actor=owner,
                    target_type="沟通",
                    target=merchant,
                    action="新增沟通记录",
                    detail=f"渠道={channel}，状态={status}",
                    time_str=f"{date.today().isoformat()} 12:55",
                )
                st.success("沟通记录已新增。")
                st.rerun()
    else:
        permission_hint("add_communication")

    c1, c2 = st.columns(2)
    if c1.button("回到找客户继续跟进", use_container_width=True):
        jump_to("拓商工具")
        st.rerun()
    if c2.button("去看平台整体情况", use_container_width=True):
        jump_to("平台首页")
        st.rerun()
    section_close()


def render_bulk_ops(data: dict[str, pd.DataFrame]) -> None:
    st.title("批量任务")
    st.caption("把容易批量处理的事情放在一起，减少重复操作。")
    stores = data["chain_stores"]
    tasks = data["bulk_tasks"].copy()
    progress_order = {"待执行": 0, "进行中": 1, "待审核": 2, "已完成": 3}
    tasks["progress_rank"] = tasks["progress"].map(progress_order).fillna(9)
    tasks = tasks.sort_values(["progress_rank", "eta"], ascending=[True, True], kind="stable").drop(columns=["progress_rank"])
    tab1, tab2, tab3 = st.tabs(["批量任务", "连锁门店", "素材分发"])
    with tab1:
        show_table_or_empty(
            prepare_display_frame(
                tasks,
                [
                    ("task_type", "任务类型"),
                    ("scope", "处理范围"),
                    ("progress", "进度"),
                    ("owner", "负责人"),
                    ("eta", "预计完成"),
                ],
            ),
            "当前没有批量任务。",
        )
        panel("这一块适合做什么", "适合集中处理认领、修改、审核这类重复工作。")
    with tab2:
        brand = st.selectbox("品牌", ["全部"] + sorted(stores["brand"].unique().tolist()), key="chain_brand")
        filtered = stores if brand == "全部" else stores[stores["brand"] == brand]
        show_table_or_empty(
            prepare_display_frame(
                filtered,
                [
                    ("brand", "品牌"),
                    ("store", "门店"),
                    ("city", "城市"),
                    ("status", "状态"),
                    ("completion", "完整度", lambda value: f"{int(value)}"),
                    ("material_status", "素材状态"),
                ],
            ),
            "当前没有符合条件的门店。",
        )
        panel("这一块适合做什么", "适合按品牌或区域统一处理门店信息。")
    with tab3:
        assets = pd.DataFrame({"素材名称": ["春季焕新主视觉", "口腔矫正案例海报", "门店环境图包", "品牌权益活动图"], "适用品牌": ["山海健身", "安心口腔", "全部", "全部"], "状态": ["已发布", "待审核", "已发布", "待分发"], "最近更新": ["2026-03-26", "2026-03-27", "2026-03-25", "2026-03-24"]})
        show_table_or_empty(assets, "当前没有可用素材。")
        panel("这一块适合做什么", "素材统一后，交付效率会更高，也更不容易出错。")


def render_renewal(data: dict[str, pd.DataFrame]) -> None:
    renewal = data["renewal"].copy()
    renewal["risk_rank"] = renewal["risk_level"].map({"高": 0, "中": 1, "低": 2}).fillna(9)
    renewal = renewal.sort_values(["risk_rank", "expiry_date"], ascending=[True, True], kind="stable").drop(columns=["risk_rank"])
    merchants = data["merchants"]
    st.title("续费跟进")
    st.caption("把快到期客户、复盘重点和增购机会放到一起看。")
    section_open("先看风险", "先处理快到期和风险高的客户，再看复盘和增购机会。")
    c1, c2, c3 = st.columns(3)
    c1.metric("30 天内到期商家", len(renewal))
    c2.metric("高风险商家", int((renewal["risk_level"] == "高").sum()))
    c3.metric("可增购商家", int((merchants["service_status"].isin(["投放中", "服务中"])).sum()))
    show_table_or_empty(
        prepare_display_frame(
            renewal,
            [
                ("merchant", "客户"),
                ("expiry_date", "到期时间"),
                ("risk_level", "风险等级"),
                ("next_action", "建议动作"),
                ("risk_reason", "风险原因"),
            ],
        ),
        "当前没有需要跟进的续费客户。",
    )
    section_close()

    section_open("生成续费沟通建议", "选一个客户，快速生成这次续费沟通的重点。")
    options = merchants["merchant"].tolist()
    if st.session_state.get("selected_merchant") not in options:
        st.session_state["selected_merchant"] = options[0]
    merchant = st.selectbox("选择商家生成复盘摘要", options, key="renewal_merchant")
    selected = merchants[merchants["merchant"] == merchant].iloc[0]
    roi = round((selected["arrivals"] * 280) / max(selected["monthly_budget"], 1), 2)
    panel("续费沟通建议", f"{merchant} 本月预算 {int(selected['monthly_budget']):,} 元，电话 {int(selected['calls'])}，导航 {int(selected['navigations'])}，到店 {int(selected['arrivals'])}，估算 ROI {roi}。建议先带着结果去沟通续费或升级。")
    section_close()


def render_platform_admin(data: dict[str, pd.DataFrame]) -> None:
    partners = data["partners"]
    incentives = data["partner_incentives"]
    complaints = data["complaints"]
    joint_visits = data["joint_visits"]
    training = data["training_records"]
    st.title("服务商管理")
    st.caption("这里更适合平台管理同学看服务商分层、激励、客诉和联合拜访。")

    section_open("先看整体情况", "先看服务商规模、风险和激励，再进入具体管理动作。")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("认证服务商", int((partners["cert_status"] == "已认证").sum()))
    c2.metric("战略/金牌服务商", int(partners["level"].isin(["战略", "金牌"]).sum()))
    c3.metric("待处理客诉", int((complaints["status"] == "待处理").sum()))
    c4.metric("本月激励支出", f"{int(incentives['total_bonus'].sum()):,}")
    section_close()

    section_open("服务商运营区", "在这里看分层、激励、客诉、联合拜访和培训情况。")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["服务商管理", "激励政策", "客诉治理", "联合拜访", "培训共创"])
    with tab1:
        show_table_or_empty(
            prepare_display_frame(
                partners,
                [
                    ("partner", "服务商"),
                    ("type", "类型"),
                    ("level", "等级"),
                    ("cert_status", "认证状态"),
                    ("city_scope", "服务城市"),
                    ("active_merchants", "服务中客户"),
                    ("monthly_revenue", "月收入", lambda value: f"{int(value):,}"),
                    ("complaint_rate", "客诉率"),
                ],
            ),
            "当前没有服务商信息。",
        )
        options = partners["partner"].tolist()
        if st.session_state.get("selected_partner") not in options:
            st.session_state["selected_partner"] = options[0]
        partner = st.selectbox("选择服务商查看详情", options, key="selected_partner")
        row = partners[partners["partner"] == partner].iloc[0]
        panel(row["partner"], f"<strong>类型：</strong>{row['type']}<br><strong>服务城市：</strong>{row['city_scope']}<br><strong>等级：</strong>{row['level']}<br><strong>认证状态：</strong>{row['cert_status']}")
        if can_do("edit_partner"):
            with st.form(f"partner_form_{row['partner']}"):
                col1, col2, col3 = st.columns(3)
                new_level = col1.selectbox("服务商等级", ["基础", "银牌", "金牌", "战略"], index=["基础", "银牌", "金牌", "战略"].index(row["level"]))
                new_cert = col2.selectbox("认证状态", ["待复审", "已认证"], index=["待复审", "已认证"].index(row["cert_status"]))
                new_type = col3.selectbox("服务商类型", ["拓店型", "增长型", "技术型"], index=["拓店型", "增长型", "技术型"].index(row["type"]))
                submitted = st.form_submit_button("保存服务商信息", use_container_width=True)
                if submitted:
                    update_record("partners", "partner", row["partner"], {"level": new_level, "cert_status": new_cert, "type": new_type})
                    append_operation_log(
                        actor="平台运营",
                        target_type="服务商",
                        target=row["partner"],
                        action="更新服务商信息",
                        detail=f"等级={new_level}，认证={new_cert}，类型={new_type}",
                        time_str=f"{date.today().isoformat()} 13:00",
                    )
                    st.success("服务商信息已保存。")
                    st.rerun()
        else:
            permission_hint("edit_partner")
        st.markdown('<div class="panel-title">服务商专属时间线</div>', unsafe_allow_html=True)
        partner_timeline = build_timeline(data)
        partner_related = (
            partner_timeline["summary"].str.contains(row["partner"], na=False)
            | (partner_timeline["owner"] == row["partner"])
        )
        show_table_or_empty(
            prepare_display_frame(
                partner_timeline[partner_related],
                [
                    ("time", "时间"),
                    ("type", "记录类型"),
                    ("entity", "对象"),
                    ("status", "状态"),
                    ("summary", "内容"),
                ],
            ),
            "这家服务商暂时还没有更多记录。",
        )
    with tab2:
        show_table_or_empty(
            prepare_display_frame(
                incentives,
                [
                    ("partner", "服务商"),
                    ("month", "月份"),
                    ("new_store_bonus", "拓店奖励", lambda value: f"{int(value):,}"),
                    ("first_charge_bonus", "首充奖励", lambda value: f"{int(value):,}"),
                    ("renewal_bonus", "续费奖励", lambda value: f"{int(value):,}"),
                    ("total_bonus", "合计", lambda value: f"{int(value):,}"),
                ],
            ),
            "当前没有激励数据。",
        )
        panel("查看重点", "这里更适合看返奖结构和重点服务商的激励变化。")
    with tab3:
        show_table_or_empty(
            prepare_display_frame(
                complaints,
                [
                    ("ticket_id", "工单号"),
                    ("partner", "服务商"),
                    ("merchant", "客户"),
                    ("issue_type", "问题类型"),
                    ("status", "处理状态"),
                    ("priority", "优先级"),
                    ("created_at", "创建时间"),
                ],
            ),
            "当前没有客诉工单。",
        )
        panel("查看重点", "先处理高优先级工单，再安排复盘和责任确认。")
        complaint_id = st.selectbox("选择客诉工单", complaints["ticket_id"].tolist(), key="complaint_detail")
        selected_complaint = complaints[complaints["ticket_id"] == complaint_id].iloc[0]
        if can_do("edit_complaint"):
            with st.form(f"complaint_form_{complaint_id}"):
                col1, col2 = st.columns(2)
                new_status = col1.selectbox("客诉状态", ["待处理", "处理中", "待复盘", "已关闭"], index=["待处理", "处理中", "待复盘", "已关闭"].index(selected_complaint["status"]))
                new_priority = col2.selectbox("优先级", ["高", "中", "低"], index=["高", "中", "低"].index(selected_complaint["priority"]))
                submitted = st.form_submit_button("保存客诉状态", use_container_width=True)
                if submitted:
                    update_record("complaints", "ticket_id", complaint_id, {"status": new_status, "priority": new_priority})
                    append_operation_log(
                        actor="平台运营",
                        target_type="客诉",
                        target=selected_complaint["merchant"],
                        action="更新客诉状态",
                        detail=f"状态={new_status}，优先级={new_priority}",
                        time_str=f"{date.today().isoformat()} 13:05",
                    )
                    st.success("客诉工单已更新。")
                    st.rerun()
        else:
            permission_hint("edit_complaint")
    with tab4:
        show_table_or_empty(
            prepare_display_frame(
                joint_visits,
                [
                    ("visit_id", "编号"),
                    ("partner", "服务商"),
                    ("merchant", "目标客户"),
                    ("city", "城市"),
                    ("owner", "平台负责人"),
                    ("status", "状态"),
                    ("visit_date", "拜访日期"),
                ],
            ),
            "当前没有联合拜访安排。",
        )
        panel("查看重点", "高客单客户、总部客户和重点城市客户，更适合一起拜访。")
        visit_id = st.selectbox("选择联合拜访", joint_visits["visit_id"].tolist(), key="visit_detail")
        selected_visit = joint_visits[joint_visits["visit_id"] == visit_id].iloc[0]
        if can_do("edit_visit"):
            with st.form(f"visit_form_{visit_id}"):
                col1, col2 = st.columns(2)
                new_visit_status = col1.selectbox("拜访状态", ["待确认", "已预约", "方案准备中", "已完成"], index=["待确认", "已预约", "方案准备中", "已完成"].index(selected_visit["status"]))
                new_owner = col2.text_input("平台负责人", value=selected_visit["owner"])
                submitted = st.form_submit_button("保存拜访状态", use_container_width=True)
                if submitted:
                    update_record("joint_visits", "visit_id", visit_id, {"status": new_visit_status, "owner": new_owner})
                    append_operation_log(
                        actor=new_owner,
                        target_type="联合拜访",
                        target=selected_visit["merchant"],
                        action="更新拜访状态",
                        detail=f"状态={new_visit_status}",
                        time_str=f"{date.today().isoformat()} 13:10",
                    )
                    st.success("联合拜访已更新。")
                    st.rerun()
        else:
            permission_hint("edit_visit")
        if can_do("add_visit"):
            with st.form("new_visit_form"):
                col1, col2, col3 = st.columns(3)
                partner = col1.selectbox("服务商", sorted(data["partners"]["partner"].unique().tolist()), key="new_visit_partner")
                merchant = col2.text_input("目标商家/品牌", key="new_visit_merchant")
                city = col3.text_input("城市", key="new_visit_city")
                col4, col5 = st.columns(2)
                owner = col4.text_input("平台BD", key="new_visit_owner")
                visit_date = col5.date_input("拜访日期", value=date.today(), key="new_visit_date")
                submitted = st.form_submit_button("提报联合拜访", use_container_width=True)
                if submitted:
                    next_id = f"JV-{100 + len(joint_visits) + 1}"
                    append_record(
                        "joint_visits",
                        {
                            "visit_id": next_id,
                            "partner": partner,
                            "merchant": merchant or "待补充",
                            "city": city or "待补充",
                            "owner": owner or "待分配",
                            "status": "待确认",
                            "visit_date": visit_date.isoformat(),
                        },
                    )
                    append_operation_log(
                        actor=owner or "待分配",
                        target_type="联合拜访",
                        target=merchant or "待补充",
                        action="提报联合拜访",
                        detail=f"服务商={partner}，城市={city or '待补充'}",
                        time_str=f"{date.today().isoformat()} 13:15",
                    )
                    st.success("联合拜访已提报。")
                    st.rerun()
        else:
            permission_hint("add_visit")
    with tab5:
        show_table_or_empty(
            prepare_display_frame(
                training,
                [
                    ("partner", "服务商"),
                    ("course", "课程"),
                    ("completion", "完成情况"),
                    ("score", "分数", lambda value: f"{int(value)}"),
                    ("last_date", "最近时间"),
                ],
            ),
            "当前没有培训记录。",
        )
        panel("查看重点", "这里更适合看培训完成情况和后续共创安排。")
    section_close()

    section_open("平台动作", "需要平台介入时，可以直接在这里发起动作并写入记录。")
    st.markdown('<div class="panel-title">平台动作入口</div>', unsafe_allow_html=True)
    if can_do("add_platform_action"):
        with st.form("platform_action_form"):
            col1, col2, col3 = st.columns(3)
            action_type = col1.selectbox("动作类型", ["发起联合拜访", "发起续费复盘", "发起专项激励", "发起问题排查"])
            target = col2.text_input("动作对象", value="安心口腔门诊")
            owner = col3.text_input("平台负责人", value="平台运营-李想")
            summary = st.text_input("动作说明", value="请服务商在本周内完成复盘并回传结果。")
            submitted = st.form_submit_button("发起平台动作", use_container_width=True)
            if submitted:
                actions = data["platform_actions"]
                next_id = f"PA-{500 + len(actions) + 1}"
                append_record(
                    "platform_actions",
                    {
                        "action_id": next_id,
                        "action_time": f"{date.today().isoformat()} 12:30",
                        "action_type": action_type,
                        "target": target or "待补充",
                        "owner": owner or "待分配",
                        "summary": summary or "待补充",
                    },
                )
                append_operation_log(
                    actor=owner or "待分配",
                    target_type="平台动作",
                    target=target or "待补充",
                    action=action_type,
                    detail=summary or "待补充",
                    time_str=f"{date.today().isoformat()} 13:20",
                )
                st.success("平台动作已发起，并写入统一时间线。")
                st.rerun()
    else:
        permission_hint("add_platform_action")
    section_close()


def render_competitor_dynamics(data: dict[str, pd.DataFrame]) -> None:
    st.title("行业动态")
    st.caption("这里汇总抖音和美团近 30 天内可确认日期的官方动态，方便销售和管理同学快速了解外部变化。")

    section_open("先更新再查看", "先更新最新内容，再看今天有没有值得同步给团队的行业变化。")
    c1, c2, c3 = st.columns(3)
    if c1.button("更新最新动态", use_container_width=True):
        st.session_state["competitor_updates"] = refresh_competitor_updates()
        st.rerun()
    if c2.button("重新整理近30天", use_container_width=True):
        st.session_state["competitor_updates"] = seed_last_30_days_baseline()
        st.rerun()

    updates = st.session_state.get("competitor_updates")
    if updates is None:
        updates = seed_last_30_days_baseline()
        st.session_state["competitor_updates"] = updates

    if not updates.empty and "checked_at" in updates.columns:
        latest_checked_at = str(updates["checked_at"].max())
        st.info(f"最近刷新时间：{latest_checked_at}。口径说明：只有明确发布日期的内容才进入“前一日动态”，其余内容进入“能力监控”。")

    dated_updates = updates[updates["date_quality"] == "明确日期"].copy()
    monitored_updates = updates[updates["date_quality"] != "明确日期"].copy()
    dated_updates = dated_updates.sort_values(["importance", "event_date"], ascending=[False, False], kind="stable")
    monitored_updates = monitored_updates.sort_values(["importance", "checked_at"], ascending=[False, False], kind="stable")
    yesterday = (pd.Timestamp.today() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    recent_cutoff = (pd.Timestamp.today() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    dated_updates = dated_updates[dated_updates["event_date"] >= recent_cutoff].copy()
    yesterday_updates = dated_updates[dated_updates["event_date"] == yesterday].copy()
    yesterday_priority = yesterday_updates[yesterday_updates["importance"] >= 85].copy()
    monitored_changes = monitored_updates[monitored_updates["status"] == "发现变更"].copy()

    if c3.button("获取海报", use_container_width=True):
        poster_input = dated_updates.copy()
        if poster_input.empty:
            st.warning("近 30 天内还没有可确认日期的动态，这次先不生成海报。")
        else:
            try:
                paths = export_competitor_poster(poster_input, "竞品动态日报海报")
            except RuntimeError as error:
                st.warning(str(error))
            else:
                st.session_state["latest_competitor_poster"] = paths["png"]
                st.session_state["show_competitor_poster_dialog"] = True
                st.rerun()
    section_close()

    latest_poster = st.session_state.get("latest_competitor_poster")
    if latest_poster and st.session_state.get("show_competitor_poster_dialog"):
        show_competitor_poster_dialog(latest_poster)

    render_insight_cards(
        [
            {"label": "昨日明确动态", "value": f"{len(yesterday_updates)} 条", "body": f"仅统计发布日期明确且为 {yesterday} 的动态。"},
            {"label": "抖音官方监控源", "value": f"{len(DOUYIN_DOC_SOURCES)} 个", "body": "以生活服务、服务商平台、代运营接入、IM、角色认证等官方能力页为主。", "tone": "slate"},
            {"label": "可信监控变更", "value": f"{len(monitored_changes)} 条", "body": "只有监控到页面真实变更时，才会出现在监控变更列表。", "tone": "teal"},
        ]
    )

    section_open("先看重点", "先快速扫一遍今天值得关注的内容，再往下看详情。")
    render_unified_competitor_summary(yesterday_updates, yesterday_priority, monitored_changes, yesterday)
    section_close()

    section_open("数据来源", "优先使用官方文档、官方新闻和官方能力页，尽量减少误报。")
    sources = pd.DataFrame(AUTHORITATIVE_SOURCES)
    st.dataframe(sources, use_container_width=True, hide_index=True)
    section_close()

    section_open("昨日新增", f"这里只展示发布日期明确且日期为 {yesterday} 的内容。")
    render_competitor_markdown_list(
        yesterday_updates,
        "日期",
        f"当前没有抓到发布日期明确且为 {yesterday} 的竞品动态。",
    )
    section_close()

    section_open("规则或能力变化", "只有确认到真实变化时，才会展示在这里。没有可信变更就不展示内容。")
    render_competitor_markdown_list(
        monitored_changes,
        "监控日期",
        "当前没有监控到可信的能力变更。",
    )
    section_close()

    section_open("近30天回看", "方便回看近 30 天里已经沉淀下来的可信内容。")
    display = pd.concat([dated_updates, monitored_changes], ignore_index=True)
    if display.empty:
        st.info("近30天内没有可公开展示的可信竞品动态。")
    else:
        show_table_or_empty(
            prepare_display_frame(
                display,
                [
                    ("platform", "平台"),
                    ("status", "状态"),
                    ("importance", "重要性", lambda value: f"{int(value)}"),
                    ("event_date", "日期"),
                    ("date_quality", "日期口径"),
                    ("source_name", "来源"),
                    ("title", "标题"),
                    ("summary", "摘要"),
                    ("url", "链接"),
                ],
            ),
            "近30天内没有可公开展示的可信竞品动态。",
        )
    section_close()

    section_open("我们需要关注什么", "把和日常销售、管理动作更相关的变化优先解释出来。")
    top = pd.concat([yesterday_updates, monitored_changes], ignore_index=True).sort_values(["importance", "event_date"], ascending=[False, False], kind="stable").head(5)
    if top.empty:
        st.info("当前没有足够可信的内容可供产品判断。")
    else:
        for _, row in top.iterrows():
            panel(
                f"{row['platform']} · {row['status']} · 重要性 {int(row['importance'])}",
                f"<strong>{row['title']}</strong><br>{row['summary']}<br><span style='color:#6b7280;'>来源：{row['source_name']} · 日期：{row['event_date']}（{row['date_quality']}） · 链接：{row['url']}</span>",
            )
    section_close()

    panel(
        "海报说明",
        "只有在存在近 30 天内、且日期可信的动态时，才会生成 PNG 海报，避免把不够新的内容带进去。",
    )


def render_architecture() -> None:
    st.title("系统说明")
    st.caption("这里简单说明当前版本覆盖了哪些常用模块，方便新人快速上手。")
    panel("当前已经覆盖", "我的工作台、平台概览、今日待办、跟进记录、找客户、方案报价、客户服务、沟通记录、批量任务、续费跟进、服务商管理、行业动态。")
    st.dataframe(pd.DataFrame({"阶段": ["MVP", "P1", "P2"], "建设重点": ["跑通拓商-销售-交付-续费主链路", "补齐线索分配、批量作业、评论和素材管理", "接入真实投放、CRM、结算和开放平台能力"]}), use_container_width=True, hide_index=True)


def render_page(page: str, data: dict[str, pd.DataFrame]) -> None:
    set_default_selection(data)
    {
        "首页总览": render_home,
        "平台首页": render_platform_home,
        "任务中心": render_task_center,
        "统一时间线": render_timeline,
        "操作日志": render_operation_logs,
        "导出中心": render_exports,
        "拓商工具": render_leads,
        "销售工具": render_sales,
        "商家与交付": render_delivery,
        "沟通协同": render_communications,
        "批量交付": render_bulk_ops,
        "续费工具": render_renewal,
        "平台管理台": render_platform_admin,
        "竞品动态": render_competitor_dynamics,
        "MVP 架构说明": lambda _: render_architecture(),
    }[page](data)
