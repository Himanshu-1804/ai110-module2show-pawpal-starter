from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup Owner ---
owner = Owner(name="Jordan", available_minutes=120)

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Add Tasks to Mochi (intentionally out of time order) ---
mochi.add_task(Task(task_id=1, title="Evening walk",    duration_minutes=30, priority="high",   pet_name="Mochi", time="18:00"))
mochi.add_task(Task(task_id=2, title="Brush fur",       duration_minutes=15, priority="medium", pet_name="Mochi", time="09:30"))
mochi.add_task(Task(task_id=3, title="Morning walk",    duration_minutes=20, priority="high",   pet_name="Mochi", time="07:00"))

# --- Add Tasks to Luna (intentionally out of time order) ---
# task_id=4 is deliberately set to "07:00" — same slot as Mochi's Morning walk (conflict)
luna.add_task(Task(task_id=4, title="Vet medication",   duration_minutes=5,  priority="high",   pet_name="Luna",  time="07:00"))  # conflicts with task_id=3
luna.add_task(Task(task_id=5, title="Clean litter box", duration_minutes=10, priority="high",   pet_name="Luna",  time=""))       # no time set
luna.add_task(Task(task_id=6, title="Play session",     duration_minutes=20, priority="low",    pet_name="Luna",  time="14:00"))

# --- Mark one task complete to demonstrate status filtering ---
luna.get_tasks()[1].mark_complete()  # "Clean litter box" is done

# --- Register Pets with Owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Run Scheduler ---
scheduler = Scheduler(owner=owner)
scheduler.generate()

SEP = "=" * 45

# --- 1. Full schedule (priority order, as generated) ---
print(SEP)
print("       SCHEDULE (priority order)")
print(SEP)
print(scheduler.explain())
print()

# --- 2. Sort by time, then reprint ---
scheduler.sort_by_time()
print(SEP)
print("       SCHEDULE (sorted by time)")
print(SEP)
for task in scheduler.scheduled_tasks:
    time_label = task.time if task.time else "(no time)"
    print(f"  {time_label}  [{task.priority.upper()}] {task.title} ({task.pet_name}) — {task.duration_minutes} min")
print()

# --- 3. Filter: Mochi's tasks only ---
print(SEP)
print("       FILTER: Mochi's tasks")
print(SEP)
for task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"  [{task.priority.upper()}] {task.title} — {task.duration_minutes} min")
print()

# --- 4. Filter: incomplete tasks only ---
print(SEP)
print("       FILTER: incomplete tasks")
print(SEP)
for task in scheduler.filter_tasks(completed=False):
    print(f"  {task.pet_name}: {task.title} — {task.duration_minutes} min")
print()

# --- 5. Filter: incomplete Mochi tasks ---
print(SEP)
print("       FILTER: Mochi — incomplete only")
print(SEP)
for task in scheduler.filter_tasks(pet_name="Mochi", completed=False):
    print(f"  {task.title} — {task.duration_minutes} min")
print(SEP)
print()

# --- 6. Conflict detection ---
print(SEP)
print("       CONFLICT DETECTION")
print(SEP)
conflicts = scheduler.detect_conflicts()
if conflicts:
    print("WARNING: The following tasks are scheduled at the same time:")
    for warning in conflicts:
        print(warning)
else:
    print("No conflicts detected.")
print(SEP)
