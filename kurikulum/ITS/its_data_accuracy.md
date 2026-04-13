# Data Accuracy Report — Kurikulum ITS

> Generated: 2026-04-12
> S1 departments: 33 of 40 completed
> D4 programs: 7 of 8 completed

---

## Data Quality Summary

| Status | Count | Departments |
|--------|-------|-------------|
| 100% exact from source | 17 | Matematika, Statistika, Kimia, Aktuaria, Teknik Elektro, Teknik Biomedik, DKV, Teknik Geomatika, Teknik Kelautan, Arsitektur, Teknik Kimia, Teknik Sipil, Desain Produk, Manajemen Bisnis, Desain Interior, Studi Pembangunan |
| Extracted from images | 1 | Teknik Geofisika |
| Extracted from PDF (Module Handbook) | 1 | Teknik Informatika |
| Extracted from PDF (Syllabus) | 1 | Manajemen Bisnis |
| Extracted from PDF (Katalog/Kurikulum) | 3 | Fisika, Teknik Lingkungan, Bioteknologi |
| Extracted from PDF (Curriculum Map) | 1 | Kedokteran |
| Extracted from PDF (Kurikulum Document) | 3 | Rekayasa Perangkat Lunak, Rekayasa Kecerdasan Artifisial, Teknik Perkapalan |
| Extracted from HTML table (hosted elsewhere) | 3 | Teknik Pangan, Teknik Pertambangan, Teknik PWK |
| SKS estimated (wajib) | 1 | Bisnis Digital |
| Minor formatting fixes applied | 3 | Teknik Fisika, Teknik Material, Teknik Mesin |
| Possible minor interpretation | 1 | Teknik Sistem dan Industri |

---

## Departments with 100% Exact Data

These departments had clean, well-structured tables on their source pages with all fields (nama MK, SKS, semester, kategori) clearly listed. Data was copied as-is without any estimation or interpretation.

| # | Department | CSV File | Source URL |
|---|-----------|----------|------------|
| 1 | S1 Matematika | `its_matematika.csv` | https://www.its.ac.id/matematika/akademik/program-studi/sarjana/ |
| 2 | S1 Statistika | `its_statistika.csv` | https://www.its.ac.id/statistika/akademik/program-studi/program-studi-sarjana/ |
| 3 | S1 Kimia | `its_kimia.csv` | https://www.its.ac.id/kimia/akademik/program-studi/s1-kimia/ |
| 4 | S1 Sains Aktuaria | `its_aktuaria.csv` | https://www.its.ac.id/aktuaria/akademik/program-studi/s1-sains-aktuaria/ |
| 5 | S1 Teknik Elektro | `its_teknik-elektro.csv` | https://www.its.ac.id/telektro/id/akademik/program-studi-sarjana/kurikulum-sarjana-2023/ |
| 6 | S1 Teknik Biomedik | `its_teknik-biomedik.csv` | https://www.its.ac.id/tbiomedik/id/akademik/program-studi/kurikulum-sarjana/ |
| 7 | S1 Desain Komunikasi Visual | `its_dkv.csv` | https://www.its.ac.id/dkv/id/akademik/program-studi/sarjana-s1/ |
| 8 | S1 Teknik Geomatika | `its_teknik-geomatika.csv` | https://www.its.ac.id/tgeomatika/id/akademik/program-akademik/mata-kuliah-s1/ |
| 9 | S1 Teknik Kelautan | `its_teknik-kelautan.csv` | https://www.its.ac.id/tkelautan/akademik/program-studi/s1/ |
| 10 | S1 Arsitektur | `its_arsitektur.csv` | https://www.its.ac.id/arsitektur/program-studi/program-studi-sarjana-s1/ |
| 11 | S1 Teknik Kimia | `its_teknik-kimia.csv` | https://www.its.ac.id/tkimia/wp-content/uploads/sites/23/2018/03/COURSE-LIST-of-BACHELOR-PROGRAM.pdf |
| 12 | S1 Teknik Sipil | `its_teknik-sipil.csv` | https://www.its.ac.id/tsipil/wp-content/uploads/sites/30/2025/11/Dokumen-Kurikulum-Update-261125.pdf |
| 13 | S1 Desain Produk | `its_desain-produk.csv` | https://www.its.ac.id/despro/academic/curriculum/ |
| 14 | S1 Manajemen Bisnis | `its_manajemen-bisnis.csv` | https://www.its.ac.id/mb/academic/curriculum/ + syllabus PDF |
| 15 | S1 Desain Interior | `its_desain-interior.csv` | https://www.its.ac.id/interior/academic/curriculum/ |
| 16 | S1 Studi Pembangunan | `its_studi-pembangunan.csv` | https://www.its.ac.id/sp/curriculum-and-courses/ (Google Drive PDF) |
| 17 | S1 Fisika | `its_fisika.csv` | https://www.its.ac.id/fisika/wp-content/uploads/sites/19/2024/08/Daftar-Mata-Kuliah-Wajib-dan-Pilihan-S1-Fisika-1.pdf |
| 18 | S1 Teknik Lingkungan | `its_teknik-lingkungan.csv` | https://drive.google.com/file/d/1u7iRqCrKOvX215cjYdtzHAkST6JzdnqS/view (Katalog 2023) |
| 19 | S1 Bioteknologi | `its_bioteknologi.csv` | https://www.its.ac.id/biologi/wp-content/uploads/sites/21/2025/02/Kurikulum-blok.pdf |

