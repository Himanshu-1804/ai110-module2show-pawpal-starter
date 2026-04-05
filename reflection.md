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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
