import copy
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import execute_values


def _fetch_sequence_params(cursor, table_name: str, schema_name: str = "public"):
    """
    Получает параметры последовательностей, связанных с таблицей, включая текущее значение.

    :param cursor: Объект курсора для выполнения SQL-запросов.
    :param table_name: Имя таблицы для поиска связанных последовательностей.
    :param schema_name: Имя схемы (по умолчанию "public").
    :return: Список словарей с параметрами последовательностей.
    """
    try:
        # Находим все связанные последовательности
        cursor.execute(
            """
            SELECT
                s.sequence_name,
                s.data_type,
                s.start_value,
                s.minimum_value,
                s.maximum_value,
                s.increment,
                s.cycle_option,
                s.sequence_schema
            FROM
                information_schema.sequences s
            WHERE
                s.sequence_schema = %s
                AND EXISTS (
                    SELECT 1
                    FROM information_schema.columns c
                    WHERE
                        c.table_schema = %s
                        AND c.table_name = %s
                        AND c.column_default = CONCAT(
                            'nextval(''',
                            s.sequence_schema, '.', s.sequence_name,
                            '''::regclass)'
                        )
                )
        """,
            (schema_name, schema_name, table_name),
        )

        sequences = []
        for row in cursor.fetchall():
            seq_name = row[0]
            seq_schema = row[7]

            # Получаем текущее значение только нужной последовательности.
            cursor.execute(f"SELECT last_value FROM {seq_schema}.{seq_name}")
            current_val = cursor.fetchone()[0]

            sequences.append(
                {
                    "name": seq_name,
                    "data_type": row[1],
                    "increment": row[5],
                    "minvalue": row[3],
                    "maxvalue": row[4],
                    "start": row[2],
                    "cycle": row[6] == "YES",
                    "current_value": current_val if current_val is not None else row[2],
                }
            )

        return sequences

    except Exception as e:
        print(f"Ошибка при извлечении последовательностей для {schema_name}.{table_name}: {str(e)}")  # noqa: T201
        return []


def _fetch_columns(cursor, table_name: str, schema_name: str = "public") -> List[Dict[str, Union[str, int, bool]]]:
    """
    Получение столбцов таблицы с учётом схемы.

    :param cursor: Курсор для работы с БД.
    :param table_name: Имя таблицы, для которой нужно получить информацию о столбцах.
    :param schema_name: Имя схемы (по умолчанию 'public').
    :return: Список словарей с информацией о столбцах.
    """
    cursor.execute(
        """
        SELECT
            c.column_name,
            c.data_type,
            c.character_maximum_length,  -- Длина для VARCHAR и CHAR
            c.is_nullable,
            c.column_default,
            c.udt_name,
            pg_catalog.col_description(
                format('%%I.%%I', c.table_schema, c.table_name)::regclass::oid,
                c.ordinal_position
            ) AS column_comment
        FROM
            information_schema.columns c
        WHERE
            c.table_name = %s AND c.table_schema = %s
        ORDER BY
            c.ordinal_position;
        """,
        (table_name, schema_name),
    )
    columns = cursor.fetchall()

    if not columns:
        raise ValueError(f"Не найдены столбцы для таблицы: {table_name} в схеме {schema_name}")

    return [
        {
            "name": col[0],
            "type": (col[5] if col[1] == "USER-DEFINED" else f"{col[1]}({col[2]})" if col[2] else col[1]),
            "nullable": col[3] == "YES",
            "default": col[4],
            "comment": col[6],
        }
        for col in columns
    ]


def _fetch_table_comment(cursor, table_name: str, schema_name: str = "public") -> str:
    """
    Получение комментария к таблице с учетом схемы.

    :param cursor: Курсор для работы с БД.
    :param table_name: Имя таблицы, для которой необходимо получить комментарий.
    :param schema_name: Имя схемы (по умолчанию 'public').
    :return: Строка - комментарий к таблице.
    """
    cursor.execute(
        """
        SELECT
            obj_description(format('%%I.%%I', %s, %s)::regclass) AS table_comment;
        """,
        (schema_name, table_name),
    )
    return cursor.fetchone()[0]


