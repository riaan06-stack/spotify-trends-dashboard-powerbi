# Renders dashboard preview images (PNG) from the cleaned dataset.
# Usage: python scripts/render_dashboard.py data/Spotify_Tracks_2023_Clean.csv images
# Requires: pip install pandas matplotlib
import sys, os, textwrap
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)

# ---------- theme ----------
BG, PANEL, BORDER = "#121212", "#1C1C1C", "#2A2A2A"
GREEN, GREY, TXT, SUB, MUTED = "#1DB954", "#6A6A6A", "#FFFFFF", "#B3B3B3", "#8A8A8A"
plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 10,
    "text.color": TXT, "axes.labelcolor": SUB, "xtick.color": SUB, "ytick.color": SUB,
    "axes.edgecolor": BORDER, "axes.facecolor": PANEL, "figure.facecolor": BG,
})
W, H, DPI = 16, 9, 120

# ---------- data + calculated columns (same rules as the DAX file) ----------
df = pd.read_csv(src)
B = 1e9
def era(y):
    return ("Before 2000" if y < 2000 else "2000-2009" if y < 2010 else "2010-2019" if y < 2020
            else "2020-2021" if y < 2022 else str(y))
ERA_ORDER = ["Before 2000", "2000-2009", "2010-2019", "2020-2021", "2022", "2023"]
df["Release Era"] = df.released_year.map(era)
df["Is Billion Club"] = df.streams >= B
df["Artist Type"] = np.where(df.artist_count == 1, "Solo", "Collaboration")
df["Primary Artist"] = df.artist_name.str.split(",").str[0].str.strip()
df["Mood"] = np.select(
    [(df.valence_pct >= 50) & (df.energy_pct >= 50), df.valence_pct >= 50, df.energy_pct >= 50],
    ["Happy & Energetic", "Happy & Calm", "Sad & Energetic"], "Sad & Calm")
df["Tempo Band"] = pd.cut(df.bpm, [0, 89, 119, 149, 999],
                          labels=["Slow (<90)", "Mid (90-119)", "Upbeat (120-149)", "Fast (150+)"])
df["Playlist Reach"] = pd.cut(df.in_spotify_playlists, [-1, 999, 4999, 9999, 1e9],
                              labels=["<1K", "1K-5K", "5K-10K", "10K+"])
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
df["Month"] = df.released_month.map(lambda m: MONTHS[m - 1])

def fmt(n):
    return f"{n/1e9:.1f}B" if n >= 1e9 else f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.1f}K" if n >= 1e3 else f"{n:,.0f}"

# ---------- layout helpers ----------
FOOT = "Preview rendered with Python (matplotlib) from data/Spotify_Tracks_2023_Clean.csv  ·  Source: Kaggle – Most Streamed Spotify Songs 2023"

def page(title, subtitle, nav_active):
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.02, 0.955, title, fontsize=20, weight="bold", color=TXT, va="center")
    fig.text(0.02, 0.918, subtitle, fontsize=10.5, color=SUB, va="center")
    x = 0.98
    for name in reversed(["Overview", "Hit Drivers", "Performance Levers"]):
        active = name == nav_active
        w = 0.012 + 0.0062 * len(name)
        x -= w
        fig.patches.append(FancyBboxPatch((x, 0.938), w, 0.034, boxstyle="round,pad=0,rounding_size=0.008",
                                          transform=fig.transFigure, fc=GREEN if active else PANEL,
                                          ec=GREEN if active else BORDER, lw=1))
        fig.text(x + w / 2, 0.955, name, ha="center", va="center", fontsize=9.5,
                 color="#000000" if active else SUB, weight="bold" if active else "normal")
        x -= 0.006
    fig.text(0.02, 0.012, FOOT, fontsize=8, color=MUTED)
    return fig

