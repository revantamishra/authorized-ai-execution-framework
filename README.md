# Authorized AI Execution Framework

## Overview
This repository contains a research-grade proof-of-concept for enforcing
pre-execution authorization and runtime execution boundaries for AI systems.

Core guarantees:
- AI systems cannot access undeclared data
- AI systems cannot perform undeclared actions
- AI systems cannot execute outside explicitly verified boundaries

## Core Principle
**No implicit behavior.** All AI capabilities must be explicitly declared,
statically verified, and enforced at runtime.

## Architecture
The system is divided into three clearly separated layers:

1. Specification Layer — declarative `AuthorizationSpec` objects
2. Static Verification Engine — deterministic checks that accept/reject specs
3. Constrained Runtime Enforcer — monitored execution enforcing the spec

## Status
Early research prototype. Not intended for production use. This code is built
for clarity, auditability, and as a foundation for experiments and extensions.

## Quickstart
Run the demo from the project root:

```bash
PYTHONPATH=src python3 -m demo.run_demo
```

## License
To be determined.
