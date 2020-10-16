from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.db.models import Q, F


CATEGORY_CHOICES = [
	("S", "Shirt"),
	("SW", "Sport wear"),
	("OW", "Outwear")
]


LABEL_CHOICES = [
	("P", "primary"),
	("S", "secondary"),
	("D", "danger")
]

class UserProfile(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
	one_click_purchasing = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username
		

class Item(models.Model):
	category = models.CharField(choices=CATEGORY_CHOICES, max_length=300, null=True)
	title = models.CharField(max_length=300)
	image = models.ImageField(upload_to='shirts', null=True)
	price = models.FloatField()
	description = models.TextField()
	discount_price = models.FloatField(blank=True, null=True)
	label = models.CharField(choices=LABEL_CHOICES, max_length=300, null=True)
	slug = models.CharField(max_length=100)


	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("mobiles:product", kwargs={
			'slug':self.slug
		})

	def get_add_to_cart_url(self):
		return reverse("mobiles:add-to-cart", kwargs={
			'slug':self.slug
		})

	def get_remove_from_cart_url(self):
		return reverse("mobiles:remove-from-cart", kwargs={
			'slug':self.slug
		})


class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return f"{self.quantity} of {self.item.title}"

	def get_total_item_price(self):
		return self.quantity * self.item.price

	def get_total_discount_item_price(self):
		return self.quantity * self.item.discount_price

	def get_amount_saved(self):
		return self.get_total_item_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_discount_item_price()
		return self.get_total_item_price()


class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)
	payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)
	coupon = models.ForeignKey('CouponCode', on_delete=models.SET_NULL, null=True, blank=True)
	being_delivered = models.BooleanField(default=False)
	recieved = models.BooleanField(default=False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)

	'''
	1. ITEM ADD TO CART
	2. ADDING ADDRESS
	   (FAILED CHECKOUT)
	3. PAYMENT
	(packaging)	
	4. BEING DELIVERED
	5. RECIEVED
	6. REFUNDS 
	'''
	def __str__(self):
		return self.user.username

	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		if self.coupon and total>1:
			total -= self.coupon.amount
		return total


class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	street_address = models.CharField(max_length=200)
	address_line2 = models.CharField(max_length=200)
	state = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	pin_code = models.CharField(max_length=6)
	default = models.BooleanField(default=False)

	def __str__(self):
		return self.street_address

	class Meta:
		verbose_name_plural = 'Addresses'


class Payment(models.Model):
	stripe_charge_id = models.CharField(max_length=100, null=True, blank=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
	amount = models.FloatField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username


class CouponCode(models.Model):
	code = models.CharField(max_length=15)
	valid_from = models.DateTimeField(null=True, blank=True)
	valid_to = models.DateTimeField(null=True, blank=True)
	amount = models.FloatField()
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.code


class Refund(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	reason = models.TextField()
	accepted = models.BooleanField(default=False)
	email = models.EmailField()

	def __str__(self):
		return f"{self.pk}"


def userprofile_reciever(sender, instance, created,*args, **kwargs):
	if created:
		userprofile = UserProfile.objects.create(user=instance)

post_save.connect(userprofile_reciever, sender=settings.AUTH_USER_MODEL)