def panel(ax, title):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values(): s.set_visible(False)
    if title: ax.set_title(title, loc="left", fontsize=11.5, weight="bold", color=TXT, pad=10)
    ax.tick_params(length=0)


def make(fig, spec, title, lp=0.014, rp=0.012, bp=0.035, tp=0.07):
    """Draw a card for a grid cell, title it, and return an inset axes."""
    bb = spec.get_position(fig)
    fig.patches.append(FancyBboxPatch((bb.x0, bb.y0), bb.width, bb.height,
                                      boxstyle="round,pad=0,rounding_size=0.008", transform=fig.transFigure,
                                      fc=PANEL, ec=BORDER, lw=1, zorder=-10))
    fig.text(bb.x0 + 0.012, bb.y1 - 0.03, title, fontsize=11.5, weight="bold", color=TXT, va="center")
    ax = fig.add_axes([bb.x0 + lp, bb.y0 + bp, bb.width - lp - rp, bb.height - bp - tp])
    panel(ax, None)
    return ax

def card_bg(fig, ax):
    bb = ax.get_position()
    pad = 0.008
    fig.patches.append(FancyBboxPatch((bb.x0 - pad, bb.y0 - pad * 1.6), bb.width + 2 * pad, bb.height + pad * 4.2,
                                      boxstyle="round,pad=0,rounding_size=0.008", transform=fig.transFigure,
                                      fc=PANEL, ec=BORDER, lw=1, zorder=-10))

def kpi(fig, rect, label, value):
    x, y, w, h = rect
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, fc=PANEL, ec=BORDER, lw=1))
    fig.patches.append(FancyBboxPatch((x, y + h - 0.006), w, 0.006, boxstyle="square,pad=0",
                                      transform=fig.transFigure, fc=GREEN, ec="none"))
    fig.text(x + 0.012, y + h * 0.62, value, fontsize=24, weight="bold", color=TXT, va="center")
    fig.text(x + 0.012, y + h * 0.24, label, fontsize=10, color=SUB, va="center")

def kpi_row(fig, items, y=0.77, h=0.11):
    n, gap, left, right = len(items), 0.012, 0.02, 0.98
    w = (right - left - gap * (n - 1)) / n
    for i, (lab, val) in enumerate(items):
        kpi(fig, (left + i * (w + gap), y, w, h), lab, val)

def vbar(ax, labels, values, labeler, highlight=None, ylim_pad=1.18):
    cols = [GREEN if (highlight is None or l in highlight) else GREY for l in labels]
    bars = ax.bar(labels, values, color=cols, width=0.62, zorder=3)
    ax.set_ylim(0, max(values) * ylim_pad)
    ax.set_yticks([])
    ax.grid(False)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(values) * 0.025, labeler(v),
                ha="center", va="bottom", fontsize=9, color=TXT)
    ax.tick_params(axis="x", labelsize=9)

def hbar(ax, labels, values, labeler, wrap=28):
    labels = [textwrap.shorten(l, wrap, placeholder="…") for l in labels][::-1]
    values = list(values)[::-1]
    bars = ax.barh(labels, values, color=GREEN, height=0.62, zorder=3)
    ax.set_xlim(0, max(values) * 1.22)
    ax.set_xticks([])
    for b, v in zip(bars, values):
        ax.text(b.get_width() + max(values) * 0.015, b.get_y() + b.get_height() / 2, labeler(v),
                va="center", fontsize=9, color=TXT)
    ax.tick_params(axis="y", labelsize=9)

def donut(ax, labels, values):
    wedges, _ = ax.pie(values, colors=[GREEN, GREY], startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.32, edgecolor=PANEL, linewidth=2))
    tot = sum(values)
    for w_, lab, v in zip(wedges, labels, values):
        ang = np.deg2rad((w_.theta2 + w_.theta1) / 2)
        ax.text(1.32 * np.cos(ang), 1.32 * np.sin(ang), f"{lab}\n{v/tot:.1%}", ha="center", va="center",
                fontsize=9, color=TXT)
    ax.set_aspect("equal")
    ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.6, 1.6)

