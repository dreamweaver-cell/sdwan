import json

import snap.json_validate as Jv
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render


def sdwan_config_uploader(request):
    # upload and verify files to server

    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        # Validate Json Schema
        uploaded_file_url = fs.url(filename)
        read_cfg_file = open(uploaded_file_url, "r")
        json_cfg_file = json.load(read_cfg_file)
        schema_result = None
        try:
            schema_result = Jv.json_validate(json_cfg_file, settings.JSON_DEVICE_TEMPLATE)
        except Jv.jsonschema.ValidationError as ex:
            if len(ex.path) > 0:
                schema_result = ex
                fs.delete(uploaded_file_url)

        # validation_status = file_validator(uploaded_file_url)
        return render(request, 'file_upload.html', {
            'uploaded_file_url': uploaded_file_url,
            'schema_result': schema_result,
        })
    return render(request, 'file_upload.html')
