"""
Google Drive integration tools using service account authentication.
Provides comprehensive file and folder operations for agents.
"""

import io
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from langchain_core.tools import tool

from broadie.config.integrations import get_integrations_config
from broadie.utils.exceptions import ToolError


def _get_drive_service():
    """Get authenticated Google Drive service using service account."""
    try:
        # Get configuration
        config = get_integrations_config()

        if not config.is_google_drive_configured():
            raise ToolError(
                "Google Drive not configured. Set GOOGLE_SERVICE_ACCOUNT_FILE environment variable. "
                "See setup instructions: python -c \"from broadie.core.tool_configurator import show_setup_instructions; show_setup_instructions('google_drive')\""
            )

        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            config.google_drive.service_account_file, scopes=config.google_drive.scopes
        )

        # Handle domain-wide delegation if configured
        if config.google_drive.delegated_user:
            credentials = credentials.with_subject(config.google_drive.delegated_user)

        # Build and return service
        service = build("drive", "v3", credentials=credentials)
        return service

    except Exception as e:
        if "not configured" in str(e):
            raise e
        raise ToolError(f"Failed to initialize Google Drive service: {str(e)}")


def _get_sheets_service():
    """Get authenticated Google Sheets service."""
    try:
        # Get configuration
        config = get_integrations_config()

        if not config.is_google_drive_configured():
            raise ToolError(
                "Google Drive not configured. Set GOOGLE_SERVICE_ACCOUNT_FILE environment variable. "
                "See setup instructions: python -c \"from broadie.core.tool_configurator import show_setup_instructions; show_setup_instructions('google_drive')\""
            )

        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            config.google_drive.service_account_file, scopes=config.google_drive.scopes
        )

        # Handle domain-wide delegation if configured
        if config.google_drive.delegated_user:
            credentials = credentials.with_subject(config.google_drive.delegated_user)

        # Build and return service
        service = build("sheets", "v4", credentials=credentials)
        return service

    except Exception as e:
        if "not configured" in str(e):
            raise e
        raise ToolError(f"Failed to initialize Google Sheets service: {str(e)}")


