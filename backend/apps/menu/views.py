"""The public site's content: one request returns everything the landing page shows."""

from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, MenuItem, Restaurant


def _image_url(field) -> str | None:
    # Relative (/media/...) so it works through the Vite proxy, Tailscale and nginx alike.
    return field.url if field else None


def _credit(subject: str, image, text: str, url: str) -> dict | None:
    if not (image and text):
        return None
    return {"subject": subject, "credit": text, "url": url}


def _item(item: MenuItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "photo": _image_url(item.photo),
        "is_available": item.is_available,
        "is_featured": item.is_featured,
    }


class SiteView(APIView):
    """GET /api/v1/site/: restaurant profile, hours, featured dishes and the menu.

    Always public, whatever REQUIRE_LOGIN says: it's the restaurant's website. No
    authentication either, so a stale token in a visitor's browser can't turn it into a 401.
    Only published categories and items are returned; empty categories are left out.
    ``credits`` lists the shown photos that carry an attribution (third-party photos).
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request):
        restaurant = Restaurant.load()
        published_items = MenuItem.objects.filter(is_published=True)
        categories = (
            Category.objects.filter(is_published=True)
            .prefetch_related(Prefetch("items", queryset=published_items))
        )
        menu = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "items": [_item(item) for item in category.items.all()],
            }
            for category in categories
        ]
        menu = [category for category in menu if category["items"]]
        gallery = list(restaurant.gallery.all())
        published = [item for category in categories for item in category.items.all()]
        credits = [
            _credit("Portada", restaurant.hero_image, restaurant.hero_credit, restaurant.hero_credit_url),
            _credit("Nuestro patio", restaurant.about_image, restaurant.about_credit, restaurant.about_credit_url),
            *(
                _credit(photo.caption or "Galería", photo.image, photo.credit, photo.credit_url)
                for photo in gallery
            ),
            *(
                _credit(item.name, item.photo, item.photo_credit, item.photo_credit_url)
                for item in published
            ),
        ]
        featured = [
            item
            for category in menu
            for item in category["items"]
            if item["is_featured"] and item["is_available"]
        ]
        return Response(
            {
                "restaurant": {
                    "name": restaurant.name,
                    "tagline": restaurant.tagline,
                    "about": restaurant.about,
                    "hero_image": _image_url(restaurant.hero_image),
                    "about_image": _image_url(restaurant.about_image),
                    "address": restaurant.address,
                    "city": restaurant.city,
                    "maps_url": restaurant.maps_url,
                    "phone": restaurant.phone,
                    "whatsapp": restaurant.whatsapp,
                    "instagram_url": restaurant.instagram_url,
                    "facebook_url": restaurant.facebook_url,
                    "menu_note": restaurant.menu_note,
                    "hours": [
                        {"days": line.days, "hours": line.hours}
                        for line in restaurant.hours.all()
                    ],
                },
                "featured": featured,
                "categories": menu,
                "gallery": [
                    {"id": photo.id, "image": photo.image.url, "caption": photo.caption}
                    for photo in gallery
                ],
                "credits": [credit for credit in credits if credit],
            }
        )
