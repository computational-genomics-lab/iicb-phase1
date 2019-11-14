from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
import os
import mysql.connector
import json
from pickle import GET
from django.core import serializers
import array
from django.http import response
import base64
from . import DBUtils
from . import Defaults
import pprint
import operator
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from django.conf import settings
print=settings.LOGGER.info # once in each module
print("Logging is configured in views.")


tree_query = """SELECT distinct(orders) FROM organism order by  orders"""
list_query = """SELECT * FROM organism  order by species"""


#
# Internal function:
# creates a dict for display in 1st page (tree or list view) from the row (each output row from database)
#
def _cerate_species_dict(row):
    # <a href = '$path'>$row2[2] $row2[3] (V$row2[12])<span style='color:red'>$row2[13]</span></a>
    species = row[2]
    strain = row[3]
    version = str(row[12])
    # print('name', species)
    # print('species', strain)
    d = {}
    d['label'] = species + ' ' + strain + ' (V' + version + ')'
    # HREF parameters
    # $path = "/cgi-bin/eumicrobedb/browserUI.cgi?
    # scaffold=$scaffold
    # &startbase=1&stopbase=150000
    # &organism=".$row2[1].
    # "&version=".$row2[11].
    # "&action=refresh&action_params=1";
    if row[14] is None:
        scaffold = "Scaffold_1"
    else:
        scaffold = str(row[14]) + "1"
    d['scaffold'] = scaffold
    d['organism'] = row[1]
    d['version'] = row[11]
    d['star'] = row[13]
    d['startbase'] = 1
    d['stopbase'] = 150000

    return d


tree_genus_query = """SELECT distinct(genus) FROM organism where orders = """
tree_species_query = """SELECT * FROM organism where genus = """
tree_species_query_oderby = """order by species"""

# Function to be called from Web

@api_view(['GET'])
def gettreedata(request):

    db = DBUtils.MariaConnection('SRES')

    order_db_list = DBUtils.MariaGetData(db, tree_query)
    print("order_db_list: {}".format(order_db_list))

    # get data from result set
    odrer_list = []
    lev_1 = 0

    for order_iter in order_db_list:
        lev_1 = lev_1 + 1
        order = {}
        order['id'] = 'folder' + str(lev_1)
        order['label'] = order_iter[0]

        genus_db_list = DBUtils.MariaGetData(db, tree_genus_query + "'" + order_iter[0] + "'")

        genus_list = []

        lev_2 = 0
        for genus_iter in genus_db_list:
            lev_2 = lev_2 + 1
            # <label> $row1[0] < / label > < input type='checkbox' id='subfolder$folder_no.$no_of_sub'
            genus = {}
            genus['id'] = 'subfolder' + str(lev_1) + "." + str(lev_2)
            genus['label'] = genus_iter[0]

            species_db_list = DBUtils.MariaGetData(db, tree_species_query + "'" + genus_iter[0] + "'" + tree_species_query_oderby)

            species_list = []
            for species_iter in species_db_list:
                species = _cerate_species_dict(species_iter)
                species_list.append(species)

            genus['species'] = species_list
            genus_list.append(genus)

        order['genus_list'] = genus_list
        odrer_list.append(order)

    DBUtils.MariaClose(db)

    data = json.dumps(odrer_list)
    print(data)

    json_resp = {'List':odrer_list}
    return Defaults.FinalResponse(json_resp)


# Function to be called from Web
@api_view(['GET'])
def getlistdata(request):
    db = DBUtils.MariaConnection('SRES')
    results = DBUtils.MariaGetData(db, list_query)
    DBUtils.MariaClose(db)
    print("RESULT:{}".format(results))

    # get data from result set
    json_list = []

    for row in results:
        d = _cerate_species_dict(row)
        json_list.append(d)

    data = json.dumps(json_list)
    print(data)

    json_resp = {'List':json_list}
    return Defaults.FinalResponse(json_resp)


