from typing import Any, Sequence, overload
from typing_extensions import Self


class Table:

    Column = list[str] | list[float]
    Row = list[str | float]

    def __init__(self, initial_headers: Sequence[str] = []):
        self.headers: list[str] = list(initial_headers)
        self.rows: list[Table.Row] = []

    @overload
    def add_column(self, header: str, column: list[str]) -> Self: ...

    @overload
    def add_column(self, header: str, column: list[float]) -> Self: ...

    def add_column(self, header: str, column: list[str] | list[float]) -> Self:

        if self.rows:
            # if we're not empty we just add
            for row, new_value in zip(self.rows, column, strict=True):
                row.append(new_value)  # type: ignore
        else:
            for value in column:
                self.rows.append([value])
        self.headers.append(header)

        return self

    # Union Any is me giving up because I have too much stuff to do to be stuck on thos
    def add_row(self, row: Sequence[str | float | Any]) -> Self:
        assert len(row) == len(self.headers)
        self.rows.append(row)  # type: ignore
        return self

    def add_rows(self, rows: list[Sequence[str | float | Any]]) -> Self:
        for row in rows:
            self.add_row(row)
        return self

    def __getitem__(self, key: str) -> Column:
        column_index = self.headers.index(key)
        return [row[column_index] for row in self.rows]  # type: ignore

    def __contains__(self, key: str):
        return key in self.headers

    def export(self) -> tuple[list[str], list[list[str]]]:
        return self.headers, [[str(inner) for inner in row] for row in self.rows]

    def _repr_html_(self) -> str:
        return self.to_html_table()

    def to_html_table(self):
        """
        Generates a nicely styled HTML table with CSS for better readability,
        especially for cells containing a lot of text.
        """
        # CSS styles for a professional-looking table
        # This is defined once and applied to the table via a class.
        css_style = """
<style>
    .classy-table {
        width: 100%;
        border-collapse: collapse; /* Removes space between borders */
        font-family: Arial, sans-serif; /* A clean, readable font */
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .classy-table th, .classy-table td {
        padding: 12px 15px; /* Adds space inside cells */
        border: 1px solid #ddd; /* Light grey borders */
        text-align: left;
        vertical-align: top; /* Aligns content to the top */
        /* This is key for handling long text */
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: pre-wrap;
    }
    .classy-table th {
        background-color: #f2f2f2; /* Light grey header background */
        font-weight: bold;
        color: #333;
    }
    .classy-table tr:nth-child(even) {
        background-color: #f9f9f9; /* Zebra-striping for even rows */
    }
    .classy-table tr:hover {
        background-color: #f1f1f1; /* Highlight row on hover */
    }
</style>"""
        # Create HTML table with a specific class
        html_table = "<table class='classy-table'>\n"

        # Add table header
        html_table += "  <thead>\n"  # Using <thead> for semantic HTML
        html_table += "    <tr>\n"
        for col_name in self.headers:
            # No more inline styles needed here!
            html_table += f"      <th>{col_name}</th>\n"
        html_table += "    </tr>\n"
        html_table += "  </thead>\n"

        # Add table rows
        html_table += "  <tbody>\n"  # Using <tbody> for semantic HTML
        for row in self.rows:
            html_table += "    <tr>\n"
            for value in row:
                # No more inline styles needed here either
                html_table += f"      <td>{value}</td>\n"
            html_table += "    </tr>\n"
        html_table += "  </tbody>\n"

        # Close HTML table
        html_table += "</table>"

        # Return the styles and the table together
        return css_style + html_table