@tool(
    description="""Search for files and folders in Google Drive by name, type, or content.
Supports powerful search queries using Google Drive search syntax.

Example usage:
- search_google_drive("meeting notes", file_type="document")  # Find documents with "meeting notes"
- search_google_drive("Q4 budget", file_type="spreadsheet")  # Find Q4 budget spreadsheets  
- search_google_drive("presentation", folder_id="1ABC123")    # Search within specific folder
- search_google_drive("modified > '2024-01-01'")             # Files modified after date

Returns list of files with id, name, type, size, and sharing info."""
)
def search_google_drive(
    query: str,
    file_type: Optional[str] = None,
    folder_id: Optional[str] = None,
    limit: int = 20,
) -> str:
    """
    Search Google Drive for files and folders.

    Args:
        query: Search query (file name, content keywords, or Drive search syntax)
        file_type: Filter by type - 'document', 'spreadsheet', 'presentation', 'folder', 'pdf', 'image'
        folder_id: Search within specific folder (use folder's Drive ID)
        limit: Maximum number of results to return

    Returns:
        Formatted string with search results
    """
    try:
        service = _get_drive_service()

        # Build search query
        search_query = f"name contains '{query}'" if query else ""

        # Add type filter
        mime_types = {
            "document": "application/vnd.google-apps.document",
            "spreadsheet": "application/vnd.google-apps.spreadsheet",
            "presentation": "application/vnd.google-apps.presentation",
            "folder": "application/vnd.google-apps.folder",
            "pdf": "application/pdf",
            "image": "image/",
        }

        if file_type and file_type in mime_types:
            mime_filter = f"mimeType='{mime_types[file_type]}'"
            if file_type == "image":
                mime_filter = f"mimeType contains '{mime_types[file_type]}'"
            search_query = (
                f"{search_query} and {mime_filter}" if search_query else mime_filter
            )

        # Add folder filter
        if folder_id:
            folder_filter = f"'{folder_id}' in parents"
            search_query = (
                f"{search_query} and {folder_filter}" if search_query else folder_filter
            )

        # Execute search
        results = (
            service.files()
            .list(
                q=search_query,
                pageSize=limit,
                fields="files(id,name,mimeType,size,modifiedTime,owners,permissions,webViewLink)",
            )
            .execute()
        )

        files = results.get("files", [])

        if not files:
            return f"No files found matching query: '{query}'"

        # Format results
        output = f"Found {len(files)} files:\n\n"
        for file in files:
            name = file.get("name", "Unknown")
            file_id = file.get("id", "Unknown")
            mime_type = file.get("mimeType", "")
            size = file.get("size", "Unknown")
            modified = file.get("modifiedTime", "Unknown")
            link = file.get("webViewLink", "No link")

            # Determine file type
            if "document" in mime_type:
                type_str = "📝 Document"
            elif "spreadsheet" in mime_type:
                type_str = "📊 Spreadsheet"
            elif "presentation" in mime_type:
                type_str = "🎯 Presentation"
            elif "folder" in mime_type:
                type_str = "📁 Folder"
                size = "N/A"
            else:
                type_str = "📄 File"

            # Format size
            if size != "Unknown" and size != "N/A":
                try:
                    size_int = int(size)
                    if size_int > 1024 * 1024:
                        size = f"{size_int/(1024*1024):.1f}MB"
                    elif size_int > 1024:
                        size = f"{size_int/1024:.1f}KB"
                    else:
                        size = f"{size_int}B"
                except:
                    pass

            output += f"{type_str} {name}\n"
            output += f"   ID: {file_id}\n"
            output += f"   Size: {size}\n"
            output += f"   Modified: {modified}\n"
            output += f"   Link: {link}\n\n"

        return output.strip()

    except HttpError as e:
        return f"Google Drive API error: {str(e)}"
    except Exception as e:
        raise ToolError(f"Error searching Google Drive: {str(e)}")


