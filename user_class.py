from mysql_class import MySQL
import logging


LOGGER = logging.getLogger(__name__)


class NameTooLong(Exception):
    pass


class PasswordTooShort(Exception):
    pass


class User:

    TABLE_NAME = "users"
    DATABASE_NAME = "main"

    def __init__(self, name, password, registration=False):
        self.name = name
        self.password = password
        self._task_table = self._name + "tasks"
        self._db = MySQL(database_name=User.DATABASE_NAME)
        if registration:
            LOGGER.info(f"Creating user {name}")
            self.__add_user_in_database()
            self._db.create_tasks_table(table_name=self._task_table)
            LOGGER.info(f"User '{name} created")
        LOGGER.info(f"User {name} sign in")
        # else:
        #     self.user_verification()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        if len(val) > 45:
            LOGGER.warning(f"too long name {val}")
            raise NameTooLong(val)
        self._name = val

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        if len(val) < 8:
            LOGGER.warning(f"too short password {val}")
            raise PasswordTooShort(val)
        self._password = val

    def __add_user_in_database(self):
        values = (self.name, self.password, self._task_table)
        LOGGER.debug(f"add user {self.name} in database")
        self._db.insert_data(table=User.TABLE_NAME, values=values)

    def select_some_task(self, condition="1=1"):
        LOGGER.debug(f"user {self.name} select task from database")
        return self._db.select_data(table=self._task_table, condition=condition)

    def turning_task_in_json(self, date):
        tasks = self.select_some_task(condition=f"date='{date}'")
        keys = ["id", "date", "short_name", "description", "complete"]
        json_data = []
        for task in tasks:
            json_data.append(dict(zip(keys, task)))
        LOGGER.debug(f"user {self.name} turning task in json: {json_data}")
        return json_data

    @classmethod
    def return_names_and_passwords(cls):
        database = MySQL(cls.DATABASE_NAME)
        users = database.select_data(table=cls.TABLE_NAME, take="name, password")
        keys = ["name", "password"]
        users_dict = []
        for user in users:
            users_dict.append(dict(zip(keys, user)))
        LOGGER.debug(f"return all names and passwords from the table {cls.TABLE_NAME}")
        return users_dict


    def delete_user(self):
        condition = f"name='{self.name}'"
        self._db.drop_table(table_name=self._task_table)
        self._db.delete(table_name="users", condition=condition)
