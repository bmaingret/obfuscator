"""Obfuscation technique protocol and concrete implementation."""

import re
from abc import abstractmethod
from typing import Protocol

from obfuscator import ctools


class Technique(Protocol):
    """Technique Protocol. A single class method `apply` that applied the
    technique to the source code and returns transformed code.
    """

    @classmethod
    @abstractmethod
    def apply(cls, source_code: str) -> str:
        pass


class PassthroughTechnique:
    """Passthrough technique, mostly for testing."""

    @classmethod
    def apply(cls, source_code: str) -> str:
        return source_code


class ReplacingTechnique(Technique):
    """Base class when the technique is a simple regex
    pattern_matcher/substitution.
    Two class attributes are defined as @property and must defined
    in subclasses.

    Attributes:
        PATTERN (str): regex pattern for matching
        REPLACEMENT (str): replacement pattern for substitution. Can use
        groups defined in pattern.
    """

    @classmethod
    @property
    @abstractmethod
    def PATTERN(cls):
        """Regex pattern for matching"""
        return NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def REPLACEMENT(cls):
        """replacement pattern for substitution. Can use
        groups defined in pattern."""
        return NotImplementedError

    @classmethod
    def apply(cls, source_code: str) -> str:
        """Transform the source code by using regex
        PATTERN.sub(REPLACEMENT, source_code)

        Args:
            source_code (str): source code

        Returns:
            str: transformed source code
        """
        compiled_pattern = re.compile(cls.PATTERN)
        obfuscated = compiled_pattern.sub(cls.REPLACEMENT, source_code)
        return obfuscated


class RemoveSpacesTechnique(ReplacingTechnique):
    """Remove spaces keeping source code compilable"""

    PATTERN = r"\s*([\n=\+\-\*\^,\){};]|(?<!\*)\/(?!\*))\s*"
    REPLACEMENT = r"\1"


class ReplaceAdditionTechnique(ReplacingTechnique):
    """Replace addition in line. Work for chained addition (ex: 'a+b+c+d')"""

    PATTERN = r"(\w+)\s*(\+)\s*(\w+)(\s*)"
    REPLACEMENT = r"(-(-\1 + (-\3)))\4"


class ReplaceXORTechnique(ReplacingTechnique):
    """Replace XOR operator. Only works for single operation
    (ex: 'a = b ^ c;')"""

    PATTERN = r"(\w+)\s*=\s*(\w+)\s*(?:\^)\s*(\w+)\s*;"
    REPLACEMENT = r"\1 = (~\2 & \3) | (\2 & ~\3);"


class ReplaceSingleAdditionTechnique(ReplacingTechnique):
    """Replace addition using a generated random number.
    Only works for single operation (ex: 'a = b + c;')"""

    PATTERN = r"(\w+)\s*=\s*(\w+)\s*(?:\+)\s*(\w+)\s*;"
    REPLACEMENT = r"r = rand (); \1 = \2 + r; \1 = \1 + \3; \1 = \1 - r;"

    @classmethod
    def apply(cls, source_code: str) -> str:
        """Overrides the default to include the 'stdlib.h' in includes
        if not already present.

        Args:
            source_code (str): source code

        Returns:
            str: transformed source code
        """
        obfuscated = super().apply(source_code)
        return ctools.insert_lib(obfuscated, "stdlib.h")
