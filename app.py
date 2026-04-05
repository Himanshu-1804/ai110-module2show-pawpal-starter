from pawpal_system import Task, Pet, Owner, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state vault — only create objects if they don't already exist.
# Streamlit reruns the entire script on every interaction, so without this
# check every widget interaction would reset the Owner, Pet, and task list.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet info
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=90)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

if st.button("Save Owner & Pet"):
    pet = Pet(name=pet_name, species=species, age=age)
    owner = Owner(name=owner_name, available_minutes=available_minutes)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.task_counter = 0
    st.success(f"Saved {owner_name} with pet {pet_name}!")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Task management
# ---------------------------------------------------------------------------
st.subheader("Tasks")

if st.session_state.pet is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        st.session_state.task_counter += 1
        new_task = Task(
            task_id=st.session_state.task_counter,
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            pet_name=st.session_state.pet.name,
        )
        st.session_state.pet.add_task(new_task)
        st.success(f"Added task: {task_title}")

    current_tasks = st.session_state.pet.get_tasks()
    if current_tasks:
        st.write("Current tasks:")
        st.table([
            {"title": t.title, "duration_minutes": t.duration_minutes, "priority": t.priority}
            for t in current_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an owner and pet first.")
    elif not st.session_state.pet.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner)
        scheduler.generate()
        st.success("Schedule generated!")
        st.text(scheduler.explain())
