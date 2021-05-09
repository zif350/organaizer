from mysql_class import MySQL


class Task:
    DATABASE_NAME = "main"

    def __init__(self, date, short_name, description, task_table_name, id=0):
        self.id = id
        self.date = date
        self.short_name = short_name
        self.description = description
        self.complete = 0
        self.task_table_name = task_table_name
        self._db = MySQL(database_name=Task.DATABASE_NAME)
        self.add_task_in_table()

    def add_task_in_table(self):
        self._db.insert_data(table=self.task_table_name,
                             values=(self.id,self.date, self.short_name, self.description, self.complete))

    def delete_task(self):
        condition = f"id={self.id}"
        self._db.delete(table_name=self.task_table_name, condition=condition)
