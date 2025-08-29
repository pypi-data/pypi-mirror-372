"""Template engine for SQL generation using Jinja2."""

from jinja2 import Environment, DictLoader  # type: ignore


class SQLTemplateEngine:
    """SQL template engine using Jinja2."""

    def __init__(self):
        self.templates = {}
        self.env = None
        self._setup_environment()

    def _setup_environment(self):
        """Set up Jinja2 environment with custom filters."""
        self.env = Environment(
            loader=DictLoader(self.templates),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False
        )

        # Add custom filters
        self.env.filters['join_columns'] = self._join_columns_filter
        self.env.filters['escape_identifier'] = self._escape_identifier_filter
        self.env.filters['escape_string'] = self._escape_string_filter

    def _join_columns_filter(self, columns, separator=', '):
        """Join column names with backticks."""
        return separator.join(f'`{col}`' for col in columns)

    def _escape_identifier_filter(self, identifier):
        """Escape SQL identifier with backticks."""
        return f'`{identifier}`'

    def _escape_string_filter(self, value):
        """Escape SQL string value."""
        if value is None:
            return 'NULL'
        return f"'{str(value).replace(chr(39), chr(39) + chr(39))}'"

    def add_template(self, name: str, template_content: str):
        """Add a template to the engine."""
        self.templates[name] = template_content
        self.env = Environment(
            loader=DictLoader(self.templates),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False
        )
        self.env.filters['join_columns'] = self._join_columns_filter
        self.env.filters['escape_identifier'] = self._escape_identifier_filter
        self.env.filters['escape_string'] = self._escape_string_filter

    def render(self, template_name: str, **kwargs) -> str:
        """Render a template with the given context."""
        template = self.env.get_template(template_name)
        return template.render(**kwargs)


# Global template engine instance
template_engine = SQLTemplateEngine()
