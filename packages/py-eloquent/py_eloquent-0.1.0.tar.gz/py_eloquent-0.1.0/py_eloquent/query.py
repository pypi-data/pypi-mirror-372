from typing import Any, Dict, List, Optional, Sequence
from .connection import execute, executemany
from .model import Model
from .exceptions import ORMError

class QueryBuilder:
    def __init__(self, model: Model):
        self.model = model
        self._table = model.table_name()
        self._wheres: List[str] = []
        self._params: List[Any] = []
        self._limit: Optional[int] = None
        self._order: Optional[str] = None

    def where(self, **kwargs):
        for k, v in kwargs.items():
            self._wheres.append(f"`{k}` = %s")
            self._params.append(v)
        return self

    def order_by(self, clause: str):
        self._order = clause
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def _build_where(self):
        if not self._wheres:
            return "", []
        return " WHERE " + " AND ".join(self._wheres), list(self._params)

    def get(self) -> List[Model]:
        where_sql, params = self._build_where()
        sql = f"SELECT * FROM `{self._table}`{where_sql}"
        if self._order:
            sql += f" ORDER BY {self._order}"
        if self._limit:
            sql += f" LIMIT {self._limit}"
        cur = execute(sql, params, commit=False)
        rows = cur.fetchall()
        return [self.model._row_to_instance(r) for r in rows]

    def first(self) -> Optional[Model]:
        self.limit(1)
        res = self.get()
        return res[0] if res else None

    def insert(self, data: Dict[str, Any]):
        if not data:
            raise ORMError("No data to insert")
        cols = ", ".join(f"`{k}`" for k in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO `{self._table}` ({cols}) VALUES ({placeholders})"
        params = list(data.values())
        cur = execute(sql, params, commit=True)
        return cur

    def insert_many(self, rows: Sequence[Dict[str, Any]]):
        if not rows:
            raise ORMError("No rows to insert")
        cols = list(rows[0].keys())
        cols_sql = ", ".join(f"`{c}`" for c in cols)
        placeholders = "(" + ", ".join(["%s"] * len(cols)) + ")"
        sql = f"INSERT INTO `{self._table}` ({cols_sql}) VALUES {placeholders}"
        seq = [tuple(r[c] for c in cols) for r in rows]
        cur = executemany(sql, seq, commit=True)
        return cur

    def update(self, values: Dict[str, Any]):
        if not values:
            raise ORMError("No values to update")
        set_sql = ", ".join(f"`{k}` = %s" for k in values.keys())
        where_sql, where_params = self._build_where()
        if not where_sql:
            raise ORMError("Update on whole table is not allowed without where")
        sql = f"UPDATE `{self._table}` SET {set_sql}{where_sql}"
        params = list(values.values()) + where_params
        cur = execute(sql, params, commit=True)
        return cur

    def delete(self):
        where_sql, where_params = self._build_where()
        if not where_sql:
            raise ORMError("Delete on whole table is not allowed without where")
        sql = f"DELETE FROM `{self._table}`{where_sql}"
        cur = execute(sql, where_params, commit=True)
        return cur
