from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from feincms.admin.item_editor import ItemEditor, FEINCMS_CONTENT_FIELDSET

from plata.product.admin import ProductAdmin, ProductVariationInline,\
    ProductPriceInline, ProductImageInline, ProductForm
from plata.product.models import Product
from . import models


import plata
class CMSProductTranslationInline(admin.StackedInline):
    model = models.CMSProductTranslation
    max_num = len(plata.settings.LANGUAGES)


class CMSProductForm(ProductForm):
    class Meta:
        model = models.CMSProduct


class ProductAdmin(ProductAdmin, ItemEditor):
#    fieldsets = [(None, {
#        'fields': ('is_active', 'name', 'slug', 'sku', 'is_featured'),
#        }),
#        FEINCMS_CONTENT_FIELDSET,
#        (_('Properties'), {
#            'fields': ('ordering', 'producer', 'categories',
#                'option_groups', 'create_variations'),
#        }),
#        ]
    form = CMSProductForm
    inlines = [ProductVariationInline, ProductPriceInline, ProductImageInline, CMSProductTranslationInline]
    search_fields = ('translations__name', 'translations__description')
    #list_display = ('is_active', 'is_featured', 'translations__name', 'sku', 'ordering')
    #list_display = ('is_active', 'is_featured', 'name', 'sku', 'ordering')
    #list_display_links = ('name',)
    list_display = ('is_active', 'is_featured', 'sku', 'ordering')
    list_display_links = ('sku',)
    #list_display_links = ('translations__name',)
    #prepopulated_fields = {'slug': ('translations__name',), 'sku': ('translations__name',)}

admin.site.unregister(Product)
admin.site.register(models.CMSProduct, ProductAdmin)
