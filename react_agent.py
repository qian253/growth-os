"""
GrowthOS 参赛版 — 基于 ReAct 的多工具智能体系统
你学过的：工具(练习1) + 多工具(练习2) + ReAct循环(练习3)
"""

import json, sys, requests, os
from dotenv import load_dotenv
load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ================================================================
# 工具定义 — Agent 的"手"
# ================================================================

def recommend_courses(goal: str) -> str:
    """根据目标推荐学习资源"""
    db = {
        "ai_agent": "1. LangChain官方教程\n2. OpenAI Agents SDK Quickstart\n3. B站: AI Agent从零实现",
        "python": "1. Python 100天从新手到大师(GitHub)\n2. 《Python编程从入门到实践》",
        "健身": "1. 《力量训练计划》(Starting Strength)\n2. B站: 帕梅拉跟练",
        "读书": "1. 《如何阅读一本书》\n2. 微信读书APP + 每日30min挑战",
    }
    for key, val in db.items():
        if key in goal.lower():
            return val
    return f"为你推荐「{goal}」相关教程，建议在B站/知乎搜索"

def calculate_time(weekday_hours: float, weekend_hours: float) -> str:
    """计算每周可用的总学习/练习时间"""
    weekly = weekday_hours * 5 + weekend_hours * 2
    monthly = weekly * 4
    return json.dumps({
        "每日工作日": f"{weekday_hours}h",
        "每日周末": f"{weekend_hours}h",
        "每周总计": f"{weekly}h",
        "每月总计": f"{monthly}h",
    }, ensure_ascii=False)

def split_plan(goal: str, weekly_hours: float) -> str:
    """把大目标拆成4周计划"""
    weeks = []
    for w in range(1, 5):
        weeks.append({
            "week": w,
            "theme": f"第{w}周：{['打基础','练技能','做项目','出成果'][w-1]}",
            "daily_hours": round(weekly_hours / 7, 1),
        })
    return json.dumps(weeks, ensure_ascii=False)

def motivation_boost(mood: str) -> str:
    """根据用户情绪状态生成鼓励"""
    boosts = {
        "累": "休息也是进步的一部分！今天少学点，但别断。",
        "烦": "关掉电脑去走走，15分钟回来再看这个问题。",
        "迷茫": "把目标写在纸上，拆成3步。先做第一步。",
    }
    for key, val in boosts.items():
        if key in mood:
            return val
    return "你已经比昨天的自己更好了。加油！💪"

TOOLS = [
    {"type": "function", "function": {
        "name": "recommend_courses",
        "description": "根据用户的学习目标推荐课程/书籍/资源",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "用户想学什么"}
            },
            "required": ["goal"]
        }
    }},
    {"type": "function", "function": {
        "name": "calculate_time",
        "description": "根据工作日和周末可用小时数，计算每周每月总时间",
        "parameters": {
            "type": "object",
            "properties": {
                "weekday_hours": {"type": "number", "description": "工作日每天几小时"},
                "weekend_hours": {"type": "number", "description": "周末每天几小时"}
            },
            "required": ["weekday_hours", "weekend_hours"]
        }
    }},
    {"type": "function", "function": {
        "name": "split_plan",
        "description": "把目标拆解为4周阶段性计划",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "目标名称"},
                "weekly_hours": {"type": "number", "description": "每周可用小时数"}
            },
            "required": ["goal", "weekly_hours"]
        }
    }},
    {"type": "function", "function": {
        "name": "motivation_boost",
        "description": "当用户说累/烦/迷茫时，生成鼓励和调整建议",
        "parameters": {
            "type": "object",
            "properties": {
                "mood": {"type": "string", "description": "用户的情绪/状态"}
            },
            "required": ["mood"]
        }
    }},
]

TOOL_IMPL = {
    "recommend_courses": lambda a: recommend_courses(a["goal"]),
    "calculate_time": lambda a: calculate_time(a["weekday_hours"], a["weekend_hours"]),
    "split_plan": lambda a: split_plan(a["goal"], a["weekly_hours"]),
    "motivation_boost": lambda a: motivation_boost(a["mood"]),
}

API_CONFIG = {
    "url": "https://api.deepseek.com/v1/chat/completions",
    "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY', '')}"},
}

def call_llm(messages: list) -> dict:
    body = {"model": "deepseek-chat", "messages": messages, "tools": TOOLS, "max_tokens": 1024}
    resp = requests.post(API_CONFIG["url"], headers=API_CONFIG["headers"], json=body, timeout=60)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}"}
    return resp.json()

def react_loop(messages: list, max_steps=10):
    """你学过的 ReAct 循环"""
    for step in range(1, max_steps + 1):
        print(f"\n  ⚡ ReAct 第{step}步")
        resp = call_llm(messages)
        if "error" in resp:
            print(f"  ❌ {resp['error']}")
            break
        msg = resp["choices"][0]["message"]
        content = msg.get("content", "") or ""
        if content:
            print(f"  🤔 {content[:120]}")
        if not msg.get("tool_calls"):
            print(f"  ✅ 完成！")
            return content
        for tc in msg["tool_calls"]:
            fn = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            print(f"  🔧 使用 {fn}")
            result = TOOL_IMPL[fn](args)
            print(f"  👀 结果: {str(result)[:80]}...")
        messages.append(dict(msg))
        for tc in msg["tool_calls"]:
            args = json.loads(tc["function"]["arguments"])
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": TOOL_IMPL[tc["function"]["name"]](args)})
    return "已生成计划"

# ================================================================
# 主程序
# ================================================================

print("\n" + "╔" + "═"*50 + "╗")
print("║     🌱 GrowthOS — ReAct 多工具智能体 ║")
print("║     参赛版 · 2026 星火杯              ║")
print("╚" + "═"*50 + "╝")

user_input = input("\n📝 描述你的情况：\n> ")

system_prompt = (
    "你是一个个人成长规划师。你有4个工具可用："
    "recommend_courses(推荐资源), calculate_time(算时间), "
    "split_plan(拆解4周计划), motivation_boost(鼓励用户)。\n"
    "每次只调用一个工具，直到完成所有分析再给出完整回答。"
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"{user_input}\n\n请分析我的情况：1) 推荐学习资源 2) 算可用时间 3) 帮我拆成4周计划"}
]

result = react_loop(messages)

print("\n" + "═"*50)
print(f"\n📋 {result}")
print("\n" + "═"*50)
print("✅ ReAct Agent 执行完毕！")
print("   你刚才看到的是一个完整的、自己决定调用什么工具的 AI 系统")
