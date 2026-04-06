
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# APICURON brand colours
APICURON_PURPLE = "#4d194d"
APICURON_PURPLE_MID = "#742574"
APICURON_PURPLE_LIGHT = "#c084c0"
GRID_COLOUR = "#e8dce8"

def create_trendline_chart(csv_path, output_path, label_fontsize=8.5):
    """
    Creates a publication-quality trendline chart from the APICURON data,
    plotting the cumulative count of partner resource integrations over time
    using exact join dates from apicuron.org/databases, and annotating with
    the names of the integrated resources.

    Args:
        csv_path (str): The path to the input CSV file.
        output_path (str): The path to save the output chart image.
    """
    df = pd.read_csv(csv_path)
    df["Date Added"] = pd.to_datetime(df["Date Added"])
    df = df.sort_values("Date Added").reset_index(drop=True)

    # Build step-function data: one point just before each event, one at the event
    dates = df["Date Added"].tolist()
    n = len(dates)
    cumulative = list(range(1, n + 1))

    # For a proper step function we add an origin point before the first join
    origin = dates[0] - timedelta(days=30)
    step_dates = [origin] + dates
    step_counts = [0] + cumulative

    # --- Figure ---
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Grid
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID_COLOUR, linewidth=0.8, linestyle="--")
    ax.xaxis.grid(False)
    for spine in ax.spines.values():
        spine.set_edgecolor("#ccbbcc")

    # Draw step function (post: the value holds until the next event)
    ax.step(step_dates, step_counts, where="post",
            color=APICURON_PURPLE, linewidth=2.2, zorder=3)

    # Markers at each join event
    ax.scatter(dates, cumulative,
               color=APICURON_PURPLE, s=50, zorder=4)

    # --- Annotations ---
    # Per-resource annotation offsets: (x_points, y_points, ha, va)
    # x/y in offset points from the data point.
    # Clock positions: 12=straight up (0,+), 3=straight right (+,0),
    # 9=straight left (-,0), 4:30=down-right 45°, 10:30=up-left 45°.
    resource_offsets = {
        "DisProt":                   ( +35,    0, "left",   "center"),  # 3 o'clock
        "PED":                       (   0,  +25, "center", "bottom"),  # 12 o'clock
        "Biomappings":               (   0,  +25, "center", "bottom"),  # 12 o'clock
        "Bioregistry":               ( -25,  +25, "center", "bottom"),  # 10:30 (mirror of Pfam)
        "Pfam":                      ( +20,  -20, "left",   "top"),     # 4:30
        "PomBase":                   (   0,  +25, "center", "bottom"),  # 12 o'clock
        "Rfam":                      (   0,  +25, "center", "bottom"),  # 12 o'clock
        "BioModels":                 ( +50,    0, "left",   "center"),  # 3 o'clock
        "Reactome":                  ( +50,    0, "left",   "center"),  # 3 o'clock
        "IntAct":                    ( +50,    0, "left",   "center"),  # 3 o'clock
        "Complex Portal":            ( +50,    0, "left",   "center"),  # 3 o'clock
        "SABIO-RK":                  ( -25,  +25, "center", "bottom"),  # 10:30 (mirror of Pfam)
        "DOME Registry":             ( -25,  +25, "center", "bottom"),  # 10:30 (mirror of Pfam)
        "ELIXIR Training Materials": ( -25,  +25, "center", "bottom"),  # 10:30 (mirror of Pfam)
        "PDBe":                      ( +45,    0, "left",   "center"),  # 3 o'clock
        "Glittr.org":                ( +45,    0, "left",   "center"),  # 3 o'clock
        "microPublication":          (   0,  +25, "center", "bottom"),  # 12 o'clock
        "S3 School":                 (   0,  +25, "center", "bottom"),  # 12 o'clock
    }

    # Display text overrides — line-break long labels so they stay compact
    label_overrides = {
        "DOME Registry":             "DOME\nRegistry",
        "ELIXIR Training Materials": "ELIXIR Training\nMaterials",
    }

    for idx, row in df.iterrows():
        name = row["Resource Name"]
        date = row["Date Added"]
        cum_val = cumulative[idx]
        x_off, y_off, ha, va = resource_offsets.get(name, (0, 45, "center", "bottom"))
        label = label_overrides.get(name, name)

        ax.annotate(
            label,
            xy=(date, cum_val),
            xytext=(x_off, y_off),
            textcoords="offset points",
            ha=ha,
            va=va,
            fontsize=label_fontsize,
            color=APICURON_PURPLE,
            arrowprops=dict(arrowstyle="-", color=APICURON_PURPLE_LIGHT,
                            lw=0.8, shrinkA=0, shrinkB=3,
                            connectionstyle="arc3,rad=0"),
        )

    # --- Axes formatting ---
    axis_fontsize = label_fontsize + 5.5
    tick_fontsize = label_fontsize + 2.5
    ax.set_xlabel("Year", fontsize=axis_fontsize, labelpad=14, color="#1a001a")
    ax.set_ylabel("Cumulative number of partner resources",
                  fontsize=axis_fontsize, labelpad=14, color="#1a001a")

    ax.tick_params(axis="both", which="major", labelsize=tick_fontsize,
                   colors="#333333", length=4, pad=6)

    # Date axis: show a tick at every Jan 1
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Y axis: integers only
    max_count = n
    ax.set_ylim(0, max_count + 3)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Extend x range a bit for breathing room
    ax.set_xlim(origin - timedelta(days=20),
                df["Date Added"].max() + timedelta(days=180))

    plt.tight_layout(pad=1.5)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Chart saved to {output_path}")


if __name__ == "__main__":
    # Base size (8.5pt labels) — current version
    create_trendline_chart(
        "APICURON_paper_figure_trend_data.csv",
        "apicuron_trendline.png"
    )
    # +2pt labels (10.5pt)
    create_trendline_chart(
        "APICURON_paper_figure_trend_data.csv",
        "apicuron_trendline_plus2.png",
        label_fontsize=10.5
    )
    # +4pt labels (12.5pt)
    create_trendline_chart(
        "APICURON_paper_figure_trend_data.csv",
        "apicuron_trendline_plus4.png",
        label_fontsize=12.5
    )
    # +6pt labels (14.5pt)
    create_trendline_chart(
        "APICURON_paper_figure_trend_data.csv",
        "apicuron_trendline_plus6.png",
        label_fontsize=14.5
    )