@tool(
    description="""Read content from Google Drive files (documents, spreadsheets, text files).
Extracts and returns the actual content for analysis or summarization.

Example usage:
- read_google_drive_file("1ABC123DEF456")  # Read document by ID
- read_google_drive_file("meeting_notes.docx", by_name=True)  # Find and read by name

Perfect for: analyzing documents, extracting data from sheets, reading reports."""
)
def read_google_drive_file(
    file_identifier: str, by_name: bool = False, sheet_range: Optional[str] = None
) -> str:
    """
    Read content from a Google Drive file.

    Args:
        file_identifier: File ID or name (if by_name=True)
        by_name: If True, search for file by name instead of using ID
        sheet_range: For spreadsheets, specify range like 'Sheet1!A1:D10'

    Returns:
        File content as formatted string
    """
    try:
        service = _get_drive_service()

        # Get file ID if searching by name
        if by_name:
            results = (
                service.files()
                .list(q=f"name='{file_identifier}'", fields="files(id,name,mimeType)")
                .execute()
            )
            files = results.get("files", [])
            if not files:
                return f"No file found with name: '{file_identifier}'"
            file_id = files[0]["id"]
            file_name = files[0]["name"]
            mime_type = files[0]["mimeType"]
        else:
            file_id = file_identifier
            # Get file metadata
            file_metadata = (
                service.files().get(fileId=file_id, fields="name,mimeType").execute()
            )
            file_name = file_metadata["name"]
            mime_type = file_metadata["mimeType"]

        output = f"Reading file: {file_name}\n"
        output += "=" * 50 + "\n\n"

        # Handle different file types
        if "google-apps.document" in mime_type:
            # Export Google Doc as plain text
            request = service.files().export_media(
                fileId=file_id, mimeType="text/plain"
            )
            content = request.execute().decode("utf-8")
            output += content

        elif "google-apps.spreadsheet" in mime_type:
            # Read spreadsheet using Sheets API
            sheets_service = _get_sheets_service()

            if not sheet_range:
                # Get all sheets and read first one
                sheet_metadata = (
                    sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
                )
                sheets = sheet_metadata.get("sheets", [])
                if sheets:
                    sheet_name = sheets[0]["properties"]["title"]
                    sheet_range = f"{sheet_name}!A1:Z1000"  # Read large range
                else:
                    return f"No sheets found in spreadsheet: {file_name}"

            result = (
                sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=file_id, range=sheet_range)
                .execute()
            )

            values = result.get("values", [])
            if not values:
                output += "Empty spreadsheet"
            else:
                # Format as table
                for i, row in enumerate(values):
                    if i == 0:  # Header row
                        output += " | ".join(str(cell) for cell in row) + "\n"
                        output += (
                            "-" * (len(" | ".join(str(cell) for cell in row))) + "\n"
                        )
                    else:
                        output += (
                            " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                        )

        elif "google-apps.presentation" in mime_type:
            # Export presentation as plain text
            request = service.files().export_media(
                fileId=file_id, mimeType="text/plain"
            )
            content = request.execute().decode("utf-8")
            output += content

        else:
            # For other file types, try to download as text
            try:
                request = service.files().get_media(fileId=file_id)
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

                content = file_content.getvalue().decode("utf-8")
                output += content
            except:
                output += f"Cannot read content from file type: {mime_type}"

        return output

    except HttpError as e:
        return f"Google Drive API error: {str(e)}"
    except Exception as e:
        raise ToolError(f"Error reading Google Drive file: {str(e)}")


@tool(
    description="""Write content to Google Drive - create documents, upload files, or update existing files.
Supports creating Google Docs, plain text files, and uploading various file types.

Example usage:
- write_google_drive_file("Meeting Notes", "Today's meeting covered...", file_type="document")
- write_google_drive_file("report.txt", "Analysis results...", folder_id="1ABC123")  
- write_google_drive_file("budget.csv", csv_data, file_type="spreadsheet", update_existing=True)

Perfect for: saving analysis results, creating reports, backing up information."""
)
def write_google_drive_file(
    filename: str,
    content: str,
    file_type: str = "document",
    folder_id: Optional[str] = None,
    update_existing: bool = False,
) -> str:
    """
    Write content to Google Drive file.

    Args:
        filename: Name for the file
        content: Content to write
        file_type: 'document', 'text', 'csv' - type of file to create
        folder_id: ID of folder to save in (optional)
        update_existing: If True, update existing file with same name

    Returns:
        Success message with file ID and link
    """
    try:
        service = _get_drive_service()

        # Check for existing file if update_existing is True
        existing_file_id = None
        if update_existing:
            search_query = f"name='{filename}'"
            if folder_id:
                search_query += f" and '{folder_id}' in parents"

            results = service.files().list(q=search_query).execute()
            files = results.get("files", [])
            if files:
                existing_file_id = files[0]["id"]

        # Determine MIME type
        mime_types = {
            "document": "application/vnd.google-apps.document",
            "text": "text/plain",
            "csv": "text/csv",
        }
        mime_type = mime_types.get(file_type, "text/plain")

        # Prepare file metadata
        file_metadata = {"name": filename}
        if folder_id and not existing_file_id:
            file_metadata["parents"] = [folder_id]

        # Create media upload
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode("utf-8")), mimetype=mime_type, resumable=True
        )

        if existing_file_id:
            # Update existing file
            file = (
                service.files()
                .update(fileId=existing_file_id, media_body=media)
                .execute()
            )
            action = "Updated"
        else:
            # Create new file
            file = (
                service.files()
                .create(
                    body=file_metadata, media_body=media, fields="id,name,webViewLink"
                )
                .execute()
            )
            action = "Created"

        file_id = file["id"]
        file_name = file.get("name", filename)

        # Get shareable link
        try:
            link_result = (
                service.files().get(fileId=file_id, fields="webViewLink").execute()
            )
            web_link = link_result.get("webViewLink", "No link available")
        except:
            web_link = f"https://drive.google.com/file/d/{file_id}/view"

        return f"{action} file successfully!\n\nFile: {file_name}\nID: {file_id}\nLink: {web_link}"

    except HttpError as e:
        return f"Google Drive API error: {str(e)}"
    except Exception as e:
        raise ToolError(f"Error writing to Google Drive: {str(e)}")


