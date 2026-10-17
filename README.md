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

- `will-ai-buy-our-cars/prophecy.py` – aktuelle Fassung (v3): EDEN-Prophezeiung (P-01 bis P-15), drei Annahmen
  mit GRANTED-Siegeln, Riss, Titel und Anfang von Kapitel 1 mit Genesis (G-01 bis G-06), 167 s
  - Standbild: `python3 prophecy.py still <sekunde> <out.png>`
  - Video: `python3 prophecy.py render <startframe> <endframe> <out.mp4>` (24 fps, 4013 Frames)
- `will-ai-buy-our-cars/opener.py` – Fassung v2: Cold Open (00-01 bis 00-09) und Flash-Forward
  mit EDEN (F-01 bis F-11) bis zur Titelkarte, 130 s. Stil: Anthrazit, knochenweisse Figuren mit Tuschekontur,
  Rasterpunkte, Papierstruktur, Filmkorn, Gold als Bedrohungsfarbe
  - Standbild: `python3 opener.py still <sekunde> <out.png>`
  - Video: `python3 opener.py render <startframe> <endframe> <out.mp4>` (24 fps, 3120 Frames)
- `will-ai-buy-our-cars/coldopen.py` – erste Testfassung (v1), nur Cold Open, 60 s
  - braucht `pip install skia-python numpy pillow` und ffmpeg
- `will-ai-buy-our-cars/fonts/` – Oswald, Cinzel, IM Fell English, Special Elite (Open-Font-Lizenzen)
- `will-ai-buy-our-cars/voice/` – Sprachaufnahmen, benannt nach Zeilennummer im Sprechskript (z. B. `00-03.mp3`)

Media (renders, images, music) is generally not stored here.
