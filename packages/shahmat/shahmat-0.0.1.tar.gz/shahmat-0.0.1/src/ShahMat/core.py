import time
import numpy as np
import pandas as pd
import requests
from datetime import datetime

from tqdm import tqdm
import matplotlib.pyplot as plt

#pd.set_option("display.max_columns", None)


def chesscom(username: str, *, start_year: int = 2025):

    URL = f"https://api.chess.com/pub/player/{username}/games"

    this_year, this_month = datetime.now().year, datetime.now().month

    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "AG Algo Lab (website: https://ag-algolab.github.io/)",
        "Accept": "application/json",
    })

    data = []

    for year in range(start_year, this_year+1):

        if year == this_year:
            max_month = this_month+1
        else:
            max_month = 13

        for month in tqdm(range(1,max_month),
                          desc=f"Extract {year}",
                          ascii='-#',
                          colour='green',
                          leave=False,
                          bar_format='{l_bar}{bar}| Remaining: {remaining}'
                          ):

            name = f'{year}-{month}'
            infos = f"{URL}/{year}/{month:02d}"
            res = sess.get(infos)

            if res.status_code == 200:
                output = res.json()
                games = output.get('games', [])

                if games:
                    extraction = pd.json_normalize(games)
                    data.append(extraction)

            else:
                print(res.status_code)

            time.sleep(.5)


    df = pd.concat(data, ignore_index=True)
    df['date'] = pd.to_datetime(df['end_time'], unit='s')
    df.set_index('date', inplace=True)
    df = df[['time_control',
             'time_class',
             'rated',
             'rules',
             'white.rating',
             'black.rating',
             'white.result',
             'black.result',
             'white.username',
             'black.username']]

    df["user_color"] = np.where(df["white.username"].str.lower() == username.lower(), "white", "black")

    df["user_elo"] = np.where(df["user_color"] == "white", df["white.rating"], df["black.rating"])
    df["opponent_elo"] = np.where(df["user_color"] == "white", df["black.rating"], df["white.rating"])
    df["elo_diff"] = df["user_elo"] - df["opponent_elo"]

    df["opponent_name"] = np.where(df["user_color"] == "white", df["black.username"], df["white.username"])

    draws = ["stalemate", "agreed", "repetition", "insufficient", "timevsinsufficient", "draw"]

    df["result"] = np.where(df["user_color"] == "white", df["white.result"], df["black.result"])
    df['result'] = np.where(df['result'] == 'win', 1, np.where(df['result'].isin(draws),.5,0))
    df['result_type'] = np.where(df['white.result'] == 'win', df['black.result'], df['white.result'])

    df = df[(df["rated"] == True) & (df["rules"] == "chess")]

    df = df.drop(columns=["white.username",
                          "black.username",
                          "white.rating",
                          "black.rating",
                          "white.result",
                          "black.result",
                          "rated",
                          "rules"])
    df_white = df[df['user_color']=='white']
    df_black = df[df['user_color']=='black']


    def hour_analysis():

        if len(df) == 0:
            raise KeyError("No data extracted")

        data_per_hour = {}
        n_per_hour = []
        sr_per_hour = []
        sr_per_hour_white = []
        sr_per_hour_black = []

        for hour in range(24):
            mask_hour = df.index.hour == hour
            df_hour = df[mask_hour]
            data_per_hour[hour] = df_hour

            n_per_hour.append(len(df_hour))

            sr_per_hour.append(round(df_hour["result"].mean(), 3) if len(df_hour) else np.nan)


        hours = list(range(24))

        sr_per_hour = np.array(sr_per_hour, dtype=float)
        sr_plot = np.nan_to_num(np.array(sr_per_hour, dtype=float), nan=0.0)

        sr_mean = df['result'].mean()
        sr_max = max(sr_plot)

        top3 = sr_per_hour.argsort()[-3:][::-1]
        print("==== Top 3 Best Hours (UTC) ====")
        for i, h in enumerate(top3, start=1):
            print(f"{i} -> {h}h  (score={sr_per_hour[h]:.3f})")


        fig, ax1 = plt.subplots(figsize=(10, 5))


        ax1.plot(hours, sr_plot, marker="o", color="tab:blue", label="Score rate")
        ax1.set_xlabel("Hour of day (UTC)")
        ax1.set_ylabel("Score rate (0=loss, 0.5=draw, 1=win)", color="tab:blue")
        ax1.tick_params(axis='y', labelcolor="tab:blue")
        ax1.set_xticks(range(24))
        ax1.set_ylim(0, 1)

        ax1.axhline(sr_mean, color="tab:grey", linestyle=":", linewidth=1.5, label="Average Score Rate")
        ax1.axhline(sr_max, color="tab:green", linestyle=":", linewidth=1.5, label="Max Score Rate")


        ax2 = ax1.twinx()
        ax2.bar(hours, n_per_hour, alpha=0.3, color="tab:purple", label="Number of games")
        ax2.set_ylabel("Number of games", color="tab:purple")
        ax2.tick_params(axis='y', labelcolor="tab:purple")

        plt.title("Score rate & number of games per hour")
        fig.tight_layout()
        plt.show()


    def elo_diff(bin_size=5):

        if "elo_diff" not in df.columns or "result" not in df.columns or "user_color" not in df.columns:
            raise KeyError("Columns missing: 'elo_diff', 'result', 'user_color'.")

        if len(df_white) == 0 and len(df_black) == 0:
            raise KeyError("No data extracted")
            return

        lo = np.floor(df["elo_diff"].min() / bin_size) * bin_size
        hi = np.ceil(df["elo_diff"].max() / bin_size) * bin_size
        if lo == hi:
            lo -= bin_size
            hi += bin_size
        edges = np.arange(lo, hi + bin_size, bin_size)

        def make_curve(dfc):
            if len(dfc) == 0:
                return np.array([]), np.array([]), np.array([])

            cats = pd.cut(dfc["elo_diff"], bins=edges, include_lowest=True)
            stats = dfc.groupby(cats, observed=True).agg(sr=("result", "mean"), n=("result", "size"))

            stats = stats[stats["n"] > 1]
            if len(stats) == 0:
                return np.array([]), np.array([]), np.array([])

            x = np.array([(iv.left + iv.right) / 2 for iv in stats.index])
            y = stats["sr"].values.astype(float)
            n = stats["n"].values.astype(int)
            return x, y, n

        x_w, y_w, n_w = make_curve(df_white)
        x_b, y_b, n_b = make_curve(df_black)

        plt.figure(figsize=(10, 5))
        if x_w.size:
            plt.plot(x_w, y_w, marker="o", linestyle="-", color="gray", label=f"White")
        else:
            print(f"[Info] Pas assez de points pour White (< 2).")

        if x_b.size:
            plt.plot(x_b, y_b, marker="o", linestyle="-", color="black", label=f"Black")
        else:
            print(f"[Info] Pas assez de points pour Black (< 2).")

        # Aides visuelles
        plt.axvline(0, linestyle="--", linewidth=.5)
        plt.axhline(0.5, linestyle=":", linewidth=.5)
        plt.ylim(0, 1)
        plt.xlabel("Elo diff (reference: you)")
        plt.ylabel("Score rate (0=loss, 0.5=draw, 1=win)")
        plt.title(f"Score rate vs Elo diff (bin={bin_size})")
        plt.legend()
        plt.tight_layout()
        plt.show()


    def result(min_pct=.03):

        if "result" not in df.columns or "result_type" not in df.columns:
            raise KeyError("Colonnes requises manquantes: 'result' et 'result_type'.")

        wins = df[df["result"] == 1]
        losses = df[df["result"] == 0]

        def prep(series, min_pct):
            if series.empty:
                return np.array([]), []
            s = series.fillna("unknown").astype(str)
            counts = s.value_counts()
            total = counts.sum()
            if total == 0:
                return np.array([]), []

            pct = counts / total
            small = pct[pct < min_pct].index
            if len(small):
                counts.loc["Other"] = counts.loc[small].sum()
                counts = counts.drop(small)

            sizes = counts.values
            labels = list(counts.index)
            return sizes, labels

        sizes_w, labels_w = prep(wins["result_type"], min_pct)
        sizes_l, labels_l = prep(losses["result_type"], min_pct)


        fig, axes = plt.subplots(1, 2, figsize=(14, 7))


        ax = axes[0]
        if sizes_w.size:
            wedges, texts, autotexts = ax.pie(
                sizes_w,
                labels=labels_w,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"linewidth": 1, "edgecolor": "white"},
            )
            ax.axis("equal")
            ax.set_title("When YOU win – opponent's result types")
        else:
            ax.text(0.5, 0.5, "No wins in data", ha="center", va="center", fontsize=12)
            ax.axis("off")


        ax = axes[1]
        if sizes_l.size:
            wedges, texts, autotexts = ax.pie(
                sizes_l,
                labels=labels_l,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"linewidth": 1, "edgecolor": "white"},
            )
            ax.axis("equal")
            ax.set_title("When YOU lose – your result types")
        else:
            ax.text(0.5, 0.5, "No losses in data", ha="center", va="center", fontsize=12)
            ax.axis("off")

        plt.suptitle("Result type breakdown (wins vs losses)", fontsize=14, y=0.98)
        plt.tight_layout()
        plt.show()




    def all_def():
        hour_analysis()
        elo_diff()
        result()






    def download():
        export = df[['user_color','time_class','user_elo','opponent_elo','result','result_type']]
        export.to_csv(f"chesscom_data_{username}.csv", index=True)




    actions = {
        "1": ("Performance by Hour", lambda: hour_analysis()),
        "2": ("Elo Difference + Color", lambda: elo_diff()),
        "3": ("Type of ending", lambda: result()),
        "4": ("Complete Analysis", lambda: all_def()),
        "5": ("Download Data", lambda: download()),
        "0": ("Quit", None),
    }
    while True:
        print("\nPick the angle to explore your games:")
        for k, (label, _) in actions.items():
            print(f"  {k}. {label}")
        choice = input("> ").strip()
        if choice == "0" or choice not in actions:
            break
        _, fn = actions[choice]
        fn()

