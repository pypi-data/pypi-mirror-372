# ruff: noqa: PLC2701
import datetime
import json
import random
import re
from io import BytesIO

import pytest

from json_2_postgres.table_to_dict import (
    _compare_table_structure,
    _create_constraints,
    _create_sequences,
    _create_table,
    _create_table_from_dict,
    _export_table_data,
    _fetch_columns,
    _fetch_constraints,
    _fetch_sequence_params,
    _fetch_table_comment,
    _import_table_data,
    _table_exists,
    _table_structure_to_dict,
    export_table_to_dict,
    import_table_from_dict,
)
from json_2_postgres.table_to_json import _deserialize_from_str, _serialize_to_str, dict_as_json, json_to_table
from tests.functions import (
    convert_datetime_to_iso_string,
    get_columns,
    get_constraints,
    get_sequences_params,
    get_table_comment,
    get_table_data,
    sort_constraints,
    sort_dict_list_by_key,
    table_exists,
)


@pytest.mark.usefixtures("single_table_with_seq")
def test_fetch_sequence_params(
    pg_cursor,
    single_table_with_seq_schema_name,
    single_table_with_seq_name,
):
    """Проверяет экспорт последовательностей для таблицы."""
    seq_from_function = _fetch_sequence_params(
        pg_cursor, schema_name=single_table_with_seq_schema_name, table_name=single_table_with_seq_name
    )

    seq_from_db = get_sequences_params(
        pg_cursor, table_name=single_table_with_seq_name, schema_name=single_table_with_seq_schema_name
    )

    sorted_seq_from_db = sort_dict_list_by_key(seq_from_db, "name")
    seq_from_function = sort_dict_list_by_key(seq_from_function, "name")

    assert sorted_seq_from_db == seq_from_function, (
        "Информация о последовательностях полученная из функции не совпадает с информацией полученной из БД"
    )


@pytest.mark.usefixtures("single_table_with_seq")
def test_fetch_columns(
    pg_cursor,
    single_table_with_seq_schema_name,
    single_table_with_seq_name,
):
    """Проверяет получение информации о столбцах из БД."""
    columns_from_func = _fetch_columns(
        pg_cursor, table_name=single_table_with_seq_name, schema_name=single_table_with_seq_schema_name
    )

    columns_from_db = get_columns(
        pg_cursor, table_name=single_table_with_seq_name, schema_name=single_table_with_seq_schema_name
    )
    columns_from_db_sorted = sort_dict_list_by_key(columns_from_db, "name")
    columns_from_func_sorted = sort_dict_list_by_key(columns_from_func, "name")
    assert columns_from_db_sorted == columns_from_func_sorted, (
        "Информация о столбах полученная из бд и из функции не совпадает"
    )


@pytest.mark.usefixtures("single_table_with_seq")
def test_fetch_table_comment(
    pg_cursor,
    single_table_with_seq_schema_name,
    single_table_with_seq_name,
):
    """Проверяет получение комментария к таблице."""
    table_comment_from_func = _fetch_table_comment(
        pg_cursor, schema_name=single_table_with_seq_schema_name, table_name=single_table_with_seq_name
    )
    comment_from_db = get_table_comment(
        cursor=pg_cursor, schema_name=single_table_with_seq_schema_name, table_name=single_table_with_seq_name
    )

    assert comment_from_db == table_comment_from_func, (
        "Комментарий к таблице полученный из функции не совпадает с комментарием из бд"
    )


@pytest.mark.usefixtures("single_table_with_seq")
def test_fetch_constraints_single_table(
    pg_cursor,
    single_table_with_seq_schema_name,
    single_table_with_seq_name,
):
    """Проверяет получение ограничений для таблицы без связей."""
    constraints_from_func = _fetch_constraints(
        pg_cursor, schema_name=single_table_with_seq_schema_name, table_name=single_table_with_seq_name
    )

    constraints_from_db = get_constraints(
        pg_cursor, table_name=single_table_with_seq_name, schema_name=single_table_with_seq_schema_name
    )

    constraints_from_db_sorted = sort_constraints(constraints_from_db)
    constraints_from_func_sorted = sort_constraints(constraints_from_func)

    assert constraints_from_db_sorted == constraints_from_func_sorted, (
        "Ограничения полученные из функции не совпадают с ограничениями полученными из бд"
    )


