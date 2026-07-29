# 🌱 GrowthOS — ReAct 多工具智能体系统

> 参赛作品 · 2026 星火杯（大模型应用创新赛）
> 引擎: DeepSeek Chat · 架构: ReAct 多工具 Agent

---

## 📋 作品简介

GrowthOS 是一个基于 **ReAct（Reasoning + Acting）** 范式的多工具智能体系统。它不只是简单的问答，而是能：

1. **理解用户目标** — 分析你的技能、时间、需求
2. **自主调用工具** — 从 4 个专业工具中按需选择
3. **多步推理执行** — 一步步完成任务，直到给出完整方案
4. **输出可执行计划** — 生成 4 周个性化成长计划

---

## 🧠 技术架构

```
用户输入
    │
    ▼
┌──────────────────────────────────────────┐
│           🔁 ReAct 循环                   │
│                                           │
│  思考(Thought) → 行动(Action) → 观察(Obs)  │
│         ↓                ↑                │
│   调用 DeepSeek  ←───  工具执行结果        │
└──────────────────────────────────────────┘
    │            │           │           │
    ▼            ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ 推荐    │ │ 计算    │ │ 拆解    │ │ 鼓励    │
│ 课程    │ │ 时间    │ │ 计划    │ │ 用户    │
└────────┘ └────────┘ └────────┘ └────────┘
```

### Agent 三要素

| 要素 | 实现 | 说明 |
|------|------|------|
| 🧠 **LLM 大脑** | DeepSeek Chat | 负责推理和决策 |
| 🔧 **工具（手）** | 4 个 Python 函数 | 推荐课程 / 算时间 / 拆计划 / 鼓励 |
| 🔁 **ReAct 循环** | 自实现 while 循环 | 想→做→看→再想，最多 10 步 |

---

## 🛠️ 工具列表

| 工具 | 功能 | 触发场景 |
|------|------|---------|
| `recommend_courses` | 推荐学习资源 | 用户想学某个技能 |
| `calculate_time` | 计算可用时间 | 用户给出时间安排 |
| `split_plan` | 拆解为周计划 | 需要制定长期计划 |
| `motivation_boost` | 鼓励与调整 | 用户说累/烦/迷茫 |

---

## 🚀 运行方式

```bash
# 1. 安装依赖
pip install requests python-dotenv

# 2. 配置 API Key
echo "DEEPSEEK_API_KEY=你的key" > .env

# 3. 运行
python react_agent.py
```

运行后输入你的情况即可：

```
📝 描述你的情况：
> 我是大二学生，想学AI Agent开发，工作日晚上2小时，周末6小时
```

---

## 📚 技术亮点

- ✅ **真·ReAct 循环** — 不是预设流程，Agent 自己决定调用哪个工具
- ✅ **结构化数据传递** — Agent 间通过 JSON 传递数据
- ✅ **安全机制** — `max_steps` 防无限循环，error 回传防崩溃
- ✅ **可扩展** — 加一个新工具只需 10 行代码
- ✅ **本地优先** — API Key 通过 `.env` 配置，不硬编码

---

## 📁 项目结构

```
growth_os_v2/
├── react_agent.py      ← ⭐ 主程序（ReAct Agent）
├── app.py              ← Web 界面版（Streamlit）
├── core/
│   ├── agent_engine.py ← Agent 引擎
│   └── orchestrator.py ← 多 Agent 编排
├── .env                ← API Key 配置（不上传）
└── requirements.txt    ← 依赖
```

---

## 📖 学习参考

本作品的实现思路参考了：
- [awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh) — AI Agent 学习路线图
- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al. 2022)

---

## 🔗 关联仓库

- 练习代码: [agent-learning](https://github.com/qian253/agent-learning)
- 参赛作品: 当前仓库
