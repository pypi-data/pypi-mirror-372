from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Union
import datetime as _dt
import warnings
import threading

import pandas as pd
from pandas.errors import DtypeWarning

from .state import StateManager, resolve_home
from .audit import audit_dataframe, write_audit_logs, audit_to_text
from .reconnecting import run_async as _ppo_run_async, generate_sync as _ppo_run_sync

PathLike = Union[str, Path]


def get_home() -> Path:
    """
    Returns the internal working directory of the library
    (by default <venv>/var/csv_health).
    """
    return resolve_home()


def _process(df: pd.DataFrame) -> pd.DataFrame:
    """
    Private processing stub:
    - trims object columns
    - drop_duplicates
    - adds UTC processed_at
    """
    out = df.copy()
    obj_cols = out.select_dtypes(include=["object"]).columns
    for c in obj_cols:
        out[c] = out[c].astype(str).str.strip()
    out = out.drop_duplicates()
    out["processed_at"] = _dt.datetime.utcnow().isoformat() + "Z"
    return out


def _read_csv_safely(path: Path) -> pd.DataFrame:
    """
    Robust CSV reader:
    - silences DtypeWarning
    - uses low_memory=False to avoid chunked type inference
    """
    warnings.simplefilter("ignore", DtypeWarning)
    return pd.read_csv(path, low_memory=False)


def analyze_csv(
    input_data: Union[PathLike, pd.DataFrame],
    report_path: PathLike | None = None,
    report_text_path: PathLike | None = None,
    preview: bool = False,
):
    """
    Analyze a CSV file or DataFrame and optionally preview generated predictions.

    Parameters
    ----------
    input_data : str | Path | pandas.DataFrame
        Either path to a CSV file or an already loaded DataFrame.
        In preview mode the value is ignored (kept for API symmetry).
    report_path : str | Path, optional
        Custom path to save JSON report (non-preview mode).
    report_text_path : str | Path, optional
        Custom path to save TXT report (non-preview mode).
    preview : bool, default False
        If False (default):
           - performs full audit of the CSV
           - remembers the file
           - kicks off background PPO predictions into <venv>/var/csv_health/ppo_predictions.csv
           - RETURNS dict with audit/report paths and internal state.

    Returns
    -------
    dict | pandas.DataFrame
        - preview=False → dict with audit/report paths and internal state
    """
    mgr = StateManager()
    home = mgr.home
    ppo_out = home / "ppo_predictions.csv"

    # ---- PREVIEW MODE ----
    if preview:
        # if predictions do not exist yet — generate synchronously from remembered copy
        if not ppo_out.exists():
            state = mgr.read()
            if not state:
                raise RuntimeError("No previous analysis found. Call analyze_csv(<path>) first.")
            copy_path = Path(state.copy_path)
            if not copy_path.exists():
                raise RuntimeError("Remembered copy not found. Call analyze_csv(<path>) again.")
            _ppo_run_sync(copy_path, ppo_out)

        preview_df = pd.read_csv(ppo_out)
        # print only first 50 rows for a concise console preview
        print("===== PPO PREVIEW (first 50 rows) =====")
        try:
            print(preview_df.head(50).to_string(index=False))
        except Exception:
            # fallback if there are very wide columns
            print(preview_df.head(50))
        print("=======================================")
        # return the FULL dataframe
        return preview_df

    # ---- REGULAR AUDIT MODE ----
    # Accept path or DataFrame; normalize to in_path + df
    if isinstance(input_data, (str, Path)):
        in_path = Path(input_data).expanduser().resolve()
        if not in_path.exists():
            raise FileNotFoundError(f"CSV not found: {in_path}")
        df = _read_csv_safely(in_path)
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
        in_path = home / "tmp_input.csv"
        df.to_csv(in_path, index=False)
    else:
        raise TypeError("input_data must be a path or pandas.DataFrame")

    # remember copy + state
    state = mgr.write_copy_and_state(in_path)

    # audit
    rep = audit_dataframe(df, file_path=in_path)

    # write reports
    if report_path is not None:
        json_out = Path(report_path).expanduser().resolve()
        json_out.parent.mkdir(parents=True, exist_ok=True)
        if report_text_path is not None:
            text_out = Path(report_text_path).expanduser().resolve()
            text_out.parent.mkdir(parents=True, exist_ok=True)
        else:
            text_out = json_out.with_suffix(".txt")
        import json as _json
        json_out.write_text(_json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        text_txt = audit_to_text(rep)
        text_out.write_text(text_txt, encoding="utf-8")
    else:
        json_out, text_out = write_audit_logs(rep, mgr.logs_dir, state.sha256)
        text_txt = audit_to_text(rep)

    mgr.enhance_with_audit_paths(state, json_out, text_out)

    # print audit to console (concise)
    print("===== CSV AUDIT =====")
    print(text_txt)
    print("=====================")

    # background PPO generation from the remembered copy
    copy_path = Path(state.copy_path)
    t = threading.Thread(target=_ppo_run_async, args=(copy_path, ppo_out), daemon=True)
    t.start()

    return {
        "path": str(in_path),
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "sha256": state.sha256,
        "audit_json": str(json_out),
        "audit_text": str(text_out),
        "ppo_predictions": str(ppo_out),
        "home": str(home),
    }


def save_processed(output_csv: PathLike | None = None) -> Path:
    """
    Process the remembered copy and save the result.
    Default location: <venv>/var/csv_health/processed/<stem>_<ts>_processed.csv
    """
    mgr = StateManager()
    st = mgr.read()
    if not st:
        raise RuntimeError("Call analyze_csv() first.")

    copy_path = Path(st.copy_path)
    if not copy_path.exists():
        raise RuntimeError("Copy not found. Call analyze_csv() again.")

    df = _read_csv_safely(copy_path)
    out_df = _process(df)

    if output_csv is not None:
        out_path = Path(output_csv).expanduser().resolve()
    else:
        orig = Path(st.original_path)
        ts = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        out_path = mgr.processed_dir / f"{orig.stem}_{ts}_processed.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    return out_path


def get_state() -> dict | None:
    """
    Returns current internal state or None.
    """
    mgr = StateManager()
    st = mgr.read()
    return None if not st else {
        "original_path": st.original_path,
        "copy_path": st.copy_path,
        "sha256": st.sha256,
        "last_audit_json": st.last_audit_json,
        "last_audit_text": st.last_audit_text,
        "home": str(mgr.home),
    }


def clear_state() -> None:
    """
    Clears remembered state and last input copy.
    """
    StateManager().clear()
