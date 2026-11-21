"""Fill an empty site with the restaurant profile and a starter Paraguayan menu.

Prices are estimates in guaraníes; staff adjust them (and add photos) in the admin.
Does nothing if the menu already has dishes, unless --reset is given.

--photos attaches the placeholder photos in ../../seed_photos/ (freely licensed, from
Wikimedia Commons, credited on the page) to anything that has no photo yet.
"""

import json
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.menu.models import Category, GalleryPhoto, MenuItem, OpeningHours, Restaurant

SEED_PHOTOS = Path(__file__).resolve().parents[2] / "seed_photos"

RESTAURANT = {
    "name": "Patio de los Sabores",
    "tagline": "Comida casera paraguaya, al aire libre y con sabor de Emboscada.",
    "about": (
        "Somos un patio familiar en Emboscada, la Capital de la Piedra. Cocinamos "
        "recetas de siempre con productos de la zona: chipa recién horneada, vori vori "
        "de la abuela y asado a la leña.\n\n"
        "Vení a compartir un tereré bajo los árboles, traé a la familia y quedate "
        "el tiempo que quieras."
    ),
    "city": "Emboscada, Cordillera, Paraguay",
    "maps_url": "https://www.google.com/maps/search/?api=1&query=Emboscada%2C+Paraguay",
    "menu_note": "Precios en guaraníes, IVA incluido. Aceptamos efectivo y transferencia.",
}

HOURS = [
    ("Martes a viernes", "11:00 – 15:00 · 18:30 – 23:00"),
    ("Sábados y domingos", "11:00 – 23:30"),
    ("Lunes", "Cerrado"),
]

# (slug, name, description, [(name, description, price, featured), ...])
MENU = [
    ("para-compartir", "Para compartir", "Clásicos para empezar la ronda.", [
        ("Chipa (4 unidades)", "Recién salida del tatakua, con queso Paraguay y anís.", 10000, False),
        ("Chipa guasu", "Pastel de choclo fresco, cebolla y queso, horneado en el momento.", 18000, True),
        ("Sopa paraguaya", "La sopa que se come con tenedor: harina de maíz, queso y cebolla.", 15000, False),
        ("Mbejú", "Torta crocante de almidón de mandioca y queso, a la plancha.", 15000, False),
        ("Empanada de carne", "Masa casera rellena de carne cortada a cuchillo, huevo y verdeo.", 7000, False),
        ("Empanada de mandi'o", "Masa de mandioca rellena de carne, frita en el momento.", 7000, False),
    ]),
    ("platos-principales", "Platos principales", "Recetas de siempre, porciones abundantes.", [
        ("Vori vori de gallina", "Caldo de gallina casera con bolitas de harina de maíz y queso.", 35000, True),
        ("Bife koygua", "Bife a la criolla con cebolla, tomate y huevo frito, con arroz o mandioca.", 45000, False),
        ("Milanesa a la napolitana", "Milanesa de carne con salsa de tomate, jamón y queso. Con papas fritas.", 48000, False),
        ("Pira caldo", "Sopa de pescado de río, al estilo del Paraguay.", 35000, False),
        ("Guiso de arroz con pollo", "Arroz carretero con pollo, pimiento y locote, bien jugoso.", 35000, False),
        ("Locro", "Maíz blanco, zapallo y carne, cocido a fuego lento.", 30000, False),
    ]),
    ("parrilla", "Parrilla", "A la leña, con mandioca y ensalada de la casa.", [
        ("Costilla de res", "Costilla a la leña, porción para una persona.", 60000, True),
        ("Medio pollo a la parrilla", "Medio pollo marinado con limón y ajo.", 45000, False),
        ("Chorizo parrillero", "Chorizo casero con chimichurri y mandioca.", 25000, False),
        ("Parrillada para dos", "Costilla, vacío, chorizo, morcilla y pollo. Para compartir.", 140000, False),
    ]),
    ("postres", "Postres", "Algo dulce para cerrar.", [
        ("Kosereva", "Dulce de cáscara de naranja agria en miel negra.", 12000, True),
        ("Dulce de mamón con queso Paraguay", "Mamón en almíbar con una tajada de queso fresco.", 15000, False),
        ("Mbaipy he'ẽ", "Postre tradicional de harina de maíz, leche y miel negra.", 12000, False),
        ("Flan casero", "Con dulce de leche o crema.", 13000, False),
    ]),
    ("bebidas", "Bebidas", "Fresquitas, como corresponde.", [
        ("Jarra de tereré con yuyos", "Agua bien fría con yuyos machacados del día. Guampa y bombilla incluidas.", 15000, False),
        ("Mosto helado", "Jugo de caña de azúcar recién exprimido.", 8000, False),
        ("Jugo natural", "Naranja, piña o mburucuyá, según la estación.", 12000, False),
        ("Cocido con leche", "Yerba quemada con azúcar, con leche.", 7000, False),
        ("Gaseosa 500 ml", "", 9000, False),
        ("Agua mineral 500 ml", "Con o sin gas.", 6000, False),
        ("Cerveza 1 litro", "Pilsen o Brahma, bien helada.", 22000, False),
    ]),
]


