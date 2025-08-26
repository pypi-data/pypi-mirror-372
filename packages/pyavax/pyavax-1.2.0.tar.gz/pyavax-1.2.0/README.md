# pyglow

![GitHub Repo stars](https://img.shields.io/github/stars/BirukBelihu/pyava)
![GitHub forks](https://img.shields.io/github/forks/BirukBelihu/pyava)
![GitHub issues](https://img.shields.io/github/issues/BirukBelihu/pyava)
[![PyPI Downloads](https://static.pepy.tech/badge/pyava)](https://pepy.tech/projects/pyava)<br>
![Python](https://img.shields.io/pypi/pyversions/pyava)

**pyava** is command line tool to help you check the availability of a package name you want on [PyPI](https://pypi.org)

---
GitHub: [pyava](https://github.com/BirukBelihu/pyava)
---

## ✨ Features

- 💻 Check up to 5 package names you want at a time.
- ✅ Set custom timeout for each package name you check
- ℹ️ Get info about the package if it's taken like `summary`, `version`, `author`, `author email`, `home page` & more.
- 🎨 Colorful output

---

### Sample

![pyava Sample](https://github.com/birukbelihu/pyava/raw/master/samples/sample_1.png)

![pyava Sample](https://github.com/birukbelihu/pyava/raw/master/samples/sample_2.png)

---

## 📦 Installation

```
pip install pyava
```

You can also install pyava from source code. source code may not be stable, but it will have the latest features and
bug fixes.

Clone the repository:

```
git clone https://github.com/birukbelihu/pyava.git
```

Go inside the project directory:

```bash
cd pyava
```

### Set up Python virtual environment(I recommend using [uv](https://github.com/astral-sh/uv) for lightning speed)

### With uv

```bash
uv venv .venv
```

### With Python

```bash
python -m venv .venv
```

# Activate virtual environment

```bash
.venv\Scripts\activate # On Windows
```

```bash
source .venv/bin/activate # On Linux, WSL & macOS
```

# Install required dependencies

### With uv

```bash
uv pip install -r requirements.txt
```

### With Python

```bash
pip install -r requirements.txt
```

---

Install pyava:

```
pip install -e .
```

---

## 🧠 Example Usage

```bash
pyava requests tensorflow mediapipe
```

### Output

![pyava Sample](https://github.com/birukbelihu/pyava/raw/master/samples/sample_3.png)

## 🙌 Contribute

Want to improve `pyava`? Contributions are welcome!

---

## 📢 Social Media

- 📺 [YouTube: @pythondevs](https://youtube.com/@pythondevs?si=_CZxaEBwDkQEj4je)

---

## 📄 License

This project is licensed under the **Apache License 2.0**. See
the [LICENSE](https://github.com/birukbelihu/pyava/blob/master/LICENSE) file for details.