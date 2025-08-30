"""
Простой базовый класс для ClickHouse коннекторов.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd


class IClickhouseConnector(ABC):
    """Базовый класс для всех ClickHouse коннекторов."""
    
    @abstractmethod
    def __init__(self, host: str, port: int, username: str, password: str, 
                 database: str = '', secure: bool = False, verify: bool = False):
        """
        Инициализация коннектора.
        
        Args:
            host: Хост ClickHouse сервера
            port: Порт ClickHouse сервера
            username: Имя пользователя
            password: Пароль
            database: База данных (по умолчанию пустая)
            secure: Использовать SSL соединение (по умолчанию False)
            verify: Проверять SSL сертификат (по умолчанию False)
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> pd.DataFrame:
        """Выполнить SELECT запрос и вернуть результат как DataFrame."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str) -> Any:
        """Выполнить команду (INSERT, UPDATE, DELETE, DDL) и вернуть результат."""
        pass
    
    @abstractmethod
    def insert_dataframe(self, df: pd.DataFrame, schema: str, table: str) -> bool:
        """Вставить DataFrame в таблицу."""
        pass
    
    @abstractmethod
    def get_query_metadata(self, query: str) -> pd.DataFrame:
        """
        Получить метаданные запроса (колонки и их типы).
        
        Args:
            query: SQL запрос для анализа
            
        Returns:
            DataFrame с колонками ['column_name', 'data_type']
        """
        pass


