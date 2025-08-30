from typing import Literal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Connection:
    def __init__(
            self,
            db_type: Literal['sqlite', 'mysql', 'postgres', 'sql_server']=None,
            host=None,
            port=None,
            user=None,
            password=None,
            database=None,
            database_path=None,
            odbc_driver=17
        ) -> None:
        self.db_type = db_type
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.database_path = database_path
        self.odbc_driver = odbc_driver

        self.__engine = None
        self.__connection_string = None
        self.session = None

        self.__test_connection()

    def __create_connection_string(self):
        if self.db_type == 'sqlite':
            return (
                f'sqlite:///{self.database_path}'
                if self.database_path
                else 'sqlite:///:memory:'
            )
        elif self.db_type == 'mysql':
            return (
                f'mysql+pymysql://{self.user}:{self.password}@'
                f'{self.host}:{self.port}/{self.database}'
            )
        elif self.db_type == 'postgres':
            return (
                f'postgresql+psycopg2://{self.user}:{self.password}@'
                f'{self.host}:{self.port}/{self.database}'
            )
        elif self.db_type == 'sql_server':
            connection_string = (
                f'DRIVER={{ODBC Driver {self.odbc_driver} for SQL Server}};SERVER={self.host};'
                f'DATABASE={self.database};UID={self.user};PWD={self.password};'
            )
            return f'mssql+pyodbc:///?odbc_connect={connection_string}'
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def __create_database_engine(self):
        if not self.__engine:
            self.__connection_string = self.__create_connection_string()

            connect_args = {}
            if self.db_type == 'sqlite':
                connect_args = {'check_same_thread': False}

            self.__engine = create_engine(
                self.__connection_string,
                connect_args=connect_args
            )

        return self.__engine

    def get_engine(self):
        if not self.__engine:
            self.__create_database_engine()
        return self.__engine

    def __test_connection(self):
        from sqlalchemy import text
        try:
            engine = self.__create_database_engine()

            with engine.connect() as connection:
                if self.db_type == 'sqlite':
                    result = connection.execute(text('SELECT 1'))
                elif self.db_type == 'mysql':
                    result = connection.execute(text('SELECT 1 FROM DUAL'))
                elif self.db_type == 'postgres':
                    result = connection.execute(text('SELECT 1'))
                elif self.db_type == 'sql_server':
                    result = connection.execute(text('SELECT 1'))
                else:
                    print(f"No specific connection test for {self.db_type}")
                    return

                result.fetchone()
                print(f"Conexão {self.db_type} estabelecida com sucesso!")
        except Exception as e:
            print(f"Erro ao estabelecer conexão: {e}")
            raise

    def __enter__(self):
        if not self.__engine:
            self.__create_database_engine()

        session_maker = sessionmaker(bind=self.__engine)
        self.session: Session = session_maker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            self.session.rollback()
        self.session.close()

        if self.__engine:
            self.__engine.dispose()
            self.__engine = None
