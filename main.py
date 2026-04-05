from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup Owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Add Tasks to Mochi ---
mochi.add_task(Task(task_id=1, title="Morning walk",    duration_minutes=30, priority="high",   pet_name="Mochi"))
mochi.add_task(Task(task_id=2, title="Brush fur",       duration_minutes=15, priority="medium", pet_name="Mochi"))

# --- Add Tasks to Luna ---
luna.add_task(Task(task_id=3, title="Clean litter box", duration_minutes=10, priority="high",   pet_name="Luna"))
luna.add_task(Task(task_id=4, title="Play session",     duration_minutes=20, priority="low",    pet_name="Luna"))
luna.add_task(Task(task_id=5, title="Vet medication",   duration_minutes=5,  priority="high",   pet_name="Luna"))

# --- Register Pets with Owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Run Scheduler ---
scheduler = Scheduler(owner=owner)
scheduler.generate()

# --- Print Today's Schedule ---
print("=" * 45)
print("           TODAY'S SCHEDULE")
print("=" * 45)
print(scheduler.explain())
print("=" * 45)
