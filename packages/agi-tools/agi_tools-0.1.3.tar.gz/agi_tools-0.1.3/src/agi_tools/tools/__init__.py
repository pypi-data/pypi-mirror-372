# -*- coding: UTF-8 -*-

import pytz
import tomli
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from typing import Optional



def get_config(file_name: str, config_name: Optional[str] = None) -> dict:
    """Carrega um arquivo de configuração TOML.

    Args:
        file_name (str): Nome do arquivo de configuração (sem extensão).
        config_name (Optional[str]): Se informado, retorna apenas a seção especificada.

    Returns:
        dict: Dicionário de configuração.
    """
    with open(f'{file_name}.toml', "rb") as f:
        config = tomli.load(f)
    if config_name is not None:
        return config.get(config_name, {})
    else:
        return config



def get_date_time() -> datetime:
    """Obtém o horário atual em America/Sao_Paulo.

    Returns:
        datetime: Data e hora atual com timezone Brasil.
    """
    return (
        datetime
        .now(timezone.utc)
        .astimezone(
            pytz.timezone("America/Sao_Paulo")
        )
    )



def is_first_day_of_month() -> bool:
    """Verifica se hoje é o primeiro dia do mês.

    Returns:
        bool: True se for o primeiro dia do mês, False caso contrário.
    """
    today = date.today()
    return today.day == 1



def get_param() -> tuple[date, date, date, date]:
    """Retorna datas úteis para particionamento mensal.

    Returns:
        tuple[date, date, date, date]:
            - Primeiro dia do mês anterior
            - Primeiro dia do mês atual
            - Primeiro dia do próximo mês
            - Último dia do mês atual
    """
    TODAY = date.today()
    return (
        (TODAY - relativedelta(months=1)).replace(day=1),
        TODAY.replace(day=1),
        (TODAY + relativedelta(months=1)).replace(day=1),
        (TODAY.replace(day=1) + relativedelta(months=1) - relativedelta(days=1))
    )



def convert_decimal_columns(df: DataFrame, columns_to_cast: dict[str, str]) -> DataFrame:
    """Converte colunas decimais de string para tipo numérico.

    Args:
        df (DataFrame): DataFrame do Spark.
        columns_to_cast (dict[str, str]): Dicionário {coluna: tipo} para conversão.

    Returns:
        DataFrame: DataFrame com colunas convertidas.
    """
    for col_name, col_type in columns_to_cast.items():
        df = (
            df
            .withColumn(
                col_name,
                F.regexp_replace(F.col(col_name), ',', '.').cast(col_type)
            )
        )
    return df