def table(ax, data, col_labels, col_widths, fontsize=8.8):
    ax.axis("off")
    t = ax.table(cellText=data, colLabels=col_labels, colWidths=col_widths, loc="upper left",
                 cellLoc="left", bbox=[0, 0, 1, 1])
    t.auto_set_font_size(False); t.set_fontsize(fontsize)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(BORDER); cell.set_linewidth(0.6)
        if r == 0:
            cell.set_facecolor("#242424"); cell.get_text().set_color(GREEN); cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor(PANEL if r % 2 else "#202020"); cell.get_text().set_color(TXT)
    return t

def save(fig, name):
    fig.savefig(os.path.join(outdir, name), dpi=DPI, facecolor=BG)
    plt.close(fig)
    print("saved", name)

N, TOT, HITS = len(df), df.streams.sum(), int(df["Is Billion Club"].sum())

# ===================== PAGE 1: OVERVIEW =====================
fig = page("Spotify Music Trends & Performance – 2023", "Music Executive Overview  ·  948 most-streamed tracks", "Overview")
kpi_row(fig, [("Total Tracks", f"{N:,}"), ("Total Streams", fmt(TOT)), ("Avg Streams / Track", fmt(df.streams.mean())),
              ("Billion Club Tracks", f"{HITS}"), ("Billion Club Rate", f"{HITS/N:.1%}"),
              ("Total Artists", f"{df['Primary Artist'].nunique()}")])
gs = GridSpec(2, 3, left=0.02, right=0.98, top=0.74, bottom=0.045, hspace=0.12, wspace=0.06,
              width_ratios=[1.15, 1.15, 0.8])
ax = make(fig, gs[0, 0], "Total Streams by Release Era")
s = df.groupby("Release Era").streams.sum().reindex(ERA_ORDER)
vbar(ax, s.index, s.values, fmt)
ax = make(fig, gs[0, 1], "Tracks by Release Month")
s = df.groupby("Month").size().reindex(MONTHS)
vbar(ax, s.index, s.values, lambda v: f"{v:.0f}", highlight={"Jan", "May"})
ax = make(fig, gs[0, 2], "Streams by Artist Type"); donut(ax, ["Solo", "Collab"], df.groupby("Artist Type").streams.sum().reindex(["Solo", "Collaboration"]).values)
ax = make(fig, gs[1, 0], "Top 10 Primary Artists by Streams", lp=0.075)
s = df.groupby("Primary Artist").streams.sum().nlargest(10)
hbar(ax, s.index, s.values, fmt)
ax = make(fig, gs[1, 1], "Top 10 Tracks by Streams", lp=0.115)
s = df.nlargest(10, "streams")
hbar(ax, s.track_name, s.streams.values, fmt, wrap=30)
ax = make(fig, gs[1, 2], "Tracks by Mode"); donut(ax, ["Major", "Minor"], df.groupby("mode").size().reindex(["Major", "Minor"]).values)
save(fig, "spotifyOverview.png")

# ===================== PAGE 2: HIT DRIVERS =====================
fig = page("Hit Drivers Deep Dive", "What separates Billion Club tracks (1B+ streams) from the rest?", "Hit Drivers")
gs = GridSpec(2, 2, left=0.02, right=0.98, top=0.89, bottom=0.045, hspace=0.1, wspace=0.05, width_ratios=[1.05, 1])

# Key drivers: likelihood of 1B+ in segment vs outside it
segs = [("Playlist Reach", "10K+"), ("Playlist Reach", "5K-10K"), ("Release Era", "2000-2009"),
        ("Release Era", "2010-2019"), ("Release Era", "Before 2000"), ("Month", "Sep"), ("Month", "Jan"),
        ("Artist Type", "Solo"), ("mode", "Major")]
