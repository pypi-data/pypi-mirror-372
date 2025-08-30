[![PyPI version](https://img.shields.io/pypi/v/linegenerator.svg)](https://pypi.org/project/linegenerator/)
[![CodeQL](https://github.com/vldmrdev/linegenerator/actions/workflows/codeql.yml/badge.svg)](https://github.com/vldmrdev/linegenerator/actions/workflows/codeql.yml)
[![Lint & Format](https://github.com/vldmrdev/linegenerator/actions/workflows/linters.yml/badge.svg)](https://github.com/ldmrdev/linegenerator/actions/workflows/linters.yml)
[![Tests](https://github.com/vldmrdev/linegenerator/actions/workflows/tests.yml/badge.svg)](https://github.com/vldmrdev/linegenerator/actions/workflows/tests.yml)

### Line Generator

This is a template-based synthetic string data generator.

### Install

```pip install linegenerator```

### After install

Show commands:

```linegenerator-cli --help```

Show available default generators:

```linegenerator-cli --help-generators```

Install autocompletion:

```linegenerator-cli --install-completion```

Show autocompletion script:

```linegenerator-cli --show-completion```

### Examples:

```linegenerator-cli --template "Hello, {name}, welcome to {city}!" --count 3```

output:

```
Hello, Timothy Lozano, welcome to North Lindaberg!
Hello, Joshua Williams, welcome to New Darrylshire!
Hello, Cody Smith, welcome to East Kimberlyton!
```

### License

[MIT License](LICENSE)
