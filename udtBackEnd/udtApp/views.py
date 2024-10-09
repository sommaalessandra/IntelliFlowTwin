import json
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from .models import Device
import os
from django.http import FileResponse, Http404
from pathlib import Path

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
    # Prendi il parametro 'type' dalla querystring
    device_type = request.GET.get('type', '')

    device_types = sorted(Device.objects.distinct('_id.type'))
    print(device_types)
    # Filtro per il tipo di dispositivo, se specificato
    if device_type:
        # deviceList = Device.objects.filter(_id__type__exact=device_type)
        deviceList = Device.objects.filter(__raw__={'_id.type': {'$regex': f".*{device_type}$"}})
    else:
        deviceList = Device.objects.all()

    print(f"Devices count: {deviceList.count()}")
    paginator = Paginator(deviceList, 10)
    pageNumber = request.GET.get('page')

    page_obj = paginator.get_page(pageNumber)

    context = {
        'page_obj': page_obj,
        'device_types': device_types,
        'request': request,  # Necessario per mantenere il filtro durante la paginazione
    }

    if deviceList:
        return render(request, 'udtApp/entityList.html', context)
    else:
        return HttpResponse("There is no device inside the DB")

def simulation(request):

    # Getting the absolute path of the scenarioCollection folder
    current_dir = os.path.abspath(os.getcwd())
    current_path = Path(current_dir).resolve()
    project_root = current_path.parent
    base_dir = project_root / 'SUMO' / 'joined' / 'scenarioCollection'

    # Get the selected type (in the page filter). Default is 'basic'
    selected_type = request.GET.get('type', 'basic')

    # List of folders containing 'basic' or 'congestioned' in the name
    folders = [f for f in os.listdir(base_dir) if selected_type in f and os.path.isdir(os.path.join(base_dir, f))]

    context = {
        'folders': folders,
        'selected_type': selected_type,
    }
    return render(request, 'udtApp/simulation.html', context)


def serve_image(request, folder):

    current_dir = os.path.abspath(os.getcwd())
    current_path = Path(current_dir).resolve()
    project_root = current_path.parent
    base_dir = project_root / 'SUMO' / 'joined' / 'scenarioCollection'
    folder_path = os.path.join(base_dir, folder)


    # Filter only .png files
    images = [img for img in os.listdir(folder_path) if img.endswith(".png")]

    # Get the selected type (in the page filter). Default is 'basic'
    selected_type = request.GET.get('type', 'basic')

    context = {
        'folder': folder,
        'images': images,
        'selected_type': selected_type,
        'base_dir': base_dir
    }
    return render(request, 'udtApp/simulationScenario.html', context)


