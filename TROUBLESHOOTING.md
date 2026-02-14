# Troubleshooting Installation

If you encounter errors like `Checking for Rust toolchain` or `Building wheel for moviepy` during installation, follow these steps:

## 1. Missing C++ Build Tools (Windows)
Python libraries like `pydantic-core` (used by Instagrapi) often require compiling C/Rust code.
- **Solution**: Install **Microsoft Visual C++ 14.0+**.
    - Download "Build Tools for Visual Studio" from Microsoft.
    - Select "Desktop development with C++" workload during installation.

## 2. Issues with MoviePy
Instagrapi depends on `moviepy`. If it fails:
- Try installing it separately:
  ```bash
  pip install moviepy --upgrade
  ```
- If that fails, install strictly from a wheel if available, or ensure you have `ffmpeg` installed/configured.

## 3. Alternative: Use Docker
If local installation is too difficult due to Windows dependencies, usage of Docker is highly recommended as the container handles all linux-based dependencies automatically.
- Ensure Docker Desktop is running.
- Run:
  ```bash
  docker-compose up --build
  ```

## 4. Rust Compiler
If you see Rust errors:
- Install Rust from [rustup.rs](https://rustup.rs/) and restart your terminal.