def _fetch_constraints(cursor, table_name: str, schema_name: str = "public") -> List[Dict[str, str]]:
    """
    Получение ограничений для таблицы.

    :param cursor: Курсор для работы с бд.
    :param  table_name: Имя таблицы.
    :param schema_name: Имя схемы (по умолчанию "public").
    :return: Список словарей с ограничениями.
    """
    cursor.execute(
        """
        SELECT
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column,
            ch.check_clause,
            tc.constraint_name,
            ccu.table_schema AS foreign_table_schema
        FROM
            information_schema.table_constraints AS tc
        LEFT JOIN
            information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_name = kcu.table_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN
            information_schema.constraint_column_usage AS ccu
            ON tc.constraint_name = ccu.constraint_name
        LEFT JOIN
            information_schema.check_constraints AS ch
            ON tc.constraint_name = ch.constraint_name
        WHERE
            tc.table_name = %s
            AND tc.table_schema = %s;
        """,
        (table_name, schema_name),
    )
    return [
        {
            "constraint_type": constraint[0],
            "column": constraint[1],
            "foreign_table": constraint[2],
            "foreign_column": constraint[3],
            "check_clause": constraint[4],
            "constraint_name": constraint[5],
            "foreign_table_schema": constraint[6],
        }
        for constraint in cursor.fetchall()
    ]


def _table_structure_to_dict(
    connection, table_name: str, schema_name: str = "public"
) -> Dict[str, Union[str, List[Dict[str, Union[str, bool, int]]]]]:
    """
    Экспортирует структуру таблицы из базы данных в словарь.

    :param connection: Объект соединения с базой данных psycopg2.
    :param table_name: Имя таблицы для экспорта.
    :param schema_name: Имя схемы (по умолчанию 'public').
    :returns: Словарь, содержащий информацию о таблице, столбцах, первичных и внешних ключах, и последовательностях.
    """
    with connection.cursor() as cursor:
        columns = _fetch_columns(cursor, table_name, schema_name)

        table_comment = _fetch_table_comment(cursor, table_name, schema_name)
        constraints = _fetch_constraints(cursor, table_name, schema_name)
        sequences = _fetch_sequence_params(cursor, table_name, schema_name)

        table_structure = {
            "table": table_name,
            "comment": table_comment,
            "columns": columns,
            "constraints": constraints,
            "sequences": sequences,
        }

    return table_structure


def _create_sequences(
    cursor,
    sequences: List[Dict[str, Union[str, int, None]]],
    table_name: str,
    old_table_name: str,
    schema_name: str = "public",
) -> None:
    """
    Создает последовательности в базе данных, учитывая все возможные параметры, включая текущее значение.

    :param cursor: Объект курсора для выполнения SQL-запросов.
    :param sequences: Список словарей, содержащих параметры последовательностей.
    :param table_name: Новое имя таблицы, заменяет старое имя в параметрах.
    :param old_table_name: Старое имя таблицы, которое будет заменено.
    :param schema_name: Имя схемы, в которой создается последовательность.
    """
    if not sequences:
        return
    for seq in sequences:
        seq_base_name = seq["name"].replace(old_table_name, table_name)
        full_seq_name = f"{schema_name}.{seq_base_name}"
        data_type = seq.get("data_type", "bigint")
        increment = seq.get("increment", 1)
        minvalue = seq.get("minvalue", "NO MINVALUE")
        maxvalue = seq.get("maxvalue", "NO MAXVALUE")
        start = seq.get("start", None)
        cycle = "CYCLE" if seq.get("cycle", False) else "NO CYCLE"
        current_value = seq.get("current_value", 1)

        # Формирование SQL-запроса
        create_sequence_sql = sql.SQL(
            """
            CREATE SEQUENCE IF NOT EXISTS {seq_name}
            AS {data_type}
            INCREMENT BY {increment}
            MINVALUE {minvalue}
            MAXVALUE {maxvalue}
            {start}
            {cycle};

            -- Set the current value of the sequence
           SELECT setval(%s, %s, true);
        """
        ).format(
            seq_name=sql.Identifier(schema_name, seq_base_name),
            data_type=sql.SQL(data_type),
            increment=sql.SQL(increment),
            minvalue=sql.SQL(minvalue),
            maxvalue=sql.SQL(maxvalue),
            start=sql.SQL(f"START WITH {start}") if start is not None else sql.SQL(""),
            cycle=sql.SQL(cycle),
        )

        cursor.execute(
            create_sequence_sql,
            (
                full_seq_name,
                current_value,
            ),
        )


