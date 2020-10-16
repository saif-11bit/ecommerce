from django import forms

STATES = [
	('', 'Choose...'),
	('bih', 'BIHAR'),
	('del', 'DELHI'),
]

CITIES = [
	('', 'Choose...'),
	('pat', 'PATNA'),
	('nd', 'NEW DELHI'),
]


PAYMENT_METHOD = [
	('stripe', 'Stripe Card'),
	('paypal', 'PAYPAL'),
	('razorpay', 'RazorPay')
]

class CheckoutForm(forms.Form):
	street_address = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': '1234 Main St','class':'form-control'}))
	address_line2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment or suite','class':'form-control'}))
	state = forms.CharField(required=False,widget=forms.Select(choices=STATES, attrs={'class':'custom-select d-block w-100'}))
	city = forms.CharField(required=False,widget=forms.Select(choices=CITIES, attrs={'class':'custom-select d-block w-100'}))
	pin_code = forms.CharField(required=False,max_length=6, widget=forms.TextInput(attrs={'placeholder': '12345','class':'form-control'}))
	set_default_address = forms.BooleanField(required=False)
	use_default_address = forms.BooleanField(required=False)
	payment_option = forms.ChoiceField(widget=forms.RadioSelect,choices=PAYMENT_METHOD)


class CouponForm(forms.Form):
	code = forms.CharField(label='',widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': 'Promo code',
		'aria-label':"Recipient's username",
		'aria-describedby':"basic-addon2"
	}))


class RefundForm(forms.Form):
	ref_code = forms.CharField()
	message = forms.CharField(widget=forms.Textarea(attrs={
		'rows': 4
	}))
	email = forms.EmailField()

class PaymentForm(forms.Form):
    # stripeToken = forms.CharField(required=False)
    # save = forms.BooleanField(required=False)
    # use_default = forms.BooleanField(required=False)
    razorpay_order_id = forms.CharField(required=False)
    razorpay_payment_id = forms.CharField(required=False)
    razorpay_signature = forms.CharField(required=False)
	