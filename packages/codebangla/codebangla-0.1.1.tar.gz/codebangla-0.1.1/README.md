# CodeBangla

**CodeBangla** is a Python package that allows you to write Python code using Bangla keywords (in English transliteration). It is designed to help beginners, especially students in Bangladesh, to learn programming concepts without being intimidated by English-based syntax.

This project transpiles `.bp` (BanglaPython) files into standard `.py` files, which can then be executed by the Python interpreter.

## ⚠️ Known Issues

-   **Numeral Conversion**: The automatic conversion of Bengali numerals (e.g., `১২৩`) to English numerals (`123`) is currently **not working** due to a deep, unresolved issue in the tokenization process. All other features are functional.

## 🚀 Features

- **Bangla Keywords**: Write Python using intuitive Bangla words (`jodi`, `noile`, `chhap`, `shuru`, etc.).
- **Transpiler**: Converts your Bangla-Python code into clean, standard Python code.
- **CLI Tool**: Run your `.bp` files directly from the command line.
- **Safe Replacement**: Preserves strings, comments, and code structure by using Python's native tokenizer.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gemini/codebangla.git
    cd codebangla
    ```

2.  **Install the package:**
    ```bash
    pip install -e .
    ```

## 📝 Usage

You can use `codebangla` in two ways:

### 1. Run a file directly

Create a file with a `.bp` extension, for example, `hello.bp`:

```python
# hello.bp
shuru main():
    chhap("Hello from CodeBangla!")

main()
```

Now, run it from your terminal:

```bash
codebangla run hello.bp
```

### 2. Compile a file

You can also compile your `.bp` file into a standard `.py` file.

```bash
codebangla compile hello.bp
```

This will create a `hello.py` file in the same directory.

## 🧪 Running Tests

To run the included tests, first install the developer dependencies:

```bash
pip install -r requirements.txt
```

Then, run pytest:

```bash
pytest
```

## 🗺️ Keyword Mappings

Here are some of the supported Bangla keywords and their Python equivalents:

| Bangla      | Python   |
|-------------|----------|
| `chhap`     | `print`  |
| `neoa`      | `input`  |
| `jodi`      | `if`     |
| `noile`     | `else`   |
| `jotokkhon` | `while`  |
| `shuru`     | `def`    |
| `phiredao`  | `return` |
| `sotti`     | `True`   |
| `miththa`   | `False`  |
| `er_jonno`  | `for`    |
| `moddhe`    | `in`     |

...and many more!