# Pyrite-MX

**Pyrite-MX: Focus only on what truly matters. No boilerplate. No distractions.**

## ⚠️ **Pre-Alpha Notice**

**Pyrite-MX** is currently in a **pre-alpha** stage of development. This means:

* Many components are  **incomplete** ,  **unstable** , or  **subject to radical change** .
* Several modules are **purely experimental** and may serve only as  **proofs of concept** .
* The codebase is  **not yet ready for production use** , and may lack documentation, tests, or consistent interfaces.

## About the Project

Pyrite-MX is a modular framework designed to help developers and thinkers  **focus only on what truly matters** . It aims to eliminate boilerplate and distractions by offering a set of composable tools for:

* **Personal knowledge management**
* **Task and project organization**
* **Context-aware data correlation**
* **Custom UI/UX layers (CLI, GUI, WebUI)**

The architecture is built around a set of core modules:

* `pyrite.monolith`: foundational elements like `@element`, `@routine`, and context propagation.
* `pyrite.attract`: a GTD-inspired system with seven lenses— **Areas** ,  **Topics** ,  **Tasks** ,  **Records** ,  **Activities** ,  **Channels** , and  **Trays** —to organize and correlate information.
* `pyrite.gui`, `pyrite.tui`, `pyrite.webui`: interface layers for different interaction modes.

### Philosophy

Pyrite-MX is built with the belief that **clarity, context, and continuity** are essential for meaningful digital workflows. It encourages:

* **Intentional design** over feature creep
* **Contextual awareness** over rigid hierarchies
* **Generational continuity** in software evolution

### Use at Your Own Risk

This repository is shared in the spirit of  **open exploration** . If you’re here, you’re likely curious, adventurous, or looking for inspiration. Feel free to explore, fork, and contribute—but please be aware that:

* Breaking changes are frequent.
* Many ideas are still being tested.
* Stability and performance are not guaranteed.

Feedback, suggestions, and philosophical discussions are welcome.

---

## ANNOTATIONS FOR AUTHOR

###### REMEMBER

`24/08/2025:` to upload to `pypi` from `python 10` is nedded to rollback `twine` to version `6.0.1`

###### TO BUILD AND UPLOAD TO PYPI

```bash
python -m build
twine check dist/*
twine upload dist/*
```