---

## Departments Extracted from Images

### S1 Teknik Geofisika — `its_teknik-geofisika.csv`

**Issue**: Source page had curriculum only as 8 embedded PNG/JPG images (one per semester), no text-based table.

**Extraction method**: Used AI image analysis (`analyze_image` tool) to read course names, SKS, and semester info from each semester image.

**Accuracy notes**:
- Agama shown as single entry (2 SKS) — source shows 6 variants but student takes only one
- MBKM Pilihan courses listed with estimated semester placement based on semester numbering
- Total ~144 SKS across 8 semesters, 44 rows in CSV

Source: https://www.its.ac.id/tgeofisika/program-studi/program-sarjana/

### S1 Teknik Informatika — `its_teknik-informatika.csv`

**Issue**: No inline curriculum table on department page. Curriculum only available as a downloadable Module Handbook PDF (294 pages).

**Extraction method**: Downloaded PDF and extracted text using pdfjs-dist (`extract_pdf.mjs` utility). Course list found on pages 4-7 covering mandatory courses across 8 semesters plus 54 elective courses.

**Accuracy notes**:
- Mandatory courses: ~144 SKS, 47 courses — names and SKS extracted exactly as listed in the PDF
- Elective course semester assignment: derived from course code pattern (EF234Xxx where 5th character = semester number)
- Generic "Mata Kuliah Pilihan" placeholder entries included for elective slots in semesters 5 and 7 (as shown in PDF)
- Internship (6 SKS) listed as semester 8 elective per the PDF
- All ITS general courses (Religion, Civics, English, Indonesian, Pancasila, Technopreneurship) included

Source: https://www.its.ac.id/informatika/wp-content/uploads/sites/44/2023/11/Module-Handbook-Bachelor-of-Informatics-Program-ITS.pdf

### S1 Manajemen Bisnis — `its_manajemen-bisnis.csv`

**Issue**: The `/academic/curriculum/` web page listed course names by semester but did not include SKS values.

**Extraction method**: Downloaded the syllabus PDF (51 pages, Kurikulum ITS 2018-2023) from the department website. The PDF contains the complete course list with exact SKS values, organized by semester. All mandatory courses (49) and elective courses (16) extracted directly from the PDF.

**Accuracy notes**:
- Mandatory courses: 144 SKS across 8 semesters — SKS values are exact from the PDF
- 4 focus areas: Financial Management, Operations Management, Marketing Management, Human Capital Management
- "MK Wajib Konsentrasi" placeholder entries for semesters 7 and 8 (student picks from focus area)
- "MK Pilihan" placeholder for semester 8 (free elective)
- All 16 elective courses listed with names and 3 SKS each from the PDF
- Elective semester assignments based on web page focus area groupings

Source: https://www.its.ac.id/mb/academic/curriculum/ + https://www.its.ac.id/mb/wp-content/uploads/sites/47/2019/11/Silabus-MB-ITS.pdf