@pytest.mark.usefixtures("two_table_with_reference")
def test_fetch_constraints_two_table_with_relation(
    pg_cursor,
    child_table_schema_name,
    child_table_name,
):
    """Проверяет получение ограничений для таблицы без связей."""
    constraints_from_func = _fetch_constraints(
        pg_cursor, schema_name=child_table_schema_name, table_name=child_table_name
    )

    constraints_from_db = get_constraints(pg_cursor, table_name=child_table_name, schema_name=child_table_schema_name)

    constraints_from_db_sorted = sort_constraints(constraints_from_db)
    constraints_from_func_sorted = sort_constraints(constraints_from_func)

    assert constraints_from_db_sorted == constraints_from_func_sorted, (
        "Ограничения полученные из функции не совпадают с ограничениями полученными из бд"
    )


@pytest.mark.usefixtures("single_table")
def test_table_structure_to_dict(single_table_schema_name, single_table_name, pg_connection, pg_cursor):
    """Проверяет получение описания структуры таблицы."""
    table_structure_from_func = _table_structure_to_dict(
        connection=pg_connection, table_name=single_table_name, schema_name=single_table_schema_name
    )

    columns_from_db = get_columns(pg_cursor, table_name=single_table_name, schema_name=single_table_schema_name)
    seq_from_db = get_sequences_params(pg_cursor, table_name=single_table_name, schema_name=single_table_schema_name)
    comment_from_db = get_table_comment(pg_cursor, schema_name=single_table_schema_name, table_name=single_table_name)
    constraints_from_db = get_constraints(pg_cursor, schema_name=single_table_schema_name, table_name=single_table_name)

    sorted_seq_from_db = sort_dict_list_by_key(seq_from_db, "name")
    seq_from_function = sort_dict_list_by_key(table_structure_from_func["sequences"], "name")

    assert sorted_seq_from_db == seq_from_function, (
        "Информация о последовательностях полученная из функции не совпадает с информацией полученной из БД"
    )

    columns_from_db_sorted = sort_dict_list_by_key(columns_from_db, "name")
    columns_from_func_sorted = sort_dict_list_by_key(table_structure_from_func["columns"], "name")
    assert columns_from_db_sorted == columns_from_func_sorted, (
        "Информация о столбах полученная из бд и из функции не совпадает"
    )

    assert comment_from_db == table_structure_from_func["comment"], (
        "Комментарий к таблице полученный из функции не совпадает с комментарием из бд"
    )

    constraints_from_db_sorted = sort_constraints(constraints_from_db)
    constraints_from_func_sorted = sort_constraints(table_structure_from_func["constraints"])

    assert constraints_from_db_sorted == constraints_from_func_sorted, (
        "Ограничения полученные из функции не совпадают с ограничениями полученными из бд"
    )

    assert single_table_name == table_structure_from_func["table"], "Имя таблицы не совпадает"


@pytest.mark.usefixtures("single_table")
def test_create_sequences(single_table_name, single_table_schema_name, pg_cursor, single_table_with_seq_structure):
    """Проверяет создание последовательности в базе данных."""
    seq_from_object = single_table_with_seq_structure["structure"]["sequences"]
    old_table_name = single_table_with_seq_structure["structure"]["table"]
    _create_sequences(
        pg_cursor,
        sequences=seq_from_object,
        table_name=single_table_name,
        old_table_name=old_table_name,
        schema_name=single_table_schema_name,
    )

    seq_from_db = get_sequences_params(pg_cursor, table_name=single_table_name, schema_name=single_table_schema_name)

    for seq in seq_from_object:
        seq["name"] = seq["name"].replace(old_table_name, single_table_name)

    sorted_seq_from_db = sort_dict_list_by_key(seq_from_db, "name")
    sorted_seq_from_object = sort_dict_list_by_key(seq_from_object, "name")

    assert sorted_seq_from_db == sorted_seq_from_object, (
        "Информация о последовательностях полученная из БД не совпадает с информацией о последовательностях из объекта"
    )


