
# **EHNPY – EnvriHub Next Python Library**

**EHNPY** is a proof-of-concept Python package demonstrating **parallel data access** across multiple scientific disciplines within the [Envri-Hub Next project](https://envri.eu/envri-hub-next/).

---

## 📦 Installation from PyPI

```bash
pip install ehnpy
```

---

## 🛠 Installing for Local Development

If you’re working on the source code, you can install EHNPY in **editable mode** so changes are picked up without reinstallation.

### **Prerequisites**

* Python 3.x
* `pip` available
* Access to the development repository (e.g., GitLab clone)

### **Steps**

1. Clone the repository:

   ```bash
   git clone https://gitlab.a.incd.pt/envri-hub-next/ehnpy.git
   cd ehnpy
   ```
2. Install in editable mode:

   ```bash
   pip install -e .
   ```

---

## 💡 Notes

* On Windows, use forward slashes (`/`) or escaped backslashes (`\\`) in paths when necessary (e.g., Git Bash, WSL).
* Verify installation:

  ```bash
  pip list | findstr ehnpy
  ```

---