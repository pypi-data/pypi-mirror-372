# chinese README in here:

[README_ZH.md](https://github.com/kkjzio/mcp-quiz-generator/blob/master/README_ZH.md)



# MCP Quiz Generator

A quiz generator server based on Model Context Protocol (MCP) that generates Markdown questions according to requirements and converts them into HTML and Word format quiz files.

## Features

- 🎯 Support for multiple question types: single choice, multiple choice, true/false, short answer
- 📄 Generate interactive HTML quiz files
- 📝 Generate Word format quiz files (including answer key and student versions)
- 🔧 Based on MCP protocol, integrates with editors like Cursor, VSCode
- ⚡ Fast dependency management using uv

## Supported Question Formats

### Single Choice Questions
```markdown
1. Which testing automation frameworks has MaxSoft developed?
    - [x] IntelliAPI  (Correct answer marked with [x])
    - [ ] WebBot      (Incorrect answer marked with [ ])
    - [ ] Gauge
    - [ ] Selenium
```

### Multiple Choice Questions
```markdown
2. Which testing automation frameworks has MaxSoft developed?
    - [x] IntelliAPI  (Multiple correct answers all marked with [x])
    - [x] WebBot      
    - [ ] Gauge       (Incorrect answer marked with [ ])
    - [ ] Selenium
```

### True/False Questions
```markdown
3. MaxSoft is a software company.
    - (x) True        (Correct answer marked with (x))
    - ( ) False       (Incorrect answer marked with ( ))
```

### Short Answer Questions
```markdown
4. Who is the co-founder of MaxSoft?
    - R:= Osanda      (Answer marked with R:= followed by correct answer)
```

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Configuring MCP in Cursor/VSCode

### Method 1: Using uvx (Recommended)

1. **Create MCP configuration file**:

   In Cursor/VSCode, open MCP settings and add the following configuration:

   ```json
   {
     "mcpServers": {
       "mcp-quiz-generator": {
         "command": "uvx",
         "args": ["mcp-quiz-generator" , "--output-folder" , "{output-folder-path}"]
       }
     }
   }
   ```
   

**Note**: Replace `{output-folder-path}` with the storage path for generated files.

### Method 2: Using Python directly

1. **First ensure dependencies are installed**:
   ```bash
   uv sync
   ```

2. **Add to MCP configuration**:
   ```json
   {
     "mcpServers": {
       "mcp-quiz-generator": {
         "command": "/path/to/mcp-quiz-generator/.venv/bin/python",
         "args": ["run", "mcp-quiz-generator" , "--output-folder" , "{output-folder-path}"]
       }
     }
   }
   ```

**Note**: Replace `{output-folder-path}` with the storage path for generated files.

### Tool Parameters

- `markdown_content`: Quiz content in Markdown format
- `format_type`: Output format
  - `"html"`: Generate HTML file only
  - `"word"`: Generate Word file only
  - `"both"`: Generate both HTML and Word files (default)
- `custom_filename`: Custom filename (optional, without extension)

## Output Files

If the `--output-folder` parameter is not used, generated files will be saved in the `data/` directory by default:

- **HTML file**: Interactive quiz with online answering support

- ![image-20250826102712411](README.assets/image-20250826102712411.png)

- **Word files**:

   ![image-20250826102752443](README.assets/image-20250826102752443.png)

- 
  
  - `*_quiz.docx`: Student version (without answers)
  - `*_answer_key.docx`: Teacher version (with answers and markings)

### Project Structure

```
mcp-quiz-generator/
├── src/
│   └── quiz_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server main file
│       └── app/               # Application module directory
│           ├── extensions/    # Markdown extensions
│           └── static/        # Static resource files
├── data/                      # Output file directory (default)
├── pyproject.toml            # Project configuration
├── uv.lock                   # Dependency lock file
└── README.md                 # Project documentation
```

## Troubleshooting

### Common Issues

1. **uv command not found**
   - Ensure uv is properly installed and added to PATH
   - Restart terminal or editor

2. **MCP server connection failed**
   - Check if paths in configuration file are correct
   - Ensure virtual environment is created: `uv sync`
   - Check editor's MCP logs for detailed error information

3. **Generated file format is incorrect**
   - Check if Markdown content follows specified format
   - Ensure options have correct indentation (4 spaces)

### --output-folder Parameter Description

The `--output-folder` parameter is used to specify the output directory for generated quiz files.

**Syntax**:
```bash
uv run mcp-quiz-generator --output-folder <directory-path>
```

**Parameter Description**:
- `<directory-path>`: Specifies the directory path for output files
- Default value: `data` (if this parameter is not specified, files will be saved to `data/` directory)
- If the specified directory doesn't exist, the program will create it automatically

**Usage Examples**:
```bash
# Use default output directory (data/)
uv run mcp-quiz-generator

# Specify custom output directory
uv run mcp-quiz-generator --output-folder ./my_quizzes

# Specify absolute path
uv run mcp-quiz-generator --output-folder /home/user/quiz_files

# Specify relative path
uv run mcp-quiz-generator --output-folder ../output
```

## Usage Example

### Complete Conversation Example: Generating Prompt Engineering Quiz

Here's a complete usage example showing how to generate a quiz about Prompt Engineering through an AI assistant:

**User Question**:
```
Q: give me some quiz about Prompt Engineering then generate word and html file
```

**AI Assistant Response**:
```
Of course, I can generate a quiz about Prompt Engineering for you. Here are a few questions. I will then use a tool to generate the Word and HTML files.

Here is the quiz content:

#### Single Choice Questions

1. What is a core principle of prompt engineering?
   -  Using the shortest prompt possible.
   -  Providing clear and specific instructions.
   -  Using complex vocabulary.
   -  Always asking for a single-word answer.

#### Multiple Choice Questions

1. Which of the following are common prompt engineering techniques?
   -  Zero-shot prompting
   -  Few-shot prompting
   -  Chain-of-thought prompting
   -  Random word generation

#### True/False Questions

1. "Few-shot prompting" involves giving the model several examples before asking the final question.
   - (x) True
   - ( ) False

#### Short Answer Questions

1. What technique encourages a model to explain its reasoning step-by-step before giving a final answer?
   - R:= Chain-of-thought prompting

Now, let me generate the files for you.

(mcp-quiz-generator : generate_quiz completed)

I have generated the quiz files for you in both Word and HTML formats. Here are the files that have been created:

- **HTML (Interactive Quiz):** `{output-folder-path}\Prompt_Engineering_Quiz.html`
- **Word (Quiz for students):** `{output-folder-path}\Prompt_Engineering_Quiz_quiz.docx`
- **Word (Answer Key):** `{output-folder-path}\Prompt_Engineering_Quiz_answer_key.docx`

Let me know if you need anything else
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Reference

https://github.com/osandadeshan/markdown-quiz-generator

## Changelog

### v0.1.0
- Initial release
- Support for basic quiz generation functionality
- Support for HTML and Word format output
- MCP protocol integration

### v0.1.1
 - Fix missing files from the app folder in the package