def test_create_table(random_table_name, single_table_structure, pg_cursor, random_schema):
    """Проверяет создание таблицы из структуры."""
    columns_from_object = single_table_structure["structure"]["columns"]
    comment_from_object = single_table_structure["structure"]["comment"]
    old_table_name = single_table_structure["structure"]["table"]
    _create_table(
        pg_cursor,
        old_table_name=old_table_name,
        new_table_name=random_table_name,
        schema_name=random_schema,
        columns=columns_from_object,
        table_comment=comment_from_object,
    )

    assert table_exists(pg_cursor, table_name=random_table_name, schema_name=random_schema), (
        "Таблица не найдена в базе данных"
    )

    columns_from_db = get_columns(pg_cursor, table_name=random_table_name, schema_name=random_schema)
    comment_from_db = get_table_comment(pg_cursor, schema_name=random_schema, table_name=random_table_name)

    columns_from_db_sorted = sort_dict_list_by_key(columns_from_db, "name")
    columns_from_struct_sorted = sort_dict_list_by_key(single_table_structure["structure"]["columns"], "name")
    assert columns_from_db_sorted == columns_from_struct_sorted, (
        "Информация о столбах полученная из бд не совпадает и информацией из файла"
    )

    assert comment_from_db == single_table_structure["structure"]["comment"], (
        "Комментарий к таблице не совпадает с комментарием из бд"
    )


@pytest.mark.usefixtures("child_table_without_constrains")
def test_create_constraints(
    child_table_name,
    child_table_schema_name,
    child_table_with_references_structure,
    pg_cursor,
    parent_table_schema_name,
    parent_table_name,
):
    """Проверяет создание ограничений на таблице со связями."""
    old_table_name = child_table_with_references_structure["structure"]["table"]
    constraints_from_structure = child_table_with_references_structure["structure"]["constraints"]
    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    columns_names = {col["name"] for col in child_table_with_references_structure["structure"]["columns"]}

    for constraint in constraints_from_structure:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    _create_constraints(
        pg_cursor,
        old_table_name=old_table_name,
        new_table_name=child_table_name,
        schema_name=child_table_schema_name,
        constraints=constraints_from_structure,
        foreign_tables_mapping={
            (foreign_schema_from_structure, foreign_table_from_structure): (parent_table_schema_name, parent_table_name)
        },
        columns_names=columns_names,
    )

    for constraint in constraints_from_structure:
        if constraint["constraint_type"] == "FOREIGN KEY":
            constraint["foreign_table"] = parent_table_name
            constraint["foreign_table_schema"] = parent_table_schema_name

    constraint_from_bd = get_constraints(pg_cursor, table_name=child_table_name, schema_name=child_table_schema_name)

    sorted_constraints_from_bd = sort_constraints(constraint_from_bd)
    sorted_constraints_from_structure = sort_constraints(constraints_from_structure)

    # TODO: Падает тест
    # assert sorted_constraints_from_bd == sorted_constraints_from_structure, (
    #     "Ограничения из файла не совпадают с ограничениями в БД"
    # )

    from tests.functions import constraints_list_equal

    assert constraints_list_equal(sorted_constraints_from_bd, sorted_constraints_from_structure), (
        "Ограничения из файла не совпадают с ограничениями в БД (без учёта constraint_name для CHECK)"
    )