def _create_table(
    cursor,
    old_table_name: str,
    new_table_name: str,
    columns: List[Dict[str, str]],
    table_comment: str = None,
    schema_name: str = "public",
) -> None:
    """
    Создает таблицу на основе предоставленных данных.

    :param cursor: Объект курсора для выполнения SQL-запросов.
    :param old_table_name: Старое имя таблицы.
    :param new_table_name: Имя таблицы.
    :param columns: Список словарей, описывающих столбцы таблицы.
    :param table_comment: Комментарий к таблице.
    :param schema_name: Имя схемы в которой создается таблица, по умолчанию "public"
    """
    column_defs = []
    for col in columns:
        col_type = col["type"]
        col_name = sql.Identifier(col["name"])
        col_def_parts = [col_name, sql.SQL(col_type)]

        if not col.get("nullable", True):
            col_def_parts.append(sql.SQL("NOT NULL"))

        if col.get("default"):
            pattern = r"(nextval\(')([^']+)(\..+::regclass)"
            default_value = sql.SQL(
                re.sub(pattern, rf"\1{schema_name}\3", col["default"]).replace(old_table_name, new_table_name)
            )
            col_def_parts.extend([sql.SQL("DEFAULT"), default_value])

        col_def = sql.SQL(" ").join(col_def_parts)
        column_defs.append(col_def)

    columns_sql = sql.SQL(",\n").join(column_defs)

    create_table_sql = sql.SQL(
        """
        CREATE TABLE {table_name} (
            {columns}
        );
    """
    ).format(
        table_name=sql.Identifier(schema_name, new_table_name),
        columns=columns_sql,
    )

    cursor.execute(create_table_sql)

    if table_comment:
        comment_sql = sql.SQL("COMMENT ON TABLE {table} IS %s;").format(
            table=sql.Identifier(schema_name, new_table_name),
        )
        cursor.execute(comment_sql, (table_comment,))

    # Комментарии к столбцам
    for col in columns:
        if "comment" in col and col["comment"]:
            comment_col_sql = sql.SQL("COMMENT ON COLUMN {table}.{column} IS %s;").format(
                table=sql.Identifier(schema_name, new_table_name),
                column=sql.Identifier(col["name"]),
            )
            cursor.execute(comment_col_sql, (col["comment"],))


