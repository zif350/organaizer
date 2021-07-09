import os
import sys
import pytest
import mysql


sys.path.append(os.path.abspath('../'))


from mysql_class import MySQL
from user_class import User
from task_class import Task



@pytest.fixture()
def new_user():
    return User(name="userfortest", password="12345678Ll", registration=True)


@pytest.fixture()
def existing_user():
    return User(name="userfortest", password="12345678Ll")


def test_select_data(new_user):
    expected_data = [(new_user.name, new_user.password, new_user._task_table)]
    selected_data = new_user._db.select_data(table=new_user.TABLE_NAME, condition=f"name='{new_user.name}'")
    assert expected_data == selected_data
    new_user.delete_user()


def test_delete_from_db_and_drop_table(new_user):
    new_user._db.drop_table(table_name=new_user._task_table)
    new_user._db.delete(table_name=new_user.TABLE_NAME, condition=f"name='{new_user.name}'")
    # checks the database for the presence of a new_user with this name
    selected_user = new_user._db.select_data(table=new_user.TABLE_NAME, condition=f"name='{new_user.name}'")
    assert selected_user == []
    # checks the database for the presence of a table with new_user tasks
    with pytest.raises(expected_exception=(mysql.connector.errors.ProgrammingError, )):
        new_user._db.select_data(table=new_user._task_table)


def test_update_task(new_user):
    Task(date="2021-07-10", short_name="test", description="test update task", task_table_name=new_user._task_table)
    condition = "id='1'"
    data = new_user._db.select_data(condition=condition, table=new_user._task_table)
    new_user._db.update_task_complete(table=new_user._task_table ,condition=condition, cl="'checked'")
    updated_data = new_user._db.select_data(condition=condition, table=new_user._task_table)
    assert updated_data[0][4] == "checked"
    new_user.delete_user()


def test_insert_data(existing_user):
    db = MySQL(database_name=existing_user.DATABASE_NAME)
    values = (existing_user.name, existing_user.password, existing_user._task_table)
    db.insert_data(table=existing_user.TABLE_NAME, values=values)
    selected_data = db.select_data(table=existing_user.TABLE_NAME, condition=f"name='{existing_user.name}'")
    assert selected_data[0] == values
    existing_user._db.create_tasks_table(table_name=existing_user._task_table)
    existing_user.delete_user()




