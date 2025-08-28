
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import os, json, pandas as pd
from datetime import datetime

def _safe_float(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return None

def _depth_summary(val: Any) -> Dict[str, Any]:
    if not isinstance(val, str):
        return {}
    try:
        payload = json.loads(val)
        bids = payload.get("b") or payload.get("B") or []
        asks = payload.get("a") or payload.get("A") or []
        sym = payload.get("s") or payload.get("symbol")
        def _first(levels):
            if not levels:
                return None, None
            p, q = levels[0]
            return float(p), float(q)
        bid_px, bid_qty = _first(bids)
        ask_px, ask_qty = _first(asks)
        spread = (ask_px - bid_px) if (bid_px is not None and ask_px is not None) else None
        mid = (ask_px + bid_px)/2 if (bid_px is not None and ask_px is not None) else None
        return {
            "symbol": sym,
            "bids_levels": len(bids),
            "asks_levels": len(asks),
            "best_bid_px": bid_px,
            "best_bid_qty": bid_qty,
            "best_ask_px": ask_px,
            "best_ask_qty": ask_qty,
            "spread": spread,
            "mid": mid,
        }
    except Exception as e:
        return {"parse_error": str(e)}

def audit_dataframe(df: pd.DataFrame, file_path: Path | None = None) -> Dict[str, Any]:
    rows, cols = df.shape
    na_counts = df.isna().sum()
    cells_total = rows * cols
    na_total = int(na_counts.sum())
    report: Dict[str, Any] = {
        "rows": int(rows),
        "cols": int(cols),
        "cells_total": int(cells_total),
        "missing_cells": int(na_total),
        "missing_pct_total": float((na_total / cells_total * 100) if cells_total else 0.0),
        "memory_bytes_est": int(df.memory_usage(deep=True).sum()),
        "missing_by_column": {c: int(na_counts[c]) for c in df.columns},
    }
    if file_path and file_path.exists():
        report["file_bytes"] = int(os.path.getsize(file_path))

    if "ts" in df.columns and rows>0:
        ts_raw = df.loc[df.index[0], "ts"]
        try:
            ts_dt = pd.to_datetime(ts_raw, utc=False, errors="raise")
            report["ts"] = {"raw": str(ts_raw), "parsed_ok": True, "iso": ts_dt.isoformat()}
        except Exception:
            report["ts"] = {"raw": str(ts_raw), "parsed_ok": False, "iso": None}

    # OHLC common prefixes
    for prefix in ("ohlcv_5m_", "ohlcv_1m_", "ohlcv_"):
        o,h,l,c = f"{prefix}open", f"{prefix}high", f"{prefix}low", f"{prefix}close"
        if all(k in df.columns for k in (o,h,l,c)) and rows>0:
            try:
                oo = _safe_float(df.loc[df.index[0], o])
                hh = _safe_float(df.loc[df.index[0], h])
                ll = _safe_float(df.loc[df.index[0], l])
                cc = _safe_float(df.loc[df.index[0], c])
                if None not in (oo,hh,ll,cc):
                    report["ohlc_checks"] = {
                        "low<=open<=high": bool(ll <= oo <= hh),
                        "low<=close<=high": bool(ll <= cc <= hh),
                        "open_close_equal": bool(abs(oo-cc) < 1e-12),
                        "all_equal": bool(abs(oo-hh)<1e-12 and abs(oo-ll)<1e-12 and abs(oo-cc)<1e-12),
                    }
            except Exception:
                pass
            break

    if "depth_raw" in df.columns and rows>0:
        report["depth_raw_summary"] = _depth_summary(df.loc[df.index[0], "depth_raw"])

    # Suggested deltas
    def sg(col): 
        return _safe_float(df.loc[df.index[0], col]) if (col in df.columns and rows>0) else None
    bc, sc = sg("mkt_order_buy_sell_cnt_buyCnt"), sg("mkt_order_buy_sell_cnt_sellCnt")
    bv, sv = sg("mkt_order_buy_sell_val_buyUsd"), sg("mkt_order_buy_sell_val_sellUsd")
    bvol, svol = sg("mkt_order_buy_sell_vol_buyVol"), sg("mkt_order_buy_sell_vol_sellVol")
    suggested = {}
    if bc is not None and sc is not None:
        suggested["mkt_order_buy_sell_cnt_deltaCnt (buy-sell)"] = bc - sc
    if bv is not None and sv is not None:
        suggested["mkt_order_buy_sell_val_deltaUsd (buy-sell)"] = bv - sv
    if bvol is not None and svol is not None:
        suggested["mkt_order_buy_sell_vol_deltaVol (buy-sell)"] = bvol - svol
    if suggested:
        report["suggested_missing_values"] = suggested

    # First row preview
    preview = []
    for c in df.columns:
        v = df.loc[df.index[0], c] if rows>0 else None
        entry = {"column": c, "dtype": str(df[c].dtype), "null": bool(pd.isna(v))}
        if not pd.isna(v):
            s = str(v)
            entry["value_preview"] = s[:200] + ("…" if len(s)>200 else "")
        preview.append(entry)
    report["first_row_preview"] = preview

    return report

def audit_to_text(rep: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Rows: {rep.get('rows')}  Cols: {rep.get('cols')}  Cells: {rep.get('cells_total')}")
    if "file_bytes" in rep:
        lines.append(f"File bytes: {rep['file_bytes']}")
    lines.append(f"Missing cells: {rep.get('missing_cells')} ({rep.get('missing_pct_total'):.4f}%)")
    lines.append(f"DF memory bytes: {rep.get('memory_bytes_est')}")
    ts = rep.get("ts")
    if ts:
        lines.append(f"ts: raw={ts.get('raw')} parsed_ok={ts.get('parsed_ok')} iso={ts.get('iso')}")
    ohlc = rep.get("ohlc_checks")
    if ohlc:
        lines.append("OHLC checks: " + ", ".join([f"{k}={v}" for k,v in ohlc.items()]))
    depth = rep.get("depth_raw_summary")
    if depth:
        lines.append("Depth: " + ", ".join([f"{k}={v}" for k,v in depth.items()]))
    sugg = rep.get("suggested_missing_values")
    if sugg:
        lines.append("Suggested deltas: " + ", ".join([f"{k}={v}" for k,v in sugg.items()]))
    lines.append("Missing by column:")
    for k,v in rep.get("missing_by_column", {}).items():
        if v:
            lines.append(f"  - {k}: {v}")
    return "\n".join(lines)

def write_audit_logs(rep: Dict[str, Any], logs_dir: Path, sha: str) -> tuple[Path, Path]:
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    base = f"{ts}_{sha}"
    json_path = logs_dir / f"{base}.json"
    text_path = logs_dir / f"{base}.txt"
    json_path.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    text_path.write_text(audit_to_text(rep), encoding="utf-8")
    return json_path, text_path
