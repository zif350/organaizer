import os
import sys
import pytest


sys.path.append(os.path.abspath('../'))


from user_class import User, NameTooLong, PasswordTooShort
from task_class import Task


@pytest.fixture()
def existing_user():
    return User(name="Yasha", password="12345678Ll")


@pytest.fixture()
def new_user():
    return  User(name="Yasha", password="12345678Ll", registration=True)


@pytest.fixture()
def tasks(new_user):
    first_task = Task(date="2021-07-10", short_name="task_1", description="task_1", task_table_name=new_user._task_table)
    second_task = Task(date="2021-07-10", short_name="task_2", description="task_2", task_table_name=new_user._task_table)
    return [first_task, second_task]


def test_basic(existing_user):
    assert existing_user.name == "Yasha"
    assert existing_user.password == "12345678Ll"


def test_raises_exception_on_long_name(existing_user):
    with pytest.raises(expected_exception=(NameTooLong, )):
        existing_user.name = existing_user.name * 10


def test_raises_exception_on_short_password(existing_user):
    with pytest.raises(expected_exception=(PasswordTooShort, )):
        existing_user.password = "12345Ll"


def test_turning_task_in_json(new_user, tasks):
    expected_json_data = [{"id": 1, "date": tasks[0].date, "short_name": tasks[0].short_name,
                      "description": tasks[0].description, "complete": tasks[0].complete},
                     {"id": 2, "date": tasks[1].date, "short_name": tasks[1].short_name,
                      "description": tasks[1].description, "complete": tasks[1].complete}
                     ]
    json_data = new_user.turning_task_in_json(date=tasks[0].date)
    assert json_data == expected_json_data
    new_user.delete_user()
