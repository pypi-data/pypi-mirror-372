# -*- coding: UTF-8 -*-

from agi_tools.tools import get_config, get_date_time
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql import DataFrame
from pyspark.sql.session import SparkSession
from datetime import datetime, timedelta
from typing import Optional


class AgiTools:


    def __init__(
        self,
        private: bool = True,
        generate_log: bool = True,
        generate_metrics: bool = False
    ):
        self.generate_log = generate_log
        self.generate_metrics = generate_metrics
        self.private = private
        self.start_process = get_date_time()
        self.full_config = get_config('config')
        self.spark_settings = self.full_config.get('spark_settings', {})
        self.process_settings = self.full_config.get('datalake_settings', {})
        self.metrics = self.process_settings.get('metrics', {})
        self.start_insert_lake = None
        self.session_name = None


    def create_spark_session(self, session_name: str) -> SparkSession:
        self.session_name = session_name.lower()

        self.spark = (
            SparkSession.builder
            .appName(self.session_name)
            .master("yarn")
            .enableHiveSupport()
            .getOrCreate()
        )

        self.sc = SparkContext.getOrCreate()
        
        for key in self.spark_settings.keys():
            self.spark.conf.set(key, self.spark_settings.get(key))

        self.spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
        
        return self.spark


    def destroy_spark_session(self) -> None:
        self.end_process = get_date_time()
        
        if self.generate_log:
            self.__insert_check_point()
        
        self.spark.stop()


    def __insert_data(
            self,
            data: DataFrame,
            table_name: str,
            private: bool = True,
            write_mode: str = 'overwrite',
            partition_by: Optional[str] = None,
            num_partitions: Optional[int] = None,
            make_copy: bool = False
        ) -> None:

        if not data.rdd.isEmpty():

            if private:
                settings = self.process_settings.get('private', {})
            else:
                settings = self.process_settings.get('public', {})

            table_path = f"{settings.get('path')}/{table_name}"
            table_name = f"{settings.get('table')}.{table_name}"

            table_repair_steps = [
                f"DROP TABLE IF EXISTS {table_name}",
                f"CREATE TABLE {table_name} USING PARQUET LOCATION '{table_path}'"
            ]

            if num_partitions:
                data = data.repartition(num_partitions)

            if not make_copy:
                data = data.dropDuplicates()

            if partition_by:
                table_repair_steps.append(f"MSCK REPAIR TABLE {table_name}")
                (
                    data
                    .write
                    .mode(write_mode)
                    .partitionBy(partition_by)
                    .parquet(table_path)
                )
            else:
                (
                    data
                    .write
                    .mode(write_mode)
                    .parquet(table_path)
                )

            for step in table_repair_steps:
                self.spark.sql(step)


    def insert_into_lake(
            self,
            data: DataFrame,
            table_name: Optional[str] = None,
            write_mode: str = 'overwrite',
            partition_by: Optional[str] = None,
            num_partitions: Optional[int] = None,
            make_copy: bool = False
        ) -> None:

        if not table_name:
            table_name = self.session_name
        else:
            table_name = table_name.lower()
        
        if not data.rdd.isEmpty():
            self.data = data.select([F.col(c).alias(c.lower()) for c in data.columns])
            self.start_insert_lake = get_date_time()

            self.__insert_data(
                data,
                table_name,
                self.private,
                write_mode,
                partition_by,
                num_partitions,
                make_copy
            )

            self.end_insert_lake = get_date_time()

            if self.generate_metrics:
                self.__insert_metrics()


    def __get_process_rules(self) -> dict:
        processes = self.metrics.get('processes', [])
        for process in processes:
            if self.session_name in process['process_name']:
                rules = self.metrics.get(process['process_rules'], {})
                break
        else:
            rules: dict = {}
        return rules


    def __insert_metrics(self):
        
        rules = self.__get_process_rules()
        if rules:
            agg_expr: list = []
            agg_expr.append(F.lit(self.session_name).alias('nm_tabela'))
            agg_expr.append(F.lit(False).alias('fl_atualizada'))
            agg_expr.append(F.max('date_partition').alias('dt_partition_tabela'))

            for item in rules.get('metrics', []):
                metric = item['metric']
                name = item['name']
                alias = item['alias']

                if metric == 'countDistinct':
                    agg_expr.append(F.countDistinct(name).alias(alias))
                elif metric == 'count':
                    agg_expr.append(F.count(name).alias(alias))
                elif metric == 'max':
                    agg_expr.append(F.max(name).alias(alias))
                elif metric == 'min':
                    agg_expr.append(F.min(name).alias(alias))
                elif metric == 'sum':
                    agg_expr.append(F.sum(name).alias(alias))
                elif metric == 'avg':
                    agg_expr.append(F.avg(name).alias(alias))

            agg_expr.append(
                F.date_format(
                    F.from_utc_timestamp(F.current_timestamp(), "America/Sao_Paulo"),
                    'HH:mm:ss'
                )
                .alias('hr_ultima_execucao')
            )
            agg_expr.append(F.current_date().alias('date_partition'))

            df = self.data.agg(*agg_expr)
            
            df = (
                df
                .withColumn(
                    'fl_atualizada',
                    F.when(df.dt_partition_tabela == F.current_date(), True)
                    .otherwise(False)
                )
            )
            
            self.__insert_data(
                data=df,
                table_name=rules.get('table_name', ''),
                private=rules.get('private', True),
                write_mode='append',
                partition_by='date_partition'
            )


    def __insert_check_point(self) -> None:
        log_register = self.process_settings.get('log', {})
        table_name = log_register.get('table_name')
        
        if self.start_insert_lake:
            data = (
                self.spark
                .createDataFrame(
                    [
                        (
                            self.session_name,
                            self.start_process,
                            self.start_insert_lake,
                            self.end_insert_lake,
                            self.end_process,
                            (self.end_insert_lake - self.start_insert_lake) // timedelta(seconds = 1),
                            (self.end_process - self.start_process) // timedelta(seconds = 1),
                            datetime.now().date()
                        )
                    ],
                    schema=[
                        'process_name',
                        'start_process',
                        'start_lake',
                        'end_lake',
                        'end_process',
                        'runtime_lake',
                        'runtime_process',
                        'execution_date'
                    ]
                )
                .withColumns(
                    {
                        'start_process': F.date_format(
                            F.from_utc_timestamp('start_process', "America/Sao_Paulo"),
                            'HH:mm:ss'
                        ),
                        'start_lake': F.date_format(
                            F.from_utc_timestamp('start_lake', 'America/Sao_Paulo'),
                            'HH:mm:ss'
                        ),
                        'end_lake': F.date_format(
                            F.from_utc_timestamp('end_lake', 'America/Sao_Paulo'),
                            'HH:mm:ss'
                        ),
                        'end_process': F.date_format(
                            F.from_utc_timestamp('end_process', 'America/Sao_Paulo'),
                            'HH:mm:ss'
                        ),
                    }
                )
            )

            self.__insert_data(
                data,
                table_name,
                write_mode = 'append',
                partition_by = 'execution_date'
            )
