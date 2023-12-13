#!/bash/sh
python3 scripts/nytimesGet.py
python3 scripts/zeitGet.py
git add .
git commit -m "checkout"
git push origin main
