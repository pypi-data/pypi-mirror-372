# Playwright Project Setup CLI Tool

A Python CLI tool that quickly scaffolds a complete Playwright test automation project with TypeScript, organized structure, and QA best practices.

## ✨ Features

- **Quick Setup**: Instantly bootstraps a full Playwright project
- **Organized Structure**: Separates E2E, frontend, backend tests using POM
- **Multi-browser**: Pre-configured for Chromium, Firefox, and WebKit
- **Dynamic Test Data**: Faker.js for realistic mock data
- **TypeScript Ready**: Fully configured for TypeScript and TS-Node
- **Fixtures & Utils**: Common helper structures and environment setup
- **Custom Location**: Use `--path` to generate your project anywhere
- **Safe Execution**: Preview with `--dry-run`, force overwrite with `--force`

---

## 🔧 Prerequisites

Make sure the following are installed:

- **Python 3.7+**
- **Node.js v18+**
- **npm**
- **[pipx](https://pypa.github.io/pipx/)**

> Install pipx if missing:

```bash
sudo apt install pipx
pipx ensurepath
```

---

## 🚀 Installation (Recommended via pipx)

```bash
pipx install qa-project-gen
```

> Now you can run the CLI globally:

```bash
qa-gen my-playwright-project
```

---

## 🛠️ Command Options

```bash
qa-gen <project-name> [options]

Options:
  --force        Overwrite existing files if they exist
  --dry-run      Show what would be created without writing to disk
  --clean        Remove generated folders and files from a project
  --path <dir>   Set the folder where the project should be created
```

---

## 📌 Usage Examples

```bash
# Create a new Playwright project
qa-gen my-test-project

# Create at a specific location
qa-gen my-project --path /home/user/qa-projects

# Simulate project creation without making changes
qa-gen temp-project --dry-run

# Overwrite files in an existing project folder
qa-gen demo-project --force

# Clean up an old project
qa-gen demo-project --clean --path /home/user/old-projects
```

---

## 📁 Generated Project Structure

```
my-test-project/
├── playwright.config.ts           # Playwright configuration
├── tsconfig.json                  # TypeScript configuration
├── package.json                   # Node.js metadata
├── .gitignore                     # Ignore rules
├── README.md                      # Template documentation
└── tests/
    ├── e2e/                       # End-to-end specs
    ├── front_end/feature_one/     # UI/FE tests
    ├── back_end/feature_one/      # API/BE tests
    └── support/
        ├── POMs/feature_one/      # Page Object Models
        └── utils/                 # Shared test utilities
            ├── helpers.ts
            ├── test-data.ts
            └── fixtures.ts
```

---

## 📦 What Gets Installed (via npm)

The CLI installs and configures:

- `playwright` — Browser automation
- `@playwright/test` — Test runner and assertion library
- `typescript` — TypeScript language support
- `ts-node` — TypeScript execution in Node
- `@faker-js/faker` — Fake test data
- `dotenv` — Environment variable support

---

## ✅ Running Tests

Once your project is generated:

```bash
cd my-test-project

# Run all tests
npx playwright test

# Run specific suite
npx playwright test tests/front_end

# Run with browser UI
npx playwright test --headed

# View test results
npx playwright show-report
```

---

## 🧠 Notes

- If using Linux or WSL and `venv` is missing:
  ```bash
  sudo apt install python3-venv
  ```
- If you’re in a restricted environment (like Debian or Ubuntu), use `pipx` instead of global `pip` to avoid permission issues.
- Avoid `sudo pip install` to prevent breaking system packages.

---

Built with ❤️ to help QA Engineers get started faster and test better.
