"""
Валидаторы для ClickHouse идентификаторов.
"""

import re
from typing import List, Dict, Any


class IdentifierValidator:
    """
    Класс для валидации ClickHouse идентификаторов.
    """
    
    # Паттерн для валидных идентификаторов
    IDENTIFIER_PATTERN = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    
    # Зарезервированные слова ClickHouse (основные)
    RESERVED_WORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
        'TABLE', 'DATABASE', 'SCHEMA', 'INDEX', 'VIEW', 'TRIGGER', 'PROCEDURE',
        'FUNCTION', 'ENGINE', 'ORDER', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET',
        'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS', 'IN', 'NOT',
        'AND', 'OR', 'IS', 'NULL', 'TRUE', 'FALSE', 'CASE', 'WHEN', 'THEN',
        'ELSE', 'END', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'
    }
    
    @classmethod
    def validate_identifier(cls, identifier: str) -> bool:
        """
        Валидация идентификатора (имя таблицы, схемы, колонки).
        
        Args:
            identifier: Идентификатор для проверки
            
        Returns:
            True если идентификатор валиден, False в противном случае
        """
        if not identifier or not isinstance(identifier, str):
            return False
        
        # Проверяем паттерн
        if not re.match(cls.IDENTIFIER_PATTERN, identifier):
            return False
        
        # Проверяем зарезервированные слова
        if identifier.upper() in cls.RESERVED_WORDS:
            return False
        
        return True
    
    @classmethod
    def validate_table_name(cls, table_name: str) -> bool:
        """
        Валидация имени таблицы.
        
        Args:
            table_name: Имя таблицы для проверки
            
        Returns:
            True если имя таблицы валидно, False в противном случае
        """
        return cls.validate_identifier(table_name)
    
    @classmethod
    def validate_schema_name(cls, schema_name: str) -> bool:
        """
        Валидация имени схемы.
        
        Args:
            schema_name: Имя схемы для проверки
            
        Returns:
            True если имя схемы валидно, False в противном случае
        """
        return cls.validate_identifier(schema_name)
    
    @classmethod
    def validate_column_name(cls, column_name: str) -> bool:
        """
        Валидация имени колонки.
        
        Args:
            column_name: Имя колонки для проверки
            
        Returns:
            True если имя колонки валидно, False в противном случае
        """
        return cls.validate_identifier(column_name)
    
    @classmethod
    def validate_table_params(cls, table_schema: str, table_name: str) -> None:
        """
        Валидация параметров таблицы.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            
        Raises:
            ValueError: Если параметры невалидны
        """
        if not cls.validate_schema_name(table_schema):
            raise ValueError(f"Invalid schema name: {table_schema}")
        if not cls.validate_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
    
    @classmethod
    def validate_columns(cls, columns: Dict[str, str]) -> None:
        """
        Валидация словаря колонок.
        
        Args:
            columns: Словарь {имя_колонки: тип_данных}
            
        Raises:
            ValueError: Если есть невалидные имена колонок
        """
        invalid_columns = []
        for column_name in columns.keys():
            if not cls.validate_column_name(column_name):
                invalid_columns.append(column_name)
        
        if invalid_columns:
            raise ValueError(f"Invalid column names: {invalid_columns}")
    
    @classmethod
    def build_safe_table_name(cls, table_schema: str, table_name: str) -> str:
        """
        Построение безопасного полного имени таблицы.
        
        Args:
            table_schema: Имя схемы
            table_name: Имя таблицы
            
        Returns:
            Безопасное полное имя таблицы
        """
        cls.validate_table_params(table_schema, table_name)
        # Для ClickHouse используем простую конкатенацию без экранирования
        return f"{table_schema}.{table_name}"
    
