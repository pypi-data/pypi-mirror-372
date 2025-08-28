from __future__ import annotations

from pathlib import Path

import pytest
from wexample_file.common.local_directory import LocalDirectory
from wexample_file.excpetion.directory_not_found_exception import (
    DirectoryNotFoundException,
)
from wexample_file.excpetion.not_a_directory_exception import NotADirectoryException


def test_local_directory_instantiation_with_str(tmp_path) -> None:
    d = tmp_path / "adir"
    d.mkdir()
    ld = LocalDirectory(path=str(d))
    assert isinstance(ld.path, Path)
    assert ld.path == d.resolve()


def test_local_directory_instantiation_with_path_nonexistent(tmp_path) -> None:
    d = tmp_path / "missing_dir"
    assert not d.exists()
    ld = LocalDirectory(path=d)
    assert ld.path == d.resolve()


def test_local_directory_rejects_file(tmp_path) -> None:
    f = tmp_path / "afile.txt"
    f.write_text("hello")
    with pytest.raises(NotADirectoryException):
        LocalDirectory(path=f)


def test_local_directory_check_exists_true_accepts_existing_dir(tmp_path) -> None:
    d = tmp_path / "exists_dir"
    d.mkdir()
    ld = LocalDirectory(path=d, check_exists=True)
    assert ld.path == d.resolve()


def test_local_directory_check_exists_true_rejects_missing(tmp_path) -> None:
    d = tmp_path / "missing_dir2"
    assert not d.exists()
    with pytest.raises(DirectoryNotFoundException):
        LocalDirectory(path=d, check_exists=True)


def test_local_directory_remove_deletes_directory_recursively(tmp_path) -> None:
    d = tmp_path / "adir_to_remove"
    sub = d / "sub"
    sub.mkdir(parents=True)
    (sub / "file.txt").write_text("hello")
    ld = LocalDirectory(path=d, check_exists=True)
    assert d.exists() and d.is_dir()
    ld.remove()
    assert not d.exists()


def test_local_directory_remove_idempotent(tmp_path) -> None:
    d = tmp_path / "missing_dir_after_remove"
    ld = LocalDirectory(path=d)
    # First remove on non-existent path should not raise
    ld.remove()
    assert not d.exists()
    # Create then remove, then remove again
    d.mkdir()
    ld2 = LocalDirectory(path=d, check_exists=True)
    ld2.remove()
    assert not d.exists()
    # Idempotent second call
    ld2.remove()


def test_local_directory_create_creates_directory_and_parents(tmp_path) -> None:
    d = tmp_path / "a/b/c"
    ld = LocalDirectory(path=d)
    assert not d.exists()
    ld.create()
    assert d.exists() and d.is_dir()
