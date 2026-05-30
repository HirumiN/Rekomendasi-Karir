import os
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pgvector.sqlalchemy import Vector
import json
from dotenv import load_dotenv
import logging
from datetime import datetime

from . import models, schemas

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables for Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBED_URL = os.getenv("GEMINI_EMBED_URL") or "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
GEMINI_GEN_URL = os.getenv("GEMINI_GEN_URL") or "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

from asyncio import sleep # Added for retry mechanism

async def embed_text_with_gemini(text: str) -> List[float]:
    """Calls the Gemini embeddings model to get the embedding for a given text with retries."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY must be set in environment variables.")

    if not GEMINI_EMBED_URL:
        raise ValueError("GEMINI_EMBED_URL must be set in environment variables.")

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [{
                "text": text
            }]
        },
        "output_dimensionality": 768
    }

    logger.info(f"Sending payload to Gemini API to URL: {GEMINI_EMBED_URL}")
    logger.info(f"Payload: {json.dumps(payload, indent=2)}")

    retries = 3
    delay = 2
    for i in range(retries):
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(GEMINI_EMBED_URL, headers=headers, json=payload)
                response.raise_for_status()
                embedding_data = response.json()
                
                if "embedding" in embedding_data and "values" in embedding_data["embedding"]:
                    embedding_values = embedding_data["embedding"]["values"]
                    logger.info(f"Generated embedding with {len(embedding_values)} dimensions.")
                    return embedding_values
                else:
                    raise ValueError(f"Unexpected embedding response format from Gemini API: {embedding_data}")
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
                logger.error(f"Attempt {i+1}/{retries}: Timeout or connection error occurred while calling Gemini Embedding API: {e}")
                if i < retries - 1:
                    await sleep(delay)
                    delay *= 2
                    continue
                raise # Re-raise if all retries fail
            except httpx.HTTPStatusError as e:
                error_detail = f"Gemini Embedding API Error: {e.response.text}"
                logger.error(error_detail)
                raise ValueError(error_detail)
            except Exception as e:
                logger.error(f"An unexpected error occurred while calling Gemini Embedding API: {e}")
                raise
    raise Exception("Failed to get embedding after multiple retries.") # Should not be reached

def retrieve_similar_rags(db: Session, query_vector: List[float], top_k: int, id_user: Optional[int] = None) -> List[models.RAGSEmbedding]:
    """Performs similarity search in the database using pgvector, optionally filtered by user ID."""
    query = db.query(models.RAGSEmbedding)
    
    if id_user is not None:
        query = query.filter(models.RAGSEmbedding.id_user == id_user)

    result = query.order_by(
        models.RAGSEmbedding.embedding.l2_distance(query_vector)
    ).limit(top_k).all()
    
    return result

def augment_prompt(
    question: str, 
    context_docs: List[models.RAGSEmbedding], 
    client_local_time: Optional[datetime] = None,
    user: Optional[models.User] = None,
    user_schedules: Optional[List[models.JadwalMatkul]] = None
) -> str:
    """Constructs an augmented prompt with retrieved context, user profile, academic schedules, and optional client local time."""
    context_str = "\n\n".join([
        f"Source: {doc.source_type} (ID: {doc.source_id or doc.id_embedding})\nContent: {doc.text_original}"
        for doc in context_docs
    ])

    user_profile_context = ""
    if user:
        user_profile_context = (
            f"USER PROFILE:\n"
            f"- Nama: {user.nama}\n"
            f"- Email: {user.email}\n"
            f"- Telepon: {user.telepon or 'Tidak diisi'}\n"
            f"- Umur: {user.umur or 'Tidak diisi'} tahun\n"
            f"- Bio: {user.bio or 'Tidak diisi'}\n"
            f"- Lokasi: {user.lokasi or 'Tidak diisi'}\n"
            f"- Universitas: {user.universitas or 'Tidak diisi'}\n"
            f"- Jurusan: {user.jurusan or 'Tidak diisi'}\n"
            f"- Semester Saat Ini: {user.semester_sekarang or 'Tidak diisi'}\n"
            f"- Target Karir: {user.target_karir or 'Tidak diisi'}\n"
            f"- Minat: {user.minat or 'Tidak diisi'}\n"
            f"- Keterampilan: {user.keterampilan or 'Tidak diisi'}\n"
            f"- Kepribadian: {user.kepribadian or 'Tidak diisi'}\n"
            f"- Gaya Belajar: {user.gaya_belajar or 'Tidak diisi'}\n"
            f"- Waktu Luang: {user.waktu_luang or 'Tidak diisi'}\n"
            "------------------\n\n"
        )

    schedules_context = ""
    if user_schedules:
        schedules_list = []
        # Sort schedules by day and start time
        day_order = {"Senin": 1, "Selasa": 2, "Rabu": 3, "Kamis": 4, "Jumat": 5, "Sabtu": 6, "Minggu": 7}
        sorted_schedules = sorted(
            user_schedules,
            key=lambda x: (day_order.get(x.hari, 8), str(x.jam_mulai))
        )
        
        user_sem = int(user.semester_sekarang) if user and user.semester_sekarang and user.semester_sekarang.isdigit() else None
        
        for s in sorted_schedules:
            if hasattr(s.jam_mulai, 'strftime') and s.jam_mulai:
                start_str = s.jam_mulai.strftime('%H:%M')
            else:
                start_str = str(s.jam_mulai)[:5]
                
            if hasattr(s.jam_selesai, 'strftime') and s.jam_selesai:
                end_str = s.jam_selesai.strftime('%H:%M')
            else:
                end_str = str(s.jam_selesai)[:5]
                
            time_str = f"{start_str} - {end_str}"
            sem_info = f"Semester {s.semester_level}" if s.semester_level else "Umum"
            
            # Highlight if it matches user's current semester
            is_current = " [SEMESTER AKTIF]" if user_sem and s.semester_level == user_sem else ""
            
            schedules_list.append(
                f"- {s.hari}: {s.nama} ({time_str}) | {s.sks} SKS | {sem_info}{is_current}"
            )
        
        schedules_context = (
            "USER CLASS SCHEDULES (JADWAL KULIAH AKTIF):\n" +
            "\n".join(schedules_list) +
            "\n------------------\n\n"
        )

    time_context = ""
    if client_local_time:
        formatted_time = client_local_time.strftime("%A, %d %B %Y, %H:%M:%S")
        time_context = f"For your information, the user's current local date and time is {formatted_time}. Please use this for any time-sensitive queries about schedules or deadlines."

    system_instruction = (
        "You are a smart, helpful personal AI Career Coach and Academic Assistant. "
        "You have DIRECT ACCESS to the user's personal profile and database.\n"
        "IMPORTANT: You MUST answer based on the provided USER PROFILE, USER CLASS SCHEDULES, and retrieved CONTEXT FROM DATABASE. "
        "Always tailor your advice, tone, and recommendations to the user's specific major, semester, university, career targets, interests, and skills. "
        "Do NOT say 'I cannot access your calendar' or 'I don't have access to your data'. "
        "You HAVE all the user profile and schedule data in the context.\n"
        "Always be concise, professional, supportive, and actionable.\n\n"
        "ATURAN SANGAT KETAT TERHADAP BATASAN LINGKUP (CRITICAL SCOPE LIMITATIONS):\n"
        "1. Peran utama Anda HANYA sebagai konsultan karir dan asisten akademik. Anda HANYA diperbolehkan menjawab pertanyaan yang berkaitan dengan rencana karir, bimbingan akademik, tugas perkuliahan, dan jadwal kuliah mahasiswa.\n"
        "2. DILARANG KERAS menjawab pertanyaan di luar lingkup akademik dan karir (misalnya: membuatkan contoh kode pemrograman umum, resep masakan, pertanyaan umum/trivia, tugas penulisan di luar kuliah, atau masalah teknis umum lainnya).\n"
        "3. Jika pengguna menanyakan beberapa hal sekaligus (mixed questions) di mana sebagian di antaranya berada di luar lingkup (contoh: 'Apa saran karirku? coba buatkan contoh pemrograman python?'), Anda WAJIB:\n"
        "   - Menolak secara sopan bagian pertanyaan yang tidak relevan tersebut dalam Bahasa Indonesia (contoh: 'Mohon maaf, saya hanya dapat membantu dalam lingkup konsultasi karir dan asisten akademik. Saya tidak dapat membuatkan contoh program Python tersebut.').\n"
        "   - Menjawab HANYA bagian pertanyaan yang berkaitan dengan konsultasi karir/akademik secara detail dan profesional.\n"
        "   - DILARANG menuliskan atau menyertakan contoh kode/jawaban dari pertanyaan luar lingkup tersebut dalam respon Anda."
    )

    if not context_docs:
        context_str = "No relevant schedule or task documents found in the user's database."

    return (
        f"{system_instruction}\n\n"
        "------------------\n\n"
        f"{user_profile_context}"
        f"{schedules_context}"
        f"{time_context}\n\n"
        "RETRIEVED DATABASE CONTEXT:\n"
        "------------------\n"
        f"{context_str}\n\n"
        "------------------\n\n"
        f"QUESTION: {question}\n\n"
        "------------------\n\n"
        "Based on the user's profile, academic schedules, and database context, provide a highly personalized, concise, and actionable answer in Bahasa Indonesia."
    )

def build_career_prompt(context_str: str, user_profile: dict, current_skills: str = "") -> str:
    profile_str = f"""
