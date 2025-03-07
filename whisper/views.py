import os
import re

from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import WhisperForm
from .models import Whisper


@login_required(login_url='login')
def home(request):
    whiperInfo = Whisper.objects.all().order_by('-id')
    if request.method == 'GET':
        return render(request, 'home.html', {'whisperInfo':whiperInfo,})
    else:
        return render(request, 'home.html', {})

def whisper(request):
    if request.method == 'POST':
        filled_form = WhisperForm(request.POST, request.FILES)
        if filled_form.is_valid():
            obj = filled_form.save(commit=False)
            obj.submitter = request.user
            filled_form.input_file_path = os.path.join(settings.MEDIA_ROOT, str(filled_form.cleaned_data['input_file_path']))
            obj.input_file_path = filled_form.input_file_path
            print("File path: ",filled_form.input_file_path)
            filled_form.save()
            jobRun(obj.id)
            messages.success(request, 'Success!')
        else:
            print(filled_form.errors)
            messages.error(request, 'Failed!')
        new_form = WhisperForm()
        whiperInfo = Whisper.objects.all().order_by('-id')
        return render(request, 'home.html', {'whisperInfo': whiperInfo, })
    else:
        form = WhisperForm()
        return render(request, 'whisper.html', {'addform': form, })


def jobRun(id):
    cmd = Whisper.objects.get(pk=id)
    command_submit = cmd.name + " " + cmd.model + " " + cmd.output_format + " " + cmd.task + " " + cmd.language + " " + cmd.input_file_path
    print("Command to be submitted: ",command_submit)