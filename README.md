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

## Threat Model

What we prevent:
- AI systems accessing undeclared data sources (static + runtime verified)
- AI systems performing undeclared actions (static verified)
- Execution beyond declared iteration limits (runtime enforced)
- Data accumulation beyond declared size limits (runtime enforced)
- Task execution beyond declared timeout (runtime enforced)

## Trust Boundary

**Trusted code:**
- The authorization specification (AuthorizationSpec object)
- The static verification engine (ensures all specs are well-formed)
- The runtime monitoring layer (MonitoredContext enforces boundaries)

**Untrusted code:**
- All AI task functions (the code being executed under authorization)
- Task implementations have no direct access to resources outside MonitoredContext

## Limitations

- No cryptographic verification of specifications (honor system on declaration)
- Data size tracking is per-operation (not cumulative transaction cost)
- Timeout enforced via wall-clock monotonic time (not CPU time)
- No sandboxing of untrusted code (relies on Python semantics + MonitoredContext)
- Task must explicitly call ctx.tick() and ctx.read_input() (not transparent interception)

## Quickstart
Run the demo from the project root:

```bash
PYTHONPATH=src python3 -m demo.run_demo
```

## License
To be determined.
