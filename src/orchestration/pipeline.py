from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_command(command: list[str], timeout: int | None = None) -> None:
    subprocess.run(command, cwd=PROJECT_ROOT, check=True, timeout=timeout)


def wait_for_postgres(timeout_seconds: int = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["docker", "exec", "healthcare_postgres", "pg_isready", "-U", "healthcare", "-d", "healthcare"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    raise TimeoutError("PostgreSQL did not become ready in time")


def run_pipeline(start_postgres: bool = True) -> None:
    if start_postgres:
        run_command(["docker", "compose", "up", "-d", "postgres"], timeout=120)
        wait_for_postgres()

    run_command(["python", "-m", "src.ingestion.load_owid", "--write-db"], timeout=180)
    run_command(["dbt", "run", "--project-dir", "dbt", "--profiles-dir", "dbt"], timeout=120)
    run_command(["dbt", "test", "--project-dir", "dbt", "--profiles-dir", "dbt"], timeout=120)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local healthcare data pipeline")
    parser.add_argument("--skip-postgres", action="store_true")
    args = parser.parse_args()

    run_pipeline(start_postgres=not args.skip_postgres)


if __name__ == "__main__":
    main()
