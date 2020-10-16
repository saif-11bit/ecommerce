from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, OrderItem, Order, Address, Payment, CouponCode, Refund, UserProfile
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
import random
import string
import stripe
import razorpay

client = razorpay.Client(auth=("id", "secret_key"))

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class HomeView(ListView):
	model = Item
	paginate_by = 8
	context_object_name = 'items'
	template_name = 'index.html'


class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):

		try:
			order = Order.objects.get(user=self.request.user,ordered=False )
			context = {
				'object': order
			}
			return render(self.request, 'order_detail.html', context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You donot have an active order")
			return redirect("/")


class ItemDetailView(DetailView):
	model = Item
	context_object_name = 'item'
	template_name = 'product-page.html'


def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid


class CheckoutView(LoginRequiredMixin, View):
	def get(self,*args, **kwargs):
		# form
		form = CheckoutForm()

		try:
			order= Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'form': form,
				'order':order,
				'couponForm':CouponForm(),
			}

			address_qs = Address.objects.filter(
				user=self.request.user,
				default=True,
			)
			
			if address_qs.exists():
				context.update( {'default_address': address_qs.last()} )

			return render(self.request, 'checkout-page.html', context)

		except ObjectDoesNotExist:
			messages.info(request, "You donot have an active order!")
			return redirect('mobiles:checkout')


	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		# print(self.request.POST)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				use_default_address = form.cleaned_data.get('use_default_address')
				if use_default_address:
					print('Using default address!')
					address_qs = Address.objects.filter(
						user=self.request.user,
						default=True,
					)
					if address_qs.exists():
						address = address_qs.first()
						order.address=address
						order.save()						
					else:
						messages.info(self.request, 'No default address available!')
						return redirect('mobiles:checkout')
				else:
					print('user is entering new shipping address!')


					street_address = form.cleaned_data.get('street_address')
					address_line2 = form.cleaned_data.get('address_line2')
					state = form.cleaned_data.get('state')
					city = form.cleaned_data.get('city')
					pin_code = form.cleaned_data.get('pin_code')
					

					if is_valid_form([street_address,state,city,pin_code]):		

						address=Address(
							user=self.request.user,street_address=street_address,address_line2=address_line2,state=state,city=city,pin_code=pin_code
						)
						address.save()

						order.address=address
						order.save()

						set_default_address = form.cleaned_data.get('set_default_address')
						if set_default_address:
							address.default = True
							address.save()

					else:
						messages.info(self.request, 'Please fill required Address fields!')

				payment_option = form.cleaned_data.get('payment_option')
				if payment_option == 'stripe':
					return redirect('mobiles:payment', payment_option='stripe')
				elif payment_option == 'razorpay':
					return redirect('mobiles:payment', payment_option='razorpay')

				else:
					messages.warning(self.request, "failed checkout")
					return redirect('mobiles:checkout')

		except ObjectDoesNotExist:
			messages.warning(self.request, "You donot have an active order")
			return redirect("/")


@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False
	)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if order items in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, "The item quantity was updated.")
			return redirect('mobiles:order-summary')
		else:
			order.items.add(order_item)
			messages.info(request, "This item was added to the cart.")
			return redirect('mobiles:product', slug=slug)

	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to the cart.")
		return redirect('mobiles:product', slug=slug)


@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if order items in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item =OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This item was removed from your cart.")
			return redirect('mobiles:order-summary')
		else:
			# order doesn't contain this order item
			messages.info(request, "This item was not in your cart.")
			return redirect('mobiles:product', slug=slug)
			
	else:
		# user doesn't have an order
		messages.info(request, "You donot have active order.")
		return redirect('mobiles:product', slug=slug)


@login_required
def remove_single_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if order items in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item =OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated!")
			return redirect('mobiles:order-summary')
		else:
			# order doesn't contain this order item
			messages.info(request, "This item was not in your cart.")
			return redirect('mobiles:product', slug=slug)
			
	else:
		# user doesn't have an order
		messages.info(request, "You donot have active order.")
		return redirect('mobiles:product', slug=slug)


