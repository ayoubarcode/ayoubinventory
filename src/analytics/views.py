#AYOUB AR
import random
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import render

from django.utils import  timezone


from orders.models import Order
from products.models import Product
from billing.models import BillingProfile
from accounts.models import User
class SalesAjaxView(View):
	def get(self, request, *args, **kwargs):
		data = {}
		if request.user.is_staff:
			qs = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=5)
			if request.GET.get('type') == 'week':
				days = 7
				start_date = timezone.now().today() - datetime.timedelta(days=days-1)
				datetime_list = []
				labels = []
				salesItems = []
				for x in range(0, days):
					new_time = start_date + datetime.timedelta(days=x)
					datetime_list.append(
							new_time
						)
					labels.append(
						new_time.strftime("%a") # mon
					)
					new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
					day_total = new_qs.totals_data()['total__sum'] or 0
					salesItems.append(
						day_total
					)
				#print(datetime_list)

				data['labels'] = labels
				data['data'] = salesItems
			if request.GET.get('type') == '4weeks':
				data['labels'] = ["Four Weeks Ago", "Three Weeks Ago", "Two Weeks Ago", "Last Week", "This Week"]
				current = 5
				data['data'] = []
				for i in range(0, 5):
					new_qs = qs.by_weeks_range(weeks_ago=current, number_of_weeks=1)
					sales_total = new_qs.totals_data()['total__sum'] or 0
					data['data'].append(sales_total)
					current -= 1
		return JsonResponse(data)



class SalesView(LoginRequiredMixin, TemplateView):
	template_name = 'analytics/sales.html'

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		if not user.is_staff:
			return render(self.request, "400.html", {})
		return super(SalesView, self).dispatch(*args, **kwargs)


	def get_context_data(self, *args, **kwargs):
		context = super(SalesView, self).get_context_data(*args, **kwargs)
		qs = Order.objects.all().by_weeks_range(weeks_ago=10, number_of_weeks=10)

		start_date = timezone.now().date() - datetime.timedelta(hours=24)
		end_date = timezone.now().date() + datetime.timedelta(hours=12)
		today_data = qs.by_range(start_date=start_date, end_date=end_date).get_sales_breakdown()
		context['today'] = today_data
		context['this_week'] = qs.by_weeks_range(weeks_ago=1, number_of_weeks=1).get_sales_breakdown()
		context['last_four_weeks'] = qs.by_weeks_range(weeks_ago=5, number_of_weeks=4).get_sales_breakdown()
		context['users']  = User.objects.all().filter(is_active=True).count()
		context['orders'] = Order.objects.all().filter(status='paid').count()
		return context

def go_dashboard(request):
	return render(request,'analytics/dashboard.html',{})


def product_list_view_admin(request):
	if request.user.is_staff:
		queryset = Product.objects.all()
		context = {
			'products': queryset,
			'title': 'All products'
		}
	return render(request, "analytics/products.html", context)



def customer_list_view(request):
	if request.user.is_staff and request.user.is_authenticated:
		customers = BillingProfile.objects.all()
		context = {
			'customers':customers,
			'Title': 'Customers',
		}
	return  render(request, "analytics/customers.html", context)


def order_list_view(request):
	if request.user.is_staff and request.user.is_authenticated:
		orders = Order.objects.all()
		context = {
			'orders':orders,
			'Title': 'All Orders',
		}
	return  render(request, "analytics/orders.html", context)
