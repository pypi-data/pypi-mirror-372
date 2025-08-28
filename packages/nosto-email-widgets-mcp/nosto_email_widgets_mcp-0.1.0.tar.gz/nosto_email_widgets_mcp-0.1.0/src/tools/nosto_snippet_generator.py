"""
Nosto Snippet Generator Tool

A tool that returns the Nosto HTML snippet for email templates.
"""

from mcp import Tool
from pydantic import BaseModel


class NostoSnippetRequest(BaseModel):
    """Request model for the Nosto snippet generator."""
    
    # No parameters needed - always returns the same snippet
    pass


class NostoSnippetGenerator(Tool):
    """Tool for generating Nosto HTML snippets."""

    name: str = "nosto_snippet_generator"
    description: str = "Generate Nosto HTML snippet for email templates with product recommendations"
    inputSchema: type[NostoSnippetRequest] = NostoSnippetRequest

    def __call__(self, request: NostoSnippetRequest) -> str:
        """Return the Nosto HTML snippet."""
        
        return """
<div class="nosto-snippet">
    <p>Hello, World! This is a Nosto snippet placeholder.</p>
</div>
        """
