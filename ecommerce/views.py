from django.shortcuts import render


def home_page(request):
    context= {}
    if request.user.is_authenticated:
        context['premium'] = "Secret"
    return render(request, 'home.html', context)
