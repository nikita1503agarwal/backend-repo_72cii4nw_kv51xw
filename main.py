import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Post, Event, Media

app = FastAPI(title="Modern KPRF Model API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Backend running", "version": "1.0.0"}


# -------------------- Posts --------------------
class PostsQuery(BaseModel):
    featured: Optional[bool] = None
    tag: Optional[str] = None
    limit: Optional[int] = 10


@app.get("/api/posts")
def list_posts(featured: Optional[bool] = None, tag: Optional[str] = None, limit: int = 10):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filter_dict = {}
    if featured is not None:
        filter_dict["featured"] = featured
    if tag:
        filter_dict["tags"] = {"$in": [tag]}

    docs = get_documents("post", filter_dict, limit)
    # Convert ObjectId and datetimes to strings
    def normalize(d):
        d["_id"] = str(d.get("_id"))
        if d.get("published_at") and isinstance(d.get("published_at"), datetime):
            d["published_at"] = d["published_at"].isoformat()
        return d

    return [normalize(d) for d in docs]


@app.post("/api/posts")
def create_post(post: Post):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    if not post.published_at:
        post.published_at = datetime.utcnow()
    inserted_id = create_document("post", post)
    return {"id": inserted_id}


# -------------------- Events --------------------
@app.get("/api/events")
def list_events(limit: int = 10):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("event", {}, limit)

    def normalize(d):
        d["_id"] = str(d.get("_id"))
        if d.get("date") and isinstance(d.get("date"), datetime):
            d["date"] = d["date"].isoformat()
        return d

    return [normalize(d) for d in docs]


@app.post("/api/events")
def create_event(event: Event):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("event", event)
    return {"id": inserted_id}


# -------------------- Media --------------------
@app.get("/api/media")
def list_media(limit: int = 12):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("media", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


@app.post("/api/media")
def create_media(item: Media):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("media", item)
    return {"id": inserted_id}


# -------------------- Utilities --------------------
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available" if db is None else "✅ Connected & Working",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "collections": []
    }
    try:
        if db is not None:
            response["collections"] = db.list_collection_names()[:10]
    except Exception as e:
        response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
    return response


@app.post("/api/seed")
def seed_demo_content():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Only seed if collections are empty
    has_posts = db["post"].count_documents({}) > 0
    has_events = db["event"].count_documents({}) > 0
    has_media = db["media"].count_documents({}) > 0

    inserted = {"posts": 0, "events": 0, "media": 0}

    if not has_posts:
        posts: List[Post] = [
            Post(
                title="Новый курс: социальная справедливость и развитие",
                summary="Ключевые инициативы для поддержки семей, образования и промышленности.",
                content="<p>Мы предлагаем комплекс мер, направленных на повышение качества жизни граждан... </p>",
                cover_image="https://images.unsplash.com/photo-1529101091764-c3526daf38fe?q=80&w=1200&auto=format&fit=crop",
                tags=["политика", "экономика"],
                author="Пресс-служба",
                featured=True,
            ),
            Post(
                title="Итоги региональных встреч",
                summary="Встречи с активистами и жителями прошли в 12 городах.",
                content="<p>Обсудили важные вопросы местной повестки, инфраструктуры и здравоохранения...</p>",
                cover_image="https://images.unsplash.com/photo-1543489816-c87b0f5f7dd2?q=80&w=1200&auto=format&fit=crop",
                tags=["регионы"],
                author="Редакция",
            ),
            Post(
                title="Молодёжные инициативы: идеи и решения",
                summary="Предложения по развитию спорта, науки и творчества.",
                content="<p>Молодёжь — драйвер перемен. Мы поддерживаем инициативы в образовании и культуре...</p>",
                cover_image="https://images.unsplash.com/photo-1503428593586-e225b39bddfe?q=80&w=1200&auto=format&fit=crop",
                tags=["молодёжь", "культура"],
                author="Редакция",
            ),
        ]
        for p in posts:
            if not p.published_at:
                p.published_at = datetime.utcnow()
            create_document("post", p)
            inserted["posts"] += 1

    if not has_events:
        events: List[Event] = [
            Event(
                title="Общественная приёмка дворовых территорий",
                description="Совместно с жителями проверим качество благоустройства.",
                location="Москва",
                date=datetime.utcnow(),
                image="https://images.unsplash.com/photo-1520975922325-24c8f6d8b15a?q=80&w=1200&auto=format&fit=crop",
            ),
            Event(
                title="Круглый стол: поддержка семей",
                description="Эксперты и общественники обсудят меры поддержки.",
                location="Санкт-Петербург",
                date=datetime.utcnow(),
            ),
        ]
        for e in events:
            create_document("event", e)
            inserted["events"] += 1

    if not has_media:
        media_items: List[Media] = [
            Media(
                title="Фоторепортаж: встреча с жителями",
                type="photo",
                url="https://images.unsplash.com/photo-1556761175-b413da4baf72?q=80&w=1600&auto=format&fit=crop",
                thumbnail="https://images.unsplash.com/photo-1556761175-b413da4baf72?q=80&w=600&auto=format&fit=crop",
                tags=["репортаж"],
            ),
            Media(
                title="Интервью с экспертами",
                type="video",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                thumbnail="https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                tags=["интервью"],
            ),
        ]
        for m in media_items:
            create_document("media", m)
            inserted["media"] += 1

    return {"inserted": inserted}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
