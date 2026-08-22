# Contributing to LocalPDF.io

Thank you for considering contributing! 🎉

## How to Contribute

### 1. Fork the project

- Fork the repository
- Clone your fork locally

#### Set up the environment

We use `ruff` and `pre-commit` to keep code quality consistent.

1. **Create a virtual environment (recommended)**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```

3. **Install pre-commit hooks**

    This ensures automatic checks run before every commit.

    ```bash
    pre-commit install
    ```

### 2. Create a branch

```bash
git checkout -b feature/my-contribution
```

### 3. Make your changes

- Write clean, commented code
- Test your changes locally
- Make sure everything works

### 4. Commit your changes

```bash
git add .
git commit -m "feat: description of your contribution"
```

Use descriptive commit messages:

- `feat: add new feature X`
- `fix: bug in conversion Y`
- `perf: improve performance of function Z`
- `docs: update README`

### 5. Push to GitHub

```bash
git push origin feature/my-contribution
```

### 6. Open a Pull Request

- Go to the original repository
- Click "New Pull Request"
- Describe your changes clearly

## What to contribute

### 🐛 Bugs

Found a bug? Open an issue describing:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Screenshots/logs if possible

### ✨ New features

Ideas for new features:

- New conversion formats
- Performance optimizations
- Automated tests
- Add more languages (i18n)

### 📚 Documentation

- Improve the README
- Add usage examples
- Fix typos
- Translate documentation

### 🎨 Design

- Add dark mode
- Add micro-animations

## Code guidelines

- Follow PEP 8 for Python code
- Comment complex code
- Test your changes before submitting
- Keep it simple

## 🎖️ Contributor recognition

We use the [All Contributors Bot](https://allcontributors.org/) to recognize all contributions!

### How to be added as a contributor

After your contribution is accepted, you or a maintainer can comment:

```
@all-contributors please add @your-username for code
```

**Recognized contribution types:**

- `code` — Code
- `doc` — Documentation
- `design` — Design
- `bug` — Bug reports
- `ideas` — Ideas
- `review` — PR reviews
- And many more! (see [docs/BOT_USAGE.md](docs/BOT_USAGE.md))

The bot will automatically create a PR adding you to the contributors list! ✨

## Questions?

- Open an issue on GitHub
- Email: <virgilio.junior94@gmail.com>

---

**Every contribution is welcome, no matter the size!** ⭐
