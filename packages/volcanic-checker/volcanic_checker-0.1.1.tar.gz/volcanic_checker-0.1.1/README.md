# Volcanic Checker

Volcanic Checker is a Python library to fetch and handle volcanic activity alerts from the Japan Meteorological Agency (JMA).

## Installation

You can install the library via pip:

```bash
pip install volcanic-checker
```

## Usage

```python
import volcanic-checker

alert = checker.get_alert_level_by_name("富士山")

print(f"Volcano: {alert.name}")
print(f"Alert level: {alert.level}")
print(f"Info URL: {alert.url or 'None'}")
print(f"Retrieved at: {alert.retrieved_at}")
```

### CLI

The library also provides a command-line interface. After installation, you can run:

```bash
python -m volcanic_checker.main
```

It will prompt you for a volcano name and display its alert level.

## License

MIT License
