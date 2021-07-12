import pytest
import os
import sys
import requests
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from threading import Thread
import time


sys.path.append(os.path.abspath('../'))


from user_class import User
from task_class import Task
from application import main


env = Environment(
    loader=FileSystemLoader('../template'),
    autoescape=select_autoescape(['html', 'xml'])
)


PORT = 19885


SESSION = requests.Session()
URL = f"http://127.0.0.1:{PORT}/"


def run_web():
    main(template_loader_path="../template", static_dir="../public", port=PORT)
    os.system("python3 for_test_wem_app.py")


run = Thread(target=run_web)
run.start()
time.sleep(2)


@pytest.fixture()
def user():
    user = User(name="test_web_app", password="12345678Ll", registration=True)
    Task(date="2021-07-10", short_name="1", description="1", task_table_name=user._task_table)
    Task(date="2021-07-10", short_name="2", description="2", task_table_name=user._task_table)
    Task(date="2021-07-10", short_name="3", description="3", task_table_name=user._task_table)
    return user


def test_index():
    response = SESSION.get(url=URL+"index")
    assert 200 == response.status_code
    template = env.get_template("signIn.html")
    assert template.render() == response.text


def test_registration_html():
    response = SESSION.get(url=URL+"registration.html")
    assert 200 == response.status_code
    template = env.get_template("registration.html")
    assert template.render() == response.text


def test_sign_in(user):
    response = SESSION.post(url=URL+"user_sign_in", data={"name": user.name, "password": user.password})
    assert 200 == response.status_code
    user.delete_user()


def test_user_registration(user):
    copy_user = user
    user.delete_user()
    response = SESSION.post(url=URL + "user_registration",
                            data={"name": copy_user.name, "password": copy_user.password, "password_repeat": copy_user.password})
    assert 200 == response.status_code
    template = env.get_template("userDailyTasks.html")
    assert template.render(date=str(datetime.today()).split()[0]) == response.text
    copy_user.delete_user()




def test_user_daily_tasks(user):
    response = SESSION.post(url=URL + "user_daily_tasks", data={"date": "1984-07-10"})
    assert 200 == response.status_code
    template = env.get_template("userDailyTasks.html")
    assert template.render(date="1984-07-10") == response.text
    user.delete_user()


def test_change_date(user):
    response = SESSION.post(url=URL + "change_date", data={"join_date": "2021-07-09"})
    assert 200 == response.status_code
    user.delete_user()


def test_user_verification(user):
    response_sign_in = SESSION.post(url=URL+"user_verification",
                            data={"create": False, "name": user.name, "password": "12345Ll"})
    assert 200 == response_sign_in.status_code
    response_registration = SESSION.post(url=URL + "user_verification",
                            data={"create": True, "name": user.name, "password": user.password})
    assert 200 == response_registration.status_code
    template_registration = env.get_template("registration.html")
    assert template_registration.render(name=user.name, password=user.password, message="user with this name already exists") == response_registration.text
    user.delete_user()


def test_add_task(user, date="2000-10-11"):
    resp_change_date = SESSION.post(url=URL + "change_date", data={"join_date": date})
    response = SESSION.post(url=URL+"add_task",
                            data={"join_date": date, "short_name": "test_add", "description": "test_add"})
    assert 200 == response.status_code
    empty_template = env.get_template("userDailyTasks.html")
    assert empty_template.render(date=date) != response.text
    user.delete_user()


def test_updated_page(user):
    response = SESSION.get(url=URL+"updated_page")
    assert 200 == response.status_code
    user.delete_user()


def test_delete_task(user, date="2021-07-10"):
    first_response = SESSION.post(url=URL + "user_daily_tasks", data={"date": date})
    second_response = SESSION.post(url=URL+"delete_task", data={"task_id": "1"})
    assert 200 == second_response.status_code
    assert first_response.text != second_response.text
    user.delete_user()


def test_update_task(user, date="2021-07-10"):
    first_response = SESSION.post(url=URL + "user_daily_tasks", data={"date": date})
    second_response = SESSION.post(url=URL + "update_task", data={"task_id": "1"})
    assert 200 == second_response.status_code
    assert first_response.text != second_response.text
    user.delete_user()


def test_sign_out(user):
    response = SESSION.get(url=URL+"sign_out")
    assert 200 == response.status_code
    template = env.get_template("signIn.html")
    assert template.render() == response.text
    user.delete_user()