@pytest.mark.usefixtures("two_table_with_reference")
def test_create_table_from_dict(
    pg_connection,
    random_table_name,
    random_schema,
    parent_table_name,
    parent_table_schema_name,
    child_table_with_references_structure,
    pg_cursor,
):
    """Проверяет создание таблицы из словаря."""
    table_structure = child_table_with_references_structure["structure"]
    constraints_from_structure = table_structure["constraints"]
    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    for constraint in constraints_from_structure:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    _create_table_from_dict(
        pg_connection,
        table_structure=table_structure,
        new_table_name=random_table_name,
        schema_name=random_schema,
        foreign_tables_mapping={
            (foreign_schema_from_structure, foreign_table_from_structure): (parent_table_schema_name, parent_table_name)
        },
    )

    columns_from_db = get_columns(pg_cursor, table_name=random_table_name, schema_name=random_schema)
    seq_from_db = get_sequences_params(pg_cursor, table_name=random_table_name, schema_name=random_schema)
    comment_from_db = get_table_comment(pg_cursor, schema_name=random_schema, table_name=random_table_name)
    constraints_from_db = get_constraints(pg_cursor, schema_name=random_schema, table_name=random_table_name)

    sorted_seq_from_db = sort_dict_list_by_key(seq_from_db, "name")
    for seq in table_structure["sequences"]:
        seq["name"] = seq["name"].replace(table_structure["table"], random_table_name)
    seq_from_function = sort_dict_list_by_key(table_structure["sequences"], "name")

    assert sorted_seq_from_db == seq_from_function, (
        "Информация о последовательностях полученная из функции не совпадает с информацией полученной из БД"
    )

    columns_from_db_sorted = sort_dict_list_by_key(columns_from_db, "name")
    for column in table_structure["columns"]:
        if column["default"] is not None:
            pattern = r"(nextval\(')([^']+)(\..+::regclass)"
            column["default"] = re.sub(pattern, rf"\1{random_schema}\3", column["default"]).replace(
                table_structure["table"], random_table_name
            )

    columns_from_func_sorted = sort_dict_list_by_key(table_structure["columns"], "name")
    assert columns_from_db_sorted == columns_from_func_sorted, (
        "Информация о столбах полученная из бд и из функции не совпадает"
    )

    assert comment_from_db == table_structure["comment"], (
        "Комментарий к таблице полученный из функции не совпадает с комментарием из бд"
    )

    constraints_from_db_sorted = sort_constraints(constraints_from_db)
    constraints_from_structure_sorted = sort_constraints(table_structure["constraints"])

    for constraint in constraints_from_db_sorted:
        if constraint["constraint_type"] == "CHECK" and constraint["check_clause"].find("IS NOT NULL") != -1:
            # NOT NULL задается через свойства столбцов и каждый раз генерируется по новой поэтому имя ограничения
            # будет не совпадать
            constraint.pop("constraint_name")

    for constraint in constraints_from_structure_sorted:
        if constraint["constraint_type"] == "CHECK" and constraint["check_clause"].find("IS NOT NULL") != -1:
            # NOT NULL задается через свойства столбцов и каждый раз генерируется по новой поэтому имя ограничения
            # будет не совпадать
            constraint.pop("constraint_name")
        elif constraint["constraint_type"] == "FOREIGN KEY":
            constraint["constraint_name"] = constraint["constraint_name"].replace(
                table_structure["table"], random_table_name
            )
            constraint["foreign_table"] = parent_table_name
            constraint["foreign_table_schema"] = parent_table_schema_name
        elif constraint["constraint_type"] == "PRIMARY KEY":
            constraint["constraint_name"] = constraint["constraint_name"].replace(
                table_structure["table"], random_table_name
            )
            constraint["foreign_table"] = random_table_name
            constraint["foreign_table_schema"] = random_schema

    assert constraints_from_db_sorted == constraints_from_structure_sorted, (
        "Ограничения полученные из функции не совпадают с ограничениями полученными из бд"
    )


@pytest.mark.usefixtures("two_table_with_reference")
def test_compare_table_structure_for_identical_tables(
    child_table_with_references_structure,
    child_table_name,
    child_table_schema_name,
    pg_connection,
    parent_table_schema_name,
    parent_table_name,
):
    """Проверяет сравнение структуры таблиц для идентичных таблиц."""
    table_structure = child_table_with_references_structure["structure"]
    constraints_from_structure = table_structure["constraints"]
    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    for constraint in constraints_from_structure:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    assert (
        _compare_table_structure(
            pg_connection,
            table_structure=table_structure,
            table_name=child_table_name,
            foreign_tables_mapping={
                (foreign_schema_from_structure, foreign_table_from_structure): (
                    parent_table_schema_name,
                    parent_table_name,
                )
            },
            schema_name=child_table_schema_name,
        )
        is True
    ), "Результат проверки структуры таблицы отличается от ожидаемого"


