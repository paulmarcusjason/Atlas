import os
import json
import time
from services.github_storage import GithubStorageService

PRODUCT_VIDEOS_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'database',
    'product_videos_data.json'
)

_LOCAL_VIDEOS = None
_CACHE_TIMESTAMP = 0
CACHE_TTL = 30

DEFAULT_VIDEOS = [
    {
        "id": "pv_1",
        "slot": 1,
        "title": "Architectural Door Locks & Hardwares",
        "category": "Hardwares",
        "badge": "Hardware Division",
        "description": "Explore digital biometric smart locks, solid brass mortise handles, security cylinders, and architectural fittings from Godrej, Yale & Quba.",
        "video_url": "/static/videos/hero_desktop.mp4",
        "poster_url": "/static/images/stores/hardware.jpg",
        "cta_text": "Know more",
        "cta_url": "/products?business=hardware",
        "is_active": True
    },
    {
        "id": "pv_2",
        "slot": 2,
        "title": "Asian Paints & Waterproofing Studio",
        "category": "Paints",
        "badge": "Paints Division",
        "description": "Discover Royale luxury emulsions, exterior weather-guard coatings, wood polishes, and complete Dr. Fixit & Sika waterproofing solutions.",
        "video_url": "/static/videos/hero_mobile.mp4",
        "poster_url": "/static/images/stores/asian_paints.jpg",
        "cta_text": "Know more",
        "cta_url": "/products?category=paints-chemicals",
        "is_active": True
    },
    {
        "id": "pv_3",
        "slot": 3,
        "title": "C.R.I. Pumps & Commercial Plumbing",
        "category": "Pumps & Plumbing",
        "badge": "Plumbing Division",
        "description": "High-efficiency domestic booster pumps, agricultural submersible motors, CPVC/UPVC pipelines, and industrial water tech for seamless flow.",
        "video_url": "/static/videos/hero_desktop.mp4",
        "poster_url": "/static/images/stores/cri_pumps_store.jpg",
        "cta_text": "Know more",
        "cta_url": "/products?category=pumps",
        "is_active": True
    },
    {
        "id": "pv_4",
        "slot": 4,
        "title": "Industrial Power Tools & Machinery",
        "category": "Industrial power tools",
        "badge": "Power Tools Division",
        "description": "Heavy-duty rotary hammers, angle grinders, cordless drill kits, and professional workshop equipment from Bosch, Makita & Ralliwolf.",
        "video_url": "/static/videos/hero_mobile.mp4",
        "poster_url": "/static/images/stores/power_tools.jpg",
        "cta_text": "Know more",
        "cta_url": "/products?business=plumbing&category=power-tools",
        "is_active": True
    },
    {
        "id": "pv_5",
        "slot": 5,
        "title": "Designer Bath & Luxury Sanitaryware",
        "category": "Bath & Sanitaryware",
        "badge": "Bath & Kitchen Division",
        "description": "Thermostatic rain showers, designer faucets, ceramic art basins, and premium luxury bathroom suites from Jaquar & Hindware.",
        "video_url": "/static/videos/hero_desktop.mp4",
        "poster_url": "/static/images/stores/luxury_bathware_store.jpg",
        "cta_text": "Know more",
        "cta_url": "/products?business=bath-kitchen",
        "is_active": True
    },
    {
        "id": "pv_6",
        "slot": 6,
        "title": "Smart BLDC Fans & Modern Electricals",
        "category": "Electricals",
        "badge": "Electricals Division",
        "description": "Super-efficient BLDC smart fans, architectural LED illumination, flame-retardant wiring, and luxury modular switches from Legrand & Orbit.",
        "video_url": "/static/videos/hero_mobile.mp4",
        "poster_url": "/static/images/stores/electricals.jpg",
        "cta_text": "Know more",
        "cta_url": "/products?category=electrical-fans",
        "is_active": True
    }
]

