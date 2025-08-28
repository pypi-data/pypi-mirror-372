Minimal working example of a packaged Python project. Key integrations include:

- Build System ([Poetry](https://python-poetry.org/)).
- Test Framework ([PyTest](https://docs.pytest.org/en/7.4.x/)).
- Auto-docs with Markdown and ReST support ([pdoc](https://pdoc.dev/)).
- CI/CD ([GitHub Actions](https://docs.github.com/en/actions)).


## Contents

- [Contents](#contents)
- [Structure](#structure)
- [Markdown and ReST support](#markdown-and-rest-support)
- [Data models](#data-models)
- [Advanced tools](#advanced-tools)


## Structure

[Documentation](https://poetry-demo.python.jambazid.dev) is generated from Python docstrings and takes a structure mirroring
that of the source code (API documentation).

Initial focus could be on high-level (public) APIs intended for direct use by end-users.

Developers can thus grow the documentation organically within a single task-based workflow.
As soon as a new feature/function is added - the developer need only include a docstring
in their commit and it will reflect in the hosted page.


## Markdown and ReST support

The [`pdoc`](https://pdoc.dev/) framework renders Markdown in docstrings to HTML:

- Lists
- Are
- Supported

As are code blocks:

```python
# Example invocation

result: Type = function(param="value", *variadic_args, **variadic_kwargs)
```


## Data models

The [`pydantic`](https://docs.pydantic.dev/latest/) framework has quickly become the leading
data validation library for Python.

It's not a stretch to say that there's [a whole ecosystem](https://github.com/Kludex/awesome-pydantic) being built around it with everything
from web frameworks to data science toolkits using it as the base for their data models.

From a documentation perspective, if you can describe your data source as a [`pydantic`](https://docs.pydantic.dev/latest/) derived
[data model](https://docs.pydantic.dev/latest/concepts/models/) and then group them accordingly
such links could be fronted as data schemas. Standard representations such as ["JSON Schema"](https://json-schema.org/) can
be generated directly from [`pydantic`](https://docs.pydantic.dev/latest/) models.

This also has [advantages for testing](https://pandera.readthedocs.io/en/stable/data_synthesis_strategies.html#usage-in-unit-tests).


## Advanced tools

The [`pdoc`](https://pdoc.dev/) framework is arguably the simplest auto-documentation tool for Python.

Below are some more advanced tools that are popular with large open-source projects:

- [mkdocstrings](https://mkdocstrings.github.io/)
- [Sphinx](https://www.sphinx-doc.org/en/master/)