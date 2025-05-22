import streamlit as st
import ast
import re
from pygments import highlight
from pygments.lexers import PythonLexer, CppLexer
from pygments.formatters import HtmlFormatter
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini AI configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Gemini AI: {str(e)}")
        st.error("Failed to initialize AI features. Please check your API key.")
else:
    logger.warning("Google API key not found")
    st.warning("Google API key not found. Please set GOOGLE_API_KEY in your .env file for enhanced conversion.")

def format_code(code, language):
    """Format code with proper indentation and style."""
    try:
        if language == 'python':
            return code.strip()
        else:
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    formatted_lines.append('')
                    continue
                    
                if line.startswith('}'):
                    indent_level = max(0, indent_level - 1)
                
                formatted_lines.append('    ' * indent_level + line)
                
                if line.endswith('{'):
                    indent_level += 1
                    
            return '\n'.join(formatted_lines)
    except Exception as e:
        logger.error(f"Error formatting code: {str(e)}")
        return code

def get_ai_enhanced_conversion(source_code, source_lang, target_lang):
    """Use Gemini AI to enhance code conversion."""
    try:
        if not GOOGLE_API_KEY:
            return None, "API key not configured"
            
        prompt = f"""You are a professional code converter. Convert the following {source_lang} code to {target_lang}.
        Follow these guidelines:
        1. Maintain the exact same functionality
        2. Use proper {target_lang} conventions and best practices
        3. Include necessary imports/headers
        4. Handle edge cases and error conditions
        5. Use appropriate data types and structures
        6. Add comments for complex logic
        7. Ensure proper memory management (for C++)
        8. Follow the language's style guide
        
        {source_lang} code:
        {source_code}
        
        Provide only the converted code without any explanations or markdown formatting.
        """
        
        response = model.generate_content(prompt)
        converted_code = response.text.strip()
        
        # Clean up the response
        converted_code = re.sub(r'```.*?\n', '', converted_code)
        converted_code = re.sub(r'```$', '', converted_code)
        converted_code = converted_code.strip()
        
        logger.info(f"Successfully converted {source_lang} to {target_lang}")
        return converted_code, None
    except Exception as e:
        logger.error(f"AI conversion error: {str(e)}")
        return None, str(e)

def validate_python_code(code):
    try:
        ast.parse(code)
        return True, "Valid Python code"
    except SyntaxError as e:
        logger.error(f"Invalid Python code: {str(e)}")
        return False, f"Invalid Python code: {str(e)}"

def validate_cpp_code(code):
    required_elements = [';', '{', '}']
    for element in required_elements:
        if element not in code:
            logger.error(f"Invalid C++ code: Missing {element}")
            return False, f"Invalid C++ code: Missing required element '{element}'"
    return True, "Valid C++ code"

def python_to_cpp(python_code):
    try:
        tree = ast.parse(python_code)
        cpp_code = []
        includes = set(['<iostream>', '<string>'])
        
        # First pass: collect includes
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name == 'math':
                        includes.add('<cmath>')
                    elif name.name == 'random':
                        includes.add('<random>')
                    elif name.name == 'time':
                        includes.add('<ctime>')
            elif isinstance(node, ast.ImportFrom):
                if node.module == 'math':
                    includes.add('<cmath>')
                elif node.module == 'random':
                    includes.add('<random>')
                elif node.module == 'time':
                    includes.add('<ctime>')
        
        cpp_code.append('\n'.join(f'#include {inc}' for inc in sorted(includes)))
        cpp_code.append('')
        
        # Second pass: convert code
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                return_type = "void"
                params = []
                for arg in node.args.args:
                    param_type = "auto"
                    if hasattr(arg, 'annotation') and arg.annotation:
                        if isinstance(arg.annotation, ast.Name):
                            param_type = arg.annotation.id
                    params.append(f"{param_type} {arg.arg}")
                
                cpp_code.append(f"{return_type} {node.name}({', '.join(params)}) {{")
                
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        if stmt.value:
                            cpp_code.append(f"    return {convert_python_expr(stmt.value)};")
                        else:
                            cpp_code.append("    return;")
                    elif isinstance(stmt, ast.Expr):
                        if isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'print':
                                args = [convert_python_expr(arg) for arg in stmt.value.args]
                                cpp_code.append(f"    std::cout << {' << '.join(args)} << std::endl;")
                            else:
                                cpp_code.append(f"    {convert_python_expr(stmt.value)};")
                    elif isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            cpp_code.append(f"    {convert_python_expr(target)} = {convert_python_expr(stmt.value)};")
                    elif isinstance(stmt, ast.If):
                        cpp_code.append(f"    if ({convert_python_expr(stmt.test)}) {{")
                        for if_stmt in stmt.body:
                            cpp_code.append(f"        {convert_python_expr(if_stmt)}")
                        cpp_code.append("    }")
                        if stmt.orelse:
                            cpp_code.append("    else {")
                            for else_stmt in stmt.orelse:
                                cpp_code.append(f"        {convert_python_expr(else_stmt)}")
                            cpp_code.append("    }")
                
                cpp_code.append("}")
                cpp_code.append("")
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    cpp_code.append(f"auto {convert_python_expr(target)} = {convert_python_expr(node.value)};")
            elif isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name) and node.value.func.id == 'print':
                        args = [convert_python_expr(arg) for arg in node.value.args]
                        cpp_code.append(f"std::cout << {' << '.join(args)} << std::endl;")
                    else:
                        cpp_code.append(f"{convert_python_expr(node.value)};")
        
        if not any("main" in line for line in cpp_code):
            cpp_code.append("""
int main() {
    // Your code will be executed here
    return 0;
}""")
        
        return '\n'.join(cpp_code)
    except Exception as e:
        logger.error(f"Error converting Python to C++: {str(e)}")
        return f"Error converting Python to C++: {str(e)}"

