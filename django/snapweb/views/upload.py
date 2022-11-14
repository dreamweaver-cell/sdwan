import json

import snap.json_validate as Jv
from django import forms
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render
from snap.config import JSON_DEVICE_CONFIG_SCHEMA


class UploadFileForm(forms.Form):
    myfile = forms.FileField(
        required=True,
        label="",
        max_length=50,
    )


def save_file(file: UploadedFile):
    fs = FileSystemStorage()
    fs.save(file.name, file)
    return fs


def json_validation(request):
    errmsg = ""
    myfile = request.FILES['myfile']
    if myfile.multiple_chunks():
        errmsg = "File too big"
    else:
        # Valid json
        try:
            json_cfg_file = json.loads(myfile.read())
        except json.decoder.JSONDecodeError as err:
            errmsg = f"Invalid JSON: {err}"
    if not errmsg:
        # Validate JSON schema
        try:
            Jv.json_validate(json_cfg_file, JSON_DEVICE_CONFIG_SCHEMA)
        except Jv.jsonschema.ValidationError as err:
            errmsg = f"SNAP configfile not valid: {err}"

    return errmsg


def snapconfig_upload(request):
    """upload and verify files to server."""
    myfile = UploadFileForm()
    if request.method == 'POST' and request.FILES:
        filen = UploadFileForm(request.POST, request.FILES)
        if filen.is_valid():
            errmsg = json_validation(request)
            if errmsg:
                messages.error(request, errmsg)
            else:
                save_file(request.FILES['myfile'])
                messages.success(request, "uploaded successfully")

            return render(request, 'upload_file.html', {"form": filen})

    else:
        return render(request, 'upload_file.html', {"form": myfile})