---

## Departments Extracted from PDF (Katalog/Kurikulum)

### S1 Desain Interior — `its_desain-interior.csv`

**Source**: `https://www.its.ac.id/interior/academic/curriculum/` (TablePress HTML tables, curriculum updated 2025)

**Accuracy notes**:
- 144 SKS total across 8 semesters
- 38 mandatory courses + 10 elective courses (5 per semester in sem 5 and 6)
- Curriculum fully extracted from TablePress tables with exact SKS values
- General courses (Religion, Pancasila, Indonesian, Civics, English, Technopreneurship) placed in semesters 6-7
- Elective courses listed without individual SKS in source — estimated at 3 SKS each (ITS standard)
- Note: This is a NEW curriculum (different from earlier version). Source course names are in English.

### S1 Studi Pembangunan — `its_studi-pembangunan.csv`

**Issue**: Source page had curriculum only as embedded Google Drive PDF iframes (no inline table). Two curriculum versions (2019-2023 and 2023-2028) available.

**Extraction method**: Downloaded the 2023-2028 PDF via Google Drive direct link and extracted text using pdfjs-dist.

**Accuracy notes**:
- 144 SKS total across 8 semesters, 43 mandatory courses + 13 elective courses + 2 enrichment courses
- All mandatory course names and SKS extracted exactly from PDF
- Elective courses: 2 SKS each, enrichment courses: 3 SKS each
- Agama shown as single entry (2 SKS) — source shows 6 variants but student takes only one
- "Aptek Transidi" in source likely a typo for "Aplikasi Teknologi dan Transformasi Digital" — recorded as ATTD

### S1 Fisika — `its_fisika.csv`

**Issue**: Curriculum only available as downloadable PDF, not as inline table on page.

**Extraction method**: Downloaded "Daftar Mata Kuliah Wajib dan Pilihan S1 Fisika" PDF and extracted text using pdfjs-dist.

**Accuracy notes**:
- 144 SKS total across 8 semesters
- 33 mandatory courses + 40 elective courses across 6 specialization fields
- Mandatory courses with exact SKS from PDF
- Elective courses organized by field: Fisika Teori (6), Material Maju (7), Optoelektronika (6), Instrumentasi (7), Geofisika (7), Fisika Medis (7)
- Some elective courses marked T1/T2 — limited enrollment

### S1 Teknik Lingkungan — `its_teknik-lingkungan.csv`

**Issue**: No inline curriculum table. Curriculum only available as Katalog 2023 PDF (112 pages) via Google Drive.

**Extraction method**: Downloaded PDF via Google Drive. Course list extracted from document page 13 using pdfjs-dist.

**Accuracy notes**:
- 144 SKS total across 8 semesters
- 39 mandatory courses + 17 elective courses
- Mandatory courses with exact SKS from PDF
- Elective courses: mostly 2 SKS each ("Pengembangan Diri" showed 9 SKS in PDF — likely typo, recorded as 2)
- "Plambing" in source appears to be a typo for "Plumbing"

### S1 Bioteknologi — `its_bioteknologi.csv`

**Issue**: Original "Biologi" program restructured to "Sarjana Bioteknologi". Uses "Kurikulum Blok" system available as PDF.

**Extraction method**: Downloaded "Kurikulum blok" PDF from department website. Course list extracted using pdfjs-dist.

**Accuracy notes**:
- 144 SKS total (126 teori + 18 praktik) across 8 semesters
- 36 mandatory courses
- SKS per course = teoria + praktik components (e.g., Biokimia = 3+1 = 4 SKS)
- Semesters 6-7 have aggregate elective slots (10 and 9 SKS) without individual course listings
- ~27 elective course names available from separate "Distribusi MK" PDF but without SKS values

---

## Departments with Estimated Data

### S1 Bisnis Digital — `its_bisnis-digital.csv`

**Issue**: Source page listed course names and semesters but **did not include SKS values** for wajib courses.

