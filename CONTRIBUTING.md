# Contributing

## Introduction.
Welcome to the contributing guide for zcached.py! This guide will walk you through the process of setting up your development environment, running tests, and ensuring code quality.

### Do's and Dont's

- Dont keep your PR scope too big. We would rather review many small PRs with seperate features than one giant one.
- Do write high-quality code without rushing, focusing on clarity, readability, and maintainability.
- Do use [semantic commit messages](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716) to describe your changes clearly and concisely.
- Do write unit tests to ensure the correctness of your code changes and improve overall code reliability.

## Setting up a environment.
**Before setting up the environment, make sure to fork the project!**

1. Clone the repository: Use the git clone command to get the forked repository to your local machine. Replace `<your-username>` with your GitHub username.
> `git clone https://github.com/<your-username>/zcached.py`

2. Navigate to the project directory: Move into the directory of the cloned repository.
> `cd zcached.py`

3. Install dependencies: Use pip to install the required dependencies for the project.
> `pip install -r requirements.txt`
>
> `pip install -r dev-requirements.txt`

**Your environment is now set up and ready for development or usage!**

## Running tests.
> [!NOTE]
> Before running the tests, make sure you are in the project directory.

### Pytest / Unit tests.
To run the unit tests use the following command:
> `pytest tests/`

### Pyright / Type checking.
To perform type checking with Pyright use:
> `pyright zcached/`

### Pre-commit hooks.
To run, use:
> `pre-commit run --all-files`
