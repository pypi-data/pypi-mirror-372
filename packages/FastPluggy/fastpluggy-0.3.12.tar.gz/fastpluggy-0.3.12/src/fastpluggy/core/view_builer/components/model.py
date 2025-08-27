from typing import Callable, Union
from typing import Type, Dict, Any, List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session, InstrumentedAttribute

from fastpluggy.core.models_tools.pydantic import ModelToolsPydantic
from fastpluggy.core.models_tools.shared import ModelToolsShared
from fastpluggy.core.models_tools.sqlalchemy import ModelToolsSQLAlchemy
from fastpluggy.core.view_builer.components import FieldHandlingView
from fastpluggy.core.widgets import AbstractWidget


class ModelView(AbstractWidget, FieldHandlingView):
    """
    A component to render a detailed view of a SQLAlchemy or Pydantic model instance.
    """
    widget_type = "model_view"

    template_name = "widgets/data/view_model.html.j2"
    macro_name = "render_model_view"
    render_method = "macro"

    def __init__(
            self,
            model: Union[BaseModel, Type[BaseModel], Any, Type[Any]],
            filters: Optional[Union[Callable[[Any], Any], Dict[str, Any]]] = None,
            fields: Optional[List[str]] = None,
            exclude_fields: Optional[List[str|InstrumentedAttribute]] = None,
            field_callbacks: Optional[Dict[str|InstrumentedAttribute, Callable[[Any], Any]]] = None,
            readonly_fields: Optional[List[str]] = None,
            title: Optional[str] = None,
            db: Optional[Session] = None,
            **kwargs
    ):
        """
        Initialize the ModelView component.

        Args:
            model: The model instance or class to render.
            filters: Filters to apply when querying the database (if model is a class).
            fields: List of fields to include. Defaults to None (include all).
            exclude_fields: List of fields to exclude. Defaults to None.
            field_callbacks: Field-specific callback functions. Defaults to None.
            readonly_fields: List of fields to render as read-only. Defaults to None.
            title: Title of the model view. Defaults to None.
            db: SQLAlchemy database session. Required if querying a SQLAlchemy model class.
            **kwargs: Additional parameters for the view.
        """
        super().__init__(**kwargs)

        self.model = model  # Can be a model instance or a model class
        self.filters = filters
        self.fields = fields
        self.exclude_fields = self.process_fields_names(exclude_fields or [])
        self.field_callbacks = self.process_field_callbacks(field_callbacks or {})
        self.readonly_fields = readonly_fields or []
        self.title = title
        self.params = kwargs
        self.db = db
        self.data = {}  # Will hold the extracted data


        #self.header_links.append(
        #    LinkHelper.get_crud_link(model=self.model, label="fa-solid fa-plus", action="create")
        #)

    def process(self, **kwargs) -> None:
        """
        Process the model data by extracting data from the provided instance or querying the database.

        Args:
            **kwargs: Additional parameters to process.
        """

        instance = None
        if self.model:
            if ModelToolsPydantic.is_model_instance(self.model):
                # Model is a Pydantic model instance
                instance = self.model
            elif ModelToolsPydantic.is_model_class(self.model):
                # Model is a Pydantic model class
                instance = self.model(**(self.filters or {}))
            elif ModelToolsPydantic.is_settings_instance(self.model):
                # Model is a BaseSettings instance
                instance = self.model
            elif ModelToolsPydantic.is_settings_class(self.model):
                # Model is a BaseSettings class
                instance = self.model(**(self.filters or {}))
            elif ModelToolsSQLAlchemy.is_sqlalchemy_model_instance(self.model):
                # Model is a SQLAlchemy model instance
                instance = self.model
            elif ModelToolsSQLAlchemy.is_sqlalchemy(self.model):
                # Model is a SQLAlchemy model class
                if not self.db:
                    raise ValueError("Database session is required to query the SQLAlchemy model.")
                # Create the query
                query = ModelToolsSQLAlchemy.create_filtered_query(
                    db=self.db, model=self.model, filters=self.filters
                )
                # Fetch the instance
                instance = query.first()
                if not instance:
                    raise ValueError("No data found for the given filters.")

            elif type(self.model) is dict:
                instance = self.model
            # else:
            #    raise ValueError("Model must be a SQLAlchemy or Pydantic model instance or class.")

            # todo: may need to refactor
            # Extract data from the instance
            self.data = ModelToolsShared.extract_model_data(instance, fields=self.fields, exclude=self.exclude_fields)

        # Apply field callbacks
        for field, callback in self.field_callbacks.items():
            if field in self.data:
                self.data[field] = callback(self.data[field])


