import json

from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Device
from django.template import loader

def index(request):
    return render(request, 'udtApp/index.html', {'nbar': 'home'})

def monitor(request):
    # TODO: modify the grafana dashboard
    return render(request, 'udtApp/monitor.html', {'nbar': 'monitor'})

def entity(request, entity_id):
    device = Device.objects(_id__id=entity_id).first()
    print(device)
    if device:
    # return HttpResponse("This is the page where the entity %s is shown" % entity_id)
        return render(request, 'udtApp/entity.html', {'device': device})
        # return HttpResponse(device)
    else:
        return HttpResponse("No device found with this ID", status=404)

def entityList(request):
    deviceList = Device.objects.all()

    paginator = Paginator(deviceList, 10)
    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    if deviceList:
        return render(request, 'udtApp/entityList.html', {'page_obj': page_obj})
    else:
        return HttpResponse("There is no device inside the DB")

def simulation(request):
    # TODO: a page were last simulation result are shown (maybe start a new simulation here?)
    return HttpResponse("Simulation Page")