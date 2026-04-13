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
GEMINI_EMBED_URL = os.getenv("GEMINI_EMBED_URL")
GEMINI_GEN_URL = os.getenv("GEMINI_GEN_URL")

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
                logger.error(f"HTTP error occurred while calling Gemini Embedding API: {e.response.text}")
                raise
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

def augment_prompt(question: str, context_docs: List[models.RAGSEmbedding], client_local_time: Optional[datetime] = None) -> str:
    """Constructs an augmented prompt with retrieved context and optional client local time."""
    context_str = "\n\n".join([
        f"Source: {doc.source_type} (ID: {doc.source_id or doc.id_embedding})\nContent: {doc.text_original}"
        for doc in context_docs
    ])

    time_context = ""
    if client_local_time:
        formatted_time = client_local_time.strftime("%A, %d %B %Y, %H:%M:%S")
        time_context = f"For your information, the user's current local date and time is {formatted_time}. Please use this for any time-sensitive queries about schedules or deadlines."

    system_instruction = (
        "You are a smart, helpful personal assistant. "
        "You have DIRECT ACCESS to the user's personal database, which includes:\n"
        "1. Complete Profile (Name, Email, Bio)\n"
        "2. To-Do List (Tasks, Deadlines)\n"
        "3. Class Schedule/Jadwal Matkul (Day, Time, SKS)\n"
        "4. UKM Activities (Organization Name, Role)\n\n"
        "IMPORTANT: You MUST answer based on the provided context below. "
        "Do NOT say 'I cannot access your calendar' or 'I don't have access to your data'. "
        "You HAVE the data in the context. "
        "If the specific answer is not in the context, state 'Based on your saved data, I couldn't find that specific information.' "
        "Always be concise and actionable."
    )

    if not context_docs:
        context_str = "No relevant information found in the user's database to answer this question."

    return (
        f"{system_instruction}\n\n"
        "------------------\n\n"
        f"{time_context}\n\n"
        "CONTEXT FROM DATABASE:\n"
        "------------------\n"
        f"{context_str}\n\n"
        "------------------\n\n"
        f"QUESTION: {question}\n\n"
        "------------------\n\n"
        "Based on the context, provide a concise and actionable answer in Bahasa Indonesia."
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
- Berikan saran yang KONGKRET dan SPESIFIK pada deskripsi, namun untuk 'skill_tags' gunakan nama TEKNOLOGI UTAMA (Parent Tech).
- Roadmap: jadikan 'phase' sebagai Topik Kategori (Misal: "Fundamental Frontend"), dan setiap 'title' di dalam 'steps' WAJIB menyebut Spesifik Teknologi / Konsep Inti (Misal: "HTML Semantics", "CSS Flexbox", "React Hooks").
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
          "skill_tags": [],
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
    """Calls the Gemini generation model to get an answer based on the prompt."""
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

    async with httpx.AsyncClient(timeout=30.0) as client: # Increased timeout to 30 seconds
        try:
            response = await client.post(GEMINI_GEN_URL, headers=headers, json=payload)
            response.raise_for_status()
            generation_data = response.json()
            # Assume response structure like: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}}
            if "candidates" in generation_data and len(generation_data["candidates"]) > 0:
                candidate = generation_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                    return candidate["content"]["parts"][0]["text"]
            
            raise ValueError(f"Unexpected generation response format from Gemini API: {generation_data}")
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            logger.error(f"Timeout error occurred while calling Gemini Generation API: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while calling Gemini Generation API: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while calling Gemini Generation API: {e}")
            raise

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
    except:
        raise ValueError("Invalid JSON from Gemini")

    return data


async def adapt_roadmap_preview(roadmap, steps, user, user_message: str):
    """
    Ask Gemini to suggest modifications to the roadmap based on user feedback.
    Returns a preview (not saved) with proposed changes per step.
    """
    import json as _json

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

Tugasmu: Analisis pesan pengguna dan sarankan perubahan roadmap agar lebih sesuai dengan keinginan/kebutuhan mereka.

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
      "skill_tags": "<JSON array string e.g. ['Python','OOP']>",
      "xp_reward": <integer>
    }}
  ]
}}

Sertakan semua step yang ADA (dengan action "keep" jika tidak ada perubahan) dan tambahkan action "add" untuk step baru.
"""

    raw = await generate_answer_with_gemini(prompt)

    try:
        if raw.startswith("```json"):
            raw = raw[7:].strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()
        data = _json.loads(raw)
    except Exception:
        raise ValueError(f"Invalid JSON from Gemini adapt: {raw[:200]}")

    return data