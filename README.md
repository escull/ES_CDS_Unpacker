# CDS Unpacker

This repository contains a Python script (`cds_unpacker.py`) designed to extract and parse telemetry data from `.cds` files. These files are often diagnostic logs containing multiple GZIP-compressed JSON data frames. The script provides a graphical user interface (GUI) to easily select a `.cds` file, process it, and export the extracted sensor readings into a structured CSV file.

## Features

-   **GZIP Stream Extraction**: Identifies and decompresses multiple GZIP streams embedded within a single binary file.
-   **JSON Telemetry Parsing**: Parses the decompressed data, expecting JSON objects containing sensor readings.
-   **CSV Export**: Organizes the extracted sensor names and values into a comprehensive CSV file, with each row representing a data frame.
-   **User-Friendly GUI**: A simple Tkinter-based interface for file selection and process monitoring.
-   **Robust Error Handling**: Gracefully handles corrupted or incomplete GZIP streams and malformed JSON data, common in live logging scenarios.
-   **Asynchronous Processing**: Uses threading to prevent the GUI from freezing during file processing.

## Requirements

-   Python 3.x
-   `zlib` (standard library)
-   `json` (standard library)
-   `csv` (standard library)
-   `os` (standard library)
-   `tkinter` (standard library, usually included with Python installations)
-   `threading` (standard library)

No external `pip` packages are required.

## How to Use

1.  **Clone the repository (or download `cds_unpacker.py`):**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
    (Replace `your-username` and `your-repo-name` with your actual GitHub details.)

2.  **Run the script:**
    ```bash
    python cds_unpacker.py
    ```

3.  **Using the GUI:**
    *   Click the "Open File" button to select your `.cds` file.
    *   Once a file is selected, the "Process" button will become active. Click it to start the extraction.
    *   The log area will display the progress and any messages.
    *   Upon successful completion, a CSV file with the same name as your input file will be created in the same directory as the input file.

## Example Output

If your input file is `example.cds`, the script will generate `example.csv` containing columns for each unique sensor found across all data frames, and rows representing the values for each frame.

## Contribution

Feel free to fork the repository, open issues, or submit pull requests.