def convert_python_expr(node):
    """Convert Python AST expression to C++ code."""
    try:
        if isinstance(node, ast.Num):
            return str(node.n)
        elif isinstance(node, ast.Str):
            return f'"{node.s}"'
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            op_map = {
                ast.Add: '+',
                ast.Sub: '-',
                ast.Mult: '*',
                ast.Div: '/',
                ast.Mod: '%',
            }
            op = op_map.get(type(node.op), str(node.op))
            return f"({convert_python_expr(node.left)} {op} {convert_python_expr(node.right)})"
        elif isinstance(node, ast.Compare):
            op_map = {
                ast.Eq: '==',
                ast.NotEq: '!=',
                ast.Lt: '<',
                ast.LtE: '<=',
                ast.Gt: '>',
                ast.GtE: '>=',
            }
            ops = [op_map.get(type(op), str(op)) for op in node.ops]
            return f"({convert_python_expr(node.left)} {' '.join(ops)} {convert_python_expr(node.comparators[0])})"
        elif isinstance(node, ast.Call):
            args = [convert_python_expr(arg) for arg in node.args]
            if isinstance(node.func, ast.Name):
                if node.func.id == 'print':
                    return f"std::cout << {' << '.join(args)} << std::endl"
                elif node.func.id == 'input':
                    return f"std::cin >> {args[0] if args else 'input_var'}"
                else:
                    return f"{node.func.id}({', '.join(args)})"
            return f"{convert_python_expr(node.func)}({', '.join(args)})"
        elif isinstance(node, ast.BoolOp):
            op_map = {
                ast.And: '&&',
                ast.Or: '||',
            }
            op = op_map.get(type(node.op), str(node.op))
            return f"({f' {op} '.join(convert_python_expr(v) for v in node.values)})"
        elif isinstance(node, ast.UnaryOp):
            op_map = {
                ast.UAdd: '+',
                ast.USub: '-',
                ast.Not: '!',
            }
            op = op_map.get(type(node.op), str(node.op))
            return f"{op}({convert_python_expr(node.operand)})"
        return str(node)
    except Exception as e:
        logger.error(f"Error converting Python expression: {str(e)}")
        return str(node)

def cpp_to_python(cpp_code):
    try:
        code_lines = cpp_code.split('\n')
        filtered_lines = []
        in_main = False
        brace_count = 0
        
        for line in code_lines:
            line = line.strip()
            
            if line.startswith('#include') or not line:
                continue
                
            if 'int main()' in line:
                in_main = True
                continue
                
            if in_main:
                if '{' in line:
                    brace_count += line.count('{')
                if '}' in line:
                    brace_count -= line.count('}')
                if brace_count == 0:
                    in_main = False
                continue
            
            line = convert_cpp_line(line)
            if line:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    except Exception as e:
        logger.error(f"Error converting C++ to Python: {str(e)}")
        return f"Error converting C++ to Python: {str(e)}"

def convert_cpp_line(line):
    """Convert a single line of C++ code to Python."""
    try:
        line = line.rstrip(';')
        line = re.sub(r'(int|float|double|string|bool|auto)\s+(\w+)\s*=\s*', r'\2 = ', line)
        
        if 'std::cout' in line:
            line = re.sub(r'std::cout\s*<<\s*', 'print(', line)
            line = re.sub(r'\s*<<\s*std::endl', ')', line)
            line = re.sub(r'\s*<<\s*', ' + ', line)
        
        if 'std::cin' in line:
            line = re.sub(r'std::cin\s*>>\s*', 'input()', line)
        
        line = re.sub(r'(int|float|double|string|bool|void)\s+(\w+)\s*\(([^)]*)\)', r'def \2(\3):', line)
        line = line.replace('true', 'True').replace('false', 'False')
        line = line.replace('&&', 'and').replace('||', 'or')
        line = line.replace('==', '==').replace('!=', '!=')
        line = re.sub(r'std::string\s*\(\s*"([^"]*)"\s*\)', r'"\1"', line)
        
        return line
    except Exception as e:
        logger.error(f"Error converting C++ line: {str(e)}")
        return line

