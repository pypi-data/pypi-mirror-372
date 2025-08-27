# SHSIM

SHSIM is a tiny unified shell-like helpers, one could use shell like commands
cross Windows, Linux and MacOS systems.

It contains following four commands types
- Log
- Environment Variables
- Action
- Status
- Action + Status

---

## Log Commands

Format: `log(i|d|w|e|ii|dd)`

| Command Pattern  | Shell Equivalent        | Action | Type   | Description                                |
|------------------|-------------------------|--------|--------|--------------------------------------------|
| `logi`           | `echo "INFO:"`          | log    | print  | Print info message                         |
| `logd`           | `echo "DEBUG:"`         | log    | print  | Print debug message                        |
| `logw`           | `echo "WARN:"`          | log    | print  | Print warning message                      |
| `loge`           | `echo "ERROR:"`         | log    | print  | Print error message                        |
| `logii`          | `echo "====\n...\n===="`| log    | print  | Info with divider                          |
| `logdd`          | `echo "----\n...\n----"`| log    | print  | Debug with divider                         |

Note:
- All messages are prefixed with timestamp, filename, and line number.
- Log messages are always teed to both stdout/stderr and file.
- Log file is configured via `shsim.logfile` (default provided).

---

## Action Commands

Format:
- `<command>`: stdout/stderr output (shell-style)
- `<command>_list`: Python `list` return for iteration
- Suffix `(_list)` means the command supports both

| Command Pattern        | Shell Equivalent         | Action     | Type         | Description                                 |
|------------------------|--------------------------|------------|--------------|---------------------------------------------|
| `pwd`                  | `pwd`                    | inspect    | return       | Get current working directory               |
| `abspath`              | `realpath`               | path       | return       | Get absolute path of input                  |
| `basename`             | `basename path`          | path       | return       | Get last component of path                  |
| `dirname`              | `dirname path`           | path       | return       | Get parent directory of path                |
| `ext`                  | N/A                      | path       | return       | Get file extension (e.g., `.txt`)           |
| `which`                | `which cmd`              | system     | return       | Locate command in system PATH               |
| `cat(_list)`           | `cat`                    | read       | return       | Read file content                           |
| `head(_list)`          | `head -n`                | read       | return       | Read first N lines from file                |
| `tail(_list)`          | `tail -n`                | read       | return       | Read last N lines from file                 |
| `grep(_list)`          | `grep`                   | filter     | return       | Match lines by fixed string                 |
| `grepn(_list)`         | `grep -n`                | filter     | return       | Match lines with line number                |
| `egrep(_list)`         | `grep -E`                | filter     | return       | Match using extended regex                  |
| `egrepn(_list)`        | `grep -nE`               | filter     | return       | Extended regex match with line numbers      |
| `ls(_list)`            | `ls`                     | list       | return       | List directory contents                     |
| `lsa(_list)`           | `ls -a`                  | list       | return       | List all files, including hidden            |
| `lss(_list)`           | `ls -st`                 | list       | return       | List sorted by modified time                |
| `find(_list)`          | `find` / `glob`          | list       | return       | Recursively find files                      |
| `mkp`                  | `mkdir -p`               | modify     | exec         | Create directory and parents if needed      |
| `rmrf`                 | `rm -rf`                 | modify     | exec         | Recursively delete file or directory        |
| `cprf`                 | `cp -rf`                 | modify     | exec         | Recursively copy file or directory          |
| `mv`                   | `mv`                     | modify     | exec         | Move or rename file or directory            |
| `touch`                | `touch`                  | modify     | exec         | Create file or update timestamp             |
| `ln`                   | `ln`                     | modify     | exec         | Create symbolic link                        |
| `lnsf`                 | `ln -sf`                 | modify     | exec         | Force overwrite symbolic link               |
| `zipdir`               | `zip`                    | archive    | exec         | Create zip archive                          |
| `unzip`                | `unzip`                  | archive    | exec         | Extract zip archive                         |
| `cd`                   | `cd`                     | exec       | exec         | Change current working directory            |
| `run(_list)`           | `echo && eval`           | exec       | exec         | Show and execute shell command              |
| `envget`               | `echo $VAR`              | env        | return       | Get environment variable                    |
| `envset`               | `export VAR=val`         | env        | exec         | Set environment variable                    |
| `envlist(_list)`       | `set`                    | env        | return       | Show environment variables                  |
| `envunset`             | `unset VAR`              | env        | exec         | Remove environment variable                 |
| `envappend`            | `export VAR=$VAR:val`    | env        | exec         | Append value to env variable                |
| `envprepend`           | `export VAR=val:$VAR`    | env        | exec         | Prepend value to env variable               |
| `envremove`            | (custom parse/remove)    | env        | exec         | Remove value from env variable              |
| `envhas`               | `[[ ":$VAR:" == *:val:* ]]` | env     | return       | Check if env variable contains a value      |

