from fastapi import APIRouter
import os

router = APIRouter()

PHOTOS_DIR = "/opt/farm-adopt/static/photos"
BASE_URL = "/static/photos"

@router.get("/api/photos")
def list_photos():
    """返回照片列表，按日期分组，最新在前"""
    if not os.path.exists(PHOTOS_DIR):
        return {"dates": [], "total": 0}

    dates = sorted(
        [d for d in os.listdir(PHOTOS_DIR)
         if os.path.isdir(os.path.join(PHOTOS_DIR, d))],
        reverse=True
    )

    result = []
    for date in dates:
        date_dir = os.path.join(PHOTOS_DIR, date)
        files = sorted(
            [f for f in os.listdir(date_dir) if f.endswith('.jpg')],
            reverse=True
        )
        if not files:
            continue
        photos = []
        for f in files:
            time_str = f.replace('.jpg', '').replace('-', ':')
            photos.append({
                "filename": f,
                "url": f"{BASE_URL}/{date}/{f}",
                "time": time_str,
                "datetime": f"{date} {time_str}"
            })
        result.append({"date": date, "photos": photos})

    return {
        "dates": result,
        "total": sum(len(d["photos"]) for d in result)
    }