@tool(
    description="""Create a new Google Sheets spreadsheet with data and formatting.
Perfect for creating reports, data analysis, financial models, and structured data.

Example usage:
- create_google_sheet("Sales Report Q4", [["Product", "Revenue"], ["Widget A", 15000]])
- create_google_sheet("Team Directory", headers=["Name", "Email", "Department"])

Creates properly formatted spreadsheet with headers, formulas support, and sharing options."""
)
def create_google_sheet(
    title: str,
    data: Optional[List[List[Any]]] = None,
    headers: Optional[List[str]] = None,
    folder_id: Optional[str] = None,
    auto_format: bool = True,
) -> str:
    """
    Create a new Google Sheets spreadsheet.

    Args:
        title: Name of the spreadsheet
        data: List of rows (each row is a list of values)
        headers: Column headers (will be added as first row)
        folder_id: Folder to create sheet in
        auto_format: Apply basic formatting (bold headers, etc.)

    Returns:
        Success message with sheet ID and link
    """
    try:
        sheets_service = _get_sheets_service()
        drive_service = _get_drive_service()

        # Create spreadsheet
        spreadsheet_body = {"properties": {"title": title}}

        spreadsheet = (
            sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
        )
        spreadsheet_id = spreadsheet["spreadsheetId"]

        # Move to folder if specified
        if folder_id:
            drive_service.files().update(
                fileId=spreadsheet_id, addParents=folder_id, fields="id,parents"
            ).execute()

        # Prepare data for insertion
        all_data = []
        if headers:
            all_data.append(headers)
        if data:
            all_data.extend(data)

        if all_data:
            # Insert data
            body = {"values": all_data}
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Sheet1!A1",
                valueInputOption="RAW",
                body=body,
            ).execute()

            # Apply formatting if requested
            if auto_format and headers:
                format_requests = [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": 0,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "textFormat": {"bold": True},
                                    "backgroundColor": {
                                        "red": 0.9,
                                        "green": 0.9,
                                        "blue": 0.9,
                                    },
                                }
                            },
                            "fields": "userEnteredFormat(textFormat,backgroundColor)",
                        }
                    }
                ]

                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, body={"requests": format_requests}
                ).execute()

        # Get shareable link
        web_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

        return f"Created Google Sheet successfully!\n\nTitle: {title}\nID: {spreadsheet_id}\nRows: {len(all_data) if all_data else 0}\nLink: {web_link}"

    except Exception as e:
        raise ToolError(f"Error creating Google Sheet: {str(e)}")


