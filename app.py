from flask import Flask, render_template, request
from experta import *
from collections import defaultdict
import mysql.connector

app = Flask(__name__)

# Koneksi ke database MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'vokasi_db'
}

class VokasiExpertSystem(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.cf_values = defaultdict(float)

    @Rule(Fact(CC01=MATCH.CF1), Fact(CC02=MATCH.CF2), Fact(CC03=MATCH.CF3), Fact(CC04=MATCH.CF4), Fact(CC05=MATCH.CF5))
    def rule_1(self, CF1, CF2, CF3, CF4, CF5):
        cf_result = min(CF1, CF2, CF3, CF4, CF5)
        self.cf_values['Tangible'] = cf_result

    @Rule(Fact(CC06=MATCH.CF6), Fact(CC07=MATCH.CF7), Fact(CC08=MATCH.CF8), Fact(CC09=MATCH.CF9), Fact(CC10=MATCH.CF10), Fact(CC11=MATCH.CF11))
    def rule_2(self, CF6, CF7, CF8, CF9, CF10, CF11):
        cf_result = min(CF6, CF7, CF8, CF9, CF10, CF11)
        self.cf_values['Thinking'] = cf_result
    
    @Rule(Fact(CC12=MATCH.CF12), Fact(CC13=MATCH.CF13), Fact(CC14=MATCH.CF14), Fact(CC15=MATCH.CF15), Fact(CC16=MATCH.CF16), Fact(CC17=MATCH.CF17))
    def rule_3(self, CF12, CF13, CF14, CF15, CF16, CF17):
        cf_result = min(CF12, CF13, CF14, CF15, CF16, CF17)
        self.cf_values['Flexible'] = cf_result

    @Rule(Fact(CC18=MATCH.CF18), Fact(CC19=MATCH.CF19), Fact(CC20=MATCH.CF20), Fact(CC21=MATCH.CF21), Fact(CC22=MATCH.CF22), Fact(CC23=MATCH.CF23))
    def rule_4(self, CF18, CF19, CF20, CF21, CF22, CF23):
        cf_result = min(CF18, CF19, CF20, CF21, CF22, CF23)
        self.cf_values['Enterprener'] = cf_result

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        nim = request.form.get("nim")

        cf_mapping = {
            "pasti tidak": 0.0,
            "hampir pasti tidak": 0.1,
            "kemungkinan besar tidak": 0.2,
            "mungkin tidak": 0.3,
            "tidak tahu": 0.4,
            "mungkin": 0.5,
            "kemungkinan besar": 0.6,
            "hampir pasti": 0.8,
            "pasti": 1.0
        }
        
        user_facts = {}
        for i in range(1, 24):
            cc_input = request.form.get(f"CC{str(i).zfill(2)}")
            if cc_input in cf_mapping:
                user_facts[f"CC{str(i).zfill(2)}"] = cf_mapping[cc_input]

        # Jalankan sistem pakar
        engine = VokasiExpertSystem()
        engine.reset()

        for fact, cf in user_facts.items():
            engine.declare(Fact(**{fact: cf}))

        engine.run()

        if engine.cf_values:
            best_match = max(engine.cf_values, key=engine.cf_values.get)
            result = f"Minat vokasi Anda adalah {best_match} dengan tingkat kepastian {engine.cf_values[best_match]*100:.1f}%"

            # Simpan hasil ke database
            try:
                db = mysql.connector.connect(**db_config)
                cursor = db.cursor()
                cursor.execute("INSERT INTO results (name, nim, result) VALUES (%s, %s, %s)", (name, nim, result))
                db.commit()
            except mysql.connector.Error as err:
                result = f"Error: {err}"
            finally:
                cursor.close()
                db.close()
        else:
            result = "Tidak ada hasil vokasi yang cocok berdasarkan input Anda."

        return render_template("result.html", result=result)

    # Daftar ciri-ciri
    ciri_ciri = [
        "Kemampuan mekanikal",
        "Psikomotor",
        "Suka menanam tumbuhan",
        "Suka pelihara hewan",
        "Suka bekerja dengan mesin",
        "Kemampuan menganalisa yang baik",
        "Cenderung berpikir matematis",
        "Suka mengobservasi",
        "Suka bekerja sendiri",
        "Selalu ingin tahu",
        "Suka kedisiplinan",
        "Berpikir abstrak",
        "Menyukai keindahan",
        "Kreatif",
        "Emosional",
        "Suka melukis",
        "Imaginative",
        "Percaya diri",
        "Mudah beradaptasi",
        "Kepemimpinan yang baik",
        "Kemampuan interpersonal yang baik",
        "Penuh energi",
        "Optimis",
    ]

    # Ubah format ciri-ciri
    ciri_ciri_indexed = {f'CC{str(i).zfill(2)}': ciri for i, ciri in enumerate(ciri_ciri, start=1)}

    return render_template("index.html", result=None, ciri_ciri=ciri_ciri_indexed)

if __name__ == "__main__":
    app.run(debug=True)
