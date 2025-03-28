from flask import Flask, render_template, send_from_directory
import pandas as pd
import os
app = Flask(__name__)
DATA_FILE = "excerpts_database.tsv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, sep="\t", encoding="cp1252")
else:
    df = pd.DataFrame()
@app.route("/")
def index():
    examples = df.to_dict(orient="records")
    return render_template("index.html", excerpts=examples)
if __name__ == "__main__":
    app.run(debug=True)