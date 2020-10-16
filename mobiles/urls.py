from django.urls import path
from .views import HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_from_cart,CheckoutView, PaymentView, AddCouponView, RequestRefundView, OrderedView

app_name = 'mobiles'

urlpatterns = [
	path('', HomeView.as_view(), name='item-list'),
	path('product/<slug>/', ItemDetailView.as_view(), name='product'),
	path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
	path('checkout/', CheckoutView.as_view(), name='checkout'),
	path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
	path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
	path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
	path('remove-single-from-cart/<slug>/', remove_single_from_cart, name='remove-single-from-cart'),
	path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
	path('ordered-items/', OrderedView.as_view(), name='ordered-items'),
	path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]