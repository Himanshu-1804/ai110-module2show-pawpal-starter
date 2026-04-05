# PawPal+ Project Reflection

## 1. System Design

1. Let a user enter basic owner + pet info
2. Let a user add/edit tasks, along with that task's duration and priority.
3. Generate a daily schedule/plan based on constraints and priorities.

Objects needed:

Owner Object -> Properties of the basic owner.
- Methods: `add_pet(pet)`, `get_pets()`

Pet Object -> Keep track of pet info.
- Methods: `add_task(task)`, `remove_task(task)`, `get_tasks()`

Task Object -> Properties of an individual task.
- Methods: `edit(title, duration_minutes, priority)`, `mark_complete()`

Schedule Object -> Keep track of the day's schedule.
- Methods: `generate(tasks, available_minutes)`, `explain()`

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Ans. This was the initial UML design that I had:

classDiagram
    class Owner {
        +String name
        +int available_minutes
        +List~Pet~ pets
        +add_pet(pet)
        +get_pets()
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~Task~ tasks
        +add_task(task)
        +remove_task(task)
        +get_tasks()
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +bool completed
        +edit(title, duration_minutes, priority)
        +mark_complete()
    }

    class Schedule {
        +Owner owner
        +List~Task~ scheduled_tasks
        +generate(tasks, available_minutes)
        +explain()
    }

    Owner "1" --> "0..*" Pet : has
    Pet "1" --> "0..*" Task : has
    Schedule "1" --> "1" Owner : uses
    Schedule "1" --> "0..*" Task : selects

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Ans. Yes, my design changed during implementation. One change was that there was no Path from Schedule to Pet. I modified the method generate in the Schedule class so that it takes no parameters. Hence, it now navigates self.owner.get_pets() internally.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Ans. The scheduler considers two constraints: total available time (tasks are skipped if they would exceed `owner.available_minutes`) and task priority (high-priority tasks are always scheduled before medium or low ones).

Ans. Available time was the most fundamental constraint because no schedule is valid if it exceeds what the owner can actually do, and priority was chosen as the ranking mechanism because pet care tasks like medication and walks have clear urgency differences that the owner needs respected automatically.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Ans. One tradeoff that my scheduler makes is that two tasks conflict only if their time strings are identical (e.g. both "08:00"), which means only during their start time. True overlap detection would require comparing time + duration_minutes ranges.

Ans. The tradeoff is reasonable in this scenario as we have multiple owners.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Ans. I used AI tools across several stages of the project. During the design phase, I used AI to review my initial UML diagram and identify missing relationships. For example, it flagged that I had no path from `Schedule` to `Pet`, which led me to redesign `generate()` to navigate `self.owner.get_pets()` internally rather than accept tasks as a parameter. During implementation, I used AI to help implement `sort_by_time()`, `filter_tasks()`, and `detect_conflicts()`, and to write the automated test suite. Later, I used AI to improve the Streamlit UI, specifically to replace the plain `st.text(scheduler.explain())` output with a structured table that includes a conflict `Status` column.

The most helpful prompts were ones that asked AI to explain *why* before suggesting *what*. For example, asking "how should conflict warnings be presented in Streamlit to be most helpful to a pet owner?" produced a reasoned answer about layering (banner + expander + table column) rather than just dropping in a code snippet.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Ans. When implementing the conflict `Status` column in the schedule table, AI initially suggested extracting the conflicting time slots by parsing the warning strings returned by `detect_conflicts()`, specifically by splitting on `"at "` and slicing characters to recover the `"HH:MM"` value. I did not accept this because it was fragile: it would break silently if the warning string format ever changed, and it was harder to read than the underlying data. Instead, I used a `Counter` on `t.time` directly over the scheduled tasks list to identify which time slots appeared more than once. I verified this was correct by tracing through a small example by hand: two tasks at `"08:00"` and one at `"09:00"` should produce `conflict_times = {"08:00"}`, which the Counter approach gives correctly without touching any strings.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Ans. The test suite in `tests/test_pawpal.py` covers 29 tests across six categories: schedule generation, sorting by time, filtering, recurring tasks, conflict detection, and pet task removal. Specifically:

