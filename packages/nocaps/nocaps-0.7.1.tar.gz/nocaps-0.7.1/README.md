# nocaps

Say no to manual run-time error debugging. Let the AI do it for you.

nocaps is an AI-powered tool that automatically detects, diagnoses, and suggests fixes for run-time errors in your code. Spend less time debugging and more time building. It also roasts your code so you get some first-hand experience of working under a Senior developer.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Features](#features)
- [Contributing](#contributing)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)

## Installation

### From PyPI
```bash
pip install nocaps
```

### From NPM
```bash
npm install -g nocaps
```

### From Source
```bash
git clone https://github.com/yourusername/nocaps.git
cd nocaps
# Add installation steps here
```

## Usage

It is compatible with python, javascript, and java.

```bash
nocaps <your-code-file>
```

## Options

- `--help`: Show help message
- `--version`: Show version information

## Features

- Suggests fixes for run-time errors
- Roasts your code
- Supports multiple programming languages

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## Project Structure
```
nocaps/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── nocaps_cli/                  # Python CLI package
│   ├── __init__.py
│   ├── nocaps.py                # main CLI logic
│   ├── authorization_pkce.py    # PKCE authorization flow
│   ├── authorization_device_code.py
│   └── __pycache__/             # (ignored in .gitignore)
│
├── nocaps_server/               # Node.js API server
│   ├── server.js
│   ├── package.json
│   ├── package-lock.json
│   └── node_modules/            # (ignored in .gitignore)
│
├── tests/                       # test files for different languages
│   ├── test.py
│   ├── test.js
│   ├── test.java
│   └── test.class               # (compiled, usually ignored)
│
├── setup.py                     # Python packaging (PyPI)
├── README.md
├── .gitignore
├── .env                         # root env (ignored)
└── image.png                    # assets (logo, docs, etc.)
```

## How It Works

nocaps uses Gemini 2.0 flash to analyze your code and identify potential run-time errors. It then provides suggestions for fixing these errors, along with explanations to help you understand the underlying issues.

It uses a Auth0 authentication system to ensure secure access and protect user data.

Here's a diagram illustrating the Authorization/Authentication flow:

![diagram](auth_flow_diagram.png)
for more information refer to the [Auth0 documentation](https://auth0.com/docs).

After successful authentication, nocaps directs user's code to the backend server for analysis and debugging.