import pytest

from simple_calculator import (
    add,
    subtract
)

def test_add():
    assert add(1, 2) == 3

def test_subtract():
    assert subtract(4, 2) == 2

def test_add_too_large_input():
    with pytest.raises(ValueError):
        add(10, 5)

def test_subtract_zero():
    assert subtract(5, 0) == 5

def test_list_tasks(capsys):
    tasks = ["task1", "task2"]
    add_task(tasks, "task3")
    captured = capsys.readouterr()
    assert 'task1' in captured.out
    assert 'task2' in captured.out
    assert 'task3' in captured.out

def test_remove_task():
    tasks = ["task1", "task2"]
    remove_task(tasks, "task1")
    assert "task1" not in tasks
    assert "task2" in tasks

def test_mark_task_as_completed():
    tasks = ["task1", "task2"]
    add_task(tasks, "task3")
    assert "task3" not in tasks
    mark_task_as_completed(tasks, "task1")
    assert "task1" in tasks

# If needed to test other specific cases or behaviors...