- **Schedule generation**: verified that tasks fitting exactly within the time budget are included, tasks one minute over are excluded, completed tasks are skipped, output is ordered high → medium → low, a zero-minute budget yields an empty schedule, and tasks from multiple pets are all collected.
- **Sorting**: verified chronological `HH:MM` ordering (catching the lexicographic trap where `"9:00"` would sort after `"10:00"`), that untimed tasks go to the end, and that an all-untimed list does not crash.
- **Filtering**: verified filtering by pet name, by completion status, both combined, neither (returns all), and a nonexistent pet name (returns empty list).
- **Recurrence**: verified that daily completion creates a task due tomorrow, weekly creates one due in 7 days, non-recurring returns `None`, and the new task preserves all fields and starts incomplete.
- **Conflict detection**: verified that same-time tasks produce a warning, three tasks at the same time produce three pairwise warnings, unique times produce no warnings, tasks with `time=""` are never flagged, and scheduler state is never mutated.
- **Pet task removal**: verified that `remove_task()` removes only the matching ID and leaves the list unchanged for a nonexistent ID.

These tests mattered because the scheduling logic is the core value of the app; an error in priority ordering or time budget arithmetic would silently produce wrong schedules, which could cause a pet to miss medication or a walk. Testing at the unit level made it easy to isolate bugs before connecting to the UI.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Ans. I am confident at roughly 4 out of 5 stars. All 29 tests pass, and the core behaviors (priority ordering, time budget cutoff, conflict detection, recurrence chaining, and filtering) are each directly verified. The remaining uncertainty comes from two gaps:

1. **Conflict detection uses start-time matching only.** Two tasks both set to `"07:00"` are flagged as conflicting even if one is 5 minutes and the other is 60 minutes, so they might not actually overlap. Conversely, a 60-minute task at `"07:00"` and a 30-minute task at `"07:45"` would *genuinely* overlap but are not flagged because their start times differ. Testing true time-range overlap would require adding duration-aware conflict logic.
2. **The Streamlit UI has no automated tests.** All UI behavior (the error banner, the expander, the Status column) is verified only by manual inspection.

If I had more time, I would test: duration-aware overlap detection, what happens when `available_minutes` is exactly 0, scheduling across more than two pets, and `mark_complete()` called twice on the same recurring task.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Ans. I am most satisfied with how the scheduling logic turned out as a self-contained, testable system. The four extended features (sorting, filtering, recurrence, conflict detection) each have a single, well-defined responsibility and no side effects, which made them straightforward to test in isolation. Having 29 passing tests gave me real confidence when connecting the backend to the Streamlit UI, because I could change the display code in `app.py` without worrying that I had broken the scheduling logic underneath. The layered conflict warning in the UI (banner, expander, and table `Status` column) is also something I am proud of, because it came from thinking about the user's perspective first rather than just outputting whatever the backend returned.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Ans. I would redesign conflict detection to be duration-aware. Right now, `detect_conflicts()` flags two tasks as conflicting only if their `time` strings are identical. A 5-minute task and a 60-minute task both starting at `"08:00"` are treated the same as two 60-minute tasks at `"08:00"`, even though the first pair might not actually conflict. True overlap detection would compare the interval `[start, start + duration)` for each pair of timed tasks. I would also add a `time` input field to the task form in `app.py` so that conflict detection becomes useful in the UI, since it currently only activates when tasks already have time strings set outside the form.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Ans. The most important thing I learned is that a UML diagram is not just a planning artifact; it is a thinking tool that keeps evolving. My initial diagram had no path from `Schedule` to `Pet`, which looked fine on paper but immediately broke when I tried to implement `generate()`. Fixing the diagram first forced me to understand the ownership chain (Owner holds Pets, Pets hold Tasks) before writing a single line of logic. Working with AI reinforced this: the most useful AI interactions happened when I brought a specific design question, not an open-ended "write this for me." When I asked about the UML gap or how to present conflict warnings, I got structured reasoning I could evaluate. When I just asked for code, I got suggestions I had to verify more carefully, as with the string-parsing approach I rejected in favor of the `Counter` solution.
