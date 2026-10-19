"""
Studi Kasus Sesi 5: Merancang dan Mengevaluasi Dashboard Visualisasi Data yang Berpusat pada Pengguna
(Studi kasus: dashboard risiko drop out untuk dosen wali dan koordinator prodi)
Berdasarkan webinar "Human-Computer Interaction & Data Visualization" (Arafat Febriandirza, BRIN).

Alur (mengikuti modul materi):
  1) Persona, skenario, dan kebutuhan fungsional/non-fungsional        (modul 5)
  2) Pemilihan grafik dan integritas visual: grafik buruk vs baik        (modul 6: Tufte, chartjunk, data-ink)
  3) Aksesibilitas: pemeriksaan rasio kontras warna WCAG                 (modul 3: Perceivable)
  4) Evaluasi usability: SUS, tingkat keberhasilan, waktu tugas          (modul 4: usability testing)
  5) Checklist 10 heuristik Nielsen (templat untuk evaluasi pakar)       (tanya jawab)
  6) Dashboard interaktif: overview first, zoom and filter, details on demand (modul 6, mantra Shneiderman)
  7) Verifikasi kebutuhan terhadap dashboard yang dibuat

Data: UCI "Predict Students' Dropout and Academic Success" (CC BY 4.0) di data/data.csv.
Data usability SINTETIS (simulasi) kecuali Anda memberi data uji coba nyata lewat --usability.
Jalankan:  python case_study_hci.py          Opsi: --usability data/usability.csv --offline
"""
import argparse, os, sys, time, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import plotly.graph_objects as go

OUT, SEED = "output", 42
URL = "https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success"
RISK, NEUTRAL, TEXT, REF = "#B71C1C", "#757575", "#212121", "#0D47A1"     # palet dashboard (diperiksa kontrasnya)
SUMMARY = {}

# variabel yang bisa dipilih pengguna di dashboard: kolom -> (judul, label nilai)
GROUPS = {
    "tuition_fees_up_to_date": ("Status pembayaran biaya kuliah", {0: "Menunggak", 1: "Lunas"}),
    "debtor": ("Status utang", {0: "Bukan debitur", 1: "Debitur"}),
    "scholarship_holder": ("Beasiswa", {0: "Tanpa beasiswa", 1: "Penerima beasiswa"}),
    "daytime_evening_attendance": ("Waktu kuliah", {0: "Malam", 1: "Siang"}),
    "gender": ("Gender (kode pada data)", {0: "Kode 0", 1: "Kode 1"}),
    "kelompok_umur": ("Kelompok umur saat mendaftar", None),
    "course": ("Program studi (kode)", None),
}

PERSONA = {
    "nama": "Bu Rina", "usia": 45, "peran": "Dosen wali dan anggota gugus mutu prodi", "kemampuan_teknologi": "Menengah (terbiasa Excel dan e-learning)",
    "goal": ["Mengetahui kelompok mahasiswa yang paling berisiko drop out dalam 5 detik sebelum rapat prodi",
             "Menunjukkan temuan kepada koordinator prodi tanpa menjelaskan angka satu per satu"],
    "pain_point": ["Laporan Excel panjang dan penuh angka tanpa penekanan warna",
                   "Sulit membandingkan kelompok (beasiswa, biaya kuliah, umur) secara cepat",
                   "Grafik lama sulit dibaca di layar proyektor"],
    "perilaku": ["Membuka laporan di laptop dan tablet", "Lebih suka grafik batang sederhana daripada tabel", "Jarang memakai pintasan keyboard"],
}
SKENARIO = {"konteks": "Rapat prodi pagi hari, layar proyektor dengan pencahayaan ruangan terang",
            "trigger": "Koordinator prodi bertanya: kelompok mahasiswa mana yang perlu didampingi lebih dulu?",
            "action": "Bu Rina membuka dashboard, memilih variabel 'Status pembayaran biaya kuliah', lalu mengarahkan kursor ke batang tertinggi",
            "outcome": "Kelompok berisiko terlihat jelas (batang merah di atas garis rata-rata) dan diputuskan untuk diberi konseling dalam kurang dari 1 menit"}
