from pydantic import BaseModel


class ImprovedFileResponse(BaseModel):
    """A response containing the complete improved file content."""

    improved_content: str
    """The complete improved file content."""

    changes_summary: str
    """A summary of the changes made to the file."""
