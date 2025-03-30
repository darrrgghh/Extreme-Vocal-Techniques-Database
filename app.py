from flask import Flask, render_template, jsonify
import pandas as pd
import os
import re

app = Flask(__name__)

DATA_FILE = "1excerpts_database.tsv"

# Функции сбора данных (оставляем как есть)
def get_stream_count(artist, song_title):
    filename = f"static/unpopularity_exports/{artist}.txt"
    if not os.path.exists(filename):
        return "N/A"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "N/A"

    for line in lines:
        if line.strip().lower().startswith("track:") and song_title.lower() in line.lower():
            match = re.search(r"Stream Count:\s*([\d,]+)", line)
            if match:
                return int(match.group(1).replace(",", ""))
    return "N/A"

def get_album_popularity(artist, album_title):
    filename = f"static/unpopularity_exports/{artist}.txt"
    if not os.path.exists(filename):
        return "N/A"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "N/A"

    for line in lines:
        if line.strip().lower().startswith("album:") and album_title.lower() in line.lower():
            match = re.search(r"Popularity:\s*(\d+)", line)
            if match:
                return int(match.group(1))
    return "N/A"

def get_top_track_stream_count(artist):
    filename = f"static/unpopularity_exports/{artist}.txt"
    if not os.path.exists(filename):
        return "N/A"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "N/A"
    for line in lines:
        if line.strip().startswith("Stream Count:"):
            match = re.search(r"Stream Count:\s*([\d,]+)", line)
            if match:
                return int(match.group(1).replace(",", ""))
    return "N/A"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, sep="\t", encoding="cp1252")
    df = df.fillna("N/A")
    df.replace("", "N/A", inplace=True)
else:
    df = pd.DataFrame()

df["Stream_Count"] = df.apply(lambda row: get_stream_count(row["Artist"], row["Song"]), axis=1)
df["Album_Popularity"] = df.apply(lambda row: get_album_popularity(row["Artist"], row["Album"]), axis=1)
df["Top_Track_Stream_Count"] = df.apply(lambda row: get_top_track_stream_count(row["Artist"]), axis=1)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extreme-vocal-techniques-popularity")
def vocal_techniques_popularity():
    examples = df.to_dict(orient="records")
    return render_template("extreme-vocal-techniques-popularity.html", excerpts=examples)

@app.route("/extreme-vocal-techniques")
def vocal_techniques():
    return render_template("extreme-vocal-techniques.html")  # пока пустая

@app.route("/extreme-vocal-only-stimuli")
def vocal_stimuli():
    return render_template("extreme-vocal-only-stimuli.html")  # пока пустая

@app.route("/analytics")
def analytics():
    columns = [
        "Technique", "Artist", "Album", "Year",
        "Album_Popularity", "Track_Popularity",
        "Stream_Count", "Top_Track_Stream_Count"
    ]
    numeric_columns = [
        "Year", "Album_Popularity", "Track_Popularity",
        "Stream_Count", "Top_Track_Stream_Count"
    ]
    categorical_columns = [
        "Technique", "Artist", "Album"
    ]
    examples = df.to_dict(orient="records")
    return render_template(
        "analytics.html",
        columns=columns,
        data=examples,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/data.json")
def data_json():
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