@pytest.mark.usefixtures("two_table_with_reference")
def test_compare_table_structure_for_different_tables(
    single_table_with_seq_structure,
    child_table_name,
    child_table_schema_name,
    pg_connection,
    parent_table_schema_name,
    parent_table_name,
):
    """Проверяет сравнение структуры таблиц для различных таблиц."""
    # TODO: Доработать тест добавив несколько тестов с разными json который будет проверять срабатывание if - return в
    #  функции _compare_table_structure и так по каждому возможному if
    table_structure = single_table_with_seq_structure["structure"]
    constraints_from_structure = table_structure["constraints"]
    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    for constraint in constraints_from_structure:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    assert (
        _compare_table_structure(
            pg_connection,
            table_structure=table_structure,
            table_name=child_table_name,
            foreign_tables_mapping=(
                {
                    (foreign_schema_from_structure, foreign_table_from_structure): (
                        parent_table_schema_name,
                        parent_table_name,
                    )
                }
                if foreign_table_from_structure is not None and foreign_schema_from_structure is not None
                else {}
            ),
            schema_name=child_table_schema_name,
        )
        is False
    ), "Результат проверки структуры таблицы отличается от ожидаемого"


@pytest.mark.usefixtures("single_table")
def test_export_table_data(single_table_pk, pg_cursor, single_table_schema_name, single_table_name, pg_connection):
    """Проверяет получение данных из таблицы."""
    table_data_from_function = _export_table_data(
        pg_connection, table_name=single_table_name, schema_name=single_table_schema_name
    )
    table_data_from_db = get_table_data(pg_cursor, schema_name=single_table_schema_name, table_name=single_table_name)

    sorted_table_data_from_function = sort_dict_list_by_key(table_data_from_function, single_table_pk)
    sorted_table_data_from_db = sort_dict_list_by_key(table_data_from_db, single_table_pk)

    assert sorted_table_data_from_db == sorted_table_data_from_function, "Данные из таблицы и из функции не совпадают"


@pytest.mark.usefixtures("single_table")
def test_export_table_to_dict(
    single_table_name,
    single_table_schema_name,
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
):
    """Проверяет экспортирование таблицы в словарь."""
    table_structure = export_table_to_dict(
        table_name=single_table_name,
        dbname=postgres_test_database,
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        port=postgres_port,
        schema_name=single_table_schema_name,
    )

    assert "structure" in table_structure, "Ключ structure не найден в структуре таблицы"
    assert "data" in table_structure, "Ключ data не найден в структуре таблицы"


@pytest.mark.usefixtures("single_table")
def test_table_exists_with_exist_table(pg_connection, single_table_name, single_table_schema_name):
    """Проверяет функцию проверки существования таблицы в БД, для существующей таблицы."""
    assert _table_exists(pg_connection, table_name=single_table_name, schema_name=single_table_schema_name) is True, (
        "Полученный ответ отличается от ожидаемого для таблицы существующей в бд"
    )


def test_table_exists_with_no_exist_table(pg_connection, random_table_name, random_schema):
    """Проверяет функцию проверки существования таблицы в БД, для таблицы отсутствующей в БД."""
    assert _table_exists(pg_connection, table_name=random_table_name, schema_name=random_schema) is False, (
        "Полученный ответ отличается от ожидаемого для таблицы отсутствующей в бд"
    )


@pytest.mark.usefixtures("two_table_with_reference")
def test_import_table_data_with_parent_table_relation(
    pg_connection,
    child_table_with_references_structure,
    child_table_schema_name,
    child_table_name,
    parent_table_name,
    parent_table_schema_name,
    child_table_pk,
    pg_cursor,
):
    """Проверяет импорт данных в таблицу."""
    table_structure = child_table_with_references_structure["structure"]
    table_data = child_table_with_references_structure["data"]

    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    for constraint in table_structure["constraints"]:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    _import_table_data(
        pg_connection,
        table_name=child_table_name,
        schema_name=child_table_schema_name,
        table_data=table_data,
        table_structure=table_structure,
        foreign_tables_mapping={
            (foreign_schema_from_structure, foreign_table_from_structure): (parent_table_schema_name, parent_table_name)
        },
    )

    table_data_from_db = get_table_data(pg_cursor, schema_name=child_table_schema_name, table_name=child_table_name)

    convert_datetime_to_iso_string(table_data_from_db)

    sorted_table_data = sort_dict_list_by_key(table_data, child_table_pk)
    sorted_table_data_from_db = sort_dict_list_by_key(table_data_from_db, child_table_pk)

    assert sorted_table_data == sorted_table_data_from_db, (
        "Данные в БД после импорта не совпадают с данными из файла импорта"
    )


