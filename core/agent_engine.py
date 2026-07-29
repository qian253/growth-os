"""
GrowthOS Agent 内核 — 支持任何 OpenAI 兼容 API
"""

import json
import os
from typing import Optional, Callable, Any

# ================================================================
# 配置区 — 换任何一个 API Key 就能用
# ================================================================

CONFIG = {
    # 方案 A: DeepSeek（已配置）
    "provider": "deepseek",
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
}

# ================================================================
# AI 调用器
# ================================================================

def call_ai(system_prompt: str, user_message: str, temperature=0.3) -> str:
    """
    调用 AI 模型。
    演示模式下返回一个标记，由外层处理；
    有 API Key 时真正调用。
    """
    cfg = CONFIG

    if cfg["provider"] == "demo":
        # 演示模式：返回结构化标记，由外层（我）处理
        return f"__AI_NEEDED__||{system_prompt}||{user_message}"
    else:
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['api_key']}"
        }
        payload = {
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": 4096,
        }
        resp = requests.post(cfg["api_url"], headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            return f"【API错误 {resp.status_code}】{resp.text}"
        return resp.json()["choices"][0]["message"]["content"]


def extract_json(text: str) -> dict:
    """从文本中提取 JSON"""
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return {"raw_output": text}


# ================================================================
# Agent 核心类
# ================================================================

class Agent:
    """通用 Agent 节点"""

    def __init__(self, name: str, system_prompt: str, tools: list = None):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.memory = []

    def run(self, user_input: str, temperature=0.3) -> dict:
        """运行 Agent"""

        # 注入工具描述
        tools_desc = ""
        if self.tools:
            tools_desc = "\n\n你可以使用以下工具：\n"
            for t in self.tools:
                tools_desc += f"- {t['name']}: {t['desc']} (参数: {t['params']})\n"

        full_system = self.system_prompt + tools_desc
        full_system += "\n\n请严格按 JSON 格式输出。"

        result = call_ai(full_system, user_input, temperature)
        self.memory.append({"input": user_input, "output": result})

        if result.startswith("__AI_NEEDED__"):
            return {"status": "need_ai", "system": full_system, "input": user_input, "raw": result}
        else:
            return {"status": "done", "output": result, "data": extract_json(result)}

    def clear_memory(self):
        self.memory = []


# ================================================================
# 工具函数
# ================================================================

def get_tools():
    return [
        {
            "name": "time_calculator",
            "desc": "计算每周/每月可用学习时间",
            "params": "weekday_hours(数字), weekend_hours(数字), weeks(数字)"
        },
        {
            "name": "resource_recommender",
            "desc": "推荐学习/练习资源",
            "params": "topic(话题), style(偏好)"
        },
        {
            "name": "progress_tracker",
            "desc": "记录和追踪执行进度",
            "params": "week(第几周), completed(完成项), hours(小时数)"
        },
    ]


# ================================================================
# Agent 定义
# ================================================================

# Agent 1: 用户画像分析
AGENT_PROFILE = Agent(
    name="用户画像分析师",
    system_prompt="""你是 GrowthOS 的用户画像分析师。

你的任务是分析用户的自我介绍，提取结构化信息。

用户可能想提升任何方面：
- 技能类：编程、设计、英语、AI
- 健康类：健身、跑步、减脂、早睡早起
- 知识类：读书、历史、哲学、心理学
- 兴趣类：吉他、摄影、写作、画画、烹饪

输出格式（严格 JSON）：
{
  "user_summary": "一句话总结",
  "goals": [
    {
      "area": "技能/健康/知识/兴趣/其他",
      "target": "具体目标描述",
      "current_level": 当前水平1-5,
      "target_level": 目标水平1-5,
      "priority": 优先级1-5,
      "deadline": "期望时间",
      "why": "为什么想提升这个"
    }
  ],
  "time": {
    "weekday_hours": 工作日每天几小时(数字),
    "weekend_hours": 周末每天几小时(数字),
    "preferred_time": "早上/下午/晚上",
    "time_quality": "时间质量评价(碎片/集中)"
  },
  "learning_style": "喜欢的方式(视频/阅读/实践/跟练/社交)",
  "personality": "用户性格特征",
  "pain_points": ["困难1", "困难2"],
  "strengths": ["用户的优势"],
  "interests": ["兴趣列表"],
  "environment": "学习/生活环境描述"
}"""
)

# Agent 2: 智能规划师
AGENT_PLANNER = Agent(
    name="智能规划师",
    system_prompt="""你是 GrowthOS 的智能规划师，擅长制定个性化提升计划。

根据用户画像，制定 4 周详细计划。

要求：
1. 非常具体可执行：
   - 技能类：具体课程名、章节、练习项目
   - 健身类：具体动作、组数、次数、休息时间
   - 读书类：具体书名、章节、阅读方法
   - 兴趣类：具体练习内容、频次
2. 针对用户痛点给出解决方案
3. 按用户可用时间分配，不可超时
4. 每周递进，第4周要有成果输出
5. 工作日轻量、周末深度

输出格式：
{
  "weekly_plans": [
    {
      "week": 1,
      "theme": "本周主题名称",
      "focus": ["重点1", "重点2"],
      "schedule": {
        "周一": "具体任务 (预计时长)",
        "周二": "具体任务 (预计时长)",
        "周三": "具体任务 (预计时长)",
        "周四": "具体任务 (预计时长)",
        "周五": "具体任务 (预计时长)",
        "周六": "具体任务 (预计时长)",
        "周日": "具体任务 (预计时长)"
      },
      "milestones": ["本周要达成的具体成果"],
      "difficulty": "难度评级(入门/进阶/挑战)",
      "tips": "本周特别提醒"
    }
  ],
  "overall_advice": "总体建议",
  "weekly_hours_summary": "每周投入总小时数",
  "motivation_message": "一句定制化的鼓励"
}"""
)

# Agent 3: 成长教练（进度追踪）
AGENT_COACH = Agent(
    name="成长教练",
    system_prompt="""你是 GrowthOS 的成长教练。

根据用户的反馈和现有计划，给出调整建议。

用户反馈类型分析：
- "太累了" → 降低强度30%，增加休息日
- "太简单" → 提升难度，增加挑战
- "没时间" → 精简到核心任务
- "效果不错" → 保持节奏，微调
- "很迷茫" → 明确短期目标，拆解步骤
- "坚持不了" → 加入习惯绑定、奖励机制

输出格式：
{
  "mood_analysis": "对用户状态的分析",
  "is_on_track": true/false,
  "adjustments": ["调整1", "调整2", "调整3"],
  "next_week_focus": "下周重点",
  "success_indicators": "怎么判断自己进步了",
  "encouragement": "一段真诚的鼓励"
}"""
)


# ================================================================
# 注册所有 Agent
# ================================================================

ALL_AGENTS = {
    "profile": AGENT_PROFILE,
    "planner": AGENT_PLANNER,
    "coach": AGENT_COACH,
}