class ProductVideoService:
    @classmethod
    def get_all(cls, active_only=False):
        global _LOCAL_VIDEOS, _CACHE_TIMESTAMP
        now = time.time()

        if _LOCAL_VIDEOS is None or (now - _CACHE_TIMESTAMP) > CACHE_TTL:
            # 1. Try GithubStorageService
            try:
                gh_videos = GithubStorageService.get_product_videos()
                if gh_videos and isinstance(gh_videos, list) and len(gh_videos) > 0:
                    _LOCAL_VIDEOS = gh_videos
                    _CACHE_TIMESTAMP = now
            except Exception as e:
                print(f"⚠️ Notice reading GitHub product videos: {e}")

            # 2. Try local disk
            if _LOCAL_VIDEOS is None and os.path.exists(PRODUCT_VIDEOS_FILE_PATH):
                try:
                    with open(PRODUCT_VIDEOS_FILE_PATH, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            _LOCAL_VIDEOS = data
                            _CACHE_TIMESTAMP = now
                except Exception as e:
                    print(f"⚠️ Notice reading {PRODUCT_VIDEOS_FILE_PATH}: {e}")

            # 3. Fallback to defaults
            if _LOCAL_VIDEOS is None:
                _LOCAL_VIDEOS = list(DEFAULT_VIDEOS)
                _CACHE_TIMESTAMP = now
                try:
                    cls.save_all(_LOCAL_VIDEOS)
                except Exception:
                    pass

        # Ensure we always have 6 slots
        videos = list(_LOCAL_VIDEOS)
        while len(videos) < 6:
            idx = len(videos)
            fallback = DEFAULT_VIDEOS[idx] if idx < len(DEFAULT_VIDEOS) else {
                "id": f"pv_{idx+1}",
                "slot": idx + 1,
                "title": f"Product Showcase {idx+1}",
                "category": "Specialized Division",
                "badge": "Store Division",
                "description": "Explore genuine materials, hardware, and fittings across our specialized stores.",
                "video_url": "/static/videos/hero_desktop.mp4",
                "poster_url": "/static/images/placeholder.jpg",
                "cta_text": "Know more",
                "cta_url": "/products",
                "is_active": True
            }
            videos.append(fallback)

        if active_only:
            return [v for v in videos if v.get('is_active', True)]
        return videos

    @classmethod
    def get_by_slot(cls, slot):
        videos = cls.get_all(active_only=False)
        for v in videos:
            if int(v.get('slot', 0)) == int(slot):
                return v
        return None

    @classmethod
    def save_all(cls, videos_list):
        global _LOCAL_VIDEOS, _CACHE_TIMESTAMP
        _LOCAL_VIDEOS = videos_list
        _CACHE_TIMESTAMP = time.time()

        # Save to local disk
        try:
            os.makedirs(os.path.dirname(PRODUCT_VIDEOS_FILE_PATH), exist_ok=True)
            with open(PRODUCT_VIDEOS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(videos_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Local write notice for {PRODUCT_VIDEOS_FILE_PATH}: {e}")

        # Commit to GitHub via GithubStorageService
        success, msg = GithubStorageService.save_product_videos(videos_list)
        return success, msg

    @classmethod
    def update_slot(cls, slot, updated_data):
        videos = cls.get_all(active_only=False)
        slot_int = int(slot)
        found = False
        for idx, v in enumerate(videos):
            if int(v.get('slot', 0)) == slot_int:
                videos[idx].update(updated_data)
                videos[idx]['slot'] = slot_int
                found = True
                break
        if not found and 1 <= slot_int <= 6:
            updated_data['slot'] = slot_int
            updated_data['id'] = f"pv_{slot_int}"
            videos.append(updated_data)

        # Sort by slot 1..6
        videos.sort(key=lambda x: int(x.get('slot', 0)))
        return cls.save_all(videos)

    @classmethod
    def push_to_github(cls):
        """Forces an immediate commit of the product videos data file to GitHub."""
        videos = cls.get_all(active_only=False)
        return GithubStorageService.save_product_videos(videos)
