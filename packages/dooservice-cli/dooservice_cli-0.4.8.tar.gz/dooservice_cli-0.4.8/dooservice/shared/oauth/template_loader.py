"""Template loader for OAuth callback server HTML templates."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class TemplateLoader:
    """Loads and renders HTML templates for OAuth callback server using Jinja2."""

    def __init__(self):
        """Initialize template loader with Jinja2 environment."""
        self.template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)), autoescape=True
        )

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Load and render an HTML template with provided variables using Jinja2.

        Args:
            template_name: Name of template file (without .html extension)
            **kwargs: Template variables to substitute

        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(f"{template_name}.html")
            return template.render(**kwargs)
        except TemplateNotFound as e:
            raise FileNotFoundError(
                f"Template {template_name}.html not found in {self.template_dir}"
            ) from e

    def render_success(self, provider_name: str = "OAuth") -> str:
        """Render success page template."""
        return self.render_template("success", provider_name=provider_name)

    def render_status(self, provider_name: str = "OAuth") -> str:
        """Render status page template."""
        return self.render_template("status", provider_name=provider_name)

    def render_error(self, error_message: str, provider_name: str = "OAuth") -> str:
        """Render error page template."""
        return self.render_template(
            "error", error_message=error_message, provider_name=provider_name
        )

    def render_404(self) -> str:
        """Render 404 page template."""
        return self.render_template("404")