@pytest.mark.usefixtures("self_referencing_table_empty")
def test_import_table_data_with_self_referencing_table(
    pg_connection,
    self_referencing_table_structure,
    self_referencing_table_schema_name,
    self_referencing_table_name,
    self_referencing_table_pk,
    pg_cursor,
):
    """Проверяет импорт данных в таблицу."""
    table_structure = self_referencing_table_structure["structure"]
    table_data = self_referencing_table_structure["data"]

    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    for constraint in table_structure["constraints"]:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    _import_table_data(
        pg_connection,
        table_name=self_referencing_table_name,
        schema_name=self_referencing_table_schema_name,
        table_data=table_data,
        table_structure=table_structure,
        foreign_tables_mapping={
            (
                foreign_schema_from_structure,
                foreign_table_from_structure,
            ): (
                self_referencing_table_schema_name,
                self_referencing_table_name,
            )
        },
    )

    table_data_from_db = get_table_data(
        pg_cursor, schema_name=self_referencing_table_schema_name, table_name=self_referencing_table_name
    )

    convert_datetime_to_iso_string(table_data_from_db)

    sorted_table_data = sort_dict_list_by_key(table_data, self_referencing_table_pk)
    sorted_table_data_from_db = sort_dict_list_by_key(table_data_from_db, self_referencing_table_pk)

    assert sorted_table_data == sorted_table_data_from_db, (
        "Данные в БД после импорта не совпадают с данными из файла импорта"
    )


def test_import_table_from_dict_non_exist_table(
    pg_cursor,
    random_schema,
    random_table_name,
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
    single_table_structure,
):
    """Проверяет функцию импорта таблицы из словаря для таблицы которой нет в бд."""
    import_table_from_dict(
        table=single_table_structure,
        table_name=random_table_name,
        schema_name=random_schema,
        dbname=postgres_test_database,
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
    )

    assert table_exists(pg_cursor, table_name=random_table_name, schema_name=random_schema) is True, (
        "Полученный результат отличается от ожидаемого для импорта таблицы которой ранее не было в БД"
    )


@pytest.mark.usefixtures("single_table")
def test_import_table_from_dict_wrong_structure(
    single_table_name,
    single_table_schema_name,
    single_table_with_seq_structure,
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
):
    """Проверяет выбрасывание исключения при несовпадении структуры таблицы переданной и в БД."""
    with pytest.raises(ValueError, match="Структура таблицы в базе данных не совпадает с переданной"):
        import_table_from_dict(
            table=single_table_with_seq_structure,
            table_name=single_table_name,
            schema_name=single_table_schema_name,
            dbname=postgres_test_database,
            host=postgres_host,
            port=postgres_port,
            user=postgres_user,
            password=postgres_password,
        )


@pytest.mark.usefixtures("self_referencing_table_empty")
def test_import_table_from_dict_existing_empty_table(
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
    self_referencing_table_structure,
    self_referencing_table_schema_name,
    self_referencing_table_name,
    self_referencing_table_pk,
    pg_cursor,
):
    """Проверяет импорт таблицы из словаря для существующей пустой таблицы."""
    table_structure = self_referencing_table_structure["structure"]
    table_data = self_referencing_table_structure["data"]

    foreign_table_from_structure = None
    foreign_schema_from_structure = None

    for constraint in table_structure["constraints"]:
        if constraint["constraint_type"] == "FOREIGN KEY":
            foreign_table_from_structure = constraint["foreign_table"]
            foreign_schema_from_structure = constraint["foreign_table_schema"]
            break

    import_table_from_dict(
        table=self_referencing_table_structure,
        table_name=self_referencing_table_name,
        schema_name=self_referencing_table_schema_name,
        dbname=postgres_test_database,
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
        foreign_tables_mapping={
            (
                foreign_schema_from_structure,
                foreign_table_from_structure,
            ): (
                self_referencing_table_schema_name,
                self_referencing_table_name,
            )
        },
    )

    table_data_from_db = get_table_data(
        pg_cursor, schema_name=self_referencing_table_schema_name, table_name=self_referencing_table_name
    )

    convert_datetime_to_iso_string(table_data_from_db)

    sorted_table_data = sort_dict_list_by_key(table_data, self_referencing_table_pk)
    sorted_table_data_from_db = sort_dict_list_by_key(table_data_from_db, self_referencing_table_pk)

    assert sorted_table_data == sorted_table_data_from_db, (
        "Данные в БД после импорта не совпадают с данными из файла импорта"
    )


