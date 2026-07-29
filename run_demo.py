import sys, json

# 修复 Windows 终端编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

user_input = (
    "我是大二计算机学生，Python还可以(3/5)，"
    "想学AI Agent开发，工作日晚上能学2小时，"
    "周末下午6小时，喜欢动手做项目。最大的问题是坚持不下来。"
)

print("*" * 50)
print("  GrowthOS v2 - 多Agent流水线")
print("*" * 50)

print()
print("*" * 50)
print("  Agent 1/3: 用户画像分析")
print("*" * 50)
print()
print(f"输入: {user_input[:60]}...")
print()
print("需要 AI 引擎处理 (我) ...")

print()
print("*" * 50)
print("  请把下面内容发给我")
print("*" * 50)
print()
print("【用户输入】")
print(user_input)
print()
print("请以GrowthOS的三个Agent身份依次分析我的情况：")
print("1. 首先作为用户画像分析师，提取我的结构化信息")
print("2. 然后作为智能规划师，生成4周计划")
print("3. 最后整合输出完整报告")