FUNGSIONAL = {"F1": "Pengguna dapat memilih variabel pengelompokan (filter) minimal 5 pilihan",
              "F2": "Detail angka muncul saat kursor diarahkan ke batang (details on demand)",
              "F3": "Grafik dapat diekspor sebagai gambar"}
NONFUNGSIONAL = {"N1": "Dashboard selesai dibangun dalam kurang dari 2 detik",
                 "N2": "Semua warna teks dan grafik memenuhi rasio kontras WCAG AA",
                 "N3": "Ukuran file dashboard di bawah batas yang ditetapkan (1 MB mode CDN, 10 MB mode offline)"}


def savefig(name):
    plt.tight_layout(); plt.savefig(f"{OUT}/{name}", dpi=130); plt.close()


# ------------------------------------------------------------- DATA
def load_data(path):
    if not os.path.exists(path):
        sys.exit(f"File '{path}' tidak ditemukan. Unduh dari {URL} dan simpan data.csv di folder data/.")
    df = pd.read_csv(path, sep=";")
    if df.shape[1] == 1: df = pd.read_csv(path, sep=",")
    df.columns = [re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_") for c in df.columns]
    df["target"] = df.target.astype(str).str.strip()
    d = df[df.target != "Enrolled"].reset_index(drop=True)          # hasil akhir 'Enrolled' belum diketahui
    d["dropout"] = (d.target == "Dropout").astype(int)
    d["kelompok_umur"] = pd.cut(d.age_at_enrollment, [0, 19, 22, 29, 100], labels=["<=19", "20-22", "23-29", ">=30"]).astype(str)
    return d


def rate_table(d, col, sort_desc=False):
    t = d.groupby(col, observed=True).dropout.agg(n="size", dropouts="sum", rate="mean").reset_index()
    labels = GROUPS.get(col, (None, None))[1]
    t["label"] = t[col].map(labels) if labels else t[col].astype(str)
    if col == "kelompok_umur":                                      # urutan logis, bukan alfabet
        t = t.set_index(col).loc[["<=19", "20-22", "23-29", ">=30"]].reset_index()
    return t.sort_values("rate", ascending=False).reset_index(drop=True) if sort_desc else t


# ------------------------------------------------------------- 1. PERSONA, SKENARIO, KEBUTUHAN
def modul1_persona():
    md = ["# Persona, Skenario, dan Kebutuhan\n", f"## Persona: {PERSONA['nama']} ({PERSONA['usia']} tahun)",
          f"- **Peran:** {PERSONA['peran']}", f"- **Kemampuan teknologi:** {PERSONA['kemampuan_teknologi']}\n", "### Goal"]
    md += [f"- {x}" for x in PERSONA["goal"]] + ["\n### Pain point"] + [f"- {x}" for x in PERSONA["pain_point"]]
    md += ["\n### Perilaku"] + [f"- {x}" for x in PERSONA["perilaku"]]
    md += ["\n## Skenario penggunaan (konteks, trigger, action, outcome)"] + [f"- **{k.capitalize()}:** {v}" for k, v in SKENARIO.items()]
    md += ["\n## Kebutuhan fungsional"] + [f"- {k}: {v}" for k, v in FUNGSIONAL.items()]
    md += ["\n## Kebutuhan non-fungsional"] + [f"- {k}: {v}" for k, v in NONFUNGSIONAL.items()]
    md += ["\n> Persona ini fiktif dan berdasarkan asumsi. Pada penerapan nyata, persona harus disintesis dari wawancara, observasi, dan survei pengguna."]
    open(f"{OUT}/persona_skenario.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(f"Persona '{PERSONA['nama']}', 1 skenario, {len(FUNGSIONAL)} kebutuhan fungsional, {len(NONFUNGSIONAL)} non-fungsional -> output/persona_skenario.md")
    SUMMARY["Persona"] = f"{PERSONA['nama']}; {len(FUNGSIONAL)} kebutuhan fungsional dan {len(NONFUNGSIONAL)} non-fungsional"


# ------------------------------------------------------------- 2. GRAFIK BURUK VS BAIK
def modul2_grafik(d):
    overall = d.dropout.mean()
    beasiswa = rate_table(d, "daytime_evening_attendance"); lb = ["Kuliah\nmalam", "Kuliah\nsiang"]    # dua kelompok dengan selisih sedang
    prodi = rate_table(d, "course"); umur = rate_table(d, "kelompok_umur")
    fig, ax = plt.subplots(2, 3, figsize=(14, 8))
    # (a) sumbu terpotong vs mulai dari nol
    lo = beasiswa.rate.min() * 0.9
    ax[0, 0].bar(lb, beasiswa.rate * 100, color="tab:red"); ax[0, 0].set_ylim(lo * 100, beasiswa.rate.max() * 100 * 1.02)
    ax[0, 0].set_title("BURUK: sumbu y terpotong\n(selisih tampak jauh lebih besar)", fontsize=10)
    ax[1, 0].bar(lb, beasiswa.rate * 100, color=[RISK if r > overall else NEUTRAL for r in beasiswa.rate]); ax[1, 0].set_ylim(0, 100)
    for i, v in enumerate(beasiswa.rate * 100): ax[1, 0].text(i, v + 2, f"{v:.0f}%", ha="center")
    ax[1, 0].set_title("BAIK: sumbu mulai dari nol, nilai dilabeli", fontsize=10)
    # (b) pie banyak irisan vs bar terurut
    ax[0, 1].pie(prodi.n, labels=prodi.course.astype(str), textprops={"fontsize": 6}); ax[0, 1].set_title(f"BURUK: pie dengan {len(prodi)} irisan\n(sulit dibandingkan)", fontsize=10)
    s = prodi.sort_values("n"); ax[1, 1].barh(s.course.astype(str), s.n, color=NEUTRAL); ax[1, 1].tick_params(labelsize=7)
    ax[1, 1].set_title("BAIK: bar terurut untuk membandingkan kategori", fontsize=10); ax[1, 1].set_xlabel("Jumlah mahasiswa")
    # (c) warna pelangi + garis berlebihan vs satu sorotan warna
    ax[0, 2].bar(umur.label, umur.rate * 100, color=["red", "orange", "yellow", "green"], edgecolor="k", linewidth=2)
    ax[0, 2].grid(True, linewidth=1.5); ax[0, 2].set_title("BURUK: warna pelangi tanpa makna\n+ garis kisi tebal (chartjunk)", fontsize=10)
    mx = umur.rate.idxmax(); ax[1, 2].bar(umur.label, umur.rate * 100, color=[RISK if i == mx else NEUTRAL for i in umur.index])
    for i, v in enumerate(umur.rate * 100): ax[1, 2].text(i, v + 1.5, f"{v:.0f}%", ha="center")
    ax[1, 2].set_title("BAIK: satu warna sorot untuk yang penting\n(atribut pra-atentif), tanpa hiasan", fontsize=10)
    for a in ax[1]: a.spines[["top", "right"]].set_visible(False)
    for a in (ax[0, 0], ax[0, 2]): a.set_ylabel("Tingkat dropout (%)")
    ax[1, 0].set_ylabel("Tingkat dropout (%)"); ax[1, 2].set_ylabel("Tingkat dropout (%)")
    savefig("01_grafik_buruk_vs_baik.png")
    lihat = (beasiswa.rate.min() - lo) / (beasiswa.rate.max() - lo)
    print(f"Tiga pasang perbandingan dibuat. Pada sumbu terpotong, batang terendah tampak hanya {lihat:.0%} dari batang tertinggi, "
          f"padahal sebenarnya {beasiswa.rate.min() / beasiswa.rate.max():.0%}.")
    SUMMARY["Grafik buruk vs baik"] = "3 pasang (sumbu terpotong, pie vs bar, warna pelangi vs sorotan) -> output/01_grafik_buruk_vs_baik.png"


# ------------------------------------------------------------- 3. KONTRAS WARNA (WCAG)
def luminance(hexcol):
    r, g, b = [int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(fg, bg):
    l1, l2 = sorted([luminance(fg), luminance(bg)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def modul3_kontras():
    items = [("Palet dashboard", "Teks utama", TEXT, "#FFFFFF", 4.5), ("Palet dashboard", "Teks sekunder", "#595959", "#FFFFFF", 4.5),
             ("Palet dashboard", "Batang berisiko", RISK, "#FFFFFF", 3.0), ("Palet dashboard", "Batang biasa", NEUTRAL, "#FFFFFF", 3.0),
             ("Palet dashboard", "Garis rata-rata", REF, "#FFFFFF", 3.0),
             ("Contoh buruk", "Teks kuning di putih", "#FFEB3B", "#FFFFFF", 4.5), ("Contoh buruk", "Teks abu muda di putih", "#BDBDBD", "#FFFFFF", 4.5),
             ("Contoh buruk", "Batang hijau muda", "#A5D6A7", "#FFFFFF", 3.0)]
    rows = [{"palet": p, "elemen": e, "warna": fg, "latar": bg, "rasio": round(contrast(fg, bg), 2), "minimum_AA": m, "lulus": contrast(fg, bg) >= m}
            for p, e, fg, bg, m in items]
    res = pd.DataFrame(rows); res.to_csv(f"{OUT}/kontras_warna.csv", index=False)
    print(res.to_string(index=False))
    ok = res[res.palet == "Palet dashboard"].lulus.all()
    SUMMARY["Kontras warna"] = f"palet dashboard lulus WCAG AA: {ok}; contoh buruk gagal: {int((~res[res.palet == 'Contoh buruk'].lulus).sum())} dari 3"
    return bool(ok)


# ------------------------------------------------------------- 4. USABILITY TESTING
def sus_score(items):                      # items: 10 nilai skala 1-5; ganjil positif, genap negatif
    a = np.asarray(items, float)
    return (np.sum(a[0::2] - 1) + np.sum(5 - a[1::2])) * 2.5


def simulate_usability(rng, n=15):
    rows = []
    for desain, p_ok, t_mu, s_mu in [("A (dashboard lama)", 0.65, np.log(90), 3.0), ("B (dashboard baru)", 0.90, np.log(45), 4.1)]:
        for i in range(n):
            s = rng.normal(s_mu, 0.6); sus = []
            for k in range(10):
                x = s if k % 2 == 0 else 6 - s
                sus.append(int(np.clip(np.round(x + rng.normal(0, 0.7)), 1, 5)))
            rows.append({"peserta": f"{desain[0]}{i+1}", "desain": desain, "tugas_berhasil": int(rng.random() < p_ok),
                         "waktu_detik": float(np.exp(rng.normal(t_mu, 0.35))), **{f"sus_{k+1}": v for k, v in enumerate(sus)}})
    return pd.DataFrame(rows)


def modul4_usability(path):
    if path and os.path.exists(path) and len(pd.read_csv(path)) > 0:
        df = pd.read_csv(path); sumber = f"DATA NYATA ({path})"
    else:
        df = simulate_usability(np.random.default_rng(SEED)); sumber = "DATA SINTETIS (simulasi untuk mendemonstrasikan prosedur analisis)"
    df["SUS"] = df[[f"sus_{k}" for k in range(1, 11)]].apply(sus_score, axis=1)
    df.to_csv(f"{OUT}/usability_data.csv", index=False)
    print(f"Sumber data: {sumber}")
    g = df.groupby("desain").agg(n=("SUS", "size"), SUS_rata2=("SUS", "mean"), SUS_sd=("SUS", "std"),
                                 berhasil=("tugas_berhasil", "mean"), waktu_median_s=("waktu_detik", "median")).round(2)
    g.to_csv(f"{OUT}/usability_ringkasan.csv"); print(g.to_string())
    a, b = [x for _, x in df.groupby("desain")]
    t_sus = stats.ttest_ind(b.SUS, a.SUS, equal_var=False)
    t_time = stats.ttest_ind(np.log(b.waktu_detik), np.log(a.waktu_detik), equal_var=False)
    table = [[b.tugas_berhasil.sum(), len(b) - b.tugas_berhasil.sum()], [a.tugas_berhasil.sum(), len(a) - a.tugas_berhasil.sum()]]
    p_succ = stats.fisher_exact(table)[1]
    pooled = np.sqrt((a.SUS.var() + b.SUS.var()) / 2); d_cohen = (b.SUS.mean() - a.SUS.mean()) / pooled
    print(f"\nUji SUS (Welch t): p = {t_sus.pvalue:.4f}, Cohen's d = {d_cohen:.2f} | uji waktu (log, Welch t): p = {t_time.pvalue:.4f} | "
          f"uji keberhasilan (Fisher): p = {p_succ:.3f}")
    print("Acuan SUS: rata-rata industri sekitar 68; di bawah 51 buruk, di atas 80 sangat baik.")
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    ax[0].boxplot([a.SUS, b.SUS], tick_labels=["A (lama)", "B (baru)"]); ax[0].axhline(68, color="r", ls="--", label="Rata-rata 68"); ax[0].legend(); ax[0].set_title("Skor SUS")
    ax[1].boxplot([a.waktu_detik, b.waktu_detik], tick_labels=["A (lama)", "B (baru)"]); ax[1].set_title("Waktu menyelesaikan tugas (detik)")
    ax[2].bar(["A (lama)", "B (baru)"], [a.tugas_berhasil.mean() * 100, b.tugas_berhasil.mean() * 100], color=[NEUTRAL, REF])
    ax[2].set_ylim(0, 100); ax[2].set_title("Tingkat keberhasilan tugas (%)")
    savefig("02_usability.png")
    SUMMARY["Usability"] = (f"{sumber.split(' (')[0].title()}: SUS A {a.SUS.mean():.0f} vs B {b.SUS.mean():.0f} (p={t_sus.pvalue:.3f}); "
                            f"berhasil {a.tugas_berhasil.mean():.0%} vs {b.tugas_berhasil.mean():.0%} (p={p_succ:.3f}, n={len(a)} per desain)")


# ------------------------------------------------------------- 5. CHECKLIST HEURISTIK NIELSEN
def modul5_heuristik():
    H = [("Visibility of system status", "Visibilitas status sistem", "Apakah pengguna selalu tahu apa yang sedang terjadi (loading, tersimpan, terkirim)?"),
         ("Match between system and real world", "Kesesuaian sistem dengan dunia nyata", "Apakah istilah dan ikon dikenal pengguna, bukan istilah teknis internal?"),
         ("User control and freedom", "Kontrol dan kebebasan pengguna", "Apakah ada undo/cancel/pintu keluar yang jelas?"),
         ("Consistency and standards", "Konsistensi dan standar", "Apakah warna, ikon, dan tata letak konsisten dan mengikuti konvensi?"),
         ("Error prevention", "Pencegahan kesalahan", "Apakah aksi berisiko diberi konfirmasi atau dibatasi?"),
         ("Recognition rather than recall", "Mengenali, bukan mengingat", "Apakah pengguna tidak dipaksa mengingat informasi dari layar lain?"),
         ("Flexibility and efficiency of use", "Fleksibilitas dan efisiensi", "Apakah ada pintasan atau kustomisasi untuk pengguna ahli?"),
         ("Aesthetic and minimalist design", "Desain estetik dan minimalis", "Apakah ada elemen yang tidak relevan atau dekoratif berlebihan?"),
         ("Help users recognize, diagnose, and recover from errors", "Membantu pulih dari kesalahan", "Apakah pesan error jelas, tanpa kode teknis, dan memberi solusi?"),
         ("Help and documentation", "Bantuan dan dokumentasi", "Apakah ada FAQ, pusat bantuan, atau panduan singkat yang mudah dicari?")]
    df = pd.DataFrame([{"no": i + 1, "heuristik": e, "terjemahan": t, "pertanyaan_evaluasi": q, "skor_keparahan_evaluator_1": "",
                        "skor_keparahan_evaluator_2": "", "catatan_temuan": ""} for i, (e, t, q) in enumerate(H)])
    df.to_csv(f"{OUT}/checklist_heuristik_nielsen.csv", index=False)
    print("Templat evaluasi pakar (kosong, isi dengan penilaian nyata; skala keparahan 0 = tidak ada masalah, 4 = bencana) -> output/checklist_heuristik_nielsen.csv")
    SUMMARY["Heuristik Nielsen"] = "templat 10 heuristik untuk diisi evaluator (tidak berisi data karangan)"


# ------------------------------------------------------------- 6. DASHBOARD INTERAKTIF
def build_dashboard(d, offline=False):
    t0 = time.perf_counter()
    overall = d.dropout.mean(); keys = list(GROUPS); fig = go.Figure(); buttons = []; hover = True
    best = None
    for i, k in enumerate(keys):
        t = rate_table(d, k, sort_desc=(k == "course"))
        big = t[t.n >= 100]
        if len(big) and (best is None or big.rate.max() > best[1]): best = (f"{GROUPS[k][0]}: {big.loc[big.rate.idxmax(), 'label']}", big.rate.max())
        colors = [RISK if r > overall else NEUTRAL for r in t.rate]                     # sorot yang di atas rata-rata
        ht = "<b>%{x}</b><br>Tingkat dropout: %{y:.1f}%<br>Jumlah mahasiswa: %{customdata[0]}<br>Dropout: %{customdata[1]}<extra></extra>"
        fig.add_trace(go.Bar(x=t.label.astype(str), y=t.rate * 100, marker_color=colors, customdata=np.c_[t.n, t.dropouts], hovertemplate=ht,
                             text=[f"{r*100:.0f}%" for r in t.rate], textposition="outside", visible=(i == 0), name=GROUPS[k][0]))
        buttons.append(dict(label=GROUPS[k][0], method="update",
                            args=[{"visible": [j == i for j in range(len(keys))]}, {"xaxis.title.text": GROUPS[k][0]}]))
    fig.add_hline(y=overall * 100, line_dash="dash", line_color=REF, annotation_text=f"Rata-rata keseluruhan {overall:.0%}", annotation_position="top left")
    kpi = f"<b>{len(d):,}</b> mahasiswa  |  Tingkat dropout <b>{overall:.1%}</b>  |  Kelompok tertinggi: <b>{best[0]}</b> ({best[1]:.0%})"
    fig.add_annotation(xref="paper", yref="paper", x=0, y=1.30, text=kpi, showarrow=False, xanchor="left", font=dict(size=16))
    fig.update_layout(title=dict(text="Dashboard Risiko Drop Out: pilih variabel untuk membandingkan kelompok", font=dict(size=18)),
                      updatemenus=[dict(buttons=buttons, direction="down", x=0, y=1.15, xanchor="left", showactive=True)],
                      yaxis=dict(range=[0, 105], title="Tingkat dropout (%)"), xaxis=dict(title=GROUPS[keys[0]][0], type="category"),
                      template="simple_white", font=dict(family="Arial", size=14, color=TEXT), showlegend=False, margin=dict(t=190))
    config = dict(displaylogo=False, toImageButtonOptions=dict(format="png", filename="dashboard_dropout", scale=2))
    path = f"{OUT}/dashboard_dropout.html"
    fig.write_html(path, include_plotlyjs=True if offline else "cdn", config=config, full_html=True)
    return fig, path, time.perf_counter() - t0, config


def modul6_dashboard(d, offline):
    fig, path, secs, config = build_dashboard(d, offline)
    size_mb = os.path.getsize(path) / 1e6
    print(f"Dashboard interaktif dibuat: {path} ({size_mb:.2f} MB, {secs:.2f} detik). Buka di browser; mode {'offline' if offline else 'CDN (butuh internet saat membuka)'}.")
    ringkas = ["# Ringkasan dashboard (alternatif teks untuk pembaca layar)\n"]
    for k in GROUPS:
        t = rate_table(d, k, sort_desc=True); ringkas.append(f"\n## {GROUPS[k][0]}\n")
        ringkas += [f"- {r.label}: dropout {r.rate:.1%} ({int(r.dropouts)} dari {int(r.n)} mahasiswa)" for r in t.itertuples()]
    open(f"{OUT}/dashboard_ringkasan.md", "w", encoding="utf-8").write("\n".join(ringkas) + "\n")
    SUMMARY["Dashboard"] = f"{len(GROUPS)} pilihan variabel, hover detail, ekspor gambar; {size_mb:.2f} MB, dibangun {secs:.2f} detik"
    return fig, secs, size_mb, config


# ------------------------------------------------------------- 7. VERIFIKASI KEBUTUHAN
def modul7_verifikasi(fig, secs, size_mb, config, kontras_ok, offline):
    n_opsi = len(fig.layout.updatemenus[0].buttons)
    hover_ok = all(tr.hovertemplate for tr in fig.data)
    limit = 10 if offline else 1
    cek = [("F1", FUNGSIONAL["F1"], n_opsi >= 5, f"{n_opsi} pilihan variabel"),
           ("F2", FUNGSIONAL["F2"], hover_ok, "hovertemplate terpasang pada semua grafik"),
           ("F3", FUNGSIONAL["F3"], "toImageButtonOptions" in config, "tombol ekspor PNG pada toolbar"),
           ("N1", NONFUNGSIONAL["N1"], secs < 2, f"{secs:.2f} detik"),
           ("N2", NONFUNGSIONAL["N2"], kontras_ok, "lihat output/kontras_warna.csv"),
           ("N3", NONFUNGSIONAL["N3"], size_mb < limit, f"{size_mb:.2f} MB (batas {limit} MB)")]
    df = pd.DataFrame([{"kode": k, "kebutuhan": t, "terpenuhi": "YA" if ok else "TIDAK", "bukti": b} for k, t, ok, b in cek])
    df.to_csv(f"{OUT}/verifikasi_kebutuhan.csv", index=False); print(df.to_string(index=False))
    print("Catatan: pemeriksaan ini hanya proksi teknis. Kenyamanan sebenarnya hanya dapat dipastikan lewat uji coba dengan pengguna nyata.")
    SUMMARY["Verifikasi kebutuhan"] = f"{(df.terpenuhi == 'YA').sum()} dari {len(df)} kebutuhan terpenuhi (pemeriksaan teknis, bukan pengganti uji pengguna)"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/data.csv")
    ap.add_argument("--usability", default="data/usability.csv", help="CSV hasil uji coba nyata (opsional)")
    ap.add_argument("--offline", action="store_true", help="sertakan plotly.js di HTML (file besar, bisa dibuka tanpa internet)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); pd.set_option("display.width", 170, "display.max_columns", 20)
    d = load_data(a.data); print(f"Data: {len(d)} mahasiswa (Dropout vs Graduate), dropout = {d.dropout.mean():.1%}")
    print("\n== 1) PERSONA, SKENARIO, KEBUTUHAN =="); modul1_persona()
    print("\n== 2) GRAFIK BURUK VS BAIK =="); modul2_grafik(d)
    print("\n== 3) KONTRAS WARNA (WCAG) =="); kontras_ok = modul3_kontras()
    print("\n== 4) USABILITY TESTING =="); modul4_usability(a.usability)
    print("\n== 5) CHECKLIST HEURISTIK NIELSEN =="); modul5_heuristik()
    print("\n== 6) DASHBOARD INTERAKTIF =="); fig, secs, size_mb, config = modul6_dashboard(d, a.offline)
    print("\n== 7) VERIFIKASI KEBUTUHAN =="); modul7_verifikasi(fig, secs, size_mb, config, kontras_ok, a.offline)
    md = ["# Ringkasan Hasil (dibuat otomatis)\n"] + [f"- **{k}:** {v}" for k, v in SUMMARY.items()]
    open(f"{OUT}/ringkasan.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    
