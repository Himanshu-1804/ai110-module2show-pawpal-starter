import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(task_id=1, title="Walk", duration=30, priority="medium",
              pet_name="Mochi", time="", recurrence="none", completed=False):
    return Task(
        task_id=task_id,
        title=title,
        duration_minutes=duration,
        priority=priority,
        pet_name=pet_name,
        time=time,
        recurrence=recurrence,
        completed=completed,
    )


def make_scheduler(available_minutes=120, tasks_per_pet=None):
    """Return a Scheduler with one pet (Mochi) pre-loaded with the given tasks."""
    owner = Owner(name="Jordan", available_minutes=available_minutes)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    if tasks_per_pet:
        for t in tasks_per_pet:
            pet.add_task(t)
    scheduler = Scheduler(owner=owner)
    scheduler.generate()
    return scheduler


# ---------------------------------------------------------------------------
# Original tests (preserved)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(task_id=1, title="Morning walk", duration_minutes=30, priority="high", pet_name="Mochi")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(task_id=1, title="Morning walk", duration_minutes=30, priority="high", pet_name="Mochi"))
    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# 1. SORTING CORRECTNESS
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """Tasks with explicit times must come out in HH:MM ascending order."""
    t1 = make_task(task_id=1, title="Evening walk",  time="18:00")
    t2 = make_task(task_id=2, title="Morning brush", time="09:30")
    t3 = make_task(task_id=3, title="Noon meds",     time="12:00")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2, t3])
    scheduler.sort_by_time()

    times = [t.time for t in scheduler.scheduled_tasks]
    assert times == ["09:30", "12:00", "18:00"]


def test_sort_by_time_untimed_tasks_go_to_end():
    """Tasks with time='' must always appear after all timed tasks."""
    timed   = make_task(task_id=1, title="Meds",  time="08:00")
    untimed = make_task(task_id=2, title="Brush", time="")

    scheduler = make_scheduler(tasks_per_pet=[untimed, timed])
    scheduler.sort_by_time()

    assert scheduler.scheduled_tasks[0].time == "08:00"
    assert scheduler.scheduled_tasks[1].time == ""


def test_sort_by_time_all_untimed_no_crash():
    """Sorting a list where every task has time='' must not raise."""
    tasks = [make_task(task_id=i, title=f"Task {i}") for i in range(1, 4)]
    scheduler = make_scheduler(tasks_per_pet=tasks)
    scheduler.sort_by_time()   # should not raise
    assert len(scheduler.scheduled_tasks) == 3


def test_sort_by_time_mixed_timed_and_untimed():
    """Mixed list: timed tasks appear first in order, untimed at the end."""
    t1 = make_task(task_id=1, title="Late walk",   time="20:00")
    t2 = make_task(task_id=2, title="No-time task", time="")
    t3 = make_task(task_id=3, title="Early feed",  time="07:00")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2, t3])
    scheduler.sort_by_time()

    result_times = [t.time for t in scheduler.scheduled_tasks]
    assert result_times == ["07:00", "20:00", ""]


# ---------------------------------------------------------------------------
# 2. RECURRENCE LOGIC
# ---------------------------------------------------------------------------

def test_mark_complete_daily_returns_next_day_task():
    """Daily task: returned task due_date must be today + 1 day."""
    task = make_task(recurrence="daily")
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_mark_complete_weekly_returns_next_week_task():
    """Weekly task: returned task due_date must be today + 7 days."""
    task = make_task(recurrence="weekly")
    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_mark_complete_non_recurring_returns_none():
    """Non-recurring task must return None (no follow-up task created)."""
    task = make_task(recurrence="none")
    result = task.mark_complete()
    assert result is None


def test_mark_complete_recurring_preserves_fields():
    """The new recurring task must inherit all original fields (not reset them)."""
    task = make_task(
        task_id=7, title="Evening walk", duration=45,
        priority="high", pet_name="Luna",
        time="18:00", recurrence="daily",
    )
    next_task = task.mark_complete()

    assert next_task.task_id         == task.task_id
    assert next_task.title           == task.title
    assert next_task.duration_minutes == task.duration_minutes
    assert next_task.priority        == task.priority
    assert next_task.pet_name        == task.pet_name
    assert next_task.time            == task.time
    assert next_task.recurrence      == task.recurrence


