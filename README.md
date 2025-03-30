# The Database of Extreme Metal Vocal Techniques — Web Version

This repository contains the source code and database files for the web version of **The Database of Extreme Metal Vocal Techniques**:  
🔗 https://extreme-vocal-techniques-db.onrender.com/

The web app allows users to browse, filter, and explore examples of extreme vocal techniques in metal music. It is designed as an interactive and constantly evolving resource for researchers, musicians, and metal enthusiasts.

## Database

The database includes curated excerpts of metal songs featuring three main extreme vocal techniques:
- **Growling**
- **Screaming**
- **Clean vocals**

Each excerpt is accompanied by detailed metadata, including artist, album, year, lyrics excerpt, rhythmic and melodic representations, and Spotify popularity metrics.

### Current and Future Updates

The current database focuses primarily on **least popular** releases of selected artists, based on Spotify popularity metrics. The database will soon be expanded to include the most popular Spotify releases by the same artists.
The database is regularly updated and expanded beyond the static version available in the research repository.

## Project Structure

- `app.py` — Flask app source code
- `index.html` — Main web interface template
- `1excerpts_database.tsv` — Current version of the database
- `/static` — Static assets (audio files, images, CSS, etc.)
- `/unpopularity_exports` — Exported data from the Spotify {UN}Popularity Analyzer