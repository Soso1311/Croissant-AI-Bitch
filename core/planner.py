from enum import Enum
from typing import List, Optional

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SubTask:
    def __init__(self, task_id: int, description: str):
        self.id = task_id
        self.description = description
        self.status = TaskStatus.PENDING
        self.result: Optional[str] = None

class ExecutionPlan:
    """State graph that coordinates goal decomposition and execution tracking."""

    def __init__(self, goal: str):
        self.goal = goal
        self.tasks: List[SubTask] = []

    def set_tasks(self, task_list: List[str]):
        self.tasks = [SubTask(i + 1, desc) for i, desc in enumerate(task_list)]

    def render(self) -> str:
        if not self.tasks:
            return "Plan status: Uninitialized."
        output = f"GOAL: {self.goal}\n"
        for t in self.tasks:
            icon = "⏳" if t.status == TaskStatus.PENDING else ("🔄" if t.status == TaskStatus.IN_PROGRESS else ("✅" if t.status == TaskStatus.COMPLETED else "❌"))
            output += f"  [{icon}] Task {t.id}: {t.description} ({t.status.value})\n"
        return output