Nama: {user_profile.get('nama')}
Universitas: {user_profile.get('universitas')}
Jurusan: {user_profile.get('jurusan')}
Semester: {user_profile.get('semester_sekarang')}
Target Karir Fokus: {user_profile.get('target_karir')}
"""
    return f"""
Anda adalah penasihat karir AI (AI Career Advisor).
Tugas Anda adalah menganalisis profil mahasiswa dan menghasilkan:
1. Rekomendasi Karir: Berikan TEPAT 3 pilihan:
   - 1 Karir Utama: Sesuai dengan Target Karir user.
   - 1 Karir Alternatif 1: Karir yang LINIER dengan JURUSAN user saat ini (Wajib relevan dengan apa yang dipelajari di kampus).
   - 1 Karir Alternatif 2: Karir lintas bidang yang masih relevan dengan skill user.

2. Roadmap Pembelajaran: Sangat adaptif terhadap level keahlian user.
3. Actionable Tasks: Tugas spesifik (Actionable tasks) dengan deadline.

PENTING: Jangan hanya memberikan rekomendasi sesuai target karir. User juga ingin melihat peluang karir yang sesuai dengan latar belakang akademiknya (Jurusan). Hubungkan Jurusan user dengan target karirnya dalam "reason".

Profil Mahasiswa:
{profile_str}

