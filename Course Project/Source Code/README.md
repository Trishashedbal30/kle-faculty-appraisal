# Source Code Location

The complete current application source remains in the repository root to preserve the established project structure and launch commands.

- Backend and workflow code: [`../../app/`](../../app/)
- Static web frontend: [`../../web/`](../../web/)
- Tests: [`../../tests/`](../../tests/)
- Project entry point and commands: [`../../manage.py`](../../manage.py)
- Dependencies: [`../../requirements.txt`](../../requirements.txt)

The source is not duplicated inside this directory. When the course submission requires a standalone archive, package the repository source from the root while excluding local environments, caches, private data, runtime files, credentials, and generated reports as specified in the root [`.gitignore`](../../.gitignore).
