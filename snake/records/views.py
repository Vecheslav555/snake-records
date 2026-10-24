from django.shortcuts import render
from .models import Record


def index(request):
    records = Record.objects.all()[:20]
    return render(request, 'records/index.html', {'records': records})