def _create_constraints(
    cursor,
    old_table_name: str,
    new_table_name: str,
    constraints: List[Dict[str, str]],
    foreign_tables_mapping: Union[Dict[Tuple[str, str], Tuple[str, str]], None],
    columns_names: Set[str],
    schema_name: str = "public",
) -> None:
    """
    Создает все ограничения для таблицы.

    :param cursor: Объект курсора для выполнения SQL-запросов.
    :param new_table_name: Имя таблицы.
    :param constraints: Список словарей, описывающих ограничения.
    :param foreign_tables_mapping: Словарь соответствия имен связанных таблиц и схем в словаре и в базе данных состоит
    из кортежей с парой значений ("имя_схемы", "имя_таблицы") ключи имена в словаре, значения в имена базе.
    :param columns_names: Имена столбцов таблицы для их оборачивания в кавычки.
    :param schema_name: Имя схемы, по умолчанию "public".
    """

    def replace_match(match: re.Match) -> str:
        """Оборачивает в кавычки слово если оно соответствует названию столбца."""
        word = match.group(0)
        return f'"{word}"' if word in columns_names else word

    primary_key_columns = []
    for constraint in constraints:
        if constraint["constraint_type"] == "PRIMARY KEY" and constraint["column"] not in primary_key_columns:
            primary_key_columns.append(constraint["column"])

    if primary_key_columns:
        primary_key_sql = sql.SQL(
            """
               ALTER TABLE {table}
               ADD CONSTRAINT {constraint_name}
               PRIMARY KEY ({columns});
           """
        ).format(
            table=sql.Identifier(schema_name, new_table_name),
            constraint_name=sql.Identifier(f"{new_table_name}_pkey"),
            columns=sql.SQL(", ").join(map(sql.Identifier, primary_key_columns)),
        )
        cursor.execute(primary_key_sql)

    for constraint in constraints:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_name = (
                foreign_tables_mapping.get(
                    (
                        constraint["foreign_table_schema"],
                        constraint["foreign_table"],
                    ),
                    (
                        constraint["foreign_table_schema"],
                        constraint["foreign_table"],
                    ),
                )
                if foreign_tables_mapping
                else (
                    constraint["foreign_table_schema"],
                    constraint["foreign_table"],
                )
            )
            constraint_sql = sql.SQL(
                """
                ALTER TABLE {table}
                ADD CONSTRAINT {constraint_name}
                FOREIGN KEY ({column})
                REFERENCES {foreign_table} ({foreign_column});
            """
            ).format(
                table=sql.Identifier(schema_name, new_table_name),
                constraint_name=sql.Identifier(f"{new_table_name}_{constraint['column']}_fkey"),
                column=sql.Identifier(constraint["column"]),
                foreign_table=sql.Identifier(foreign_table_name[0], foreign_table_name[1]),
                foreign_column=sql.Identifier(constraint["foreign_column"]),
            )

        elif constraint["constraint_type"] == "UNIQUE":
            constraint_sql = sql.SQL(
                """
                ALTER TABLE {table}
                ADD CONSTRAINT {constraint_name}
                UNIQUE ({column});
            """
            ).format(
                table=sql.Identifier(schema_name, new_table_name),
                constraint_name=sql.Identifier(f"uq_{new_table_name}_{constraint['column']}"),
                column=sql.Identifier(constraint["column"]),
            )

        elif constraint["constraint_type"] == "CHECK":
            if constraint["check_clause"].find("IS NOT NULL") != -1:
                continue  # NOT NULL задается через свойства столбцов. Поэтому если попадается такое ограничение мы его
                # пропускаем
            check_clause = constraint["check_clause"].replace(old_table_name, new_table_name)

            pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b")
            check_clause = pattern.sub(replace_match, check_clause)
            check_clause = check_clause.replace('""', '"')
            constraint_sql = sql.SQL(
                """
                ALTER TABLE {table}
                ADD CONSTRAINT {constraint_name}
                CHECK ({check_clause});
            """
            ).format(
                table=sql.Identifier(schema_name, new_table_name),
                constraint_name=sql.Identifier(constraint["constraint_name"].replace(old_table_name, new_table_name)),
                check_clause=sql.SQL(check_clause),
            )
        else:
            continue

        cursor.execute(constraint_sql)


