# Package root: src/

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CheckResult:
    checker_name: str
    passed: bool
    violations: List[str]
