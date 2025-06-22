from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)
DATA_FILE = "1excerpts_database.tsv"
METALVOX_FILE = "1metal_vox.tsv"
TRIPLE_TWELVE_FILE = "1triple_twelve_stimuli_set.tsv"

# Загрузка Triple Twelve
if os.path.exists(TRIPLE_TWELVE_FILE):
    triple_df = pd.read_csv(TRIPLE_TWELVE_FILE, sep="\t")
    triple_df = triple_df.fillna("N/A")
    triple_df.replace("", "N/A", inplace=True)
else:
    triple_df = pd.DataFrame()

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

# Загрузка основной базы
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, sep="\t", encoding="cp1252")
    df = df.fillna("N/A")
    df.replace("", "N/A", inplace=True)
else:
    df = pd.DataFrame()

df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Syllable_Count"] = df["Rhythmic_representation"].apply(count_syllables)
df["Excerpt_ID"] = df["Excerpt_ID"].astype(str)

# Загрузка METALVOX
if os.path.exists(METALVOX_FILE):
    metalvox_df = pd.read_csv(METALVOX_FILE, sep="\t")
else:
    metalvox_df = pd.DataFrame()

metalvox_df["Original_Corresponding_Excerpt"] = metalvox_df["Original_Corresponding_Excerpt"].astype(str)

# Shared songs
SHARED_EXCERPT_IDS = [
    "EXCE-093", "EXCE-056", "EXCE-108", "EXCE-124",
    "EXCE-064", "EXCE-155", "EXCE-179", "EXCE-087",
    "EXCE-141", "EXCE-042", "EXCE-208", "EXCE-184"
]

@app.route("/metalvox")
def metalvox():
    selected_vocalist = request.args.get("vocalist", "C")
    df_vocalist = metalvox_df[metalvox_df["Vocalist_ID"] == selected_vocalist].copy()

    # ВАЖНО: вот правильное разделение
    shared_df = df_vocalist[df_vocalist["Original_Corresponding_Excerpt"].isin(SHARED_EXCERPT_IDS)].copy()
    unique_df = df_vocalist[~df_vocalist["Original_Corresponding_Excerpt"].isin(SHARED_EXCERPT_IDS)].copy()

    shared_df = shared_df.sort_values(["Song", "Technique"])
    unique_df = unique_df.sort_values(["Song", "Technique"])

    vocalists_df = metalvox_df[["Vocalist_ID", "Credits"]].drop_duplicates()
    vocalists_df = vocalists_df[
        (vocalists_df["Vocalist_ID"].notnull()) &
        (vocalists_df["Vocalist_ID"].str.strip() != "") &
        (vocalists_df["Vocalist_ID"].str.len() == 1)
        ]
    vocalists_df = vocalists_df.sort_values("Vocalist_ID")
    vocalist_credits = {
        row["Vocalist_ID"]: row["Credits"] for _, row in vocalists_df.iterrows()
    }
    vocalists = list(vocalist_credits.keys())

    excerpts_dict = {row["Excerpt_ID"]: row.to_dict() for _, row in df.iterrows()}

    return render_template(
        "metalvox.html",
        shared=shared_df.to_dict(orient="records"),
        unique=unique_df.to_dict(orient="records"),
        vocalists=vocalists,
        vocalist_credits=vocalist_credits,
        selected_vocalist=selected_vocalist,
        excerpts=df.to_dict(orient="records"),
        excerpts_dict=excerpts_dict,
    )


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/spotty5-emvt-examples-dataset")
def vocal_techniques_popularity():
    return render_template("spotty5-emvt-examples-dataset.html", excerpts=df.to_dict(orient="records"))

@app.route("/extreme-metal-vocal-techniques-dataset")
def vocal_techniques():
    return render_template("extreme-metal-vocal-techniques-dataset.html")

