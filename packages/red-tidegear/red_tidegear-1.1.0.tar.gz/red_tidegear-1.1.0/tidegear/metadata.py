# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""This module contains metadata objects for keeping track of cog information."""

import re
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Literal, Self, overload

import orjson
from furl import furl
from typing_extensions import override


@total_ordering
@dataclass
class SemVer:
    """A simple dataclass for storing [Semantic Versioning](https://semver.org/) version numbers.

    Example:
        ```python
        from tidegear.metadata import SemVer

        version = SemVer.from_str("6.27.394-rc1")
        print(version.as_tuple())  # (6, 27, 394, '-rc1', None)
        print(version)  # 6.27.394-rc1
        ```

    Attributes:
        major: The major version number.
        minor: The minor version number.
        patch: The patch version number.
        extra: Any extra information that this version number contains. This isn't used in numerical comparison checks.
        commit: The commit that this version number contains. This isn't used in numerical comparison checks.
            This is not set by the [`SemVer.from_str`][tidegear.metadata.SemVer.from_str] method, to simplify regex parsing.
            As such, this should usually only be set for the SemVer object accessible at
            [`tidegear.version.version`][], and only on development builds.
    """

    major: int
    minor: int
    patch: int
    extra: str | None = None
    commit: str | None = None

    @override
    def __str__(self) -> str:
        """Return the fully qualified version string."""
        string = f"{self.major}.{self.minor}.{self.patch}"
        if self.extra:
            string += f"{self.extra}"
        if self.commit:
            string += f"+{self.commit}"
        return string

    def __gt__(self, other: Self) -> bool:
        """Compare a semver version to another semver version. Ignores `extra` and `commit`.

        Returns:
            Whether or not this SemVer is a higher version than the passed SemVer object.
        """
        if not isinstance(other, SemVer):
            return NotImplemented
        return self.as_tuple(num_only=True) > other.as_tuple(num_only=True)

    @overload
    def as_tuple(self, num_only: Literal[True]) -> tuple[int, int, int]: ...
    @overload
    def as_tuple(self, num_only: Literal[False] = False) -> tuple[int, int, int, str | None, str | None]: ...

    def as_tuple(self, num_only: bool = False) -> tuple[int, int, int, str | None, str | None] | tuple[int, int, int]:
        """Return the SemVer as a tuple, for use in other tooling or for easier comparisons.

        Args:
            num_only: Whether or not to include the contents of `extra` and `commit` in the tuple.

        Returns:
            The created tuple.
        """
        if num_only:
            return (self.major, self.minor, self.patch)
        return (self.major, self.minor, self.patch, self.extra, self.commit)

    @classmethod
    def from_str(cls, version: str, /) -> Self:
        """Parse a version string and return a SemVer object.

        Args:
            version: The version string to parse.

        Raises:
            ValueError: If the version string does not match the expected regex pattern; see implementation for the pattern.

        Returns:
            (SemVer): The created SemVer object.
        """
        pattern = r"^(\d+)\.(\d+)\.(\d+)([-+].+)?$"
        m = re.match(pattern, version)
        if not m:
            msg = f"Invalid SemVer string: {version!r}"
            raise ValueError(msg)
        major, minor, patch, extra = m.groups()
        return cls(int(major), int(minor), int(patch), extra)

    @classmethod
    def _from_tuple(cls, version: tuple[int, int, int, str, str] | tuple[int, int, int, str] | tuple[int, int, int]) -> Self:
        """Create a SemVer object from a tuple.

        This is an internal method used for automatically generating Tidegear version information
        from git tags through [`hatch-vcs`](https://github.com/ofek/hatch-vcs), and is not intended for public use.

        Args:
            version: The version tuple to generate an object from.

        Returns:
            (SemVer): The created SemVer object.
        """
        major, minor, patch, extra, commit = (*version, None, None)[:5]
        extra = f"-{str(extra).lstrip('-')}" if extra else None
        return cls(major, minor, patch, extra, commit)  # pyright: ignore[reportArgumentType]


@dataclass
class User:
    """Dataclass representing a User, primarily for storing cog authors.

    Attributes:
        name: The user's username.
        profile: The user's preferred social networking profile, should usually be a GitHub or other software forge link.
    """

    name: str
    profile: furl

    @override
    def __str__(self) -> str:
        """Return the user's name."""
        return self.name

    @property
    def markdown(self) -> str:
        """Return the user's name within a Markdown masked link pointing to their profile URL."""
        return f"[{self.name}]({self.profile})"


@dataclass
class Repository:
    """Dataclass representing a git repository.

    Attributes:
        owner: The name of the repository owner.
        name: The name of the repository itself.
        url: A link pointing to the repository.
    """

    owner: str
    name: str
    url: furl

    @override
    def __str__(self) -> str:
        """Return the repository's name."""
        return self.name

    @property
    def slug(self) -> str:
        """Return the repository's lowercased name."""
        return self.name.lower()

    @property
    def issues(self) -> furl:
        """Return a URl pointing to the repository's issues page."""
        return self.url / "issues"

    @property
    def markdown(self) -> str:
        """Return the repository's owner and name, wrapped in a Markdown masked link."""
        return f"[{self.owner}/{self.name}]({self.url})"


@dataclass
class CogMetadata:
    """Convenient metadata dataclass containing some useful information regarding the loaded cog.

    Attributes:
        name: The name of the cog's class - NOT the cog's package name.
        version: The version of the cog, provided in the cog's `meta.json`.
        authors: The authors of the cog, provided in the cog's `meta.json`.
        repository: The repository information provided in the cog's `meta.json`.
        documentation: An optional link to the cog's documentation, providd in the cog's `meta.json`.
    """

    name: str
    version: SemVer
    authors: list[User]
    repository: Repository
    documentation: furl | None = None

    @classmethod
    def from_json(cls, cog_name: str, file: Path) -> Self:
        """Load cog metadata from a JSON file.

        Args:
            cog_name: The name of the cog.
            file: The file path of the JSON file to load from.

        Returns:
            (CogMetadata): The constructed metadata object.
        """
        with open(file, "rb") as f:
            obj = orjson.loads(f.read())

        authors = [User(name=author["name"], profile=furl(author["url"])) for author in obj["authors"]]
        repository = Repository(owner=obj["repository"]["owner"], name=obj["repository"]["name"], url=furl(obj["repository"]["url"]))
        if (documentation := obj.get("documentation", None)) is not None:
            documentation = furl(documentation)
        version = SemVer.from_str(obj["version"])
        return cls(name=cog_name, version=version, authors=authors, repository=repository, documentation=documentation)


@dataclass
class TidegearMeta:
    """A metadata class containing version and repository information for Tidegear.
    You shouldn't use this for your own cogs, use [`tidegear.metadata.CogMetadata`][] instead.

    Attributes:
        version: The current Tidegear version.
        repository: Information about the Tidegear git repository.
    """

    version: SemVer
    repository: Repository

    @override
    def __str__(self) -> str:
        """Return the current Tidegear version as a string."""
        return str(self.version)

    @property
    def markdown(self) -> str:
        """Return the current Tidegear version in a markdown hyperlink linking to the Tidegear git repository."""
        return f"[{self.version}]({self.repository.url})"
