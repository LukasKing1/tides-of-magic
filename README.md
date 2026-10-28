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

- `will-ai-buy-our-cars/start.py` – Entwurf 1 des Videoanfangs (P-01 bis P-15, 2:20) mit echter Stimme, Musik und Sounds
  - Bild: `python3 start.py render <startframe> <endframe> <out.mp4>` (3354 Frames), Ton: `python3 start.py audio <out.wav>`
- `will-ai-buy-our-cars/voice/`, `music/`, `sfx/` – Aufnahmen nach Zeilennummer, Musik und Sounds nach Stelle (Listen: `zuordnung.csv`, `musik.csv`, `sfx.csv`)
- `will-ai-buy-our-cars/rich.py` – aktuelle Fassung (v4) im Niveau von Rational Animations: Prophezeiung P-01 bis P-11
  (Dach mit Silhouetten, EDEN, Vertrag, Fabrik/Kueche, Nachtbuero, goldene Stadt, Zeitungen, Menge, Autosalon,
  letzter Job, Kristallkugel mit Schlange) und Titel, 90 s
  - Standbild: `python3 rich.py still <sekunde> <out.png>`
  - Video: `python3 rich.py render <startframe> <endframe> <out.mp4>` (24 fps, 2160 Frames)
- `will-ai-buy-our-cars/rich_base.py` – Zeichenbasis v4: Cel-Schatten, Konturen in Bildschirmpixeln, Profilfiguren,
  Haende, Roboterhand und -arm, Silhouetten mit Randlicht, Schlange mit Bauchschuppen
- `will-ai-buy-our-cars/concept4.py` – Stilbilder zur Bildsprache "Kugel, Haut und Ring"
- `will-ai-buy-our-cars/prophecy.py` – Fassung v3 (wird von v4 als Bausteinsammlung importiert): EDEN-Prophezeiung (P-01 bis P-15), drei Annahmen
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
