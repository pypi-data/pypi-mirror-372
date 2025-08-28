# -*- coding: UTF-8 -*-

import pytz
import tomli
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from typing import Any, Union, Optional


def get_config(file_name: str, config_name: Optional[str] = None) -> Union[Any, dict[str, dict]]:

    with open(f'{file_name}.toml', "rb") as f:
            config = tomli.load(f)

    if config_name is not None:
        return config.get(config_name, {})
    else:
        return config


def get_date_time() -> datetime:
    return (
        datetime
        .now(timezone.utc)
        .astimezone(
            pytz.timezone("America/Sao_Paulo")
        )
    )


def is_first_day_of_month() -> bool:
    today = date.today()
    return today.day == 1


def get_param() -> tuple[date, date, date, date]:
    TODAY = date.today()
    return (
        (TODAY - relativedelta(months=1)).replace(day=1),
        TODAY.replace(day=1),
        (TODAY + relativedelta(months=1)).replace(day=1),
        (TODAY.replace(day=1) + relativedelta(months=1) - relativedelta(days=1))
    )


def convert_decimal_columns(df: DataFrame, columns_to_cast: dict[str, str]) -> DataFrame:
    for col_name, col_type in columns_to_cast.items():
        df = (
            df
            .withColumn(
                col_name,
                F.regexp_replace(F.col(col_name), ',', '.').cast(col_type)
            )
        )
    return df
