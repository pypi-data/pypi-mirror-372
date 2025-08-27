# Changelog


## 1.0.0

- Initial release
  - This application was created by combining and adapting elements of both the [_Fuisce_](https://github.com/mitchnegus/fuisce/blob/main/CHANGELOG.md) and [_Authanor_](https://github.com/mitchnegus/authanor/blob/main/CHANGELOG.md) packages

### 1.0.1

- Extend the Python version range to include 3.13

### 1.0.2

- Catch errors where the application factory function may not exist

### 1.1.0

- Refactor views to enable compatibility with SQLAlchemy 2.0.39
- Allow the `Factory` to accept database interface parameters
- Use type annotations for declarative mappings
- Accommodate systems with pre-defined configurations when testing

### 1.2.0

- Allow handlers to pass subset selectors (e.g., offset and limit keywords) to the SQLAlchemy `Select` object