@api_view(['GET'])
def GetData_Usage_Policy(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from FixedDataUsagePolicy where Line_Status=1 order by Line_No"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)

    #l_body = request.body

    lines = []
    for line in result:
        oneline = {}
        oneline['Line_No'] = line[0]
        oneline['Line_Text'] = line[1]
        oneline['Line_Status'] = 1

        lines.append(oneline)

    return Defaults.FinalResponse({'lines':lines})


@api_view(['POST'])
def SetData_Usage_Policy(request):
    
    db = DBUtils.MariaConnection('IICB')
    
    #
    # extract json from request
    # expected format of payload in POST call
    #    {"lines":[{"Line_No":5, "Line_Text":"aaa", "Line_Status":1},
    #              {"Line_No":6, "Line_Text":"bbb", "Line_Status":0}]}
    #

    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    ##print("JSON DATA:\n", jsondata) #### print(jsondata)


    #if isinstance(jsondata['Line_No'], str):
     #   jsondata['Line_No'] = int(jsondata['Line_No'])
    #if isinstance(jsondata['Line_Text'], str):
     #   jsondata['Line_Text'] = int(jsondata['Line_Text'])
    #if isinstance(jsondata['Line_Status'], str):
     #   jsondata['Line_Status'] = int(jsondata['Line_Status'])
    

    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into FixedDataUsagePolicy (Line_No,Line_Text,Line_Status) values(%s,%s,%s)"
        replace_tuple = (eachLine['Line_No'], eachLine['Line_Text'], eachLine['Line_Status'])
        results = DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        #print("RESULTS********************\n", results)
        print("Record Inserted successfully")

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})


@api_view(['GET'])
def GetData_News(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from FixedDataNews"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)

    items = []
    for row in result:
        items.append({'Line_No': row[0], 'Line_Text': row[1], 'Line_Status': row[2], 'Line_Format': row[3]})

    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})


@api_view(['POST'])
def SetData_News(request):
    db = DBUtils.MariaConnection('IICB')

    #
    # extract json from request
    # expected format of payload in POST call
    #    {"lines":[{"Line_No":5, "Line_Text":"aaa", "Line_Status":1, "Line_Format":"BOLD"},
    #              {"Line_No":6, "Line_Text":"bbb", "Line_Status":0, "Line_Format":"BOLD"}]}
    #

    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)

    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into FixedDataNews (Line_No,Line_Text,Line_Status,Line_Format) values(%s,%s,%s,%s)"
        replace_tuple = (eachLine['Line_No'], eachLine['Line_Text'], eachLine['Line_Status'], eachLine['Line_Format'])
        #print(sql_parameterized_query)
        results= DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        print("Record Inserted successfully")

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})



@api_view(['GET'])
def GetDataAbout(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from FixedDataAbout"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)

    items = []
    for row in result:
        items.append({'About_Id': row[0], 'About_Text': row[1], 'About_Status': row[2]})

    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})


@api_view(['POST'])
def SetDataAbout(request):
    db = DBUtils.MariaConnection('IICB')

    #
    # extract json from request
    # expected format of payload in POST call
    #    {"lines":[{"Line_No":5, "Line_Text":"aaa", "Line_Status":1},
    #              {"Line_No":6, "Line_Text":"bbb", "Line_Status":0}]}
    #

    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)

    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into FixedDataAbout (About_Id,About_Text,About_Status) values(%s,%s,%s)"
        replace_tuple = (eachLine['About_Id'], eachLine['About_Text'], eachLine['About_Status'])
        print(sql_parameterized_query)
        results= DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        print("Record Inserted successfully")

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})


@api_view(['GET'])
def GetAboutUs(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from AboutUs"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)

    items = []
    for row in result:
        items.append({'AboutUs_Id': row[0], 'AboutUs_Type_No': row[1], 'AboutUs_Type_Name': row[2], 'AboutUs_Person_Name': row[3], 'Person_Brief_Bio': row[4], 'Person_Interests': row[5], 'Person_ContactInfo': row[6], 'AboutUs_Status': row[7]})

    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})


