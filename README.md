# Code Converter

A Streamlit-based web application that converts code between Python and C++. This tool helps you translate basic code structures between the two languages.

## Features

- Convert Python code to C++
- Convert C++ code to Python
- Syntax validation for both languages
- Syntax highlighting for better readability
- User-friendly interface

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone this repository
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. The application will open in your default web browser

## Usage

1. Select the source language (Python or C++)
2. Enter your code in the input text area
3. Click the "Convert" button
4. View the converted code in the output area

## Limitations

- This is a simplified converter and may not handle all complex code structures
- Some language-specific features may not be perfectly translated
- Always review the converted code before using it in production

## Contributing

Feel free to submit issues and enhancement requests! 