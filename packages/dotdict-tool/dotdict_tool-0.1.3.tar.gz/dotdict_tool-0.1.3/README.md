### Dotdict (dotdict-tool)

A tiny, convenient wrapper around Python's `dict` that lets you access keys via dot notation while preserving normal dict behavior. Nested `dict`s (and dicts inside `list`s) are auto-wrapped into `Dotdict` on access.

Works great for quick data access in scripts, small apps, and anywhere you want ergonomic attribute-style access without bringing in heavy dependencies.

### Installation

```bash
pip install dotdict-tool
```

### Quick start

```python
from Dotdict import Dotdict

data = {
    "name": "Bao",
    "age": 30,
    "address": {"city": "HCMC", "country": "Vietnam"}
}

# Convert sang Dotdict
d = Dotdict(data)

print(d.name)            # Bao
print(d.age)             # 30
print(d.address.city)    # HCMC
```

### Key features

- **Dot notation access**: `d.user.name` instead of `d["user"]["name"]`.
- **Auto-wrap nested dicts**: Nested `dict`s become `Dotdict` on access.
- **List support**: Dicts inside lists are wrapped on access (`d.items[0].id`).
- **Missing keys are safe**: Accessing a missing key returns a readable placeholder string instead of raising an error.
- **Still a real dict**: Inherits from `dict`; you can use all standard dict methods (`keys`, `items`, `get`, `update`, ...).

### Behavior and API

- **Attribute access and assignment**
  - `d.attr` is equivalent to `d["attr"]`.
  - `d.attr = value` is equivalent to `d["attr"] = value`.

- **Auto-wrapping on read**
  - When you read a key:
    - If the value is a `dict`, it is replaced in-place with `Dotdict(value)` and returned.
    - If the value is a `list`, any `dict` elements inside are converted in-place to `Dotdict`.

- **Missing keys**
  - Accessing a missing key returns the string pattern `"[~~missing-key-<key>~~]"`.
  - Example:
    ```python
    d = Dotdict({})
    print(d.username)  # [~~missing-key-username~~]
    ```

- **Standard dict behavior**
  - All regular dict operations are supported: iteration, membership checks, updates, etc.
  - Example:
    ```python
    for key, value in d.items():
        print(key, value)
    d.update({"role": "admin"})
    ```

### Edge cases and tips

- **Key name clashes with dict attributes**
  - If a key name matches a dict attribute/method (e.g., `keys`, `items`, `get`), attribute access will refer to the dict method, not your value. Use index access in such cases:
    ```python
    d = Dotdict({"keys": [1, 2, 3]})
    d.keys            # <built-in method keys of Dotdict object>
    d["keys"]        # [1, 2, 3]
    ```

- **Converting back to plain dicts**
  - `dict(d)` returns a shallow dict, but nested values remain `Dotdict` where present. For a deep conversion:
    ```python
    def to_plain_dict(obj):
        if isinstance(obj, Dotdict):
            return {k: to_plain_dict(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_plain_dict(v) for v in obj]
        return obj

    plain = to_plain_dict(d)
    ```

- **Serialization**
  - `Dotdict` is JSON-serializable as long as the underlying values are. If you need to ensure no `Dotdict` instances are present, run the deep conversion above first.

### Additional examples

```python
# Attribute assignment
d = Dotdict({})
d.user = {"name": "Bao"}     # auto-wraps on read
print(d.user.name)             # Bao

# Lists of dicts
d = Dotdict({"items": [{"id": 1}, {"id": 2}]})
print(d.items[0].id)           # 1
print(d.items[1].id)           # 2

# Mixing attribute and index access
profile = Dotdict({"name": "Bao", "links": {"github": "https://github.com/..."}})
print(profile["name"])        # Bao
print(profile.links.github)    # https://github.com/...
```

### Import path

- After install via pip: `from Dotdict import Dotdict`
- Inside this repository (editable install): still `from Dotdict import Dotdict`

### Requirements

- Python 3.10+

### Contributing

Issues and pull requests are welcome. If you spot an edge case or want to propose improvements (e.g., optional strict mode, opt-out of missing-key placeholder), open an issue first to discuss.

### Disclaimer

`Dotdict` trades a bit of strictness for convenience. Prefer explicit key access in production-critical or highly dynamic domains where silent fallbacks could hide errors.