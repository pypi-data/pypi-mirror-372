import datetime
import multiprocessing
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC
from enum import StrEnum

from opentelemetry.trace import get_current_span

from uncountable.core.environment import get_local_admin_server_port
from uncountable.integration.entrypoint import main as cron_target
from uncountable.integration.queue_runner.command_server import (
    CommandServerTimeout,
    check_health,
)
from uncountable.integration.queue_runner.queue_runner import start_queue_runner
from uncountable.integration.telemetry import Logger

SHUTDOWN_TIMEOUT_SECS = 30

AnyProcess = multiprocessing.Process | subprocess.Popen[bytes]


class ProcessName(StrEnum):
    QUEUE_RUNNER = "queue_runner"
    CRON_SERVER = "cron_server"
    UWSGI = "uwsgi"


@dataclass(kw_only=True)
class ProcessInfo:
    name: ProcessName
    process: AnyProcess

    @property
    def is_alive(self) -> bool:
        match self.process:
            case multiprocessing.Process():
                return self.process.is_alive()
            case subprocess.Popen():
                return self.process.poll() is None

    @property
    def pid(self) -> int | None:
        return self.process.pid

    @property
    def exitcode(self) -> int | None:
        match self.process:
            case multiprocessing.Process():
                return self.process.exitcode
            case subprocess.Popen():
                return self.process.poll()


def handle_shutdown(logger: Logger, processes: dict[ProcessName, ProcessInfo]) -> None:
    logger.log_info("received shutdown command, shutting down sub-processes")
    for proc_info in processes.values():
        if proc_info.is_alive:
            proc_info.process.terminate()

    shutdown_start = time.time()
    still_living_processes = list(processes.values())
    while (
        time.time() - shutdown_start < SHUTDOWN_TIMEOUT_SECS
        and len(still_living_processes) > 0
    ):
        current_loop_processes = [*still_living_processes]
        logger.log_info(
            "waiting for sub-processes to shut down",
            attributes={
                "still_living_processes": [
                    proc_info.name for proc_info in still_living_processes
                ]
            },
        )
        still_living_processes = []
        for proc_info in current_loop_processes:
            if not proc_info.is_alive:
                logger.log_info(f"{proc_info.name} shut down successfully")
            else:
                still_living_processes.append(proc_info)
        time.sleep(1)

    for proc_info in still_living_processes:
        logger.log_warning(
            f"{proc_info.name} failed to shut down after {SHUTDOWN_TIMEOUT_SECS} seconds, forcefully terminating"
        )
        proc_info.process.kill()


def restart_process(
    logger: Logger, proc_info: ProcessInfo, processes: dict[ProcessName, ProcessInfo]
) -> None:
    logger.log_error(
        f"process {proc_info.name} shut down unexpectedly - exit code {proc_info.exitcode}. Restarting..."
    )

    match proc_info.name:
        case ProcessName.QUEUE_RUNNER:
            queue_proc = multiprocessing.Process(target=start_queue_runner)
            queue_proc.start()
            new_info = ProcessInfo(name=ProcessName.QUEUE_RUNNER, process=queue_proc)
            processes[ProcessName.QUEUE_RUNNER] = new_info
            try:
                _wait_queue_runner_online()
                logger.log_info("queue runner restarted successfully")
            except Exception as e:
                logger.log_exception(e)
                logger.log_error(
                    "queue runner failed to restart, shutting down scheduler"
                )
                handle_shutdown(logger, processes)
                sys.exit(1)

        case ProcessName.CRON_SERVER:
            cron_proc = multiprocessing.Process(target=cron_target)
            cron_proc.start()
            new_info = ProcessInfo(name=ProcessName.CRON_SERVER, process=cron_proc)
            processes[ProcessName.CRON_SERVER] = new_info
            logger.log_info("cron server restarted successfully")

        case ProcessName.UWSGI:
            uwsgi_proc: AnyProcess = subprocess.Popen(["uwsgi", "--die-on-term"])
            new_info = ProcessInfo(name=ProcessName.UWSGI, process=uwsgi_proc)
            processes[ProcessName.UWSGI] = new_info
            logger.log_info("uwsgi restarted successfully")


def check_process_alive(
    logger: Logger, processes: dict[ProcessName, ProcessInfo]
) -> None:
    for proc_info in processes.values():
        if not proc_info.is_alive:
            restart_process(logger, proc_info, processes)


def _wait_queue_runner_online() -> None:
    MAX_QUEUE_RUNNER_HEALTH_CHECKS = 10
    QUEUE_RUNNER_HEALTH_CHECK_DELAY_SECS = 1

    num_attempts = 0
    before = datetime.datetime.now(UTC)
    while num_attempts < MAX_QUEUE_RUNNER_HEALTH_CHECKS:
        try:
            if check_health(port=get_local_admin_server_port()):
                return
        except CommandServerTimeout:
            pass
        num_attempts += 1
        time.sleep(QUEUE_RUNNER_HEALTH_CHECK_DELAY_SECS)
    after = datetime.datetime.now(UTC)
    duration_secs = (after - before).seconds
    raise Exception(f"queue runner failed to come online after {duration_secs} seconds")


def main() -> None:
    logger = Logger(get_current_span())
    processes: dict[ProcessName, ProcessInfo] = {}

    multiprocessing.set_start_method("forkserver")

    def add_process(process: ProcessInfo) -> None:
        processes[process.name] = process
        logger.log_info(f"started process {process.name}")

    runner_process = multiprocessing.Process(target=start_queue_runner)
    runner_process.start()
    add_process(ProcessInfo(name=ProcessName.QUEUE_RUNNER, process=runner_process))

    try:
        _wait_queue_runner_online()
    except Exception as e:
        logger.log_exception(e)
        handle_shutdown(logger, processes=processes)
        return

    cron_process = multiprocessing.Process(target=cron_target)
    cron_process.start()
    add_process(ProcessInfo(name=ProcessName.CRON_SERVER, process=cron_process))

    uwsgi_process = subprocess.Popen([
        "uwsgi",
        "--die-on-term",
    ])
    add_process(ProcessInfo(name=ProcessName.UWSGI, process=uwsgi_process))

    try:
        while True:
            check_process_alive(logger, processes=processes)
            time.sleep(1)
    except KeyboardInterrupt:
        handle_shutdown(logger, processes=processes)


if __name__ == "__main__":
    main()
