from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    task_id: int
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    pet_name: str
    completed: bool = False
    time: str = ""  # scheduled start time in "HH:MM" format, e.g. "08:30"
    recurrence: str = "none"  # "none", "daily", or "weekly"
    due_date: Optional[date] = None  # date this task is due; None means unscheduled

    def edit(self, title: str, duration_minutes: int, priority: str) -> None:
        """Update the task's title, duration, and priority in place."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed.

        For recurring tasks, returns a new Task instance due on the next
        occurrence (today + 1 day for 'daily', today + 7 days for 'weekly').
        Returns None for non-recurring tasks.
        """
        self.completed = True

        if self.recurrence == "daily":
            next_due = date.today() + timedelta(days=1)
        elif self.recurrence == "weekly":
            next_due = date.today() + timedelta(weeks=1)
        else:
            return None

        return Task(
            task_id=self.task_id,
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_name=self.pet_name,
            time=self.time,
            recurrence=self.recurrence,
            due_date=next_due,
        )


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

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> List[Task]:
        """Return a filtered view of scheduled_tasks.

        Args:
            pet_name:  If provided, only return tasks belonging to this pet.
            completed: If True, return only completed tasks.
                       If False, return only incomplete tasks.
                       If None, completion status is ignored.
        """
        return [
            t for t in self.scheduled_tasks
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def detect_conflicts(self) -> List[str]:
        """Check scheduled_tasks for time slot collisions.

        Two tasks conflict when both have the same non-empty 'time' value.
        Returns a list of human-readable warning strings — one per conflicting
        pair.  An empty list means no conflicts were found.  The scheduler is
        never modified; this is a read-only check.
        """
        warnings: List[str] = []

        timed = [t for t in self.scheduled_tasks if t.time]

        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                if timed[i].time == timed[j].time:
                    warnings.append(
                        f"  CONFLICT at {timed[i].time}: "
                        f'"{timed[i].title}" ({timed[i].pet_name}) '
                        f'overlaps with '
                        f'"{timed[j].title}" ({timed[j].pet_name})'
                    )

        return warnings

    def sort_by_time(self) -> None:
        """Sort scheduled_tasks in place by their 'time' field (HH:MM strings).
        Tasks with no time set ("") are moved to the end."""
        self.scheduled_tasks.sort(
            key=lambda t: (t.time == "", tuple(int(x) for x in t.time.split(":")) if t.time else ())
        )

    def clear(self) -> None:
        """Reset the scheduled task list so generate() can be re-run cleanly."""
        self.scheduled_tasks = []
