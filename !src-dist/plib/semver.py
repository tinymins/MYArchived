# -*- coding: utf-8 -*-
"""
semver for Python
Based on the Lua version from Boilerplate_!Base/src/lib/Semver.lua
Supports npm-style version constraints like ^, ~, *, etc.
"""

import re
from typing import Optional, Union, List, Tuple


class SemverError(Exception):
    """Semver related errors"""

    pass


def _check_positive_integer(number: int, name: str) -> None:
    """Check if number is a positive integer"""
    if number < 0:
        raise SemverError(f"{name} must be a valid positive number")
    if not isinstance(number, int):
        raise SemverError(f"{name} must be an integer")


def _present(value: Optional[str]) -> bool:
    """Check if value is present and not empty"""
    return value is not None and value != ""


def _split_by_dot(s: str) -> List[str]:
    """Split string by dots"""
    if not s:
        return []
    return [part for part in s.split(".") if part]


def _parse_prerelease_and_build_with_sign(
    s: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Parse prerelease and build with their signs"""
    # Try to match both prerelease and build
    match = re.match(r"^(-[^+]+)(\+.+)$", s)
    if match:
        return match.group(1), match.group(2)

    # Try to match only prerelease
    match = re.match(r"^(-.+)$", s)
    if match:
        return match.group(1), None

    # Try to match only build
    match = re.match(r"^(\+.+)$", s)
    if match:
        return None, match.group(1)

    if s:
        raise SemverError(
            f"The parameter '{s}' must begin with + or - to denote a prerelease or a build"
        )

    return None, None


def _parse_prerelease(prerelease_with_sign: Optional[str]) -> Optional[str]:
    """Parse prerelease from string with sign"""
    if not prerelease_with_sign:
        return None

    match = re.match(r"^-(\w[\w.-]*)$", prerelease_with_sign)
    if not match:
        raise SemverError(
            f"The prerelease '{prerelease_with_sign}' is not a dash followed by alphanumerics, dots and dashes"
        )

    return match.group(1)


def _parse_build(build_with_sign: Optional[str]) -> Optional[str]:
    """Parse build from string with sign"""
    if not build_with_sign:
        return None

    match = re.match(r"^\+(\w[\w.-]*)$", build_with_sign)
    if not match:
        raise SemverError(
            f"The build '{build_with_sign}' is not a + sign followed by alphanumerics, dots and dashes"
        )

    return match.group(1)


def _parse_prerelease_and_build(s: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse prerelease and build from string"""
    if not _present(s):
        return None, None

    prerelease_with_sign, build_with_sign = _parse_prerelease_and_build_with_sign(s)
    prerelease = _parse_prerelease(prerelease_with_sign)
    build = _parse_build(build_with_sign)

    return prerelease, build


def _parse_version(s: str) -> Tuple[int, int, int, Optional[str], Optional[str]]:
    """Parse version string into components"""
    match = re.match(r"^(\d+)\.?(\d*)\.?(\d*)(.*)$", s)
    if not match:
        raise SemverError(f"Could not extract version number(s) from '{s}'")

    major_str, minor_str, patch_str, prerelease_and_build = match.groups()

    major = int(major_str)
    minor = int(minor_str) if minor_str else 0
    patch = int(patch_str) if patch_str else 0

    prerelease, build = _parse_prerelease_and_build(prerelease_and_build)

    return major, minor, patch, prerelease, build


def _compare(a, b):
    """Compare two values, return -1, 0, or 1"""
    if a == b:
        return 0
    return -1 if a < b else 1


def _compare_ids(my_id: Optional[str], other_id: Optional[str]) -> int:
    """Compare two version component IDs"""
    if my_id == other_id:
        return 0
    if my_id is None:
        return -1
    if other_id is None:
        return 1

    # Try to convert to numbers
    try:
        my_number = int(my_id)
        try:
            other_number = int(other_id)
            # Both are numbers
            return _compare(my_number, other_number)
        except ValueError:
            # my_id is number, other_id is not
            return -1
    except ValueError:
        try:
            int(other_id)
            # my_id is not number, other_id is number
            return 1
        except ValueError:
            # Both are strings
            return _compare(my_id, other_id)


def _smaller_id_list(my_ids: List[str], other_ids: List[str]) -> bool:
    """Check if my_ids list is smaller than other_ids list"""
    my_length = len(my_ids)

    for i in range(my_length):
        if i >= len(other_ids):
            break
        comparison = _compare_ids(my_ids[i], other_ids[i])
        if comparison != 0:
            return comparison == -1

    return my_length < len(other_ids)


def _smaller_prerelease(mine: Optional[str], other: Optional[str]) -> bool:
    """Check if mine prerelease is smaller than other"""
    if mine == other or mine is None:
        return False
    if other is None:
        return True

    return _smaller_id_list(_split_by_dot(mine), _split_by_dot(other))


class Semver:
    """Semantic version class"""

    def __init__(
        self,
        major: Union[int, str],
        minor: int = 0,
        patch: int = 0,
        prerelease: Optional[str] = None,
        build: Optional[str] = None,
    ):
        if isinstance(major, str):
            major, minor, patch, prerelease, build = _parse_version(major)

        _check_positive_integer(major, "major")
        _check_positive_integer(minor, "minor")
        _check_positive_integer(patch, "patch")

        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

    def next_major(self) -> "Semver":
        """Get next major version"""
        return Semver(self.major + 1, 0, 0)

    def next_minor(self) -> "Semver":
        """Get next minor version"""
        return Semver(self.major, self.minor + 1, 0)

    def next_patch(self) -> "Semver":
        """Get next patch version"""
        return Semver(self.major, self.minor, self.patch + 1)

    def __eq__(self, other: "Semver") -> bool:
        """Check equality (build is ignored)"""
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: "Semver") -> bool:
        """Check if less than"""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        return _smaller_prerelease(self.prerelease, other.prerelease)

    def __le__(self, other: "Semver") -> bool:
        """Check if less than or equal"""
        return self < other or self == other

    def __gt__(self, other: "Semver") -> bool:
        """Check if greater than"""
        return not (self <= other)

    def __ge__(self, other: "Semver") -> bool:
        """Check if greater than or equal"""
        return not (self < other)

    def __pow__(self, other: "Semver") -> bool:
        """Caret operator: check if other is backwards-compatible with self"""
        if self.major == 0:
            return self == other
        return self.major == other.major and self.minor <= other.minor

    def __str__(self) -> str:
        """String representation"""
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            result += f"-{self.prerelease}"
        if self.build:
            result += f"+{self.build}"
        return result

    def satisfies(self, range_str: str) -> bool:
        """Check if this version satisfies the given range"""
        # Handle OR conditions (||)
        if "||" in range_str:
            for part in range_str.split("||"):
                if self.satisfies(part.strip()):
                    return True
            return False

        # Handle AND conditions (space separated)
        range_str = re.sub(r"\s+", " ", range_str.strip())

        if " " in range_str:
            parts = range_str.split(" ")
            i = 0
            while i < len(parts):
                # Handle hyphen ranges: X.Y.Z - A.B.C
                if i + 2 < len(parts) and parts[i + 1] == "-":
                    if not self.satisfies(f">={parts[i]}"):
                        return False
                    if not self.satisfies(f"<={parts[i + 2]}"):
                        return False
                    i += 3
                else:
                    if not self.satisfies(parts[i]):
                        return False
                    i += 1
            return True

        # Single comparator
        range_str = range_str.lstrip("=v")

        # Handle wildcards
        if range_str == "" or range_str == "*":
            return self.satisfies(">=0.0.0")

        # Find where the version number starts
        pos = 0
        for i, char in enumerate(range_str):
            if char.isdigit():
                pos = i
                break
        else:
            raise SemverError(f"Version range must start with number: {range_str}")

        operator = range_str[:pos] if pos > 0 else "="
        version_str = range_str[pos:]

        # Handle X-ranges (1.2.x, 1.X, 1.2.*)
        version_str = re.sub(r"\.[xX*]", "", version_str)
        x_range = max(0, 2 - version_str.count("."))

        # Pad with .0 for missing components
        for _ in range(x_range):
            version_str += ".0"

        sv = Semver(version_str)

        # Handle different operators
        if operator == "<":
            return self < sv
        elif operator == "<=":
            if x_range > 0:
                if x_range == 1:
                    sv = sv.next_minor()
                elif x_range == 2:
                    sv = sv.next_major()
                return self < sv
            return self <= sv
        elif operator == ">":
            if x_range > 0:
                if x_range == 1:
                    sv = sv.next_minor()
                elif x_range == 2:
                    sv = sv.next_major()
                return self >= sv
            return self > sv
        elif operator == ">=":
            return self >= sv
        elif operator == "=":
            if x_range > 0:
                if self < sv:
                    return False
                if x_range == 1:
                    sv = sv.next_minor()
                elif x_range == 2:
                    sv = sv.next_major()
                return self < sv
            return self == sv
        elif operator == "^":
            # Caret ranges
            if sv.major == 0 and x_range < 2:
                if sv.minor == 0 and x_range < 1:
                    return (
                        self.major == 0
                        and self.minor == 0
                        and self >= sv
                        and self < sv.next_patch()
                    )
                return self.major == 0 and self >= sv and self < sv.next_minor()
            return self.major == sv.major and self >= sv and self < sv.next_major()
        elif operator == "~":
            # Tilde ranges
            if self < sv:
                return False
            if x_range == 2:
                return self < sv.next_major()
            return self < sv.next_minor()
        else:
            raise SemverError(f"Invalid operator found: {operator}")


def parse(version_str: str) -> Semver:
    """Parse a version string into a Semver object"""
    return Semver(version_str)


def satisfies(version: Union[str, Semver], range_str: str) -> bool:
    """Check if a version satisfies a range"""
    if isinstance(version, str):
        version = parse(version)
    return version.satisfies(range_str)