def _create_table_from_dict(
    connection,
    table_structure: Dict[str, Union[str, List[str], List[Dict[str, str]]]],
    new_table_name: Union[str, None] = None,
    foreign_tables_mapping: Union[Dict[Tuple[str, str], Tuple[str, str]], None] = None,
    schema_name="public",
) -> None:
    """
    Создает таблицу в базе данных PostgreSQL на основе структуры, описанной в словаре.

    :param connection: Объект соединения с базой данных psycopg2.
    :param table_structure: Словарь содержащий структуру таблицы.
    :param new_table_name: Имя таблицы в базе данных.
    :param foreign_tables_mapping: Словарь соответствия имен связанных таблиц и схем в словаре и в базе данных состоит
    из кортежей с парой значений ("имя_схемы", "имя_таблицы") ключи имена в словаре, значения в имена базе.
    :param schema_name: Имя схемы (по умолчанию 'public').
    """
    table_name = new_table_name if new_table_name else table_structure["table"]
    table_comment = table_structure.get("comment")
    columns = table_structure.get("columns", [])
    columns_names = {column["name"] for column in columns}
    constraints = table_structure.get("constraints", [])
    sequences = table_structure.get("sequences", [])

    with connection.cursor() as cursor:
        # Создание последовательностей, если они указаны
        _create_sequences(
            cursor,
            sequences=sequences,
            table_name=table_name,
            old_table_name=table_structure["table"],
            schema_name=schema_name,
        )

        # Создание таблицы
        _create_table(
            cursor,
            old_table_name=table_structure["table"],
            new_table_name=table_name,
            columns=columns,
            table_comment=table_comment,
            schema_name=schema_name,
        )

        # Создание ограничений и внешних ключей
        _create_constraints(
            cursor,
            table_structure["table"],
            table_name,
            constraints,
            foreign_tables_mapping,
            columns_names,
            schema_name=schema_name,
        )


def _compare_table_structure(
    connection,
    table_structure: Dict[str, Union[str, List[Dict[str, Union[str, bool, int, None]]]]],
    table_name: str,
    foreign_tables_mapping: Union[Dict[Tuple[str, str], Tuple[str, str]], None] = None,
    schema_name: str = "public",
) -> bool:
    """
    Сравнивает структуру таблицы из базы данных с переданной структурой таблицы.

    :param connection: Объект соединения с базой данных psycopg2.
    :param table_structure: Словарь содержащий структуру таблицы.
    :param table_name: Имя таблицы в базе данных с которой осуществляется сравнение.
    :param foreign_tables_mapping: Словарь соответствия имен связанных таблиц и схем в словаре и в базе данных состоит
    из кортежей с парой значений ("имя_схемы", "имя_таблицы") ключи имена в словаре, значения в имена базе.
    :param schema_name: Имя схемы (по умолчанию 'public').
    :return: True если основные параметры таблиц совпадают. False если различаются.
    """
    table_from_db = _table_structure_to_dict(connection, table_name=table_name, schema_name=schema_name)
    old_table_name = table_structure["table"]
    # Сравнение столбцов
    structure_columns = {col["name"]: col for col in table_structure["columns"]}
    db_columns = {col["name"]: col for col in table_from_db["columns"]}
    if structure_columns.keys() != db_columns.keys():
        return False
    pattern = r"(nextval\(')([^']+)(\..+::regclass)"
    for column_name, structure_column in structure_columns.items():
        db_column = db_columns[column_name]

        if (
            structure_column["default"]
            and re.sub(pattern, rf"\1{schema_name}\3", structure_column["default"]).replace(old_table_name, table_name)
            != db_column["default"]
        ):
            return False
        if structure_column["nullable"] != db_column["nullable"]:
            return False
        if structure_column["type"] != db_column["type"]:
            return False

    # Изменяем имя таблиц в constraints на новые и удаляем имя ограничения
    constraints_structure = copy.deepcopy(table_structure["constraints"])
    for constraint in constraints_structure:
        if constraint["constraint_type"] == "PRIMARY KEY" or constraint["constraint_type"] == "UNIQUE":
            constraint["foreign_table"] = table_name
        if constraint["constraint_type"] == "FOREIGN KEY":
            constraint["foreign_table_schema"], constraint["foreign_table"] = (
                foreign_tables_mapping.get(
                    (
                        constraint["foreign_table_schema"],
                        constraint["foreign_table"],
                    ),
                    (
                        constraint["foreign_table_schema"],
                        constraint["foreign_table"],
                    ),
                )
                if foreign_tables_mapping
                else (
                    constraint["foreign_table_schema"],
                    constraint["foreign_table"],
                )
            )
        constraint.pop("constraint_name")
    constraints_db = table_from_db["constraints"]
    for constraint in constraints_db:
        constraint.pop("constraint_name")

    # Преобразуем списки ограничений в словари для удобства сравнения
    def constraints_to_dict(
        constraints: List[Dict[str, str]],
    ) -> Dict[str, Dict[str, str]]:
        return {f"{c['constraint_type']}_{c['column']}": c for c in constraints}

    constraints_structure = constraints_to_dict(constraints_structure)
    constraints_db = constraints_to_dict(constraints_db)

    if constraints_structure != constraints_db:
        return False

    # Проверка на совпадение последовательностей
    seq_structure = table_structure["sequences"]
    if seq_structure:
        for seq in seq_structure:
            seq["name"] = seq["name"].replace(old_table_name, table_name)
        seq_structure = sorted(seq_structure, key=lambda x: x["name"])
        seq_db = sorted(table_from_db["sequences"], key=lambda x: x["name"])
        if len(seq_structure) != len(seq_db):
            return False
        for index in range(len(seq_db)):
            if seq_db[index]["name"] != seq_structure[index]["name"]:
                return False
            if seq_db[index]["cycle"] != seq_structure[index]["cycle"]:
                return False
            if seq_db[index]["data_type"] != seq_structure[index]["data_type"]:
                return False
            if seq_db[index]["increment"] != seq_structure[index]["increment"]:
                return False
            if seq_db[index]["maxvalue"] != seq_structure[index]["maxvalue"]:
                return False
            if seq_db[index]["minvalue"] != seq_structure[index]["minvalue"]:
                return False
            if seq_db[index]["start"] != seq_structure[index]["start"]:
                return False
    else:
        seq_db = table_from_db["sequences"]
        if seq_db:
            return False
    return True