@api_view(['POST'])
def SetAboutUs(request):
    db = DBUtils.MariaConnection('IICB')


    # extract json from request
    # expected format of payload in POST call
    # {"lines":[{"AboutUs_Id":4, "AboutUs_Type_No":3, "AboutUs_Type_Name":"Masters Students", "AboutUs_Person_Name":"Pranab Basu",
    # "Person_Brief_Bio":"This Application is under development stage in Azure Software","Person_Interests":"Analytics, Machine Learning","Person_ContactInfo":"prnb01@gmail.com","Person_Photo":"NULL","AboutUs_Status":1}]}


    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)

    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into AboutUs (AboutUs_Id,AboutUs_Type_No,AboutUs_Type_Name,AboutUs_Person_Name,Person_Brief_Bio,Person_Interests,Person_ContactInfo,AboutUs_Status) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        replace_tuple = (eachLine['AboutUs_Id'], eachLine['AboutUs_Type_No'], eachLine['AboutUs_Type_Name'], eachLine['AboutUs_Person_Name'], eachLine['Person_Brief_Bio'], eachLine['Person_Interests'], eachLine['Person_ContactInfo'], eachLine['AboutUs_Status'])
        #print(sql_parameterized_query)
        results=DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        # Save the incoming BASE64 string from the expected JSON to a given PATH
        image_64_decode = base64.decodestring(eachLine['Person_Photo'].encode())
        filename = Defaults.ABOUT_US_PATH + str(eachLine['AboutUs_Id']) + ".jpg"
        print("\n\n",filename)
        with open(filename, "wb+") as fp:
            fp.write(image_64_decode)
        print("RESULT:{}".format(results))
        print("Record Inserted successfully")

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})


@api_view(['GET'])
def GetHelp(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from HelpPage"
    #sql_parameterized_query = "select HelpPage.*,HelpQuesAns.* from HelpPage,HelpQuesAns"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)

    lines = []
    for line in result:
        oneline = {}
        oneline['Help_Id'] = line[0]
        oneline['Help_Heading'] = line[1]
        oneline['Released_On_Month'] = line[2]
        oneline['Released_On_Year'] = line[3]
        oneline['Help_Status'] = line[4]   
        lines.append(oneline)
#    items = []
#    for row in result:
#        items.append({'Help_Id': row[0], 'Help_Heading': row[1], 'Released_On_Month': row[2], 'Released_On_Year': row[3], 'Help_Status': row[4]})

    return Defaults.FinalResponse({'lines':lines})

#    print(json.dumps({'items': items}))
#    return JsonResponse({'items': items})



@api_view(['GET'])
def GetHelpQuesAns(request):
    db = DBUtils.MariaConnection('IICB')

    sql_parameterized_query = "select * from HelpQuesAns"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)
    
    print("\n\n+++++++++++    Result of Help QnA    +++++++++++++\n\n{}".format(result))

    items = []
    inner_items = []
    for row in result:
        inner_items.append({'Question': row[4], 'Answer': row[5]})
    for row in result:
        items.append({'HelpQuesAns_Id': row[0], 'Question_Type_No': row[1], 'Question_Type_Name': row[2], 'Question_ID': row[3], 'qa': inner_items, 'Answer_Image': row[6], 'HelpQuesAns_Status': row[7]})
        break
    
    print("\n\nITEMS : \n{}".format(items))
#    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})

#@api_view(['GET'])
#def GetHelpQuesAns(request):
#    db = DBUtils.MariaConnection('IICB')
#
#    sql_parameterized_query = "select * from HelpQuesAns"
#    result = DBUtils.MariaGetData(db, sql_parameterized_query)
#    DBUtils.MariaClose(db)
#    HelpQuesAns_Id,Question_Type_No,Question_Type_Name,Question_ID,Question_Text,Answer_Text,Answer_Image,HelpQuesAns_Status=zip(*result)
#    print("\n\n+++++++++++    Result of Help QnA    +++++++++++++\n\n",result)
#    inner_inner_items=[]
#    inner_inner_items_new=[]
#    for x in set(Question_Type_No):
#        inner_inner_item_dict={'Question_id':None,'Qusetion_no':None,'Question':None, 'Answer':None,'Answer_image':None}
#        inner_inner_items=[]
#        for row in result:
#            if x==row[1]:
#            
#                inner_inner_item_dict.update({'Question_id':row[0],'Qusetion_no':row[3],'Question': row[4], 'Answer': row[5],'Answer_image':row[6]})
#                inner_inner_items.append(inner_inner_item_dict)
#                inner_inner_item_dict={'Question_id':None,'Qusetion_no':None,'Question':None, 'Answer':None,'Answer_image':None}
#            inner_inner_items_new.append(inner_inner_items)
#    inner_item=[]
#    inner_item_dict={}
#    for x in set(Question_Type_No):
#        inner_item_dict={}
#            #print(x)
#        inner_item_dict={'Question_Type':None,'Qusetion_Type_no':None,'Status':None, 'qa':None}
#        inner_item_dict.update({'Question_Type':list(Question_Type_Name)[x-1],'Qusetion_Type_no':x,'Status':list(HelpQuesAns_Status)[x-1],'qa':inner_inner_items_new[x-1]})
#        inner_item.append(inner_item_dict)
#        item={}
#    for z in range(len(set(Question_Type_No))):
#        item.update({'item'+str(z+1):inner_item[z]})
#    print("*******************************************")
#    items={}
#    
#    sorted_d = sorted(item.items(), key=operator.itemgetter(0))
#    items={"items":sorted_d}
#    print("\n\nITEMS : \n",items)
#    return Defaults.FinalResponse({'items': items})



