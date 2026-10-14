# Usage: python clean_data.py data/raw_spotify_2023.csv data/Spotify_Tracks_2023_Clean.csv data/Spotify_Tracks_2023_Clean.xlsx
# Requires: pip install pandas openpyxl
import sys, re, pandas as pd, numpy as np
src, out_csv, out_xlsx = sys.argv[1:4]
df=pd.read_csv(src,encoding='latin-1')
n0=len(df)
df['streams']=pd.to_numeric(df['streams'],errors='coerce')
bad=df.streams.isna().sum(); df=df.dropna(subset=['streams'])
for c in ['in_deezer_playlists','in_shazam_charts']:
    df[c]=pd.to_numeric(df[c].astype(str).str.replace(',',''),errors='coerce')
df['in_shazam_charts']=df['in_shazam_charts'].fillna(0)
df['key']=df['key'].fillna('Unknown')

# --- repair broken characters (the Kaggle source lost accented letters as "ï¿½") ---
G='ï¿½'
ARTIST_FIX={
    'ROSAL'+G:'ROSALÍA', 'Ti'+G*2+'sto':'Tiësto', 'M'+G*2+'ne':'Måneskin', 'R'+G*2+'ma':'Rema',
    'Mar'+G*2+'lia Mendon'+G*2+'a':'Marília Mendonça', 'Mar'+G*2+'lia Mendo':'Marília Mendonça',
    'Jos'+G*2+' Felic':'José Feliciano', 'Lenny Tav'+G*2+'rez':'Lenny Tavárez', 'Eden Mu'+G+'ï':'Eden Muñoz',
    'Cruz Cafun'+G*2:'Cruz Cafuné', 'Xam'+G*2:'Xamã', 'Matu'+G*2:'Matuê', 'Lu'+G*2+'sa Sonza':'Luísa Sonza',
    'Z'+G*2+' Fe':'Zé Felipe', 'Z'+G*2+' Neto & Crist':'Zé Neto & Cristiano', 'Sch'+G*2+'rze':'Schürze',
    'Esc'+G*2+'cia':'Escócia', 'Jasiel Nu'+G*2+'ez':'Jasiel Núñez', 'Do'+G*2+'u':'Doğu',
    'Bomba Est'+G*2+'reo':'Bomba Estéreo', 'Beyoncï¿':'Beyoncé', 'Michael Bublï¿':'Michael Bublé',
    'Elley Duhï¿':'Elley Duhé', 'Matuï¿':'Matuê', 'The Mar'+G+'ï':'The Marías', 'Ti'+G+'ï¿':'Tiësto',
}
def repair(s, fixes=None):
    for bad_txt, good in (fixes or {}).items():
        s = s.replace(bad_txt, good)
    s = s.replace(G*3, "'")                                       # curly apostrophe (3 bytes)
    s = re.sub(r'(?:ï¿½)+(?:ï¿?)?|ï¿?$|ï$', '?', s)                # anything else unrecoverable
    return s
fixed_names = int(df['track_name'].str.contains('ï').sum() + df['artist(s)_name'].str.contains('ï').sum())
df['artist(s)_name'] = df['artist(s)_name'].map(lambda s: repair(s, ARTIST_FIX))
df['track_name'] = df['track_name'].map(repair)
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
print(n0,bad,dup,len(df),"names repaired:",fixed_names)
