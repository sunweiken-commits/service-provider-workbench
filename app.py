from __future__ import annotations

import streamlit as st

from gaode_console.pages import PAGE_LABELS, PAGES, ROLE_LABELS, ROLE_PAGE_ACCESS, render_page
from gaode_console.storage import load_data
from gaode_console.styles import apply_styles


st.set_page_config(
    page_title="高德服务商增长工作台",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


SIDEBAR_GROUPS = [
    ("开始工作", ["首页总览", "任务中心", "统一时间线", "操作日志", "导出中心"]),
    ("客户推进", ["拓商工具", "销售工具", "商家与交付", "沟通协同", "批量交付", "续费工具"]),
    ("平台管理", ["平台首页", "平台管理台", "竞品动态", "MVP 架构说明"]),
]


def main() -> None:
    apply_styles()
    data = load_data()

    current_role = st.session_state.get("current_role", "平台运营")
    if current_role not in ROLE_LABELS:
        current_role = "平台运营"
    visible_pages = ROLE_PAGE_ACCESS[current_role]
    default_page = st.session_state.get("nav_page", visible_pages[0])
    if default_page not in visible_pages:
        default_page = visible_pages[0]
    default_index = visible_pages.index(default_page)

    st.sidebar.title("工作区")
    role = st.sidebar.selectbox("我的身份", ROLE_LABELS, index=ROLE_LABELS.index(current_role))
    st.session_state["current_role"] = role
    visible_pages = ROLE_PAGE_ACCESS[role]
    if st.session_state.get("nav_page") not in visible_pages:
        st.session_state["nav_page"] = visible_pages[0]
    st.sidebar.markdown("### 我现在要做什么")
    page = st.session_state["nav_page"]

    for group_name, group_pages in SIDEBAR_GROUPS:
        group_visible = [group_page for group_page in group_pages if group_page in visible_pages]
        if not group_visible:
            continue
        st.sidebar.markdown(f'<div class="sidebar-group-label">{group_name}</div>', unsafe_allow_html=True)
        for group_page in group_visible:
            is_active = group_page == page
            if st.sidebar.button(
                PAGE_LABELS.get(group_page, group_page),
                key=f"nav_{group_page}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["nav_page"] = group_page
                st.rerun()

    page = st.session_state["nav_page"]
    st.session_state["nav_page"] = page
    st.sidebar.markdown("---")
    st.sidebar.caption("先看今日待办，再处理找客户、客户服务和续费跟进。")
    st.sidebar.caption(f"当前页面：{PAGE_LABELS.get(page, page)}")

    render_page(page, data)


if __name__ == "__main__":
    main()