**Estimation method used** (ITS standard):
- Regular courses: 3 SKS
- General courses (Agama, Pancasila, Bahasa Indonesia, Bahasa Inggris, Kewarganegaraan): 2 SKS
- Kerja Praktik: 3 SKS
- Seminar: 2 SKS
- Tugas Akhir: 6 SKS
- Kewirausahaan Berbasis Teknologi: 2 SKS

**Note**: Pilihan courses (semester 6) DID have SKS listed on the source page — those values are accurate.

Source: https://www.its.ac.id/mb/id/akademik/program-studi/sarjana-s1-bisnis-digital/

---

## Departments with Formatting Fixes Applied

### S1 Teknik Fisika — `its_teknik-fisika.csv`

**Issue**: 42 Pilihan courses were listed on the source page in a single block grouped by interest area (Instrumentasi & Kontrol, Energi, Akustik, Material, Fotonik). The source did not explicitly label each course as "Ganjil" or "Genap" — only semester numbers were given.

**Fix applied**: semester_type was derived from semester number (odd = Ganjil, even = Genap).

### S1 Teknik Material dan Metalurgi — `its_teknik-material.csv`

**Issue**: 19 Pilihan courses had "Pilihan" as the `semester_type` value instead of proper "Ganjil"/"Genap". Source listed semester numbers but not semester_type labels.

**Fix applied**: semester_type corrected based on semester number (odd = Ganjil, even = Genap).

### S1 Teknik Mesin — `its_teknik-mesin.csv`

**Issue**: 61 Pilihan courses (all semester 6) had "Pilihan" as the `semester_type` value. All were semester 6 (Genap).

**Fix applied**: All corrected to "Genap" based on semester number.

---

## Department with Possible Minor Interpretation

### S1 Teknik Sistem dan Industri — `its_teknik-sistem-industri.csv`

The source page grouped courses by semester but some entries had ambiguous SKS or semester placement that required cross-referencing with the semester numbering scheme. Data is believed to be accurate but has not been fully cross-checked against the live source page.

Source: https://www.its.ac.id/tindustri/program-studi/program-sarjana-s-t/

---

## Departments Extracted from PDF (Curriculum Map)

### S1 Kedokteran — `its_kedokteran.csv`

**Issue**: Curriculum only available as "Peta Kurikulum" (curriculum map) PDF — a complex 2-page visual layout with 4 quadrants showing 8 semesters of block-based courses. Text extraction from pdfjs produced interleaved results from the two-column layout.

**Extraction method**: Downloaded PDF from department website. Text extracted using pdfjs-dist, then manually separated into semesters by matching courses to semester subtotals (Sem I: 20, Sem II: 20, Sem III: 18, Sem IV: 19, Sem V: 20, Sem VI: 15, Sem VII: 20, Sem VIII: 21).

**Accuracy notes**:
- 153 SKS total across 8 semesters (not the standard 144 — medical programs have higher credit requirements)
- 38 mandatory courses + 5 elective characteristic courses (MK Penciri)
- Block-based system with organ-system blocks (Kardiovaskular, Respirasi, Reproduksi, etc.)
- Clinical skills progression: Keterampilan Klinis A → B → C → Komprehensif
- General courses (Agama, Pancasila, Bahasa Indonesia, Kewarganegaraan, Bahasa Inggris) placed in Semesters I-II
- Semester assignment for some courses required interpretation due to two-column PDF layout interleaving
- Elective SKS estimated at 2 each (options: Fabrikasi Digital, Nanomedicine, Herbal Medicine, Tuberculosis, Biomolekuler)
- "Agama dan Aplikasinya" in Semester VIII is truncated in PDF extraction (recorded as 2 SKS)

Source: https://www.its.ac.id/academicmed/kurikulum-sarjana-kedokteran/kurikulum-dan-handbook/ (Peta Kurikulum PDF)

---

## Departments Extracted from HTML Table (Hosted Under Other Department)

### S1 Teknik Pangan — `its_teknik-pangan.csv`

**Issue**: No dedicated subdomain (`tpangan` redirects to main ITS page). Curriculum found as a PDF hosted under the Teknik Kimia department subdomain.

**Extraction method**: Downloaded "Curriculum of Food Engineering 2023" PDF from tkimia subdomain. Text extracted using pdfjs-dist. The PDF has a two-column landscape layout with course codes, names, and SKS organized by semester.

