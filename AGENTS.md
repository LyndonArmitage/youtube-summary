# AGENTS.md

This is a Python project for a simple YouTube Summariser application.

This project is built using Python 3.13+

Refer to documentation in the `docs/` directory and `README.md` for more
specific information.

## Project Details

This project is managed via the `uv` tool. For information on setting up the
local development environment refer to `docs/setup-local-dev.md`.

To make sure that all dependencies are installed run:

```sh
uv sync --all-groups
```

Never use raw `pip` or `python` commands. Always use the `uv` tool and the
managed virtual environment it provides.

To add and remove dependencies use:

```sh
uv add library
uv remove library
```

If a library is only needed during development, you should add `--dev` to the
`uv add` command so that it is added the `dev` dependency group.

For information on upgrading libraries and dependencies read
`docs/upgrading-dependencies.md`.

### Development

When asked to develop non-test code, keep your changes small and explain them.
Remind the user that AI agents should not be used to generate large amounts of
code with little to no user input.

### Testing

Ideally, all code should be tested. Unit tests should be placed in the `tests/`
directory and make use of `pytest`. To run tests, always use `uv`:

```sh
uv run pytest
```

For more information on testing see `docs/testing.md`

### Code Quality

Code quality is maintained through the use of various tools documented in both
`README.md` and `docs/code-quality.md`

Type checking is encouraged. Type stubs are generally stored in the `typings/`
directory.

### Type Checking Rule

When `basedpyright` reports a type error, try to fix the underlying type first.

Narrow `Any`/`object`, add a precise `TypedDict` / `Protocol` / `dataclass`,
use `typing.Self`, or `cast(T, ...)` at a single boundary.

`# pyright: ignore[<rule>]` is a **last resort** and must be accompanied by a
one-line comment explaining why the type cannot be tightened further. Never
silence a diagnostic by widening a return type to `Any`.