def _export_table_data(connection, table_name: str, schema_name: str = "public") -> List[Dict[str, Any]]:
    """
    Экспортирует данные таблицы в виде списка словарей.

    :param connection: Объект соединения с базой данных psycopg2.
    :param table_name: Имя таблицы в базе данных данные из которой необходимо экспортировать.
    :param schema_name: Имя схемы (по умолчанию "public").
    :return: Список словарей содержащий данные таблицы.
    """
    with connection.cursor() as cursor:
        query = sql.SQL("SELECT * FROM {table};").format(table=sql.Identifier(schema_name, table_name))
        cursor.execute(query)
        rows: List[tuple] = cursor.fetchall()

        # Получение названий столбцов
        column_names: List[str] = [desc[0] for desc in cursor.description]

        # Преобразование данных в список словарей
        data: List[Dict[str, Any]] = []
        for row in rows:
            row_dict: Dict[str, Any] = {column_names[i]: row[i] for i in range(len(column_names))}
            data.append(row_dict)
        return data


def _export_with_connection(connection: PgConnection, table_name: str, schema_name: str) -> Dict[str, Any]:
    """Внутренняя функция для экспорта с использованием подключения."""
    table = {
        "structure": _table_structure_to_dict(connection, table_name, schema_name),
        "data": _export_table_data(connection, table_name, schema_name),
    }
    return table


