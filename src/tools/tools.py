from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from .registry import tool


@tool()
async def run_spark_job(app_path: str, args: Optional[List[str]] = None, timeout: float = 300.0) -> str:
    """Run a Spark job using `spark-submit` if available, otherwise provide guidance.

    This function prefers calling the `spark-submit` CLI (non-blocking via asyncio).
    If `spark-submit` isn't on PATH but `pyspark` is importable, it will return a message
    describing how to run it programmatically. This keeps the project lightweight while
    providing helpful behavior when Spark is available.
    """
    args = args or []
    if shutil.which("spark-submit"):
        # call spark-submit asynchronously
        proc = await asyncio.create_subprocess_exec(
            "spark-submit",
            app_path,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return "spark-submit timed out"
        if proc.returncode == 0:
            return out.decode(errors="ignore")
        return f"spark-submit failed (rc={proc.returncode}):\n" + err.decode(errors="ignore")

    # fallback message when spark isn't available
    try:
        import pyspark  # type: ignore

        return (
            "pyspark is importable in this environment.\n"
            "You can create a SparkSession and run your job programmatically."
        )
    except Exception:
        return (
            "spark-submit not found on PATH and pyspark is not installed.\n"
            "Install Apache Spark or add `spark-submit` to PATH to run jobs, or install `pyspark`"
        )


@tool()
async def hdfs_list(path: str) -> List[str]:
    """List files in an HDFS path.

    Tries to use the `hdfs` CLI (`hdfs dfs -ls -C`) if available, otherwise tries a
    Python HDFS client (`hdfs` package). Returns a list of paths or raises RuntimeError with guidance.
    """
    if shutil.which("hdfs"):
        cmd = ["hdfs", "dfs", "-ls", "-C", path]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("hdfs dfs command failed: " + err.decode(errors="ignore"))
        lines = out.decode().splitlines()
        return [ln.strip() for ln in lines if ln.strip()]

    try:
        from hdfs import InsecureClient  # type: ignore

        client = InsecureClient("http://localhost:50070")
        # simple listing
        return client.list(path)
    except Exception:
        raise RuntimeError(
            "No HDFS client available: install Hadoop CLI (hdfs) or the `hdfs` Python package and configure the client."
        )


@tool()
async def hdfs_put(local_path: str, hdfs_path: str) -> str:
    """Upload a local file to HDFS. Returns success message or raises RuntimeError."""
    if shutil.which("hdfs"):
        cmd = ["hdfs", "dfs", "-put", local_path, hdfs_path]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("hdfs put failed: " + err.decode(errors="ignore"))
        return out.decode(errors="ignore") or "uploaded"

    try:
        from hdfs import InsecureClient  # type: ignore

        client = InsecureClient("http://localhost:50070")
        client.upload(hdfs_path, local_path)
        return "uploaded"
    except Exception:
        raise RuntimeError("No HDFS client available: install Hadoop CLI or `hdfs` python package.")


@tool()
async def run_sql_query(conn_str: str, query: str, fetch: int = 100) -> str:
    """Run SQL and return JSON-serializable results (stringified JSON for the tool payload).

    - If SQLAlchemy is available we use it.
    - If conn_str points to sqlite (sqlite:///...) we use the stdlib sqlite3.
    """
    # try SQLAlchemy first
    try:
        from sqlalchemy import create_engine, text  # type: ignore

        engine = create_engine(conn_str)
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = [dict(r) for r in result.fetchmany(fetch)]
            return json.dumps(rows, default=str)
    except Exception:
        pass

    # fallback to sqlite3 for local sqlite urls
    if conn_str.startswith("sqlite"):
        import sqlite3

        # extract path part for sqlite:///path.db or sqlite:///:memory:
        if conn_str.startswith("sqlite:///"):
            path = conn_str.replace("sqlite:///", "")
        elif conn_str == "sqlite:///:memory:":
            path = ":memory:"
        else:
            path = conn_str

        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute(query)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = []
        for r in cur.fetchmany(fetch):
            rows.append({k: v for k, v in zip(cols, r)})
        conn.close()
        return json.dumps(rows, default=str)

    raise RuntimeError("No SQL client available: install sqlalchemy or use a sqlite connection string.")


__all__ = ["run_spark_job", "hdfs_list", "hdfs_put", "run_sql_query"]
