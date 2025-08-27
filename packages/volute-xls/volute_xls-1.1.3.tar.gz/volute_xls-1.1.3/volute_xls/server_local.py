#!/usr/bin/env python3
"""
Volute-XLS Local Server - Excel-focused MCP server for local COM access.

This server runs locally on Windows machines with Excel installed,
providing COM-based Excel manipulation tools and multimodal sheet capture.

Run with: python server_local.py
"""

import os
import sys
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("LOCAL_SERVER_NAME", "Volute-XLS-Local")
SERVER_HOST = os.getenv("LOCAL_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("LOCAL_SERVER_PORT", "8002"))

# Create FastMCP server instance
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=f"""
        This is a LOCAL Volute-XLS server providing Excel analysis and multimodal tools.
        
        🖥️ **Local Access Features**:
        - Excel COM integration via xlwings (comprehensive metadata extraction)
        - Sheet image capture for multimodal LLM analysis
        - Range-specific image capture for focused analysis
        - Local file system access
        - Windows-specific functionality
        - Thread-safe Excel operations
        
        🎯 **Multimodal Capabilities**:
        - Capture Excel sheets as images
        - Capture specific cell ranges as images
        - Export sheets for visual analysis by multimodal LLMs
        - Return base64-encoded images compatible with vision models
        - Support for selective sheet capture (specify sheet names)
        - Zoom control for optimal image quality
        
        📊 **Excel Analysis Tools**:
        - Comprehensive workbook metadata extraction
        - Sheet structure and content analysis
        - Formula and data type detection
        - Charts and images detection
        - Named ranges and merged cells analysis
        - Sample data extraction for content understanding
        
        🌐 **Companion Cloud Server**: https://volutemcp-server.onrender.com
        - Use cloud server for general tools (calculate, echo, etc.)
        - Use this local server for Excel and local file operations
        
        ⚠️ **Requirements**:
        - Windows operating system (recommended)
        - Microsoft Excel installed (for image capture)
        - openpyxl package for metadata extraction
        - xlwings package for COM automation and image capture
        - Pillow package for image processing
        - Local file access permissions
    """,
    on_duplicate_tools="warn",
    on_duplicate_resources="warn", 
    on_duplicate_prompts="replace",
    include_fastmcp_meta=True,
)

# ============================================================================
# EXCEL TOOLS REGISTRATION (LOCAL COM ACCESS)
# ============================================================================