@api_view(['POST'])
def SetHelpPage(request):
    db = DBUtils.MariaConnection('IICB')

    # extract json from request
    # expected format of payload in POST call
    # {"lines":[{"Help_Id":2, "Help_Heading":"EUMICROBEDB.ORG V12.0", "Released_On_Month":"October", "Released_On_Year":2016,"Help_Status":1}]}

    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print("JSON DATA:\n{}".format(jsondata))

    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into HelpPage (Help_Id,Help_Heading,Released_On_Month,Released_On_Year,Help_Status) values(%s,%s,%s,%s,%s)"
        replace_tuple = (eachLine['Help_Id'], eachLine['Help_Heading'], eachLine['Released_On_Month'], eachLine['Released_On_Year'], eachLine['Help_Status'])
        #print("RESULT*******************\n", sql_parameterized_query)
        results=DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        print("RESULTS********************\n{}".format(results))
        print("Record Inserted successfully")

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})


@api_view(['POST'])
def SetHelpQuesAns(request):
    db = DBUtils.MariaConnection('IICB')

    #expected format of paylod in post call
    #{"lines":[{"HelpQuesAns_Id":2, "Question_Type_No":3, "Question_Type_Name":"XXXX", "Question_ID":4,"Question_Text":"porpeorpoepror bewbhj","Answer_Text":"Rtjrekjrektjrek mnjregfj","Answer_Image":"NULL","HelpQuesAns_Status":1}]}
    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)
    
    
    for key in jsondata.keys():
        for ele in jsondata[key]:
            Question_type_no = ele.get('Question_type_no')
            Question_type = ele.get('Question_type')
            Status = ele.get('Status')
            for ele_2 in ele.keys():
                if ele_2 == 'qa':
                    for ele_3 in ele[ele_2]:
                        HelpQuesAns_Id = ele_3.get('Question_id')
                        print('\n\n'%s, HelpQuesAns_Id)
                        Question_no = ele_3.get('Question_no')
                        print("\n\n%s", Question_no)
                        Question = ele_3.get('Question')
                        print(Question)
                        Answer = ele_3.get('Answer')
                        print(Answer)
                        Answer_image = ele_3.get('Answer_image')
                        print(Answer_image)

                        sql_parameterized_query = "REPLACE into HelpQuesAns (HelpQuesAns_Id,Question_Type_No,Question_Type_Name,Question_ID,Question_Text,Answer_Text,Answer_Image,HelpQuesAns_Status) values(%s,%s,%s,%s,%s,%s,%s,%s)"
#                sql_parameterized_query = "REPLACE into HelpQuesAns (HelpQuesAns_Id,Question_Type_No,Question_Type_Name,Question_ID,Question_Text,Answer_Text,Answer_Image,HelpQuesAns_Status) values(%s,%s,%s,%s,%s,%s,%s,%s)"
                        replace_tuple = (HelpQuesAns_Id,Question_type_no, Question_type, Question_no, Question, Answer, Answer_image, Status)
