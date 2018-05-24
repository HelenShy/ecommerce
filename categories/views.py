from django.views.generic import View, ListView
from django.http import JsonResponse

from .models import Category, Collection
from carts.models import Cart


class CategoriesAjaxView(View):
    def get(self, *args, **kwargs):
        data = {}
        categories = Category.objects.all()
        data['categories'] = [{'url': c.get_absolute_url(),
                              'title': c.title}
                              for c in categories]
        return JsonResponse(data)


class CollectionListView(ListView):
    queryset = Collection.objects.all()
    template_name = 'categories/collections-list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CollectionListView, self).get_context_data(*args, **kwargs)
        collections = Collection.objects.show_on_home_page().all()
        context['collections'] = collections
        return context
