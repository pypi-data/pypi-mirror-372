

# Интерфейсы
from .base_connector import IClickhouseConnector

# Фабрика коннекторов
from .factory import ConnectorFactory

# Реализации коннекторов
from .clickhouse_connect_connector import ClickhouseConnectConnector
from .clickhouse_driver_connector import ClickhouseDriverConnector

# Регистрируем доступные типы коннекторов
ConnectorFactory.register("clickhouse_connect", ClickhouseConnectConnector)
ConnectorFactory.register("clickhouse_driver", ClickhouseDriverConnector)