def test_mark_complete_recurring_new_task_not_completed():
    """The newly created recurring task must start with completed=False."""
    task = make_task(recurrence="weekly")
    next_task = task.mark_complete()
    assert next_task.completed == False


# ---------------------------------------------------------------------------
# 3. CONFLICT DETECTION
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_time():
    """Two tasks at the same time must produce exactly one conflict warning."""
    t1 = make_task(task_id=1, title="Meds",  time="07:00", pet_name="Mochi")
    t2 = make_task(task_id=2, title="Walk",  time="07:00", pet_name="Luna")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2])
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "07:00" in warnings[0]
    assert "Meds"  in warnings[0]
    assert "Walk"  in warnings[0]


def test_detect_conflicts_three_way_produces_three_warnings():
    """Three tasks sharing a time slot must produce 3 pair-wise warnings (AB, AC, BC)."""
    t1 = make_task(task_id=1, title="A", time="09:00")
    t2 = make_task(task_id=2, title="B", time="09:00")
    t3 = make_task(task_id=3, title="C", time="09:00")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2, t3])
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 3


def test_detect_conflicts_unique_times_no_warnings():
    """No two tasks share a time — conflict list must be empty."""
    t1 = make_task(task_id=1, time="08:00")
    t2 = make_task(task_id=2, time="09:00")
    t3 = make_task(task_id=3, time="10:00")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2, t3])
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_empty_time():
    """Tasks with time='' must never be flagged as conflicts with each other."""
    t1 = make_task(task_id=1, title="Task A", time="")
    t2 = make_task(task_id=2, title="Task B", time="")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2])
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_does_not_mutate_scheduled_tasks():
    """detect_conflicts() must not modify scheduled_tasks (read-only)."""
    t1 = make_task(task_id=1, time="07:00")
    t2 = make_task(task_id=2, time="07:00")

    scheduler = make_scheduler(tasks_per_pet=[t1, t2])
    original_ids = [t.task_id for t in scheduler.scheduled_tasks]

    scheduler.detect_conflicts()

    assert [t.task_id for t in scheduler.scheduled_tasks] == original_ids


# ---------------------------------------------------------------------------
# 4. SCHEDULER GENERATE — time budget edge cases
# ---------------------------------------------------------------------------

def test_generate_exact_budget_fit():
    """A task whose duration equals available_minutes exactly must be scheduled."""
    task = make_task(duration=60)
    scheduler = make_scheduler(available_minutes=60, tasks_per_pet=[task])
    assert len(scheduler.scheduled_tasks) == 1


def test_generate_exceeds_budget_by_one_minute_excluded():
    """A task 1 minute over budget must not appear in scheduled_tasks."""
    task = make_task(duration=61)
    scheduler = make_scheduler(available_minutes=60, tasks_per_pet=[task])
    assert len(scheduler.scheduled_tasks) == 0


def test_generate_skips_completed_tasks():
    """Completed tasks must never appear in scheduled_tasks."""
    done = make_task(task_id=1, title="Done task", completed=True)
    todo = make_task(task_id=2, title="Pending task", completed=False)

    scheduler = make_scheduler(tasks_per_pet=[done, todo])
    titles = [t.title for t in scheduler.scheduled_tasks]

    assert "Done task"    not in titles
    assert "Pending task" in titles


def test_generate_priority_ordering():
    """Scheduled tasks must appear high → medium → low."""
    low  = make_task(task_id=1, title="Low",  priority="low",    duration=10)
    med  = make_task(task_id=2, title="Med",  priority="medium", duration=10)
    high = make_task(task_id=3, title="High", priority="high",   duration=10)

    scheduler = make_scheduler(available_minutes=30, tasks_per_pet=[low, med, high])
    priorities = [t.priority for t in scheduler.scheduled_tasks]

    assert priorities == ["high", "medium", "low"]


def test_generate_zero_available_minutes():
    """Owner with 0 available minutes must produce an empty schedule."""
    task = make_task(duration=5)
    scheduler = make_scheduler(available_minutes=0, tasks_per_pet=[task])
    assert scheduler.scheduled_tasks == []


