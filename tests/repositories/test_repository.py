from __future__ import annotations

import pytest

from poetry.core.constraints.version import Version
from poetry.core.packages.package import Package

from poetry.factory import Factory
from poetry.repositories import Repository


@pytest.fixture(scope="module")
def black_repository() -> Repository:
    repo = Repository("repo")
    repo.add_package(Package("black", "19.10b0"))
    repo.add_package(Package("black", "21.11b0", yanked="reason"))
    return repo


@pytest.mark.parametrize(
    ["constraint", "expected"],
    [
        # yanked 21.11b0 is ignored except for pinned version
        ("*", ["19.10b0"]),
        (">=19.0a0", ["19.10b0"]),
        (">=20.0a0", []),
        (">=21.11b0", []),
        ("==21.11b0", ["21.11b0"]),
    ],
)
def test_find_packages_yanked(
    black_repository: Repository, constraint: str, expected: list[str]
) -> None:
    packages = black_repository.find_packages(
        Factory.create_dependency("black", constraint)
    )

    assert [str(p.version) for p in packages] == expected


@pytest.mark.parametrize(
    "package_name, version, yanked, yanked_reason",
    [
        ("black", "19.10b0", False, ""),
        ("black", "21.11b0", True, "reason"),
    ],
)
def test_package_yanked(
    black_repository: Repository,
    package_name: str,
    version: str,
    yanked: bool,
    yanked_reason: str,
) -> None:
    package = black_repository.package(package_name, Version.parse(version))

    assert package.name == package_name
    assert str(package.version) == version
    assert package.yanked is yanked
    assert package.yanked_reason == yanked_reason


def test_package_pretty_name_is_kept() -> None:
    pretty_name = "Not_canoni-calized.name"
    repo = Repository("repo")
    repo.add_package(Package(pretty_name, "1.0"))
    package = repo.package(pretty_name, Version.parse("1.0"))

    assert package.pretty_name == pretty_name
