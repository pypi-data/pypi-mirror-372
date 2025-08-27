"""
Excel sheet image capture tools for multimodal analysis.
Uses xlwings to capture sheet ranges as images and return them for LLM multimodal processing.
"""

import os
import base64
import hashlib
import tempfile
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Check for xlwings availability
XLWINGS_AVAILABLE = False
try:
    import xlwings as xw
    from PIL import Image
    XLWINGS_AVAILABLE = True
    logger.info("xlwings and PIL available for Excel sheet image capture")
except ImportError as e:
    logger.warning(f"xlwings or PIL not available: {e}")

# Thread-safe lock for Excel operations
_excel_lock = threading.Lock()


class SheetImageCaptureResult(BaseModel):
    """Model for sheet image capture results."""
    success: bool = Field(description="Whether the capture was successful")
    message: str = Field(description="Status message")
    sheet_images: Dict[str, str] = Field(default_factory=dict, description="Map of sheet names to base64 image data")
    captured_count: int = Field(default=0, description="Number of sheets successfully captured")
    failed_sheets: List[str] = Field(default_factory=list, description="List of sheet names that failed to capture")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional capture metadata")


class RangeImageCaptureResult(BaseModel):
    """Model for range image capture results."""
    success: bool = Field(description="Whether the capture was successful")
    message: str = Field(description="Status message")
    range_images: Dict[str, str] = Field(default_factory=dict, description="Map of range addresses to base64 image data")
    captured_count: int = Field(default=0, description="Number of ranges successfully captured")
    failed_ranges: List[str] = Field(default_factory=list, description="List of range addresses that failed to capture")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional capture metadata")


