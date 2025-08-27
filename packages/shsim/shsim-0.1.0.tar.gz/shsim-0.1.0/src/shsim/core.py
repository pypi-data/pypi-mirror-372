#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import shutil
import subprocess
import re
from pathlib import Path
from datetime import datetime
import inspect
from typing import Sequence, Union
import zipfile

################################################################################
# log session
logfile = os.environ.get("SHSIM_LOGFILE", "_shsim.log")
log_debug = os.environ.get("SHSIM_DEBUG", "1") != "0"
log_verbose = os.environ.get("SHSIM_VERBOSE", "1") != "0"


def _log(tag: str, msg: str, divider: str = None):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller = inspect.stack()[2]
    prefix = " ".join(
        [
            f"[{ts}]"
            f"[{tag.upper():5}]"
            f"[({os.path.basename(caller.filename)}:{caller.lineno})]"
        ]
    )
    body = f"{prefix} {msg}"
    full = f"{divider}\n{body}\n{divider}" if divider else body
    print(full)
    try:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(full + "\n")
    except Exception:
        pass  # Ignore logging errors


def logi(msg: str):
    if log_verbose:
        _log("INFO", msg)


def logd(msg: str):
    if log_debug:
        _log("DEBUG", msg)


def logw(msg: str):
    _log("WARN", msg)


def loge(msg: str):
    _log("ERROR", msg)


def logii(msg: str):
    if log_verbose:
        _log("INFO", msg, "=" * 80)


def logdd(msg: str):
    if log_debug:
        _log("DEBUG", msg, "-" * 80)


################################################################################
# action session
def pwd() -> str:
    return os.getcwd()


def abspath(path: str) -> str:
    return os.path.abspath(path)


def basename(path: str) -> str:
    return os.path.basename(path)


def dirname(path: str) -> str:
    return os.path.dirname(path)


def ext(path: str) -> str:
    return os.path.splitext(path)[1]


def which(cmd: str) -> str:
    return shutil.which(cmd)


