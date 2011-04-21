from django.utils.translation import get_language, ugettext_lazy as _

from feincms.models import Base

from plata.product.models import Product, ProductManager

from django.db import models
from feincms.translations import TranslatedObjectMixin, Translation

class CMSProduct(Product, Base, TranslatedObjectMixin):
    class Meta:
        app_label = 'product'
        verbose_name = _('product')
        verbose_name_plural = _('products')

    objects = ProductManager()

    def __unicode__(self):
        return self.translation.name

class CMSProductTranslation(Translation(CMSProduct)):
    name = models.CharField(_('name'), max_length=100, blank=True) # make it blank=True
    origdescription = models.TextField(verbose_name=_('original description'), blank=True)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        # use parent__ordering instead of ordering
        #ordering = ['ordering', 'name']
        ordering = ['parent__ordering', 'name']
        verbose_name = _('CMSProduct translation')
        verbose_name_plural = _('CMSProduct translations')

    def __unicode__(self):
        return self.name
