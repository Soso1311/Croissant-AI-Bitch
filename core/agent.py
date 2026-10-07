import json
from typing import List, Dict, Any
from openai import OpenAI
import config
from memory.store import MemoryStore
from core.planner import ExecutionPlan
from tools.registry import TOOLS_REGISTRY, TOOL_SCHEMAS

class AutonomousAgent:
    """ReAct execution core with dynamic security filtering and self-repair logic."""

    def __init__(self):
        self.client = OpenAI(base_url=config.OLLAMA_BASE_URL, api_key="ollama")
        self.memory = MemoryStore()

    def run(self, goal: str, max_steps: int = 12) -> str:
        plan = ExecutionPlan(goal=goal)
        memories = self.memory.recall(goal, n_results=2)
        mem_context = "\n".join([f"- {m}" for m in memories]) if memories else "None"

        system_prompt = (
            f"You are Jarvis, an autonomous local AI agent operating within a secure sandbox environment.\n"
            f"Workspace Path: {config.WORKSPACE_DIR}\n\n"
            f"Relevant Memory:\n{mem_context}\n\n"
            f"Rules:\n"
            f"1. Break down complex tasks into subtasks.\n"
            f"2. Use available tools to solve problems step-by-step.\n"
            f"3. When a security refusal or error occurs, adjust your approach and continue.\n"
            f"4. Output your final response clearly once the goal is complete."
        )

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {goal}"}
        ]

        for step in range(1, max_steps + 1):
            print(f"\n🧠 [Step {step}/{max_steps}] Reasoning...")

            try:
                response = self.client.chat.completions.create(
                    model=config.MODEL_NAME,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    temperature=0.2
                )
            except Exception as e:
                return f"Inference engine error: {str(e)}"

            msg = response.choices[0].message
            messages.append(msg)

            if msg.tool_calls:
                for call in msg.tool_calls:
                    fn_name = call.function.name
                    try:
                        args = json.loads(call.function.arguments)
                    except Exception:
                        args = {}

                    print(f"🔧 Tool: {fn_name}({args})")

                    if fn_name in TOOLS_REGISTRY:
                        obs = TOOLS_REGISTRY[fn_name](**args)
                    else:
                        obs = f"Error: Tool '{fn_name}' not found."

                    print(f"👁️ Result: {str(obs)[:200]}...")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(obs)
                    })
            else:
                final_res = msg.content or "Task completed."
                self.memory.save(f"Goal: {goal} | Result: {final_res[:200]}")
                return final_res

        return "Max execution steps reached."
