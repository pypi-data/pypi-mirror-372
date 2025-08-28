from IPython.display import display_markdown as display_markdown
from _typeshed import Incomplete
from solas_shared._ui._html import Html as Html

class Logo:
    HTML: Incomplete
    TEXT: str
    def __call__(self) -> Logo: ...
    def __rich__(self) -> None: ...
