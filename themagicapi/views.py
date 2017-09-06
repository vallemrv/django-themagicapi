# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: views.py
# @Last modified by:   valle
# @Last modified time: 06-Sep-2017
# @License: Apache license vesion 2.0


from django.conf import settings
from tokenapi.decorators import token_required
from tokenapi.http import JsonResponse, JsonError
from valleorm.models import QSonHelper
from valleorm.django.models import QSonHelper as QSonHelperDjango
import json

# Create your views here.
@token_required
def index(request):
    if request.method != 'POST' or not 'data' in request.POST:
        return JsonError("Este servidor solo acepta peticiones POST")
    data = json.loads(request.POST.get("data"))
    fichero = None if not 'docfile' in request.FILES else request.FILES["docfile"]
    JSONResponse = {}
    THEMAGIC_PATH_DBS = settings.THEMAGIC_PATH_DBS
    if "send_mail" in data:
        datos_mail = data.get("send_mail")
        email(datos_mail, JSONResponse)

    qson_helper = QSonHelper(path=THEMAGIC_PATH_DBS)

    JSONResponse = qson_helper.decode_qson(data)
    http = JsonResponse(JSONResponse)
    return http



# Create your views here.
@token_required
def qson_django(request):
    if request.method != 'POST' or not 'data' in request.POST:
        return JsonError("Este servidor solo acepta peticiones POST")
    data = json.loads(request.POST.get("data"))
    JSONResponse = {}
    default_db = settings.DATABASES["default"]["NAME"]
    if "send_mail" in data:
        datos_mail = data.get("send_mail")
        email(datos_mail, JSONResponse)

    qson_helper = QSonHelperDjango(dbName=default_db)

    JSONResponse = qson_helper.decode_qson(data)
    http = JsonResponse(JSONResponse)

    return http



@token_required
def getfiles(request):
    if request.method != 'POST' or not 'ID' in request.POST:
        return JsonError("Este servidor solo acepta peticiones POST")

    id_file = request.POST["ID"]
    path = FileController.getPath(id_file)
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    return JsonError("Pagina no encontrada o un error inesperado")


def email(datos, JSONResponse):
    from django.core.mail import send_mail
    try:
        send_mail(datos.get("subject"), datos.get("men"), datos.get("from"),
                  [datos.get("to")], fail_silently=False)
        JSONResponse["send_mail"] = {"success": True}
    except:
        JSONResponse["send_mail"] = {"success": False}
