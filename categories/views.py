from django.views.generic import View
from django.http import JsonResponse

from .models import Category
from carts.models import Cart


class CategoriesAjaxView(View):
    def get(self, *args, **kwargs):
        data = {}
        categories = Category.objects.all()
        data['categories'] = [{'url': c.get_absolute_url(),
                              'title': c.title}
                              for c in categories]
        return JsonResponse(data)
