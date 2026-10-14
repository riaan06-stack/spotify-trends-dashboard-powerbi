# 🚀 How to Add This Project to GitHub

Do this **after** you have built the `.pbix` file and saved the 5 screenshots into `images/` (see `BUILD_GUIDE.md`).

---

## Option A – Using Git (command line) ✅ recommended

### 1. Install Git (one time only)
Download from https://git-scm.com/download/win → install with default options.
Check it works – open **Command Prompt** or **Git Bash**:
```bash
git --version
```

### 2. Tell Git who you are (one time only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

### 3. Create an empty repository on GitHub
1. Go to https://github.com → **+** (top right) → **New repository**.
2. Repository name: `spotify-trends-dashboard-powerbi`
3. Description: *Power BI dashboard analysing Spotify's most-streamed songs of 2023*
4. Choose **Public**.
5. ⚠️ **Do NOT** tick "Add a README", ".gitignore" or "license" (the project already has them).
6. Click **Create repository** and keep the page open.

### 4. Open a terminal inside the project folder
In File Explorer open the `spotify-trends-dashboard-powerbi` folder → click the address bar → type `cmd` → Enter.
(Or right-click inside the folder → **Open Git Bash here**.)

### 5. Initialise, commit and push
```bash
git init
git add .
git commit -m "Add Spotify music trends Power BI dashboard"
git branch -M main
git remote add origin https://github.com/riaan06/spotify-trends-dashboard-powerbi.git
git push -u origin main
```

When asked to sign in, a browser window opens – log in to GitHub and approve.
(If it asks for a password in the terminal, use a **Personal Access Token**: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate, tick `repo`, and paste it as the password.)

### 6. Check it
Refresh the GitHub page – you should see `data/`, `dax/`, `images/`, `powerBI/`, `scripts/` and the README with screenshots showing.

### 7. Making changes later
```bash
git add .
git commit -m "Update dashboard screenshots"
git push
```

---

## Option B – Upload through the GitHub website (no Git needed)

1. Create the repository as in step 3 above, **but tick "Add a README file"**.
2. Click **Add file → Upload files**.
3. Drag the **contents** of the `spotify-trends-dashboard-powerbi` folder (all folders + files) into the page – folder structure is kept.
4. Commit message: *Add Spotify music trends Power BI dashboard* → **Commit changes**.
5. When it asks about `README.md`, let the upload replace the default one.

---

## Finishing touches on GitHub
- On the repo page click the ⚙️ next to **About** → add a description and topics: `powerbi`, `dax`, `data-analytics`, `spotify`, `dashboard`, `music-analytics`.
- Fill in your **Name** and **Roll No** at the top of `README.md` (edit with the ✏️ pencil icon on GitHub, or locally and push again).

## Troubleshooting
| Problem | Fix |
| --- | --- |
| `remote origin already exists` | `git remote set-url origin https://github.com/riaan06/spotify-trends-dashboard-powerbi.git` |
| `failed to push… fetch first` (you created the repo with a README) | `git pull origin main --allow-unrelated-histories` then `git push -u origin main` |
| Images not showing in README | Check file names in `images/` match exactly (case-sensitive): `spotifyOverview.png` etc. |
| `.pbix` over 100 MB | Very unlikely with this dataset; if it happens, use Git LFS: `git lfs install` → `git lfs track "*.pbix"` → commit `.gitattributes` |
