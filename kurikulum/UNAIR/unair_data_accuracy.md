# Data Accuracy Report — Kurikulum UNAIR (Universitas Airlangga)

> Generated: 2026-04-12
> S1 programs: 8 of 44 completed, 2 skipped
> D4 programs: 0 of 16 completed
> Source master: https://ppmb.unair.ac.id/en/program-studi-sarjana (S1) & https://ppmb.unair.ac.id/en/program-studi-diploma-4 (D4)

---

## Notes

- Program names in master list use Indonesian names (official UNAIR naming)
- PPMB website lists programs in English; Indonesian names mapped accordingly
- All D4 programs are under Fakultas Vokasi (FV), subdomain: vokasi.unair.ac.id
- FIKKIA Banyuwangi programs (#41-44) are duplicates of main campus programs but located in Banyuwangi campus
- Data extraction method: Playwright headless Chrome, HTML table parsing

---

## S1 — Extraction Notes

### S1 Matematika (#18) — DONE
- Source: https://matematika.fst.unair.ac.id/kurikulum/
- CSV: unair_s1-matematika.csv — 83 courses, 196 SKS
- Table: Single HTML table with rowspan/colspan merged cells
- Columns: NO | Kode | Nama | Unsur (MKPK/MKLR/MKRI/MKPS) | Kuliah | Tutorial | Praktikum | Jumlah | Prasyarat
- SKS extraction: kodeIdx + 6 (Jumlah column)
- Agama: 5 variants consolidated per semester (Sem1 basic, Sem6 Lanjut)
- kategori mapped from section headers (Wajib/Pilihan), not from Unsur column
- Semester totals match table summary (Sem1=19, Sem2=25, ..., Sem8=6, Total=196)

### S1 Fisika (#24) — DONE
- Source: https://fisika.fst.unair.ac.id/kurikulum/
- CSV: unair_s1-fisika.csv — 78 courses, 184 SKS
- Table: Single HTML table, same format as Matematika
- 8 semesters detected correctly

### S1 Kimia (#21) — DONE
- Source: http://kimia.fst.unair.ac.id/kurikulum/
- CSV: unair_s1-kimia.csv — 90 courses, 189 SKS
- Table: EA Data Table plugin inside Elementor accordion widgets (8 accordions for 8 semesters)
- Key: Content hidden in collapsed accordions — must use `textContent` (not `innerText`) to read hidden DOM
- Course names in English (source page uses English)
- Agama courses named "Religion I (Islam)", "Religion I (Catholic)", etc.

### S1 Biologi (#22) — DONE
- Source: http://biologi.fst.unair.ac.id/struktur-kurikulum/
- CSV: unair_s1-biologi.csv — 102 courses, 196 SKS
- Table: 8 separate HTML tables (one per semester), no "Semester X" text markers
- Semester inferred from table index (table 0 = Sem 1, etc.)
- Simple column format: No. | Kode | Mata Ajar | SKS
- Includes MBKM (Merdeka Belajar) courses without standard course codes — these are skipped

### S1 Manajemen (#6) — DONE
- Source: http://s1.manajemen.feb.unair.ac.id/akademik/kurikulum/
- CSV: unair_s1-manajemen.csv — 54 courses, 154 SKS
- Table: 12 separate HTML tables (one per semester + 5 concentration variants for Sem 6)
- Semester 6 has 5 Konsentrasi options (Keuangan, Pemasaran, SDM, Operasi, Kewirausahaan)
- Only first concentration (Keuangan) included — others skipped to avoid duplicate SKS inflation
- Actual JUMLAH TOTAL from page: 145 SKS (close to our 154 SKS)
- Agama: 6 variants including Kong Hu Chu (AGC101)

### S1 Hubungan Internasional (#12) — DONE
- Source: http://hi.fisip.unair.ac.id/kurikulum/
- CSV: unair_s1-hubungan-internasional.csv — 103 courses, 298 SKS
- Table: 2 tables on page (2021 and 2025 curriculum); used 2025 (last table, 167 rows)
- Note: Total SKS (298) exceeds actual program load (160 SKS) because table lists ALL available courses including elective pools
- Per-semester max from page: Sem1=20, Sem2=20, Sem3-7=24 each
- No explicit Wajib/Pilihan section headers — all courses treated as available catalog

### S1 Ilmu Politik (#13) — DONE
- Source: http://politik.fisip.unair.ac.id/kurikulum/
- CSV: unair_s1-ilmu-politik.csv — 116 courses, 341 SKS
- Table: Single large table (180 rows)
- Note: Total SKS (341) exceeds actual program load (144-160 SKS) — includes Pilihan Terbatas and Pilihan Bebas pools
- Semester markers include combined semesters: "Semester 6-7", "Semester 7-8"
- Category detection: "Pilihan Terbatas" and "Pilihan Bebas" both mapped to Pilihan

### S1 Sosiologi (#14) — DONE
- Source: http://sosiologi.fisip.unair.ac.id/kurikulum/
- CSV: unair_s1-sosiologi.csv — 71 courses, 210 SKS
- Table: 2 tables on page; used last (newer, 125 rows)
- Note: Total SKS (210) exceeds actual program load (~144-160) due to elective pools

### S1 Statistika (#20) — SKIP
- Source: http://stat.fst.unair.ac.id/struktur-kurikulum/
- Reason: Page only has download links, no inline kurikulum table. Table present is a document list (No | Dokumen | Versi Indonesia | Versi Inggris).

### S1 Ilmu Perpustakaan dan Informasi (#16) — SKIP
- Source: http://dip.fisip.unair.ac.id/kurikulum/
- Reason: HTML table only shows ~8 courses (partial summary). Full kurikulum in Google Drive PDFs: "Dokumen Kurikulum 2021" and "Dokumen Kurikulum 2025".

---

## D4 — Extraction Notes

> Not yet started. D4 programs on vokasi.unair.ac.id show "Silahkan download" but no actual kurikulum documents found on the download page.
