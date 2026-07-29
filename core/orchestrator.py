"""
GrowthOS Orchestrator — 多 Agent 编排调度器
"""

import json
import os
from datetime import datetime
from core.agent_engine import (
    ALL_AGENTS, AGENT_PROFILE, AGENT_PLANNER, AGENT_COACH,
    call_ai, get_tools, extract_json
)


class GrowthOS:
    """多 Agent 编排系统"""

    def __init__(self):
        self.data = {
            "user_id": datetime.now().strftime("%Y%m%d%H%M"),
            "profile": None,        # Agent 1 输出
            "plan": None,           # Agent 2 输出
            "current_week": 0,      # 当前周
        }
        self.agent_calls = []  # 记录所有 Agent 调用

    # ================================================================
    # Agent 调用（带 AI 引擎回传模式）
    # ================================================================

    def call_agent(self, agent: object, input_text: str, temperature=0.3):
        """调用一个 Agent，返回结构化结果"""
        result = agent.run(input_text, temperature)

        call_record = {
            "agent": agent.name,
            "input": input_text[:200],
            "result": result
        }
        self.agent_calls.append(call_record)

        return result

    # ================================================================
    # 流水线执行
    # ================================================================

    def run_pipeline(self, user_input: str):
        """执行完整的多 Agent 流水线"""
        print("=" * 60)
        print("  🌱 GrowthOS 启动 — 多 Agent 流水线")
        print("=" * 60)

        # ── Agent 1: 画像分析 ──
        print("\n  ┌──────────────────────────────────────┐")
        print(f"  │ 🤖 Agent 1/3: 用户画像分析              │")
        print("  └──────────────────────────────────────┘")

        result1 = self.call_agent(AGENT_PROFILE, user_input, temperature=0.3)

        if result1["status"] == "need_ai":
            # AI 引擎模式：返回提示词，等待外部 AI 处理
            return {
                "status": "need_ai_pipeline",
                "agents": [
                    {
                        "name": "profile",
                        "label": "用户画像分析",
                        "system": result1["system"],
                        "input": result1["input"],
                    },
                    {
                        "name": "planner",
                        "label": "智能规划生成",
                        "system": None,  # 下个节点
                        "input": None,
                    },
                    {
                        "name": "coach",
                        "label": "成长教练反馈",
                        "system": None,
                        "input": None,
                    }
                ]
            }

        # ── 如果有 API Key，完整处理 ──
        if result1["data"].get("goals"):
            print(f"  ✅ 完成")
            self.data["profile"] = result1["data"]
            print(f"     发现 {len(result1['data'].get('goals', []))} 个目标")
        else:
            print(f"  ⚠️ 结果: {result1}")

        # ── Agent 2: 规划生成 ──
        print("\n  ┌──────────────────────────────────────┐")
        print(f"  │ 🤖 Agent 2/3: 智能规划生成              │")
        print("  └──────────────────────────────────────┘")

        profile_json = json.dumps(self.data["profile"], ensure_ascii=False)
        result2 = self.call_agent(AGENT_PLANNER, profile_json, temperature=0.5)

        if result2["status"] == "need_ai":
            return {
                "status": "need_ai_planner",
                "profile": self.data["profile"],
                "agent": {
                    "name": "planner",
                    "system": result2["system"],
                    "input": result2["input"],
                },
                "agent1_result": result1
            }

        print(f"  ✅ 完成")
        self.data["plan"] = result2["data"]
        weeks = len(result2["data"].get("weekly_plans", []))
        print(f"     生成 {weeks} 周计划")

        # ── Agent 3: 生成最终展示 ──
        print("\n  ┌──────────────────────────────────────┐")
        print(f"  │ 🤖 Agent 3/3: 计划整合输出              │")
        print("  └──────────────────────────────────────┘")
        print("  ✅ 完成")

        return {"status": "complete", "data": self.data}

    # ================================================================
    # 接受 AI 引擎回传结果，继续流水线
    # ================================================================

    def continue_pipeline(self, stage: str, profile_data: dict = None, planner_data: dict = None):
        """从某一阶段继续流水线"""
        if stage == "need_ai_planner" and profile_data:
            self.data["profile"] = profile_data

            profile_json = json.dumps(profile_data, ensure_ascii=False)

            print("\n  ┌──────────────────────────────────────┐")
            print(f"  │ 🤖 Agent 2/3: 智能规划生成              │")
            print("  └──────────────────────────────────────┘")

            result2 = self.call_agent(AGENT_PLANNER, profile_json, temperature=0.5)

            if result2["status"] == "need_ai":
                return {
                    "status": "need_ai_planner",
                    "profile": profile_data,
                    "agent": {
                        "name": "planner",
                        "system": result2["system"],
                        "input": result2["input"],
                    },
                }

            self.data["plan"] = result2["data"]
            return {"status": "complete", "data": self.data}

        return {"status": "error", "message": "Unknown stage"}
