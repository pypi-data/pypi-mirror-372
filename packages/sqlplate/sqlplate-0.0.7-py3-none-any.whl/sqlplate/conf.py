# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class Config:
    etl_columns: list[str]
    scd1_soft_delete_columns: list[str]
    scd2_columns: list[str]

    def remove_sys_cols(self, columns: list[str]) -> list[str]:
        return [col for col in columns if col not in self.scd2_columns]

    def export(self, template_type: str | None = None) -> dict[str, Any]:
        template_type = template_type or "NOT_SET"
        etl_vars: dict[str, Any] = {}
        if template_type == "etl":
            etl_vars: dict[str, Any] = {
                "etl_columns": self.etl_columns,
                "scd1_soft_delete_columns": self.scd1_soft_delete_columns,
                "scd2_columns": self.scd2_columns,
                "only_main": False,
            }

        return {"only_main": False} | etl_vars


def config() -> Config:
    """Return a Config dataclass object"""

    etl_columns: list[str] = [
        os.getenv("ETL_LOAD_SRC_COL", "load_src"),
        os.getenv("ETL_LOAD_ID_COL", "load_id"),
        os.getenv("ETL_LOAD_DATE_COL", "load_date"),
        os.getenv("ETL_UPDT_LOAD_SRC_COL", "updt_load_src"),
        os.getenv("ETL_UPDT_LOAD_ID_COL", "updt_load_id"),
        os.getenv("ETL_UPDT_LOAD_DATE_COL", "updt_load_date"),
    ]

    scd1_soft_delete_columns: list[str] = [
        os.getenv("SCD1_SOFT_DELETE_COL", "delete_f")
    ] + etl_columns

    scd2_columns: list[str] = [
        os.getenv("SCD2_START_DT_COL", "start_date"),
        os.getenv("SCD2_END_DT_COL", "end_date"),
        os.getenv("SCD2_DELETE_COL", "delete_f"),
    ] + etl_columns

    return Config(
        etl_columns=etl_columns,
        scd1_soft_delete_columns=scd1_soft_delete_columns,
        scd2_columns=scd2_columns,
    )
