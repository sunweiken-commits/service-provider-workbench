from __future__ import annotations

from datetime import date

import pandas as pd


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "leads": pd.DataFrame(
            [
                {"lead_id": "LD-001", "merchant": "喜乐洗车工坊", "industry": "汽车服务", "city": "上海", "district": "浦东新区", "status": "待跟进", "owner": "王晨", "intent_score": 92, "poi_status": "未认领", "opportunity": "周边搜索需求高、竞对已有深度信息", "budget_band": "3000-8000"},
                {"lead_id": "LD-002", "merchant": "白桃轻食", "industry": "餐饮", "city": "杭州", "district": "西湖区", "status": "已沟通", "owner": "李娜", "intent_score": 83, "poi_status": "已认领", "opportunity": "导航转化率低、评论未维护", "budget_band": "5000-12000"},
                {"lead_id": "LD-003", "merchant": "悦己丽人皮肤管理", "industry": "丽人", "city": "广州", "district": "天河区", "status": "方案中", "owner": "赵宇", "intent_score": 88, "poi_status": "未认领", "opportunity": "品牌词需求增长快、门店素材老旧", "budget_band": "8000-20000"},
                {"lead_id": "LD-004", "merchant": "安心口腔门诊", "industry": "医疗", "city": "深圳", "district": "南山区", "status": "待跟进", "owner": "陈蕾", "intent_score": 95, "poi_status": "未认领", "opportunity": "高客单线索行业、电话留资潜力高", "budget_band": "10000-30000"},
                {"lead_id": "LD-005", "merchant": "山海健身", "industry": "运动健身", "city": "成都", "district": "高新区", "status": "已签约", "owner": "周航", "intent_score": 79, "poi_status": "已认领", "opportunity": "新店开业、适合做首月拉新", "budget_band": "5000-15000"},
            ]
        ),
        "merchants": pd.DataFrame(
            [
                {"merchant_id": "MC-101", "merchant": "山海健身", "industry": "运动健身", "city": "成都", "service_status": "投放中", "package": "曝光增长包", "owner": "周航", "monthly_budget": 12000, "exposure": 82340, "clicks": 5320, "calls": 166, "navigations": 438, "arrivals": 117, "renewal_risk": "低"},
                {"merchant_id": "MC-102", "merchant": "白桃轻食", "industry": "餐饮", "city": "杭州", "service_status": "待首充", "package": "基础经营包", "owner": "李娜", "monthly_budget": 5000, "exposure": 14200, "clicks": 840, "calls": 29, "navigations": 74, "arrivals": 18, "renewal_risk": "中"},
                {"merchant_id": "MC-103", "merchant": "悦己丽人皮肤管理", "industry": "丽人", "city": "广州", "service_status": "服务中", "package": "转化增强包", "owner": "赵宇", "monthly_budget": 18000, "exposure": 93620, "clicks": 6130, "calls": 205, "navigations": 317, "arrivals": 88, "renewal_risk": "中"},
                {"merchant_id": "MC-104", "merchant": "安心口腔门诊", "industry": "医疗", "city": "深圳", "service_status": "方案待确认", "package": "转化增强包", "owner": "陈蕾", "monthly_budget": 25000, "exposure": 22480, "clicks": 1230, "calls": 61, "navigations": 98, "arrivals": 22, "renewal_risk": "高"},
                {"merchant_id": "MC-105", "merchant": "喜乐洗车工坊", "industry": "汽车服务", "city": "上海", "service_status": "待认领", "package": "基础经营包", "owner": "王晨", "monthly_budget": 8000, "exposure": 0, "clicks": 0, "calls": 0, "navigations": 0, "arrivals": 0, "renewal_risk": "中"},
            ]
        ),
        "packages": pd.DataFrame(
            [
                {"package": "基础经营包", "price": 2999, "target": "首次入驻、信息不完整门店", "contents": "认领、认证、资料治理、门店装修、评价回复", "goal": "先提升门店完整度和信任感"},
                {"package": "曝光增长包", "price": 6999, "target": "已有门店基础、想提升曝光的商家", "contents": "搜索曝光、商圈曝光、品牌词、类目词优化", "goal": "提升被找到和被点击概率"},
                {"package": "转化增强包", "price": 9999, "target": "高客单、重线索行业商家", "contents": "电话留资、预约组件、活动页、到店权益", "goal": "提升线索获取和到店转化"},
                {"package": "连锁经营包", "price": 19999, "target": "总部客户和多门店客户", "contents": "连锁管理、批量分发、区域报表、统一策略", "goal": "提升总部经营效率和大客户客单价"},
            ]
        ),
        "renewal": pd.DataFrame(
            [
                {"merchant": "安心口腔门诊", "expiry_date": date(2026, 4, 8), "risk_level": "高", "risk_reason": "通话线索转化偏低，商家尚未确认续投预算", "next_action": "安排复盘会，建议切换到高意图词包并追加预约组件"},
                {"merchant": "白桃轻食", "expiry_date": date(2026, 4, 12), "risk_level": "中", "risk_reason": "基础经营完成，但尚未升级曝光包", "next_action": "用竞对对比报告推动首充升级"},
                {"merchant": "悦己丽人皮肤管理", "expiry_date": date(2026, 4, 20), "risk_level": "中", "risk_reason": "效果稳定，但商家希望看到更清晰 ROI 证明", "next_action": "生成月报并展示到店归因趋势"},
            ]
        ),
        "keyword_insights": pd.DataFrame(
            [
                {"keyword": "附近洗车", "search_index": 98, "competition": "高", "recommendation": "优先投放浦东新区和高架周边门店"},
                {"keyword": "轻食外卖", "search_index": 76, "competition": "中", "recommendation": "建议配合午间时段活动页"},
                {"keyword": "皮肤管理", "search_index": 89, "competition": "高", "recommendation": "建议加强品牌词保护和预约转化组件"},
                {"keyword": "口腔矫正", "search_index": 94, "competition": "高", "recommendation": "优先做电话留资和预约承接"},
            ]
        ),
        "competitor_benchmark": pd.DataFrame(
            [
                {"platform": "抖音", "role_model": "代运营服务商 + 代开发服务商", "core_support": "角色认证、合作关系建立、商品批量发布、交易系统、IM 客服、服务市场", "product_implication": "高德应优先建设服务商身份、商家授权和标准商品能力"},
                {"platform": "美团", "role_model": "官方代运营 + SaaS + 本地化服务团队", "core_support": "服务标准、经营工具、评价治理、AI 经营工具、客诉托底、连锁经营系统", "product_implication": "高德应优先建设服务标准、续费复盘、风险治理和本地化支持"},
                {"platform": "高德 MVP 方向", "role_model": "本地商家增长伙伴", "core_support": "商机线索、诊断报告、套餐报价、交付看板、到店归因、续费预警", "product_implication": "先把拓商、销售、交付、续费主链路做通，再逐步补 CRM 和开放能力"},
            ]
        ),
        "lead_activity": pd.DataFrame(
            [
                {"lead_id": "LD-001", "date": "2026-03-25", "stage": "首次触达", "actor": "王晨", "note": "电话沟通，商家对认领和基础曝光有兴趣。"},
                {"lead_id": "LD-001", "date": "2026-03-26", "stage": "发送诊断", "actor": "王晨", "note": "已发送门店诊断和基础经营包方案。"},
                {"lead_id": "LD-002", "date": "2026-03-24", "stage": "复盘沟通", "actor": "李娜", "note": "商家反馈想先看竞对和投放差异。"},
                {"lead_id": "LD-003", "date": "2026-03-26", "stage": "方案确认", "actor": "赵宇", "note": "确认转化增强包，等待门店授权。"},
                {"lead_id": "LD-004", "date": "2026-03-27", "stage": "待拜访", "actor": "陈蕾", "note": "建议平台 BD 联合服务商拜访，提高医疗行业成交率。"},
                {"lead_id": "LD-005", "date": "2026-03-20", "stage": "签约完成", "actor": "周航", "note": "已完成首充，进入门店装修和投放准备。"},
            ]
        ),
        "merchant_monthly_report": pd.DataFrame(
            [
                {"merchant": "山海健身", "month": "2026-03", "exposure": 82340, "clicks": 5320, "calls": 166, "navigations": 438, "arrivals": 117, "roi": 2.73},
                {"merchant": "白桃轻食", "month": "2026-03", "exposure": 14200, "clicks": 840, "calls": 29, "navigations": 74, "arrivals": 18, "roi": 1.01},
                {"merchant": "悦己丽人皮肤管理", "month": "2026-03", "exposure": 93620, "clicks": 6130, "calls": 205, "navigations": 317, "arrivals": 88, "roi": 1.37},
                {"merchant": "安心口腔门诊", "month": "2026-03", "exposure": 22480, "clicks": 1230, "calls": 61, "navigations": 98, "arrivals": 22, "roi": 0.25},
                {"merchant": "喜乐洗车工坊", "month": "2026-03", "exposure": 0, "clicks": 0, "calls": 0, "navigations": 0, "arrivals": 0, "roi": 0.0},
            ]
        ),
        "chain_stores": pd.DataFrame(
            [
                {"brand": "山海健身", "store": "山海健身·成都高新店", "city": "成都", "status": "营业中", "completion": 92, "material_status": "已同步"},
                {"brand": "山海健身", "store": "山海健身·成都天府店", "city": "成都", "status": "营业中", "completion": 88, "material_status": "待更新"},
                {"brand": "安心口腔", "store": "安心口腔·深圳南山店", "city": "深圳", "status": "营业中", "completion": 76, "material_status": "待补充"},
                {"brand": "安心口腔", "store": "安心口腔·深圳福田店", "city": "深圳", "status": "待认领", "completion": 42, "material_status": "未分发"},
            ]
        ),
        "bulk_tasks": pd.DataFrame(
            [
                {"task_id": "BK-201", "task_type": "批量认领", "scope": "安心口腔 2 家门店", "progress": "进行中", "owner": "陈蕾", "eta": "2026-03-29"},
                {"task_id": "BK-202", "task_type": "素材分发", "scope": "山海健身 2 家门店", "progress": "待审核", "owner": "周航", "eta": "2026-03-28"},
                {"task_id": "BK-203", "task_type": "评价回复", "scope": "白桃轻食 1 家门店", "progress": "已完成", "owner": "李娜", "eta": "2026-03-27"},
                {"task_id": "BK-204", "task_type": "连锁批量修改", "scope": "安心口腔 营业时间调整", "progress": "待执行", "owner": "陈蕾", "eta": "2026-03-30"},
            ]
        ),
        "partners": pd.DataFrame(
            [
                {"partner": "沪上增长伙伴", "type": "拓店型", "city_scope": "上海 / 苏州", "level": "金牌", "cert_status": "已认证", "active_merchants": 42, "monthly_revenue": 186000, "complaint_rate": "0.8%"},
                {"partner": "南区丽人运营中心", "type": "增长型", "city_scope": "广州 / 深圳", "level": "银牌", "cert_status": "已认证", "active_merchants": 27, "monthly_revenue": 132000, "complaint_rate": "1.4%"},
                {"partner": "连锁数字化实验室", "type": "技术型", "city_scope": "全国", "level": "战略", "cert_status": "已认证", "active_merchants": 18, "monthly_revenue": 254000, "complaint_rate": "0.3%"},
                {"partner": "西南商家服务站", "type": "拓店型", "city_scope": "成都 / 重庆", "level": "基础", "cert_status": "待复审", "active_merchants": 15, "monthly_revenue": 54000, "complaint_rate": "2.2%"},
            ]
        ),
        "partner_incentives": pd.DataFrame(
            [
                {"partner": "沪上增长伙伴", "month": "2026-03", "new_store_bonus": 12000, "first_charge_bonus": 8600, "renewal_bonus": 4200, "total_bonus": 24800},
                {"partner": "南区丽人运营中心", "month": "2026-03", "new_store_bonus": 6000, "first_charge_bonus": 9400, "renewal_bonus": 5100, "total_bonus": 20500},
                {"partner": "连锁数字化实验室", "month": "2026-03", "new_store_bonus": 3000, "first_charge_bonus": 12000, "renewal_bonus": 8800, "total_bonus": 23800},
                {"partner": "西南商家服务站", "month": "2026-03", "new_store_bonus": 4500, "first_charge_bonus": 2600, "renewal_bonus": 1200, "total_bonus": 8300},
            ]
        ),
        "complaints": pd.DataFrame(
            [
                {"ticket_id": "CS-301", "partner": "西南商家服务站", "merchant": "雾山火锅", "issue_type": "虚假承诺", "status": "待处理", "priority": "高", "created_at": "2026-03-26"},
                {"ticket_id": "CS-302", "partner": "沪上增长伙伴", "merchant": "喜乐洗车工坊", "issue_type": "跟进延迟", "status": "处理中", "priority": "中", "created_at": "2026-03-25"},
                {"ticket_id": "CS-303", "partner": "南区丽人运营中心", "merchant": "悦己丽人皮肤管理", "issue_type": "效果争议", "status": "待复盘", "priority": "中", "created_at": "2026-03-24"},
            ]
        ),
        "joint_visits": pd.DataFrame(
            [
                {"visit_id": "JV-101", "partner": "沪上增长伙伴", "merchant": "某连锁洗车品牌", "city": "上海", "owner": "平台BD-张宁", "status": "已预约", "visit_date": "2026-03-29"},
                {"visit_id": "JV-102", "partner": "南区丽人运营中心", "merchant": "某轻医美品牌", "city": "深圳", "owner": "平台BD-林珊", "status": "待确认", "visit_date": "2026-03-30"},
                {"visit_id": "JV-103", "partner": "连锁数字化实验室", "merchant": "某口腔连锁", "city": "广州", "owner": "平台BD-周哲", "status": "方案准备中", "visit_date": "2026-04-02"},
            ]
        ),
        "training_records": pd.DataFrame(
            [
                {"partner": "沪上增长伙伴", "course": "基础认证考试", "completion": "已完成", "score": 92, "last_date": "2026-03-12"},
                {"partner": "南区丽人运营中心", "course": "丽人行业增长方案", "completion": "已完成", "score": 88, "last_date": "2026-03-18"},
                {"partner": "连锁数字化实验室", "course": "连锁经营与 API 接入", "completion": "已完成", "score": 95, "last_date": "2026-03-19"},
                {"partner": "西南商家服务站", "course": "客诉治理与服务规范", "completion": "待完成", "score": 0, "last_date": "2026-03-27"},
            ]
        ),
        "communications": pd.DataFrame(
            [
                {"comm_id": "CM-401", "merchant": "安心口腔门诊", "partner": "南区丽人运营中心", "channel": "电话", "direction": "外呼", "status": "待回访", "owner": "陈蕾", "last_time": "2026-03-27 10:30", "summary": "商家希望先看 ROI 与竞对对比，再决定是否首充。"},
                {"comm_id": "CM-402", "merchant": "白桃轻食", "partner": "沪上增长伙伴", "channel": "企业微信", "direction": "双向沟通", "status": "已跟进", "owner": "李娜", "last_time": "2026-03-27 09:20", "summary": "已发送竞对诊断和套餐报价，等待商家确认预算。"},
                {"comm_id": "CM-403", "merchant": "悦己丽人皮肤管理", "partner": "南区丽人运营中心", "channel": "平台IM", "direction": "商家发起", "status": "处理中", "owner": "赵宇", "last_time": "2026-03-26 18:40", "summary": "商家询问预约组件和电话留资的差异。"},
                {"comm_id": "CM-404", "merchant": "山海健身", "partner": "连锁数字化实验室", "channel": "线下拜访", "direction": "联合拜访", "status": "已完成", "owner": "周航", "last_time": "2026-03-25 15:00", "summary": "总部确认继续续费，并讨论连锁经营包升级。"},
            ]
        ),
        "platform_actions": pd.DataFrame(
            [
                {"action_id": "PA-501", "action_time": "2026-03-27 11:20", "action_type": "发起续费复盘", "target": "安心口腔门诊", "owner": "平台运营-李想", "summary": "要求服务商本周内组织 ROI 复盘会并反馈结果。"},
                {"action_id": "PA-502", "action_time": "2026-03-27 10:10", "action_type": "发起联合拜访", "target": "某轻医美品牌", "owner": "平台BD-林珊", "summary": "与南区丽人运营中心联合推进深圳重点客户。"},
            ]
        ),
        "operation_logs": pd.DataFrame(
            [
                {"log_id": "LG-601", "time": "2026-03-27 11:25", "actor": "平台运营-李想", "target_type": "平台动作", "target": "安心口腔门诊", "action": "发起续费复盘", "detail": "要求服务商组织 ROI 复盘会。"},
                {"log_id": "LG-602", "time": "2026-03-27 10:45", "actor": "陈蕾", "target_type": "线索", "target": "安心口腔门诊", "action": "更新线索状态", "detail": "线索状态更新为待跟进。"},
            ]
        ),
        "competitor_snapshots": pd.DataFrame(
            columns=[
                "snapshot_id",
                "platform",
                "item_type",
                "item_id",
                "title",
                "url",
                "event_date",
                "importance",
                "summary",
                "content_hash",
                "status",
                "checked_at",
                "source_name",
                "date_quality",
            ]
        ),
    }