rows = []
for col, val in segs:
    m = df[col].astype(str) == val
    rin, rout = df.loc[m, "Is Billion Club"].mean(), df.loc[~m, "Is Billion Club"].mean()
    nice = {"mode": "Mode", "Month": "Release month"}.get(col, col)
    rows.append((f"{nice} is {val}", rin, rin / rout if rout else np.nan))
rows.sort(key=lambda r: r[2], reverse=True)
ax = make(fig, gs[0, 0], "Key Drivers – how much more likely a track is to reach 1B+ streams", lp=0.135)
labs = [r[0] for r in rows][::-1]; lifts = [r[2] for r in rows][::-1]
bars = ax.barh(labs, lifts, color=GREEN, height=0.6, zorder=3)
ax.axvline(1, color=MUTED, lw=1, ls="--", zorder=2)
ax.set_xlim(0, max(lifts) * 1.3); ax.set_xticks([])
for b, r in zip(bars, rows[::-1]):
    ax.text(b.get_width() + max(lifts) * 0.015, b.get_y() + b.get_height() / 2,
            f"{r[2]:.1f}x  ({r[1]:.0%} hit rate)", va="center", fontsize=9, color=TXT)
ax.tick_params(axis="y", labelsize=9)

# Decomposition-style heat table: Billion Club tracks by era x playlist reach
ax = make(fig, gs[0, 1], "Billion Club Tracks – Release Era × Playlist Reach", lp=0.07, tp=0.095)
pv = df[df["Is Billion Club"]].pivot_table(index="Release Era", columns="Playlist Reach", values="track_id",
                                             aggfunc="count", observed=False).reindex(ERA_ORDER).fillna(0)
pv = pv[["<1K", "1K-5K", "5K-10K", "10K+"]]
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("g", [PANEL, "#0F5C2B", GREEN])
ax.imshow(pv.values, cmap=cmap, aspect="auto")
ax.set_xticks(range(4), pv.columns); ax.set_yticks(range(len(ERA_ORDER)), ERA_ORDER)
ax.xaxis.tick_top(); ax.tick_params(axis="both", labelsize=9)
mx = pv.values.max()
for i in range(pv.shape[0]):
    for j in range(pv.shape[1]):
        v = int(pv.values[i, j])
        ax.text(j, i, str(v), ha="center", va="center", fontsize=10, weight="bold",
                color="#000000" if v > mx * 0.55 else TXT)
ax.set_xlabel("Spotify playlist reach", fontsize=9)

# Scatter
ax = make(fig, gs[1, 0], "Spotify Playlists vs Streams  (r = %.2f)" % df.in_spotify_playlists.corr(df.streams), lp=0.05, bp=0.065)
nb = df[~df["Is Billion Club"]]; bc = df[df["Is Billion Club"]]
ax.scatter(nb.in_spotify_playlists, nb.streams / B, s=14, color=GREY, alpha=0.75, edgecolor=PANEL, lw=0.4, label="Under 1B", zorder=3)
ax.scatter(bc.in_spotify_playlists, bc.streams / B, s=18, color=GREEN, alpha=0.9, edgecolor=PANEL, lw=0.4, label="Billion Club", zorder=4)
ax.axhline(1, color=MUTED, lw=0.8, ls="--", zorder=2)
ax.set_xlabel("Spotify playlists", fontsize=9); ax.set_ylabel("Streams (billions)", fontsize=9)
ax.grid(color=BORDER, lw=0.5, zorder=0)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}K"))
leg = ax.legend(loc="lower right", frameon=False, fontsize=9)
for t in leg.get_texts(): t.set_color(SUB)