#                replace_tuple = (eachLine['HelpQuesAns_Id'], eachLine['Question_type_no'], eachLine['Question_type'], eachLine['Question_no'], eachLine['Question'], eachLine['Answer'], eachLine['Answer_image'], eachLine['Status'])
            
                #print(sql_parameterized_query)
                        results=DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
                        print("Record Inserted successfully")
                    
                

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})



@api_view(['GET'])
def GetArchivePage(request):
    db = DBUtils.MariaConnection('IICB')

    sql_parameterized_query = "select * from ArchivePage"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)

    items = []
    for row in result:
        #row_split=row[4].split('||')
        items.append({'Archive_Id': row[0], 'Archive_Heading': row[1], 'Released_On_Month': row[2], 'Released_On_Year': row[3], 'Update_Text': row[4], 'Archive_Status': row[5]})

    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})



@api_view(['POST'])
def SetArchivePage(request):
    db = DBUtils.MariaConnection('IICB')


    # extract json from request
    # expected format of payload in POST call
    # {"lines":[{"Archive_Id":3, "Archive_Heading":"Version 9.0", "Released_On_Month":"November", "Released_On_Year":2015,"Update_Text":"This is a test text inserted by Jayjit Ray", "Archive_Status":1}]}


    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)

    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into ArchivePage (Archive_Id,Archive_Heading,Released_On_Month,Released_On_Year,Update_Text,Archive_Status) values(%s,%s,%s,%s,%s,%s)"
        replace_tuple = (eachLine['Archive_Id'], eachLine['Archive_Heading'], eachLine['Released_On_Month'], eachLine['Released_On_Year'], eachLine['Update_Text'], eachLine['Archive_Status'])
        #print(sql_parameterized_query)
        results=DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        print("Record Inserted successfully")

    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})
    
    
@api_view(['GET'])
def GetContactUs(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from ContactUs"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)
    
    items = []
    for row in result:
        items.append({'ContactUs_Id': row[0], 'ContactUs_Info_Text': row[1], 'ContactUs_Status': row[2]})
        
    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})

    
@api_view(['POST'])
def SetContactUs(request):
    db = DBUtils.MariaConnection('IICB')
    # extract json from request
    # expected format of payload in POST call
    # {"lines":[{"ContactUs_Id":3, "ContactUs_Info_Text":"Please contact me.", "ContactUs_Status":"1"}]}
    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)
    
    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into ContactUs (ContactUs_Id,ContactUs_Info_Text,ContactUs_Status) values(%s,%s,%s)"
        replace_tuple = (eachLine['ContactUs_Id'], eachLine['ContactUs_Info_Text'], eachLine['ContactUs_Status'])
        #print(sql_parameterized_query)
        results=DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        print("Record Inserted successfully")
        
    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})
    

@api_view(['GET'])
def GetVideos(request):
    db = DBUtils.MariaConnection('IICB')
    sql_parameterized_query = "select * from Videos"
    result = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)
    
    items = []
    for row in result:
        #row_split=row[4].split('||')
        items.append({'video_id': row[0], 'video_title': row[1], 'video_link': row[2], 'video_status': row[3]})
    print(json.dumps({'items': items}))
    return Defaults.FinalResponse({'items': items})
    

@api_view(['POST'])
def SetVideos(request):
    db = DBUtils.MariaConnection('IICB')
    # extract json from request
    # expected format of payload in POST call
    # {"lines":[{"video_id":1, "video_title":"Jiya Jaale", "video_link":"https://www.youtube.com/watch?v=3RtKj_HuncI&list=RD3RtKj_HuncI&start_radio=1", "video_status":"1"}]}
    #print(request.body)
    jsondata = json.loads(request.body.decode("utf-8"))
    print(jsondata)
    
    for eachLine in jsondata['lines']:
        sql_parameterized_query = "REPLACE into Videos (video_id,video_title,video_link,video_status) values(%s,%s,%s,%s)"
        replace_tuple = (eachLine['video_id'], eachLine['video_title'], eachLine['video_link'], eachLine['video_status'])
        #print(sql_parameterized_query)
        results=DBUtils.MariaSetData(db, sql_parameterized_query, replace_tuple)
        print("Record Inserted successfully")
        
    DBUtils.MariaClose(db)
    return Defaults.FinalResponse({'status':'SUCCESS'})
    
