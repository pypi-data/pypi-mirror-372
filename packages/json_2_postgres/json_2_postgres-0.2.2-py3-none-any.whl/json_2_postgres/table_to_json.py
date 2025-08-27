import contextlib
import json
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Tuple, Union

from . import import_table_from_dict


def _serialize_to_str(obj: Any) -> str:
    """
    Если переданный объект имеет типа datetime, то преобразует его в строку в iso формате.

    :param obj: Объект для сериализации
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def _deserialize_from_str(dct: Dict[str, Any]) -> Dict[str, Any]:
    """
    Десереализует переданные значения в поддерживаемые типы данных.

    :param dct: Словарь содержащий данные для десериализации.
    """
    for key, value in dct.items():
        if isinstance(value, str) and len(value) >= 10:
            with contextlib.suppress(ValueError):
                dct[key] = datetime.fromisoformat(value)
    return dct


def dict_as_json(table: Dict[str, Any]) -> BytesIO:
    """
    Сохранение структуры и данных таблицы в буфер в json формате.

    :param table: Структура для сохранения в json формате.
    :return: Объект BytesIO содержащий "файл" с переданной структурой в json формате.
    """
    buffer = BytesIO()
    buffer.write(json.dumps(table, indent=4, default=_serialize_to_str, ensure_ascii=False).encode())
    buffer.seek(0)
    return buffer


def json_to_table(
    data_source: Union[str, BytesIO],
    table_name: str,
    dbname: str,
    user: str,
    password: str,
    host: str,
    port: str,
    foreign_tables_mapping: Union[Dict[Tuple[str, str], Tuple[str, str]], None] = None,
    schema_name: str = "public",
) -> None:
    """
    Загружает данные из файла или BytesIO объекта в формате json и импортирует их в таблицу.

    :param data_source: Путь к файлу или BytesIO объект
    :param table_name: Имя таблицы в базе данных.
    :param dbname: Имя базы данных.
    :param user: Пользователь БД.
    :param password: Пароль пользователя.
    :param host: Адрес сервера баз данных.
    :param port: Порт сервера баз данных.
    :param foreign_tables_mapping: Словарь соответствия имен связанных таблиц и схем в json и в базе данных состоит
    из кортежей с парой значений ("имя_схемы", "имя_таблицы") ключи имена в json, значения в имена базе.
    """
    if isinstance(data_source, str):
        # Если это строка пытаемся загрузить json из файла
        with open(data_source, "r", encoding="utf-8") as file:
            data = json.load(file, object_hook=_deserialize_from_str)
    elif isinstance(data_source, (BytesIO)):
        # Если это BytesIO объект
        data_source.seek(0)
        data = json.load(data_source, object_hook=_deserialize_from_str)
    else:
        raise TypeError("Неподдерживаемый тип хранилища данных")
    import_table_from_dict(
        data,
        table_name,
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        foreign_tables_mapping=foreign_tables_mapping,
        schema_name=schema_name,
    )
