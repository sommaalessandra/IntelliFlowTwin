import json
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from .models import Device
import os
from django.http import FileResponse, Http404
from pathlib import Path
from datetime import datetime

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
    selected_date = request.GET.get('date', '')

    today = datetime.now().date()
    default_date = today.strftime('%Y-%m-%d')

    selected_time_range = request.GET.get('time_range', '')
    # Selezione della fascia oraria: ottieni gli orari di inizio e fine dalla selezione
    start_time = None
    end_time = None
    if selected_time_range:
        start_time_str, end_time_str = selected_time_range.split('-')
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

    # List of folders containing 'basic' or 'congestioned' in the name
    folders = [f for f in os.listdir(base_dir) if selected_type in f and os.path.isdir(os.path.join(base_dir, f))]
    filtered_folders = []
    for folder in folders:
        # Estrai la data e l'ora dal nome della cartella
        folder_date_str = folder.split('_')[0]  # Es. 2024-10-08
        folder_time_str = folder.split('_')[1]  # Es. 12-29-03
        folder_date = datetime.strptime(folder_date_str, '%Y-%m-%d').date()
        folder_time = datetime.strptime(folder_time_str, '%H-%M-%S').time()


        # Filtra in base alla selezione dell'utente
        if selected_date and folder_date != datetime.strptime(selected_date, '%Y-%m-%d').date():
            continue

        # Filtra in base alla fascia oraria monoraria
        if start_time and end_time and not (start_time <= folder_time <= end_time):
            continue

        filtered_folders.append(folder)


    context = {
        'folders': filtered_folders,
        'selected_type': selected_type,
        'selected_date': selected_date,
        'selected_time_range': selected_time_range,
        'default_date': default_date,
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


