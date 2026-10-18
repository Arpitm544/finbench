import os
import sys
import time
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from finbench.database import engine

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def run_all_sql_queries():
    print("=" * 70)
    print("FINBENCH ADVANCED SQL SUITE EXECUTION & BENCHMARK")
    print("=" * 70)

    sql_files = sorted(list(SQL_DIR.rglob("*.sql")))
    # Exclude schema.sql
    queries = [f for f in sql_files if f.name != "schema.sql"]

    total = len(queries)
    passed = 0
    total_time = 0.0

    print(f"Discovered {total} advanced analytical SQL queries across {len(set(f.parent.name for f in queries))} modules.\n")

    with engine.connect() as conn:
        for idx, q_path in enumerate(queries, 1):
            query_text = q_path.read_text()
            start = time.perf_counter()
            try:
                result = conn.execute(text(query_text))
                rows = result.fetchall()
                elapsed_ms = (time.perf_counter() - start) * 1000
                total_time += elapsed_ms
                passed += 1
                print(f"[{idx:02d}/{total:02d}] {q_path.parent.name}/{q_path.name:<40} | Rows: {len(rows):<5} | Latency: {elapsed_ms:6.2f} ms | PASSED")
            except Exception as e:
                print(f"[{idx:02d}/{total:02d}] {q_path.parent.name}/{q_path.name:<40} | FAILED: {e}")

    print("\n" + "=" * 70)
    print(f"SQL Execution Summary: {passed}/{total} Queries Passed. Total Query Time: {total_time:.2f} ms")
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    success = run_all_sql_queries()
    if not success:
        sys.exit(1)
