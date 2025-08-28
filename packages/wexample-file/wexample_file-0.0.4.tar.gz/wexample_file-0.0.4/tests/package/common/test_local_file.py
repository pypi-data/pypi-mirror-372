from __future__ import annotations

from pathlib import Path

import pytest
from wexample_file.common.local_file import LocalFile
from wexample_file.excpetion.file_not_found_exception import FileNotFoundException
from wexample_file.excpetion.not_a_file_exception import NotAFileException


def test_local_file_instantiation_with_str(tmp_path) -> None:
    p = tmp_path / "file.txt"
    p.write_text("hello")
    lf = LocalFile(path=str(p))
    assert isinstance(lf.path, Path)
    assert lf.path == p.resolve()


def test_local_file_instantiation_with_path_nonexistent(tmp_path) -> None:
    p = tmp_path / "missing.txt"
    assert not p.exists()
    lf = LocalFile(path=p)
    assert lf.path == p.resolve()


def test_local_file_rejects_directory(tmp_path) -> None:
    d = tmp_path / "adir"
    d.mkdir()
    with pytest.raises(NotAFileException):
        LocalFile(path=d)


def test_local_file_check_exists_true_accepts_existing_file(tmp_path) -> None:
    p = tmp_path / "exists.txt"
    p.write_text("data")
    lf = LocalFile(path=p, check_exists=True)
    assert lf.path == p.resolve()


def test_local_file_check_exists_true_rejects_missing(tmp_path) -> None:
    p = tmp_path / "missing2.txt"
    assert not p.exists()
    with pytest.raises(FileNotFoundException):
        LocalFile(path=p, check_exists=True)


def test_local_file_remove_deletes_file(tmp_path) -> None:
    p = tmp_path / "toremove.txt"
    p.write_text("data")
    lf = LocalFile(path=p, check_exists=True)
    assert p.exists()
    lf.remove()
    assert not p.exists()


def test_local_file_remove_idempotent(tmp_path) -> None:
    p = tmp_path / "missing_after_remove.txt"
    lf = LocalFile(path=p)
    # First remove on non-existent path should not raise
    lf.remove()
    assert not p.exists()
    # Create then remove, then remove again
    p.write_text("hello")
    lf2 = LocalFile(path=p, check_exists=True)
    lf2.remove()
    assert not p.exists()
    # Idempotent second call
    lf2.remove()


def test_local_file_read_returns_content_when_exists(tmp_path) -> None:
    p = tmp_path / "readme.txt"
    content = "héllo world"
    p.write_text(content, encoding="utf-8")
    lf = LocalFile(path=p)
    assert lf.read() == content


def test_local_file_read_returns_none_when_missing(tmp_path) -> None:
    p = tmp_path / "missing_read.txt"
    lf = LocalFile(path=p)
    assert lf.read() is None


def test_local_file_read_raises_if_not_a_file(tmp_path) -> None:
    d = tmp_path / "not_a_file"
    d.mkdir()
    # Constructing LocalFile with a directory path would already raise NotAFileException
    # So we simulate a race: create a file path then replace with directory
    p = tmp_path / "was_file.txt"
    p.write_text("x")
    lf = LocalFile(path=p)
    # Replace the path with a directory at same location
    p.unlink()
    d.rename(p)

    assert lf.read() is None


def test_local_file_touch_creates_file_and_parents(tmp_path) -> None:
    nested = tmp_path / "a/b/c/file.txt"
    lf = LocalFile(path=nested)
    assert not nested.exists()
    lf.touch()
    assert nested.exists() and nested.is_file()


def test_local_file_write_writes_content_and_creates_parents(tmp_path) -> None:
    nested = tmp_path / "x/y/z/out.txt"
    lf = LocalFile(path=nested)
    text = "some content"
    lf.write(text)
    assert nested.exists() and nested.read_text() == text


def test_local_file_get_extension_simple(tmp_path) -> None:
    p = tmp_path / "report.pdf"
    lf = LocalFile(path=p)
    assert lf.get_extension() == "pdf"


def test_local_file_get_extension_compound(tmp_path) -> None:
    p = tmp_path / "archive.tar.gz"
    lf = LocalFile(path=p)
    assert lf.get_extension() == "gz"


def test_local_file_get_extension_none(tmp_path) -> None:
    p = tmp_path / "README"
    lf = LocalFile(path=p)
    assert lf.get_extension() == ""


def test_local_file_get_extension_hidden_file(tmp_path) -> None:
    p = tmp_path / ".gitignore"
    lf = LocalFile(path=p)
    assert lf.get_extension() == ""
