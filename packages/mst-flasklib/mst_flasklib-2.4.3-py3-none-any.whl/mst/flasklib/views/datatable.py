from typing import Dict, List
from flask import render_template


class DataTable:
    """The DataTable view renders a template containing a Javascript DataTable that pulls data from a JSON source.

    The default settings include buttons to reload, export to csv, export to excel, and set column visibility.

    Args:
        data_source (str): The AJAX data source that the table pulls from. Must return a JSON object of the form:
            ```json
            {"data": [
                {"first_name": "Joe", "last_name": "Miner", ... },
                ...
            ]}
            ```

        column_config (List[Dict[str, str]]): The configuration of the columns, passed directly to the DataTables columns parameter.
            Must be a list of dicts containing the properties for each column.
            At a minimum this should contain `data` and `title` corresponding to the JSON key and display name of the column.
            See https://datatables.net/reference/option/columns for valid options.
            ```json
            [
                {"data": "first_name", "title": "First Name", "width": "20px"},
                {"data": "last_name", "title": "Last Name"},
                ...
            ]
            ```

        datatable_config (Dict): Additional configuration to apply to the DataTable.

        column_defs (str): A string of raw javascript code that contains the value for the DataTables columnDefs parameter.
    """

    def __init__(
        self,
        data_source: str,
        column_config: List[Dict[str, str]],
        datatable_config: Dict = None,
        column_defs: str = None,
    ):
        self.data_source = data_source
        self.column_config = column_config
        self.column_defs = column_defs

        # Default DataTable Config
        default_datatable_config = {
            "ajax": self.data_source,
            "columns": self.column_config,
            "lengthMenu": [[10, 25, 50, 100, 500, -1], [10, 25, 50, 100, 500, "ALL"]],
            "deferRender": True,
            "pageLength": 100,
            "buttons": ["reload", "csv", "excel", "colvis"],
            "dom": "Blfrtip",
        }

        if datatable_config:
            self.datatable_config = {**default_datatable_config, **datatable_config}
        else:
            self.datatable_config = default_datatable_config

    def render_template(self, template_name="views/datatable.html", **kwargs) -> str:
        """Wrapper for Flask's render_template function to render the DataTable template.

        Args:
            template_name (str, optional): The template name to render. Defaults to "views/datatable.html".

        Returns:
            str: The rendered template as a string.
        """

        return render_template(
            template_name,
            datatable_config=self.datatable_config,
            column_defs=self.column_defs,
            **kwargs,
        )
