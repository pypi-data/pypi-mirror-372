# -*- coding: UTF-8 -*-

import json
from agi_tools.tools import get_date_time, get_config
from pyspark.sql import functions as F
from pyspark.sql import DataFrame, Row
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, DateType
from pyspark.sql.session import SparkSession


def check_table_schema(spark: SparkSession, database_name: str, table_name: str, columns: list[str] = []) -> tuple[bool, list[Row]]:
    if historical_table_schema := __get_historical_table_schema(spark, table_name):
        current_table_schema = __get_current_table_schema(spark, database_name, table_name)
        if len(columns) > 0:
            historical_table_schema = [i for i in historical_table_schema if i[0].lower() in columns]
            current_table_schema = [i for i in current_table_schema if i[0].lower() in columns]
        
        if current_table_schema == historical_table_schema:
            return (True, [])
        else:
            return (False, __check_different_schema(current_table_schema, historical_table_schema))
    else:
        return (False, [])


def __check_different_schema(schema1, schema2) -> list[Row]:
    fields1 = {field.name: field.dataType for field in schema1.fields}
    fields2 = {field.name: field.dataType for field in schema2.fields}

    different_fields = []
    common_fields = set(fields1.keys()) & set(fields2.keys())

    for field in common_fields:
        if fields1[field] != fields2[field]:
            different_fields.append(
                Row(
                    Coluna=field,
                    Origem=fields1[field],
                    Destino=fields2[field]
                )
            )

    return different_fields


def __get_current_table_schema(spark: SparkSession, database_name: str, table_name: str) -> list[Row]:
    query = f"DESCRIBE FORMATTED {database_name}.{table_name}"
    descriptions = spark.sql(query).collect()
    current_table_schema = []
    
    for description in descriptions:
        if description.col_name and description.data_type:
            if description.col_name.startswith('#'):
                break
            current_table_schema.append(
                Row(
                    coluna=description.col_name,
                    tipo=description.data_type
                )
            )
    return current_table_schema


def __get_historical_table_schema(spark: SparkSession, table_name: str) -> list[Row]:
    semaphore_config = get_config('semaphore', 'semaphores')
    historical_table = semaphore_config.get('historical_table', '')

    if isinstance(historical_table, str):
        schema = spark.sql(historical_table % (table_name)).collect()
        if schema:
            return schema[0][0]
        else:
            return []
    else:
        return []


def put_historical_table_schema(spark: SparkSession, database_name: str, table_name: str) -> DataFrame:
    df =  (
        spark
        .createDataFrame(
            [
                Row(
                    table_name=table_name,
                    schema=__get_current_table_schema(spark, database_name, table_name)
                )
            ]
        )
        .withColumn(
            'last_update',
            F.from_utc_timestamp(F.current_timestamp(), "America/Sao_Paulo")
        )
        .select(['table_name', 'last_update', 'schema'])
    )
    return df


def __put_semaphore_to_parquet(spark: SparkSession, semaphore_data: dict, semaphore_path: str) -> dict:
    schema = StructType(
        [
            StructField('semaphore', StringType()),
            StructField('success', BooleanType()),
            StructField('execution_time', DateType())
        ]
    )

    try:
        df = spark.createDataFrame([Row(**semaphore_data)], schema=schema)
        df.write.mode("overwrite").parquet(semaphore_path)
    except Exception as e:
        return {'error': str(e)}
    return {'success': True}


def put_semaphore(spark: SparkSession, name: str) -> tuple[bool, list[DataFrame], dict]:
    semaphore_config = get_config('semaphore', 'semaphores')
    semaphore_path = f"{semaphore_config.get('path')}/semaphore_{name}.parquet"
    semaphores = semaphore_config.get(name, {})
    tables = semaphores.keys()

    status = True
    dfs = []

    for table in tables:
        flag, change = check_table_schema(
            spark,
            semaphores.get(table, {}).get('database'),
            semaphores.get(table, {}).get('table'),
            semaphores.get(table, {}).get('columns', [])
        )

        status = status and flag

        dfs.append(
            spark
            .createDataFrame(
                [
                    Row(
                        table_name=table,
                        fl_semaphore=flag,
                        ds_semaphore='green' if flag else 'red',
                        change=json.dumps([row.asDict() for row in ([] if flag else change)])
                    )
                ]
            )
            .withColumn(
                'last_update',
                F.from_utc_timestamp(F.current_timestamp(), "America/Sao_Paulo")
            )
            .select(['table_name', 'last_update', 'fl_semaphore', 'ds_semaphore', 'change'])
        )

    semaphore_data = {
        "semaphore": name,
        "success": status,
        "execution_time": get_date_time()
    }

    result = __put_semaphore_to_parquet(spark, semaphore_data, semaphore_path)

    if result.get('success', False):
        return (True, dfs, result)
    else:
        return (False, dfs, result)


def __get_semaphore_from_parquet(spark: SparkSession, semaphore_path: str) -> dict:
    try:
        df = spark.read.parquet(semaphore_path)
        return df.collect()[0].asDict()
    except Exception as e:
        return {'error': str(e)}


def get_semaphore(spark: SparkSession, name: str) -> dict:
    semaphores = get_config('semaphore', 'semaphores')
    semaphore_path = f"{semaphores.get('path')}/semaphore_{name}.parquet"
    return __get_semaphore_from_parquet(spark, semaphore_path)
