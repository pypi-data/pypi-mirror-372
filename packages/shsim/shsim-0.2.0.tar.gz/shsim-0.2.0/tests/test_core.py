
import os
import sys
from pathlib import Path

import pytest

from shsim import core  # loaded via conftest's sys.path tweak


def write_lines(p: Path, n: int):
    p.write_text("".join(f"line-{i}\n" for i in range(n)), encoding="utf-8")


def read_lines(s: str):
    return s.splitlines()


def test_touch_and_cat(tmp_path: Path):
    f = tmp_path / "a.txt"
    core.touch(str(f), create_parents=False)
    assert f.exists()
    f.write_text("hello\nworld\n", encoding="utf-8")
    print(core.cat(str(f)))
    print(core.cat_list(str(f)))
    assert core.cat(str(f)) == "hello\nworld\n"
    assert core.cat_list(str(f)) == ["hello\n", "world\n"]


def test_head_tail(tmp_path: Path):
    f = tmp_path / "data.txt"
    write_lines(f, 10)  # line-0 ... line-9
    assert read_lines(core.head(str(f), 3)) == ["line-0", "line-1", "line-2"]
    assert read_lines(core.tail(str(f), 2)) == ["line-8", "line-9"]
    assert [l.strip() for l in core.head_list(str(f), 4)] == ["line-0", "line-1", "line-2", "line-3"]
    assert [l.strip() for l in core.tail_list(str(f), 1)] == ["line-9"]


def test_grep_and_egrep(tmp_path: Path):
    f = tmp_path / "g.txt"
    f.write_text("alpha\nbeta\ngamma\nalphabet\n", encoding="utf-8")
    assert core.grep_list(str(f), "alp") == ["alpha", "alphabet"]
    assert core.grep(str(f), "alp") == "alpha\nalphabet"
    assert core.grepn_list(str(f), "beta") == ["2:beta"]
    assert core.grepn(str(f), "beta") == "2:beta"
    assert core.egrep_list(str(f), r"^a.*t$") == ["alphabet"]
    assert core.egrepn_list(str(f), r"^g.m") == ["3:gamma"]
    assert core.egrep(str(f), r"^a.*t$") == "alphabet"
    assert core.egrepn(str(f), r"^g.m") == "3:gamma"


def test_mkp_rmrf(tmp_path: Path):
    d = tmp_path / "a" / "b" / "c"
    core.mkp(str(d))
    assert d.is_dir()
    (d / "x.txt").write_text("x", encoding="utf-8")
    top = tmp_path / "a"
    core.rmrf(str(top))
    assert not top.exists()


def test_cprf_file_and_dir(tmp_path: Path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "f.txt").write_text("hello", encoding="utf-8")
    core.cprf(str(src), str(dst), force=True)
    assert (dst / "f.txt").read_text(encoding="utf-8") == "hello"
    (dst / "nested").mkdir()
    (src / "h.txt").write_text("H", encoding="utf-8")
    core.cprf(str(src / "h.txt"), str(dst / "nested" / "h.txt"))
    assert (dst / "nested" / "h.txt").read_text(encoding="utf-8") == "H"


@pytest.mark.skipif(os.name == "nt", reason="symlink needs elevation or dev mode on Windows; fallback used")
def test_ln_symlink_posix(tmp_path: Path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data", encoding="utf-8")
    core.ln(str(src), str(dst))
    assert dst.exists()
    assert dst.is_symlink()
    assert dst.read_text(encoding="utf-8") == "data"


def _windows_symlink_allowed(tmp_path: Path) -> bool:
    if os.name != "nt":
        return False
    t_src = tmp_path / "t_src.txt"
    t_src.write_text("x", encoding="utf-8")
    t_dst = tmp_path / "t_dst.txt"
    try:
        os.symlink(str(t_src), str(t_dst))  # type: ignore[attr-defined]
        return t_dst.is_symlink()
    except Exception:
        return False

@pytest.mark.skipif(os.name != "nt", reason="Windows-only")
def test_ln_windows_symlink_if_possible(tmp_path: Path):
    if not _windows_symlink_allowed(tmp_path):
        pytest.skip("Symlinks not permitted on this Windows host")
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data", encoding="utf-8")

    core.ln(str(src), str(dst))

    assert dst.exists()
    assert dst.is_symlink()  # explicit: we wanted a link

@pytest.mark.skipif(os.name != "nt", reason="Windows-only")
def test_ln_windows_copy_fallback_when_denied(tmp_path: Path, monkeypatch):
    # Force the fallback path by making os.symlink raise
    if hasattr(os, "symlink"):
        monkeypatch.setattr(os, "symlink", lambda *a, **k: (_ for _ in ()).throw(OSError("denied")))

    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data", encoding="utf-8")

    core.ln(str(src), str(dst))

    assert dst.exists()
    assert not dst.is_symlink()
    assert dst.read_text(encoding="utf-8") == "data"


def test_run_and_run_list(tmp_path: Path):
    py = sys.executable
    code = 'import sys; print("OUT"); print("ERR", file=sys.stderr)'
    rc = core.run([py, "-c", code], bg=False)
    assert rc == 0
    lines = core.run_list([py, "-c", code])
    assert "OUT" in lines and "ERR" in lines


def test_env_helpers(monkeypatch):
    key = "SHSIM_TEST_PATH"
    monkeypatch.delenv(key, raising=False)

    core.envappend(key, "/a")
    assert os.environ.get(key) == "/a"

    core.envappend(key, "/b")
    assert os.environ.get(key) == f"/a{os.pathsep}/b"

    core.envprepend(key, "/z")
    assert os.environ.get(key).split(os.pathsep)[0] == "/z"

    assert core.has(key)

    core.envremove(key, "/a")
    assert "/a" not in os.environ.get(key)


def test_isd_ise_and_combined(tmp_path: Path):
    d = tmp_path / "d"
    f = tmp_path / "f.txt"
    d.mkdir()
    f.write_text("x", encoding="utf-8")

    assert core.isd(str(d)) is True
    assert core.ise(str(f)) is True
    assert core.isd(str(f)) is False
    assert core.ise(str(d)) is True

    assert core.isd_lss(str(d)) == "\\n".join(core.lss_list(str(d)))
    assert core.ise_cat(str(f)) == "x"
    assert core.ise_grep(str(f), "x") == "x"


def test_zipdir_and_unzip(tmp_path: Path):
    if not hasattr(core, "zipdir") or not hasattr(core, "unzip"):
        pytest.skip("zipdir/unzip not implemented in this build")
    src = tmp_path / "srcdir"
    src.mkdir()
    (src / "a.txt").write_text("A", encoding="utf-8")
    (src / "b.txt").write_text("B", encoding="utf-8")
    z = tmp_path / "arc.zip"
    core.zipdir(str(src), str(z))
    assert z.exists() and z.stat().st_size > 0
    out = tmp_path / "out"
    core.unzip(str(z), str(out))
    assert (out / "a.txt").read_text(encoding="utf-8") == "A"
    assert (out / "b.txt").read_text(encoding="utf-8") == "B"


def test_logging_no_crash():
    core.logi("info")
    core.logd("debug")
    core.logw("warn")
    core.loge("error")
    core.logii("title")
    core.logdd("section")
