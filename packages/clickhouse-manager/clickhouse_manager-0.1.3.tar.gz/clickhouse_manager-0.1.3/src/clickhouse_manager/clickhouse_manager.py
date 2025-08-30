"""
ClickHouse Manager - высокоуровневый интерфейс для работы с ClickHouse.
"""

import pandas as pd
from .connectors import ConnectorFactory
from .validators import IdentifierValidator


class ClickhouseManager:
    """
    Класс для работы с ClickHouse.
    Использует коннекторы для низкоуровневых операций и валидаторы для безопасности.
    """
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 database: str = '', secure: bool = False, verify: bool = False,
                 connector_type: str = 'clickhouse_connect'):
        """
        Инициализация ClickHouse менеджера.
        
        Args:
            host: Хост ClickHouse сервера
            port: Порт ClickHouse сервера
            username: Имя пользователя
            password: Пароль
            database: База данных (по умолчанию пустая)
            secure: Использовать SSL соединение (по умолчанию False)
            verify: Проверять SSL сертификат (по умолчанию False)
            connector_type: Тип коннектора ('clickhouse_connect' или 'clickhouse_driver')
        """
        self.connector = ConnectorFactory.create(
            connector_type=connector_type,
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            secure=secure,
            verify=verify
        )
    
    def query_to_df(self, query: str) -> pd.DataFrame:
        """
        Выполнить SELECT запрос и вернуть результат как DataFrame.
        
        Args:
            query: SQL запрос
            
        Returns:
            DataFrame с результатами запроса
        """
        return self.connector.execute_query(query)
    
    def insert_df(self, table_schema: str, table_name: str, df: pd.DataFrame):
        """
        Вставить DataFrame в таблицу.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            df: DataFrame для вставки
            
        Returns:
            Результат вставки
        """
        # Валидируем параметры таблицы
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Вставляем через коннектор с новым порядком параметров
        return self.connector.insert_dataframe(df, table_schema, table_name)
    
    def execute_command(self, query: str, **kwargs):
        """
        Выполнить команду (INSERT, UPDATE, DELETE, DDL).
        
        Args:
            query: SQL команда
            **kwargs: Дополнительные параметры
            
        Returns:
            Результат выполнения команды
        """
        return self.connector.execute_command(query, **kwargs)
    
    def check_column_consistency(self, table_column: list, df_column: list):
        """
        Проверить соответствие колонок таблицы и DataFrame.
        
        Args:
            table_column: Список колонок таблицы
            df_column: Список колонок DataFrame
            
        Returns:
            True если колонки соответствуют
            
        Raises:
            NameError: Если есть несоответствия в колонках
        """
        excessed_table_column = list(set(table_column) - set(df_column))
        if len(excessed_table_column) > 0:
            raise NameError(f"В dataframe не хватает колонок: {excessed_table_column}")

        excessed_df_column = list(set(df_column) - set(table_column))
        if len(excessed_df_column) > 0:
            raise NameError(f"В dataframe лишние колонки: {excessed_df_column}")
        
        return True
    
    def check_table_if_exists(self, table_schema: str, table_name: str) -> bool:
        """
        Проверить существование таблицы в ClickHouse.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            
        Returns:
            True если таблица существует, False в противном случае
        """
        # Валидируем параметры
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Используем валидированные имена без экранирования
        query = f"SELECT count(*) AS qnt FROM system.tables WHERE name = '{table_name}' AND database = '{table_schema}' LIMIT 1"
        df = self.query_to_df(query=query)
        if df['qnt'][0] == 0:
            return False
        return True

    def get_table_column(self, table_schema: str, table_name: str) -> pd.DataFrame:
        """
        Получить информацию о колонках таблицы.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            
        Returns:
            DataFrame с информацией о колонках (column_name, data_type)
            
        Raises:
            NameError: Если таблица не найдена
        """
        
        
        # Валидируем параметры
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Проверяем, что таблица существует
        if not self.check_table_if_exists(table_schema, table_name):
            raise NameError("Не могу найти таблицу {} в клике".format(table_name))
        
        query = f"SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema = '{table_schema}' AND table_name = '{table_name}'"
        return self.query_to_df(query=query)

    def get_table_info(self, table_schema: str, table_name: str):
        """
        Получить полную информацию о таблице.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            
        Returns:
            Кортеж (DataFrame с колонками, первичный ключ)
            
        Raises:
            NameError: Если таблица не найдена
        """
        if not self.check_table_if_exists(table_schema, table_name):
            raise NameError("Не могу найти таблицу {} в клике".format(table_name))
        
        df = self.get_table_column(table_schema, table_name)
        
        # Валидируем параметры
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Используем валидированные имена без экранирования
        query = f"""
            SELECT primary_key FROM system.tables
            WHERE 1=1
            AND database = '{table_schema}'
            AND name = '{table_name}'
        """
        df_PK = self.query_to_df(query)
        pk = df_PK.loc[0, "primary_key"].split(",")[0]
        return df, pk if len(pk) > 0 else None

    def drop_table(self, table_schema: str, table_name: str, cluster: str = 'cluster', if_exists: bool = True):
        """
        Удалить таблицу из базы данных.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            cluster: Имя кластера (по умолчанию 'cluster')
            if_exists: Удалять только если существует (по умолчанию True)
            
        Returns:
            self для цепочки вызовов
        """
        # Валидируем параметры
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Используем валидированные имена без экранирования
        cluster = "{" + cluster + "}"
        query = f"DROP TABLE {'IF EXISTS' if if_exists == True else ''} {table_schema}.{table_name} ON CLUSTER '{cluster}' NO DELAY;"
        self.execute_command(query)
        return self

    def create_table(self, table_schema: str, table_name: str, columns: dict, order_by: str, 
                    drop_if_exists: bool = True, cluster: str = 'cluster', 
                    replica_placeholder: str = '{replica}', index_granularity: int = 8192):
        """
        Создать таблицу в ClickHouse.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            columns: Словарь колонок {имя: тип}
            order_by: Колонка для сортировки
            drop_if_exists: Удалять существующую таблицу (по умолчанию True)
            cluster: Имя кластера (по умолчанию 'cluster')
            replica_placeholder: Плейсхолдер для реплики (по умолчанию '{replica}')
            index_granularity: Размер гранулы индекса (по умолчанию 8192)
            
        Returns:
            self для цепочки вызовов
        """
        # Валидируем параметры таблицы
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Валидируем колонки
        IdentifierValidator.validate_columns(columns)
        
        # Валидируем order_by
        if not IdentifierValidator.validate_column_name(order_by):
            raise ValueError(f"Invalid order_by column: {order_by}")

        # Используем параметры вместо хардкода
        replica = replica_placeholder
        cluster = "{" + cluster + "}"

        if drop_if_exists:
            self.drop_table(table_schema, table_name, cluster=cluster.replace('{', '').replace('}', ''), if_exists=True)
        
        query_column = ""
        for column_name, data_type in columns.items():
            # Валидируем имя колонки
            if not IdentifierValidator.validate_column_name(column_name):
                raise ValueError(f"Invalid column name: {column_name}")
            query_column += f"""
                    \t{"," if len(query_column) > 0 else ""}{column_name} {data_type}\n
                """

        query_create_table = f"""
            CREATE TABLE {table_schema}.{table_name} ON CLUSTER '{cluster}'(
            {query_column}
            )
            ENGINE = ReplicatedMergeTree('/clickhouse/tables/{table_schema}.{table_name}', '{replica}') ORDER BY {order_by}
            SETTINGS index_granularity = {index_granularity};
            """
        self.execute_command(query_create_table)
        return self
    
    
    def create_table_as_select(self, query: str, table_schema: str, table_name: str, order_by: str, 
                              drop_if_exists: bool = True, insert: bool = True, cluster: str = 'cluster',
                              replica_placeholder: str = '{replica}', index_granularity: int = 8192):
        """
        Создать таблицу на основе SELECT запроса.
        
        Args:
            query: SQL запрос для создания таблицы
            table_schema: Имя схемы
            table_name: Имя таблицы
            order_by: Колонка для сортировки
            drop_if_exists: Удалять существующую таблицу (по умолчанию True)
            insert: Вставлять данные после создания (по умолчанию True)
            cluster: Имя кластера (по умолчанию 'cluster')
            replica_placeholder: Плейсхолдер для реплики (по умолчанию '{replica}')
            index_granularity: Размер гранулы индекса (по умолчанию 8192)
            
        Returns:
            self для цепочки вызовов
        """
        # Получаем метаданные запроса через коннектор
        column_info_df = self.connector.get_query_metadata(query)
        if column_info_df.empty:
            raise NameError("Не могу получить метаданные запроса")
        
        self.create_table(table_schema=table_schema
                          , table_name=table_name
                          , columns=dict(zip(column_info_df['column_name'], column_info_df['data_type']))
                          , order_by=order_by
                          , drop_if_exists=drop_if_exists
                          , cluster=cluster
                          , replica_placeholder=replica_placeholder
                          , index_granularity=index_granularity)
        
        if insert:
            self.insert_select_into_table(query=query
                                        , table_schema=table_schema
                                        , table_name=table_name)
        return self
    
    def insert_select_into_table(self, query: str, table_schema: str, table_name: str):
        """
        Вставить результат SELECT запроса в таблицу.
        
        Args:
            query: SQL запрос
            table_schema: Имя схемы
            table_name: Имя таблицы
        """
        # Валидируем параметры
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Используем валидированные имена без экранирования
        query_wrapper = f"INSERT INTO {table_schema}.{table_name} {query}"
        return self.execute_command(query_wrapper)
    
    def _insert_df_query_builder(self, table_schema: str, table_name: str, table_columns) -> str:
        """
        Построить SQL запрос для вставки DataFrame.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            table_columns: Список колонок
            
        Returns:
            SQL запрос для вставки
        """
        # Валидируем параметры
        IdentifierValidator.validate_table_params(table_schema, table_name)
        
        # Строим запрос без экранирования
        query = f"INSERT INTO {table_schema}.{table_name}"
        query_columns = ''
        for it, column in enumerate(table_columns):

            if not IdentifierValidator.validate_column_name(column):
                raise ValueError(f"Invalid column name: {column}")

            query_columns += f"{' ,' if it != 0 else ''}{column}"
            
        query_columns = f"({query_columns})"
        return f"{query} {query_columns} VALUES"
            
    def execute_commands(self, query):
        """
        Выполнить несколько команд, разделенных точкой с запятой.
        
        Args:
            query: Строка с командами, разделенными ';'
            
        Returns:
            self для цепочки вызовов
        """
        def parse_commands(query):
            commands = list(
                filter(
                    lambda x: True if len(x) > 0 else False
                    , query.strip().split(';')
                )
            )
            return commands

        commands = parse_commands(query=query)
        for command in commands:
            self.execute_command(command)
        return self

