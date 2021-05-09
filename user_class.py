from mysql_class import MySQL
from task_class import Task


class User:

    TABLE_NAME = "users"
    DATABASE_NAME = "main"
    def __init__(self, name, password):
        self._name = name
        self._password = password
        self._task_table = self._name + "tasks"
        self._db = MySQL(database_name=User.DATABASE_NAME)
        self.__add_user_in_database()
        self._db.create_tasks_table(table_name=self._task_table)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        self._password = val

    def __add_user_in_database(self):
        values = (self._name, self._password, self._task_table)
        self._db.insert_data(table=User.TABLE_NAME, values=values)

    def select_some_task(self, condition="1=1"):
        return self._db.select_data(table=self._task_table, condition=condition)

    def add_task(self, task):
        task.add_task_in_table()

    def delete_task(self, task):
        task.delete_task()

    def delete_user(self):
        condition = f"name='{self._name}'"
        self._db.drop_table(table_name=self._task_table)
        self._db.delete(table_name="users", condition=condition)

if __name__ == '__main__':
    person1 = User(name="yasha12", password="1234")
    task = Task(date="1984-11-12", short_name="test functionality", description="dadfasdfa", task_table_name=person1._task_table)
    print(person1.select_some_task())
    person1.delete_user()