@tool(
    description="""Update existing Google Sheets with new data, formulas, or formatting.
Supports range-based updates, appending data, and batch operations.

Example usage:
- update_google_sheet("1ABC123", "A1:C10", new_data)  # Update specific range
- update_google_sheet("budget_sheet_id", append_data=[["Jan", 5000, 3000]])  # Add new rows
- update_google_sheet("1XYZ789", "B2", "=SUM(A1:A10)")  # Insert formula

Perfect for: updating reports, adding new data, financial calculations."""
)
def update_google_sheet(
    spreadsheet_id: str,
    range_name: Optional[str] = None,
    data: Optional[List[List[Any]]] = None,
    append_data: Optional[List[List[Any]]] = None,
    formula: Optional[str] = None,
) -> str:
    """
    Update an existing Google Sheet.

    Args:
        spreadsheet_id: ID of the spreadsheet to update
        range_name: Range to update (e.g., 'Sheet1!A1:C10')
        data: New data to insert
        append_data: Data to append at end of sheet
        formula: Formula to insert (use with range_name for single cell)

    Returns:
        Success message with update details
    """
    try:
        sheets_service = _get_sheets_service()

        updates_made = []

        # Regular range update
        if range_name and data:
            body = {"values": data}
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()
            updates_made.append(f"Updated range {range_name} with {len(data)} rows")

        # Formula update
        if range_name and formula:
            body = {"values": [[formula]]}
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()
            updates_made.append(f"Inserted formula in {range_name}")

        # Append data
        if append_data:
            body = {"values": append_data}
            sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="Sheet1",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            ).execute()
            updates_made.append(f"Appended {len(append_data)} rows")

        if not updates_made:
            return "No updates specified. Provide data, append_data, or formula."

        web_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

        return (
            f"Updated Google Sheet successfully!\n\nChanges:\n"
            + "\n".join(f"• {update}" for update in updates_made)
            + f"\n\nLink: {web_link}"
        )

    except Exception as e:
        raise ToolError(f"Error updating Google Sheet: {str(e)}")


@tool(
    description="""List folders and their contents in Google Drive for better organization and navigation.
Helps agents understand the Drive structure and find appropriate locations for files.

Example usage:
- list_drive_folders()  # List root folders
- list_drive_folders("1ABC123")  # List contents of specific folder
- list_drive_folders(parent_id="root", include_files=True)  # Show files too

Perfect for: organizing documents, finding project folders, understanding Drive structure."""
)
def list_drive_folders(
    parent_id: str = "root", include_files: bool = False, max_results: int = 50
) -> str:
    """
    List folders (and optionally files) in Google Drive.

    Args:
        parent_id: ID of parent folder ('root' for Drive root)
        include_files: Whether to include files in listing
        max_results: Maximum number of items to return

    Returns:
        Formatted listing of folders and files
    """
    try:
        service = _get_drive_service()

        # Build query
        if include_files:
            query = f"'{parent_id}' in parents and trashed=false"
        else:
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

        # Get items
        results = (
            service.files()
            .list(
                q=query,
                pageSize=max_results,
                fields="files(id,name,mimeType,modifiedTime,size)",
                orderBy="folder,name",
            )
            .execute()
        )

        items = results.get("files", [])

        if not items:
            return f"No {'items' if include_files else 'folders'} found in specified location."

        # Format output
        parent_name = "Drive Root" if parent_id == "root" else f"Folder {parent_id}"
        output = f"Contents of {parent_name}:\n"
        output += "=" * 50 + "\n\n"

        folders = []
        files = []

        for item in items:
            name = item.get("name", "Unknown")
            item_id = item.get("id", "Unknown")
            mime_type = item.get("mimeType", "")
            modified = item.get("modifiedTime", "Unknown")

            if "folder" in mime_type:
                folders.append(f"📁 {name} (ID: {item_id})")
            else:
                if "document" in mime_type:
                    icon = "📝"
                elif "spreadsheet" in mime_type:
                    icon = "📊"
                elif "presentation" in mime_type:
                    icon = "🎯"
                else:
                    icon = "📄"
                files.append(f"{icon} {name} (ID: {item_id}) - Modified: {modified}")

        # Display folders first
        if folders:
            output += "FOLDERS:\n"
            for folder in folders:
                output += f"  {folder}\n"
            output += "\n"

        if files and include_files:
            output += "FILES:\n"
            for file in files:
                output += f"  {file}\n"

        output += f"\nTotal: {len(folders)} folders"
        if include_files:
            output += f", {len(files)} files"

        return output

    except HttpError as e:
        return f"Google Drive API error: {str(e)}"
    except Exception as e:
        raise ToolError(f"Error listing Drive folders: {str(e)}")
