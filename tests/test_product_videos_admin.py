import unittest
import os
from app import create_app
from models.product_video import ProductVideoModel

class ProductVideosAdminTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'product_videos_data.json')
        cls.original_content = None
        if os.path.exists(cls.db_path):
            with open(cls.db_path, 'r', encoding='utf-8') as f:
                cls.original_content = f.read()

    @classmethod
    def tearDownClass(cls):
        if cls.original_content is not None and os.path.exists(cls.db_path):
            with open(cls.db_path, 'w', encoding='utf-8') as f:
                f.write(cls.original_content)

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_admin_product_videos_page_ui(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-admin'
                sess['role'] = 'admin'

            res = client.get('/admin/product-videos')
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')

            # Ensure GitHub labels and badges are removed
            self.assertNotIn('GitHub Sync Active', html)
            self.assertNotIn('Local Disk Storage (Configure GITHUB_TOKEN', html)

            # Ensure Save and Push button exists
            self.assertIn('Save and Push', html)

            # Ensure modal trigger uses clean scalar slot syntax
            self.assertIn('openEditVideoModal(1)', html)

            # Ensure JS data dictionary exists
            self.assertIn('PRODUCT_VIDEOS_DATA', html)
            self.assertIn('PRODUCT_VIDEOS_DATA[1] =', html)

    def test_edit_product_video_slot(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-admin'
                sess['role'] = 'admin'

            # Edit slot 1
            payload = {
                'title': 'Ultra Premium Smart Locks & Digital Security',
                'category': 'Architectural Hardware',
                'badge': 'Smart Door Hardware',
                'description': 'Advanced digital fingerprint and smart mortise handles for modern residences.',
                'video_url': '/static/videos/smart_locks.mp4',
                'poster_url': '/static/images/stores/hardware.jpg',
                'cta_text': 'Explore Hardware',
                'cta_url': '/products?category=Hardware',
                'is_active': 'on'
            }
            res = client.post('/admin/product-videos/1/edit', data=payload, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')

            # Verify updated content appears on admin page
            self.assertIn('Ultra Premium Smart Locks &amp; Digital Security', html)
            self.assertIn('Advanced digital fingerprint', html)
            self.assertIn('Box 1', html)

    def test_save_and_push_endpoint(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-admin'
                sess['role'] = 'admin'

            res = client.post('/admin/product-videos/save-and-push', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')
            self.assertIn('All product videos saved and pushed successfully', html)

if __name__ == '__main__':
    unittest.main()
