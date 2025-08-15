import os
import re

from datetime import datetime

from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.context_processors import request
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
    command_submit = cmd.name + " --model " + cmd.model + " --output_format " + cmd.output_format + " --" + cmd.task + " --language " + cmd.language + " " + cmd.input_file_path
    print("Command to be submitted: ",command_submit)
    lines = ["#!/bin/bash \n",
             "#$ -N whisper \n",
             "#$ -cwd \n",
             "#$ -q cuda.q \n",
             "#$ -S /bin/bash \n",
             "#$ -M mldproc \n",
             "#$ -m beas \n",
             "module purge \n",
             "module load ffmpeg \n",
             "module load miniconda/3.2021.10 \n",
             "conda activate whisper \n",
             command_submit,
             "\n"
             ]
    print(lines)
    time_now = datetime.now().strftime('%m%d%Y_%H%M%S')
    filename = cmd.name + "_"+ request.__name__+ "_"+ time_now+ ".sge"
    filepath = os.path.join(settings.FILE_RUN_FOLDER, filename)
    print("Filename: ",filename)
    print("Filepath: ",filepath)

    os.makedirs(settings.FILE_RUN_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

    try:
        with open(filepath, 'x') as f:
            for line in lines:
                f.write(line)
    except FileExistsError:
        print("File already exists")
    finally:
        print("File created successfully")
        os.system("qsub " + filename)
        print("qsub submitted successfully")
