def generate_health_recommendations(data, prediction_label=None):
    recommendations = []
    headline = []

    def add(level, title, message):
        recommendations.append({
            "level": level,
            "title": title,
            "message": message
        })

    def add_headline(level, title, message):
        headline.append({
            "level": level,
            "title": title,
            "message": message
        })

    systolic = data.get("systolic", 0)
    diastolic = data.get("diastolic", 0)
    salt_intake = data.get("salt_intake", 0)
    bmi = data.get("bmi", 0)
    stress_level = data.get("stress_level", 0)
    sleep_duration = data.get("sleep_duration", 0)
    smoking_status = data.get("smoking_status", False)
    exercise_level = str(data.get("exercise_level", "")).lower()
    family_history = data.get("family_history", False)
    age = data.get("age", 0)
    medication = str(data.get("medication", "None"))

    # =====================================================
    # 1. AI PREDICTION HEADLINE (ALWAYS FIRST)
    # =====================================================
    if prediction_label == "Berisiko":
        add_headline(
            "critical",
            "Hasil Prediksi: Anda Berisiko Hipertensi",
            "Model machine learning mendeteksi adanya kecenderungan risiko hipertensi berdasarkan kombinasi indikator kesehatan Anda. Disarankan melakukan pemantauan tekanan darah dan konsultasi medis lebih lanjut."
        )
    elif prediction_label == "Tidak Berisiko":
        add_headline(
            "good",
            "Hasil Prediksi: Risiko Hipertensi Rendah",
            "Berdasarkan data yang dimasukkan, kondisi Anda saat ini belum menunjukkan kecenderungan risiko hipertensi yang tinggi. Tetap pertahankan pola hidup sehat secara konsisten."
        )

    # =====================================================
    # 2. BLOOD PRESSURE RULES
    # =====================================================
    if systolic >= 140 or diastolic >= 90:
        add("critical", "Tekanan Darah Tinggi",
            "Nilai tekanan darah Anda berada di atas batas normal. Kurangi asupan natrium, lakukan pemantauan rutin, dan pertimbangkan pemeriksaan lanjutan.")
    elif systolic >= 130 or diastolic >= 85:
        add("warning", "Tekanan Darah Mulai Meningkat",
            "Tekanan darah Anda mulai mendekati kategori hipertensi. Perbaikan pola makan dan aktivitas fisik perlu mulai diperhatikan.")
    elif systolic < 120 and diastolic < 80:
        add("good", "Tekanan Darah Dalam Batas Normal",
            "Nilai tekanan darah Anda masih dalam rentang yang baik. Pertahankan pola hidup sehat agar tetap stabil.")

    # =====================================================
    # 3. SALT INTAKE
    # =====================================================
    if salt_intake > 10:
        add("critical", "Konsumsi Garam Sangat Tinggi",
            "Asupan garam Anda jauh di atas anjuran WHO yaitu maksimal 5 gram per hari. Batasi makanan asin, instan, dan olahan.")
    elif salt_intake > 5:
        add("warning", "Konsumsi Garam Berlebih",
            "Konsumsi garam Anda melebihi batas ideal. Mengurangi penggunaan garam dapat membantu menjaga tekanan darah.")
    else:
        add("good", "Konsumsi Garam Terkontrol",
            "Asupan garam Anda sudah dalam batas yang cukup baik.")

    # =====================================================
    # 4. BMI
    # =====================================================
    if bmi >= 30:
        add("critical", "Obesitas",
            "BMI Anda termasuk kategori obesitas yang memiliki hubungan kuat dengan hipertensi dan penyakit jantung.")
    elif bmi >= 25:
        add("warning", "Berat Badan Berlebih",
            "Kelebihan berat badan dapat meningkatkan tekanan darah. Penurunan berat badan bertahap sangat disarankan.")
    elif bmi < 18.5:
        add("info", "Berat Badan Rendah",
            "BMI Anda di bawah normal. Pastikan kebutuhan nutrisi harian tetap tercukupi.")
    else:
        add("good", "BMI Ideal",
            "Indeks massa tubuh Anda berada dalam kategori sehat.")

    # =====================================================
    # 5. STRESS
    # =====================================================
    if stress_level >= 8:
        add("critical", "Tingkat Stres Sangat Tinggi",
            "Stres berat dapat memicu lonjakan tekanan darah. Coba lakukan manajemen stres, relaksasi, dan istirahat cukup.")
    elif stress_level >= 5:
        add("warning", "Tingkat Stres Sedang",
            "Stres yang terus berlangsung dapat memengaruhi kesehatan jantung. Luangkan waktu untuk aktivitas relaksasi.")
    else:
        add("good", "Tingkat Stres Terkendali",
            "Kondisi stres Anda relatif masih terkendali.")

    # =====================================================
    # 6. SLEEP
    # =====================================================
    if sleep_duration < 5:
        add("critical", "Kurang Tidur Berat",
            "Durasi tidur sangat kurang dan dapat memengaruhi kestabilan hormon serta tekanan darah.")
    elif sleep_duration < 7:
        add("warning", "Durasi Tidur Kurang",
            "Tidur kurang dari 7 jam dapat meningkatkan beban jantung dan stres tubuh.")
    elif sleep_duration > 9:
        add("info", "Tidur Berlebih",
            "Tidur terlalu lama dapat mengindikasikan kualitas tidur yang kurang optimal.")
    else:
        add("good", "Durasi Tidur Baik",
            "Durasi tidur Anda sudah sesuai kebutuhan tubuh.")

    # =====================================================
    # 7. SMOKING
    # =====================================================
    if smoking_status:
        add("critical", "Kebiasaan Merokok",
            "Merokok meningkatkan kekakuan pembuluh darah dan memperbesar risiko hipertensi.")
    else:
        add("good", "Tidak Merokok",
            "Tidak merokok merupakan keputusan yang sangat baik untuk menjaga kesehatan jantung.")

    # =====================================================
    # 8. EXERCISE
    # =====================================================
    if exercise_level == "low":
        add("warning", "Aktivitas Fisik Rendah",
            "Aktivitas fisik Anda masih minim. Lakukan olahraga minimal 30 menit sebanyak 3–5 kali per minggu.")
    elif exercise_level == "moderate":
        add("info", "Aktivitas Fisik Cukup",
            "Aktivitas fisik Anda cukup baik namun masih dapat ditingkatkan.")
    elif exercise_level == "high":
        add("good", "Aktivitas Fisik Sangat Baik",
            "Kebiasaan olahraga Anda sangat membantu menjaga tekanan darah tetap stabil.")

    # =====================================================
    # 9. FAMILY HISTORY
    # =====================================================
    if family_history:
        add("warning", "Riwayat Hipertensi Keluarga",
            "Riwayat keluarga meningkatkan kerentanan hipertensi sehingga pemeriksaan berkala sangat dianjurkan.")

    # =====================================================
    # 10. AGE
    # =====================================================
    if age >= 50:
        add("info", "Faktor Usia",
            "Pertambahan usia membuat elastisitas pembuluh darah menurun sehingga kontrol kesehatan perlu lebih rutin.")

    # =====================================================
    # 11. MEDICATION
    # =====================================================
    if medication.lower() != "none":
        add("info", "Riwayat Konsumsi Obat",
            "Pastikan penggunaan obat dilakukan sesuai anjuran dokter dan tidak dihentikan sepihak.")

    # =====================================================
    # 12. ADVANCED COMBINATION RULES
    # =====================================================
    if salt_intake > 5 and systolic >= 130:
        add("critical", "Kombinasi Garam & Tekanan Darah",
            "Asupan garam tinggi disertai tekanan darah meningkat menunjukkan perlunya diet rendah natrium secara serius.")

    if bmi >= 25 and exercise_level == "low":
        add("warning", "Berat Badan & Kurang Aktivitas",
            "Kombinasi berat badan berlebih dan kurang olahraga mempercepat peningkatan tekanan darah.")

    if stress_level >= 7 and sleep_duration < 6:
        add("critical", "Stres Tinggi & Kurang Tidur",
            "Kombinasi ini dapat meningkatkan beban kerja jantung dan memicu hipertensi.")

    if smoking_status and family_history:
        add("critical", "Faktor Risiko Ganda",
            "Merokok ditambah riwayat keluarga hipertensi meningkatkan risiko kardiovaskular secara signifikan.")

    if age >= 50 and systolic >= 130:
        add("warning", "Usia & Tekanan Darah",
            "Usia lanjut dengan tekanan darah meningkat memerlukan monitoring yang lebih konsisten.")

    # =====================================================
    # DEFAULT FALLBACK
    # =====================================================
    if len(recommendations) == 0:
        add("good", "Kondisi Umum Baik",
            "Sebagian besar indikator kesehatan Anda berada dalam kondisi yang baik. Tetap pertahankan pola hidup sehat.")

    # =====================================================
    # SORTING
    # =====================================================
    priority_order = {
        "critical": 1,
        "warning": 2,
        "info": 3,
        "good": 4
    }

    recommendations.sort(key=lambda x: priority_order[x["level"]])

    return headline + recommendations