import matplotlib.pyplot as plt
from io import BytesIO
import os
from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import matplotlib
matplotlib.use("Agg")

app = Flask(__name__)

CSV_FILE = "dinkes-od_17448_jml_penderita_diabetes_melitus_brdsrkn_kabupatenko_v2_data.csv"

COLUMNS = [
    "id",
    "kode_provinsi",
    "nama_provinsi",
    "kode_kabupaten_kota",
    "nama_kabupaten_kota",
    "jumlah_penderita_dm",
    "satuan",
    "tahun"
]


def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df.to_csv(CSV_FILE, index=False)


def generate_id(df):
    if df.empty:
        return 1
    return int(df["id"].max()) + 1


# ===================== READ =====================

@app.route("/kab", methods=["GET"])
def get_all():
    df = load_data()
    return jsonify(df.to_dict(orient="records"))


@app.route("/kab/<int:id>", methods=["GET"])
def get_by_id(id):
    df = load_data()
    data = df[df["id"] == id]

    if data.empty:
        return jsonify({"message": "Data tidak ditemukan"}), 404

    return jsonify(data.to_dict(orient="records")[0])


# ===================== CREATE =====================

@app.route("/kab", methods=["POST"])
def create_data():
    df = load_data()
    new_data = request.json

    new_data["id"] = generate_id(df)
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    save_data(df)
    return jsonify({"message": "Data berhasil ditambahkan", "data": new_data}), 201


# ===================== UPDATE =====================

@app.route("/kab/<int:id>", methods=["PUT"])
def update_data(id):
    df = load_data()
    index = df[df["id"] == id].index

    if index.empty:
        return jsonify({"message": "Data tidak ditemukan"}), 404

    for key, value in request.json.items():
        if key in df.columns:
            df.loc[index, key] = value

    save_data(df)
    return jsonify({"message": "Data berhasil diupdate"})


# ===================== DELETE =====================

@app.route("/kab/<int:id>", methods=["DELETE"])
def delete_data(id):
    df = load_data()
    if id not in df["id"].values:
        return jsonify({"message": "Data tidak ditemukan"}), 404

    df = df[df["id"] != id]
    save_data(df)
    return jsonify({"message": "Data berhasil dihapus"})


# ===================== VIEW =====================

@app.route("/")
def index():
    df = load_data()
    data = df.to_dict(orient="records")
    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/grafik")
def grafik():
    df = load_data()

    if df.empty:
        return "Data kosong"

    jenis = request.args.get("jenis", "kab")  # default grafik per kabupaten

    plt.figure(figsize=(10, 6))

    # ===================== VARIASI =====================

    if jenis == "kab":
        grouped = df.groupby("nama_kabupaten_kota")[
            "jumlah_penderita_dm"].sum()
        grouped.plot(kind="bar")
        plt.xlabel("Kabupaten/Kota")

    elif jenis == "tahun":
        grouped = df.groupby("tahun")["jumlah_penderita_dm"].sum()
        grouped.plot(kind="line", marker="o")
        plt.xlabel("Tahun")

    elif jenis == "top10":
        grouped = (
            df.groupby("nama_kabupaten_kota")["jumlah_penderita_dm"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        grouped.plot(kind="bar")
        plt.xlabel("Kabupaten/Kota (Top 10)")

    elif jenis == "pie":
        grouped = (
            df.groupby("nama_kabupaten_kota")["jumlah_penderita_dm"]
            .sum()
            .head(5)
        )
        grouped.plot(kind="pie", autopct="%1.1f%%")
        plt.ylabel("")

    else:
        return "Jenis grafik tidak dikenal"

    # ===================== UMUM =====================

    plt.title("Grafik Penderita Diabetes Melitus")
    plt.ylabel("Jumlah Penderita")
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)

    return send_file(img, mimetype="image/png")
