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

import logging
logger = logging.getLogger('plata_shop')

class CMSProductForm(ProductForm):

    class Meta:
        model = models.CMSProduct

    def save(self, *args, **kwargs):
        instance = super(CMSProductForm, self).save(*args, **kwargs)
        instance._cleaned_data = self.cleaned_data
        return instance

class CMSProductAdmin(ProductAdmin, ItemEditor):
    # NOTE: we can't use 'name' (doesn't exist anymore) or 'translations__name' (ambiguous ForeignKey relation) as 'fields' here
    fieldsets = [(None, {
        'fields': ('is_active', 'slug', 'sku', 'is_featured'),
        }),
        FEINCMS_CONTENT_FIELDSET,
        (_('Properties'), {
            'fields': ('ordering', 'producer', 'categories',
                'option_groups', 'create_variations'),
        }),
        ]

    form = CMSProductForm
    inlines = [ProductVariationInline, ProductPriceInline, ProductImageInline, CMSProductTranslationInline]
    search_fields = ('translations__name', 'translations__description')
    # NOTE: we can't use 'name' (doesn't exist anymore) or 'translations__name' (ambiguous ForeignKey relation) here
    list_display = ('is_active', 'is_featured', 'sku', 'ordering')
    list_display_links = ('sku',)
    # NOTE: prepopulated_fields doesn't accept ForeignKey fields (ambiguous), we thus can't prepopulate the slug and sku for new products.
    #prepopulated_fields = {'slug': ('translations__name',), 'sku': ('translations__name',)}

admin.site.unregister(Product)
admin.site.register(models.CMSProduct, CMSProductAdmin)
