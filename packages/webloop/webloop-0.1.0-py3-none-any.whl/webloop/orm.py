import sqlite3

class Field:
    def __init__(self, column_type):
        self.column_type = column_type

class Integer(Field):
    def __init__(self, primary_key=False):
        super().__init__('INTEGER')
        self.primary_key = primary_key

class String(Field):
    def __init__(self, max_length=255):
        super().__init__(f'VARCHAR({max_length})')

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return super().__new__(cls, name, bases, attrs)
        mappings = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        attrs['__mappings__'] = mappings
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=ModelMeta):
    __tablename__ = None

    @classmethod
    def create_table(cls):
        columns = []
        for name, field in cls.__mappings__.items():
            col_def = f"{name} {field.column_type}"
            if isinstance(field, Integer) and field.primary_key:
                col_def += " PRIMARY KEY AUTOINCREMENT"
            columns.append(col_def)
        sql = f"CREATE TABLE IF NOT EXISTS {cls.__tablename__ or cls.__name__.lower()} ({', '.join(columns)});"
        conn = sqlite3.connect('webloop.db')
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()

    def save(self):
        table = self.__tablename__ or self.__class__.__name__.lower()
        fields = self.__mappings__.keys()
        values = [getattr(self, f, None) for f in fields]
        placeholders = ','.join(['?'] * len(values))
        sql = f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})"
        conn = sqlite3.connect('webloop.db')
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        conn.close()