def register_sheet_capture_tools(mcp: FastMCP) -> None:
    """
    Register sheet image capture tools with the FastMCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    def capture_excel_sheets(
        excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
        sheet_names: List[str] = Field(description="Array of sheet names to capture"),
        image_width: int = Field(default=1200, description="Width of captured images in pixels"),
        image_height: int = Field(default=800, description="Height of captured images in pixels"),
        include_metadata: bool = Field(default=True, description="Include capture metadata in response"),
        zoom_level: float = Field(default=100.0, description="Zoom level for capture (percentage, e.g., 100.0 = 100%)")
    ) -> SheetImageCaptureResult:
        """
        Capture Excel sheet images for multimodal LLM analysis.
        
        This tool uses xlwings COM automation to:
        - Open Excel workbooks invisibly
        - Navigate to specific worksheets
        - Capture sheet contents as PNG images
        - Return base64-encoded images for multimodal analysis
        - Handle Excel application lifecycle safely with thread safety
        - Provide comprehensive error handling and guardrails
        
        Perfect for agents that need visual analysis of spreadsheet content!
        """
        try:
            # Validate environment and requirements
            if not XLWINGS_AVAILABLE:
                return SheetImageCaptureResult(
                    success=False,
                    message="xlwings not available",
                    error="xlwings library is required but not available. Install with: pip install xlwings pillow"
                )
            
            # Validate file exists
            if not os.path.exists(excel_path):
                return SheetImageCaptureResult(
                    success=False,
                    message="File not found",
                    error=f"Excel file not found: {excel_path}"
                )
            
            # Check file extension
            file_ext = os.path.splitext(excel_path)[1].lower()
            if file_ext not in ['.xlsx', '.xlsm', '.xls']:
                return SheetImageCaptureResult(
                    success=False,
                    message="Unsupported file format",
                    error=f"Unsupported file format: {file_ext}. Only .xlsx, .xlsm, and .xls files are supported."
                )
            
            # Validate sheet names
            if not sheet_names:
                return SheetImageCaptureResult(
                    success=False,
                    message="No sheets specified",
                    error="At least one sheet name must be specified"
                )
            
            # Limit sheet capture to prevent resource exhaustion
            if len(sheet_names) > 10:
                return SheetImageCaptureResult(
                    success=False,
                    message="Too many sheets requested",
                    error=f"Maximum 10 sheets can be captured at once. Requested: {len(sheet_names)}"
                )
            
            # Validate image dimensions
            if image_width < 200 or image_width > 4000 or image_height < 200 or image_height > 4000:
                return SheetImageCaptureResult(
                    success=False,
                    message="Invalid image dimensions",
                    error="Image dimensions must be between 200 and 4000 pixels"
                )
            
            # Validate zoom level
            if zoom_level < 10.0 or zoom_level > 400.0:
                return SheetImageCaptureResult(
                    success=False,
                    message="Invalid zoom level",
                    error="Zoom level must be between 10% and 400%"
                )
            
            # Perform sheet image capture with thread safety
            result = _capture_sheet_images_safe(
                excel_path, 
                sheet_names, 
                image_width, 
                image_height,
                zoom_level
            )
            
            # Add metadata if requested
            metadata = None
            if include_metadata:
                metadata = {
                    "captureTime": datetime.now().isoformat(),
                    "excelPath": excel_path,
                    "excelName": os.path.basename(excel_path),
                    "requestedSheets": sheet_names,
                    "imageFormat": "PNG",
                    "imageWidth": image_width,
                    "imageHeight": image_height,
                    "zoomLevel": zoom_level,
                    "totalRequested": len(sheet_names),
                    "capturedSuccessfully": len(result["sheet_images"]),
                    "failedSheets": result["failed_sheets"]
                }
            
            return SheetImageCaptureResult(
                success=result["success"],
                message=result["message"],
                sheet_images=result["sheet_images"],
                captured_count=len(result["sheet_images"]),
                failed_sheets=result["failed_sheets"],
                error=result.get("error"),
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error in sheet image capture: {str(e)}")
            return SheetImageCaptureResult(
                success=False,
                message="Capture failed with exception",
                error=f"Unexpected error during sheet capture: {str(e)}"
            )
    
    @mcp.tool()
    def capture_excel_ranges(
        excel_path: str = Field(description="Path to the Excel file (.xlsx, .xlsm, .xls)"),
        sheet_ranges: Dict[str, List[str]] = Field(description="Dictionary mapping sheet names to lists of range addresses (e.g., {'Sheet1': ['A1:C10', 'E1:G5']})"),
        image_width: int = Field(default=800, description="Width of captured images in pixels"),
        image_height: int = Field(default=600, description="Height of captured images in pixels"),
        include_metadata: bool = Field(default=True, description="Include capture metadata in response"),
        zoom_level: float = Field(default=100.0, description="Zoom level for capture (percentage)")
    ) -> RangeImageCaptureResult:
        """
        Capture specific Excel ranges as images for detailed multimodal analysis.
        
        This tool enables precise capture of specific cell ranges from Excel sheets:
        - Target specific data ranges, charts, or table areas
        - Capture multiple ranges from different sheets in one operation
        - Automatically fit ranges to image dimensions
        - Return base64-encoded images with range identifiers
        - Thread-safe Excel COM operations
        
        Ideal for focused analysis of particular spreadsheet sections!
        """
        try:
            if not XLWINGS_AVAILABLE:
                return RangeImageCaptureResult(
                    success=False,
                    message="xlwings not available",
                    error="xlwings library is required but not available. Install with: pip install xlwings pillow"
                )
            
            # Validate file exists
            if not os.path.exists(excel_path):
                return RangeImageCaptureResult(
                    success=False,
                    message="File not found",
                    error=f"Excel file not found: {excel_path}"
                )
            
            # Validate sheet_ranges input
            if not sheet_ranges:
                return RangeImageCaptureResult(
                    success=False,
                    message="No ranges specified",
                    error="At least one sheet with ranges must be specified"
                )
            
            # Count total ranges and validate limits
            total_ranges = sum(len(ranges) for ranges in sheet_ranges.values())
            if total_ranges > 20:
                return RangeImageCaptureResult(
                    success=False,
                    message="Too many ranges requested",
                    error=f"Maximum 20 ranges can be captured at once. Requested: {total_ranges}"
                )
            
            # Validate image dimensions
            if image_width < 100 or image_width > 2000 or image_height < 100 or image_height > 2000:
                return RangeImageCaptureResult(
                    success=False,
                    message="Invalid image dimensions",
                    error="Image dimensions must be between 100 and 2000 pixels for range capture"
                )
            
            # Perform range image capture
            result = _capture_range_images_safe(
                excel_path,
                sheet_ranges,
                image_width,
                image_height,
                zoom_level
            )
            
            # Add metadata if requested
            metadata = None
            if include_metadata:
                metadata = {
                    "captureTime": datetime.now().isoformat(),
                    "excelPath": excel_path,
                    "excelName": os.path.basename(excel_path),
                    "requestedRanges": sheet_ranges,
                    "imageFormat": "PNG",
                    "imageWidth": image_width,
                    "imageHeight": image_height,
                    "zoomLevel": zoom_level,
                    "totalRequested": total_ranges,
                    "capturedSuccessfully": len(result["range_images"]),
                    "failedRanges": result["failed_ranges"]
                }
            
            return RangeImageCaptureResult(
                success=result["success"],
                message=result["message"],
                range_images=result["range_images"],
                captured_count=len(result["range_images"]),
                failed_ranges=result["failed_ranges"],
                error=result.get("error"),
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error in range image capture: {str(e)}")
            return RangeImageCaptureResult(
                success=False,
                message="Capture failed with exception",
                error=f"Unexpected error during range capture: {str(e)}"
            )
    
    @mcp.tool()
    def get_sheet_capture_capabilities() -> Dict[str, Any]:
        """
        Get information about sheet capture capabilities and requirements.
        
        Returns system capabilities for Excel sheet image capture.
        """
        try:
            capabilities = {
                "xlwings_available": XLWINGS_AVAILABLE,
                "supported_formats": [".xlsx", ".xlsm", ".xls"],
                "max_sheets_per_request": 10,
                "max_ranges_per_request": 20,
                "supported_image_format": "PNG",
                "sheet_capture": {
                    "min_image_size": {"width": 200, "height": 200},
                    "max_image_size": {"width": 4000, "height": 4000},
                    "default_image_size": {"width": 1200, "height": 800}
                },
                "range_capture": {
                    "min_image_size": {"width": 100, "height": 100},
                    "max_image_size": {"width": 2000, "height": 2000},
                    "default_image_size": {"width": 800, "height": 600}
                },
                "zoom_control": {
                    "min_zoom": 10.0,
                    "max_zoom": 400.0,
                    "default_zoom": 100.0
                },
                "multimodal_ready": True,
                "base64_encoded": True,
                "thread_safe": True,
                "requirements": {
                    "windows_os": "Recommended for COM automation",
                    "excel_installed": "Required for xlwings COM operations",
                    "xlwings": "Required Python package",
                    "pillow": "Required for image processing"
                }
            }
            
            # Test Excel availability if xlwings is available
            if XLWINGS_AVAILABLE:
                try:
                    # Test Excel availability (non-blocking)
                    test_app = xw.App(visible=False, add_book=False)
                    test_app.quit()
                    capabilities["excel_available"] = True
                    capabilities["status"] = "Ready for sheet capture"
                except Exception as e:
                    capabilities["excel_available"] = False
                    capabilities["status"] = f"Excel not available: {str(e)}"
            else:
                capabilities["excel_available"] = False
                capabilities["status"] = "xlwings library not available"
            
            return capabilities
            
        except Exception as e:
            logger.exception(f"Error getting sheet capture capabilities: {str(e)}")
            return {"error": str(e)}


def _capture_sheet_images_safe(excel_path: str, sheet_names: List[str], 
                              image_width: int, image_height: int, 
                              zoom_level: float = 100.0) -> Dict[str, Any]:
    """
    Thread-safe sheet image capture implementation.
    
    Args:
        excel_path: Path to Excel file
        sheet_names: List of sheet names to capture
        image_width: Image width in pixels
        image_height: Image height in pixels
        zoom_level: Zoom level percentage
        
    Returns:
        Dictionary with capture results
    """
    with _excel_lock:
        app = None
        wb = None
        
        try:
            # Create Excel application
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(excel_path)
            
            sheet_images = {}
            failed_sheets = []
            
            # Get available sheet names for validation
            available_sheets = [sheet.name for sheet in wb.sheets]
            
            for sheet_name in sheet_names:
                try:
                    if sheet_name not in available_sheets:
                        logger.warning(f"Sheet '{sheet_name}' not found in workbook")
                        failed_sheets.append(sheet_name)
                        continue
                    
                    # Select the sheet
                    sheet = wb.sheets[sheet_name]
                    sheet.activate()
                    
                    # Set zoom level
                    if hasattr(sheet.api, 'Zoom'):
                        sheet.api.Zoom = zoom_level
                    
                    # Create temporary file for image
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        temp_path = tmp_file.name
                    
                    try:
                        # Capture sheet as image
                        # Use xlwings picture export functionality
                        used_range = sheet.used_range
                        if used_range:
                            # Export the used range as an image
                            used_range.api.CopyPicture(Format=2)  # xlBitmap format
                            
                            # Create a new sheet temporarily to paste and export
                            temp_sheet = wb.sheets.add(name="__temp_capture__")
                            temp_sheet.activate()
                            
                            # Paste as picture
                            temp_sheet.api.Paste()
                            
                            # Export as image
                            temp_sheet.api.ExportAsFixedFormat(
                                Type=0,  # xlTypePNG
                                Filename=temp_path,
                                Quality=0,  # xlQualityStandard
                                IncludeDocProps=False,
                                IgnorePrintAreas=True,
                                OpenAfterPublish=False
                            )
                            
                            # Clean up temp sheet
                            temp_sheet.delete()
                            
                            # Read and encode image
                            if os.path.exists(temp_path):
                                # Resize image if needed
                                with Image.open(temp_path) as img:
                                    img = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
                                    img.save(temp_path, 'PNG', optimize=True)
                                
                                with open(temp_path, 'rb') as img_file:
                                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                                    sheet_images[sheet_name] = f"data:image/png;base64,{img_data}"
                        
                        else:
                            logger.warning(f"Sheet '{sheet_name}' appears to be empty")
                            failed_sheets.append(sheet_name)
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                
                except Exception as e:
                    logger.error(f"Failed to capture sheet '{sheet_name}': {e}")
                    failed_sheets.append(sheet_name)
            
            success = len(sheet_images) > 0
            if success:
                message = f"Successfully captured {len(sheet_images)} out of {len(sheet_names)} sheets"
            else:
                message = "Failed to capture any sheets"
            
            return {
                "success": success,
                "message": message,
                "sheet_images": sheet_images,
                "failed_sheets": failed_sheets
            }
            
        except Exception as e:
            logger.exception(f"Critical error in sheet capture: {e}")
            return {
                "success": False,
                "message": "Critical capture error",
                "sheet_images": {},
                "failed_sheets": sheet_names,
                "error": str(e)
            }
        
        finally:
            # Clean up Excel resources
            try:
                if wb:
                    wb.close()
                if app:
                    app.quit()
            except Exception as cleanup_error:
                logger.error(f"Error during Excel cleanup: {cleanup_error}")


def _capture_range_images_safe(excel_path: str, sheet_ranges: Dict[str, List[str]],
                              image_width: int, image_height: int,
                              zoom_level: float = 100.0) -> Dict[str, Any]:
    """
    Thread-safe range image capture implementation.
    
    Args:
        excel_path: Path to Excel file
        sheet_ranges: Dictionary of sheet names to range lists
        image_width: Image width in pixels
        image_height: Image height in pixels
        zoom_level: Zoom level percentage
        
    Returns:
        Dictionary with capture results
    """
    with _excel_lock:
        app = None
        wb = None
        
        try:
            # Create Excel application
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(excel_path)
            
            range_images = {}
            failed_ranges = []
            
            # Get available sheet names for validation
            available_sheets = [sheet.name for sheet in wb.sheets]
            
            for sheet_name, ranges in sheet_ranges.items():
                if sheet_name not in available_sheets:
                    logger.warning(f"Sheet '{sheet_name}' not found in workbook")
                    failed_ranges.extend([f"{sheet_name}!{r}" for r in ranges])
                    continue
                
                # Select the sheet
                sheet = wb.sheets[sheet_name]
                sheet.activate()
                
                # Set zoom level
                if hasattr(sheet.api, 'Zoom'):
                    sheet.api.Zoom = zoom_level
                
                for range_addr in ranges:
                    range_key = f"{sheet_name}!{range_addr}"
                    try:
                        # Select the range
                        range_obj = sheet.range(range_addr)
                        range_obj.select()
                        
                        # Create temporary file for image
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                            temp_path = tmp_file.name
                        
                        try:
                            # Copy range as picture
                            range_obj.api.CopyPicture(Format=2)  # xlBitmap format
                            
                            # Create temporary sheet for export
                            temp_sheet = wb.sheets.add(name="__temp_range__")
                            temp_sheet.activate()
                            
                            # Paste and export
                            temp_sheet.api.Paste()
                            temp_sheet.api.ExportAsFixedFormat(
                                Type=0,  # xlTypePNG
                                Filename=temp_path,
                                Quality=0,  # xlQualityStandard
                                IncludeDocProps=False,
                                IgnorePrintAreas=True,
                                OpenAfterPublish=False
                            )
                            
                            # Clean up temp sheet
                            temp_sheet.delete()
                            
                            # Process image
                            if os.path.exists(temp_path):
                                with Image.open(temp_path) as img:
                                    img = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
                                    img.save(temp_path, 'PNG', optimize=True)
                                
                                with open(temp_path, 'rb') as img_file:
                                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                                    range_images[range_key] = f"data:image/png;base64,{img_data}"
                        
                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_path):
                                try:
                                    os.unlink(temp_path)
                                except:
                                    pass
                    
                    except Exception as e:
                        logger.error(f"Failed to capture range '{range_key}': {e}")
                        failed_ranges.append(range_key)
            
            success = len(range_images) > 0
            total_requested = sum(len(ranges) for ranges in sheet_ranges.values())
            
            if success:
                message = f"Successfully captured {len(range_images)} out of {total_requested} ranges"
            else:
                message = "Failed to capture any ranges"
            
            return {
                "success": success,
                "message": message,
                "range_images": range_images,
                "failed_ranges": failed_ranges
            }
            
        except Exception as e:
            logger.exception(f"Critical error in range capture: {e}")
            all_ranges = []
            for sheet_name, ranges in sheet_ranges.items():
                all_ranges.extend([f"{sheet_name}!{r}" for r in ranges])
            
            return {
                "success": False,
                "message": "Critical capture error",
                "range_images": {},
                "failed_ranges": all_ranges,
                "error": str(e)
            }
        
        finally:
            # Clean up Excel resources
            try:
                if wb:
                    wb.close()
                if app:
                    app.quit()
            except Exception as cleanup_error:
                logger.error(f"Error during Excel cleanup: {cleanup_error}")
