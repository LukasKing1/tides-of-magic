# Video-Werkstatt (Repo-Name historisch: tides-of-magic)

Zwischenspeicher fuer alle Videoprojekte. Ein Ordner pro Video, Code und Stimmen liegen hier,
gerenderte Videos und lizenzierte Musik nur dort, wo .gitignore es erlaubt.

## The Tides of Magic (ASOIAF-Fantheorie)

- `main/ch1/` – chapter 1 (cold open): book, Mirri, pages, places, audio mix, render scripts
- `main/script_v2.py` – narration script (snippet IDs, voices, directions)
- `main/voice/gen_order.json` – order in which the voice snippets were generated in Epidemic (maps file timestamps to snippet IDs)
- `short1/` – Short 1
- `rig/` – the Starseer character rig

## Will AI Buy Our Cars? (KI und Jobverlust)

- `will-ai-buy-our-cars/coldopen.py` – Testanimation Cold Open (Szenen 00-01 bis 00-09), Stil: Anthrazit,
  knochenweisse Figuren mit Tuschekontur, Rasterpunkte, Filmkorn, Gold als Bedrohungsfarbe
  - Standbild: `python3 coldopen.py still <sekunde> <out.png>`
  - Video: `python3 coldopen.py render <startframe> <endframe> <out.mp4>` (24 fps, 1440 Frames)
  - braucht `pip install skia-python numpy pillow` und ffmpeg
- `will-ai-buy-our-cars/fonts/` – Oswald, Cinzel, IM Fell English (SIL Open Font License)
- `will-ai-buy-our-cars/voice/` – Sprachaufnahmen, benannt nach Zeilennummer im Sprechskript (z. B. `00-03.mp3`)

Media (renders, images, music) is generally not stored here.
