# minitap — Python Meta‑Package

A lightweight meta-package that installs Minitap Python libraries under one name. Today it bundles the mobile automation project: `minitap-mobile-use`.

- Website: https://minitap.ai/
- Source (mobile-use): https://github.com/minitap-ai/mobile-use
- Python: >= 3.10

## What you get

Installing `minitap` pulls in:

- `minitap-mobile-use` — Control Android/iOS devices using natural language. After install, its code is available via `import minitap.mobile_use` (exposed by the dependency itself).

## Install

```bash
pip install minitap
```

## Usage

```python
# The dependency exposes this namespace:
import minitap.mobile_use

# See full usage and examples here:
# https://github.com/minitap-ai/mobile-use
```

## About mobile-use

Mobile-use is an open-source AI agent that:
- Understands natural language instructions
- Navigates app UIs
- Can scrape and return structured data (e.g., JSON)
- Is configurable with different LLMs

Benchmarks and details: https://minitap.ai/research/mobile-ai-agents-benchmark

## Why a meta‑package?

`minitap` provides a single pip install that brings in Minitap public Python packages. There is no runtime API in this package itself; it only manages dependencies.

## Links

- Website: https://minitap.ai/
- Source (mobile-use): https://github.com/minitap-ai/mobile-use
- Issues/Support: please open issues on the mobile-use repo.

## License

Each included project follows its own license. See the respective repositories for details.