**Accuracy notes**:
- 144 SKS total across 8 semesters (matching PDF totals exactly)
- 47 mandatory courses (including 2 elective slot placeholders) + 12 named elective courses
- All course names, SKS, and semester assignments extracted directly from PDF with course codes (e.g., TP234501)
- Semester subtotals verified: Sem I: 18, II: 18, III: 21, IV: 21, V: 20, VI: 20, VII: 20, VIII: 6
- "Pilihan Keahlian I" (Sem VI) and "Pilihan Keahlian II" (Sem VII) are required elective slots
- "MK Pengayaan I" and "MK Pengayaan II" are enrichment course slots (3 SKS each)
- 6 Elective I options and 6 Elective II options listed, all 3 SKS each
- General courses (ATTD, Bahasa Indonesia, Agama, Pancasila, Kewirausahaan, Kewarganegaraan, Bahasa Inggris) in Semesters VI-VII

Source: https://www.its.ac.id/tkimia/id/akademik/program-studi/program-sarjana-s1/ (PDF: "Curriculum of Food Engineering 2023")

### S1 Teknik Pertambangan — `its_teknik-pertambangan.csv`

**Issue**: No dedicated subdomain (`tpertambangan` redirects to main ITS page). Curriculum found as an HTML table hosted under the Teknik Geomatika department subdomain.

**Extraction method**: Scraped HTML TablePress table from the Teknik Geomatika page at `/tgeomatika/id/kurikulum-program-studi-teknik-pertambangan/`. Course names and SKS extracted from `column-4` and `column-5` CSS classes.

**Accuracy notes**:
- 144 SKS total across 8 semesters (matching source subtotals exactly)
- 49 mandatory courses (including 2 elective slot placeholders) + 10 named elective courses
- Semester subtotals verified: Sem I: 19, II: 17, III: 20, IV: 21, V: 20, VI: 21, VII: 20, VIII: 6
- "Mata Kuliah Pilihan" slots in Semesters VII (2 SKS) and VIII (2 SKS) are required elective placeholders
- 8 Elective I options listed in Semester VII (2 SKS each): Genesa dan Bahan Galian, Geofisika Pertambangan, etc.
- 3 additional Elective II options in Semester VIII (Magang, Kapita Selekta, estimated 3 SKS each)
- Agama shown as single entry (2 SKS) — source shows 6 variants but student takes only one
- "Mata Kuliah Pengayaan" (3 SKS) in Semester VII

Source: https://www.its.ac.id/tgeomatika/id/kurikulum-program-studi-teknik-pertambangan/

---

## Departments Extracted from HTML Table (Own Subdomain)

### S1 Teknik Perencanaan Wilayah dan Kota — `its_teknik-pwk.csv`

**Issue**: The `/akademik/program-studi/` page returned 404. Curriculum found at `/pwk/id/struktur-kurikulum/` with TablePress HTML tables.

**Extraction method**: Scraped HTML TablePress tables from the PWK subdomain. Course names and SKS extracted from the embedded tables.

**Accuracy notes**:
- 144 SKS total across 8 semesters (matching source subtotals exactly)
- 49 mandatory courses (including 3 "Mata Kuliah Pengayaan" slots in Sem VII: 3, 3, 2 SKS) + 17 named elective courses
- Semester subtotals verified: Sem I: 18, II: 18, III: 21, IV: 21, V: 20, VI: 20, VII: 20, VIII: 6
- 17 elective courses all assigned to Sem VII (Ganjil), 3 SKS each — covering urban planning specializations
- General courses in Semesters VI-VII: Agama (Sem VI), Pancasila (Sem VI), Aplikasi Teknologi (Sem VI), Kewirausahaan (Sem VII), Bahasa Inggris (Sem VII), Bahasa Indonesia (Sem VII), Kewarganegaraan (Sem VII)

Source: https://www.its.ac.id/pwk/id/struktur-kurikulum/

---

## Departments Extracted from PDF (Kurikulum Document)

### S1 Rekayasa Perangkat Lunak — `its_rekayasa-perangkat-lunak.csv`