def cat(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def cat_list(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def head(path: str, n: int = 10) -> str:
    return "".join(cat_list(path)[:n])


def head_list(path: str, n: int = 10) -> list[str]:
    return cat_list(path)[:n]


def tail(path: str, n: int = 10) -> str:
    return "".join(cat_list(path)[-n:])


def tail_list(path: str, n: int = 10) -> list[str]:
    return cat_list(path)[-n:]


################################################################################
# --- grep correctness & memory ---
def _iter_lines(path: str):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            yield line.rstrip("\n")


def grep_list(path: str, keyword: str) -> list[str]:
    return [line for line in _iter_lines(path) if keyword in line]


def grepn_list(path: str, keyword: str) -> list[str]:
    return [
        f"{i}:{line}"
        for i, line in enumerate(_iter_lines(path), start=1)
        if keyword in line
    ]


def egrep_list(path: str, pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return [line for line in _iter_lines(path) if rx.search(line)]


def egrepn_list(path: str, pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return [
        f"{i}:{line}"
        for i, line in enumerate(_iter_lines(path), start=1)
        if rx.search(line)
    ]


################################################################################


def grep(path: str, keyword: str) -> str:
    return "\n".join(grep_list(path, keyword))


def grepn(path: str, keyword: str) -> str:
    return "\n".join(grepn_list(path, keyword))


def egrep(path: str, pattern: str) -> str:
    return "\n".join(egrep_list(path, pattern))


def egrepn(path: str, pattern: str) -> str:
    return "\n".join(egrepn_list(path, pattern))


def ls_list(path: str = ".") -> list[str]:
    return os.listdir(path)


def ls(path: str = ".") -> str:
    return "\n".join(os.listdir(path))


def lsa_list(path: str = ".") -> list[str]:
    return os.listdir(path)


def lsa(path: str = ".") -> str:
    return "\n".join(lsa_list(path))


def lss_list(path: str = ".") -> list[str]:
    return sorted(
        os.listdir(path),
        key=lambda x: os.path.getmtime(os.path.join(path, x)),
        reverse=True,
    )


def lss(path: str = ".") -> str:
    return "\n".join(lss_list(path))


def find_list(path: str = ".", suffix: str = "") -> list[str]:
    return [str(p) for p in Path(path).rglob(f"*{suffix}")]


def find(path: str = ".", suffix: str = "") -> str:
    return "\n".join(find_list(path, suffix))


def mkp(path: str):
    os.makedirs(path, exist_ok=True)


def rmrf(path: str):
    p = Path(path)
    if p.is_file() or p.is_symlink():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p, ignore_errors=True)


def cprf(src: str, dst: str, *, force: bool = True):
    src_path = Path(src)
    dst_path = Path(dst)
    if src_path.is_dir():
        if dst_path.exists() and force:
            shutil.rmtree(dst_path, ignore_errors=True)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copytree(src_path, dst_path)
        except FileExistsError:
            # Python <3.8 alternative when not forcing
            pass
    else:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)


def mv(src: str, dst: str):
    shutil.move(src, dst)


def touch(path: str, *, create_parents: bool = False):
    p = Path(path)
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)


def ln(src: str, dst: str):
    try:
        os.symlink(src, dst)
    except (NotImplementedError, OSError):
        # Fallbacks for Windows
        src_p = Path(src)
        dst_p = Path(dst)
        if src_p.is_file():
            try:
                os.link(src, dst)  # hardlink
            except Exception as e:
                raise OSError(f"ln fallback failed on Windows: {e}") from e
        elif src_p.is_dir() and os.name == "nt":
            # Directory junction
            subprocess.check_call(
                ["cmd", "/c", "mklink", "/J", str(dst_p), str(src_p)]
            )
        else:
            raise


def lns(src: str, dst: str):
    try:
        if os.path.exists(dst) or os.path.islink(dst):
            os.unlink(dst)
        os.symlink(src, dst)
    except Exception as e:
        loge(f"lns failed: {e}")


def zipdir(path: str, archive: str) -> None:
    """
    Create a ZIP archive of the directory at ``path``.

    The archive is written to the filename specified by ``archive``.
    Unlike shutil.make_archive, this function does not append an extra
    '.zip' extension if the destination already ends in '.zip'.
    """
    src_path = Path(path)
    dest_path = Path(archive)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(
        dest_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for root, _dirs, files in os.walk(src_path):
            for name in files:
                full_path = Path(root) / name
                # store relative paths inside the archive
                arcname = str(full_path.relative_to(src_path))
                zf.write(full_path, arcname)


def unzip(archive: str, path: str):
    shutil.unpack_archive(archive, path)


def cd(path: str):
    os.chdir(path)


def _normalize_cmd(cmd: Union[str, Sequence[str]]):
    if isinstance(cmd, str):
        return cmd, True
    return list(cmd), False


def run(
    cmd: Union[str, Sequence[str]],
    *,
    bg: bool = False,
    delay: float = 0,
    log_file: str | None = None,
) -> int:
    """
    Prints stdout/stderr as it arrives and returns the exit code.
    If bg=True, returns 0 and doesn't wait (fire-and-forget).
    Consider returning a handle instead.
    """
    if delay:
        time.sleep(delay)
    the_cmd, use_shell = _normalize_cmd(cmd)
    if bg:
        # pylint: disable=consider-using-with
        subprocess.Popen(the_cmd, shell=use_shell)
        return 0
    with subprocess.Popen(
        the_cmd,
        shell=use_shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        out, err = proc.communicate()
    if out:
        print(out, end="")
    if err:
        print(err, end="", file=sys.stderr)
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                if out:
                    f.write(out)
                if err:
                    f.write(err)
        except Exception:
            pass
    return proc.returncode


def run_list(
    cmd: Union[str, Sequence[str]],
    *,
    delay: float = 0,
    log_file: str | None = None,
) -> list[str]:
    """
    Returns combined stdout lines (stderr lines appended after).
    """
    if delay:
        time.sleep(delay)
    the_cmd, use_shell = _normalize_cmd(cmd)
    with subprocess.Popen(
        the_cmd,
        shell=use_shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        out, err = proc.communicate()
    lines = []
    if out:
        lines.extend(out.splitlines())
    if err:
        lines.extend(err.splitlines())
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except Exception:
            pass
    return lines


def envget(k: str):
    return os.environ.get(k)


def envset(k: str, v: str):
    os.environ[k] = v


def envunset(k: str):
    os.environ.pop(k, None)


def _split_env(v):
    return [p for p in v.split(os.pathsep) if p]


def has(key: str) -> bool:
    """
    Return True if environment variable `key` exists and is non-empty.
    """
    v = os.environ.get(key)
    return v is not None and v != ""


def envappend(k: str, v: str):
    base = _split_env(os.environ.get(k, ""))
    if v and v not in base:
        base.append(v)
    os.environ[k] = os.pathsep.join(base)


def envprepend(k: str, v: str):
    base = _split_env(os.environ.get(k, ""))
    if v in base:
        base.remove(v)
    os.environ[k] = os.pathsep.join([v] + base)


def envremove(k: str, v: str):
    base = [p for p in _split_env(os.environ.get(k, "")) if p != v]
    os.environ[k] = os.pathsep.join(base)


def envhas(k: str, v: str):
    return v in os.environ.get(k, "").split(";" if os.name == "nt" else ":")


def envlist():
    print("\n".join(f"{k}={v}" for k, v in os.environ.items()))


def envlist_list():
    return [f"{k}={v}" for k, v in os.environ.items()]


################################################################################
# status
def isd(path: str):
    return os.path.isdir(path)


def isf(path: str):
    return os.path.isfile(path)


def ise(path: str):
    return os.path.exists(path)


def isx(path: str):
    return os.access(path, os.X_OK)


def isl(path: str):
    return os.path.islink(path)


def nod(path: str):
    return not isd(path)


def nof(path: str):
    return not isf(path)


def noe(path: str):
    return not ise(path)


def nox(path: str):
    return not isx(path)


def nol(path: str):
    return not isl(path)


################################################################################
# status + action commands
def noe_mkp(path):
    if noe(path):
        mkp(path)


def isd_rmrf(path):
    if isd(path):
        rmrf(path)


def isf_rmrf(path: str):
    if isf(path):
        rmrf(path)


def ise_rmrf(path: str):
    if ise(path):
        rmrf(path)


def ise_mv(src: str, dst: str):
    if ise(src):
        mv(src, dst)


def ise_cprf(src: str, dst: str):
    if ise(src):
        cprf(src, dst)


def isd_lss(path: str = ".") -> str:
    return "\n".join(lss_list(path)) if isd(path) else ""


def isd_lss_list(path: str = ".") -> list[str]:
    return lss_list(path) if isd(path) else []


def ise_cat(path: str) -> str:
    return cat(path) if ise(path) else ""


def ise_cat_list(path: str) -> list[str]:
    return cat_list(path) if ise(path) else []


def ise_grep(path: str, keyword: str) -> str:
    return "\n".join(grep_list(path, keyword)) if ise(path) else ""


def ise_grep_list(path: str, keyword: str) -> list[str]:
    return grep_list(path, keyword) if ise(path) else []
