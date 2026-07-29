"""
GrowthOS v2 — Web 版
在浏览器里运行，不是终端了！
"""

import streamlit as st
import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.agent_engine import AGENT_PROFILE, AGENT_PLANNER, CONFIG

st.set_page_config(
    page_title="GrowthOS - 个人成长智能体",
    page_icon="🌱",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { max-width: 1000px; margin: 0 auto; }
    .agent-card {
        background: #f0f2f6;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border-left: 4px solid #4CAF50;
    }
    .agent-1 { border-left-color: #2196F3; }
    .agent-2 { border-left-color: #FF9800; }
    .week-card {
        background: #fafafa;
        border-radius: 10px;
        padding: 20px;
        margin: 12px 0;
        border: 1px solid #e0e0e0;
    }
    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    .tag-blue { background: #E3F2FD; color: #1565C0; }
    .tag-green { background: #E8F5E9; color: #2E7D32; }
    .tag-orange { background: #FFF3E0; color: #E65100; }
    .tag-purple { background: #F3E5F5; color: #6A1B9A; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# 标题
# ================================================================

st.title("🌱 GrowthOS")
st.caption(f"多 Agent 智能成长系统 · 引擎: {CONFIG['provider']} ({CONFIG['model']})")
st.divider()

# ================================================================
# Agent 流水线状态
# ================================================================

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**🧑‍💻 你**")
    st.caption("输入你的情况")
with col2:
    st.markdown("**🤖 Agent 1**")
    st.caption("画像分析")
with col3:
    st.markdown("**🤖 Agent 2**")
    st.caption("智能规划")
with col4:
    st.markdown("**📋 输出**")
    st.caption("成长计划")

st.divider()

# ================================================================
# 用户输入
# ================================================================

st.subheader("📝 描述你的情况")
st.info("支持任何目标：学习编程、健身增肌、读书写作、早睡早起……越详细计划越精准！")

default_input = "我是大二计算机学生，Python还可以（3/5），想学AI Agent开发，工作日晚上能学2小时，周末下午6小时，喜欢动手做项目。最大的问题就是坚持不下来。"

with st.container():
    user_input = st.text_area(
        "你的情况：",
        value=default_input,
        height=120,
        placeholder="告诉我你的技能、目标、可用时间、学习偏好、困难……"
    )
    cols = st.columns([1, 3])
    with cols[0]:
        run_btn = st.button("🚀 生成我的成长计划", type="primary", use_container_width=True)
    with cols[1]:
        st.caption("点击后系统会依次调用 2 个 AI Agent 分析你的情况")

st.divider()

# ================================================================
# 执行流水线
# ================================================================

if run_btn and user_input.strip():
    with st.status("🤖 多 Agent 流水线运行中...", expanded=True) as status:

        # ── Agent 1: 画像分析 ──
        st.markdown("### 🤖 Agent 1/2: 用户画像分析")
        st.caption("调用 DeepSeek 分析你的技能、目标、时间、痛点……")
        progress_bar = st.progress(0, text="正在分析...")

        result1 = AGENT_PROFILE.run(user_input.strip(), temperature=0.3)

        if result1["status"] != "done":
            st.error(f"画像分析失败: {result1}")
            st.stop()

        profile = result1["data"]
        progress_bar.progress(50, text="✅ 画像分析完成")

        # 展示画像结果
        with st.expander("📊 画像分析结果（结构化数据）", expanded=False):
            st.json(profile)
            goals = profile.get("goals", [])
            st.markdown(f"**发现 {len(goals)} 个提升目标**")

            cols = st.columns(len(goals) if goals else 1)
            for i, g in enumerate(goals):
                with cols[i % len(cols)]:
                    area = g.get("area", "?")
                    target = g.get("target", "?")
                    cl = g.get("current_level", "?")
                    tl = g.get("target_level", "?")
                    st.markdown(
                        f"<span class='tag tag-blue'>{area}</span><br>"
                        f"**{target}**<br>"
                        f"水平: {cl} → {tl}",
                        unsafe_allow_html=True
                    )

        time_info = profile.get("time", {})
        st.markdown(
            f"<div class='agent-card agent-1'>"
            f"✅ **画像分析完成** — "
            f"时间: 工作日{time_info.get('weekday_hours','?')}h/天 · "
            f"周末{time_info.get('weekend_hours','?')}h/天 · "
            f"偏好{time_info.get('preferred_time','?')}<br>"
            f"痛点: {' · '.join(profile.get('pain_points',['无']))}"
            f"</div>",
            unsafe_allow_html=True
        )

        # ── Agent 2: 规划生成 ──
        st.markdown("---")
        st.markdown("### 🤖 Agent 2/2: 智能规划生成")
        st.caption("调用 DeepSeek 定制 4 周详细计划……")
        progress_bar.progress(60, text="正在生成计划...")

        profile_json = json.dumps(profile, ensure_ascii=False)
        result2 = AGENT_PLANNER.run(profile_json, temperature=0.5)

        if result2["status"] != "done":
            st.error(f"规划生成失败: {result2}")
            st.stop()

        plan = result2["data"]
        st.markdown(
            "<div class='agent-card agent-2'>✅ **计划生成完成**</div>",
            unsafe_allow_html=True
        )

        progress_bar.progress(100, text="✅ 全部完成！")
        status.update(label="🎉 多 Agent 流水线执行完毕！", state="complete")

    # ================================================================
    # 展示完整计划
    # ================================================================

    st.divider()
    st.subheader("📋 你的个性化成长计划")

    weeks = plan.get("weekly_plans", [])
    tabs = st.tabs([f"第{w.get('week','?')}周" for w in weeks])

    for i, w in enumerate(weeks):
        with tabs[i]:
            theme = w.get("theme", "")
            focus = w.get("focus", [])
            difficulty = w.get("difficulty", "适中")

            diff_color = {
                "入门": ("🟢", "green"),
                "进阶": ("🟡", "orange"),
                "挑战": ("🔴", "red"),
            }
            diff_icon, diff_c = diff_color.get(difficulty, ("⚪", "gray"))

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {diff_icon} 第{w.get('week','?')}周：{theme}")
            with col2:
                st.markdown(f"<span class='tag tag-{diff_c}'>{difficulty}</span>", unsafe_allow_html=True)
                st.caption(f"重点：{' · '.join(focus)}")

            st.divider()

            schedule = w.get("schedule", {})

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**工作日**")
                for day in ["周一", "周二", "周三", "周四", "周五"]:
                    if day in schedule:
                        st.markdown(f"- **{day}**：{schedule[day]}")

            with col2:
                st.markdown("**周末**")
                for day in ["周六", "周日"]:
                    if day in schedule:
                        st.markdown(f"- **{day}**：{schedule[day]}")

            milestones = w.get("milestones", [])
            if milestones:
                st.markdown("---")
                st.markdown("**🎯 本周里程碑**")
                for m in milestones:
                    st.markdown(f"- ✅ {m}")

            if w.get("tips"):
                st.info(f"💡 {w['tips']}")

    # ================================================================
    # 总体建议
    # ================================================================
    st.divider()
    st.subheader("📝 总体建议")

    if plan.get("overall_advice"):
        st.success(plan["overall_advice"])

    if plan.get("motivation_message"):
        st.info(f"💪 {plan['motivation_message']}")

    # ================================================================
    # 技术架构
    # ================================================================
    with st.expander("🏗️ 查看系统架构", expanded=False):
        st.markdown("""
        ```
        User Input
            │
            ▼
        ┌──────────┐     ┌──────────┐
        │ Agent 1  │ ──→ │ Agent 2  │ ──→ Plan Output
        │ 画像分析  │     │ 智能规划  │
        └──────────┘     └──────────┘
              │                │
              ▼                ▼
          JSON Data       4周详细计划
        ```
        """)
        st.caption(f"引擎: {CONFIG['provider']} ({CONFIG['model']}) · 架构: 多 Agent 流水线 · 结构化数据传递")

else:
    st.info("👆 输入你的情况，点击按钮生成专属成长计划")
