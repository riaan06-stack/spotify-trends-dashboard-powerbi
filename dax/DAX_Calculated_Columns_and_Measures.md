# DAX – Calculated Columns & Measures

Table name used everywhere below: **`Spotify_Tracks`** (the sheet in `data/Spotify_Tracks_2023_Clean.xlsx`).

How to add them in Power BI Desktop:
- **Calculated column:** Data view → select `Spotify_Tracks` → *Table tools* → **New column** → paste one formula.
- **Measure:** Report view → right-click `Spotify_Tracks` in the Data pane → **New measure** → paste one formula.
  Tip: create a blank table called `_Measures` (Home → Enter data → Load) and keep all measures there.

---

## 1. Calculated Columns

```DAX
Release Era =
SWITCH (
    TRUE (),
    Spotify_Tracks[released_year] < 2000, "Before 2000",
    Spotify_Tracks[released_year] < 2010, "2000-2009",
    Spotify_Tracks[released_year] < 2020, "2010-2019",
    Spotify_Tracks[released_year] < 2022, "2020-2021",
    Spotify_Tracks[released_year] = 2022, "2022",
    "2023"
)
```

```DAX
Era Sort =
SWITCH ( Spotify_Tracks[Release Era],
    "Before 2000", 1, "2000-2009", 2, "2010-2019", 3,
    "2020-2021", 4, "2022", 5, "2023", 6 )
```
*(Select `Release Era` → Column tools → **Sort by column** → `Era Sort`.)*

```DAX
Stream Tier =
SWITCH (
    TRUE (),
    Spotify_Tracks[streams] >= 1000000000, "1B+ (Billion Club)",
    Spotify_Tracks[streams] >= 500000000,  "500M-1B",
    Spotify_Tracks[streams] >= 250000000,  "250M-500M",
    "Under 250M"
)
```

```DAX
Is Billion Club = IF ( Spotify_Tracks[streams] >= 1000000000, "Yes", "No" )
```

```DAX
Artist Type = IF ( Spotify_Tracks[artist_count] = 1, "Solo", "Collaboration" )
```

```DAX
Primary Artist =
VAR pos = SEARCH ( ",", Spotify_Tracks[artist_name], 1, 0 )
RETURN IF ( pos = 0, Spotify_Tracks[artist_name], TRIM ( LEFT ( Spotify_Tracks[artist_name], pos - 1 ) ) )
```

```DAX
Danceability Band =
SWITCH ( TRUE (),
    Spotify_Tracks[danceability_pct] >= 70, "High (70+)",
    Spotify_Tracks[danceability_pct] >= 50, "Medium (50-69)",
    "Low (<50)" )
```

```DAX
Energy Band =
SWITCH ( TRUE (),
    Spotify_Tracks[energy_pct] >= 70, "High (70+)",
    Spotify_Tracks[energy_pct] >= 50, "Medium (50-69)",
    "Low (<50)" )
```

```DAX
Mood =
SWITCH ( TRUE (),
    Spotify_Tracks[valence_pct] >= 50 && Spotify_Tracks[energy_pct] >= 50, "Happy & Energetic",
    Spotify_Tracks[valence_pct] >= 50, "Happy & Calm",
    Spotify_Tracks[energy_pct] >= 50,  "Sad & Energetic",
    "Sad & Calm" )
```

```DAX
Tempo Band =
SWITCH ( TRUE (),
    Spotify_Tracks[bpm] >= 150, "Fast (150+)",
    Spotify_Tracks[bpm] >= 120, "Upbeat (120-149)",
    Spotify_Tracks[bpm] >= 90,  "Mid (90-119)",
    "Slow (<90)" )
```

```DAX
Playlist Reach =
SWITCH ( TRUE (),
    Spotify_Tracks[in_spotify_playlists] >= 10000, "10K+",
    Spotify_Tracks[in_spotify_playlists] >= 5000,  "5K-10K",
    Spotify_Tracks[in_spotify_playlists] >= 1000,  "1K-5K",
    "<1K" )
```

```DAX
Month Name = FORMAT ( DATE ( 2000, Spotify_Tracks[released_month], 1 ), "MMM" )
```
*(Sort `Month Name` by `released_month`.)*

---

## 2. Measures

```DAX
Total Tracks = COUNTROWS ( Spotify_Tracks )

Total Streams = SUM ( Spotify_Tracks[streams] )

Avg Streams per Track = AVERAGE ( Spotify_Tracks[streams] )

Median Streams = MEDIAN ( Spotify_Tracks[streams] )

Billion Club Tracks =
CALCULATE ( [Total Tracks], Spotify_Tracks[streams] >= 1000000000 )

Billion Club Rate = DIVIDE ( [Billion Club Tracks], [Total Tracks] )

Total Artists = DISTINCTCOUNT ( Spotify_Tracks[Primary Artist] )

Avg Danceability = AVERAGE ( Spotify_Tracks[danceability_pct] )
Avg Energy       = AVERAGE ( Spotify_Tracks[energy_pct] )
Avg Valence      = AVERAGE ( Spotify_Tracks[valence_pct] )
Avg BPM          = AVERAGE ( Spotify_Tracks[bpm] )

Total Spotify Playlists = SUM ( Spotify_Tracks[in_spotify_playlists] )

Streams per Playlist = DIVIDE ( [Total Streams], [Total Spotify Playlists] )

Breakout Watchlist Count =
CALCULATE (
    [Total Tracks],
    Spotify_Tracks[released_year] = 2023,
    Spotify_Tracks[in_spotify_charts] >= 20,
    Spotify_Tracks[streams] < 1000000000
)
```

**Formatting:** set `Total Streams` and `Avg Streams per Track` to *Display units = Billions / Millions*, and `Billion Club Rate` to *Percentage, 1 decimal*.