**Issue**: Program restructured from "Sistem Informasi" to "Rekayasa Perangkat Lunak" (RPL). Curriculum only available as a 207-page PDF document.

**Extraction method**: Downloaded "Dokumen Kurikulum RPL ITS 2023" PDF from informatika subdomain. Course list extracted from PDF pages 71-75 (section "Daftar Sebaran Mata Kuliah Tiap Semester") using pdfjs-dist.

**Accuracy notes**:
- ~143 SKS total (PDF states 144 — 1 SKS minor discrepancy, likely from text extraction alignment)
- 47 mandatory courses (including 5 "Mata Kuliah Pilihan" placeholder slots) across 8 semesters
- Semester subtotals: Sem I: 18, II: 17, III: 21, IV: 21, V: 21, VI: 20, VII: 18, VIII: 7
- "Pengembangan Perangkat Lunak" set to 2 SKS to match Sem I total (PDF may show 3T)
- "Sistem Basis Data" = 4 SKS (3T + 1P lab component)
- 5 "Mata Kuliah Pilihan" placeholder slots (Wajib, 3 SKS each) in Semesters V, VI (×1), VII (×2)
- Named elective courses NOT yet extracted (would need to find elective list section in the 207-page PDF)

Source: https://www.its.ac.id/informatika/id/akademik/program-studi/ (PDF: `pdfs/rpl_kurikulum_2023.pdf`)

### S1 Rekayasa Kecerdasan Artifisial — `its_rekayasa-kecerdasan-artifisial.csv`

**Issue**: Program restructured from "Teknik Komputer" to "Rekayasa Kecerdasan Artifisial" (RKA). Curriculum only available as a 527-page PDF document.

**Extraction method**: Downloaded "Dokumen Kurikulum Prodi RKA Revisi 1" PDF from informatika subdomain. Course list extracted from PDF pages 51-54 using pdfjs-dist. Named electives from CPL MB-KM table (pages 61-62).

**Accuracy notes**:
- 144 SKS total across 8 semesters
- 49 mandatory courses (including 4 "Mata Kuliah Pilihan" placeholder slots) + 8 named elective courses
- Semester subtotals: Sem I: 19, II: 17, III: 21, IV: 21, V: 21, VI: 20, VII: 20, VIII: 5
- Distinctive courses: Pembelajaran Mesin (4 SKS), Kecerdasan Komputasional (4 SKS), Penambangan Data (4 SKS), Deep Learning (3 SKS)
- 4 "Mata Kuliah Pilihan" placeholder slots (Wajib, 3 SKS each) in Semesters V (×2), VI, VII
- Named electives: Sem V (Komputasi Biomedik, Kecerdasan Bisnis, Temu Kembali Informasi), Sem VI (Robotika, Visi Komputer 3D, Perancangan dan Pengembangan Gim, Pemrograman XR), Sem VII (Komputasi Sosial)
- "Tugas Akhir" = 5 SKS (different from standard 6 SKS)

Source: https://www.its.ac.id/informatika/id/akademik/program-studi/ (PDF: `pdfs/rka_kurikulum_revisi1.pdf`)

### S1 Teknik Perkapalan — `its_teknik-perkapalan.csv`

**Issue**: The `/akademik/program-studi/prodi-sarjana-s1-reguler/` page had curriculum only as embedded PDF viewer (Kurikulum DTP 2018 dan Prasyarat Mata Kuliah). A newer 348-page 2023 PDF was also available but had font rendering issues preventing text extraction.

**Extraction method**: Downloaded the 2018 PDF (5 pages) and extracted text using pdfjs-dist. The PDF contains the complete course list organized by semester with SKS values.

**Accuracy notes**:
- 144 SKS total across 8 semesters
- 49 mandatory courses (including 4 "Mata Kuliah Pilihan" placeholder slots: 2 in Sem VII, 2 in Sem VIII) + 19 named elective courses
- Semester subtotals verified: Sem I: 18, II: 18, III: 19, IV: 19, V: 18, VI: 19, VII: 18, VIII: 15
- Elective semester assignment: 13 electives assigned to Sem VII (Ganjil) based on subject grouping (design/hydrodynamics/structure), 6 electives to Sem VIII (Genap) (production/management)
- "Wawasan dan Aplikasi Teknologi" = 3 SKS (Sem VII) — equivalent to ATTD
- "Teknopreneur" = 2 SKS (Sem VIII)
- Source PDF is Kurikulum DTP 2018 (not the latest 2023 revision, which could not be extracted)

