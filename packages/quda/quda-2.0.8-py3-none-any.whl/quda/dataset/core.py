# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/8/27 10:47
# Description:

from __future__ import annotations

import lidb
from functools import partial
import polars.selectors as cs
import polars as pl
from typing import Callable
import logair
import ygo

logger = logair.get_logger("quda.dataset")

def complete_data(fn, date, save_tb, partitions, **constraints):
    data = fn(date=date, **constraints)
    # 剔除以 `_` 开头的列
    data = data.filter(**constraints).select(~cs.starts_with("_"))
    if not isinstance(data, (pl.DataFrame, pl.LazyFrame)):
        logger.error("Result of dataset.fn must be polars.DataFrame or polars.LazyFrame.")
        return
    if isinstance(data, pl.LazyFrame):
        data = data.collect()
    lidb.put(data, save_tb, partitions=partitions)


class Dataset:

    def __init__(self, fn: Callable[..., pl.DataFrame], partitions: list[str], save_tb: str, **constraints):
        """

        Parameters
        ----------
        fn:
        partitions: list[str]
            分区
        save_tb: str
            数据集保存表格
        constraints: dict
            过滤条件，该过滤条件也会传递给fn
        """
        self.fn = partial(fn, **constraints)
        if partitions:
            if "date" not in partitions:
                partitions = ["date", *partitions]
        self.partitions = partitions
        self.save_tb = lidb.tb_path(save_tb)
        for k, v in constraints.items():
            self.save_tb = self.save_tb / f"{k}={v}"

        self._empty = self.is_empty()

    @property
    def hive_info(self):
        return lidb.parse_hive_partition_structure(self.save_tb)

    def is_empty(self) -> bool:
        return not any(self.save_tb.glob("*.parquet"))

    def __call__(self, *args, **kwargs):
        # self.fn =
        fn = partial(self.fn, *args, **kwargs)
        return Dataset(fn=fn, partitions=self.partitions, save_tb=self.save_tb)

    def get_value(self, date, **constraints):
        if not self._empty:
            lf = lidb.scan(self.save_tb).filter(**constraints)
            data = lf.collect()
            if not data.is_empty():
                return data
        complete_data(self.fn, date, self.save_tb, partitions=self.partitions, **constraints)
        # 剔除以 `_` 开头的列
        self._empty = False

        return lidb.scan(self.save_tb).filter(**constraints).collect()

    def get_history(self, dateList: list[str], **constraints):
        missing_dates = []
        if self._empty:
            # 需要补全全部数据
            missing_dates = dateList
        else:
            exist_dates = self.hive_info["date"].to_list()
            missing_dates = set(dateList).difference(set(exist_dates))
            missing_dates = sorted(list(missing_dates))
        if missing_dates:
            with ygo.pool() as go:
                for date in missing_dates:
                    go.submit(complete_data, job_name="complete data")(date=date, **constraints)
                go.do()
        data = lidb.scan(self.save_tb).filter(pl.col("date").is_in(dateList), **constraints)
        return data.sort("date").collect()

