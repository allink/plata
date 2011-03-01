from datetime import date, datetime

from django.db import models
from django.db.models import Q, Count

from django.utils.translation import ugettext_lazy as _

import plata
from plata.compat import product as itertools_product
from plata.fields import CurrencyField

#import sys
#import feincms
#print "---------------------------------------------------------"
#print feincms
#print "---------------------------------------------------------"
#print sys.path
#print "---------------------------------------------------------"
from feincms.translations import TranslatedObjectMixin, Translation

class TaxClass(models.Model):
    name = models.CharField(_('name'), max_length=100)
    rate = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    priority = models.PositiveIntegerField(_('priority'), default=0,
        help_text = _('Used to order the tax classes in the administration interface.'))

    class Meta:
        ordering = ['-priority']
        verbose_name = _('tax class')
        verbose_name_plural = _('tax classes')

    def __unicode__(self):
        return self.name


class CategoryManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def public(self):
        return self.filter(is_active=True, is_internal=False)


class Category(models.Model, TranslatedObjectMixin):
    is_active = models.BooleanField(_('is active'), default=True)
    is_internal = models.BooleanField(_('is internal'), default=False,
        help_text=_('Only used to internally organize products, f.e. for discounting.'))

    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    description = models.TextField(_('description'), blank=True)

    parent = models.ForeignKey('self', blank=True, null=True,
        limit_choices_to={'parent__isnull': True},
        related_name='children', verbose_name=_('parent'))

    class Meta:
        ordering = ['parent__ordering', 'parent__name', 'ordering', 'name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    objects = CategoryManager()

    def __unicode__(self):
        if self.parent_id:
            return u'%s - %s' % (self.parent, self.name)
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('plata_category_detail', (), {'object_id': self.pk})


class CategoryTranslation(Translation(Category)):
    teasertext = models.TextField(verbose_name=_('teasertext'), blank=True)
    
    class Meta:
        verbose_name = _('category translation')
        verbose_name_plural = _('category translations')

    def __unicode__(self):
        return self.teasertext


class CategoryImage(models.Model):
    category = models.ForeignKey(Category, verbose_name=_('category'),
        related_name='images')
    image = models.ImageField(_('image'),
        upload_to=lambda instance, filename: 'categories/%s/%s' % (instance.category.slug, filename))
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        ordering = ['ordering']
        verbose_name = _('category image')
        verbose_name_plural = _('category images')

    def __unicode__(self):
        return self.image.name


class OptionGroup(models.Model):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        ordering = ['id']
        verbose_name = _('option group')
        verbose_name_plural = _('option groups')

    def __unicode__(self):
        return self.name


class Option(models.Model):
    group = models.ForeignKey(OptionGroup, related_name='options',
        verbose_name=_('option group'))
    name = models.CharField(_('name'), max_length=100)
    value = models.CharField(_('value'), max_length=100)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        ordering = ['group', 'ordering']
        verbose_name = _('option')
        verbose_name_plural = _('options')

    def __unicode__(self):
        return self.name

    def full_name(self):
        return u'%s - %s' % (self.group, self.name)


class ProductManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def featured(self):
        return self.active().filter(is_featured=True)

    def bestsellers(self, queryset=None):
        queryset = queryset or self
        return queryset.annotate(sold=Count('variations__orderitem')).order_by('-sold')

    def also_bought(self, product):
        return self.bestsellers(
            self.exclude(id=product.id).exclude(variations__orderitem__isnull=True
                ).filter(variations__orderitem__order__items__variation__product=product))


#class Product(models.Model):
class Product(models.Model, TranslatedObjectMixin):
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)

    categories = models.ManyToManyField(Category,
        verbose_name=_('categories'), related_name='products',
        blank=True, null=True)
    description = models.TextField(_('description'), blank=True)
    option_groups = models.ManyToManyField(OptionGroup, related_name='products',
        blank=True, null=True, verbose_name=_('option groups'))

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = _('product')
        verbose_name_plural = _('products')

    objects = ProductManager()

    def __unicode__(self):
        # if name were in ProductTranslation, we'd use this:
        #return "%s" % (self.translation.name)
        return self.name

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.slug
        super(Product, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('plata_product_detail', (), {'object_id': self.pk})

    @property
    def main_image(self):
        if not hasattr(self, '_main_image'):
            try:
                self._main_image = self.images.all()[0]
            except IndexError:
                self._main_image = None
        return self._main_image

    def get_price(self, currency=None, quantity=1, **kwargs):
        # TODO Refactor. Method not optimized for performance etc. at all.
        kwargs['currency'] = currency or plata.shop_instance().default_currency()
        stagger_prices = self.get_prices(**kwargs)
        # assumption: stagger_prices is sorted in reverse numeric order
        for my_currency, my_staggered_price in stagger_prices:
            if (my_currency == currency) and (quantity >= my_staggered_price['stagger']):
                # assume the sales price is lower than the normal price
                if my_staggered_price['sale']:
                    return my_staggered_price['sale']
                else:
                    if my_staggered_price['normal']:
                        return my_staggered_price['normal']
                    else:
                        raise "Strange error: Both the sales and normal price are None"


    
    def get_prices(self, **kwargs):
        # TODO Refactor. Method not optimized for performance etc. at all.
        # NOTE: We also handle **kwargs as we use this function in get_price(..) which allowed **kwargs
        from django.core.cache import cache
        key = 'product-prices-%s' % self.pk
        if cache.has_key(key):
            return cache.get(key)

        prices = []
        for currency in plata.settings.CURRENCIES:
            try:
                # return all active prices (including stagger prices) for this product and currency
                normal = self.prices.active().filter(currency=currency).filter(**kwargs)
            except self.prices.model.DoesNotExist:
                continue
            
            # determine the unique stagger categories for this product on-the-fly
            stagger_categories = []
            for temp_price in normal:
                if not temp_price.stagger in stagger_categories:
                    stagger_categories.append(temp_price.stagger)
            stagger_categories.sort(reverse=True)

            # get this product's latest normal and sales price for each stagger category we found
            # and append them to the price list to be returned
            for current_stagger_category in stagger_categories:
                normal_price = sales_price = None
                try:
                    normal_price = self.prices.active().filter(is_sale=False, currency=currency, stagger=current_stagger_category).filter(**kwargs).latest()
                except self.prices.model.DoesNotExist:
                    pass
                try:
                    sales_price = self.prices.active().filter(is_sale=True, currency=currency, stagger=current_stagger_category).filter(**kwargs).latest()
                except self.prices.model.DoesNotExist:
                    pass
                prices.append((currency, {
                    'normal': normal_price,
                    'sale': sales_price,
                    'stagger': current_stagger_category,
                    }))

        cache.set(key, prices)
        return prices

    def in_sale(self, currency):
        # TODO doesn't get used anywhere
        prices = dict(self.get_prices())
#        print "currency: %s" % currency
#        print "prices[currency]['sale']: %s" % prices[currency]['sale']
        if currency in prices and prices[currency]['sale']:
            return True
        return False

    def create_variations(self):
        variations = itertools_product(*[group.options.all() for group in self.option_groups.all()])

        for idx, variation in enumerate(variations):
            try:
                qset = self.variations
                for o in variation:
                    qset = qset.filter(options=o)

                instance = qset.get()
            except ProductVariation.DoesNotExist:
                parts = [self.sku]
                parts.extend(o.value for o in variation)
                instance = self.variations.create(
                    is_active=self.is_active,
                    sku=u'-'.join(parts),
                    )
                instance.options = variation

            instance.ordering = idx
            instance.save()

    def items_in_stock(self):
        items = {}

        for variation in self.variations.all():
            key = '_'.join(str(pk) for pk in variation.options.values_list('pk', flat=True))
            items[key] = variation.items_in_stock

        return items


class ProductTranslation(Translation(Product)):
    descriptiontest = models.TextField(verbose_name=_('descriptiontest'), blank=True)
    
    class Meta:
        verbose_name = _('product translation')
        verbose_name_plural = _('product translations')

    def __unicode__(self):
        return self.descriptiontest


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations')
    is_active = models.BooleanField(_('is active'), default=True)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    items_in_stock = models.IntegerField(_('items in stock'), default=0)
    options = models.ManyToManyField(Option, related_name='variations',
        blank=True, null=True, verbose_name=_('options'))
    options_name_cache = models.CharField(_('options name cache'), max_length=100,
        blank=True, editable=False)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        ordering = ['ordering', 'product']
        verbose_name = _('product variation')
        verbose_name_plural = _('product variations')

    def __unicode__(self):
        if self.options_name_cache:
            return u'%s (%s)' % (self.product, self.options_name_cache)
        return u'%s' % self.product

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def _regenerate_cache(self, options=None):
        if options is None:
            options = self.options.all()

        self.options_name_cache = u', '.join(unicode(o) for o in options)

    def can_delete(self):
        return self.orderitem_set.count() == 0

    def available(self, exclude_order=None):
        if exclude_order:
            return self.stock_transactions.items_in_stock(self,
                query=Q(order__isnull=True) | ~Q(order=exclude_order))
        else:
            return self.stock_transactions.items_in_stock(self, update=True)


class ProductPriceManager(models.Manager):
    def active(self):
        return self.filter(
            Q(is_active=True),
            Q(valid_from__lte=date.today()),
            Q(valid_until__isnull=True) | Q(valid_until__gte=date.today()))


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='prices')
    currency = CurrencyField()
    _unit_price = models.DecimalField(_('unit price'), max_digits=18, decimal_places=10)
    tax_included = models.BooleanField(_('tax included'),
        help_text=_('Is tax included in given unit price?'),
        default=plata.settings.PLATA_PRICE_INCLUDES_TAX)
    tax_class = models.ForeignKey(TaxClass, verbose_name=_('tax class'))
    stagger = models.PositiveIntegerField(_('stagger'), default=1,
        help_text = _('Price applicable when ordering at least x items. Used for stagger pricing.'))
    is_active = models.BooleanField(_('is active'), default=True)
    valid_from = models.DateField(_('valid from'), default=date.today)
    valid_until = models.DateField(_('valid until'), blank=True, null=True)

    is_sale = models.BooleanField(_('is sale'), default=False,
        help_text=_('Set this if this price is a sale price. Whether the sale is temporary or not does not matter.'))

    class Meta:
        get_latest_by = 'id'
        ordering = ['-valid_from']
        verbose_name = _('product price')
        verbose_name_plural = _('product prices')

    objects = ProductPriceManager()

    def __unicode__(self):
        return u'%s %.2f' % (self.currency, self.unit_price)

    @property
    def unit_tax(self):
        return self.unit_price_excl_tax * (self.tax_class.rate/100)

    @property
    def unit_price_incl_tax(self):
        if self.tax_included:
            return self._unit_price
        return self._unit_price * (1+self.tax_class.rate/100)

    @property
    def unit_price_excl_tax(self):
        if not self.tax_included:
            return self._unit_price
        return self._unit_price / (1+self.tax_class.rate/100)

    @property
    def unit_price(self):
        if plata.settings.PLATA_PRICE_INCLUDES_TAX:
            return self.unit_price_incl_tax
        else:
            return self.unit_price_excl_tax


class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='images')
    image = models.ImageField(_('image'),
        upload_to=lambda instance, filename: 'products/%s/%s' % (instance.product.slug, filename))
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        ordering = ['ordering']
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    def __unicode__(self):
        return self.image.name
