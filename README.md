# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Scheduler` class has been extended with four features beyond basic priority-based scheduling:

**Sorting by time** — `sort_by_time()` reorders `scheduled_tasks` by their `"HH:MM"` start time using numeric comparison, so `"9:00"` correctly sorts before `"10:00"`. Tasks with no time set are moved to the end.

**Filtering** — `filter_tasks(pet_name, completed)` returns a subset of scheduled tasks in a single pass. Both parameters are optional and can be combined — e.g. incomplete tasks for a specific pet only.

**Recurring tasks** — `Task` now supports a `recurrence` field (`"none"`, `"daily"`, `"weekly"`). When `mark_complete()` is called on a recurring task, it returns a new `Task` instance with `due_date` set to the next occurrence via `timedelta`, which the caller can add back to the pet.

**Conflict detection** — `detect_conflicts()` checks all scheduled tasks with a time set and returns a list of human-readable warning strings for any two tasks sharing the same start time. It never raises an exception or modifies state.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
