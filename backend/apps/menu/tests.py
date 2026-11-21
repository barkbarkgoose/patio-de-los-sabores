"""Tests for the public site endpoint, the seed command and photo shrinking."""

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from PIL import Image
from rest_framework.test import APIClient

from apps.menu.models import Category, GalleryPhoto, MenuItem, OpeningHours, Restaurant

SITE_URL = "/api/v1/site/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


def make_image(width: int, height: int, fmt: str = "PNG") -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGBA" if fmt == "PNG" else "RGB", (width, height), "red").save(buffer, fmt)
    return SimpleUploadedFile(f"photo.{fmt.lower()}", buffer.getvalue())


@pytest.mark.django_db
class TestSiteView:
    def test_returns_profile_hours_and_menu(self, api_client):
        restaurant = Restaurant.load()
        restaurant.tagline = "Comida casera"
        restaurant.save()
        OpeningHours.objects.create(restaurant=restaurant, days="Lunes", hours="Cerrado")
        category = Category.objects.create(name="Postres", slug="postres")
        MenuItem.objects.create(category=category, name="Kosereva", price=12000)

        response = api_client.get(SITE_URL)

        assert response.status_code == 200
        assert response.data["restaurant"]["tagline"] == "Comida casera"
        assert response.data["restaurant"]["hours"] == [{"days": "Lunes", "hours": "Cerrado"}]
        [postres] = response.data["categories"]
        assert postres["items"][0]["name"] == "Kosereva"
        assert postres["items"][0]["price"] == 12000
        assert postres["items"][0]["photo"] is None

    def test_hides_unpublished_items_and_categories(self, api_client):
        shown = Category.objects.create(name="Visible", slug="visible", order=0)
        hidden = Category.objects.create(name="Oculta", slug="oculta", is_published=False)
        empty = Category.objects.create(name="Vacía", slug="vacia")
        MenuItem.objects.create(category=shown, name="Sí", price=1)
        MenuItem.objects.create(category=shown, name="Borrador", price=1, is_published=False)
        MenuItem.objects.create(category=hidden, name="En categoría oculta", price=1)
        MenuItem.objects.create(category=empty, name="Solo borrador", price=1, is_published=False)

        response = api_client.get(SITE_URL)

        assert [c["slug"] for c in response.data["categories"]] == ["visible"]
        assert [i["name"] for i in response.data["categories"][0]["items"]] == ["Sí"]

    def test_unavailable_items_are_listed_but_not_featured(self, api_client):
        category = Category.objects.create(name="Platos", slug="platos")
        MenuItem.objects.create(category=category, name="Hay", price=1, is_featured=True)
        MenuItem.objects.create(
            category=category, name="Agotado", price=1, is_featured=True, is_available=False
        )

        response = api_client.get(SITE_URL)

        assert [i["name"] for i in response.data["featured"]] == ["Hay"]
        assert {i["name"] for i in response.data["categories"][0]["items"]} == {"Hay", "Agotado"}

    @override_settings(REQUIRE_LOGIN=True)
    def test_public_even_when_login_required(self, api_client):
        assert api_client.get(SITE_URL).status_code == 200

    def test_stale_token_is_ignored(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        assert api_client.get(SITE_URL).status_code == 200

    def test_read_only(self, api_client):
        assert api_client.post(SITE_URL, {}).status_code == 405


@pytest.mark.django_db
class TestPhotos:
    def test_large_upload_is_shrunk_to_jpeg(self, media_root):
        category = Category.objects.create(name="Platos", slug="platos")
        item = MenuItem.objects.create(
            category=category, name="Asado", price=1, photo=make_image(4000, 3000)
        )

        assert item.photo.name.endswith(".jpg")
        with Image.open(item.photo.path) as stored:
            assert max(stored.size) == 1600
            assert stored.mode == "RGB"

    def test_resaving_keeps_the_stored_photo(self, media_root):
        category = Category.objects.create(name="Platos", slug="platos")
        item = MenuItem.objects.create(
            category=category, name="Asado", price=1, photo=make_image(800, 600, "JPEG")
        )
        name = item.photo.name

        item.price = 2
        item.save()

        item.refresh_from_db()
        assert item.photo.name == name

    def test_gallery_and_credits(self, api_client, media_root):
        restaurant = Restaurant.load()
        restaurant.hero_image = make_image(10, 10)
        restaurant.hero_credit = "Autor · CC BY-SA 4.0"
        restaurant.hero_credit_url = "https://commons.wikimedia.org/wiki/File:X.jpg"
        restaurant.save()
        GalleryPhoto.objects.create(restaurant=restaurant, image=make_image(10, 10), caption="La iglesia")
        category = Category.objects.create(name="Platos", slug="platos")
        MenuItem.objects.create(
            category=category, name="Con crédito", price=1,
            photo=make_image(10, 10), photo_credit="Otro · CC BY 4.0",
        )
        MenuItem.objects.create(category=category, name="Foto propia", price=1, photo=make_image(10, 10))
        MenuItem.objects.create(category=category, name="Crédito sin foto", price=1, photo_credit="x")
        MenuItem.objects.create(
            category=category, name="Oculto", price=1, is_published=False,
            photo=make_image(10, 10), photo_credit="no debe salir",
        )

        data = api_client.get(SITE_URL).data

        assert [g["caption"] for g in data["gallery"]] == ["La iglesia"]
        assert data["gallery"][0]["image"].startswith("/media/gallery/")
        assert [(c["subject"], c["credit"]) for c in data["credits"]] == [
            ("Portada", "Autor · CC BY-SA 4.0"),
            ("Con crédito", "Otro · CC BY 4.0"),
        ]
        assert data["credits"][0]["url"] == "https://commons.wikimedia.org/wiki/File:X.jpg"

    def test_photo_url_is_relative(self, api_client, media_root):
        category = Category.objects.create(name="Platos", slug="platos")
        MenuItem.objects.create(category=category, name="Asado", price=1, photo=make_image(10, 10))

        photo = api_client.get(SITE_URL).data["categories"][0]["items"][0]["photo"]

        assert photo.startswith("/media/menu/")


@pytest.mark.django_db
class TestAdmin:
    @pytest.mark.parametrize(
        "path",
        ["menu/menuitem/", "menu/menuitem/add/", "menu/category/", "menu/restaurant/1/change/"],
    )
    def test_pages_render(self, client, settings, path):
        from django.contrib.auth import get_user_model

        call_command("seed_menu")
        admin = get_user_model().objects.create_superuser(
            email="admin@example.com", name="Admin", password="ValidPassword123!"
        )
        client.force_login(admin)

        response = client.get(f"/{settings.ADMIN_URL}{path}")

        assert response.status_code == 200


@pytest.mark.django_db
class TestSeedMenu:
    def test_seeds_once(self):
        call_command("seed_menu")
        count = MenuItem.objects.count()
        assert count > 0
        assert Restaurant.load().hours.exists()

        call_command("seed_menu")
        assert MenuItem.objects.count() == count

    def test_photos_fill_only_empty_slots(self, media_root, tmp_path, monkeypatch):
        import json

        from apps.menu.management.commands import seed_menu

        photos = tmp_path / "seed"
        photos.mkdir()
        for name in ("hero.jpg", "church.jpg", "chipa.jpg"):
            Image.new("RGB", (20, 10), "blue").save(photos / name)
        (photos / "manifest.json").write_text(json.dumps({
            "hero": {"file": "hero.jpg", "credit": "A · CC BY 4.0", "url": "https://example.com/a"},
            "gallery": [{"file": "church.jpg", "caption": "La iglesia", "credit": "PD", "url": ""}],
            "dishes": {
                "Chipa guasu": {"file": "chipa.jpg", "credit": "B · CC BY-SA 4.0", "url": ""},
                "Kosereva": {"file": "chipa.jpg", "credit": "C", "url": ""},
            },
        }))
        monkeypatch.setattr(seed_menu, "SEED_PHOTOS", photos)
        call_command("seed_menu")
        own = MenuItem.objects.get(name="Kosereva")
        own.photo = make_image(10, 10)
        own.save()
        own_photo = MenuItem.objects.get(name="Kosereva").photo.name

        call_command("seed_menu", photos=True)
        call_command("seed_menu", photos=True)  # a second run changes nothing

        restaurant = Restaurant.load()
        assert restaurant.hero_image and restaurant.hero_credit == "A · CC BY 4.0"
        assert not restaurant.about_image
        assert list(restaurant.gallery.values_list("caption", flat=True)) == ["La iglesia"]
        chipa = MenuItem.objects.get(name="Chipa guasu")
        assert chipa.photo and chipa.photo_credit == "B · CC BY-SA 4.0"
        kosereva = MenuItem.objects.get(name="Kosereva")
        assert kosereva.photo.name == own_photo and kosereva.photo_credit == ""

    def test_reset_replaces(self):
        call_command("seed_menu")
        MenuItem.objects.update(price=1)

        call_command("seed_menu", reset=True)

        assert not MenuItem.objects.filter(price=1).exists()
        assert Restaurant.objects.count() == 1
