# 🤝 Contributing to CausalLLM

Welcome to **CausalLLM** — a powerful and modular library designed to bridge the gap between causal inference and large language models. Whether you're a student, data scientist, AI researcher, or developer, your contributions help push the boundaries of responsible, explainable, and impactful AI.

We’re building a vibrant and inclusive community, and we’re thrilled to have you join us. 🚀

---

## 🌟 Mission Areas You Can Contribute To

We welcome contributions across a range of needs. Choose what excites you the most:

### 🐛 Bug Reports and Feature Requests

* Found a bug? File a detailed issue with reproduction steps.
* Have an idea for a new feature? Open a feature request explaining its use case and how it fits our causal inference mission.

### 📝 Documentation Improvements

* Help improve clarity in docstrings, READMEs, and tutorials.
* Fix typos, add missing explanations, or rework tricky sections.
* Translate docs (coming soon: localization initiative).

### 🧪 Test Cases and Examples

* Add or improve unit tests to increase reliability.
* Submit Jupyter notebooks showing real-world causal workflows.
* Help us test edge cases and new backends (OpenAI, LLaMA, Grok).

### 💡 New Algorithms and Methods

* Submit new estimators, SCM structures, or causal discovery algorithms.
* Propose novel integrations with existing LLMs or causal packages.
* Follow our modular plugin design to add your own module.

### 🌍 Community Support and Tutorials

* Answer questions in Discussions or Discord.
* Create beginner-friendly YouTube tutorials, blog posts, or code demos.
* Organize local workshops or study groups.

---

## 📌 Getting Started

1. **Fork** the repository and clone it locally.
git clone https://github.com/rdmurugan/causallm.git
cd causallm

3. Install dependencies:

   ```bash
   pip install -e .[dev]
   ```
4. Run tests to confirm your setup:

   ```bash
   pytest tests/
   ```
5. Make your changes in a new branch:

   ```bash
   git checkout -b my-feature-branch
   ```

---

## ✅ Contribution Guidelines

* Follow **PEP8** for Python style. Run `black` before submitting.
* Use clear commit messages: `fix:`, `feat:`, `docs:`, etc.
* Keep pull requests focused and small. One feature/fix per PR.
* Always write or update unit tests for your changes.
* Document your feature with code comments and docstrings.

---

## 🧪 Running Tests

We use `pytest` and `mypy` for type checking. Before submitting, run:

```bash
pytest tests/
mypy causalllm/
```

---

## 💬 Join the Community

* 📣 [GitHub Discussions](https://github.com/rdmurugan/causalllm/discussions)
* 💬 Discord server - [Join our community](https://discord.gg/d4zD76hb)

---

## 🛡️ Code of Conduct

We are committed to a welcoming and harassment-free experience. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for contributing to **CausalLLM** — together, we're redefining what it means to reason intelligently with machines. 🧠📊

— The CausalLLM Core Team
