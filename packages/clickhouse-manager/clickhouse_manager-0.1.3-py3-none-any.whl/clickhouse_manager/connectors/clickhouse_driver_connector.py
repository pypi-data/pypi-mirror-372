"""
Реализация коннектора для библиотеки clickhouse-driver.
"""

import clickhouse_driver
import pandas as pd
from typing import Any, Optional
from .base_connector import IClickhouseConnector


class ClickhouseDriverConnector(IClickhouseConnector):
    """Коннектор на основе библиотеки clickhouse-driver."""
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 database: str = '', secure: bool = False, verify: bool = False):
        """
        Инициализация коннектора через clickhouse-driver.
        
        Args:
            host: Хост ClickHouse сервера
            port: Порт ClickHouse сервера
            username: Имя пользователя
            password: Пароль
            database: База данных (по умолчанию пустая)
            secure: Использовать SSL соединение (по умолчанию False)
            verify: Проверять SSL сертификат (по умолчанию False)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.secure = secure
        self.verify = verify
        
        # Создаем клиент
        self.client = clickhouse_driver.Client(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            secure=secure,
            verify=verify
        )
    
    def _get_client(self):
        """Получить клиент подключения."""
        if self.client is None:
            self.client = clickhouse_driver.Client(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
                secure=self.secure,
                verify=self.verify
            )
        return self.client
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Выполнить SELECT запрос и вернуть результат как DataFrame."""
        client = self._get_client()
        result = client.query_dataframe(query)
        
        return result
    
    def execute_command(self, command: str) -> Any:
        """Выполнить команду (INSERT, UPDATE, DELETE, DDL) и вернуть результат."""
        client = self._get_client()
        return client.execute(command)
    
    def insert_dataframe(self, df: pd.DataFrame, schema: str, table: str) -> bool:
        """Вставить DataFrame в таблицу."""
        client = self._get_client()
        
        # Формируем полное имя таблицы
        full_table = f"{schema}.{table}" if schema else table
        
        # Конвертируем DataFrame в список кортежей
        data = [tuple(row) for row in df.itertuples(index=False, name=None)]
        
        # Вставляем данные
        client.execute(f"INSERT INTO {full_table} VALUES", data)
        return True
    
    def get_query_metadata(self, query: str) -> pd.DataFrame:
        """
        Получить метаданные запроса (колонки и их типы).
        
        Args:
            query: SQL запрос для анализа
            
        Returns:
            DataFrame с колонками ['column_name', 'data_type']
        """
        client = self._get_client()
        
        try:
            # Оборачиваем запрос для получения метаданных
            query_wrapper = f"SELECT * FROM ({query}) t1 LIMIT 0"
            
            # Выполняем запрос с получением типов колонок
            result = client.execute(query_wrapper, with_column_types=True)
            
            # clickhouse-driver возвращает (data, column_types)
            data, column_types = result
            
            # Извлекаем имена колонок и типы
            columns = [col[0] for col in column_types]
            types = [col[1] for col in column_types]
            
            # Создаем DataFrame с метаданными
            metadata_df = pd.DataFrame(zip(columns, types), 
                                     columns=['column_name', 'data_type'])
            
            return metadata_df
            
        except Exception as e:
            # Если не удалось получить метаданные, возвращаем пустой DataFrame
            print(f"Warning: Could not get query metadata via clickhouse-driver: {e}")
            return pd.DataFrame(columns=['column_name', 'data_type'])