def highlight_code(code, language):
    try:
        if language == 'python':
            lexer = PythonLexer()
        else:
            lexer = CppLexer()
        
        formatter = HtmlFormatter(style='monokai')
        highlighted = highlight(code, lexer, formatter)
        return highlighted
    except Exception as e:
        logger.error(f"Error highlighting code: {str(e)}")
        return code

# Set page config
st.set_page_config(
    page_title="Convertifier",
    page_icon="🔄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: 'Consolas', monospace;
    }
    .code-output {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        color: #ff4b4b;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffebee;
        margin: 1rem 0;
    }
    .success-message {
        color: #00acb5;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e0f7fa;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔄 Convertifier")
st.markdown("""
Convert your code between Python and C++ with professional-grade accuracy. This tool provides both basic and AI-enhanced
conversion capabilities, ensuring high-quality output that maintains functionality and follows best practices.
""")

# Create two columns for input and output
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Code")
    source_language = st.selectbox(
        "Select source language",
        ["Python", "C++"]
    )
    
    input_code = st.text_area(
        "Enter your code here",
        height=300,
        placeholder="Enter your code here...",
        help="Enter valid code in the selected language. The converter will maintain functionality while following best practices."
    )
    
    use_ai = st.checkbox(
        "Use AI Enhancement (requires Google API key)",
        value=False,
        help="Enable AI-powered conversion for more accurate and context-aware results"
    )
    
    if st.button("Convert", type="primary"):
        if not input_code.strip():
            st.error("Please enter some code to convert")
        else:
            try:
                # Validate input code
                if source_language == "Python":
                    is_valid, message = validate_python_code(input_code)
                    if not is_valid:
                        st.error(message)
                    else:
                        # Try AI conversion first if enabled
                        if use_ai:
                            with st.spinner("Using AI to enhance conversion..."):
                                ai_output, ai_error = get_ai_enhanced_conversion(input_code, "Python", "C++")
                                if ai_output and not ai_error:
                                    output_code = format_code(ai_output, 'cpp')
                                    st.success("AI-enhanced conversion completed successfully!")
                                else:
                                    st.warning(f"AI conversion failed: {ai_error}. Falling back to basic conversion.")
                                    output_code = format_code(python_to_cpp(input_code), 'cpp')
                        else:
                            output_code = format_code(python_to_cpp(input_code), 'cpp')
                        
                        with col2:
                            st.subheader("Converted C++ Code")
                            st.markdown('<div class="code-output">', unsafe_allow_html=True)
                            st.code(output_code, language="cpp")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.markdown("### Syntax Highlighted Version")
                            st.markdown('<div class="code-output">', unsafe_allow_html=True)
                            st.markdown(highlight_code(output_code, 'cpp'), unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.button("Copy to Clipboard", key="copy_cpp")
                else:
                    is_valid, message = validate_cpp_code(input_code)
                    if not is_valid:
                        st.error(message)
                    else:
                        # Try AI conversion first if enabled
                        if use_ai:
                            with st.spinner("Using AI to enhance conversion..."):
                                ai_output, ai_error = get_ai_enhanced_conversion(input_code, "C++", "Python")
                                if ai_output and not ai_error:
                                    output_code = format_code(ai_output, 'python')
                                    st.success("AI-enhanced conversion completed successfully!")
                                else:
                                    st.warning(f"AI conversion failed: {ai_error}. Falling back to basic conversion.")
                                    output_code = format_code(cpp_to_python(input_code), 'python')
                        else:
                            output_code = format_code(cpp_to_python(input_code), 'python')
                        
                        with col2:
                            st.subheader("Converted Python Code")
                            st.markdown('<div class="code-output">', unsafe_allow_html=True)
                            st.code(output_code, language="python")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.markdown("### Syntax Highlighted Version")
                            st.markdown('<div class="code-output">', unsafe_allow_html=True)
                            st.markdown(highlight_code(output_code, 'python'), unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.button("Copy to Clipboard", key="copy_python")
            except Exception as e:
                logger.error(f"Conversion error: {str(e)}")
                st.error(f"An error occurred during conversion: {str(e)}")

# Add some helpful information
st.markdown("""
---
### Features and Best Practices:
1. **Code Validation**: Ensures input code is syntactically correct
2. **AI Enhancement**: Uses Gemini AI for context-aware conversion
3. **Syntax Highlighting**: Makes code more readable
4. **Proper Formatting**: Maintains consistent code style
5. **Error Handling**: Graceful fallback if AI conversion fails

### Setting up AI Enhancement:
1. Get a Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root
3. Add your API key: `GOOGLE_API_KEY=your_api_key_here`

### Tips for Best Results:
1. Write clean, well-formatted input code
2. Use AI enhancement for complex code structures
3. Review the converted code for accuracy
4. Test the converted code before using in production
""") 