class PaymentView(LoginRequiredMixin, View):

	def get(self, *args, **kwargs):
		# order
		order= Order.objects.get(user=self.request.user, ordered=False)
		amount = int(order.get_total()*100)
		order_amount = amount
		order_currency = 'INR'
		order_receipt = 'order_rcptid_11'
		# notes = {'Shipping address': 'Bommanahalli, Bangalore'}

		razo = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, payment_capture='0'))
		print(razo)
		if order.address:
			context = {
				'order':order,
				'razo': razo['id'],
			}
			# userprofile = self.request.user.userprofile
			# if userprofile.one_click_purchasing:

			# 	cards = stripe.Customer.list_sources(
			# 		userprofile.stripe_customer_id,
			# 		limit=3,
			# 		object='card'
			# 	)
			# 	card_list = cards['data']
			# 	if len(card_list)>0:
			# 		context.update({
			# 			'card':card_list[0]
			# 		})
			return render(self.request, 'payment.html', context)
		else:
			messages.warning(self.request, "You have not added your address!")
			return redirect('mobiles:checkout')


	def post(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		form = PaymentForm(self.request.POST)
		userprofile = UserProfile.objects.get(user=self.request.user)

		if form.is_valid():
			razorpay_order_id = form.cleaned_data.get('razorpay_order_id')
			razorpay_payment_id = form.cleaned_data.get('razorpay_payment_id')
			razorpay_signature = form.cleaned_data.get('razorpay_signature')
			params_dict = {
				'razorpay_order_id': razorpay_order_id,
				'razorpay_payment_id': razorpay_payment_id,
				'razorpay_signature': razorpay_signature
			}
			client.utility.verify_payment_signature(params_dict)

			amount = int(order.get_total()*100)

			payment = Payment()
			# payment.stripe_charge_id = charge['id']
			payment.user = self.request.user
			payment.amount = amount
			payment.save()

			# assign payment to the order

			order_items = order.items.all()
			order_items.update(ordered=True)
			for item in order_items:
				item.save()

				order.ordered = True
				order.payment = payment
				order.ref_code = create_ref_code()
				order.save()

				messages.success(self.request, "Your order was successful!")
				return redirect("/")			


			# token = form.cleaned_data.get('stripeToken')
			# save = form.cleaned_data.get('save')
			# use_default = form.cleaned_data.get('use_default')
			# print(token)

			# if save:
			# 	if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
			# 		customer = stripe.Customer.retrieve(userprofile.stripe_customer_id)
			# 		customer.sources.create(source=token)

			# 	else:
			# 		customer = stripe.Customer.create(
			# 			email=self.request.user.email,
			# 		)
			# 		customer.sources.create(source=token)
			# 		userprofile.stripe_customer_id = customer['id']
			# 		userprofile.one_click_purchasing = True
			# 		userprofile.save()

			# amount = int(order.get_total()*100)

			# try:
			# 	if use_default or save:					
			# 		charge = stripe.Charge.create(
			# 			amount=amount,
			# 			currency="inr",
			# 			customer=userprofile.stripe_customer_id,
			# 			description='Software development services',
			# 		)

			# 	else:
			# 		charge = stripe.Charge.create(
			# 			amount=amount,
			# 			currency="inr",
			# 			source=token,
			# 			description='Software development services',
			# 		)

			# create the payment


			# except stripe.error.CardError as e:
			# 	# Since it's a decline, stripe.error.CardError will be caught

			# 	messages.warning(self.request, f"{e.error.message}")
			# 	return redirect("/")
			# except stripe.error.RateLimitError as e:
			# 	# Too many requests made to the API too quickly
			# 	messages.warning(self.request, "Rate Limit Error")
			# 	return redirect("/")
			# except stripe.error.InvalidRequestError as e:
			# 	# Invalid parameters were supplied to Stripe's API
			# 	messages.warning(self.request, "Invalid Request Error")
			# 	return redirect("/")
			# except stripe.error.AuthenticationError as e:
			# 	# Authentication with Stripe's API failed
			# 	# (maybe you changed API keys recently)
			# 	messages.warning(self.request, "Not Authenticated")
			# 	return redirect("/")
			# except stripe.error.APIConnectionError as e:
			# 	# Network communication with Stripe failed
			# 	messages.warning(self.request, "Network error")
			# 	return redirect("/")
			# except stripe.error.StripeError as e:
			# 	# Display a very generic error to the user, and maybe send
			# 	# yourself an email
			# 	messages.warning(self.request, "Something went wrong!Please try again")
			# 	return redirect("/")
			# except Exception as e:
			# 	# send an email to ourselves
			# 	messages.warning(self.request, "A serious error occured!We have been notified!")
			# 	return redirect("/")


def get_coupon(request, code):
	now = timezone.now()
	print(now)
	try:
		coupon = CouponCode.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now,active=True)
		return coupon

	except ObjectDoesNotExist:
		messages.info(request, "This Coupon Does not exists!")
		return redirect('mobiles:checkout')

		
class AddCouponView(View):
	def post(self,*args, **kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():
			try:
				code = form.cleaned_data.get('code')
				order= Order.objects.get(user=self.request.user, ordered=False)

				order.coupon = get_coupon(self.request, code)
				order.save()
				messages.success(self.request, "Successfully Added Coupon!")
				return redirect("mobiles:checkout")

			except ObjectDoesNotExist:
				messages.info(self.request, "You donot have an active order!")
				return redirect('mobiles:checkout')


class RequestRefundView(LoginRequiredMixin, View):

	def get(self, *args, **kwargs):
		form = RefundForm()
		context = {
			'form': form
		}
		return render(self.request, 'request-refund.html', context)

	def post(self, *args, **kwargs):
		form = RefundForm(self.request.POST)
		if form.is_valid():
			ref_code = form.cleaned_data.get('ref_code')
			message = form.cleaned_data.get('message')
			email = form.cleaned_data.get('email')

			try:
				order = Order.objects.get(ref_code=ref_code)
				order.refund_requested = True
				order.save()

				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()
				messages.info(self.request, "Your request was recieved")
				return redirect("/")
				

			except ObjectDoesNotExist:
				messages.info(self.request, "This order doesnot exist")
				return redirect("/")


class OrderedView(View):
	def get(self,*args, **kwargs):

		order = OrderItem.objects.filter(user=self.request.user,ordered=True )
			# context = {
			# 	'object': order
			# }
		# for o in order:
		# 	# print(o)
		# 	for i in o.items.all():
		# 		print(i)
		# for o in order:
		# 	print(o)

		context = {
			'ordered_items': order
		}
		return render(self.request, 'ordered_items.html', context)