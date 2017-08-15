# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: views.py
# @Last modified by:   valle
# @Last modified time: 10-Aug-2017
# @License: Apache license vesion 2.0

from django.conf import settings
from tokenapi.decorators import token_required
from tokenapi.http import JsonResponse, JsonError
from themagicapi.controller.addcontroller import AddController
from themagicapi.controller.getcontroller import GetController
from themagicapi.controller.rmcontroller import RmController
from themagicapi.controller.filecontroller import FileController
import json

# Create your views here.
@token_required
def index(request):
    if request.method != 'POST' or not 'data' in request.POST:
        return JsonError("Este servidor solo acepta peticiones POST")
    data = json.loads(request.POST.get("data"))
    fichero = None if not 'docfile' in request.FILES else request.FILES["docfile"]
    JSONResponse = {}
    for name in data.keys():
        if "add" == name:
            JSONRequire = data.get("add")
            if not "db" in JSONRequire:
                return JsonResponse("No se sabe el nombre de la db. Indique una con la Key='db'")
            AddController(JSONRequire=JSONRequire,
                          JSONResponse=JSONResponse, path=settings.PATH_DBS, fichero=fichero)

        if "get" == name:
            JSONRequire = data.get("get")
            if not "db" in JSONRequire:
                return JsonError("No se sabe el nombre de la db. Indique una con la Key='db'")
            GetController(JSONRequire=JSONRequire,
                          JSONResponse=JSONResponse, path=settings.PATH_DBS)

        if "rm" == name:
            JSONRequire = data.get("rm")
            if not "db" in JSONRequire:
                return JsonError("No se sabe el nombre de la db. Indique una con la Key='db'")
            RmController(JSONRequire=JSONRequire,
                         JSONResponse=JSONResponse, path=settings.PATH_DBS)

        if "send_mail" == name:
            datos_mail = data.get("send_mail")
            email(datos_mail, JSONResponse)

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
