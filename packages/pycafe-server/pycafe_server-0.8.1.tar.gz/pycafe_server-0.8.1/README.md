# pycafe_server

[![PyPI - Version](https://img.shields.io/pypi/v/pycafe-server.svg)](https://pypi.org/project/pycafe-server)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pycafe-server.svg)](https://pypi.org/project/pycafe-server)

---

**Table of Contents**

- [Installation](#installation)
- [Changelog](#changelog)
- [License](#license)

## Installation

```console
pip install pycafe-server
```

## Changelog

### 0.8.1 - 2025-08-27

- chore: show become editor URL as "here"
- fix: API keys link should only be visible for editors

### 0.8.0 - 2025-08-26

- feat: get editor/admin permission from oauth token
- feat: environment variable with link to get editor access

### 0.7.5 - 2025-08-11

- fix: unicode characters not stored correctly with client

### 0.7.4 - 2025-08-07

- fix: handle trailing slashes in the client.

### 0.7.3 - 2025-08-07

- fix: use correct uv version.

### 0.7.2 - 2025-08-07

- fix: pin / constrain uv (v0.8 incompatibility).
- fix: error when hashing project with large files
- feat: show warning for system reset in pycafe_server UI

### 0.7.1 - 2025-06-30

- fix: vizro example compatibility with latest dash version
- chore: update vizro example

### 0.7.0 - 2025-04-14

- feat: support newer Pyodide versions in client.
- feat: ignore virtual environments in client.
- feat: enable hot reloading of app with snippet from parent page
- fix: local wheel does not work in file export
- fix: pyodide 0.27.2 cannot be default due to typing_extension incompatibility
- feat: support pyodide 0.27.2 and make default for vizro

### 0.6.0 - 2025-03-24

- feat: add request proxy support.
- fix: add missing dependency.
- fix: support dash 3.0 on pyodide 0.27

### 0.5.0 - 2025-03-17

- feat: create .html file from command line.

### 0.4.0 - 2025-03-11

- feat: support installing local wheels.
- fix: file content excluded from hash for signing
- fix: remove demo message from self-hosted instances

### 0.3.4 - 2025-02-13

- fix: large HTML file not loading correctly
- fix: sharing features visibility respect settings

### 0.3.3 - 2025-02-10

- fix: sharing features were available regardless of settings

### 0.3.2 - 2025-02-10

- feat: support Dash 3.0

### 0.3.1 - 2025-02-07

- fix: remove unintentionally added background endpoint.

### 0.3.0 - 2025-02-07

- feat: setting to remove branding for anonymous visitors.
- fix: don't provide sitemap for self-hosted instances.

### 0.2.0 - 2025-01-29

- fix: shorten login log cleanup interval.
- fix: extra security checks when trail mode disabled.
- feat: opening exported files via drag and drop.

### 0.1.0 - 2025-01-29

- Initial release.

## License

You need a license for `pycafe-server`, it is not open source.
