"""Supabase diagnostics script for BananaKart backend."""
from __future__ import annotations

import os
import sys
import types
import uuid
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:  # type: ignore[override]
        return False

    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = load_dotenv  # type: ignore[attr-defined]
    sys.modules.setdefault("dotenv", dotenv_stub)


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()


def safe_length(value: Optional[str]) -> int:
    return len(value or "")


def print_env_status() -> Dict[str, Dict[str, Any]]:
    env_names = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
    ]
    status: Dict[str, Dict[str, Any]] = {}
    print("Supabase environment variables:")
    for name in env_names:
        raw = os.getenv(name)
        exists = bool(raw)
        length = safe_length(raw)
        print(f"  {name}: {exists} (length {length})")
        status[name] = {"present": exists, "length": length}
    return status


def with_supabase_client() -> Dict[str, Any]:
    try:
        from apps.backend.supabase_client import supabase
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to initialize supabase client: {exc}")
        return {"client": None, "error": str(exc)}
    return {"client": supabase, "error": None}


def test_select(client: Optional["Client"]) -> Dict[str, Any]:
    print("\nTesting select on 'recipes' (limit 1):")
    if client is None:
        print("  Skipped: client unavailable.")
        return {"status": "skipped", "error": "client unavailable"}
    try:
        response = client.table("recipes").select("*").limit(1).execute()
        row_count = len(response.data or [])
        print(f"  Rows returned: {row_count}")
        return {"status": "ok", "rows": row_count, "data": response.data}
    except Exception as exc:  # pylint: disable=broad-except
        print(f"  Select failed: {exc}")
        return {"status": "error", "error": str(exc)}


def describe_table(client: Optional["Client"]) -> Dict[str, Any]:
    print("\nFetching column metadata for 'recipes':")
    if client is None:
        print("  Skipped: client unavailable.")
        return {"status": "skipped", "columns": [], "method": None, "error": "client unavailable"}
    columns: List[str] = []
    method_used = ""
    try:
        method_used = "rpc_pg_table_def"
        response = client.rpc(
            "pg_table_def",
            {"schemaname": "public", "tablename": "recipes"},
        ).execute()
        columns = sorted({row["column"] for row in response.data if row.get("column")})
    except Exception:  # pylint: disable=broad-except
        method_used = "select_limit_0"
        try:
            response = client.table("recipes").select("*").limit(1).execute()
            sample = response.data[0] if response.data else {}
            columns = sorted(sample.keys())
        except Exception as exc:  # pylint: disable=broad-except
            print(f"  Column fetch failed: {exc}")
            return {"status": "error", "error": str(exc), "method": method_used, "columns": []}
    if not columns:
        print("  Columns: []")
    else:
        print(f"  Columns: {', '.join(columns)}")
    return {"status": "ok", "columns": columns, "method": method_used}


def simulate_insert(client: Optional["Client"]) -> Dict[str, Any]:
    print("\nAttempting dummy insert into 'recipes':")
    if client is None:
        print("  Skipped: client unavailable.")
        return {"status": "skipped", "error": "client unavailable"}
    payload = {
        "user_id": str(uuid.uuid4()),
        "recipe_text": "diagnostic-test",
        "urgency": "low",
    }
    try:
        response = client.table("recipes").insert(payload).execute()
        inserted = len(response.data or [])
        print(f"  Insert succeeded: {inserted} row(s)")
        return {"status": "ok", "rows": inserted}
    except Exception as exc:  # pylint: disable=broad-except
        message = str(exc)
        print(f"  Insert failed: {message}")
        return {"status": "error", "error": message}


def main() -> None:
    env_status = print_env_status()

    client_info = with_supabase_client()
    client = client_info.get("client")
    client_error = client_info.get("error")

    if client_error:
        print("\nSupabase client initialization failed.")
        print(f"  Reason: {client_error}")

    select_result = test_select(client)
    describe_result = describe_table(client)
    insert_result = simulate_insert(client)

    print("\nSupabase Diagnostics Summary")
    print("----------------------------")
    print(f"URL present: {env_status.get('SUPABASE_URL', {}).get('present')}")
    service_info = env_status.get("SUPABASE_SERVICE_ROLE_KEY", {})
    print(
        f"Service key present: {service_info.get('present')} "
        f"(length {service_info.get('length')})"
    )
    anon_info = env_status.get("SUPABASE_ANON_KEY", {})
    print(
        f"Anon key present: {anon_info.get('present')} "
        f"(length {anon_info.get('length')})"
    )

    if select_result.get("status") == "ok":
        print(f"Select test: OK ({select_result.get('rows')} row)")
    elif select_result.get("status") == "skipped":
        print(f"Select test: SKIPPED ({select_result.get('error')})")
    else:
        print(f"Select test: FAIL ({select_result.get('error')})")

    if describe_result.get("status") == "ok":
        cols = describe_result.get("columns", [])
        printable_cols = ", ".join(cols) if cols else "(none)"
        print(f"Table columns: {printable_cols}")
    elif describe_result.get("status") == "skipped":
        print(f"Table columns: SKIPPED ({describe_result.get('error')})")
    else:
        print(f"Table columns: ERROR ({describe_result.get('error')})")

    if insert_result.get("status") == "ok":
        print("Insert test: OK")
    elif insert_result.get("status") == "skipped":
        print(f"Insert test: SKIPPED ({insert_result.get('error')})")
    else:
        print(f"Insert test: FAIL ({insert_result.get('error')})")

    if client_error:
        print(f"Client init error: {client_error}")


if __name__ == "__main__":
    main()

