

import pandas as pd
import json
import re

class SheetsManager:
    # Class-level variables to store the URL and sheet data
    sheet_url = ""
    sheet_data = {}

    """
    A class to manage and load Google Sheets data from all tabs.

    Attributes:
        sheet_url (str): The URL of the Google Sheet.
        sheet_data (dict): A dictionary to store the data loaded from all tabs.
    """

    @staticmethod
    def init(sheet_identifier: str, force_string=False):
        """
        Initialize the SheetsManager with a Google Sheet ID, URL, or file path.

        This method accepts:
        - A Google Sheet ID
        - A Google Sheets URL (will extract the ID)
        - Any other URL or file path that points to an Excel/CSV file

        Args:
            sheet_identifier (str): The ID of the Google Sheet, Google Sheets URL, or any other URL/file path.
            force_string (bool): If True, forces all data to be loaded as strings.
        """
        # Check if the input is a URL or file path
        if sheet_identifier.startswith(('http://', 'https://', 'file://', '/', './', '../')):
            # It's a URL or file path - use it directly
            SheetsManager.sheet_url = sheet_identifier
        else:
            # Assume it's a Google Sheet ID - construct the Google Sheets URL
            SheetsManager.sheet_url = f"https://docs.google.com/spreadsheets/d/e/{sheet_identifier}/pub?output=xlsx"
            
        SheetsManager.force_string = force_string
        SheetsManager.reload()

    @staticmethod
    def _extract_sheet_id_from_url(url: str) -> str:
        """
        Extract the sheet ID from a Google Sheets URL.
        
        Args:
            url (str): The Google Sheets URL.
            
        Returns:
            str: The extracted sheet ID.
            
        Raises:
            ValueError: If the URL format is not recognized.
        """
        # Pattern to match Google Sheets URL and extract the ID
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',  # Standard format
            r'/spreadsheets/d/e/([a-zA-Z0-9-_]+)',  # Published format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Could not extract sheet ID from the provided URL. Please check the URL format.")

    @staticmethod
    def reload():
        """
        Load data from all tabs in the Google Sheet.

        This method fetches the data from the Google Sheets URL and loads all tabs into 
        a dictionary. Each key in the dictionary corresponds to a tab name, and the 
        value is a list of records in JSON format.

        Raises:
            ValueError: If there is an issue loading the data (e.g., network issues, wrong URL).
        """
        try:
            xls = pd.ExcelFile(SheetsManager.sheet_url)
            data = {}
            
            for sheet_name in xls.sheet_names:
                rows_data = pd.read_excel(xls, sheet_name, dtype="string" if SheetsManager.force_string else None)
                rows_data = json.loads(rows_data.to_json(orient='records'))
                
                data[sheet_name] = rows_data
                
            SheetsManager.sheet_data = data
        
        except Exception as e:
            raise ValueError(f"Error loading data from spreadsheet: {e}")