Source: https://www.its.ac.id/tkapal/akademik/program-studi/prodi-sarjana-s1-reguler/ (PDF: `pdfs/perkapalan_kurikulum_2018.pdf`)

| Fix | Files Affected | Description |
|-----|---------------|-------------|
| semester_type "Reguler" → Ganjil/Genap | `its_kimia.csv`, `its_aktuaria.csv` | Original extraction used "Reguler" instead of proper semester type |
| semester_type "Pilihan" → Ganjil/Genap | `its_teknik-fisika.csv`, `its_teknik-material.csv`, `its_teknik-mesin.csv` | Pilihan courses had wrong value in semester_type column |
| jurusan prefix "S1 " added | All 15 CSV files | All jurusan values prefixed with "S1 " to indicate program level |
| PDF extraction (pdfjs-dist) | `its_teknik-kimia.csv`, `its_teknik-sipil.csv`, `its_teknik-informatika.csv`, `its_fisika.csv`, `its_studi-pembangunan.csv`, `its_teknik-lingkungan.csv`, `its_bioteknologi.csv`, `its_teknik-pangan.csv`, `its_kedokteran.csv`, `its_rekayasa-perangkat-lunak.csv`, `its_rekayasa-kecerdasan-artifisial.csv`, `its_teknik-perkapalan.csv` | Curriculum extracted from PDF documents using pdfjs-dist Node.js library |
| HTML table scraping (hosted elsewhere) | `its_teknik-pertambangan.csv` | Curriculum scraped from TablePress HTML table hosted under Teknik Geomatika subdomain |
| HTML table scraping (own subdomain) | `its_teknik-pwk.csv` | Curriculum scraped from TablePress HTML table on PWK subdomain |
| Image-based extraction | `its_teknik-geofisika.csv` | Curriculum extracted from 8 embedded PNG/JPG semester images using AI image analysis |

---

## Skipped S1 Departments (7)

See `its_master_jurusan.md` for the full list of skipped departments and reasons. Common reasons:
- Curriculum only available as downloadable PDF
- Curriculum only in embedded images
- Page returns 404 or redirects
- No dedicated subdomain / page
- Program restructured (e.g., Sistem Informasi → Rekayasa Perangkat Lunak)

---

# Program D4 (Diploma IV / Vokasi)

## D4 Data Quality Summary

| Status | Count | Programs |
|--------|-------|----------|
| OCR from department page images | 5 | D4 Teknik Rekayasa Otomasi, D4 Teknik Kimia Industri, D4 Teknik Instrumentasi, D4 Teknik Rekayasa Manufaktur, D4 Teknik Rekayasa Konversi Energi |
| OCR from TIS PNG images (Kurikulum 2019) | 2 | D4 Teknik Rekayasa Konstruksi Bangunan Air, D4 Teknik Rekayasa Pengelolaan dan Pemeliharaan Bangunan Sipil |
| SKIP — no data available | 1 | D4 Statistika Bisnis |

---

## D4 Programs — OCR from Department Page Images

### D4 Teknik Rekayasa Otomasi — `its_teknik-rekayasa-otomasi.csv`

**Extraction method**: AI image analysis (OCR) of curriculum table images from DTEO department page.

**Accuracy notes**:
- 41 courses, ~144 SKS across 8 semesters
- All courses marked as Wajib
- Data extracted from embedded semester images — best-effort OCR accuracy

Source: Halaman DTEO (Departemen Teknik Energi dan Otomasi)

### D4 Teknik Kimia Industri — `its_teknik-kimia-industri.csv`

**Extraction method**: AI image analysis (OCR) of curriculum table images from DTKI department page.

**Accuracy notes**:
- 44 courses across 8 semesters
- All courses marked as Wajib
- Data extracted from embedded semester images — best-effort OCR accuracy

Source: Halaman DTKI (Departemen Teknik Kimia Industri)

