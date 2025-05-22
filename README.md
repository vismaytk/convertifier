# Convertifier 🔄

A professional-grade code converter that transforms code between Python and C++ with high accuracy. Built with Streamlit and powered by Google's Gemini AI.

## 🌟 Features

- **Bidirectional Conversion**: Convert between Python and C++ seamlessly
- **AI Enhancement**: Powered by Google's Gemini AI for context-aware conversion
- **Syntax Validation**: Ensures input code is syntactically correct
- **Code Formatting**: Maintains consistent code style and indentation
- **Syntax Highlighting**: Makes code more readable with proper highlighting
- **Error Handling**: Graceful fallback if AI conversion fails
- **User-Friendly Interface**: Clean and intuitive UI

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/convertifier.git
   cd convertifier
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/MacOS
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## 🛠️ Usage

1. Select the source language (Python or C++)
2. Enter your code in the input text area
3. (Optional) Enable AI enhancement for better results
4. Click "Convert" to see the converted code
5. Review and copy the converted code

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google API key for Gemini AI (required for AI enhancement)

### Dependencies

- Python 3.7+
- Streamlit
- Pygments
- Google Generative AI
- python-dotenv

## 📝 Example

### Python to C++

Input (Python):
```python
def calculate_sum(a: int, b: int) -> int:
    if a > 0 and b > 0:
        return a + b
    return 0

print(calculate_sum(5, 3))
```

Output (C++):
```cpp
#include <iostream>
#include <string>

int calculate_sum(int a, int b) {
    if ((a > 0) && (b > 0)) {
        return (a + b);
    }
    return 0;
}

int main() {
    std::cout << calculate_sum(5, 3) << std::endl;
    return 0;
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework
- [Google Gemini AI](https://deepmind.google/technologies/gemini/) for AI enhancement
- [Pygments](https://pygments.org/) for syntax highlighting

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/convertifier/issues). 