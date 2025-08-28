"""
Main MCP Server

Integrates FastMCP with the email widget tools.
"""

from mcp.server.fastmcp import FastMCP
from .tools import EmailTemplateGenerator, NostoSnippetGenerator


def create_fastmcp_app():
    """Create the FastMCP application."""

    # Create FastMCP server with HTTP transport configuration
    mcp = FastMCP("nosto-email-widgets", host="0.0.0.0", port=8000)

    # Create tool instances
    template_tool = EmailTemplateGenerator()
    nosto_tool = NostoSnippetGenerator()

    # Add email template generator tool
    @mcp.tool()
    def email_template_generator(
        template_type: str,
        company_name: str,
        primary_color: str = "#007bff",
        logo_url: str = None,
        content_sections: list[str] = None,
        custom_message: str = None
    ) -> str:
        from .tools.email_template_generator import EmailTemplateRequest

        # Set default content sections if none provided
        if content_sections is None:
            content_sections = ["header", "main_content", "footer"]

        request = EmailTemplateRequest(
            template_type=template_type,
            company_name=company_name,
            primary_color=primary_color,
            logo_url=logo_url,
            content_sections=content_sections,
            custom_message=custom_message
        )

        return template_tool(request)

    # Add Nosto snippet generator tool
    @mcp.tool()
    def nosto_snippet_generator() -> str:
        """Generate Nosto HTML snippet for email templates."""
        from .tools.nosto_snippet_generator import NostoSnippetRequest

        request = NostoSnippetRequest()
        return nosto_tool(request)

    return mcp
