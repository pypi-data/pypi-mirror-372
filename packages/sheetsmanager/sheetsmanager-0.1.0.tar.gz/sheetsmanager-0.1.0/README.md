# Sheets Manager

**Sheets Manager** is a lightweight Python package designed for loading and managing data from Google Sheets, fetching data from all tabs within the file. This package provides a simple interface for accessing and storing tabular data in JSON format.

---

## Features

- **Load All Tabs**: Fetch data from all tabs within a spreadsheet automatically.
- **Easy to Use**: Minimal setup to integrate into your projects.
- **Lightweight**: No unnecessary dependencies—uses only `pandas` and `json`.

---

## Installation

You can install **Sheets Manager** via pip:

```bash
pip install sheetsmanager
```

---

## Usage

### Initializing the Manager

```python
from sheetsmanager import SheetsManager

# Initialize the SheetsManager with your Google Sheet ID
sheet_id = "your_google_sheet_id"
SheetsManager.init(sheet_id)
```

The `SheetsManager` will automatically load all data from all tabs in the spreadsheet upon initialization. **Note**: The `sheet_data` and `sheet_url` variables are static, meaning they are shared across all instances of the `SheetsManager` class.

### Accessing the Loaded Data

```python
# Access the loaded data as a dictionary
print(SheetsManager.sheet_data)  # Dictionary where keys are tab names and values are the tab data
```

Since `sheet_data` is a static variable, it will store the data globally, allowing all references to `SheetsManager` to access the same data.

### Reloading the Data

If you want to reload the data from the Google Sheet and update all stored data, you can call the `reload()` method:

```python
# Reload data from the spreadsheet
SheetsManager.reload()
```

This will refresh the `sheet_data` dictionary with the latest data from all tabs. The `sheet_data` variable is static, so any update will affect all instances that reference it.

---

## Parameters

### `force_string` (optional)

- **Type**: `bool`
- **Default**: `False`
- **Description**: Forces all values to be returned as strings when loading data. If `force_string=True`, numerical values will be stored as strings.

#### Example Usage:

```python
# Example usage with force_string
SheetsManager.init(sheet_id, force_string=True)
```

This ensures that all values remain in string format, which can be useful for preserving formatting from Google Sheets.

---

## Getting the Sheet ID and Generating the URL

To use a Google Sheet with this package, you need the **Sheet ID**. Follow these steps:

### Step 1: Open the Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/) and open your spreadsheet.

### Step 2: Retrieve the Sheet ID from the Publish to Web Dialog

1. Click on `File` in the top menu.
2. Select `Share` > `Publish to the web`.
3. In the dialog that opens, you will see the **Sheet ID** in the generated URL. It looks like this:
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/pub?output=xlsx
   ```
4. Copy the part between `/d/` and `/pub`—this is your **Sheet ID**.

### Step 3: Publish the Google Sheet

1. In the same dialog, choose:
   - **Entire Document**: To make all tabs available.
   - **Microsoft Excel (.xlsx)** as the file format.
2. Click `Publish` and confirm your choice.

### Important Warning

- **Public Access**: Publishing makes the spreadsheet accessible to anyone with the link.
- **Read-Only**: Others can download the file but cannot directly edit it.

---

## Requirements

- Python 3.7+
- pandas

---

## Contributing

Contributions are welcome! If you encounter bugs, have feature requests, or want to contribute code, feel free to submit issues and pull requests on GitHub.

---

## License

**Sheets Manager** is licensed under the MIT License. See the LICENSE file for more details.
