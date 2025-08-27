# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
import contextlib
from dataclasses import dataclass, field
from typing import List, Optional

@contextlib.contextmanager
def _argv_context(target_argv: List[str]):
    original = sys.argv
    try:
        sys.argv = target_argv
        yield
    finally:
        sys.argv = original

@dataclass
class PhicodeArgs:
    module_or_file: str = "main"
    debug: bool = False
    bypass: bool = False
    remaining_args: List[str] = field(default_factory=list)
    interpreter: Optional[str] = None
    list_interpreters: bool = False
    show_versions: bool = False
    version: bool = False
    benchmark: bool = False
    _original_argv: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self._original_argv:
            self._original_argv = sys.argv.copy()

    @property
    def should_exit_early(self) -> bool:
        return any([self.version, self.list_interpreters, self.interpreter, self.benchmark and not self.module_or_file])

    def get_module_argv(self) -> List[str]:
        return ['__main__'] + self.remaining_args

_current_args: Optional[PhicodeArgs] = None
_is_switched_execution = False

def get_current_args() -> Optional[PhicodeArgs]:
    return _current_args

def is_switched_execution() -> bool:
    return _is_switched_execution

def _set_current_args(args: PhicodeArgs):
    global _current_args
    _current_args = args

def _set_switched_execution(switched: bool):
    global _is_switched_execution
    _is_switched_execution = switched