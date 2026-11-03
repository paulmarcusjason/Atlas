from services.product_video_service import ProductVideoService

class ProductVideoModel:
    @classmethod
    def find_all(cls, active_only=False):
        return ProductVideoService.get_all(active_only=active_only)

    @classmethod
    def find_by_slot(cls, slot):
        return ProductVideoService.get_by_slot(slot)

    @classmethod
    def update_slot(cls, slot, updated_data):
        return ProductVideoService.update_slot(slot, updated_data)

    @classmethod
    def save_all(cls, videos_list):
        return ProductVideoService.save_all(videos_list)

    @classmethod
    def push_to_github(cls):
        return ProductVideoService.push_to_github()
