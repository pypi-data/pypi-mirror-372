"""
TableModelWidget for displaying SQLAlchemy models in a table.
This is the widget version of TableModelView.
"""
from typing import Optional, Union, Callable, Any, Dict, List

from sqlalchemy import and_
from sqlalchemy.orm import Session, DeclarativeMeta as ModelBase
from starlette.datastructures import MultiDict
from wtforms.form import Form

from fastpluggy.core.models_tools.shared import ModelToolsShared
from fastpluggy.core.models_tools.sqlalchemy import ModelToolsSQLAlchemy
from fastpluggy.core.view_builer.components.pagination import Pagination
from fastpluggy.core.widgets.categories.data.table import TableWidget
from fastpluggy.core.widgets.categories.input.button import BaseButtonWidget


class TableModelWidget(TableWidget):
    db: Session

    widget_type = "tablemodel"
    category = "data"

    def __init__(
            self,
            model: ModelBase,
            filters: Optional[Union[Callable[[Any], Any], Dict[str, Any]]] = None,
            default_sort: Optional[Dict[str, str]] = None,
            limits: int = 100,
            db: Session = None,
            pagination_options: Optional[Dict[str, Any]] = None,
            links: Optional[List[Union[BaseButtonWidget, Dict[str, Any]]]] = None,
            **kwargs
    ):
        self.model = model
        self.filters = filters
        self.default_sort = default_sort
        self.links = links
        self.limits = limits
        self.pagination_options = pagination_options or {}
        self.db = db

        if 'data' in kwargs:
            del kwargs['data']

        # Call the parent class constructor
        super().__init__(
            data=[],  # `data` will be fetched dynamically in `process()`
            links=self.links,
            **kwargs
        )

        # Initialize search params
        self.search_params = {}


    def apply_filters_from_query(self, query, model, query_params, search_params):
        """
        Apply filters from query parameters to a SQLAlchemy query.

        Args:
            query (Query): The SQLAlchemy query to modify.
            model (Base): The SQLAlchemy model class.
            query_params (dict): Query parameters from the request (e.g., request.query_params).
            search_params (dict): A dictionary defining the fields and their types for filtering.

        Returns:
            Query: The modified query with filters applied.
        """
        filter_conditions = []

        for field, config in search_params.items():
            filter_value = query_params.get(field)
            if filter_value and 'filter_type' in config:
                # Handle different field types based on the `config`
                if config['filter_type'] == 'partial':
                    # Add a LIKE filter
                    filter_conditions.append(getattr(model, field).like(f"%{filter_value}%"))
                elif config['filter_type'] == 'exact':
                    filter_conditions.append(getattr(model, field) == filter_value)

        # Apply filters to the query
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        return query

    def _build_search_params_form(self):
        """
        Build a WTForms-based search form for the fields you want to filter on.
        This replaces the old dictionary-based approach.
        """
        # Import FormBuilder here to avoid circular imports
        from fastpluggy.core.view_builder import FormBuilder

        search_params = {}
        attributes = {}

        # 1) Fetch metadata for ALL fields in the model.
        fields_metadata = ModelToolsShared.get_model_metadata(
            model=self.model,
            exclude_fields=self.exclude_fields
        )

        # 3) Build `field_render_kw` so each field can have placeholders
        #    or any other custom attributes.
        field_render_kw = {}
        for field_name in fields_metadata:
            # Decide how to display the placeholder or other attributes
            field_type = fields_metadata[field_name].get("type", "string").lower()
            filter_type = "partial" if field_type == "string" else "exact"
            # For instance, partial vs. exact
            if field_type == 'bool':
                fields_metadata[field_name]['type'] = 'enum'
                fields_metadata[field_name]['choices'] = [("", 'None'), ("True", 'yes'), ("False", 'no')]

            field_render_kw[field_name] = {
                "placeholder": f"Search by {field_name.replace('_', ' ')} ({filter_type})",
                "class": "form-control",
            }
            fields_metadata[field_name].update({
                "readonly": False,
                "required": False,
                "primary_key": False,
            })
            field = FormBuilder.create_field(
                field_name=field_name,
                metadata=fields_metadata[field_name],
                widget=None,
                render_kw=field_render_kw[field_name]
            )
            search_params[field_name] = {
                "type": field_type,
                "filter_type": filter_type,  # Default filter type
                "widget": field.field_class,
            }
            attributes[field_name] = field

        # # 6) Dynamically create a form class with these attributes
        # #    so that we can instantiate it with user input.
        FilterForm = type("FilterForm", (Form,), attributes)

        # # 7) Grab query params from the request (assuming GET-based filtering)
        search_filter = dict(self.request.query_params) if self.request else {}

        # # 8) Instantiate the form with the user-provided search data
        self.search_form = FilterForm(formdata=MultiDict(search_filter))
        return search_params


    def process(self, **kwargs) -> None:
        """
        Dynamically process the view with additional parameters like db and request.
        Converts SQLAlchemy model instances into dictionaries before passing to TableView.
        """
        self.data = self._preprocess_data(self.data)  # Data should already be a list of dictionaries

        # Ensure fields and headers are set up
        self.exclude_fields = self.process_fields_names(self.exclude_fields or [])

        self._process_fields_and_headers()

        # Build search params for filters
        self.search_params = self._build_search_params_form()

        query = ModelToolsSQLAlchemy.create_filtered_query(
            db=self.db, model=self.model, filters=self.filters
        )

        # Apply dynamic filters from query parameters
        if self.request:
            query = self.apply_filters_from_query(
                query=query,
                model=self.model,
                query_params=dict(self.request.query_params),
                search_params=self.search_params,
            )

        # Handle sorting
        query = self.apply_sort_on_query(query)

        # Initialize Pagination
        self.pagination = Pagination(
            request=self.request,
            query=query,
            default_rows_per_page=self.limits,
            **self.pagination_options
        )
        self.pagination.calculate_pagination()

        # Fetch data and transform into dictionaries
        self.data = [
            item
            for item in query.offset(self.pagination.offset).limit(self.pagination.rows_per_page).all()
        ]

        # Call parent process with transformed data
        super().process(**kwargs)

    def apply_sort_on_query(self, query):
        sort_by = self.get_query_param("sort_by", default=None, param_type=str)
        sort_order = self.get_query_param("sort_order", default="asc", param_type=str)

        if sort_by and hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            query = query.order_by(column.desc() if sort_order.lower() == "desc" else column.asc())
        elif self.default_sort:
            default_sort_by = self.default_sort.get("column")
            default_sort_order = self.default_sort.get("order", "asc")
            if default_sort_by and hasattr(self.model, default_sort_by):
                column = getattr(self.model, default_sort_by)
                query = query.order_by(column.desc() if default_sort_order.lower() == "desc" else column.asc())
        return query
