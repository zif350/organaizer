import mysql.connector


class MySQL:
    def __init__(self, database_name):
        self.connection = mysql.connector.connect(
            user="root", password="secret",
            autocommit=True, port=3306,
            database=database_name)

    def execute(self, query, select=False):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            if select:
                return cursor.fetchall()

    def insert_data(self, table, values):
        query = f"insert into {table} values {values}"
        self.execute(query=query)

    def update_data(self, table, condition, **kwargs):
        set_values = ", ".join([f"{k} = '{v}'" for k, v in kwargs.items()])
        query = f"update {table} set {set_values} where {condition}"
        self.execute(query=query)

    def select_data(self, table, condition="1=1", take="*"):
        query = f"select {take} from {table} where {condition}"
        return self.execute(query=query, select=True)


    def delete(self, table_name, condition):
        query = f"delete from {table_name} where {condition}"
        self.execute(query)

    def drop_table(self, table_name):
        query = f"drop table {table_name}"
        self.execute(query=query)

    def create_tasks_table(self, table_name):
        query = f"create table `{table_name}`(" \
                f"`ID` int auto_increment," \
                f"`date` date not null," \
                f"`shortName` varchar(40) not null," \
                f"`description` TINYTEXT default null," \
                f"`complete` int default 0," \
                f"PRIMARY KEY (`ID`)" \
                f") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        self.execute(query)