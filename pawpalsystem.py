from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    completed: bool = False

    def edit(self, title: str, duration_minutes: int, priority: str) -> None:
        pass

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", "other"
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> List[Pet]:
        pass


@dataclass
class Schedule:
    owner: Owner
    scheduled_tasks: List[Task] = field(default_factory=list)

    def generate(self, tasks: List[Task], available_minutes: int) -> None:
        pass

    def explain(self) -> str:
        pass