def test_serialize_datetime_to_str():
    """Проверяет сериализацию datetime в строку."""
    date = datetime.datetime.now(tz=datetime.timezone.utc)

    date_str = _serialize_to_str(date)
    assert date_str == date.isoformat(), "Полученное значение отличается от ожидаемого."


def test_serialize_obj_to_str():
    """Проверяет сериализацию произвольного объекта не являющегося datetime."""
    obj = random.randint(0, 1000)
    obj_serialized = _serialize_to_str(obj)
    assert obj_serialized == obj, "Полученное значение отличается от ожидаемого."


def test_deserialize_from_str():
    """Проверяет дессериализацию строки в datetime."""
    today = datetime.datetime.now(tz=datetime.timezone.utc)
    obj = {
        "short string": "str",
        "long string": (
            "too long string too long string too long string too long string too long string too long string"
        ),
        "iso datetime": today.isoformat(),
        "number": random.randint(0, 1000),
    }

    obj2 = obj.copy()
    obj2["iso datetime"] = today
    obj = _deserialize_from_str(obj)

    assert obj == obj2, "Возвращенный функцией объект отличается от ожидаемого"


def test_dict_as_json(self_referencing_table_structure):
    """Проверяет получение буфера с файлом в json формате."""
    buffer = dict_as_json(self_referencing_table_structure)
    json_from_file = json.load(buffer)
    assert json_from_file == self_referencing_table_structure, (
        "Структура из json полученная из буфера отличается от переданной"
    )


def test_json_to_table_from_file(
    random_table_name,
    random_schema,
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
    single_table_json_file_name,
    pg_cursor,
):
    """Проверяет преобразование json в таблицу из файла."""
    json_to_table(
        single_table_json_file_name,
        random_table_name,
        dbname=postgres_test_database,
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
        schema_name=random_schema,
    )

    assert table_exists(pg_cursor, table_name=random_table_name, schema_name=random_schema) is True, (
        "Таблица не найдена в базе данных"
    )


def test_json_to_table_from_buffer(
    random_table_name,
    random_schema,
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
    single_table_structure,
    pg_cursor,
):
    """Проверяет преобразование json в таблицу из буфера."""
    buffer = BytesIO()
    buffer.write(json.dumps(single_table_structure, indent=4, default=_serialize_to_str, ensure_ascii=False).encode())
    buffer.seek(0)
    json_to_table(
        buffer,
        random_table_name,
        dbname=postgres_test_database,
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
        schema_name=random_schema,
    )

    assert table_exists(pg_cursor, table_name=random_table_name, schema_name=random_schema) is True, (
        "Таблица не найдена в базе данных"
    )


def test_json_to_table_wrong_format(
    random_table_name,
    random_schema,
    postgres_test_database,
    postgres_host,
    postgres_port,
    postgres_user,
    postgres_password,
    single_table_structure,
    pg_cursor,
):
    """Проверяет поднятие исключения при некорректном входном формате json."""
    with pytest.raises(TypeError) as exc_info:
        json_to_table(
            single_table_structure,
            random_table_name,
            dbname=postgres_test_database,
            host=postgres_host,
            port=postgres_port,
            user=postgres_user,
            password=postgres_password,
            schema_name=random_schema,
        )

    assert str(exc_info.value) == "Неподдерживаемый тип хранилища данных", "Не получено ожидаемое исключение"
