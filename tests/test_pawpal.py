import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