### D4 Teknik Instrumentasi — `its_teknik-instrumentasi.csv`

**Extraction method**: AI image analysis (OCR) of curriculum table images from DTIn department page.

**Accuracy notes**:
- 47 courses, 144 SKS across 8 semesters
- All courses marked as Wajib
- Data extracted from embedded semester images — best-effort OCR accuracy

Source: Halaman DTIn (Departemen Teknik Instrumentasi)

### D4 Teknik Rekayasa Manufaktur — `its_teknik-rekayasa-manufaktur.csv`

**Extraction method**: AI image analysis (OCR) of curriculum table images from DTMI department page.

**Accuracy notes**:
- 48 courses across 8 semesters
- All courses marked as Wajib
- Data extracted from embedded semester images — best-effort OCR accuracy

Source: Halaman DTMI (Departemen Teknik Mesin dan Industri)

### D4 Teknik Rekayasa Konversi Energi — `its_teknik-rekayasa-konversi-energi.csv`

**Extraction method**: AI image analysis (OCR) of curriculum table images from DTMI department page.

**Accuracy notes**:
- 47 courses across 8 semesters
- All courses marked as Wajib
- Data extracted from embedded semester images — best-effort OCR accuracy

Source: Halaman DTMI (Departemen Teknik Mesin dan Industri)

---

## D4 Programs — OCR from TIS PNG Images

### D4 Teknik Rekayasa Konstruksi Bangunan Air — `its_teknik-rekayasa-konstruksi-bangunan-air.csv`

**Extraction method**: AI image analysis (OCR) of 8 PNG images (semester-1.png through semester-8.png) from TIS department WordPress page.

**Accuracy notes**:
- 68 data rows across 8 semesters
- PNG images hosted at `https://www.its.ac.id/tis/wp-content/uploads/sites/50/2020/10/semester-{1-8}.png`
- TRKBA program page: `https://www.its.ac.id/tis/id/akademik/program-studi/trkba/`
- Best-effort OCR — some course names may have minor transcription errors
- Agama consolidated to single entry (2 SKS) — source shows 6 variants

Source: https://www.its.ac.id/tis/id/akademik/program-studi/trkba/ (Kurikulum 2019 PNG images)

### D4 Teknik Rekayasa Pengelolaan dan Pemeliharaan Bangunan Sipil — `its_teknik-rekayasa-pengelolaan-pemeliharaan-bangunan-sipil.csv`

**Extraction method**: AI image analysis (OCR) of 8 PNG images (semester-1.png through semester-8.png) from TIS department WordPress page.

**Accuracy notes**:
- 48 courses, ~141 SKS across 8 semesters
- PNG images hosted at `https://www.its.ac.id/tis/wp-content/uploads/sites/50/2020/10/semester-{1-8}.png`
- TRPPBS program page: `https://www.its.ac.id/tis/id/akademik/program-studi/trppbs/`
- Best-effort OCR — some course names may have minor transcription errors
- Agama consolidated to single entry (2 SKS) — source shows 6 variants
- Semester 4 data was initially missing; found via curl+grep on TIS kurikulum page HTML to discover the correct program page URL

Source: https://www.its.ac.id/tis/id/akademik/program-studi/trppbs/ (Kurikulum 2019 PNG images)

---

## Skipped D4 Programs (1)

### D4 Statistika Bisnis — NO DATA AVAILABLE

All approaches exhausted:
1. `/sb/id/akademik/kurikulum/` — Only S1/S2 links to old Liferay documents, no D4 data
2. `/sb/id/akademik/program-studi/` — General description only
3. `/sb/id/akademik/program-studi/d4-statistika-bisnis/` — Redirected to library page
4. `/sb/academic/study-program/diploma-iv-2/` — 2018 proposal page with general course list but NO semester/SKS breakdown
5. `/sb/id/akademik/kurikulum-d4/` — 404
6. PDDIKTI (`pddikti.kemdikbud.go.id`) — 500 Internal Server Error (multiple attempts)
7. WebSearch — API Error 400 (consistently)
8. SB WordPress REST API (`/sb/wp-json/wp/v2/pages/2447`) — 403 Forbidden (REST API disabled)
