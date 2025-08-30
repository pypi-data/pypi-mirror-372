from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .constants import ControllerType

this_path = Path(__file__).parent
jinja_path = this_path / "snippets"


class PlcGenerator:
    def __init__(self, controller: ControllerType) -> None:

        if controller == ControllerType.pbrick:
            jinja_path = this_path / "snippets/power"
        else:
            jinja_path = this_path / "snippets/turbo"

        self.templateLoader = FileSystemLoader(searchpath=jinja_path)
        self.environment = Environment(
            loader=self.templateLoader,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, **args) -> str:
        template = self.environment.get_template(template_name)
        output = template.render(**args)

        return output
