import typing
import datetime
from uuid import UUID

import sqlalchemy
import sqlalchemy.dialects.postgresql

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime, String


class utcnow(expression.FunctionElement):
    type = DateTime()


class uuid(expression.FunctionElement):
    type = String()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


def compile_query(
    query: typing.Union[
        sqlalchemy.sql.Select,
        sqlalchemy.sql.Update,
        sqlalchemy.sql.Insert,
        sqlalchemy.sql.Delete,
    ],
) -> str:
    return query.compile(
        compile_kwargs=dict(
            literal_binds=True,
        ),
        dialect=sqlalchemy.dialects.postgresql.dialect(),
    ).string

class UUIDAwareJSONB(sqlalchemy.TypeDecorator):
    impl = sqlalchemy.dialects.postgresql.JSONB
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Convert Python objects to JSON-serializable format before insertion"""
        if value is not None:
            return self._convert_to_serializable(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Convert JSON back to Python objects after reading from database"""
        if value is not None:
            return self._convert_from_serialized(value)
        return value
    
    def _convert_to_serializable(self, obj):
        """Recursively convert non-serializable types to serializable formats"""
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._convert_to_serializable(obj.__dict__)
        return obj
    
    def _convert_from_serialized(self, obj):
        """Recursively convert serialized formats back to Python objects"""
        if isinstance(obj, dict):
            return {k: self._convert_from_serialized(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_from_serialized(item) for item in obj]
        elif isinstance(obj, str):
            # Try to detect and convert UUID strings
            return self._try_convert_uuid(obj)
        return obj
    
    def _try_convert_uuid(self, value):
        """Attempt to convert string to UUID if it matches UUID pattern"""
        if isinstance(value, str) and len(value) == 36:
            try:
                return UUID(value)
            except (ValueError, AttributeError):
                pass
        return value