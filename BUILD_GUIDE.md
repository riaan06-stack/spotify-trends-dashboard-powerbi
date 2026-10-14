# 🛠️ Build Guide – Spotify Trends Dashboard in Power BI Desktop

Follow these steps on Windows with **Power BI Desktop** (free from the Microsoft Store). Total time: about 2-3 hours.

---

## Step 1 – Load the data
1. Open Power BI Desktop → **Blank report**.
2. **Home → Get data → Excel workbook** → choose `data/Spotify_Tracks_2023_Clean.xlsx`.
3. Tick the sheet **Spotify_Tracks** → **Transform Data** (opens Power Query).
4. In Power Query check the column types:
   - `track_name`, `artist_name`, `key`, `mode` → **Text**
   - `release_date` → **Date**
   - every other column → **Whole Number**
5. **Close & Apply**.

## Step 2 – Apply the theme
**View → Themes → Browse for themes** → select `powerBI/spotify_theme.json`. The canvas turns Spotify dark (black + green).

## Step 3 – Add calculated columns and measures
Open `dax/DAX_Calculated_Columns_and_Measures.md` and add every **calculated column**, then every **measure**.
- Sort `Release Era` by `Era Sort` and `Month Name` by `released_month` (Column tools → Sort by column).
- Format: `Total Streams` → display units *Billions*; `Avg Streams per Track` → *Millions*; `Billion Club Rate` → *Percentage*.

Quick check – with no filters your cards should show: **948 tracks · 487.6B streams · 152 Billion Club · 16.0%**.

---

## Step 4 – Page 1: "Music Executive Overview"
Rename the page (double-click the tab).
1. **Title** text box: *Spotify Music Trends & Performance – 2023*.
2. **6 Card visuals** across the top: Total Tracks, Total Streams, Avg Streams per Track, Billion Club Tracks, Billion Club Rate, Total Artists.
3. **Clustered column chart** – X: `Release Era`, Y: `Total Streams`.
4. **Clustered column chart** – X: `Month Name`, Y: `Total Tracks`.
5. **Clustered bar chart** – Y: `Primary Artist`, X: `Total Streams` → Filters pane → `Primary Artist` → Filter type **Top N** → Top 10 by `Total Streams`.
6. **Clustered bar chart** – Y: `track_name`, X: `Total Streams` → Top N = 10.
7. **Donut chart** – Legend: `Artist Type`, Values: `Total Streams`.
8. **Donut chart** – Legend: `mode`, Values: `Total Tracks`.
9. **Slicers** (Dropdown style): `Release Era`, `Artist Type`, `mode`, `Stream Tier`, `key`.

## Step 5 – Page 2: "Hit Drivers Deep Dive"
1. **Key Influencers** visual:
   - *Analyze*: `Is Billion Club` → set "What influences Is Billion Club to be **Yes**".
   - *Explain by*: `Playlist Reach`, `in_spotify_playlists`, `in_apple_playlists`, `in_spotify_charts`, `Release Era`, `Artist Type`, `mode`, `Danceability Band`, `Energy Band`, `Mood`, `Tempo Band`.
2. **Decomposition Tree**:
   - *Analyze*: `Billion Club Tracks`.
   - *Explain by*: `Release Era`, `Playlist Reach`, `Artist Type`, `mode`. Click **+** to expand each level in that order.
3. **Scatter chart** – X: `in_spotify_playlists` (Don't summarize), Y: `streams` (Don't summarize), Legend: `Is Billion Club`, Values: `track_name`.
4. Two **text boxes** with insights, e.g.
   - *"Tracks in 10K+ playlists reach 1B streams 78.5% of the time vs 0.4% under 1K."*
   - *"Playlist count correlates with streams at r = 0.79; audio features ≤ 0.11."*

## Step 6 – Page 3: "Performance Levers"
1. **Column chart** – X: `Playlist Reach`, Y: `Billion Club Rate`.
2. **Line chart** – X: `Month Name`, Y: `Avg Streams per Track`.
3. **Column chart** – X: `Mood`, Y: `Billion Club Rate`.
4. **Column chart** – X: `Tempo Band`, Y: `Billion Club Rate`.
5. **Table – Breakout Watchlist**: columns `track_name`, `artist_name`, `release_date`, `streams`, `in_spotify_charts`, `in_spotify_playlists`, `in_apple_playlists`, `in_shazam_charts`, `danceability_pct`.
   Visual-level filters: `released_year` **is 2023**, `in_spotify_charts` **≥ 20**, `streams` **< 1000000000**. Sort by `in_spotify_charts` descending. → **74 rows**.
6. **Card**: `Breakout Watchlist Count` + a text box callout.

## Step 7 – Page 4: "Track Details" (drill-through)
1. Add a new page, rename it **Track Details**.
2. In the Visualizations pane → **Drill through** section → drag `Primary Artist` and `Release Era` into it.
3. Add a **Table**: `track_name`, `artist_name`, `release_date`, `streams`, `Stream Tier`, `in_spotify_playlists`, `in_spotify_charts`, `bpm`, `key`, `mode`, `danceability_pct`, `energy_pct`, `valence_pct`.
4. Power BI automatically adds a **Back** button; also add an *Overview* navigation button.
5. Right-click the page tab → **Hide page**.
6. Test: on the Overview page, right-click a bar in *Top 10 Artists* → **Drill through → Track Details**.

## Step 8 – Navigation buttons
On each visible page: **Insert → Buttons → Blank** → Format → *Action* ON → Type **Page navigation** → Destination = target page. Add text like "Hit Drivers →". (Ctrl + click to test in Desktop.)

## Step 9 – Save and screenshot
1. **File → Save as** → `powerBI/Spotify_Trends_Analytics.pbix`.
2. Take screenshots (Win + Shift + S) and save into `images/` with these exact names (the README already points to them):
   - `spotifyOverview.png`
   - `spotifyDeepDive.png`
   - `spotifyLevers.png`
   - `spotifyDrillThrough.png` (the right-click menu)
   - `spotifyDetails.png`

Then follow **GIT_STEPS.md** to upload everything to GitHub.
