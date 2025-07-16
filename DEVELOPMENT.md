# Development Code of Conduct

## Overview

This document establishes the mandatory coding standards and practices for all contributors to this repository. **Absolute compliance is required** - no exceptions will be made to these standards.

## 1. Import and Namespace Management

### 1.1 Import Restrictions

- **PROHIBITED**: Never use `from module import X` syntax
- **REQUIRED**: Always use `import module` and reference attributes via `module.attribute`

**❌ Incorrect:**
```python
from os import path
from typing import Dict, List
from datetime import datetime
```

**✅ Correct:**
```python
import os
import typing
import datetime
```

### 1.2 Rationale

Explicit module references improve code readability, reduce namespace pollution, and make dependencies immediately apparent to reviewers and maintainers.

## 2. Documentation Standards

### 2.1 NumPy-Style Docstrings

Every function, class, and module **must** include comprehensive NumPy-style docstrings containing:

- **Summary**: One-line description
- **Parameters**: Input parameters with types and descriptions
- **Returns**: Return value types and descriptions
- **Raises**: Exception types and conditions
- **Examples**: Usage examples with expected outputs
- **Notes**: Additional implementation details (when applicable)

### 2.2 Docstring Template

```python
def example_function(param1: str, param2: int) -> typing.List[str]:
    """
    Brief one-line summary of the function.

    More detailed description of what the function does, its purpose,
    and any important behavioral notes.

    Parameters
    ----------
    param1 : str
        Description of the first parameter.
    param2 : int
        Description of the second parameter.

    Returns
    -------
    typing.List[str]
        Description of the return value.

    Raises
    ------
    ValueError
        When param2 is negative.
    TypeError
        When param1 is not a string.

    Examples
    --------
    >>> result = example_function("test", 5)
    >>> print(result)
    ['test_0', 'test_1', 'test_2', 'test_3', 'test_4']

    Notes
    -----
    This function implements a specific algorithm that...
    """
```

### 2.3 Class Documentation

```python
class ExampleClass:
    """
    Brief description of the class purpose.

    Detailed explanation of the class functionality, its role in the system,
    and any important usage patterns.

    Parameters
    ----------
    init_param : str
        Description of initialization parameter.

    Attributes
    ----------
    public_attr : int
        Description of public attribute.
    _private_attr : str
        Description of private attribute.

    Methods
    -------
    public_method(param)
        Brief description of public method.

    Examples
    --------
    >>> obj = ExampleClass("initial_value")
    >>> result = obj.public_method(42)
    >>> print(result)
    Expected output here

    Notes
    -----
    Additional implementation details, design decisions, or usage patterns.
    """
```

## 3. Code Completeness Requirements

### 3.1 Self-Contained Implementation

- **Production-Ready**: All code must be fully implemented and ready for production use
- **No Placeholders**: Absolutely no `TODO`, `FIXME`, or placeholder comments
- **Complete Logic**: All functions must contain complete implementation
- **Ready to Execute**: Users should not need to modify or complete any code

### 3.2 Dependency Management

- **Explicit Dependencies**: All required imports must be clearly stated
- **Version Compatibility**: Code must work with specified Python versions
- **Minimal Dependencies**: Use only necessary external libraries

## 4. Library Usage Policy

### 4.1 Permitted Libraries

- **Standard Library**: All Python standard library modules
- **Open Source**: Any open-source Python library that operates offline
- **Data Processing**: NumPy, Pandas, SciPy, etc.
- **Testing**: pytest, unittest, mock, etc.
- **Utilities**: pathlib, collections, itertools, etc.

### 4.2 Prohibited Libraries

- **Network Libraries**: `requests`, `aiohttp`, `httpx`, `urllib` for web requests
- **Web Frameworks**: Flask, Django, FastAPI (except for internal APIs)
- **Cloud Services**: AWS SDK, Google Cloud SDK, Azure SDK
- **External APIs**: Any library requiring internet connectivity

### 4.3 Justification Required

Any library usage must be justified in code comments or documentation explaining:
- Why the library is necessary
- How it improves the solution
- What alternatives were considered

## 5. Performance and Security Standards

### 5.1 FinTech Best Practices

- **Data Integrity**: Implement proper validation and error handling
- **Security**: Follow secure coding practices for sensitive data
- **Scalability**: Design for performance and maintainability
- **Auditability**: Code must be easily reviewable and traceable

### 5.2 Performance Requirements

- **Efficiency**: Optimize for both time and space complexity
- **Resource Management**: Proper cleanup of resources (files, connections)
- **Error Handling**: Comprehensive exception handling
- **Logging**: Appropriate logging for debugging and monitoring

### 5.3 Security Considerations

- **Input Validation**: All user inputs must be validated
- **Data Sanitization**: Sanitize data before processing
- **Secure Defaults**: Use secure defaults for all configurations
- **Minimal Privileges**: Follow principle of least privilege

## 6. Type Safety and Style Requirements

### 6.1 Type Annotations

- **Mandatory**: Every function signature must include type hints
- **Comprehensive**: All parameters, return values, and class attributes
- **Accurate**: Types must accurately reflect the actual data types
- **Import Style**: Use `import typing` and reference `typing.Type`

