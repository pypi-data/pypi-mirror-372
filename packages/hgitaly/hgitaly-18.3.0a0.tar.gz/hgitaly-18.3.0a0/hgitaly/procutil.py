import os
import psutil

IS_CHILD_PROCESS = False


def is_current_service_process(pid):
    """Determine whether the given pid is part of the current HGitaly service.

    For now, the logic is that other processes from the same HGitaly service
    are expected to be siblings of the current process, unless in the special
    case where HGitaly is not started as a prefork server, which should happen
    with the `--mono-process` option (debuging sessions) and tests only.
    """
    this_pid = os.getpid()

    if not IS_CHILD_PROCESS:
        return pid == this_pid

    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False

    return proc.ppid() == os.getppid()