def export_table_to_dict(
    table_name: str,
    schema_name: str = "public",
    connection: Optional[Any] = None,
    dbname: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Преобразует таблицу в словарь со структурой и данными.

    :param table_name: Имя таблицы в базе данных.
    :param dbname: Имя базы данных.
    :param connection: Существующее подключение.
    :param user: Пользователь БД.
    :param password: Пароль пользователя.
    :param host: Адрес сервера баз данных.
    :param port: Порт сервера баз данных.
    :param schema_name: Имя схемы (по умолчанию "public").
    :return: Словарь со структурой и данными таблицы.
    """
    if connection is None:
        required_params = [dbname, user, password, host, port]
        if any(param is None for param in required_params):
            raise ValueError(
                "Все параметры подключения (dbname, user, password, host, port) "
                "должны быть указаны когда connection не предоставлен"
            )

        with psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port) as new_connection:
            return _export_with_connection(new_connection, table_name, schema_name)
    else:
        return _export_with_connection(connection, table_name, schema_name)


def _table_exists(connection, table_name, schema_name: str = "public"):
    """
    Проверяет, существует ли таблица с именем table_name в базе данных conn.

    :param connection: Подключение к базе данных psycopg2
    :param table_name: Имя таблицы (строка)
    :param schema_name: Имя схемы (по умолчанию "public").
    :return: True, если таблица существует, иначе False
    """
    with connection.cursor() as cursor:
        query = sql.SQL(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s
            );
        """
        )
        cursor.execute(
            query,
            (
                schema_name,
                table_name,
            ),
        )
        result = cursor.fetchone()
        return result[0]


def _import_table_data(
    connection,
    table_name: str,
    table_data: List[Dict[str, Any]],
    table_structure: Dict[str, Any],
    foreign_tables_mapping: Union[Dict[Tuple[str, str], Tuple[str, str]], None] = None,
    schema_name: str = "public",
) -> None:
    """
    Импортирует данные из списка словарей в таблицу при этом заменяя старые данные новыми.

    :param connection: Объект соединения с базой данных psycopg2.
    :param table_name: Имя таблицы в базе данных в которую осуществляется импорт.
    :param table_data: Данные для импорта.
    :param table_structure: Метаданные о структуре таблицы.
    :param schema_name: Имя схемы (по умолчанию "public")
    """
    if foreign_tables_mapping is None:
        foreign_tables_mapping = {}
    with connection.cursor() as cursor:
        primary_keys = []
        columns_names = [column["name"] for column in table_structure["columns"]]
        constraints = _fetch_constraints(cursor, table_name, schema_name=schema_name)
        self_foreign_key_constraints = []
        for constraint in constraints:
            if constraint["constraint_type"] == "PRIMARY KEY":
                primary_keys.append(constraint["column"])
            if constraint["constraint_type"] == "FOREIGN KEY" and foreign_tables_mapping.get(
                (
                    constraint["foreign_table_schema"],
                    constraint["foreign_table"],
                ),
                (
                    constraint["foreign_table_schema"],
                    constraint["foreign_table"],
                ),
            ) == (
                schema_name,
                table_name,
            ):
                constraint_copy = constraint.copy()
                constraint_copy["foreign_table"] = table_name
                self_foreign_key_constraints.append(constraint_copy)
        for constraint in self_foreign_key_constraints:
            drop_constraint_sql = sql.SQL(
                """
                ALTER TABLE {table}
                DROP CONSTRAINT {constraint_name};
                """,
            ).format(
                table=sql.Identifier(schema_name, table_name),
                constraint_name=sql.Identifier(f"{constraint['constraint_name']}"),
            )
            cursor.execute(drop_constraint_sql)
        if table_data:
            ids_to_keep = tuple(tuple(data[pk] for pk in primary_keys) for data in table_data)
            delete_query = sql.SQL(
                """
                DELETE FROM {table}
                WHERE ({columns}) NOT IN %s;
                """,
            ).format(
                table=sql.Identifier(schema_name, table_name),
                columns=sql.SQL(", ").join(map(sql.Identifier, (primary_keys))),
            )
            cursor.execute(delete_query, (ids_to_keep,))

            insert_query = sql.SQL(
                """
            INSERT INTO {table} ({columns})
            VALUES %s
            ON CONFLICT ({pk}) DO UPDATE SET
            ({columns}) = ROW({excluded});
            """
            ).format(
                table=sql.Identifier(schema_name, table_name),
                columns=sql.SQL(", ").join(map(sql.Identifier, (columns_names))),
                pk=sql.SQL(", ").join(map(sql.Identifier, (primary_keys))),
                excluded=sql.SQL(", ").join(map(sql.SQL, (f"EXCLUDED.{x}" for x in columns_names))),
            )
            values = [tuple(data[column] for column in columns_names) for data in table_data]
            execute_values(cursor, insert_query, values)
        for constraint in self_foreign_key_constraints:
            constraint_sql = sql.SQL(
                """
                ALTER TABLE {table}
                ADD CONSTRAINT {constraint_name}
                FOREIGN KEY ({column})
                REFERENCES {foreign_table} ({foreign_column});
            """
            ).format(
                table=sql.Identifier(schema_name, table_name),
                constraint_name=sql.Identifier(f"fk_{table_name}_{constraint['column']}"),
                column=sql.Identifier(constraint["column"]),
                foreign_table=sql.Identifier(constraint["foreign_table_schema"], constraint["foreign_table"]),
                foreign_column=sql.Identifier(constraint["foreign_column"]),
            )
            cursor.execute(constraint_sql)


