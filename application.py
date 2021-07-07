# всё буду запускать отсюда
import cherrypy
import os
from user_class import User
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from task_class import Task


env = Environment(
    loader=FileSystemLoader('./template'),
    autoescape=select_autoescape(['html', 'xml'])
)


class MyWebServices:

    @cherrypy.expose()
    def index(self):
        return open("template/signIn.html")

    @cherrypy.expose()
    def user_sign_in(self, name, password):
        return self.user_verification(create=False, name=name, password=password)

    @cherrypy.expose()
    def registration_html(self):
        return open("template/registration.html")

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
        return template.render(date=date, tasks_data=tasks)

    @cherrypy.expose()
    def change_date(self, join_date):
        cherrypy.session["date"] = join_date
        raise cherrypy.HTTPRedirect("/updated_page")

    @cherrypy.expose()
    def user_verification(self, create, name, password):
        users_list = User.return_names_and_passwords()
        if create:
            for user in users_list:
                if user["name"] == name:
                    return self.registration_html()
            person = User(name=name, password=password, registration=True)
            cherrypy.session["person"] = person
            return self.user_daily_tasks()
        else:
            for user in users_list:
                if user["name"] == name and user["password"] == password:
                    person = User(name=name, password=password, registration=False)
                    cherrypy.session["person"] = person
                    return self.user_daily_tasks()
            return self.index()

    @cherrypy.expose()
    def sign_out(self):
        cherrypy.session["person"] = None
        cherrypy.session["date"] = None
        return self.index()

    @cherrypy.expose()
    def add_task(self, join_date, short_name, description):
        Task(date=join_date, short_name=short_name, description=description,
             task_table_name=cherrypy.session["person"]._task_table)
        raise cherrypy.HTTPRedirect("/updated_page")

    @cherrypy.expose()
    def updated_page(self):
        return self.user_daily_tasks(cherrypy.session["date"])

    @cherrypy.expose()
    def delete_task(self, task_id):
        condition = f"id={task_id}"
        cherrypy.session["person"]._db.delete(table_name=cherrypy.session["person"]._task_table, condition=condition)
        raise cherrypy.HTTPRedirect("/updated_page")

    @cherrypy.expose()
    def update_task(self, task_id):
        complete = cherrypy.session["person"]._db.select_data(take="complete",
                                    table=cherrypy.session["person"]._task_table, condition=f"id='{task_id.strip()}'")
        print(f"update_task: {complete}")
        if complete[0][0] == "":
            cherrypy.session["person"]._db.update_task_complete(table=cherrypy.session["person"]._task_table,
                                                                condition=f"id='{task_id.strip()}'", cl="'checked'")
        else:
            cherrypy.session["person"]._db.update_task_complete(table=cherrypy.session["person"]._task_table,
                                                                condition=f"id='{task_id.strip()}'", cl="''")
        raise cherrypy.HTTPRedirect("/updated_page")


def main():
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
    cherrypy.quickstart(MyWebServices(), '/', conf)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print("critical")
