from django.shortcuts import render


def index(request):
    return render(request, 'index.jinja2')


def vue_index(request):
    return render(request, "vue_base.jinja2")
