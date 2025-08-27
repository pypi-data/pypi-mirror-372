# 🚀 Instance Checker

A simple and powerful Python utility to **count running instances of an application** by checking both:

- Running processes (via `psutil`)
- Lock files in a specified directory

Perfect for preventing multiple concurrent runs of the same app.

---

## 📦 Features

✅ Count processes by command line  
✅ Count lock files with `.lock.` pattern  
✅ Works on Unix and Windows  
✅ Easy to integrate into your project  
✅ 100% Pythonic 😍

---

## 🧰 Installation

```bash
pip install instance-checker
```

> ⚠️ This package requires Python 3.9+

---

## 🧪 Usage Example

```python
from instance_checker.utils import CountHelper

helper = CountHelper(lock_dir="/tmp/my_app_locks")

print(helper.process_count("my_app"))        #> 2
print(helper.pid_file_count("my_app"))       #> 1
```

---

## 🛠 How It Works

### Process Checking ✅

Counts how many running processes have a given identifier in their command-line arguments.

```python
CountHelper.process_count("my_app")
```

### Lock File Checking 🔐

Counts how many `.lock.` files exist in the specified directory that contain the identifier.

```python
helper.pid_file_count("my_app")
```

---

## 🧹 Why You Should Use This

- Prevents race conditions when running apps concurrently
- Lightweight and easy to integrate
- No need to write boilerplate process/lock management code
- Safe and reliable thanks to `psutil` and `pathlib`

---

## 🧾 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

If you like this tool, give it a star ⭐ — it really helps!
And if you're building cool stuff with it, let me know — I'd love to see it! 💻✨

## 🐙 GITVERSE

🔗 [https://gitverse.ru/dkurchigin/instance_checker](https://gitverse.ru/dkurchigin/instance_checker)