def _import_with_connection(
    connection: Any,
    table_structure: Dict[str, Any],
    table_data: List[Dict[str, Any]],
    table_name: str,
    foreign_tables_mapping: Optional[Dict[Tuple[str, str], Tuple[str, str]]],
    schema_name: str,
) -> None:
    """Внутренняя функция для импорта с использованием подключения."""
    if not _table_exists(connection, table_name=table_name, schema_name=schema_name):
        _create_table_from_dict(
            connection,
            table_structure=table_structure,
            new_table_name=table_name,
            foreign_tables_mapping=foreign_tables_mapping,
            schema_name=schema_name,
        )
    else:
        if not _compare_table_structure(
            connection,
            table_structure=table_structure,
            table_name=table_name,
            foreign_tables_mapping=foreign_tables_mapping,
            schema_name=schema_name,
        ):
            raise ValueError("Структура таблицы в базе данных не совпадает с переданной")
        _import_table_data(
            connection,
            table_name=table_name,
            table_data=table_data,
            table_structure=table_structure,
            foreign_tables_mapping=foreign_tables_mapping,
            schema_name=schema_name,
        )


def import_table_from_dict(
    table: Dict[str, Any],
    table_name: str,
    dbname: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[str] = None,
    foreign_tables_mapping: Optional[Dict[Tuple[str, str], Tuple[str, str]]] = None,
    schema_name: str = "public",
    connection: Optional[Any] = None,
) -> None:
    """
    Импортирует данные из словаря в базу данных.

    :param table: Структура таблицы и данные для импорта в виде словаря.
    :param table_name: Имя таблицы в базе данных.
    :param dbname: Имя базы данных.
    :param user: Пользователь БД.
    :param password: Пароль пользователя.
    :param host: Адрес сервера баз данных.
    :param port: Порт сервера баз данных.
    :param foreign_tables_mapping: Словарь соответствия имен связанных таблиц и схем в словаре и в базе данных состоит
    из кортежей с парой значений ("имя_схемы", "имя_таблицы") ключи имена в словаре, значения в имена базе.
    :param schema_name: Имя схемы (по умолчанию 'public').
    """
    if connection is None and any(param is None for param in [dbname, user, password, host, port]):
        raise ValueError("Все параметры подключения должны быть указаны когда connection не предоставлен")

    table_structure = table["structure"]
    table_data = table["data"]

    if connection is not None:
        _import_with_connection(
            connection, table_structure, table_data, table_name, foreign_tables_mapping, schema_name
        )
    else:
        with psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port) as new_connection:
            _import_with_connection(
                new_connection, table_structure, table_data, table_name, foreign_tables_mapping, schema_name
            )
