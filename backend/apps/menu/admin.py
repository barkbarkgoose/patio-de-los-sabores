"""Staff edit the whole public site here: the restaurant profile, categories and dishes."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Category, GalleryPhoto, MenuItem, OpeningHours, Restaurant

admin.site.site_header = "Patio de los Sabores"
admin.site.site_title = "Patio de los Sabores"
admin.site.index_title = "Administración del sitio"


def _thumbnail(field, size: int = 64):
    if not field:
        return "—"
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:6px">',
        field.url,
        size,
        size,
    )


def format_gs(amount: int) -> str:
    return "Gs. " + f"{amount:,}".replace(",", ".")


class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 0


class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 0
    fields = ["preview", "image", "caption", "order", "credit", "credit_url"]
    readonly_fields = ["preview"]

    @admin.display(description="vista previa")
    def preview(self, obj):
        return _thumbnail(obj.image)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [OpeningHoursInline, GalleryPhotoInline]
    readonly_fields = ["hero_preview", "about_preview"]
    fieldsets = [
        (None, {"fields": ["name", "tagline", "about"]}),
        ("Fotos", {
            "fields": [
                "hero_image", "hero_preview", "hero_credit", "hero_credit_url",
                "about_image", "about_preview", "about_credit", "about_credit_url",
            ],
        }),
        ("Ubicación y contacto", {
            "fields": [
                "address", "city", "maps_url", "phone", "whatsapp",
                "instagram_url", "facebook_url",
            ],
        }),
        ("Menú", {"fields": ["menu_note"]}),
    ]

    @admin.display(description="vista previa")
    def hero_preview(self, obj):
        return _thumbnail(obj.hero_image, size=240)

    @admin.display(description="vista previa")
    def about_preview(self, obj):
        return _thumbnail(obj.about_image, size=240)

    def has_add_permission(self, request):
        return not Restaurant.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ["name", "price", "is_available", "is_featured", "is_published", "order"]
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "item_count", "is_published", "order"]
    list_editable = ["is_published", "order"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [MenuItemInline]

    @admin.display(description="platos")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        "thumbnail", "name", "category", "price_display",
        "is_available", "is_featured", "is_published", "order",
    ]
    list_display_links = ["thumbnail", "name"]
    list_editable = ["is_available", "is_featured", "is_published", "order"]
    list_filter = ["category", "is_available", "is_featured", "is_published"]
    list_select_related = ["category"]
    search_fields = ["name", "description"]
    readonly_fields = ["photo_preview"]
    fields = [
        "category", "name", "description", "price",
        "photo", "photo_preview", "photo_credit", "photo_credit_url",
        "is_available", "is_featured", "is_published", "order",
    ]

    @admin.display(description="foto")
    def thumbnail(self, obj):
        return _thumbnail(obj.photo)

    @admin.display(description="vista previa")
    def photo_preview(self, obj):
        return _thumbnail(obj.photo, size=240)

    @admin.display(description="precio", ordering="price")
    def price_display(self, obj):
        return format_gs(obj.price)
