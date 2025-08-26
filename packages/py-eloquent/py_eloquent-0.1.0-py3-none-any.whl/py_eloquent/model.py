from .fields import Field
from .connection import execute
from .query import QueryBuilder
from .exceptions import ORMError

class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        fields = {}
        pk_name = None
        for key, val in list(attrs.items()):
            if isinstance(val, Field):
                val.name = key
                fields[key] = val
                attrs.pop(key)
                if val.primary_key:
                    pk_name = key
        attrs['_fields'] = fields
        attrs['_pk_name'] = pk_name or 'id'
        cls = super().__new__(mcs, name, bases, attrs)
        table = getattr(cls, 'Meta', None)
        return cls

class Model(metaclass=ModelMeta):
    class Meta:
        table = None

    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            setattr(self, name, kwargs.get(name, field.default))
        # allow primary key even if not declared
        if self._pk_name not in self._fields:
            setattr(self, self._pk_name, kwargs.get(self._pk_name))

    @classmethod
    def table_name(cls):
        meta = getattr(cls, 'Meta', None)
        t = getattr(meta, 'table', None)
        if t:
            return t
        return cls.__name__.lower()  # simple default

    @classmethod
    def query(cls):
        return QueryBuilder(cls)

    @classmethod
    def all(cls):
        return cls.query().get()

    @classmethod
    def find(cls, pk):
        return cls.query().where(**{cls._pk_name: pk}).first()

    @classmethod
    def where(cls, **kwargs):
        return cls.query().where(**kwargs)

    def to_dict(self):
        data = {}
        for k in self._fields:
            data[k] = getattr(self, k)
        # include pk if present
        if hasattr(self, self._pk_name):
            data[self._pk_name] = getattr(self, self._pk_name)
        return data

    @classmethod
    def _row_to_instance(cls, row):
        if row is None:
            return None
        inst = cls(**{k: row.get(k) for k in row})
        return inst

    def save(self):
        data = {k: getattr(self, k) for k in self._fields}
        pk = getattr(self, self._pk_name, None)
        if pk:
            # update
            qb = self.__class__.query().where(**{self._pk_name: pk})
            qb.update(data)
        else:
            # insert
            res = self.__class__.query().insert(data)
            # try to set pk if lastrowid available
            try:
                last = res.lastrowid
                if last:
                    setattr(self, self._pk_name, last)
            except Exception:
                pass
        return self

    def delete(self):
        pk = getattr(self, self._pk_name, None)
        if not pk:
            raise ORMError("Cannot delete without primary key set")
        return self.__class__.query().where(**{self._pk_name: pk}).delete()
