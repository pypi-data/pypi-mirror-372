import datetime
import inspect
from typing import Dict, List, Optional, Any, Type

from sqlalchemy import and_, Enum as SQLAlchemyEnumType, String, Integer, Float, Boolean, DateTime, Text, Date, \
    inspect as sa_inspect, func
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeMeta, class_mapper, ColumnProperty
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from fastpluggy.core.database import Base
from fastpluggy.core.view_builer.components import FieldHandlingView
from .base import FieldMeta
from ..tools.inspect_tools import get_module

try:
    # SQLAlchemy ≥1.0 / 2.0
    from sqlalchemy.orm.attributes import InstrumentedAttribute
except ImportError:
    InstrumentedAttribute = None  # if SQLAlchemy isn’t installed

ParamResult = str | tuple[Type, str]


class ModelToolsSQLAlchemy:
    SQLALCHEMY_FIELD_MAPPING = {
        String: "string",
        Text: "text",
        Integer: "int",
        Float: "float",
        Boolean: "bool",
        DateTime: "datetime",
        Date: "date",
        SQLAlchemyEnumType: "enum",  # Enum maps to a dropdown
    }

    @staticmethod
    def is_sqlalchemy(model_or_instance) -> bool:
        """
        Checks if the given model or instance is a SQLAlchemy declarative model.

        :param model_or_instance: The model class or instance to check.
        :return: True if it is a SQLAlchemy model or instance, False otherwise.
        """
        # If it's a class, check if it's a SQLAlchemy model class
        if isinstance(model_or_instance, type):
            return isinstance(model_or_instance, (DeclarativeMeta, DeclarativeAttributeIntercept))
        # If it's an instance, check its class
        return isinstance(type(model_or_instance), (DeclarativeMeta, DeclarativeAttributeIntercept))

    @staticmethod
    def is_sqlalchemy_model_instance(obj) -> bool:
        """
        Checks if the given object is an instance of a SQLAlchemy declarative model.
        :param obj: The object to check.
        :return: bool: True if it is a SQLAlchemy model instance, False otherwise.
        """
        return (
                hasattr(obj, "__table__")
                and hasattr(obj, "__mapper__")
                and not isinstance(obj, type)
        )

    @staticmethod
    def create_filtered_query(db, model, filters):
        query = db.query(model)
        if filters:
            if isinstance(filters, dict):
                query = query.filter(and_(
                    *[getattr(model, FieldHandlingView.get_field_name(key)) == value for key, value in filters.items()]
                ))
            elif callable(filters):
                query = query.filter(filters)
            else:
                raise ValueError("Filters must be a dictionary or a callable.")
        return query

    @staticmethod
    def model_to_dict(instance, exclude_fields: Optional[list[str | Any]] = None) -> dict[str, Any]:
        exclude_fields = FieldHandlingView.process_fields_names(exclude_fields) or []
        mapper = sa_inspect(instance.__class__)
        fields = {attr.key: getattr(instance, attr.key) for attr in mapper.attrs}
        return {key: value for key, value in fields.items() if key not in exclude_fields}

    @staticmethod
    def extract_fields(model: Type[DeclarativeMeta], exclude_fields: List[str], readonly_fields: List[str]) -> Dict[
        str, FieldMeta]:
        exclude_fields = FieldHandlingView.process_fields_names(exclude_fields) or []
        fields = {}
        mapper = class_mapper(model)
        for prop in mapper.iterate_properties:
            if isinstance(prop, ColumnProperty):
                field_name = prop.key
                if field_name in exclude_fields:
                    continue
                column = prop.columns[0]
                column_type = type(column.type)
                description = column.doc or column.comment
                default = column.default.arg if column.default else None
                if isinstance(default, func.now().__class__):
                    default =  datetime.datetime.now(datetime.UTC)

                metadata = FieldMeta(
                    type=column_type,
                    required=not column.nullable and not column.primary_key,
                    readonly=field_name in readonly_fields,
                    default=default,
                    primary_key=column.primary_key,
                    description=description,
                )
                if isinstance(column.type, SQLAlchemyEnumType):
                    metadata.enum_class = column.type.enum_class
                fields[field_name] = metadata
        return fields

    @staticmethod
    def get_model_primary_keys(model) -> List[str]:
        """
        Returns the primary key(s) of the given SQLAlchemy model.
        """
        if not ModelToolsSQLAlchemy.is_sqlalchemy(model):
            raise ValueError(f"The provided object {model} is not a valid SQLAlchemy model.")
        return [key.name for key in model.__mapper__.primary_key]

    @staticmethod
    def get_model_class(model_name: str, base=None):
        """
        Dynamically fetch the SQLAlchemy model class by its name.
        """
        if base is None:
            base = Base

        for mapper in base.registry.mappers:
            if mapper.class_.__name__ == model_name:
                return mapper.class_

        return None

    @staticmethod
    def split_param(
            param: str | InstrumentedAttribute
    ) -> (tuple[None, str] | tuple[Any, Any]):
        """
        If `param` is a plain string, return it.
        If it’s a SQLAlchemy InstrumentedAttribute (eg. User.username),
        return (ModelClass, "attr_name").
        """
        # 1) plain string → just hand it back
        if isinstance(param, str):
            return None, param

        # 2) InstrumentedAttribute → unpack
        #    (SQLAlchemy’s InstrumentedAttribute has .class_ and .key)
        if InstrumentedAttribute and isinstance(param, InstrumentedAttribute):
            model = param.class_
            field_name = param.key
            return model, field_name

        # 3) fallback if SQLAlchemy’s API changed, but attr has the two bits
        if hasattr(param, 'class_') and hasattr(param, 'key'):
            return param.class_, param.key

        raise TypeError(f"Expected a string or InstrumentedAttribute, got {type(param)}")

    @staticmethod
    def get_fk_models(
            model: DeclarativeMeta,
            field_name: str
    ) -> Optional[List[tuple[Type | None, Any, Any]]]:
        """
        If `model.field_name` is a ForeignKey column, returns
        a list of tuples containing (mapped_class, target_column, target_table)
        for each foreign key reference.
        Otherwise returns None.
        """
        # 1) ensure the attribute exists
        if not hasattr(model, field_name):
            raise AttributeError(f"{model.__name__!r} has no attribute {field_name!r}")

        # 2) pull out the InstrumentedAttribute and its Column
        attr = getattr(model, field_name)
        if not isinstance(attr, InstrumentedAttribute):
            raise TypeError(f"{field_name!r} on {model.__name__!r} is not a mapped attribute")

        col = attr.property.columns[0]
        fks = list(col.foreign_keys)
        if not fks:
            return None

        # 3) inspect registry to find any mapped class for the FK table
        registry = sa_inspect(model).mapper.registry
        results = []

        for fk in fks:
            target_col = fk.column
            target_table = target_col.table  # sqlalchemy.Table

            # try to match a mapper whose table is this FK target
            mapped_cls: Type | None = None
            for mapper in registry.mappers:
                if mapper.local_table is target_table:
                    mapped_cls = mapper.class_
                    break

            results.append((mapped_cls, target_col, target_table))

        return results

    @staticmethod
    def make_fk_selects_sa(
            model: DeclarativeMeta,
            field_name: str,
            specific_value: Any = None
    ) -> Optional[List]:
        """
        If `model.field_name` is a ForeignKey column, returns
        a list of SQLAlchemy Select statements (core or ORM) for
        each referenced table or mapped class.
        If specific_value is provided, the select statements will filter
        for rows where the target column equals the specific_value.
        Otherwise returns None.
        """
        fk_models = ModelToolsSQLAlchemy.get_fk_models(model, field_name)
        if fk_models is None:
            return None

        statements = []
        for mapped_cls, target_col, target_table in fk_models:
            if mapped_cls:
                # ORM-style select of the class
                stmt = select(mapped_cls)
                if specific_value is not None:
                    # Get the attribute corresponding to the target column
                    target_attr = getattr(mapped_cls, target_col.name, None)
                    if target_attr is not None:
                        stmt = stmt.where(target_attr == specific_value)
                statements.append(stmt)
            else:
                # Core-style select of the table
                stmt = select(target_table)
                if specific_value is not None:
                    # Filter by the target column directly
                    stmt = stmt.where(target_col == specific_value)
                statements.append(stmt)

        return statements

    @staticmethod
    def get_sqlalchemy_models(module_name: str) -> list[type]:
        module = get_module(f"{module_name}.models", reload=False)
        return [
            obj for name, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and ModelToolsSQLAlchemy.is_sqlalchemy(obj) and obj is not Base
        ]
