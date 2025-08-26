# SPDX-FileCopyrightText: 2024-present Minddistrict <info@minddistrict.com>
#
# SPDX-License-Identifier: MIT

import pathlib
import re
from dataclasses import dataclass, field
from functools import wraps

from packaging.version import Version, parse

REQUIREMENTS_TXT_RE = re.compile("^(.+)==(.+)")
VERSION_CFG_RE = re.compile("^(.+) ?= ?(.+)")


def cleanup(func):
    """Decorator: Clean up config file internals after function call."""

    @wraps(func)
    def _cleanup(self):
        try:
            return func(self)
        finally:
            self.r_txt.reset()
            self.v_cfg.reset()

    return _cleanup


@dataclass
class VersionsCfgRequirementsTxtSync:
    """Keep a versions.cfg in sync with a requirements.txt file."""

    requirements_txt: str
    version_cfg: str
    versions_section: str = "versions"

    def __post_init__(self):
        self.r_txt = RequirementsTxt(
            pathlib.Path(self.requirements_txt).resolve()
        )
        self.v_cfg = VersionCfg(
            pathlib.Path(self.version_cfg).resolve(), self.versions_section
        )

    @cleanup
    def in_sync(self) -> bool:
        """Tell whether requirements.txt and version.cfg are in sync."""
        r_exhausted = False
        v_exhausted = False
        while True:
            try:
                r_package, r_version = next(self.r_txt)
            except StopIteration:
                r_exhausted = True
            try:
                v_package, v_version = next(self.v_cfg)
            except StopIteration:
                v_exhausted = True
            if r_exhausted != v_exhausted:
                return False
            if r_exhausted and v_exhausted:
                return True
            if v_package != r_package:
                return False
            if v_version != r_version:
                return False

    def update(self) -> None:
        """Re-sync out of sync config files."""
        try:
            self._sync()
            print(f"Synced {self.v_cfg.path} to {self.r_txt.path}.")
        except ReferenceError:
            self._recreate()
            print(f"Recreated {self.r_txt.path}.")

    @cleanup
    def _sync(self):
        """Synchronize requirements.txt with version.cfg."""
        r_exhausted = False
        v_exhausted = False
        r_package = "none"
        while True:
            try:
                r_package, r_version = next(self.r_txt)
            except StopIteration:
                r_exhausted = True
            try:
                v_package, v_version = next(self.v_cfg)
            except StopIteration:
                v_exhausted = True
            if r_exhausted and v_exhausted:
                self.r_txt.write()
                self.v_cfg.write()
                return
            if r_package != v_package:
                msg = (
                    f"Package entries out of order: {r_package} !="
                    f" {v_package}. Please recreate {self.requirements_txt}."
                )
                raise ReferenceError(msg)
            if r_version > v_version:
                self.v_cfg.update_current(r_version)
            elif v_version > r_version:
                self.r_txt.update_current(v_version)

    @cleanup
    def _recreate(self):
        """Re-create requirements.txt from version.cfg."""
        self.r_txt.clean()
        for v_package, v_version in self.v_cfg:
            self.r_txt.append(v_package, v_version)
        self.r_txt.write()


@dataclass
class ConfigFile:
    """Abstract base class to model config files."""

    path: pathlib.Path
    line_pointer: int = field(init=False, default=-1)
    lines: list[str] = field(init=False)

    def __post_init__(self):
        """Configure the instance."""
        if not self.path.exists():
            msg = f"{self.path!r} does not exist."
            raise FileNotFoundError(msg)
        self.reset()

    def __next__(self) -> tuple[str, Version]:
        """Return the next package, version tuple."""
        self.line_pointer += 1
        try:
            return self._parse_current_line()
        except EOFError:
            raise StopIteration from None

    def __iter__(self):
        """Make ourselves an iterator as we provide __next__."""
        return self

    @property
    def current_line(self):
        """Return the contents of the line the line_pointer points to."""
        return self.lines[self.line_pointer]

    @current_line.setter
    def current_line(self, value):
        """Change the contents of the line the line_pointer points to."""
        self.lines[self.line_pointer] = value

    @property
    def exhausted(self):
        """Return whether we read till at the end of the file."""
        return self.line_pointer >= len(self.lines)

    def update_current(self, version: Version):
        """Update the version of the current line."""
        self.current_line = self._format(self._parse_current_line()[0], version)

    def write(self):
        """Write changes back to the file."""
        self.path.write_text("\n".join(self.lines) + "\n")

    def reset(self):
        """Reset the internal representation to the beginning of the data."""
        self.line_pointer = -1
        self.lines = self.path.read_text().splitlines()
        self._skip_header()

    def clean(self):
        """Clean the file contents in internal representation."""
        self.lines = []
        self.line_pointer = -1

    def append(self, package: str, version: Version):
        """Add a (package, version) at the end."""
        self.line_pointer += 1
        self.lines.append(self._format(package, version))

    def _parse_current_line(self) -> tuple[str, Version]:
        """Parse a version line into package (name, version).

        Omit empty lines and comments.
        """
        if self.exhausted:
            raise EOFError
        while self.current_line.startswith("#") or not self.current_line:
            self.line_pointer += 1
            if self.exhausted:
                raise EOFError
        match = self.LINE_MATCHER.match(self.current_line)
        try:
            package, version = match.groups()
        except AttributeError:
            if self.current_line.startswith("[versions:python"):
                error = EOFError
            else:
                error = SyntaxError(
                    f"Cannot parse: {self.path}:{self.line_pointer + 1}"
                    f" {self.current_line}"
                )
            raise error from None
        return package.strip(), parse(version)


class RequirementsTxt(ConfigFile):
    """A requirements.txt configuration file."""

    LINE_MATCHER = REQUIREMENTS_TXT_RE

    def _skip_header(self):
        pass

    def _format(self, package: str, version: Version):
        return f"{package}=={version}"


@dataclass
class VersionCfg(ConfigFile):
    """A version.cfg configuration file."""

    LINE_MATCHER = VERSION_CFG_RE
    versions_section: str = "versions"

    def _skip_header(self):
        while not self.current_line.startswith(f"[{self.versions_section}]"):
            self.line_pointer += 1

    def _format(self, package: str, version: Version):
        return f"{package} = {version}"
