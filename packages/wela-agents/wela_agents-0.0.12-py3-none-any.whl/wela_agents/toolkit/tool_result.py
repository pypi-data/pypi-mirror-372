
from typing import List
from typing_extensions import Literal
from typing_extensions import Required
from typing_extensions import Optional
from typing_extensions import TypedDict

class Attachment(TypedDict, total=False):
    type: Required[Literal["text", "image_url"]]

    content: Required[str]

class ToolResult(TypedDict, total=False):
    result: Required[str]

    attachment: Optional[List[Attachment]]
