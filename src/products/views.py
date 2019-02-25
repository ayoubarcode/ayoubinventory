#AYOUB AR
# from django.views import ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger , Paginator

from django.http import JsonResponse

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart
from .models import Product, ProductFile
from categories.models import Category

from ecommerce.utils import isUpcExist

from .forms import ProductForm


class ProductFeaturedListView(ListView):
	template_name = "products/list.html"

	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.all().featured()


class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
	queryset = Product.objects.all().featured()
	template_name = "products/featured-detail.html"

	# def get_queryset(self, *args, **kwargs):
	#     request = self.request
	#     return Product.objects.featured()


class UserProductHistoryView(LoginRequiredMixin, ListView):
	template_name = "products/user-history.html"
	def get_context_data(self, *args, **kwargs):
		context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context['cart'] = cart_obj
		return context

	def get_queryset(self, *args, **kwargs):
		request = self.request
		views = request.user.objectviewed_set.by_model(Product, model_queryset=False)
		return views



class ProductListView(ListView):
	template_name = "products/list.html"
	paginate_by = 2

	def get_context_data(self, *args, **kwargs):
		context = super(ProductListView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context['cart'] = cart_obj
		return context

	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.all()


def product_list_view(request):
	queryset = Product.objects.all()
	categories = Category.objects.draft()
	paginator = Paginator(queryset, 18)
	page =  request.GET.get('page')
	page_listings = paginator.get_page(page)
	# for c in categories:
	# 	for  sub in c.subcategory_set.all():
	# 		print('{}: {}'.format(c,sub))

	context = {
		'listings': page_listings,
		'categories':categories,
	}
	return render(request, "products/list.html", context)



class ProductDetailSlugView(ObjectViewedMixin, DetailView):
	queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context['cart'] = cart_obj
		return context

	def get_object(self, *args, **kwargs):
		request = self.request
		slug = self.kwargs.get('slug')

		#instance = get_object_or_404(Product, slug=slug, active=True)
		try:
			instance = Product.objects.get(slug=slug, active=True)
		except Product.DoesNotExist:
			raise Http404("Not found..")
		except Product.MultipleObjectsReturned:
			qs = Product.objects.filter(slug=slug, active=True)
			instance = qs.first()
		except:
			raise Http404("Uhhmmm ")
		return instance

import os
from wsgiref.util import FileWrapper # this used in django
from mimetypes import guess_type

from django.conf import settings
from orders.models import ProductPurchase

class ProductDownloadView(View):
	def get(self, request, *args, **kwargs):
		slug = kwargs.get('slug')
		pk = kwargs.get('pk')
		downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)
		if downloads_qs.count() != 1:
			raise Http404("Download not found")
		download_obj = downloads_qs.first()
		# permission checks

		can_download = False
		user_ready  = True
		if download_obj.user_required:
			if not request.user.is_authenticated:
				user_ready = False

		purchased_products = Product.objects.none()
		if download_obj.free:
			can_download = True
			user_ready = True
		else:
			# not free
			purchased_products = ProductPurchase.objects.products_by_request(request)
			if download_obj.product in purchased_products:
				can_download = True
		if not can_download or not user_ready:
			messages.error(request, "You do not have access to download this item")
			return redirect(download_obj.get_default_url())

		aws_filepath = download_obj.generate_download_url()
		print(aws_filepath)
		return HttpResponseRedirect(aws_filepath)
		# file_root = settings.PROTECTED_ROOT
		# filepath = download_obj.file.path # .url /media/
		# final_filepath = os.path.join(file_root, filepath) # where the file is stored
		# with open(final_filepath, 'rb') as f:
		#     wrapper = FileWrapper(f)
		#     mimetype = 'application/force-download'
		#     gussed_mimetype = guess_type(filepath)[0] # filename.mp4
		#     if gussed_mimetype:
		#         mimetype = gussed_mimetype
		#     response = HttpResponse(wrapper, content_type=mimetype)
		#     response['Content-Disposition'] = "attachment;filename=%s" %(download_obj.name)
		#     response["X-SendFile"] = str(download_obj.name)
		#     return response
		#return redirect(download_obj.get_default_url())




class ProductDetailView(ObjectViewedMixin, DetailView):
	#queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		print(context)
		# context['abc'] = 123
		return context

	def get_object(self, *args, **kwargs):
		request = self.request
		pk = self.kwargs.get('pk')
		instance = Product.objects.get_by_id(pk)
		if instance is None:
			raise Http404("Product doesn't exist")
		return instance

	# def get_queryset(self, *args, **kwargs):
	#     request = self.request
	#     pk = self.kwargs.get('pk')
	#     return Product.objects.filter(pk=pk)


def product_detail_view(request, pk=None, *args, **kwargs):
	# instance = Product.objects.get(pk=pk, featured=True) #id
	# instance = get_object_or_404(Product, pk=pk, featured=True)
	# try:
	#     instance = Product.objects.get(id=pk)
	# except Product.DoesNotExist:
	#     print('no product here')
	#     raise Http404("Product doesn't exist")
	# except:
	#     print("huh?")

	instance = Product.objects.get_by_id(pk)
	if instance is None:
		raise Http404("Product doesn't exist")
	#print(instance)
	# qs  = Product.objects.filter(id=pk)

	# #print(qs)
	# if qs.exists() and qs.count() == 1: # len(qs)
	#     instance = qs.first()
	# else:
	#     raise Http404("Product doesn't exist")

	context = {
		'object': instance
	}
	return render(request, "products/detail.html", context)


def add_product_upc(request):
	if not  request.user.is_staff: 
		return redirect("home")
	form = ProductForm()
	instance = None
	if request.method == 'POST':
		form = ProductForm(request.POST)
		if form.is_valid():
			print(request.POST)
			instance = form.save(commit=False)
			form.save(commit=False)
			print('begein test')
			results ,isexist = isUpcExist(instance.upc)
			if isexist:
				print("Product Found")
				instance.title = results['results'][0]['name']
				instance.price = float(results['results'][0]['sitedetails'][0]['latestoffers'][0]['price'])
				instance.active  = False
				instance.description = results['results'][0]['description']
				instance.image  = results['results'][0]['images'][0]
				print("save final")
				# instance.save()
				# return render(request, 'products/add-product-upc.html',{'form':form})
		else:
			print("Error")
	context= {'form':form,'instance':instance}
	return render(request, 'products/add-product-upc.html',context)