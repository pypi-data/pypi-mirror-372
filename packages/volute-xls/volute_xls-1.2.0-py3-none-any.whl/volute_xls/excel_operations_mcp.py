#!/usr/bin/env python3
"""
Excel Operations MCP Tools Registration

This module registers the Excel operations MCP tools for use with the MCP framework.
"""

import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def register_excel_mcp_tools(mcp):
    """
    Register Excel operations MCP tools with the FastMCP framework.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    from fastmcp import FastMCP
    from pydantic import Field
    
    try:
        # Import both old and optimized versions
        from .excel_operations_tools import (
            excel_cell_operations,
            excel_row_column_operations, 
            excel_sheet_operations
        )
        
        from .excel_operations_optimized import (
            excel_edit,
            excel_quick_cells,
            excel_quick_format
        )
        
        # Register the ultra-simple main tool - BEST FOR AI AGENTS
        @mcp.tool()
        def excel_edit_tool(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            commands: str = Field(description="Natural commands (one per line): A1 = \"Hello\", B1 = 42, A1 bold, insert row 5, add sheet \"Data\""),
            sheet: str = Field(default=None, description="Optional sheet name (auto-detected if not provided)")
        ) -> str:
            """EASIEST Excel editing tool for AI agents! Use natural commands like: A1 = \"Hello\", B1 = 42, A1 bold, insert row 5, add sheet \"Data\"."""
            # Convert sheet parameter to proper string if it's not None
            sheet_name = None if sheet is None else str(sheet) if not isinstance(sheet, str) else sheet
            return excel_edit(excel_path, commands, sheet_name)
        
        # Register quick cell operations - SIMPLEST FOR CELL VALUES
        @mcp.tool()
        def excel_set_cells_tool(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            cell_data: str = Field(description="Cell assignments (one per line): A1 = \"Text\", B1 = 123, C1 = =SUM(A1:B1)"),
            sheet: str = Field(default=None, description="Sheet name (optional)")
        ) -> str:
            """Set cell values with the simplest possible syntax: A1 = \"Text\", B1 = 123, C1 = =SUM(A1:B1)."""
            # Convert sheet parameter to proper string if it's not None
            sheet_name = None if sheet is None else str(sheet) if not isinstance(sheet, str) else sheet
            return excel_quick_cells(excel_path, cell_data, sheet_name)
        
        # Register quick formatting - SIMPLEST FOR FORMATTING
        @mcp.tool()
        def excel_format_cells_tool(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            format_commands: str = Field(description="Format commands (one per line): A1 bold, B1 background yellow, C1 font red"),
            sheet: str = Field(default=None, description="Sheet name (optional)")
        ) -> str:
            """Format cells with simple commands: A1 bold, B1 background yellow, C1 font red."""
            # Convert sheet parameter to proper string if it's not None
            sheet_name = None if sheet is None else str(sheet) if not isinstance(sheet, str) else sheet
            return excel_quick_format(excel_path, format_commands, sheet_name)
        
        # Keep original tools for backwards compatibility
        @mcp.tool()
        def excel_cell_operations_tool(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            cell_operations: str = Field(description="DSL string specifying cell operations (formatting, values, formulas)")
        ) -> str:
            """Perform cell operations on an Excel file using DSL format. Set cell values, format cells, and add data validation."""
            return excel_cell_operations(excel_path, cell_operations)
        
        @mcp.tool()
        def excel_row_column_operations_tool(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            row_column_operations: str = Field(description="DSL string specifying row/column operations")
        ) -> str:
            """Perform row and column operations on an Excel file using DSL format. Insert/delete/resize/hide rows and columns."""
            return excel_row_column_operations(excel_path, row_column_operations)
        
        @mcp.tool()
        def excel_sheet_operations_tool(
            excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
            sheet_operations: str = Field(description="DSL string specifying sheet operations")
        ) -> str:
            """Perform sheet operations on an Excel file using DSL format. Add/delete/rename/move/copy worksheets."""
            return excel_sheet_operations(excel_path, sheet_operations)
        
        logger.info("Successfully registered Excel operations MCP tools (including optimized AI-friendly tools)")
        
    except Exception as e:
        logger.error(f"Failed to register Excel operations MCP tools: {e}")
        raise


if __name__ == "__main__":
    # Example registration (for testing)
    def mock_register(name, description, input_schema, func):
        print(f"Registered tool: {name}")
        print(f"Description: {description}")
        print(f"Schema: {input_schema}")
        print("-" * 50)
    
    register_excel_mcp_tools(mock_register)