@app.route("/triple_twelve")
def triple_twelve():
    # Получаем выбранного вокалиста и технику из GET-параметров (по умолчанию All)
    selected_vocalist = request.args.get("vocalist", "A")
    selected_technique = request.args.get("technique", "All")

    # Получаем фрагменты выбранного вокалиста
    df_vocalist = triple_df[triple_df["Vocalist_ID"] == selected_vocalist].copy()

    # Определяем функции для фильтрации и получения оригинальной техники
    excerpts_dict = {str(row["Excerpt_ID"]): row.to_dict() for _, row in df.iterrows()}
    def get_original_tech(ex_id):
        ex = excerpts_dict.get(str(ex_id))
        return ex["Technique"] if ex is not None and "Technique" in ex else "N/A"

    # Добавляем колонку Original_Technique
    df_vocalist["Original_Technique"] = df_vocalist["Original_Corresponding_Excerpt"].apply(get_original_tech)

    # Список техник, доступных у выбранного вокалиста (для выпадающего меню)
    technique_options = sorted(df_vocalist["Original_Technique"].dropna().unique(), key=lambda x: x.lower())
    # Для сортировки: Clean, Screaming, Growling (можно дополнять список)
    technique_order = ["Clean", "Screaming", "Growling"]
    def technique_sort_key(tech):
        tech = (tech or "").lower()
        for idx, base in enumerate(technique_order):
            if base.lower() in tech:
                return idx
        return len(technique_order)  # все прочие в конец

    # Разделяем shared и unique
    shared_df = df_vocalist[df_vocalist["Original_Corresponding_Excerpt"].isin(SHARED_EXCERPT_IDS)].copy()
    unique_df = df_vocalist[~df_vocalist["Original_Corresponding_Excerpt"].isin(SHARED_EXCERPT_IDS)].copy()

    # Фильтрация по технике, если не All
    if selected_technique != "All":
        shared_df = shared_df[shared_df["Original_Technique"] == selected_technique]
        unique_df = unique_df[unique_df["Original_Technique"] == selected_technique]

    # Сортировка: сначала Clean, потом Screaming, потом Growling, затем всё остальное по алфавиту
    shared_df = shared_df.sort_values(
        by=["Original_Technique", "Song", "Technique"],
        key=lambda col: col.map(lambda x: (technique_sort_key(x), x or ""))
    )
    unique_df = unique_df.sort_values(
        by=["Original_Technique", "Song", "Technique"],
        key=lambda col: col.map(lambda x: (technique_sort_key(x), x or ""))
    )

    # Список вокалистов и кредиты
    vocalists_df = triple_df[["Vocalist_ID", "Credits"]].drop_duplicates()
    vocalists_df = vocalists_df[
        (vocalists_df["Vocalist_ID"].notnull()) &
        (vocalists_df["Vocalist_ID"].str.strip() != "") &
        (vocalists_df["Vocalist_ID"].str.len() == 1)
    ].sort_values("Vocalist_ID")
    vocalist_credits = {row["Vocalist_ID"]: row["Credits"] for _, row in vocalists_df.iterrows()}
    vocalists = list(vocalist_credits.keys())

    return render_template(
        "triple_twelve.html",
        shared=shared_df.to_dict(orient="records"),
        unique=unique_df.to_dict(orient="records"),
        vocalists=vocalists,
        vocalist_credits=vocalist_credits,
        selected_vocalist=selected_vocalist,
        selected_technique=selected_technique,
        technique_options=technique_options,
        excerpts=df.to_dict(orient="records"),
        excerpts_dict=excerpts_dict,
    )



@app.route("/analytics")
def analytics():
    db_info = {
        "columns": ["Artist", "Album", "Year", "Example_type",
                    "Album_Popularity", "Track_Popularity",
                    "Stream_Count", "Syllable_Count", "Tempo_(approx.)", "Excerpt_duration_ms"],
        "numeric_columns": ["Album_Popularity", "Track_Popularity", "Stream_Count",
                            "Syllable_Count", "Year", "Tempo_(approx.)", "Excerpt_duration_ms"],
        "categorical_columns": ["Artist"]
    }

    return render_template(
        "analytics.html",
        columns=db_info["columns"],
        data=df.to_dict(orient="records"),
        numeric_columns=db_info["numeric_columns"],
        categorical_columns=db_info["categorical_columns"],
        year_range=[int(df["Year"].min()), int(df["Year"].max())]
    )

@app.route("/spectral-centroid-analysis")
def spectral_centroid():
    df_local = df[df["Technique"].isin(["Growling", "Screaming", "Clean"])].copy()
    df_local = df_local[df_local["Spectral_Centroid"] != "N/A"]

    df_local["Spectral_Centroid"] = pd.to_numeric(df_local["Spectral_Centroid"], errors="coerce")
    df_local = df_local.dropna(subset=["Spectral_Centroid"])

    group_stats = df_local.groupby("Technique")["Spectral_Centroid"].agg(['mean', 'std', 'count', 'min', 'max'])

    from scipy.stats import f_oneway, ttest_ind
    from statsmodels.stats.multicomp import pairwise_tukeyhsd

    growl = df_local[df_local["Technique"] == "Growling"]["Spectral_Centroid"]
    scream = df_local[df_local["Technique"] == "Screaming"]["Spectral_Centroid"]
    clean = df_local[df_local["Technique"] == "Clean"]["Spectral_Centroid"]

    f_stat, p_value_anova = f_oneway(growl, scream, clean)
    t_stat, p_value_ttest = ttest_ind(growl, scream)

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