---

### Run Command Usage

`run` and `run_list` provide basic shell-style command execution.

**Format**:
- `run(cmd, ...)` → Run shell command and print output
- `run_list(cmd, ...)` → Run shell command and return list of output lines

**Supported Parameters**:

| Parameter     | Type     | Description                                                        |
|---------------|----------|--------------------------------------------------------------------|
| `bg=True`     | bool     | Run in background (non-blocking)                                   |
| `delay=2.5`   | float    | Delay execution by seconds (supports float)                        |
| `logfile="..."` | str    | Redirect stdout/stderr to log file (in addition to stdout/stderr)  |

---

## Status Commands

Format: `(is|no)(d|f|e|x|l)`
- `is`: means is true
- `no`: means not true
- `d`: directory
- `f`: file
- `e`: exists
- `x`: executable
- `l`: symlink

| Command Pattern | Shell Equivalent     | Action  | Type   | Description                             |
|-----------------|----------------------|---------|--------|-----------------------------------------|
| `isd`           | `[ -d path ]`        | status  | return | True if path is a directory             |
| `isf`           | `[ -f path ]`        | status  | return | True if path is a file                  |
| `ise`           | `[ -e path ]`        | status  | return | True if path exists                     |
| `isx`           | `[ -x path ]`        | status  | return | True if path is executable              |
| `isl`           | `[ -L path ]`        | status  | return | True if path is a symlink               |
| `nod`           | `[ ! -d path ]`      | status  | return | Not a directory                         |
| `nof`           | `[ ! -f path ]`      | status  | return | Not a file                              |
| `noe`           | `[ ! -e path ]`      | status  | return | Path does not exist                     |
| `nox`           | `[ ! -x path ]`      | status  | return | Not executable                          |
| `nol`           | `[ ! -L path ]`      | status  | return | Not a symlink                           |

---

## Combined Status + Action Commands

Format: `<status>_<action>([_list])`

| Command Pattern    | Shell Equivalent           | Action         | Type         | Description                                      |
|--------------------|----------------------------|----------------|--------------|--------------------------------------------------|
| `noe_mkp`          | `[ ! -e path ] && mkdir -p`| status+modify  | exec         | Make dir only if not exists                      |
| `isd_rmrf`         | `[ -d path ] && rm -rf`    | status+modify  | exec         | Remove dir only if it exists                     |
| `isf_rmrf`         | `[ -f path ] && rm -rf`    | status+modify  | exec         | Remove file only if it exists                    |
| `ise_rmrf`         | `[ -e path ] && rm -rf`    | status+modify  | exec         | Remove if it exists                              |
| `ise_mv`           | `[ -e path ] && mv`        | status+modify  | exec         | Move if source exists                            |
| `ise_cprf`         | `[ -e path ] && cp -rf`    | status+modify  | exec         | Copy if source exists                            |
| `isd_lss(_list)`   | `ls -st` if dir exists     | status+list    | return       | Sorted list only if directory exists             |
| `ise_cat(_list)`   | `cat` if file exists       | status+read    | return       | Show file contents if exists                     |
| `ise_grep(_list)`  | `grep` if file exists      | status+filter  | return       | Grep lines only if file exists                   |

---

# Install

Install Command:

```
pip install shsim
```

