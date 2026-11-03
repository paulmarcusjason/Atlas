import unittest
import os
from app import create_app
from models.product import ProductModel
from models.brand import BrandModel
from models.category import CategoryModel

class GTMAndPagesRegressionTest(unittest.TestCase):
    def setUp(self):
        # Ensure fresh clean environment per test
        if 'VERCEL' in os.environ:
            del os.environ['VERCEL']

    def test_local_development_tracking_disabled_by_default(self):
        """Task 10: Verify local development tracking is disabled by default."""
        app = create_app()
        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(b'GTM-NZR4VKQZ', res.data)
            self.assertNotIn(b'https://www.googletagmanager.com/gtm.js', res.data)
            self.assertNotIn(b'https://www.googletagmanager.com/ns.html', res.data)

    def test_local_development_tracking_enabled_when_explicitly_configured(self):
        """Task 10: Verify tracking is enabled locally when ENABLE_LOCAL_GTM=True."""
        app = create_app()
        app.config['ENABLE_LOCAL_GTM'] = True
        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'GTM-NZR4VKQZ', res.data)
            self.assertEqual(res.data.count(b'https://www.googletagmanager.com/gtm.js?id='), 1)
            self.assertEqual(res.data.count(b'https://www.googletagmanager.com/ns.html?id=GTM-NZR4VKQZ'), 1)

    def test_production_gtm_installation_and_placement(self):
        """Tasks 3, 4, 5, 6, 7, 8, 9: Verify GTM installation in production mode."""
        os.environ['VERCEL'] = '1'
        app = create_app()
        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')

            # Verify head & body placement
            head_end = html.find('</head>')
            body_start = html.find('<body')
            self.assertNotEqual(head_end, -1)
            self.assertNotEqual(body_start, -1)

            head_content = html[:head_end]
            body_content = html[body_start:]

            # 1. GTM Script in <head>
            self.assertIn('https://www.googletagmanager.com/gtm.js?id=', head_content)
            self.assertIn("window,document,'script','dataLayer','GTM-NZR4VKQZ'", head_content)
            self.assertEqual(head_content.count('https://www.googletagmanager.com/gtm.js?id='), 1)

            # 2. GTM noscript immediately after <body>
            body_tag_end = html.find('>', body_start) + 1
            after_body = html[body_tag_end:].lstrip()
            self.assertTrue(
                after_body.startswith('<!-- Google Tag Manager (noscript) -->') or
                '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NZR4VKQZ"' in after_body[:200]
            )
            self.assertEqual(body_content.count('https://www.googletagmanager.com/ns.html?id=GTM-NZR4VKQZ'), 1)

            # 3. Exactly 2 occurrences of container ID (1 head script, 1 body noscript)
            self.assertEqual(html.count('GTM-NZR4VKQZ'), 2)

            # 4. No separate GA4 script
            self.assertNotIn('G-2SZ2BENH05', html)
            self.assertNotIn('gtag(', html)

            # 5. Preserved SEO metadata
            self.assertIn('<title>', html)
            self.assertIn('name="description"', html)
            self.assertIn('application/ld+json', html)
            self.assertIn('Sathik Groups', html)

    def test_all_public_pages_for_duplicate_gtm(self):
        """Task 11: Check all public website pages for duplicate GTM installations."""
        os.environ['VERCEL'] = '1'
        app = create_app()
        with app.test_client() as client:
            prods, _ = ProductModel.find_all(limit=1)
            prod_slug = prods[0]['slug'] if prods else 'finolux-upvc-pipes-and-fitting'
            brands = BrandModel.find_all()
            brand_slug = brands[0]['slug'] if brands else 'asian-paints'
            cats = CategoryModel.find_all()
            cat_slug = cats[0]['slug'] if cats else 'bathware'

            public_routes = [
                '/',
                '/products',
                f'/products/{prod_slug}',
                f'/product/{prod_slug}',
                '/brands',
                f'/brands/{brand_slug}',
                '/stores',
                '/stores/hardware',
                f'/stores/hardware/{cat_slug}',
                '/locations/red-hills',
                '/locations/red-hills/',
                '/projects',
                '/msasathik',
                '/register'
            ]

            for route in public_routes:
                with self.subTest(route=route):
                    res = client.get(route, follow_redirects=True)
                    self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
                    html = res.data.decode('utf-8')

                    head_end = html.find('</head>')
                    body_start = html.find('<body')
                    head_html = html[:head_end]
                    body_html = html[body_start:]

                    # Exactly 1 head script
                    self.assertEqual(head_html.count('https://www.googletagmanager.com/gtm.js?id='), 1, f"Duplicate head GTM script on {route}")
                    # Exactly 1 body noscript
                    self.assertEqual(body_html.count('https://www.googletagmanager.com/ns.html?id=GTM-NZR4VKQZ'), 1, f"Duplicate body GTM noscript on {route}")
                    # Exactly 2 total mentions of container ID
                    self.assertEqual(html.count('GTM-NZR4VKQZ'), 2, f"Unexpected GTM-NZR4VKQZ count on {route}")
                    # No separate GA4 script
                    self.assertNotIn('G-2SZ2BENH05', html, f"Found separate GA4 script on {route}")
                    self.assertNotIn('gtag(', html, f"Found gtag script on {route}")

if __name__ == '__main__':
    unittest.main()