class Command(BaseCommand):
    help = "Fill the site with the restaurant profile and a starter menu (skips if dishes exist)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete every category and dish first (also resets the profile and hours).",
        )
        parser.add_argument(
            "--photos",
            action="store_true",
            help="Attach the placeholder photos to the cover, about, gallery and dishes without one.",
        )

    @transaction.atomic
    def handle(self, *args, reset: bool = False, photos: bool = False, **options):
        if MenuItem.objects.exists() and not reset:
            self.stdout.write("The menu already has dishes; left it as is (use --reset to replace).")
        else:
            self.seed_menu(reset)
        if photos:
            self.attach_photos()

    def seed_menu(self, reset: bool) -> None:
        if reset:
            MenuItem.objects.all().delete()
            Category.objects.all().delete()
            OpeningHours.objects.all().delete()

        restaurant = Restaurant.load()
        for field, value in RESTAURANT.items():
            setattr(restaurant, field, value)
        restaurant.save()
        for order, (days, hours) in enumerate(HOURS):
            OpeningHours.objects.create(restaurant=restaurant, days=days, hours=hours, order=order)

        dishes = 0
        for category_order, (slug, name, description, items) in enumerate(MENU):
            category = Category.objects.create(
                slug=slug, name=name, description=description, order=category_order
            )
            for item_order, (item_name, item_description, price, featured) in enumerate(items):
                MenuItem.objects.create(
                    category=category,
                    name=item_name,
                    description=item_description,
                    price=price,
                    is_featured=featured,
                    order=item_order,
                )
                dishes += 1
        self.stdout.write(self.style.SUCCESS(f"Created {len(MENU)} categories and {dishes} dishes."))

    def attach_photos(self) -> None:
        manifest = json.loads((SEED_PHOTOS / "manifest.json").read_text())
        restaurant = Restaurant.load()
        attached = 0

        def store(field, photo: dict) -> None:
            with (SEED_PHOTOS / photo["file"]).open("rb") as handle:
                field.save(photo["file"], File(handle), save=False)

        for field, key in (("hero", "hero"), ("about", "about")):
            image = getattr(restaurant, f"{field}_image")
            if key in manifest and not image:
                store(image, manifest[key])
                setattr(restaurant, f"{field}_credit", manifest[key]["credit"])
                setattr(restaurant, f"{field}_credit_url", manifest[key]["url"])
                attached += 1
        restaurant.save()

        if not restaurant.gallery.exists():
            for order, photo in enumerate(manifest.get("gallery", [])):
                gallery_photo = GalleryPhoto(
                    restaurant=restaurant,
                    caption=photo["caption"],
                    credit=photo["credit"],
                    credit_url=photo["url"],
                    order=order,
                )
                store(gallery_photo.image, photo)
                gallery_photo.save()
                attached += 1

        for name, photo in manifest.get("dishes", {}).items():
            for item in MenuItem.objects.filter(name=name, photo=""):
                store(item.photo, photo)
                item.photo_credit = photo["credit"]
                item.photo_credit_url = photo["url"]
                item.save()
                attached += 1

        self.stdout.write(self.style.SUCCESS(f"Attached {attached} placeholder photos."))
