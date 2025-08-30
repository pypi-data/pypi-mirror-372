from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class Template:
    """
    A dataclass for holding details of a jinja template to render into the PLC code.

    As the Plc object is being evaluated a list of these is build up. It is then used
    at render time to insert snippets with arguments into the rendered code.

    May also represent a callback function to be called from the root plc.pmc.jinja.

    Args:
        jinja_file (str): the prefix of the jinja template file name
        args (Dict[str, Any]): arguments to pass to the template if jinja file
            is not None, or to pass to the function if function is not None
        function: (Callable): if not None then this is a callback function to call
            instead of inserting a jinja template snippet
        custom_text: str = ""
    """

    jinja_file: Optional[str]
    args: Dict[str, Any]
    function: Optional[Callable]
    custom_text: str = ""
