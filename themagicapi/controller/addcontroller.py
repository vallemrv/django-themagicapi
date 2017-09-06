# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: addcontroller.py
# @Last modified by:   valle
# @Last modified time: 04-Sep-2017
# @License: Apache license vesion 2.0

from valleorm.models import Models
from filecontroller import FileController

class AddController():
    def __init__(self, JSONResponse, JSONRequire, fichero=None):
        self.JSONResponse = JSONResponse
        self.JSONRequire = JSONRequire
        self.fichero = fichero

        self.db = JSONRequire.get("db")
        for k, v in JSONRequire.items():
            if k == "db":
                pass
            elif type(v) is list:
                for row in v:
                    for kr, vr in row.items():
                        self.actionAdd(vr, kr)
            else:
                self.actionAdd(v, k)

    def actionAdd(self, row_req, tb):
        self.JSONResponse["add"] = {tb: []}
        row, relations = self.modifyRow(row_req, tb)
        row.save()
        row_send = row.toDICT()
        if len(relations) <= 0 and self.fichero:
            filecontroller = FileController(db=self.db)
            rowfile = filecontroller.addFile(row, self.fichero)
            row_send[row.tableName] = rowfile
        for relation in relations:
            nameKey = relation["fieldName"] if 'fieldName' in relation else relation["relationName"]
            _rows = []
            if not nameKey in row_send:
                row_send[nameKey] = []
            if type(row_req[nameKey]) is dict:
                _rows = [row_req[nameKey]]
            else:
                _rows = row_req[nameKey]
            for r in _rows:
                if relation["relationTipo"] == "MANY":
                    child, relchild = self.modifyRow(r, nameKey, relationship={
                        'relationName': tb,
                        'relationTipo': "ONE",
                    })
                else:
                    tbName = relation["relationName"]
                    child, relchild = self.modifyRow(r[tbName], tbName)
                    child.save()

                getattr(row, nameKey).add(child)
                child_send = child.toDICT()
                if self.fichero:
                    filecontroller = FileController(db=self.db)
                    rowfile = filecontroller.addFile(child, self.fichero)
                    child_send = rowfile

                row_send[nameKey].append(child_send)


        self.JSONResponse["add"][tb].append(row_send)

    def modifyRow(self, row_json, tb, relationship=None):
        model = {}
        row = None
        if "ID" in row_json:
            row = Models(dbName=self.db, tableName=tb)
            row.loadByPk(row_json.get("ID"))
        else:
            if Models.exitsTable(dbName=self.db, tableName=tb):
                model = Models.getModel(dbName=self.db, tableName=tb)
                model = self.repare_model(model=model, row=row_json, tb=tb)
            else:
                model = self.create_model(row_json)
                if relationship:
                    model["relationship"].append(relationship)
            row = Models(dbName=self.db, tableName=tb, model=model)
        relations = []
        for key, v in row_json.items():
            if type(row_json[key]) is list  or type(v) is dict:
                fieldName = key
                relationName = key
                childs = row_json[key]
                tipo = "MANY"
                child = childs[0] if type(v) is list else childs
                for kr, vr in  child.items():
                    if type(vr) is dict:
                        tipo = "MANYTOMANY"
                        relationName = kr
                        break;
                    else:
                        break;

                rship = {
                    'fieldName': fieldName,
                    'relationName': relationName,
                    'relationTipo': tipo,
                }
                relations.append(rship)
            else:
                setattr(row, key, v)

        if len(relations) > 0:
            row.appendRelations(relations)
        return row, relations

    def repare_model(self, model, row, tb):
        for key, v in row.items():
            if not type(v) is list  and not type(v) is dict:
                search = filter(lambda field: field['fieldName'] == key, model["fields"])
                if len(search) <= 0:
                    default, tipo = self.getTipo(v)
                    field = {
                        'fieldName': key,
                        'fieldDato': default,
                        'fieldTipo': tipo
                    }
                    model['fields'].append(field)
                    Models.alter(dbName=self.db, tableName=tb, field=field)

        return model

    def create_model(self, row):
        model = {"fields":[], "relationship": []}

        for key, v in row.items():
            if not type(v) is list and not type(v) is dict:
                default, tipo = self.getTipo(v)
                model["fields"].append({
                 'fieldName': key,
                 'fieldDato': default,
                 'fieldTipo': tipo
                })

        return model




    def getTipo(self, val):
        val = self.canConvert(val, op='int')
        val = self.canConvert(val, op='float')
        if type(val) is unicode:
            return ("None", "TEXT")
        elif type(val) is float:
            return (None, "REAL")
        elif type(val) is int:
            return (None, "INTEGER")
        else:
            return ("None", "TEXT")



    def canConvert(self, value, op='int'):
        try:
            if type(value) is unicode:
                if op == 'int':
                    value = int(value)
                if op == 'float' and value.find(".") > 0:
                    value = float(value)
            return value
        except ValueError:
             return value
