from dataclasses import dataclass, field
from typing import List

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    task_id: int
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    pet_name: str
    completed: bool = False

    def edit(self, title: str, duration_minutes: int, priority: str) -> None:
        """Update the task's title, duration, and priority in place."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", "other"
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove the task matching the given task_id from this pet's list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets


@dataclass
class Scheduler:
    owner: Owner
    scheduled_tasks: List[Task] = field(default_factory=list)

    def generate(self) -> None:
        """Collect all incomplete tasks from the owner's pets and schedule them by priority within the available time."""
        all_tasks = []
        for pet in self.owner.get_pets():
            all_tasks.extend(pet.get_tasks())

        all_tasks.sort(key=lambda t: PRIORITY_ORDER[t.priority])

        time_remaining = self.owner.available_minutes
        self.scheduled_tasks = []
        for task in all_tasks:
            if not task.completed and task.duration_minutes <= time_remaining:
                self.scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes

    def explain(self) -> str:
        """Return a human-readable summary of the scheduled tasks and total time used."""
        if not self.scheduled_tasks:
            return "No tasks scheduled. Run generate() first."

        lines = [f"Schedule for {self.owner.name} ({self.owner.available_minutes} min available):\n"]
        time_used = 0
        for task in self.scheduled_tasks:
            lines.append(
                f"  [{task.priority.upper()}] {task.title} ({task.pet_name}) — {task.duration_minutes} min"
            )
            time_used += task.duration_minutes

        lines.append(f"\nTotal time used: {time_used} / {self.owner.available_minutes} min")
        return "\n".join(lines)

    def clear(self) -> None:
        """Reset the scheduled task list so generate() can be re-run cleanly."""
        self.scheduled_tasks = []
