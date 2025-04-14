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
        if token.startswith('['):
            while not tokens[i].endswith(']') and i < len(tokens) - 1:
                i += 1
            count += 1
        elif token.endswith('q'):
            count += 1
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

DATABASES = {
    "emvt": {
        "file": "1excerpts_database.tsv",
        "columns": [
            "Artist", "Album", "Year", "Example_type",
            "Album_Popularity", "Track_Popularity",
            "Stream_Count", "Syllable_Count", "Tempo_(approx.)", "Excerpt_duration_ms"
        ],
        "numeric_columns": [
            "Album_Popularity", "Track_Popularity", "Stream_Count",
            "Syllable_Count", "Year", "Tempo_(approx.)", "Excerpt_duration_ms"
        ],
        "categorical_columns": ["Artist"]
    }
    # в будущем сюда можно добавить другие базы
}

@app.route("/analytics")
def analytics():
    db_info = DATABASES["emvt"]
    data = df.to_dict(orient="records")

    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())

    return render_template(
        "analytics.html",
        columns=db_info["columns"],
        data=data,
        numeric_columns=db_info["numeric_columns"],
        categorical_columns=db_info["categorical_columns"],
        year_range=[year_min, year_max]
    )

@app.route("/spectral-centroid-analysis")
def spectral_centroid():
    df_local = pd.read_csv(DATA_FILE, sep="\t", encoding="cp1252")
    df_local = df_local[df_local["Technique"].isin(["Growling", "Screaming", "Clean"])]
    df_local = df_local.dropna(subset=["Spectral_Centroid"])

    group_stats = df_local.groupby('Technique')["Spectral_Centroid"].agg(['mean', 'std', 'count', 'min', 'max'])

    from scipy.stats import f_oneway, ttest_ind
    from statsmodels.stats.multicomp import pairwise_tukeyhsd

    growling = df_local[df_local["Technique"] == "Growling"]["Spectral_Centroid"]
    screaming = df_local[df_local["Technique"] == "Screaming"]["Spectral_Centroid"]
    clean = df_local[df_local["Technique"] == "Clean"]["Spectral_Centroid"]

    f_stat, p_value_anova = f_oneway(growling, screaming, clean)
    t_stat, p_value_ttest = ttest_ind(growling, screaming)

    tukey_result = pairwise_tukeyhsd(df_local["Spectral_Centroid"], df_local["Technique"])
    tukey_df = pd.DataFrame(data=tukey_result.summary().data[1:], columns=tukey_result.summary().data[0])

    return render_template(
        "spectral-centroid-analysis.html",
        stats=group_stats.to_dict(),
        anova={"f": round(f_stat, 3), "p": round(p_value_anova, 3)},
        ttest={"t": round(t_stat, 3), "p": round(p_value_ttest, 3)},
        tukey=tukey_df.to_dict(orient="records")
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/data.json")
def data_json():
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
