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


class CMSProductTranslation(Translation(CMSProduct)):
    origdescription = models.TextField(verbose_name=_('original description'), blank=True)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('CMSProduct translation')
        verbose_name_plural = _('CMSProduct translations')

    def __unicode__(self):
        return self.description
