# -*- coding: utf-8 -*-

# Import our libs
from .control import (
    wildcardtarget,
    get_salt_client,
    get_api_client,
    )
from .forms import LowdataForm

# Import Python libs
import json

# Import Django libs
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

# Import REST libs
from rest_framework import status


def JsonResponse(content, **kwargs):
    return HttpResponse(
        content=json.dumps(content),
        content_type='application/json',
        **kwargs)

# Externally accessible functions

#@login_required
@wildcardtarget
def ping(request, tgt):
    client = get_salt_client()
    ret = client.cmd(tgt, 'test.ping', ret='json')
    return JsonResponse(ret)

#@login_required
@wildcardtarget
def echo(request, tgt, arg):
    client = get_salt_client()
    ret = client.cmd(tgt, 'test.echo', arg, ret='json')
    return JsonResponse(ret)

#@login_required
def minions_list(request):
    client = get_salt_client()
    ret = client.cmd('*', 'grains.items', ret='json')
    return JsonResponse(ret)

#@login_required
def minions_details(request, tgt):
    client = get_salt_client()
    ret = client.cmd(tgt, 'grains.items', ret='json')
    return JsonResponse(ret)

#@login_required
def jobs_list(request):
    client = get_api_client()
    lowdata = {
        'client': 'runner',
        'fun': 'jobs.list_jobs',
        }
    ret = client.run(lowdata)
    return JsonResponse(ret)

#@login_required
def jobs_details(request, jid):
    client = get_api_client()
    lowdata = {
        'client': 'runner',
        'fun': 'jobs.lookup_jid',
        'jid': jid,
        }
    ret = client.run(lowdata)
    return JsonResponse(ret)

#@login_required
@csrf_exempt
def apiwrapper(request):
    if request.method == 'POST':
        form = LowdataForm(request.POST)

        if form.is_valid():
            client = get_api_client()
            lowdata = {
                'client': form.cleaned_data['client'],
                'tgt': form.cleaned_data['tgt'],
                'fun': form.cleaned_data['fun'],
                'arg': form.cleaned_data['arg'],
                }
            ret = client.run(lowdata)

            return JsonResponse(ret)
        else:
            ret = {
                'status': status.HTTP_400_BAD_REQUEST,
                'return': form.errors,
                }
            return JsonResponse(ret, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        return render(request, 'index.html')