### 6.2 PEP Compliance

- **PEP 8**: Style Guide for Python Code
- **PEP 20**: The Zen of Python
- **PEP 257**: Docstring Conventions
- **PEP 484**: Type Hints
- **PEP 526**: Variable Annotations

### 6.3 Type Checking

- **Zero Warnings**: Code must pass strict type checking
- **MyPy Compatible**: Must pass `mypy --strict` without errors
- **IDE Support**: Must work with VS Code/PyCharm strict mode
- **Runtime Safety**: Type hints must match runtime behavior

## 7. Testing and Quality Assurance

### 7.1 Testing Requirements

- **Unit Tests**: All functions must have corresponding unit tests
- **Integration Tests**: Complex interactions must be tested
- **Edge Cases**: Test boundary conditions and error scenarios
- **Coverage**: Minimum 90% code coverage required

### 7.2 Code Quality Tools

- **Linting**: Must pass all enabled Ruff rules
- **Formatting**: Must conform to project formatting standards
- **Documentation**: Must pass docstring linting
- **Security**: Must pass security scanning tools

## 8. Ruff Configuration Compliance

### 8.1 Enabled Rules

The following Ruff rules are enforced:

- **E**: Pycodestyle errors (PEP 8 compliance)
- **F**: Pyflakes (undefined names, unused imports)
- **I**: isort (import ordering and formatting)
- **TCH**: Type-checking violations
- **C**: Complexity (cyclomatic complexity limits)
- **N**: Naming conventions
- **D2**: Pydocstyle blank lines after summary
- **D3**: Multi-line docstring formatting
- **D415**: Sections must end with colon
- **D417**: Docstring args must match signature
- **D418**: Section capitalization
- **D419**: Final newline in docstring
- **ASYNC**: Async-specific linting
- **Q**: Quotes consistency
- **RSE**: Raise-statement correctness
- **SIM**: Simplification rules
- **RUF**: Ruff-specific rules

### 8.2 Configuration Details

```toml
[tool.ruff]
extend-exclude = ["examples/*", ".venv/*"]
line-length = 79

[tool.ruff.lint]
select = [
    "E", "F", "I", "TCH", "C", "N", "D2", "D3", 
    "D415", "D417", "D418", "D419", "ASYNC", 
    "Q", "RSE", "SIM", "RUF"
]
ignore = [
    "F405", "F403", "E501", "D205", "D417", "C901"
]
fixable = ["I", "TCH", "D"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.lint.isort]
force-single-line = true

[tool.ruff.format]
docstring-code-format = true
```

## 9. Operational Constraints

### 9.1 Local Execution Only

- **Offline Operation**: All code must run without internet connectivity
- **No External Services**: No dependencies on cloud services or APIs
- **Self-Contained**: All required resources must be included or generated locally

### 9.2 Environment Requirements

- **Python Version**: Support specified Python versions only
- **Platform Independence**: Code should work across major platforms
- **Resource Limits**: Consider memory and CPU constraints
- **Dependency Management**: Use lock files for reproducible builds

## 10. Code Review Process

### 10.1 Review Checklist

Before submitting code, ensure:

- [ ] All imports follow the explicit module reference pattern
- [ ] Every function/class has complete NumPy-style docstrings
- [ ] Code is fully implemented with no placeholders
- [ ] All type hints are present and accurate
- [ ] Passes all Ruff linting rules
- [ ] Includes comprehensive tests
- [ ] Documentation is complete and accurate
- [ ] Security best practices are followed

### 10.2 Reviewer Responsibilities

Reviewers must verify:

- [ ] Compliance with all coding standards
- [ ] Proper documentation completeness
- [ ] Type safety and accuracy
- [ ] Performance and security considerations
- [ ] Test coverage and quality
- [ ] Integration with existing codebase

## 11. Enforcement

### 11.1 Automated Checks

- **CI/CD Pipeline**: Automated enforcement of all rules
- **Pre-commit Hooks**: Local validation before commits
- **IDE Integration**: Real-time feedback during development
- **Quality Gates**: Prevent merging of non-compliant code

### 11.2 Consequences

- **Code Rejection**: Non-compliant code will be rejected
- **Review Delays**: Incomplete documentation causes review delays
- **Technical Debt**: Accumulation of violations creates technical debt
- **Maintenance Issues**: Poor compliance leads to maintenance problems

## 12. Continuous Improvement

### 12.1 Standards Evolution

- **Regular Reviews**: Periodic assessment of standards effectiveness
- **Community Input**: Gather feedback from development team
- **Tool Updates**: Adapt to new linting and formatting tools
- **Best Practices**: Incorporate industry best practices

### 12.2 Training and Support

- **Documentation**: Maintain comprehensive development guides
- **Examples**: Provide clear examples of compliant code
- **Tools**: Provide configuration files and development tools
- **Support**: Offer guidance for compliance challenges

---

**Remember**: These standards are not suggestions—they are requirements. Compliance is mandatory for all contributions to maintain code quality, security, and maintainability.