def test_generate_collects_tasks_from_multiple_pets():
    """generate() must pull tasks from all pets, not just the first one."""
    owner = Owner(name="Jordan", available_minutes=120)

    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna",  species="cat", age=5)

    pet1.add_task(make_task(task_id=1, title="Dog walk",  pet_name="Mochi", duration=30))
    pet2.add_task(make_task(task_id=2, title="Cat meds",  pet_name="Luna",  duration=10))

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner=owner)
    scheduler.generate()

    pet_names = {t.pet_name for t in scheduler.scheduled_tasks}
    assert "Mochi" in pet_names
    assert "Luna"  in pet_names


# ---------------------------------------------------------------------------
# 5. FILTER TASKS
# ---------------------------------------------------------------------------

def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) must return only tasks for that pet."""
    owner = Owner(name="Jordan", available_minutes=120)

    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna",  species="cat", age=5)

    pet1.add_task(make_task(task_id=1, title="Dog walk", pet_name="Mochi", duration=20))
    pet2.add_task(make_task(task_id=2, title="Cat meds", pet_name="Luna",  duration=10))

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner=owner)
    scheduler.generate()

    result = scheduler.filter_tasks(pet_name="Mochi")
    assert all(t.pet_name == "Mochi" for t in result)
    assert len(result) == 1


def test_filter_tasks_completed_false_excludes_done():
    """filter_tasks(completed=False) must exclude completed tasks."""
    done    = make_task(task_id=1, title="Done",    completed=True,  duration=10)
    pending = make_task(task_id=2, title="Pending", completed=False, duration=10)

    scheduler = make_scheduler(tasks_per_pet=[done, pending])
    # Manually mark the done task so it's in scheduled_tasks but completed
    for t in scheduler.scheduled_tasks:
        if t.title == "Done":
            t.completed = True

    result = scheduler.filter_tasks(completed=False)
    assert all(not t.completed for t in result)


def test_filter_tasks_no_args_returns_all():
    """filter_tasks() with no arguments must return every scheduled task."""
    tasks = [make_task(task_id=i, title=f"Task {i}", duration=10) for i in range(1, 4)]
    scheduler = make_scheduler(available_minutes=60, tasks_per_pet=tasks)

    result = scheduler.filter_tasks()
    assert len(result) == len(scheduler.scheduled_tasks)


def test_filter_tasks_combined_pet_and_completed():
    """filter_tasks(pet_name=..., completed=False) must apply both filters."""
    owner = Owner(name="Jordan", available_minutes=120)

    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna",  species="cat", age=5)

    pet1.add_task(make_task(task_id=1, title="Dog walk", pet_name="Mochi", duration=20))
    pet2.add_task(make_task(task_id=2, title="Cat meds", pet_name="Luna",  duration=10))

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner=owner)
    scheduler.generate()

    result = scheduler.filter_tasks(pet_name="Luna", completed=False)
    assert all(t.pet_name == "Luna" and not t.completed for t in result)


def test_filter_tasks_nonexistent_pet_returns_empty():
    """Filtering by a pet name that doesn't exist must return an empty list."""
    task = make_task()
    scheduler = make_scheduler(tasks_per_pet=[task])

    result = scheduler.filter_tasks(pet_name="GhostPet")
    assert result == []


# ---------------------------------------------------------------------------
# 6. PET — remove_task edge cases
# ---------------------------------------------------------------------------

def test_remove_task_removes_correct_task():
    """remove_task must delete only the matching task_id."""
    pet = Pet(name="Mochi", species="dog", age=3)
    t1 = make_task(task_id=1, title="Walk")
    t2 = make_task(task_id=2, title="Feed")
    pet.add_task(t1)
    pet.add_task(t2)

    pet.remove_task(1)

    remaining_ids = [t.task_id for t in pet.get_tasks()]
    assert 1 not in remaining_ids
    assert 2 in remaining_ids


def test_remove_task_nonexistent_id_is_noop():
    """Removing a task_id that doesn't exist must leave the list unchanged."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = make_task(task_id=5)
    pet.add_task(task)

    pet.remove_task(999)   # should not raise or remove anything

    assert len(pet.get_tasks()) == 1
