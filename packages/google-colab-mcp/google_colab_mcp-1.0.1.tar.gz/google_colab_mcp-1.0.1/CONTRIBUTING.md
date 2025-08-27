# Contributing to Google Colab MCP Server

Thank you for your interest in contributing to the Google Colab MCP Server! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Google Cloud account (for testing)
- Basic knowledge of MCP (Model Context Protocol)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/google-colab-mcp.git
   cd google-colab-mcp
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Setup Authentication**
   ```bash
   python setup_auth_simple.py
   ```

5. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

## 🛠️ Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Write docstrings for all functions and classes
- Keep functions focused and small

### Example Code Style

```python
def create_notebook(self, name: str, content: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new Google Colab notebook.
    
    Args:
        name: The name of the notebook
        content: Optional initial content for the notebook
        
    Returns:
        Dictionary containing notebook information
        
    Raises:
        AuthenticationError: If Google authentication fails
        NotebookCreationError: If notebook creation fails
    """
    # Implementation here
    pass
```

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add automatic token refresh
fix(selenium): handle timeout errors gracefully
docs(readme): update installation instructions
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_auth_manager.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write tests for all new features
- Include both positive and negative test cases
- Mock external dependencies (Google APIs, Selenium)
- Use descriptive test names

Example test:

```python
def test_create_notebook_success():
    """Test successful notebook creation."""
    auth_manager = Mock()
    drive_manager = ColabDriveManager(auth_manager)
    
    result = drive_manager.create_notebook("Test Notebook")
    
    assert result["success"] is True
    assert "id" in result
    assert result["name"] == "Test Notebook.ipynb"
```

## 📝 Documentation

### Code Documentation

- Write clear docstrings for all public functions
- Include parameter types and return types
- Document exceptions that may be raised
- Provide usage examples where helpful

### README Updates

When adding new features:
- Update the features list
- Add new tools to the tools table
- Include usage examples
- Update configuration options if needed

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - Browser version (for Selenium issues)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Error messages or logs

3. **Additional Context**
   - Screenshots if applicable
   - Configuration files (remove sensitive data)
   - Relevant log entries

## ✨ Feature Requests

For new features:

1. **Check Existing Issues** - Avoid duplicates
2. **Describe the Problem** - What need does this address?
3. **Propose a Solution** - How should it work?
4. **Consider Alternatives** - Are there other approaches?
5. **Additional Context** - Examples, mockups, etc.

## 🔄 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   python -m pytest
   python test_mcp_config.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Requirements**
   - Clear description of changes
   - Link to related issues
   - All tests passing
   - Documentation updated

## 🏗️ Project Structure

```
google-colab-mcp/
├── src/                    # Source code
│   ├── auth_manager.py     # Google authentication
│   ├── colab_drive.py      # Drive API integration
│   ├── colab_selenium.py   # Selenium automation
│   ├── mcp_server.py       # Main MCP server
│   ├── session_manager.py  # Session handling
│   └── utils.py            # Utility functions
├── config/                 # Configuration files
├── tests/                  # Test files
├── docs/                   # Documentation
├── examples/               # Usage examples
└── scripts/                # Utility scripts
```

## 🔒 Security

### Reporting Security Issues

Please do not report security vulnerabilities through public GitHub issues. Instead:

1. Email security concerns to [security@yourproject.com]
2. Include detailed description of the vulnerability
3. Provide steps to reproduce if possible
4. Allow time for investigation before public disclosure

### Security Guidelines

- Never commit credentials or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Follow OAuth2 best practices
- Keep dependencies updated

## 📋 Code Review Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No sensitive data in commits
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete

## 🎯 Areas for Contribution

We especially welcome contributions in:

- **Testing**: Improve test coverage
- **Documentation**: Better examples and guides
- **Error Handling**: More robust error messages
- **Performance**: Optimization improvements
- **Features**: New Colab integrations
- **Compatibility**: Support for more MCP clients

## 💬 Getting Help

- **GitHub Discussions**: For questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Code Review**: Tag maintainers for review help

## 🙏 Recognition

Contributors will be:
- Listed in the README contributors section
- Mentioned in release notes for significant contributions
- Invited to join the maintainers team for consistent contributors

Thank you for contributing to the Google Colab MCP Server! 🚀