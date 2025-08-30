"""
Фабрика для создания ClickHouse коннекторов.
"""

from typing import Dict, Any, Optional
from .base_connector import IClickhouseConnector


class ConnectorFactory:
    """Фабрика для создания ClickHouse коннекторов различных типов."""
    
    _connectors: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, connector_class: type) -> None:
        """
        Зарегистрировать тип коннектора.
        
        Args:
            name: Название типа коннектора
            connector_class: Класс коннектора, наследующий от IClickhouseConnector
        """
        if not issubclass(connector_class, IClickhouseConnector):
            raise ValueError(f"Класс {connector_class} должен наследовать от IClickhouseConnector")
        
        cls._connectors[name] = connector_class
    
    @classmethod
    def create(cls, connector_type: str, host: str, port: int, username: str, 
               password: str, database: str = '', secure: bool = False, verify: bool = False):
        """
        Создает коннектор указанного типа.
        
        Args:
            connector_type: Тип коннектора ('clickhouse_connect' или 'clickhouse_driver')
            host: Хост ClickHouse сервера
            port: Порт ClickHouse сервера
            username: Имя пользователя
            password: Пароль
            database: База данных (по умолчанию пустая)
            secure: Использовать SSL соединение (по умолчанию False)
            verify: Проверять SSL сертификат (по умолчанию False)
            
        Returns:
            Экземпляр коннектора
            
        Raises:
            ValueError: Если тип коннектора не поддерживается
        """
        if connector_type not in cls._connectors:
            available = list(cls._connectors.keys())
            raise ValueError(f"Неподдерживаемый тип коннектора: {connector_type}. "
                           f"Доступные типы: {available}")
        
        connector_class = cls._connectors[connector_type]
        return connector_class(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            secure=secure,
            verify=verify
        )
    
    @classmethod
    def get_available_types(cls) -> list:
        """Получить список доступных типов коннекторов."""
        return list(cls._connectors.keys())
    
    @classmethod
    def is_registered(cls, connector_type: str) -> bool:
        """Проверить, зарегистрирован ли тип коннектора."""
        return connector_type in cls._connectors
    
    @classmethod
    def get_connector_class(cls, connector_type: str) -> type:
        """Получить класс коннектора по типу."""
        if connector_type not in cls._connectors:
            raise ValueError(f"Тип коннектора не зарегистрирован: {connector_type}")
        
        return cls._connectors[connector_type]
    
    @classmethod
    def unregister(cls, connector_type: str) -> None:
        """Убрать регистрацию типа коннектора."""
        if connector_type in cls._connectors:
            del cls._connectors[connector_type]
    
    @classmethod
    def clear(cls) -> None:
        """Очистить все зарегистрированные типы коннекторов."""
        cls._connectors.clear()
