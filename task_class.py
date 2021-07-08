from mysql_class import MySQL
import logging


LOGGER = logging.getLogger(__name__)


class Task:

    DATABASE_NAME = "main"

    def __init__(self, date, short_name, description, task_table_name, task_id=0):
        logging.info("creating task")
        self.id = task_id
        self.date = date
        self.short_name = short_name
        self.description = description
        self.complete = ""
        self.task_table_name = task_table_name
        self._db = MySQL(database_name=Task.DATABASE_NAME)
        logging.info(f"task(short_name={short_name}, description={description}, date={date}, table={task_table_name}")
        self.add_task_in_table()

    def add_task_in_table(self):
        LOGGER.debug(f"add task in table {self.task_table_name}")
        self._db.insert_data(table=self.task_table_name,
                             values=(self.id,self.date, self.short_name, self.description, self.complete))
