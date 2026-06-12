"""
The Agent Loop
 
用一种模式概括 AI 编程智能体的全部秘诀:

    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results

    +----------+      +-------+      +---------+
    |   User   | ---> |  LLM  | ---> |  Tool   |
    |  prompt  |      |       |      | execute |
    +----------+      +---+---+      +----+----+
                          ^               |
                          |   tool_result |
                          +---------------+
                          (loop continues)

核心循环：将工具的执行结果重新反馈给模型，直到模型决定停止
在此基础上，生产环境中的 Agent 还会叠加策略（Policy）、钩子机制（Hooks）以及生命周期控制（Lifecycle Controls）等功能。

用法:
    pip install anthropic python-dotenv
    ANTHROPIC_API_KEY=... python s01_agent_loop/code.py
"""


"""
两个While True循环, 内循环用于Agent loop, LLM自己决定何时使用工具何时停止(核心循环), 外循环用于多轮对话
"""


import os
import subprocess  # Python 标准库中用于创建和管理子进程的模块

# macOS 的 libedit 在处理中文输入时有退格问题，这四行修复它（libedit 在处理中文等多字节字符时，按退格键可能无法正确删除字符）
# 确保在 macOS/Linux 终端中输入中文时，退格键能正常工作
try:
    import readline
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]

SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."

# 终端工具定义
TOOLS = [{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}]

# ✅️
# 执行终端工具
def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
                            command, 
                            shell=True,  # 通过 shell 解释器执行（支持管道、通配符等）
                            cwd=os.getcwd(),  # 在当前工作目录执行
                            capture_output=True,  # 捕获标准输出和标准错误
                            text=True,  # 输出以字符串形式返回（而非字节）
                            timeout=120  # 超时时间 120 秒
                        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"

# ✅️
# 核心循环
def agent_loop(messages: list):
    while True:
        response = client.messages.create(
                                            model=MODEL, 
                                            system=SYSTEM, 
                                            messages=messages,
                                            tools=TOOLS, 
                                            max_tokens=8000,
                                        )

        # Append assistant turn
        messages.append({"role": "assistant", "content": response.content})

        # If the model didn't call a tool, we're done
        if response.stop_reason != "tool_use":
            return

        # Execute each tool call, collect results
        results = []
        for block in response.content:
            if block.type == "tool_use":
                # ANSI 转义码 ，用于在终端中输出 彩色文本; \033[33m -> 设置文字为黄色, $ {block.input['command']} -> 要打印的命令内容, \033[0m -> 重置颜色（恢复默认）
                print(f"\033[33m$ {block.input['command']}\033[0m")
                output = run_bash(block.input["command"])
                print(output[:200])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

        # Feed tool results back, loop continues
        messages.append({"role": "user", "content": results})

if __name__ == "__main__":
    print("s01: Agent Loop")
    print("输入问题，回车发送。输入 q 退出。\n")

    history = []
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)
        # Print the model's final text response
        response_content = history[-1]["content"]
        if isinstance(response_content, list):
            for block in response_content:
                if getattr(block, "type", None) == "text":
                    print(block.text)
        print()