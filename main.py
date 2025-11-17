import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents

app = FastAPI(title="Curtains API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactIn(BaseModel):
    name: str
    phone: str
    message: str
    source: str | None = None


CATEGORIES = [
    "Blackout Curtains",
    "Sheer Curtains",
    "Motorized Curtains",
    "Curtain Accessories",
    "Track Systems",
]

GALLERY_FILTERS = [
    "living",
    "bedrooms",
    "majlis",
    "offices",
    "custom",
]


def _seed_products_if_empty():
    try:
        count = db["product"].count_documents({}) if db else 0
        if count > 0:
            return
        # Create 10 demo products with bilingual fields
        demo: List[Dict[str, Any]] = []
        base_imgs = [
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=1400&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1505692952047-1a78307da8f2?q=80&w=1400&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=1400&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1400&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=1400&auto=format&fit=crop",
        ]
        cats = [
            "Blackout Curtains",
            "Sheer Curtains",
            "Motorized Curtains",
            "Curtain Accessories",
            "Track Systems",
        ]
        for i in range(1, 11):
            category = cats[i % len(cats)]
            slug = f"curtain-model-{i}"
            demo.append(
                {
                    "slug": slug,
                    "title": {
                        "en": f"Curtain Model {i}",
                        "ar": f"طراز ستارة {i}",
                    },
                    "description": {
                        "en": "Premium handcrafted curtains with elegant drape and tailored finish.",
                        "ar": "ستائر فاخرة مصنوعة بعناية بملمس أنيق وتفاصيل متقنة.",
                    },
                    "category": category,
                    "image": base_imgs[i % len(base_imgs)],
                    "gallery": [
                        base_imgs[(i + j) % len(base_imgs)] for j in range(3)
                    ],
                }
            )
        for p in demo:
            create_document("product", p)
    except Exception:
        # In case database is not configured, just skip
        pass


def _seed_gallery_if_empty():
    try:
        count = db["galleryitem"].count_documents({}) if db else 0
        if count > 0:
            return
        imgs = [
            ("living", "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1400&auto=format&fit=crop"),
            ("bedrooms", "https://images.unsplash.com/photo-1505691723518-36a6dd1f0472?q=80&w=1400&auto=format&fit=crop"),
            ("majlis", "https://images.unsplash.com/photo-1484101403633-562f891dc89a?q=80&w=1400&auto=format&fit=crop"),
            ("offices", "https://images.unsplash.com/photo-1538688423619-a81d3f23454b?q=80&w=1400&auto=format&fit=crop"),
            ("custom", "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1400&auto=format&fit=crop"),
        ]
        for cat, url in imgs:
            for _ in range(4):
                create_document(
                    "galleryitem",
                    {
                        "category": cat,
                        "image": url,
                        "title": {"en": cat.title(), "ar": ""},
                    },
                )
    except Exception:
        pass


@app.on_event("startup")
async def startup_seed():
    _seed_products_if_empty()
    _seed_gallery_if_empty()


@app.get("/")
def root():
    return {"status": "ok", "service": "Curtains API"}


@app.get("/api/config")
def get_config():
    return {
        "brand": {
            "name_en": "Premium Curtains",
            "name_ar": "ستائر فاخرة",
        },
        "contact": {
            "address_en": "Business Bay, Dubai, UAE",
            "address_ar": "الخليج التجاري، دبي، الإمارات",
            "phone": "+971 55 123 4567",
            "whatsapp": "+971551234567",
            "instagram": "https://instagram.com/yourbrand",
            "tiktok": "https://www.tiktok.com/@yourbrand",
            "map_embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d115868.2872060351!2d55.17128!3d25.07501!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3e5f4348c1382c2d%3A0xdeb32a40ca331c0!2sBusiness%20Bay%20-%20Dubai!5e0!3m2!1sen!2sae!4v1700000000000",
        },
        "categories": CATEGORIES,
        "gallery_filters": GALLERY_FILTERS,
    }


@app.get("/api/products")
def list_products():
    try:
        products = get_documents("product")
        for p in products:
            p["_id"] = str(p.get("_id"))
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{slug}")
def get_product(slug: str):
    try:
        item = db["product"].find_one({"slug": slug}) if db else None
        if not item:
            raise HTTPException(status_code=404, detail="Product not found")
        item["_id"] = str(item.get("_id"))
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gallery")
def gallery():
    try:
        items = get_documents("galleryitem")
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contact")
def contact(data: ContactIn):
    try:
        create_document("contactmessage", data.model_dump())
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
