# всё буду запускать отсюда
import cherrypy
import os
from user_class import User
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from task_class import Task
import logging
import sys


LOGGER = logging.getLogger(__name__)


env = Environment(
    loader=FileSystemLoader('./template'),
    autoescape=select_autoescape(['html', 'xml'])
)


class MyWebServices:

    @cherrypy.expose()
    def index(self, message="", name="", password=""):
        template = env.get_template("signIn.html")
        return template.render(message=message, name=name, password=password)

    @cherrypy.expose()
    def user_sign_in(self, name, password):
        return self.user_verification(create=False, name=name, password=password)

    @cherrypy.expose()
    def registration_html(self,  message="", name="", password=""):
        template = env.get_template("registration.html")
        return template.render(message=message, name=name, password=password)

    @cherrypy.expose()
    def user_registration(self, name, password, password_repeat):
        if password != password_repeat:
            return self.registration_html()
        return self.user_verification(create=True, name=name, password=password)

    @cherrypy.expose()
    def user_daily_tasks(self, date=str(datetime.today()).split()[0]):
        template = env.get_template('userDayliTasks.html')
        tasks = cherrypy.session["person"].turning_task_in_json(date)
        cherrypy.session["date"] = date
        LOGGER.debug(f"user {cherrypy.session['person']._name} on date {date}")
        return template.render(date=date, tasks_data=tasks)

    @cherrypy.expose()
    def change_date(self, join_date):
        LOGGER.debug(f"selected day: {join_date}")
        cherrypy.session["date"] = join_date
        raise cherrypy.HTTPRedirect("/updated_page")

    @cherrypy.expose()
    def user_verification(self, create, name, password):
        users_list = User.return_names_and_passwords()
        if create:
            LOGGER.info("creating user")
            for user in users_list:
                if user["name"] == name:
                    LOGGER.info(f"user with name '{name}' already exists")
                    return self.registration_html(message="user with this name already exists",
                                                  name=name, password=password)
            person = User(name=name, password=password, registration=True)
            cherrypy.session["person"] = person
            LOGGER.info(f"user {name} created")
            return self.user_daily_tasks()
        else:
            for user in users_list:
                if user["name"] == name and user["password"] == password:
                    person = User(name=name, password=password, registration=False)
                    cherrypy.session["person"] = person
                    LOGGER.info(f"user {name} sign in")
                    return self.user_daily_tasks()
            LOGGER.info(f"incorrect password({password}) or username({name})")
            return self.index(message="incorrect password or user name", name=name, password=password)

    @cherrypy.expose()
    def sign_out(self):
        LOGGER.debug(f"user {cherrypy.session['person']._name} sign out")
        cherrypy.session["person"] = None
        cherrypy.session["date"] = None
        return self.index()

    @cherrypy.expose()
    def add_task(self, join_date, short_name, description):
        LOGGER.info(f"user {cherrypy.session['person']._name} creating task")
        Task(date=join_date, short_name=short_name, description=description,
             task_table_name=cherrypy.session["person"]._task_table)
        LOGGER.info("task created")
        raise cherrypy.HTTPRedirect("/updated_page")

    @cherrypy.expose()
    def updated_page(self):
        LOGGER.debug("update page")
        return self.user_daily_tasks(cherrypy.session["date"])

    @cherrypy.expose()
    def delete_task(self, task_id):
        LOGGER.info(f"deleting task with id: {task_id}")
        condition = f"id={task_id}"
        cherrypy.session["person"]._db.delete(table_name=cherrypy.session["person"]._task_table, condition=condition)
        LOGGER.info(f"task with id: {task_id} deleted")
        raise cherrypy.HTTPRedirect("/updated_page")

    @cherrypy.expose()
    def update_task(self, task_id):
        complete = cherrypy.session["person"]._db.select_data(take="complete",
                                    table=cherrypy.session["person"]._task_table, condition=f"id='{task_id.strip()}'")
        LOGGER.debug(f"updating task(id: {task_id}): {complete}")
        if complete[0][0] == "":
            cherrypy.session["person"]._db.update_task_complete(table=cherrypy.session["person"]._task_table,
                                                                condition=f"id='{task_id.strip()}'", cl="'checked'")
        else:
            cherrypy.session["person"]._db.update_task_complete(table=cherrypy.session["person"]._task_table,
                                                                condition=f"id='{task_id.strip()}'", cl="''")
        raise cherrypy.HTTPRedirect("/updated_page")


def main():
    LOGGER.debug("update cherrypy config")
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.config.update({"server.socket_port": 8097})
    LOGGER.debug("starting application")
    cherrypy.quickstart(MyWebServices(), '/', conf)


def setup_logging(log_level=logging.DEBUG):
    file_handler = logging.FileHandler("application.log")
    formatter = logging.Formatter("[%(asctime)s] - %(levelname)s - %(module)s : %(message)s")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(log_level)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(log_level)


if __name__ == '__main__':
    setup_logging()
    try:
        main()
    except Exception as ex:
        logging.critical(f"CRITICAL! Application failed, details: {ex}")
