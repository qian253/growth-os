"""
GrowthOS v2 — 真·多 Agent 智能成长系统
已接入 DeepSeek API，真正的大模型驱动
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.agent_engine import AGENT_PROFILE, AGENT_PLANNER, CONFIG


def main():
    print()
    print("=" * 55)
    print("  🌱 GrowthOS 多 Agent 智能成长系统")
    print(f"  引擎: {CONFIG['provider']} ({CONFIG['model']})")
    print("  流水线: 画像分析 → 智能规划")
    print("=" * 55)

    print()
    print("📝 描述你的情况（越详细计划越精准）")
    print("  支持任何目标：技能学习/健身/读书/兴趣/作息调整...")
    print("  示例：")
    print('  "我是大二学生，Python还可以，想学AI Agent开发..."')
    print('  "上班族，想健身增肌+学英语，工作日1小时，周末3小时..."')
    print('  "想多读书+早睡早起+学摄影，工作日晚上2小时..."')
    print("-" * 40)

    user_input = input(">>> ").strip()
    if not user_input:
        print("  输入不能为空")
        return

    # ================================================================
    # Agent 1: 画像分析
    # ================================================================
    print()
    print("┌──────────────────────────────────────┐")
    print("│ 🤖 Agent 1/2: 用户画像分析              │")
    print("└──────────────────────────────────────┘")
    print("  正在调用 DeepSeek 分析你的情况...", end=" ")

    result1 = AGENT_PROFILE.run(user_input, temperature=0.3)

    if result1["status"] != "done":
        print(f"\n  ❌ 画像分析失败: {result1}")
        return

    profile = result1["data"]
    print("✅ 完成！")
    goals = profile.get("goals", [])
    print(f"  发现 {len(goals)} 个提升目标:")
    for g in goals:
        area = g.get("area", "?")
        target = g.get("target", "?")
        cl = g.get("current_level", "?")
        tl = g.get("target_level", "?")
        print(f"    [{area}] {target} ({cl} → {tl})")

    t = profile.get("time", {})
    wd = t.get("weekday_hours", "?")
    we = t.get("weekend_hours", "?")
    pt = t.get("preferred_time", "?")
    print(f"  时间: 工作日{wd}h/天, 周末{we}h/天, 偏好{pt}")

    pain = profile.get("pain_points", [])
    if pain:
        print(f"  痛点: {' | '.join(pain)}")

    # ================================================================
    # Agent 2: 规划生成
    # ================================================================
    print()
    print("┌──────────────────────────────────────┐")
    print("│ 🤖 Agent 2/2: 智能规划生成              │")
    print("└──────────────────────────────────────┘")
    print("  正在调用 DeepSeek 制定计划...", end=" ")

    profile_json = json.dumps(profile, ensure_ascii=False)
    result2 = AGENT_PLANNER.run(profile_json, temperature=0.5)

    if result2["status"] != "done":
        print(f"\n  ❌ 规划生成失败: {result2}")
        return

    plan = result2["data"]
    print("✅ 完成！")
    print()

    # ================================================================
    # 展示完整结果
    # ================================================================
    print("=" * 55)
    print("  📋 你的个性化成长计划")
    print("=" * 55)

    weeks = plan.get("weekly_plans", [])
    for w in weeks:
        print()
        print(f"  {'─' * 50}")
        print(f"  第{w.get('week','?')}周 | {w.get('theme','')}")
        print(f"  重点: {', '.join(w.get('focus',[]))}")
        print(f"  难度: {w.get('difficulty','适中')}")
        print(f"  {'─' * 50}")

        schedule = w.get("schedule", {})
        for day in ["周一", "周二", "周三", "周四", "周五"]:
            if day in schedule:
                print(f"    {day} → {schedule[day]}")

        print()
        for day in ["周六", "周日"]:
            if day in schedule:
                print(f"    {day} → {schedule[day]}")

        milestones = w.get("milestones", [])
        if milestones:
            print(f"\n  🎯 {', '.join(milestones)}")

        if w.get("tips"):
            print(f"  💡 {w['tips']}")

    print()
    print(f"  {'=' * 50}")
    if plan.get("overall_advice"):
        print(f"\n  📝 {plan['overall_advice']}")
    if plan.get("motivation_message"):
        print(f"\n  💪 {plan['motivation_message']}")
    print()

    # ================================================================
    # 展示架构
    # ================================================================
    print("=" * 55)
    print("  🏗️  系统架构")
    print("=" * 55)
    print("""
  User Input
      │
      ▼
  ┌──────────┐     ┌──────────┐
  │ Agent 1  │ ──→ │ Agent 2  │ ──→  Plan Output
  │ 画像分析  │     │ 智能规划  │
  └──────────┘     └──────────┘
       │                │
       ▼                ▼
    JSON Data       4周详细计划

  引擎: DeepSeek Chat
  架构: 多 Agent 流水线 · 结构化数据传递
""")


if __name__ == "__main__":
    main()
