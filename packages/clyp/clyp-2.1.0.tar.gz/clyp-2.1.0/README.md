# Clyp

Clyp is an experimental programming language that transpiles to Python. It's designed with a clean and simple syntax, aiming to make coding more straightforward and readable.

*Site at [codesoft.is-a.dev/clyp/](https://codesoft.is-a.dev/clyp/)*

## Features

- **Static-like Typing**: Variables are declared with their types, providing clarity and robustness.
- **Simplified Syntax**: Uses `{}` for blocks and `;` for newlines, similar to C-like languages.
- **Python Interoperability**: Seamlessly uses Python libraries and functions.
- **Standard Library**: Comes with a handy set of built-in functions for common tasks.

## Installation

To get started with Clyp, you need to have Python installed. Then, you can install Clyp using pip:

```bash
pip install clyp
```

Want to install from source? Clone the repository and run:

```bash
git clone https://github.com/clyplang/clyp.git
cd clyp
pip install -r requirements.txt
```

## Usage

The Clyp CLI allows you to execute `.clyp` files directly from your terminal.

- **Run a file**:

  ```bash
  clyp go path/to/your/file.clyp
  ```

- **Check the version**:

  ```bash
  clyp --version
  ```

- **Display help**:

  ```bash
  clyp --help
  ```

## Language Syntax

### Variables

Variables are declared with their type followed by the name and value.

```clyp
int x = 10;
str message = "Hello, World!";
bool is_active = true;
```

### Functions

Functions are defined using the `def` keyword, with type hints for arguments and a `returns` clause for the return type.

```clyp
def greet(str name) returns None {
    print("Hello, " + name);
}
```

### Conditionals

Clyp uses `if`, `else if`, and `else` for conditional logic.

```clyp
int a = 10;
if (a > 5) {
    print("a is greater than 5");
} else {
    print("a is not greater than 5");
}
```

### Comments

Comments start with `#`.

```clyp
# This is a single-line comment
```

## Standard Library

Clyp includes a standard library with useful functions:

- `fetch(url: str)`: Fetches content from a URL.
- `read_file(path: str)`: Reads a file's content.
- `write_file(path: str, content: str)`: Writes content to a file.
- `slugify(text: str)`: Converts a string into a URL-friendly slug.
- `is_empty(value)`: Checks if a value is empty.
- `is_prime(n: int)`: Checks if a number is prime.
- `to_roman_numerals(num: int)`: Converts an integer to Roman numerals.

## Development

To contribute to Clyp, you can set up a development environment:

```bash
pip install -r requirements-dev.txt
```

Run tests using `pytest`:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