try:
    # Import from the relative package module
    from .excel_tools import register_excel_tools
    register_excel_tools(mcp)
    print("✅ Excel metadata tools registered (local access)", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ Excel tools not available: {e}", file=sys.stderr)
except Exception as e:
    print(f"❌ Error registering Excel tools: {e}", file=sys.stderr)

# ============================================================================
# SHEET IMAGE CAPTURE TOOLS (MULTIMODAL SUPPORT)
# ============================================================================

try:
    from .sheet_capture_tools import register_sheet_capture_tools
    register_sheet_capture_tools(mcp)
    print("✅ Sheet image capture tools registered (multimodal support)", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ Sheet capture tools not available: {e}", file=sys.stderr)
except Exception as e:
    print(f"❌ Error registering sheet capture tools: {e}", file=sys.stderr)

# ============================================================================
# LOCAL TOOLS - Functions that require local access
# ============================================================================

@mcp.tool(tags={"local", "files"})
def list_local_files(directory: str = ".", pattern: str = "*.xlsx") -> list:
    """
    List Excel files in a local directory.
    
    Args:
        directory: Local directory to search (default: current directory)
        pattern: File pattern to match (default: *.xlsx)
    """
    import glob
    import os
    
    if not os.path.exists(directory):
        raise ValueError(f"Directory not found: {directory}")
    
    search_path = os.path.join(directory, pattern)
    files = glob.glob(search_path)
    
    # Also search for other Excel formats
    if pattern == "*.xlsx":
        for ext in ["*.xlsm", "*.xls"]:
            search_path = os.path.join(directory, ext)
            files.extend(glob.glob(search_path))
    
    return [
        {
            "path": file,
            "name": os.path.basename(file),
            "size": os.path.getsize(file),
            "modified": os.path.getmtime(file),
            "extension": os.path.splitext(file)[1].lower()
        }
        for file in files
    ]

@mcp.tool(tags={"local", "system"})
def get_local_system_info() -> dict:
    """Get information about the local system and Excel availability."""
    import platform
    
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "server_type": "LOCAL",
        "excel_available": False,
        "openpyxl_available": False,
        "xlwings_available": False
    }
    
    # Check if openpyxl is available
    try:
        import openpyxl
        info["openpyxl_available"] = True
        info["openpyxl_version"] = openpyxl.__version__
    except ImportError:
        pass
    
    # Check if xlwings is available
    try:
        import xlwings as xw
        info["xlwings_available"] = True
        info["xlwings_version"] = xw.__version__
        
        # Try to connect to Excel
        try:
            app = xw.App(visible=False, add_book=False)
            info["excel_available"] = True
            info["excel_version"] = app.version
            app.quit()
        except:
            pass
    except ImportError:
        pass
    
    return info

@mcp.tool(tags={"local", "files"})  
def read_local_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read content from a local file.
    
    Args:
        file_path: Path to local file
        encoding: File encoding (default: utf-8)
    """
    import os
    
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()

# ============================================================================
# LOCAL RESOURCES - Local data sources
# ============================================================================

@mcp.resource("local://system")
def get_local_system_status() -> dict:
    """Provides local system status and capabilities."""
    return {
        "server_type": "LOCAL",
        "excel_integration": True,
        "local_file_access": True,
        "com_objects": True,
        "multimodal_capture": True,
        "companion_cloud_server": "https://volutemcp-server.onrender.com"
    }

@mcp.resource("local://files/{directory}")
def get_directory_listing(directory: str) -> dict:
    """Get listing of files in a local directory."""
    import os
    import glob
    
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}
    
    files = []
    for file_path in glob.glob(os.path.join(directory, "*")):
        if os.path.isfile(file_path):
            files.append({
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": os.path.getsize(file_path),
                "extension": os.path.splitext(file_path)[1],
                "is_excel": os.path.splitext(file_path)[1].lower() in ['.xlsx', '.xlsm', '.xls']
            })
    
    return {
        "directory": directory,
        "files": files,
        "count": len(files),
        "excel_files": len([f for f in files if f["is_excel"]])
    }

# ============================================================================
# CUSTOM ROUTES
# ============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("LOCAL-OK")

@mcp.custom_route("/info", methods=["GET"])
async def server_info_endpoint(request: Request) -> PlainTextResponse:
    """Local server information endpoint."""
    info = f"Server: {SERVER_NAME}\\nType: LOCAL\\nExcel: Available\\nStatus: Running"
    return PlainTextResponse(info)

# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the local server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Volute-XLS Local Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "http"], 
        default="http",
        help="Transport protocol (default: http)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=SERVER_PORT,
        help=f"Port number for HTTP transport (default: {SERVER_PORT})"
    )
    parser.add_argument(
        "--host", 
        default=SERVER_HOST,
        help=f"Host address for HTTP transport (default: {SERVER_HOST})"
    )
    
    # Support legacy stdio argument
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        args = argparse.Namespace(transport="stdio", port=SERVER_PORT, host=SERVER_HOST)
    else:
        args = parser.parse_args()
    
    if args.transport == "stdio":
        # STDIO transport for local MCP clients
        print(f"Starting {SERVER_NAME} with STDIO transport...", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        # HTTP transport
        print(f"Starting {SERVER_NAME} LOCAL server...", file=sys.stderr)
        print(f"Local server: http://{args.host}:{args.port}", file=sys.stderr)
        print(f"Cloud companion: https://volutemcp-server.onrender.com", file=sys.stderr)
        print(f"Health check: http://{args.host}:{args.port}/health", file=sys.stderr)
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
        )

if __name__ == "__main__":
    main()
