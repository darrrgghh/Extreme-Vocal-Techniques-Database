from flask import Flask, render_template, jsonify
import pandas as pd
import os
import re

app = Flask(__name__)
DATA_FILE = "1excerpts_database.tsv"

def count_syllables(rhythmic_representation):
    if rhythmic_representation == "N/A":
        return 0
    tokens = rhythmic_representation.strip().split()
    count = 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        # Считаем как один слог, если это группа в квадратных скобках
        if token.startswith('['):
            # ищем конец группы
            while not tokens[i].endswith(']') and i < len(tokens) - 1:
                i += 1
            count += 1
        # Считаем, если token оканчивается на q
        elif token.endswith('q'):
            count += 1
        # Считаем, если обычный слог (не пауза)
        elif not token.endswith('r') and not token.endswith('r.'):
            count += 1
        i += 1
    return count


if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, sep="\t", encoding="cp1252")
    df = df.fillna("N/A")
    df.replace("", "N/A", inplace=True)
else:
    df = pd.DataFrame()

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Syllable_Count"] = df["Rhythmic_representation"].apply(count_syllables)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extreme-vocal-techniques-popularity")
def vocal_techniques_popularity():
    examples = df.to_dict(orient="records")
    return render_template("extreme-vocal-techniques-popularity.html", excerpts=examples)

@app.route("/extreme-vocal-techniques")
def vocal_techniques():
    return render_template("extreme-vocal-techniques.html")

@app.route("/extreme-vocal-only-stimuli")
def vocal_stimuli():
    return render_template("extreme-vocal-only-stimuli.html")

@app.route("/analytics")
def analytics():
    columns = [
        "Artist", "Technique", "Album", "Year",
        "Album_Popularity", "Track_Popularity",
        "Stream_Count", "Syllable_Count"
    ]
    numeric_columns = [
        "Album_Popularity", "Track_Popularity", "Stream_Count",
        "Syllable_Count", "Year"
    ]
    categorical_columns = ["Technique", "Artist"]

    data = df.to_dict(orient="records")

    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())

    return render_template(
        "analytics.html",
        columns=columns,
        data=data,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        year_range=[year_min, year_max]
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/data.json")
def data_json():
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
