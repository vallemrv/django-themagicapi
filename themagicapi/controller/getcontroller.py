# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: getcontroller.py
# @Last modified by:   valle
# @Last modified time: 04-Sep-2017
# @License: Apache license vesion 2.0

from valleorm.models import Models
from filecontroller import FileController

class GetController():
    def __init__(self, JSONResponse, JSONRequire):
        self.JSONResponse = JSONResponse
        self.JSONRequire = JSONRequire

        JSONResponse['get'] = []

        self.db = JSONRequire.get("db")
        for k, v in JSONRequire.items():
            if k == "db":
                pass
            elif k == "rows":
                rows = JSONRequire.get("rows")
                for row in rows:
                    for kr, vr in row.items():
                        self.actionGet(vr, kr)
            else:
                self.actionGet(v, k)



    def actionGet(self, condition, tb):
        self.JSONResponse['get'] = {tb: []}
        if not Models.exitsTable(self.db, tb):
            return ''
        row = Models(dbName=self.db, tableName=tb)
        if "ID" in condition:
            row.loadByPk(condition["ID"])
            row_send = row.toDICT()
            if FileController.hasFile(row):
                fileController = FileController(db=self.db)
                row_send = fileController.getFile(row)

            response = row_send
            for col, val in condition.items():
                if type(condition[col]) is list and len(condition[col]) > 0:
                    condition[col] = condition[col][0]
                    val = condition[col]
                if type(condition[col]) is dict:
                    modelCondition, subQuery = self.getModelQuery(val)
                    if hasattr(row, col):
                        rows = getattr(row, col).get(modelCondition)
                        response[col] = []
                    else:
                        rows = []
                        response[col] = []
                    for child in rows:
                        child_send = child.toDICT()
                        if FileController.hasFile(child):
                            fileController = FileController(db=self.db)
                            child_send = fileController.getFile(child)

                        response[col].append(child_send)

            self.JSONResponse["get"][tb].append(response)

        else:
            mainCondition, subQuery = self.getModelQuery(condition)

            for rowMain in row.getAll(condition=mainCondition):
                if len(subQuery) > 0:
                    for nodeCondition, fieldName in subQuery:
                        subNodeCondition, nothing = self.getModelQuery(nodeCondition)
                        rows = getattr(rowMain, fieldName).get(subNodeCondition)
                        if len(rows) > 0:
                            rowMain_send = rowMain.toDICT()
                            if FileController.hasFile(rowMain):
                                fileController = FileController(db=self.db)
                                rowMain_send = fileController.getFile(rowMain)

                            response = rowMain_send
                            response[fieldName] = []
                            for row in rows:
                                row_send = row.toDICT()
                                if FileController.hasFile(row):
                                    fileController = FileController(db=self.db)
                                    row_send = fileController.getFile(row)

                                response[fieldName].append(row_send)

                            self.JSONResponse["get"][tb].append(response)
                else:
                    rowMain_send = rowMain.toDICT()
                    if FileController.hasFile(rowMain):
                        fileController = FileController(db=self.db)
                        rowMain_send = fileController.getFile(rowMain)

                    self.JSONResponse["get"][tb].append(rowMain_send)

    def getModelQuery(self, condition):
        modelCondition = {}
        query = []
        subQuery = []
        for col, val in condition.items():
            isWordReserver = col == 'columns' or col == 'limit' or col == 'offset'
            isWordReserver = isWordReserver or col == 'query' or col == 'order'
            isWordReserver = isWordReserver or col == 'joins' or col == 'group'
            if isWordReserver:
                modelCondition[col] = val
            elif not isWordReserver and type(condition[col]) is dict :
                subQuery.append((condition[col], col))
            else:
               packQuery = self.getPackQuery(col, val)
               query.append(packQuery)
        if 'query' in modelCondition and len(query) > 0:
            modelCondition['query'] += " AND "+" AND ".join(query)
        elif len(query) > 0:
            modelCondition["query"] = " AND ".join(query)

        return modelCondition, subQuery

    def getPackQuery(self, col, val):
        if type(val) is unicode:
            return col + " LIKE '"+val+"'"
        elif type(val) is float:
            return col + "="+val
        elif type(val) is int:
            return col + "="+val
        else:
            return col + " LIKE '"+val+"'"