# Insight callouts
ax = make(fig, gs[1, 1], "Insights"); ax.axis("off")
r10 = df[df["Playlist Reach"] == "10K+"]["Is Billion Club"].mean()
r1 = df[df["Playlist Reach"] == "<1K"]["Is Billion Club"].mean()
audio_max = df[["danceability_pct", "energy_pct", "valence_pct", "acousticness_pct", "bpm"]].corrwith(df.streams).abs().max()
callouts = [
    ("Distribution beats sound",
     f"Tracks in 10K+ Spotify playlists reach 1B streams {r10:.1%} of the time, versus {r1:.1%} for tracks in under 1K playlists. "
     f"Playlist count correlates with streams at r = {df.in_spotify_playlists.corr(df.streams):.2f}, while no audio feature exceeds |r| = {audio_max:.2f}."),
    ("Time in market compounds",
     f"Streams are cumulative: 2010-2019 releases average {fmt(df[df['Release Era']=='2010-2019'].streams.mean())} streams, "
     f"2023 releases only {fmt(df[df['Release Era']=='2023'].streams.mean())}. Only {int(df[df['Release Era']=='2023']['Is Billion Club'].sum())} "
     f"of {int((df['Release Era']=='2023').sum())} 2023 tracks is in the Billion Club so far."),
]
y = 0.93
for head, body in callouts:
    ax.add_patch(FancyBboxPatch((0.0, y - 0.40), 0.012, 0.40, boxstyle="square,pad=0", transform=ax.transAxes, fc=GREEN, ec="none"))
    ax.text(0.04, y - 0.02, head, transform=ax.transAxes, fontsize=12, weight="bold", color=TXT, va="top")
    ax.text(0.04, y - 0.12, textwrap.fill(body, 78), transform=ax.transAxes, fontsize=10, color=SUB, va="top", linespacing=1.45)
    y -= 0.5
save(fig, "spotifyDeepDive.png")

# ===================== PAGE 3: PERFORMANCE LEVERS =====================
fig = page("Performance Levers", "Factors a label can influence  ·  plus the 2023 Breakout Watchlist", "Performance Levers")
gs = GridSpec(2, 4, left=0.02, right=0.98, top=0.89, bottom=0.045, hspace=0.12, wspace=0.08,
              height_ratios=[1, 1.15])
pct = lambda v: f"{v:.1%}"
ax = make(fig, gs[0, 0], "Billion Club Rate by Playlist Reach")
s = df.groupby("Playlist Reach", observed=True)["Is Billion Club"].mean()
vbar(ax, [str(i) for i in s.index], s.values, pct, highlight={"10K+"})
ax = make(fig, gs[0, 1], "Avg Streams per Track by Release Month", lp=0.035)
s = df.groupby("Month").streams.mean().reindex(MONTHS) / 1e6
ax.plot(range(12), s.values, color=GREEN, lw=2, marker="o", ms=5, zorder=3)
ax.set_xticks(range(12), [m[0] for m in MONTHS], fontsize=9)
ax.set_ylim(0, s.max() * 1.25); ax.grid(axis="y", color=BORDER, lw=0.5)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}M"))
for i, dy, va in ((int(np.argmax(s.values)), 9, "bottom"), (int(np.argmin(s.values)), -10, "top")):
    ax.annotate(f"{MONTHS[i]} {s.values[i]:.0f}M", (i, s.values[i]), textcoords="offset points", xytext=(0, dy),
                ha="center", va=va, fontsize=8.5, color=TXT)
ax = make(fig, gs[0, 2], "Billion Club Rate by Mood")
order = ["Happy & Energetic", "Happy & Calm", "Sad & Energetic", "Sad & Calm"]
s = df.groupby("Mood")["Is Billion Club"].mean().reindex(order)
vbar(ax, [o.replace(" & ", "\n& ") for o in order], s.values, pct)
ax.tick_params(axis="x", labelsize=8.5)
ax = make(fig, gs[0, 3], "Billion Club Rate by Tempo")
s = df.groupby("Tempo Band", observed=True)["Is Billion Club"].mean()
vbar(ax, [str(i).replace(" (", "\n(") for i in s.index], s.values, pct)
ax.tick_params(axis="x", labelsize=8.5)