Keahlian Saat Ini:
{current_skills if current_skills else "Belum ada data."}

Konteks Akademik (RAG):
{context_str}

Aturan Ketat Adaptivitas:
- Jika user sudah memiliki level 'Menengah' atau 'Lanjutan/Mahir' pada suatu skill, JANGAN mulai dari dasar. Langsung ke topik tingkat lanjut atau implementasi projek.
- Jika user adalah 'Pemula', berikan panduan fundamental yang mendalam.

Aturan Output:
- WAJIB memberikan 3 rekomendasi karir dalam array 'careers'. 
- Gunakan BAHASA INDONESIA.
- SANGAT PENTING: Lakukan analisis profil secara menyeluruh. Sesuaikan rekomendasi karir, alasan, dan roadmap secara alami, logis, dan relevan dengan latar belakang akademik (Jurusan) serta target karir pengguna. Buatlah rekomendasi yang general, fleksibel, dan dapat diaplikasikan langsung sesuai rumpun keilmuan pengguna tanpa membatasi atau mengunggulkan satu bidang industri secara default.
- Untuk 'skill_tags', PILIH MAKSIMAL 6 CORE HARD SKILLS/METODOLOGI SPESIFIK yang relevan dengan bidang karir/jurusan target. Contoh:
  * Bidang IT/Teknologi: "React", "PostgreSQL", "Docker", "TensorFlow"
  * Bidang Bisnis/Manajemen: "Financial Modeling", "Google Analytics", "SQL for Analytics", "Salesforce CRM"
  * Bidang Sosial/Pendidikan: "SPSS", "CBT Counseling", "Instructional Design", "Metodologi Riset Kualitatif"
  * Bidang Teknik/Sains: "AutoCAD", "SolidWorks", "MATLAB", "PLC Programming"
- DILARANG KERAS menggunakan soft skills umum, istilah abstrak, atau skill yang terlalu dasar/umum (seperti "Teamwork", "Komunikasi", "Dasar-dasar", "Microsoft Word"). Harus berupa hard skill atau alat/metodologi praktis nyata. Gunakan ulang 6 skill teknis spesifik tersebut di semua step!
- Roadmap: jadikan 'phase' sebagai Topik Kategori yang relevan (Misal: "Manajemen Keuangan Mikro" atau "Fundamental Konseling BKI"), dan setiap 'title' di dalam 'steps' WAJIB menyebut Spesifik Teknologi/Metode/Konsep Inti (Misal: "Analisis Arus Kas", "Metode Konseling Kognitif", "Perancangan Rencana Belajar").
- Untuk setiap 'step', sertakan 'xp_reward' berdasarkan kesulitan: '20' (Mudah), '50' (Menengah), atau '100' (Sulit).

Kembalikan HANYA JSON:

