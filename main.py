"""
GrowthOS v2 — 真·多 Agent 个人成长系统
支持任何 OpenAI 兼容 API，零配置演示模式

用法:
  python main.py             交互模式（我当AI引擎）
  python main.py --api       使用 API Key（需在 core/agent_engine.py 配置）
"""

import json
import sys
import os

# 加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import GrowthOS


BANNER = """
╔══════════════════════════════════════════════════╗
║          🌱  GrowthOS  v2.0                      ║
║       个人成长智能体系统 · 多 Agent 协作          ║
║                                                  ║
║  Agent流水线: 画像分析 → 差距规划 → 成长教练      ║
║  支持: DeepSeek / OpenAI / 通义千问 / 演示模式    ║
╚══════════════════════════════════════════════════╝
"""


def print_plan(plan_data: dict):
    """打印计划的最终展示"""
    profile = plan_data.get("profile", {})
    plan = plan_data.get("plan", {})

    # ── 用户摘要 ──
    print("\n" + "="*60)
    print("  📋 你的个人成长报告")
    print("="*60)

    if profile.get("user_summary"):
        print(f"\n  👤 {profile['user_summary']}")

    # ── 目标列表 ──
    goals = profile.get("goals", [])
    if goals:
        print(f"\n  🎯 提升目标 ({len(goals)}项)")
        for i, g in enumerate(goals, 1):
            priority_stars = "⭐" * (6 - g.get("priority", 3))
            print(f"    {i}. {g.get('target','?')} [{g.get('area','?')}] {priority_stars}")
            print(f"       当前{g.get('current_level',1)}/5 → 目标{g.get('target_level',5)}/5")

    # ── 时间安排 ──
    t = profile.get("time", {})
    if t:
        print(f"\n  ⏰ 时间安排")
        print(f"    工作日: {t.get('weekday_hours',2)}h/天 · 周末: {t.get('weekend_hours',5)}h/天")
        print(f"    偏好时间: {t.get('preferred_time','晚上')}")

    # ── 每周计划 ──
    weeks = plan.get("weekly_plans", [])
    if weeks:
        print(f"\n  📅 4周成长计划")
        for w in weeks:
            print(f"\n  {'─'*50}")
            print(f"  第{w.get('week','?')}周 | {w.get('theme','')}")
            print(f"  重点: {' · '.join(w.get('focus',[]))}")
            print(f"  难度: {w.get('difficulty','适中')}")

            schedule = w.get("schedule", {})
            for day in ["周一","周二","周三","周四","周五","周六","周日"]:
                if day in schedule:
                    print(f"    {day} → {schedule[day]}")

            milestones = w.get("milestones", [])
            if milestones:
                print(f"  🎯 里程碑: {' | '.join(milestones)}")

            if w.get("tips"):
                print(f"  💡 {w['tips']}")
        print()

        total = plan.get("weekly_hours_summary", "")
        if total:
            print(f"  📊 每周投入: ~{total}小时")

    # ── 建议 ──
    if plan.get("overall_advice"):
        print(f"\n  📝 {plan['overall_advice']}")

    if plan.get("motivation_message"):
        print(f"\n  💪 {plan['motivation_message']}")

    # ── 技术架构展示 ──
    print(f"\n{'='*60}")
    print("  🏗️  系统架构")
    print(f"{'='*60}")
    print("""
  用户输入
      │
      ▼
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │ 🤖 Agent 1  │ → │ 🤖 Agent 2  │ → │ 🤖 Agent 3  │
  │  画像分析    │   │  差距规划    │   │  成长教练    │
  └─────────────┘   └─────────────┘   └─────────────┘
      │                   │                  │
      ▼                   ▼                  ▼
  ┌──────────────────────────────────────────────┐
  │           记忆存储 · 数据持久化                │
  │       支持切换任何 AI 模型作为引擎              │
  └──────────────────────────────────────────────┘

  技术亮点:
  ✅ 多 Agent 协作流水线 — 专业分工，层层递进
  ✅ 结构化数据传递 — Agent间通过JSON通信
  ✅ 插件式 AI 引擎 — 支持DeepSeek/OpenAI/通义千问
  ✅ 记忆持久化 — 数据本地存储，支持追踪
  ✅ 工具调用 — Agent可调用计算器/搜索等工具
""")


def main():
    print(BANNER)

    # 检查配置
    from core.agent_engine import CONFIG
    has_api = CONFIG["provider"] != "demo" and CONFIG["api_key"]

    if has_api:
        print(f"  🔌 使用 {CONFIG['provider']} API | 模型: {CONFIG['model']}")
    else:
        print(f"  🎯 演示模式 — 我（Claude）亲自当 AI 引擎")
        print(f"  💡 配好 API Key 后自动切换为真调用")
    print()

    # 收集用户输入
    print("📝 描述你的情况，越详细计划越精准！")
    print("   比如：")
    print('   "大二计算机系，Python还可以（3/5），想学AI Agent...')
    print('   "上班族，想健身增肌，工作日1小时，周末2小时..."')
    print('   "想多读书、学英语、早睡早起，工作日晚上..."')
    print("-"*40)

    user_input = input(">>> ").strip()

    if not user_input:
        print("  ⚠️ 输入不能为空")
        return

    # 运行流水线
    os = GrowthOS()
    result = os.run_pipeline(user_input)

    if result["status"] == "need_ai_pipeline":
        # 演示模式：输出 Agent 提示词
        print("\n" + "="*60)
        print("  🔄 演示模式 — 切换到 AI 引擎处理")
        print("="*60)
        print()
        print(f"  用户输入: {user_input[:100]}")
        print()
        print("  ⏳ 交给 AI 引擎（我）处理中...")
        print()

        # 显示每个 Agent 的 system prompt
        for agent in result["agents"]:
            print(f"  ┌─ Agent: {agent['label']} ─────────────")
            print(f"  │ System Prompt:")
            for line in agent["system"].split("\n"):
                print(f"  │ {line}")
            print(f"  │")
            print(f"  │ User Input: {agent['input'][:100]}...")
            print(f"  └{'─'*50}")
            print()

        print("  ⚡ 请将上方的 System Prompt 和 User Input 复制给我，")
        print("     我作为 AI 引擎处理完后返回结果给你！")
        print()

    elif result["status"] == "complete":
        print_plan(result["data"])
    else:
        print(f"  ❌ 流水线执行异常: {result}")


if __name__ == "__main__":
    main()
