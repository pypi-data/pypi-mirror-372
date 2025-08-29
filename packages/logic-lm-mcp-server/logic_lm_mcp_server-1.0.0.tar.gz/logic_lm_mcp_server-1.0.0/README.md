# Logic-LM MCP Server

A Model Context Protocol (MCP) server that provides symbolic reasoning capabilities using Logic-LM framework and Answer Set Programming (ASP).

## Attribution

This implementation is inspired by and builds upon the Logic-LLM framework:

**Original Research:**
- **Paper:** [Logic-LLM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning](https://arxiv.org/abs/2305.12295)
- **Repository:** [teacherpeterpan/Logic-LLM](https://github.com/teacherpeterpan/Logic-LLM)
- **Authors:** Liangming Pan, Alon Albalak, Xinyi Wang, William Yang Wang

This MCP server adapts the Logic-LLM approach for integration with Claude Code and other MCP clients, providing LLM-collaborative symbolic reasoning through Answer Set Programming.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher

### Installation

Choose your preferred installation method:

#### Option 1: Install from PyPI (Recommended) ✅ **LIVE ON PYPI**
```bash
# Install with pip
pip install logic-lm-mcp-server

# Or install with uv (10-100x faster)
uv pip install logic-lm-mcp-server
```

📦 **Package URL:** https://pypi.org/project/logic-lm-mcp-server/

#### Option 2: Install with Clingo solver (for full functionality)
```bash
# Install with optional solver
pip install logic-lm-mcp-server[solver]

# Or with uv
uv pip install logic-lm-mcp-server[solver]
```

#### Option 3: Development Installation
```bash
git clone https://github.com/stevenwangbe/logic-lm-mcp-server.git
cd logic-lm-mcp-server
pip install -e .
```

### Test Installation
```bash
logic-lm-mcp --help
```

### Integration with Claude Code

After installing the package, add it to your Claude Code configuration:

**Method 1: Using the console command (after PyPI installation)**
```bash
claude mcp add logic-lm-mcp logic-lm-mcp
```

**Method 2: Manual configuration**

Edit `~/.config/claude/claude_desktop_config.json` (create if it doesn't exist):

```json
{
  "mcpServers": {
    "logic-lm": {
      "command": "logic-lm-mcp"
    }
  }
}
```

**Restart Claude Code** to load the new MCP server.

3. **Test the integration:**

Try these commands in Claude Code:
```
Check Logic-LM server health
Translate this logic problem to ASP: "All birds can fly. Penguins are birds. Can penguins fly?"
```

### Alternative Integration (Other MCP Clients)

For other MCP-compatible tools, start the server manually:
```bash
python start_server.py
```

The server will run on stdio and provide these tools:
- `get_asp_guidelines` - Get ASP translation guidelines
- `translate_to_asp_instructions` - Get problem-specific ASP guidance
- `verify_asp_program` - Execute ASP programs with Clingo
- `check_solver_health` - Verify system health

## Overview

Logic-LM MCP Server converts natural language logical problems into Answer Set Programming (ASP) format, solves them using the Clingo solver, and returns human-readable results. It provides a three-stage reasoning pipeline: Problem Formulation → Symbolic Reasoning → Result Interpretation.

## Features

- **Natural Language Input**: Convert English logical problems to formal representations
- **ASP-Based Reasoning**: Uses Answer Set Programming for robust logical inference
- **Clingo Integration**: Leverages the Clingo ASP solver for symbolic reasoning
- **Self-Refinement**: Iterative improvement of solutions through multiple reasoning passes
- **Template Library**: Reusable ASP patterns for common logical structures
- **Fallback Handling**: Graceful degradation when solver components unavailable
- **FastMCP Integration**: Modern MCP server implementation with type safety

## Tools Provided

### 1. `get_asp_guidelines`
Get comprehensive ASP translation guidelines (cached for efficiency).

**Parameters:** None

**Returns:** Complete ASP Logic Translation Guidelines document with comprehensive instructions for translating natural language into Answer Set Programming format.

### 2. `translate_to_asp_instructions`  
Get lightweight instructions for translating a specific natural language problem to ASP.

**Parameters:**
- `problem` (string, required): Natural language logical problem to translate

**Example:**
```json
{
  "problem": "All cats are mammals. Fluffy is a cat. Is Fluffy a mammal?"
}
```

**Response:**
```json
{
  "success": true,
  "solution": "TRANSLATE TO ASP: All cats are mammals...\n\nINSTRUCTIONS:\n1. Call get_asp_guidelines() for complete patterns\n2. Analyze logical structure...",
  "confidence": 1.0,
  "method": "lightweight_translation_instructions",
  "metadata": {
    "problem_length": 58,
    "guidelines_cached": false,
    "next_steps": ["Call get_asp_guidelines() if needed", "Generate ASP code", "Call verify_asp_program()"]
  }
}
```

### 3. `verify_asp_program`
Directly verify and solve an ASP program using the Clingo solver.

**Parameters:**
- `program` (string, required): ASP program code to verify and solve
- `max_models` (integer, 1-100, default: 10): Maximum number of models to find

**Example:**
```json
{
  "program": "% Facts\ncat(fluffy).\n\n% Rule: All cats are mammals\nmammal(X) :- cat(X).\n\n% Query\n#show mammal/1.",
  "max_models": 10
}
```

### 4. `check_solver_health`
Check Logic-LM server and Clingo solver health status.

**Returns:**
- Server status and component initialization status
- Clingo availability and version information
- System capabilities and configuration details
- Basic functionality test results

## Architecture

### Core Components

1. **LogicFramework**: Main reasoning orchestrator
2. **ClingoSolver**: ASP solver interface and management  
3. **ASPTemplateLibrary**: Reusable logical pattern templates
4. **FastMCP Integration**: Modern MCP server implementation

### Processing Pipeline

```
Natural Language Input
         ↓
LLM Translation Instructions (Problem-specific guidance)
         ↓  
ASP Program Generation (LLM-driven with guidelines)
         ↓
Clingo Solver Execution
         ↓
Model Interpretation (Symbolic results)
         ↓
Human-Readable Output
```

## Dependencies

- **Python 3.8+**: Core runtime environment
- **FastMCP 2.0+**: Modern MCP server framework
- **Pydantic 2.0+**: Input validation and type safety
- **Clingo 5.8.0+**: ASP solver (automatically detects if missing)

## Installation

### Option 1: Using pip
```bash
pip install -r requirements.txt
```

### Option 2: Manual installation
```bash
pip install fastmcp>=2.0.0 pydantic>=2.0.0 clingo>=5.8.0
```

### Option 3: Development setup
```bash
git clone <repository-url>
cd logic-lm-mcp-server
pip install -e .
```

## Configuration

The server automatically handles:
- Clingo solver installation detection
- Template library loading
- Environment-specific optimizations
- Error recovery and fallback modes

### Environment Variables
- No environment variables required
- Server runs with sensible defaults

## Usage Examples

### Basic Logical Reasoning
```
Input: "If it's raining, then the ground is wet. It's raining. Is the ground wet?"
Output: "Yes, the ground is wet. This conclusion follows from modus ponens..."
```

### Syllogistic Reasoning  
```
Input: "All birds can fly. Penguins are birds. Can penguins fly?"
Output: "Based on the given premises, yes. However, this conflicts with real-world knowledge..."
```

### Set-Based Logic
```
Input: "All members of set A are in set B. X is in set A. Is X in set B?"
Output: "Yes, X is in set B. This follows from set inclusion transitivity..."
```

## Testing

### Basic Functionality Test
```bash
python test_basic.py
```

### Full Setup Test (if MCP dependencies available)
```bash
python test_setup.py
```

## Error Handling

- **Clingo Unavailable**: Provides informative error messages with installation guidance
- **Invalid ASP Programs**: Syntax checking with detailed error messages  
- **Solver Timeouts**: Graceful handling of complex problems
- **Resource Constraints**: Memory and time limit management

## Performance

- **Simple Problems**: 50-200ms response time
- **Complex Reasoning**: 200-1000ms with self-refinement
- **Memory Usage**: ~25MB base + ~1MB per concurrent request
- **Concurrent Support**: Multiple simultaneous reasoning requests

## Troubleshooting

### Common Issues

1. **"No module named 'pydantic'" or similar**
   - Install dependencies: `pip install -r requirements.txt`

2. **"Clingo not available"**
   - Install Clingo: `pip install clingo`
   - Server will run with limited functionality if Clingo is missing

3. **Server fails to start**
   - Check Python version: `python --version` (requires 3.8+)
   - Run basic test: `python test_basic.py`

4. **MCP connection issues**
   - Ensure you're running the correct startup script: `python start_server.py`
   - Check that no other process is using the same port

### Getting Help

1. Run the basic test to isolate issues: `python test_basic.py`
2. Check the health endpoint: use `check_solver_health` tool
3. Enable debug traces: set `include_trace=true` in requests

## FAQ - Common Setup Errors

### "Missing required dependencies" on startup

**Error:**
```
❌ Missing required dependencies:
  - fastmcp>=2.0.0
  - pydantic>=2.0.0
```

**Cause:** Dependencies not properly installed or virtual environment not activated.

**Solution:**
```bash
# Option 1: Use virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 2: Install globally
pip install -r requirements.txt

# Option 3: Use venv python directly
venv/bin/python start_server.py
```

### "ModuleNotFoundError: No module named 'fastmcp'"

**Error:**
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'fastmcp'
```

**Cause:** Virtual environment not properly activated or dependencies not installed.

**Solution:**
```bash
# Clean installation
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'pydantic'"

**Error:**
```
ModuleNotFoundError: No module named 'pydantic'
```

**Cause:** Missing core dependency, often from incomplete installation.

**Solution:**
```bash
pip install pydantic>=2.0.0
# Or reinstall all dependencies
pip install -r requirements.txt
```

### Virtual environment using system Python instead of venv Python

**Error:** Virtual environment is using the system Python instead of the isolated venv Python.

**Symptoms:**
- Packages installed globally instead of in venv
- Permission errors during package installation
- `which python` shows system path after activation
- Inconsistent behavior between development and production

**Causes:**
- Incorrect virtual environment activation
- Shell aliases overriding PATH (alias python, alias python3)
- Corrupted virtual environment
- PATH configuration issues

**Solutions:**

**Option 1: Verify and fix activation**
```bash
# Check if activation worked properly
source venv/bin/activate
which python  # Should show venv/bin/python, not /usr/bin/python

# If still showing system python, check for aliases
alias python
alias python3

# Remove problematic aliases
unalias python
unalias python3
```

**Option 2: Use explicit venv path (most reliable)**
```bash
# Instead of relying on activation, use direct paths
venv/bin/python -c "import sys; print(sys.executable)"
venv/bin/pip install package-name

# For our package specifically
venv/bin/python -c "from logic_lm_mcp import LogicFramework; print('✅ Works!')"
```

**Option 3: Recreate virtual environment**
```bash
# Clean recreation if venv is corrupted
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
which python  # Verify it shows venv/bin/python
pip install logic-lm-mcp-server
```

**Option 4: Use absolute paths in shell**
```bash
# For Linux/Mac
/full/path/to/venv/bin/python script.py

# For Windows  
C:\full\path\to\venv\Scripts\python.exe script.py
```

### "Clingo not available" but everything else works

**Error:**
```
"clingo_available": false
```

**Cause:** Clingo ASP solver not installed.

**Solution:**
```bash
# Option 1: Via pip
pip install clingo>=5.8.0

# Option 2: Via conda
conda install -c conda-forge clingo

# Option 3: Check installation
python -c "import clingo; print('Clingo available')"
```

### Server starts but MCP tools not available

**Error:** MCP connection fails or tools not found.

**Cause:** Server not properly configured in Claude Code.

**Solution:**
1. Verify server is running: `python start_server.py`
2. Check Claude Code MCP configuration
3. Restart Claude Code if needed
4. Use absolute paths in configuration

### Python version compatibility issues

**Error:**
```
SyntaxError: invalid syntax
```

**Cause:** Python version < 3.8.

**Solution:**
```bash
# Check Python version
python --version  # Must be 3.8+

# Use specific Python version
python3.8 -m venv venv
# or
python3.9 -m venv venv
```

### Background process conflicts

**Error:** Server won't start, port already in use.

**Cause:** Previous server instance still running.

**Solution:**
```bash
# Kill existing processes
pkill -f start_server.py
pkill -f logic-lm

# Or find and kill specific process
ps aux | grep start_server
kill <process_id>
```

### File permission errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Cause:** Insufficient file permissions.

**Solution:**
```bash
# Fix permissions
chmod +x start_server.py
chmod -R 755 src/

# Or run with appropriate permissions
sudo python start_server.py  # Not recommended
```

### Import path issues

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Cause:** Python can't find local modules.

**Solution:**
```bash
# Run from project root directory
cd /path/to/logic-lm-mcp-server
python start_server.py

# Or use absolute imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Cache or old dependency conflicts

**Error:** Server uses old logic after code changes.

**Cause:** Python bytecode cache or old dependencies.

**Solution:**
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstall dependencies cleanly
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Restart Claude Code
```

### Memory or resource issues

**Error:** Server crashes or becomes unresponsive.

**Cause:** Insufficient system resources.

**Solution:**
- Close other applications to free memory
- Use smaller `max_models` parameter in requests
- Check system requirements (25MB base memory)
- Monitor server logs for resource warnings

## Development

### Project Structure
```
logic-lm-mcp-server/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastMCP server implementation
│   ├── logic_framework.py    # Core Logic-LM framework
│   └── asp_templates.py      # ASP template library
├── requirements.txt          # Python dependencies
├── setup.py                 # Package setup
├── start_server.py          # Recommended startup script
├── run.py                   # Alternative startup script
├── test_basic.py            # Basic functionality tests
├── test_setup.py            # Full setup tests
└── README.md               # This file
```

### Adding New Templates

1. Edit `src/asp_templates.py`
2. Add new template to `_initialize_templates()` method
3. Test with `python test_basic.py`

### Extending Logic Framework

1. Edit `src/logic_framework.py`
2. Add new reasoning methods to `LogicFramework` class
3. Update FastMCP tools in `src/main.py`

## Resources

### ASP Templates
The server provides access to ASP templates via MCP resources:
- `asp-templates://list` - List all available templates
- `asp-templates://info/{template_name}` - Get template information
- `asp-templates://template/{template_name}` - Get template code

### Available Templates
- **universal**: Universal quantification (All X are Y)
- **conditional**: Conditional rules (If X then Y)
- **syllogism**: Basic syllogistic reasoning
- **existential**: Existential quantification (Some X are Y)
- **negation**: Negation patterns (No X are Y)
- **set_membership**: Set membership and relationships
- **transitive**: Transitive relationships

## License

MIT License - See LICENSE file for details.

## Support

For issues, feature requests, or questions about Logic-LM reasoning capabilities, please:

1. Run `python test_basic.py` to verify basic functionality
2. Check the troubleshooting section above
3. Open an issue in the repository with:
   - Python version
   - Operating system
   - Error messages
   - Output of basic test