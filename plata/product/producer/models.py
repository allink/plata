from datetime import datetime

from django.db import models
from django.db.models import Sum, signals
from django.utils.translation import ugettext_lazy as _

from plata.product.models import Product

from feincms.translations import TranslatedObjectMixin, Translation

class ProducerManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)


class Producer(models.Model, TranslatedObjectMixin):
    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        app_label = 'product'
        ordering = ['ordering', 'name']
        verbose_name = _('producer')
        verbose_name_plural = _('producers')

    def __unicode__(self):
        return self.name
    
    @property
    def main_image(self):
        if not hasattr(self, '_main_image'):
            try:
                self._main_image = self.images.all()[0]
            except IndexError:
                self._main_image = None
        return self._main_image


class ProducerTranslation(Translation(Producer)):
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('producer translation')
        verbose_name_plural = _('producer translations')

    def __unicode__(self):
        return self.parent.name


class ProducerImage(models.Model):
    producer = models.ForeignKey(Producer, verbose_name=_('producer'),
        related_name='images')
    image = models.ImageField(_('image'),
        upload_to=lambda instance, filename: 'producer/%s/%s' % (instance.producer.slug, filename))
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        ordering = ['ordering']
        verbose_name = _('producer image')
        verbose_name_plural = _('producer images')

    def __unicode__(self):
        return self.image.name

# Note: Important: Changed related_name from "products" to "producers", for consistency.
Product.add_to_class('producer', models.ForeignKey(Producer, blank=True, null=True,
    related_name='producers', verbose_name=_('producer')))