# Pylitex

This is a Python api library for Litex core, which aims to help Python users to interact with Litex core.

## installation

This reuqires **Litex core** and Python(version >= 3.12), you could install Litex core follow the [Installation](https://litexlang.org/doc/Installation).

After Litex core installation, you could install litex for your python environment:

```bash
# remember to install Litex core before install pylitex
# change your Python env to which your are using
# then run following commands
pip install pylitex
```

## usage

Import `pylitex` as you installed.

```python
import pylitex
```

### run fill code

```python
# run full code
result = pylitex.run("code...")

# run full codes with multi-process
results = pylitex.run_batch(["code1...", "code2..."], 2)
```

### run continuous codes

```python
# run continuous codes in one litex env
litex_runner = pylitex.Runner()
result1 = litex_runner.run("code1...")
result2 = litex_runner.run("code2...")
litex_runner.close()

# run continuous code in litex multi-process pool
litex_pool = pylitex.RunnerPool()
litex_pool.inject_code({id: "id1", code: "code1..."})
litex_pool.inject_code({id: "id2", code: "code2..."})
litex_pool.inject_code({id: "id1", code: "code3..."})
litex_pool.inject_code({id: "id1", code: "code4..."})
litex_pool.inject_code({id: "id2", code: "code5..."})
results = litex_pool.get_results()
litex_pool.close()
```

### return type

For `pylitex.run()` and `pylitex.Runner().run()`, the return type is a python `dict` like (Call it `pylitexResult`):

```json
{"success": boolean, "payload": str, "message": str}
```

For `pylitex.run_batch()`, the return type is a python `list[pylitexResult]` like:

```json
[
    {"success": boolean, "payload": str, "message": str},
    {"success": boolean, "payload": str, "message": str},
    ...
]
```

For `pylitex.RunnerPool().get_results()`, the return type is a python `dict[list[pylitexResult]]` like:

```json
{
    "id1": [
        {"success": boolean, "payload": str, "message": str},
        {"success": boolean, "payload": str, "message": str},
        {"success": boolean, "payload": str, "message": str},
        ...
    ],
    "id2": [
        {"success": boolean, "payload": str, "message": str},
        {"success": boolean, "payload": str, "message": str},
        ...
    ],
    ...
}
```
