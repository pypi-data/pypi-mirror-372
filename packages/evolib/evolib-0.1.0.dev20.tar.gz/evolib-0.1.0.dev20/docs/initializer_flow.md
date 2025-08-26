# Initializer Mechanism in EvoLib

This document explains the logic behind EvoLib’s two-stage initializer mechanism and clarifies why each initializer receives both the configuration and (optionally) the current `Pop` instance. This design provides full flexibility for advanced initialization strategies, while remaining easy to use for simpler cases.

---

## 🧭 Overview

All parameter initializers in EvoLib follow a unified two-stage structure:

ParaInitializer = Callable[[dict], Callable[[Pop], ParaBase]]

This means:
1. The first stage processes the configuration (`cfg: dict`)
2. The second stage creates a `ParaBase` instance (e.g., `ParaVector`) from a given `Pop`

---

## 🔍 Why is `Pop` passed to the initializer?

In many cases, the `Pop` object is not required for initialization.  
However, including it in the interface allows advanced or custom initializers to access dynamic population-level information such as:

- pop.generation_num
- pop.parents
- pop.selection_strategy
- pop.elites
- logging IDs or contextual seeding

This enables:

Use Case                        | Benefit
-------------------------------|------------------------------------------
Diversity-based initialization | Seed from existing population
Elite seeding                  | Start new individuals near top performers
Co-evolutionary pairing        | Initialize based on another population
Traceable/reproducible seeding| Use logging context or run state

---

## ✅ Convention: `(_: Pop) → ParaBase`

If your initializer does **not** use the `Pop` argument, follow this convention:

def init_fn(_: Pop) -> ParaVector:
    ...

- The underscore `_` signals to human readers and linters that the parameter is intentionally unused
- The type annotation `: Pop` ensures full compatibility with EvoLib's initializer system and type checkers (e.g., `mypy`)

---

## 🧪 Example: Pop-independent initializer

def zero_initializer(cfg: dict) -> Callable[[Pop], ParaVector]:
    dim = int(cfg["dim"])

    def init_fn(_: Pop) -> ParaVector:
        return ParaVector(vector=np.zeros(dim))

    return init_fn

---

## 🧬 Example: Pop-dependent initializer

def diversity_seeded_initializer(cfg: dict) -> Callable[[Pop], ParaVector]:
    def init_fn(pop: Pop) -> ParaVector:
        dim = int(cfg["dim"])
        seed = np.mean([indiv.para.vector for indiv in pop.parents], axis=0)
        vector = seed + np.random.normal(0, 0.1, size=dim)
        return ParaVector(vector=vector)

    return init_fn

---

## 🧾 Summary

Aspect                    | Design decision
--------------------------|----------------------------
Unified initializer type  | Callable[[dict], Callable[[Pop], ParaBase]]
`Pop` usage               | Optional, but always passed
When `Pop` is unused      | Use `_: Pop`
Motivation                | Full flexibility with consistent interface

This ensures that all initializers—whether minimal or sophisticated—can be treated uniformly by EvoLib's population system.
