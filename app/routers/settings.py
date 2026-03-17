from fastapi import APIRouter, Depends
from app.auth import get_current_admin
import json, os

router = APIRouter()

SETTINGS_FILE = "/opt/farm-adopt/static/settings.json"
DEFAULT_SETTINGS = {
    "banner_image": "",
    "banner_title": "\u4e00\u68f5\u8336\u6811\uff0c\u4e00\u5e74\u7684\u6765\u5f80",
    "banner_sub": "\u6c49\u4e2d\u00b7\u897f\u4e61\uff0c\u6d77\u62d8800\u7c73\uff0c\u6625\u8336\u5c06\u51fa"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(data: dict):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False)

@router.get("/api/settings")
def get_settings():
    return load_settings()

@router.put("/api/settings")
def update_settings(data: dict, _=Depends(get_current_admin)):
    settings = load_settings()
    for k in DEFAULT_SETTINGS:
        if k in data:
            settings[k] = data[k]
    save_settings(settings)
    return settings
