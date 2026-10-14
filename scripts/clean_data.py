# Usage: python clean_data.py data/raw_spotify_2023.csv data/Spotify_Tracks_2023_Clean.csv data/Spotify_Tracks_2023_Clean.xlsx
# Requires: pip install pandas openpyxl
import sys, pandas as pd, numpy as np
src, out_csv, out_xlsx = sys.argv[1:4]
df=pd.read_csv(src,encoding='latin-1')
n0=len(df)
df['streams']=pd.to_numeric(df['streams'],errors='coerce')
bad=df.streams.isna().sum(); df=df.dropna(subset=['streams'])
for c in ['in_deezer_playlists','in_shazam_charts']:
    df[c]=pd.to_numeric(df[c].astype(str).str.replace(',',''),errors='coerce')
df['in_shazam_charts']=df['in_shazam_charts'].fillna(0)
df['key']=df['key'].fillna('Unknown')
df=df.sort_values('streams',ascending=False)
dup=df.duplicated(['track_name','artist(s)_name']).sum()
df=df.drop_duplicates(['track_name','artist(s)_name'])
df=df.rename(columns={'artist(s)_name':'artist_name'})
df.columns=[c.replace('_%','_pct') for c in df.columns]
df['streams']=df.streams.astype('int64')
for c in ['in_deezer_playlists','in_shazam_charts']: df[c]=df[c].astype('int64')
df['release_date']=pd.to_datetime(dict(year=df.released_year,month=df.released_month,day=df.released_day)).dt.date
df.insert(0,'track_id',range(1,len(df)+1))
df.to_csv(out_csv,index=False,encoding='utf-8')
df.to_excel(out_xlsx,index=False,sheet_name='Spotify_Tracks')
print(n0,bad,dup,len(df))
