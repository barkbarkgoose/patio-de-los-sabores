"""The restaurant's public profile and its menu, all edited from the Django admin."""

from django.db import models

from .images import shrink_upload


def credit_field(verbose_name: str = "crédito de la foto") -> models.CharField:
    return models.CharField(
        verbose_name,
        max_length=200,
        blank=True,
        help_text="Solo para fotos de terceros que exigen atribución (autor y licencia). "
        "Dejalo vacío para fotos propias.",
    )


def credit_url_field(verbose_name: str = "enlace del crédito") -> models.URLField:
    return models.URLField(verbose_name, blank=True)


class Restaurant(models.Model):
    """The one restaurant this site is for. Always row pk=1; use ``Restaurant.load()``."""

    name = models.CharField("nombre", max_length=120, default="Patio de los Sabores")
    tagline = models.CharField("frase principal", max_length=200, blank=True)
    about = models.TextField("sobre nosotros", blank=True)
    hero_image = models.ImageField("foto de portada", upload_to="restaurant/", blank=True)
    hero_credit = credit_field()
    hero_credit_url = credit_url_field()
    about_image = models.ImageField("foto de «Nuestro patio»", upload_to="restaurant/", blank=True)
    about_credit = credit_field()
    about_credit_url = credit_url_field()
    address = models.CharField("dirección", max_length=200, blank=True)
    city = models.CharField("ciudad", max_length=120, default="Emboscada, Cordillera, Paraguay")
    maps_url = models.URLField(
        "enlace a Google Maps",
        blank=True,
        help_text="Abrí el lugar en Google Maps, tocá «Compartir» y pegá el enlace aquí.",
    )
    phone = models.CharField("teléfono", max_length=40, blank=True)
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=20,
        blank=True,
        help_text="Con código de país, solo números. Ejemplo: 595981123456",
    )
    instagram_url = models.URLField("Instagram", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    menu_note = models.CharField(
        "nota del menú",
        max_length=200,
        blank=True,
        help_text="Se muestra debajo del menú, por ejemplo sobre precios o formas de pago.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "restaurante"
        verbose_name_plural = "restaurante"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        shrink_upload(self.hero_image, max_size=2000)
        shrink_upload(self.about_image)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "Restaurant":
        restaurant, _ = cls.objects.get_or_create(pk=1)
        return restaurant


class OpeningHours(models.Model):
    """A line of the opening hours, free text so staff can write it however they say it."""

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="hours", verbose_name="restaurante"
    )
    days = models.CharField("días", max_length=80, help_text="Ejemplo: Martes a viernes")
    hours = models.CharField("horario", max_length=80, help_text="Ejemplo: 11:00 – 22:00")
    order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "horario"
        verbose_name_plural = "horarios"

    def __str__(self) -> str:
        return f"{self.days}: {self.hours}"


class Category(models.Model):
    name = models.CharField("nombre", max_length=80)
    slug = models.SlugField("identificador", max_length=80, unique=True)
    description = models.CharField("descripción", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField("orden", default=0)
    is_published = models.BooleanField("publicada", default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self) -> str:
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="items", verbose_name="categoría"
    )
    name = models.CharField("nombre", max_length=120)
    description = models.TextField("descripción", blank=True)
    price = models.PositiveIntegerField("precio (Gs.)")
    photo = models.ImageField("foto", upload_to="menu/", blank=True)
    photo_credit = credit_field()
    photo_credit_url = credit_url_field()
    is_available = models.BooleanField(
        "disponible", default=True, help_text="Desmarcá cuando se termine: se muestra «Agotado»."
    )
    is_featured = models.BooleanField(
        "destacado", default=False, help_text="Aparece en «Los favoritos de la casa»."
    )
    is_published = models.BooleanField(
        "publicado", default=True, help_text="Desmarcá para ocultarlo del sitio."
    )
    order = models.PositiveSmallIntegerField("orden", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "plato"
        verbose_name_plural = "platos"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        shrink_upload(self.photo)
        super().save(*args, **kwargs)


class GalleryPhoto(models.Model):
    """Photos for the «El patio» band: the place, the people, the food."""

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="gallery", verbose_name="restaurante"
    )
    image = models.ImageField("foto", upload_to="gallery/")
    caption = models.CharField("descripción", max_length=120, blank=True)
    credit = credit_field()
    credit_url = credit_url_field()
    order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "foto de la galería"
        verbose_name_plural = "galería"

    def __str__(self) -> str:
        return self.caption or self.image.name

    def save(self, *args, **kwargs):
        shrink_upload(self.image)
        super().save(*args, **kwargs)
