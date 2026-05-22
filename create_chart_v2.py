
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import timedelta

APICURON_PURPLE       = "#4d194d"
APICURON_PURPLE_LIGHT = "#c084c0"
GRID_COLOUR           = "#e8dce8"

# Estimated height of a 2-line label (name + year) at 10.5 pt font, in pts.
# Used to place inter-stack connector lines so they sit in the gap between
# the top of the lower label and the bottom of the upper label.
LABEL_HEIGHT_PTS = 27.0
CONNECTOR_MARGIN = 2.0   # pts clear on each side of text


def create_chart_v2(csv_path, output_path, label_fontsize=10.5):
    df = pd.read_csv(csv_path)

    # Time-series columns
    ts = df[["period", "cumulative count"]].dropna().copy()
    ts["date"] = pd.to_datetime(ts["period"], format="%Y-%m")
    ts = ts.sort_values("date").reset_index(drop=True)

    # Resource join data
    res = df[["Resource", "Year"]].dropna().copy()
    res["join_date"] = pd.to_datetime(res["Year"], format="%Y-%m")

    def cum_at(d):
        mask = ts["date"] <= d
        return ts.loc[mask, "cumulative count"].iloc[-1] if mask.any() else ts["cumulative count"].iloc[0]

    res["cum_val"] = res["join_date"].apply(cum_at)
    res_dict = {row["Resource"]: (row["join_date"], row["cum_val"])
                for _, row in res.iterrows()}

    # --- Figure ---
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID_COLOUR, linewidth=0.8, linestyle="--")
    ax.xaxis.grid(False)
    for spine in ax.spines.values():
        spine.set_edgecolor("#ccbbcc")

    ax.plot(ts["date"], ts["cumulative count"],
            color=APICURON_PURPLE, linewidth=2.2, zorder=3)

    ax.scatter(res["join_date"], res["cum_val"],
               color=APICURON_PURPLE, s=55, zorder=4)

    # --- Annotation offsets: (x_pts, y_pts, va) ---
    # All labels use ha="center".  Positive y = above ("bottom"), negative = below ("top").
    # Clusters stack in 40 pt steps matching the DisProt/PED spacing.
    # Only the anchor (bottom/closest) label of each stack carries a connector arrow;
    # upper labels float so no line pierces through the stack text.
    resource_offsets = {
        # 2021-01 cluster — PED = anchor, DisProt = upper
        "DisProt":                   (  0, +90, "bottom"),
        "PED":                       (  0, +50, "bottom"),
        # singletons above the line
        "Biomappings":               (  0, +40, "bottom"),
        "Bioregistry":               (  0, +40, "bottom"),
        "PomBase":                   (  0, +40, "bottom"),
        "Rfam":                      (  0, +40, "bottom"),
        # Pfam below (swapped with PomBase to avoid overlap)
        "Pfam":                      (  0, -50, "top"),
        # 2023-12 cluster — Complex Portal = anchor
        "Complex Portal":            (  0, +50, "bottom"),
        "IntAct":                    (  0, +90, "bottom"),
        "Reactome":                  (  0,+130, "bottom"),
        "BioModels":                 (  0,+170, "bottom"),
        # SABIO-RK: tiny rightward nudge (~8 pts) to clear the trendline
        "SABIO-RK":                  ( +8, -47, "top"),
        "DOME Registry":             (  0, -50, "top"),
        # 2024-11 cluster — ELIXIR = anchor, PDBe = upper
        "ELIXIR Training Materials": (  0, +50, "bottom"),
        "PDBe":                      (  0, +90, "bottom"),
        # below-line singletons
        "Glittr.org":                (  0, -50, "top"),
        "microPublication":          (  0, -90, "top"),
        "S3 School":                 (  0, +40, "bottom"),
    }

    # Upper (non-anchor) stack labels: no arrow so the connector line
    # doesn't pierce through all the text above the data point.
    no_connector = {"DisProt", "IntAct", "Reactome", "BioModels", "PDBe"}

    for _, row in res.iterrows():
        name     = row["Resource"]
        date     = row["join_date"]
        cum_val  = row["cum_val"]
        year_str = str(row["Year"])[:4]
        x_off, y_off, va = resource_offsets.get(name, (0, +40, "bottom"))
        label = f"{name}\n({year_str})"

        arrow = None if name in no_connector else dict(
            arrowstyle="-",
            color=APICURON_PURPLE_LIGHT,
            lw=0.8,
            shrinkA=0,
            shrinkB=3,
            connectionstyle="arc3,rad=0",
        )

        ax.annotate(
            label,
            xy=(date, cum_val),
            xytext=(x_off, y_off),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=label_fontsize,
            color=APICURON_PURPLE,
            arrowprops=arrow,
        )

    # --- Axes ---
    axis_fontsize = label_fontsize + 5.5
    tick_fontsize = label_fontsize + 2.5

    ax.set_xlabel("Year", fontsize=axis_fontsize, labelpad=14, color="#1a001a")
    ax.set_ylabel("Cumulative annotation count",
                  fontsize=axis_fontsize, labelpad=14, color="#1a001a")

    ax.tick_params(axis="both", which="major", labelsize=tick_fontsize,
                   colors="#333333", length=4, pad=6)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x/1000)}k"))

    max_count = ts["cumulative count"].max()
    ax.set_ylim(0, max_count * 1.5)

    # End x-axis right at the last data point (tiny padding only)
    ax.set_xlim(
        ts["date"].min() - timedelta(days=40),
        ts["date"].max() + timedelta(days=15),
    )

    plt.tight_layout(pad=1.5)

    # --- Inter-stack connector lines ---
    # Draw AFTER tight_layout so the axes dimensions are finalised and we can
    # convert offset-point positions to data coordinates accurately.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax_h_px  = ax.get_window_extent(renderer).height          # pixels (screen DPI)
    pts_per_px = 72.0 / fig.dpi                               # pts per pixel
    ax_h_pts   = ax_h_px * pts_per_px                         # axes height in pts
    ymin, ymax = ax.get_ylim()
    data_per_pt = (ymax - ymin) / ax_h_pts                    # data units per pt

    def y_offset_to_data(y_pts, base_y):
        return base_y + y_pts * data_per_pt

    # Each stack: list of (resource_name, y_offset_pts) from bottom to top.
    # A short line is drawn in the gap between each adjacent pair.
    stacks = [
        [("PED", 50), ("DisProt", 90)],
        [("Complex Portal", 50), ("IntAct", 90), ("Reactome", 130), ("BioModels", 170)],
        [("ELIXIR Training Materials", 50), ("PDBe", 90)],
    ]

    for stack in stacks:
        date, base_y = res_dict[stack[0][0]]
        for i in range(len(stack) - 1):
            _, y_lower = stack[i]
            _, y_upper = stack[i + 1]
            # Line sits in the gap between top of lower text and bottom of upper text
            y_start = y_offset_to_data(y_lower + LABEL_HEIGHT_PTS + CONNECTOR_MARGIN, base_y)
            y_end   = y_offset_to_data(y_upper - CONNECTOR_MARGIN, base_y)
            ax.plot([date, date], [y_start, y_end],
                    color=APICURON_PURPLE_LIGHT, lw=0.8, zorder=2,
                    solid_capstyle="round")

    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Chart saved to {output_path}")


if __name__ == "__main__":
    create_chart_v2("APICURON_data_v2.csv", "apicuron_trendline_v2.png")
