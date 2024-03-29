#AYOUB AR
from django.contrib import admin

from .models import Product, ProductFile


class ProductFileInline(admin.TabularInline):
	model = ProductFile
	extra = 1


class ProductAdmin(admin.ModelAdmin):
	list_display = ['__str__', 'slug', 'is_digital','category','sub_category','price','pretty_date','active']
	list_editable = ['category','sub_category','active']
	inlines = [ProductFileInline]
	class Meta:
		model = Product

admin.site.register(Product, ProductAdmin)
