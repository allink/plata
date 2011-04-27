from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models

from django import forms

import plata

class ProducerTranslationInline(admin.StackedInline):
    model = models.ProducerTranslation
    max_num = len(plata.settings.LANGUAGES)

    # IMPORTANT: Do NOT put this import anywhere else!
    # It needs to stay exactly here, within class scope an after the line "model = models.CMSProductTranslation"
    from django.db import models
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'class':'mceEditorText'})},
    }

    class Media:
        js = ('js/jquery-1.5.1.min.js',
              'js/tiny_mce/tiny_mce.js',
              'js/tiny_mce_init.js',
        )

class ProducerImageInline(admin.TabularInline):
    model = models.ProducerImage
    extra = 0

admin.site.register(models.Producer,
    inlines = [ProducerImageInline, ProducerTranslationInline],
    list_display=('is_active', 'name', 'ordering'),
    list_display_links=('name',),
    prepopulated_fields={'slug': ('name',)},
    search_fields=('name', 'translations__description'),
    )

product_admin = admin.site._registry.get(models.Product)
if product_admin:
    product_admin.list_display += ('producer',)
    product_admin.list_filter += ('producer',)
