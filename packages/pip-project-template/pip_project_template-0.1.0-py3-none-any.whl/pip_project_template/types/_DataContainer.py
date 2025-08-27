#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-27 01:54:08 (ywatanabe)"
# File: /home/ywatanabe/proj/pip-project-template/src/types/_DataContainer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./pip-project-template/src/types/_DataContainer.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Simple data class using @dataclass decorator."""

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class DataContainer:
    """Minimal data class container with @dataclass decorator."""

    name: str
    value: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        return asdict(self)


def main():
    obj = DataContainer("test", 42)
    print(obj.to_dict())


if __name__ == "__main__":
    main()

# EOF
