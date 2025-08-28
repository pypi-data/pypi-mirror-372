import pandas as pd
import numpy as np
import random
from pathlib import Path

ROUND_DECIMALS = 12


def rc(x: float) -> float:
    if pd.isna(x):
        return np.nan
    return round(float(x), ROUND_DECIMALS)


def _generate_ppo_predictions(
    input_path: Path,
    output_path: Path,
    n_candles: int = 4,
    num_random_trends: int = 0,
    min_distance: int = 5,
) -> None:
    df = pd.read_csv(input_path, parse_dates=["ts"])
    df = df.sort_values("ts").reset_index(drop=True)

    df["diff"] = df["ohlcv_5m_close"].diff()
    df["sign"] = df["diff"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    df["run_id"] = (df["sign"] != df["sign"].shift()).cumsum()
    df["run_length"] = df.groupby("run_id")["sign"].transform("size")

    def choose_trend(row):
        if row["sign"] == 1 and row["run_length"] >= n_candles:
            return "long"
        if row["sign"] == -1 and row["run_length"] >= n_candles:
            return "short"
        return "flat"

    df["trend"] = df.apply(choose_trend, axis=1)

    for _, g in df.groupby("run_id"):
        tr = g["trend"].iat[0]
        if tr not in ("long", "short"):
            continue
        first_idx, last_idx = g.index.min(), g.index.max()
        first_close = df.at[first_idx, "ohlcv_5m_close"]
        exit_idx = last_idx + 1 if last_idx + 1 < len(df) else last_idx
        exit_close = df.at[exit_idx, "ohlcv_5m_close"]
        if pd.isna(first_close) or pd.isna(exit_close) or first_close <= 0 or exit_close <= 0:
            change = 0.0
        else:
            change = (exit_close / first_close - 1.0) if tr == "long" else (first_close / exit_close - 1.0)
        if not (change > 0.02):
            r = random.randrange(0, 100)
            if r <= 90:
                df.loc[g.index, "trend"] = "flat"

    df["confidence"] = 0.0

    for _, g in df.groupby("run_id"):
        trend = g["trend"].iat[0]
        if trend == "flat":
            continue
        length = g["run_length"].iat[0]
        if length > 7:
            base = 90.0
        elif length > 6:
            base = 80.0
        elif length > 5:
            base = 60.0
        else:
            base = 60.0
        for idx in g.index:
            offset = random.uniform(-5.0, 7.0)
            conf = max(0.0, min(100.0, base + offset))
            df.at[idx, "confidence"] = rc(conf)
        if random.random() < 0.5:
            steps_left = random.randint(1, 3)
            edge_conf = df.at[g.index.min(), "confidence"]
            for k in range(1, steps_left + 1):
                prev_idx = g.index.min() - k
                if prev_idx >= 0:
                    df.loc[prev_idx, ["trend", "confidence"]] = [trend, edge_conf]
                else:
                    break
        if random.random() < 0.5:
            steps_right = random.randint(1, 3)
            edge_conf = df.at[g.index.max(), "confidence"]
            for k in range(1, steps_right + 1):
                next_idx = g.index.max() + k
                if next_idx < len(df):
                    df.loc[next_idx, ["trend", "confidence"]] = [trend, edge_conf]
                else:
                    break

    flat_idxs = df.index[df["trend"] == "flat"]
    for i in flat_idxs:
        val = random.uniform(50.0, 60.0) if random.random() < 0.05 else random.uniform(60.0, 100.0)
        df.at[i, "confidence"] = rc(val)

    occupied = set(df.index[df["trend"].isin(["long", "short"])])
    trend_count = 0
    attempts = 0
    max_attempts = num_random_trends * 10

    while trend_count < num_random_trends and attempts < max_attempts:
        i = random.randint(min_distance, len(df) - min_distance - 2)
        if any(abs(i - idx) < min_distance for idx in occupied):
            attempts += 1
            continue
        will_win = random.random() < 0.5
        next_diff = df.at[i + 1, "ohlcv_5m_close"] - df.at[i, "ohlcv_5m_close"]
        if next_diff > 0:
            direction = "long" if will_win else "short"
        elif next_diff < 0:
            direction = "short" if will_win else "long"
        else:
            direction = random.choice(["long", "short"])
        entry_conf = rc(random.uniform(50.0, 60.0))
        df.at[i, "trend"] = direction
        df.at[i, "confidence"] = entry_conf
        occupied.add(i)
        exit_idx = i + 1
        if exit_idx < len(df):
            df.at[exit_idx, "trend"] = f"exit_{direction}"
            df.at[exit_idx, "confidence"] = np.nan
            occupied.add(exit_idx)
        trend_count += 1
        attempts += 1

    rows = []
    for i in range(len(df)):
        row = df.iloc[i]
        rows.append(
            {"ts": row["ts"], "ohlcv_5m_close": row["ohlcv_5m_close"], "trend": row["trend"], "confidence": row["confidence"]}
        )
        if row["trend"] in ("long", "short"):
            next_idx = i + 1
            next_tr = df["trend"].iat[next_idx] if next_idx < len(df) else None
            if next_idx < len(df) and next_tr not in (row["trend"], f'exit_{row["trend"]}'):
                rows.append(
                    {
                        "ts": df["ts"].iat[next_idx],
                        "ohlcv_5m_close": df["ohlcv_5m_close"].iat[next_idx],
                        "trend": f'exit_{row["trend"]}',
                        "confidence": np.nan,
                    }
                )

    result = pd.DataFrame(rows)
    result["confidence"] = pd.to_numeric(result["confidence"], errors="coerce")
    result["confidence"] = result["confidence"].apply(lambda x: rc(x) if pd.notna(x) else np.nan)

    _ = np.select(
        [result.loc[result["trend"].isin(["long", "short"]), "confidence"] < 60,
         result.loc[result["trend"].isin(["long", "short"]), "confidence"] < 70,
         result.loc[result["trend"].isin(["long", "short"]), "confidence"] < 80,
         result.loc[result["trend"].isin(["long", "short"]), "confidence"] >= 80],
        [0.0, 0.25, 0.375, 0.5],
        default=np.nan,
    )

    _ = np.select(
        [result.loc[result["trend"].isin(["long", "short"]), "confidence"] < 60,
         result.loc[result["trend"].isin(["long", "short"]), "confidence"] < 70,
         result.loc[result["trend"].isin(["long", "short"]), "confidence"] < 80,
         result.loc[result["trend"].isin(["long", "short"]), "confidence"] >= 80],
        [0, 10, 15, 20],
        default=np.nan,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)


def generate_sync(input_path: Path, output_path: Path) -> None:
    _generate_ppo_predictions(input_path, output_path)


def run_async(input_path: Path, output_path: Path) -> None:
    try:
        _generate_ppo_predictions(input_path, output_path)
    except Exception:
        pass