{{
  "careers": [
    {{
      "name": "",
      "reason": "",
      "strengths": [],
      "weaknesses": []
    }}
  ],
  "roadmap": [
    {{
      "phase": "",
      "steps": [
        {{
          "title": "",
          "description": "",
          "skill_tags": ["<tag1>", "<tag2>", "<tag3>"], // STRICT RULE: 3-6 TAGS, MAX 6 TAGS
          "xp_reward": 20
        }}
      ]
    }}
  ],
  "tasks": [
    {{
      "task": "",
      "priority": "Tinggi/Menengah/Rendah",
      "deadline": ""
    }}
  ]
}}
"""

async def generate_answer_with_gemini(augmented_prompt: str) -> str:
    """Calls the Gemini generation model to get an answer based on the prompt with retries."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY must be set in environment variables.")

    if not GEMINI_GEN_URL:
        raise ValueError("GEMINI_GEN_URL must be set in environment variables.")

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": augmented_prompt}
                ]
            }
        ]
    }

    current_url = GEMINI_GEN_URL
    retries = 3
    delay = 2
    for i in range(retries):
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(current_url, headers=headers, json=payload)
                response.raise_for_status()
                generation_data = response.json()
                # Assume response structure like: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}}
                if "candidates" in generation_data and len(generation_data["candidates"]) > 0:
                    candidate = generation_data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                        return candidate["content"]["parts"][0]["text"]
                
                raise ValueError(f"Unexpected generation response format from Gemini API: {generation_data}")
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
                logger.error(f"Attempt {i+1}/{retries}: Timeout or connection error occurred while calling Gemini Generation API: {e}")
                if i < retries - 1:
                    await sleep(delay)
                    delay *= 2
                    continue
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    error_detail = "Token API sedang habis. Silakan hubungi Developer/Admin untuk memperbaruinya."
                    logger.error(error_detail)
                    raise ValueError(error_detail)
                # Retry for temporary server errors (5xx)
                if e.response.status_code in [500, 502, 503, 504] and i < retries - 1:
                    logger.warning(f"Attempt {i+1}/{retries}: Gemini API returned status {e.response.status_code}. Retrying in {delay}s...")
                    await sleep(delay)
                    delay *= 2
                    continue
                error_detail = f"Gemini Generation API Error: {e.response.text}"
                logger.error(error_detail)
                raise ValueError(error_detail)
            except Exception as e:
                logger.error(f"An unexpected error occurred while calling Gemini Generation API: {e}")
                raise
    raise Exception("Failed to generate answer after multiple retries.")

async def generate_career_analysis(db: Session, user_id: int):
    # 0. Ambil data user secara langsung untuk konteks utama
    from . import models
    user = db.query(models.User).filter_by(id_user=user_id).first()
    current_skills = user.keterampilan if user else ""

    # 1. Ambil embedding user (dummy query text)
    query_text = "career analysis based on profile"
    query_vector = await embed_text_with_gemini(query_text)

    # 2. RAG retrieval (semester, ukm, dsb)
    docs = retrieve_similar_rags(db, query_vector, top_k=5, id_user=user_id)

    # 3. Build context from docs
    context_str = "\n\n".join([doc.text_original for doc in docs])

    # 4. Build profil data untuk konteks eksplisit
    user_profile = {
        "nama": user.nama,
        "universitas": user.universitas,
        "jurusan": user.jurusan,
        "semester_sekarang": user.semester_sekarang,
        "target_karir": user.target_karir
    }

    # 5. Build prompt khusus career dengan data profil lengkap
    prompt = build_career_prompt(context_str, user_profile, current_skills)

    # 5. Call Gemini
    raw_response = await generate_answer_with_gemini(prompt)

    # 6. Parse JSON
    try:
        # Menghapus blok backtick (```json ... ```) jika Gemini mengembalikannya dalam format Markdown
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:-3].strip()
        data = json.loads(raw_response)
        
        # Enforce max 6 UNIQUE skill tags ACROSS THE ENTIRE ROADMAP programmatically
        if "roadmap" in data and isinstance(data["roadmap"], list):
            from collections import Counter
            all_tags = []
            for phase in data["roadmap"]:
                if "steps" in phase and isinstance(phase["steps"], list):
                    for step in phase["steps"]:
                        tags = step.get("skill_tags")
                        if isinstance(tags, list):
                            all_tags.extend(tags)
            
            tag_counts = Counter(all_tags)
            allowed_tags = set([t for t, c in tag_counts.most_common(6)])
            
            for phase in data["roadmap"]:
                if "steps" in phase and isinstance(phase["steps"], list):
                    for step in phase["steps"]:
                        tags = step.get("skill_tags")
                        if isinstance(tags, list):
                            filtered = [t for t in tags if t in allowed_tags]
                            if not filtered and allowed_tags:
                                filtered = [list(allowed_tags)[0]]
                            step["skill_tags"] = filtered[:3]
    except:
        raise ValueError("Invalid JSON from Gemini")

    return data


