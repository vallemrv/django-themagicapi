# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Filename: rmcontroller.py
# @Last modified by:   valle
# @Last modified time: 04-Sep-2017
# @License: Apache license vesion 2.0

from valleorm.models import Models
from filecontroller import FileController

class RmController():
    def __init__(self, JSONResponse, JSONRequire):
        self.JSONResponse = JSONResponse
        self.JSONRequire = JSONRequire
        self.db = JSONRequire.get("db")
        for k, v in JSONRequire.items():
            if k == "db":
                pass
            elif type(v) is list:
                self.JSONResponse['rm'] = {k: []}
                for item in v:
                    self.actionGet(item, k)
            else:
                self.JSONResponse['rm'] = {k: []}
                self.actionGet(v, k)



    def actionGet(self, condition, tb):
        if not Models.exitsTable(self.db, tb):
            return ''
        row = Models(dbName=self.db, tableName=tb)
        if "ID" in condition:
            row.loadByPk(condition["ID"])
            response = {'num':"remove:" +'1' if row.ID > 0 else '0' , 'ID': row.ID}
            rmRoot = True
            for col, val in condition.items():
                if type(condition[col]) is dict:
                    rmRoot = False
                    modelCondition, subQuery = self.getModelQuery(val)
                    rows = getattr(row, col).get(modelCondition)
                    response = {'num':"remove "+str(len(rows)), 'IDs': []}

                    for child in rows:
                        response["IDs"].append(child.ID)
                        if FileController.hasFile(child):
                            fileController = FileController(db=self.db)
                            row_send = fileController.rmFile(child)

                        getattr(row, col).remove(child)

            if rmRoot:
                if FileController.hasFile(row):
                    fileController = FileController(db=self.db)
                    row_send = fileController.rmFile(row)

                row.remove()

            self.JSONResponse["rm"][tb].append(response)

        else:
            mainCondition, subQuery = self.getModelQuery(condition)
            numRemoveRow = 0
            for rowMain in row.getAll(condition=mainCondition):
                if len(subQuery) > 0:
                    for nodeCondition, fieldName in subQuery:
                        subNodeCondition, nothing = self.getModelQuery(nodeCondition)
                        rows = getattr(rowMain, fieldName).get(subNodeCondition)
                        if len(rows) > 0:
                            response = {}
                            response[fieldName] = [{'num':"remove "+str(len(rows)), 'IDs': []}]
                            for row in rows:
                                if FileController.hasFile(row):
                                    fileController = FileController(db=self.db)
                                    row_send = fileController.rmFile(row)

                                getattr(rowMain, fieldName).remove(row)
                                response[fieldName]['IDs'].append(row.ID)

                            self.JSONResponse["rm"][tb].append(response)
                else:
                    numRemoveRow += 1
                    self.JSONResponse["rm"][tb].append({'num':"remove: "+str(numRemoveRow), 'ID': rowMain.ID})
                    if FileController.hasFile(rowMain):
                        fileController = FileController(db=self.db)
                        row_send = fileController.rmFile(rowMain)

                    rowMain.remove()

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
