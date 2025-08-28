#!/usr/bin/env python3
"""
Main entry point for the Nosto Email Widgets MCP Server

Run this file to start the server.
"""

import uvicorn
from src.server import create_fastmcp_app


def main():
    """Main function to run the server."""
    
    # Create the FastMCP app
    mcp = create_fastmcp_app()
    
    # Get the Starlette app from FastMCP for HTTP transport
    app = mcp.streamable_http_app()
    
    # Add CORS middleware
    from starlette.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development - restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add health check endpoint using Starlette's route decorator
    @app.route("/health", methods=["GET"])
    async def health_check(request):
        """Health check endpoint."""
        from starlette.responses import JSONResponse
        return JSONResponse({"status": "healthy", "service": "nosto-email-widgets-mcp"})
    
    # Run the server using uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
        # Note: reload=True requires the app as an import string, not as an object
    )


if __name__ == "__main__":
    main()