watch = df[(df.released_year == 2023) & (~df["Is Billion Club"]) & (df.in_spotify_charts >= 20)] \
    .sort_values("in_spotify_charts", ascending=False)
ax = make(fig, gs[1, :3], f"Breakout Watchlist – 2023 releases, 20+ Spotify chart appearances, under 1B streams (top 12 of {len(watch)})")
rows = [[textwrap.shorten(r.track_name, 34, placeholder="…"), textwrap.shorten(r.artist_name, 26, placeholder="…"),
         r.release_date, fmt(r.streams), f"{r.in_spotify_charts}", f"{r.in_spotify_playlists:,}",
         f"{r.in_apple_playlists}", f"{r.in_shazam_charts:,}", f"{r.danceability_pct}"] for r in watch.head(12).itertuples()]
table(ax, rows, ["Track", "Artist", "Released", "Streams", "Sp. Charts", "Sp. Playlists", "Apple Pl.", "Shazam", "Dance %"],
      [0.22, 0.17, 0.10, 0.08, 0.08, 0.10, 0.08, 0.08, 0.07])
ax = make(fig, gs[1, 3], "Breakout Watchlist"); ax.axis("off")
ax.text(0.04, 0.84, f"{len(watch)}", transform=ax.transAxes, fontsize=46, weight="bold", color=GREEN, va="top")
ax.text(0.04, 0.50, "2023 tracks already charting\nstrongly but still under 1B", transform=ax.transAxes, fontsize=10.5, color=TXT, va="top", linespacing=1.4)
r1, r2 = (df[df["Playlist Reach"] == k]["Is Billion Club"].mean() for k in ("1K-5K", "5K-10K"))
ax.text(0.04, 0.26, textwrap.fill(f"Lever: moving a track from 1K-5K to 5K-10K playlists is linked to a jump in hit rate from {r1:.1%} to {r2:.1%}.", 36),
        transform=ax.transAxes, fontsize=9.5, color=SUB, va="top", linespacing=1.4)
save(fig, "spotifyLevers.png")

# ===================== PAGE 4: TRACK DETAILS =====================
artist = df.groupby("Primary Artist").streams.sum().idxmax()
sub = df[df["Primary Artist"] == artist].sort_values("streams", ascending=False)
fig = page("Track Details", f"Drill-through  ·  Primary Artist = {artist}  ·  {len(sub)} tracks  ·  {fmt(sub.streams.sum())} streams", "Overview")
ax = make(fig, GridSpec(1, 1, left=0.02, right=0.98, top=0.88, bottom=0.05)[0, 0], f"Underlying track records (top {min(22, len(sub))} of {len(sub)} by streams)")
tier = lambda v: "1B+ (Billion Club)" if v >= 1e9 else "500M-1B" if v >= 5e8 else "250M-500M" if v >= 2.5e8 else "Under 250M"
rows = [[textwrap.shorten(r.track_name, 34, placeholder="…"), textwrap.shorten(r.artist_name, 30, placeholder="…"),
         r.release_date, fmt(r.streams), tier(r.streams), f"{r.in_spotify_playlists:,}", f"{r.in_spotify_charts}",
         f"{r.bpm}", r.key, r.mode, f"{r.danceability_pct}", f"{r.energy_pct}", f"{r.valence_pct}"]
        for r in sub.head(22).itertuples()]
table(ax, rows, ["Track", "Artist(s)", "Released", "Streams", "Stream Tier", "Sp. Playlists", "Sp. Charts", "BPM", "Key", "Mode", "Dance", "Energy", "Valence"],
      [0.17, 0.15, 0.08, 0.07, 0.11, 0.08, 0.07, 0.05, 0.05, 0.06, 0.05, 0.06, 0.06], fontsize=8.6)
save(fig, "spotifyDetails.png")