async def adapt_roadmap_preview(roadmap, steps, user, user_message: str):
    """
    Ask Gemini to suggest modifications to the roadmap based on user feedback.
    Returns a preview (not saved) with proposed changes per step.
    """
    import json as _json

    # Gather all existing unique skill tags across all steps in the current roadmap
    existing_tags = set()
    for s in steps:
        if s.skill_tags:
            parts = [p.strip() for p in s.skill_tags.split(",") if p.strip()]
            existing_tags.update(parts)

    allowed_tags_list = list(existing_tags)
    allowed_tags_str = ", ".join(allowed_tags_list) if allowed_tags_list else "Tidak ada tag sebelumnya"

    steps_summary = "\n".join([
        f"[{s.id}] Phase={s.phase}, Order={s.step_order}, Title={s.title}, Tags={s.skill_tags or '[]'}"
        for s in steps
    ])

    prompt = f"""
Kamu adalah AI Career Coach yang membantu mahasiswa menyesuaikan roadmap belajar mereka.

Berikut adalah daftar langkah roadmap saat ini milik pengguna (format: [id] Phase, Step, Judul, Skill Tags):
---
{steps_summary}
---

Target karir pengguna: {user.target_karir or 'Belum ditentukan'}

Pesan dari pengguna:
"{user_message}"

Daftar Skill Tags yang diperbolehkan (Hanya gunakan dari daftar ini, jangan tambahkan tag baru!):
[{allowed_tags_str}]

Tugasmu: Analisis pesan pengguna dan sarankan perubahan roadmap agar lebih sesuai dengan keinginan/kebutuhan mereka.

ATURAN SANGAT KETAT: Kamu HANYA BOLEH menggunakan skill tags yang sudah ada pada daftar diperbolehkan di atas ([{allowed_tags_str}]). JANGAN PERNAH menambahkan atau menggunakan skill tag baru di luar daftar tersebut!

Kembalikan HANYA JSON berikut tanpa penjelasan apapun. action bisa: "keep" (tidak diubah), "edit" (ubah konten), "add" (step baru), "remove" (hapus):

{{
  "ai_message": "Penjelasan singkat perubahan yang kamu sarankan (Bahasa Indonesia)",
  "proposed_changes": [
    {{
      "id": <integer atau null jika step baru>,
      "action": "keep|edit|add|remove",
      "phase": "<phase name>",
      "step_order": <integer>,
      "title": "<judul step>",
      "description": "<deskripsi>",
      "skill_tags": ["<tag1>", "<tag2>", "<tag3>"], // HANYA gunakan tag dari daftar diperbolehkan!
      "xp_reward": <integer>
    }}
  ]
}}

Sertakan semua step yang ADA (dengan action "keep" jika tidak ada perubahan) dan tambahkan action "add" untuk step baru. SANGAT PENTING: Batasi 'skill_tags' SEKITAR 3-6 TAGS per step! JANGAN PERNAH LEBIH DARI 6 TAGS!
"""

    raw = await generate_answer_with_gemini(prompt)

    try:
        if raw.startswith("```json"):
            raw = raw[7:].strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()
        data = _json.loads(raw)
        
        # Programmatic filtering and mapping to ensure NO new tags are added
        tag_lower_map = {t.lower(): t for t in existing_tags}
        
        if "proposed_changes" in data and isinstance(data["proposed_changes"], list):
            for change in data["proposed_changes"]:
                tags = change.get("skill_tags")
                
                # Convert string to list if AI returned a comma-separated string
                if isinstance(tags, str):
                    tags = [p.strip() for p in tags.split(",") if p.strip()]
                    
                if isinstance(tags, list):
                    filtered_tags = []
                    for t in tags:
                        t_clean = t.strip()
                        if t_clean.lower() in tag_lower_map:
                            filtered_tags.append(tag_lower_map[t_clean.lower()])
                    
                    # Fallback to existing tags if all got filtered out to prevent empty tags
                    if not filtered_tags and existing_tags:
                        filtered_tags = list(existing_tags)[:3]
                        
                    change["skill_tags"] = filtered_tags[:6]
    except Exception:
        raise ValueError(f"Invalid JSON from Gemini adapt: {raw[:200]}")

    return data