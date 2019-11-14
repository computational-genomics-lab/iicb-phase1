# Function to be called for Chromosome page
#from django.http import JsonResponse
#from django.core import serializers
import os
import mysql.connector
import array
import json
import math
import subprocess
import shutil
import collections
#from django.http import response
from rest_framework.decorators import api_view
from . import Defaults
from . import browserUIHandlers
from . import DBUtils 
#required for get_non_coding_sequence
from . import function
from json import JSONEncoder
from pathlib import Path
from itertools import islice
import re
import time
import copy
import pandas as pd
import numpy as np
##import numpy as np
from django.conf  import settings

#imports for fileupload
from rest_framework.parsers import MultiPartParser, FormParser,FileUploadParser
from rest_framework.response import Response
from rest_framework import status
#from .serializer import FileSerializer
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.conf import settings


#print(settings.LOGGER)


print=settings.LOGGER.info # once in each module
print("Logging is configured in browserImage.")






#######################
# Search for CHANGE_DATARANGE for changing the start/stopbase hardcoding values
#######################


rowht = 7  # thickness of the rows
rowgap = 50  # gap between the lower border of one track and the top border of the next track
minorgap = 10  # gap between rows that belong to the same track
topoffset = 20  # the top offset to print the base position nos.
horzlevel = rowgap + topoffset  # the starting horzlevel of the first track
breadth = 700  # the actual gap between the startbase and the endbase
leftedge = 250  # the starting point of the startbase
rightedge = leftedge + breadth  # the end point of the endbase
connectionBarHt = 6  # the thickness of the connection bar that exons of the same feature
height = 1030  # the height of the image drawn
diff = 10  # gap between two vertical lines

dividerLevel = 2 * (topoffset + rowht + (rowgap / 2))  # Starting y coordinate of dividing line

scaffold_present = 1


json_for_gff_uploader={}


#import logging
#logger=logging.getLogger(__name__)
#print=logger.info






def massage_request_json(request):
    body_unicode = request.body.decode(encoding='utf-8')
    #jsondata = {}
    jsondata = json.loads(body_unicode)
    

    if jsondata.get('organism') is not None:
        if isinstance(jsondata['organism'], str):
            jsondata['organism'] = int(jsondata['organism'])
    if jsondata.get('startbase') is not None:
        if isinstance(jsondata['startbase'], str):
            jsondata['startbase'] = int(jsondata['startbase'])
    if jsondata.get('stopbase') is not None:
        if isinstance(jsondata['stopbase'], str):
            jsondata['stopbase'] = int(jsondata['stopbase'])
    if jsondata.get('len') is not None:
        if isinstance(jsondata['len'], str):
            jsondata['len'] = int(jsondata['len'])
    if jsondata.get('version') is not None:
        if isinstance(jsondata['version'], str):
            jsondata['version'] = float(jsondata['version'])
    return jsondata


###################################################
# Function to call for viewing chromosome page
###################################################
# Expected JSON payload
'''
{
    "startbase": 1,
    "stopbase": 150000,
    "label": "Phytophthora sojae  (V1.0)",
    "version": 1,
    "organism": 67593,
    "star": null,
    "scaffold": "Scaffold_1"
}
'''





# def GFFparse(file):
#     from BCBio import GFF
#     import re
#     in_file = file
#     record={}
#     for item in ['gene','CDS','exon']:
#         outer_record=[]
#         limit_info = dict(
#                 gff_type = [item]
             
#         )
#         in_handle = open(in_file)
#         for rec in GFF.parse(in_handle, limit_info=limit_info):
#             for inner_rec in rec.features:
#                 inner_record={}
#                 inner_record.update({'scaffold':rec.id})
#                 inner_record.update({'name':inner_rec.type})
#                 inner_record.update({'id':re.sub("\D", "", inner_rec.id)})
#                 inner_record.update({'start':inner_rec.location.start.real})
#                 inner_record.update({'end':inner_rec.location.end.real})
#                 outer_record.append(inner_record)
#             print(outer_record)
               
#         record.update({item:outer_record})
#     in_handle.close()
#     return record










# def GFFparse(file):
#     from gffutils.iterators import DataIterator
#     import itertools
#     from operator import itemgetter
#     from collections import defaultdict
#     import re
#     record=[]
       
#     output_filename =file 
    
#     for feature in DataIterator(output_filename):
#         dict_feature={}
#         dict_feature.update({'start':feature.start})
#         dict_feature.update({'end':feature.stop})
#         dict_feature.update({'strand':feature.strand})
#         dict_feature.update({'scaffold':feature.seqid})
#         dict_feature.update({key:value[-1] for key,value in feature.attributes.items()})
#         record.append(dict_feature)
#     record=[item for item in record if item['gbkey'] not in ['Src'] and item['scaffold'] in ['Scaffold_1','NC_013771.1','NC_009933.1','NC_019428.1']] 
#     for d in record :
#         #print(d)
#         d['id']=re.sub("\D", "",d.pop('ID'))
#         d['name']=d.pop('gbkey')
#         d.pop('Name',None)

#     import itertools
#     import operator
#     from collections import defaultdict
#     ls=()
       
#     for key, items in itertools.groupby(record, operator.itemgetter('name')):
#         ls=ls+((key,list(items)),)

#     data=list(ls)
#     d = defaultdict(list)
#     for k, *v in data:
#         d[k].append(v[0][0])
#     record=dict(d)
#     return record    
   
def GFFparse(file):
    import re
    import gffpandas.gffpandas as gffpd
    annotation = gffpd.read_gff3(file)
    gff_df=annotation._read_gff3_to_df()
    seq_type=gff_df['type'].unique().tolist()
    seq_ids=gff_df['seq_id'].unique().tolist()[0]
    gff_df=gff_df[gff_df.seq_id==seq_ids]
    record={item:gff_df[gff_df.type==item].to_dict(orient='records') for item in seq_type}
    for item in seq_type:
        for it in range(len(record[item])):

            record[item][it].update({key:val for key,val  in [tuple(map(str, sub.split('='))) for sub in record[item][it]['attributes'].split(';')]})


            if 'Dbxref' in record[item][it].keys():
                record[item][it][record[item][it]['Dbxref'].split(':')[0]]=record[item][it]['Dbxref'].split(':')[-1]
                del record[item][it]['Dbxref']
            del record[item][it]['attributes']
            if 'taxon' in record[item][it].keys():
                record[item][it].update({key.replace('taxon','GeneID'):val for key,val in record[item][it].items() if key=='taxon'})
                del record[item][it]['taxon']
           
            # if 'Genbank' in record[item][it].keys():
            #     record[item][it].update({key.replace('Genbank','GeneID'):val for key,val in record[item][it].items() if key=='Genbank'})
            #     del record[item][it]['Genbank'] 
            # if 'type' in record[item][it].keys():
            #     record[item][it]['Name']=record[item][it]['type']
            
            record[item][it]['ID']=re.sub("\D","",record[item][it].pop('ID'))
           
            record[item][it]={key.lower():val for key,val in record[item][it].items() }
           
    return record  


















@api_view(['POST'])
def UploadFile(request):
    #expected json payload
    #{"scaffold":"Scaffold_1","label":"Albugo laibachii Nc14 (V1.0)","version":"1","stopbase":"150000","organism":"890382","startbase":"1","star":""}
    
     
    file_obj=request.FILES['file']
    fs=FileSystemStorage()
    filename=fs.save(file_obj.name,file_obj)
    gff_file=os.path.join(fs.location,filename)
    ext=os.path.splitext(gff_file)[1]
    valid_extension=['.gff']



    ##uncomment if required for chromosome page response
    param_keys=['organism','scaffold','label','version']
    param_obj=eval(request.data['param'].split('\\')[0])
    param_obj = { your_key: param_obj[your_key] for your_key in param_keys }
    jsondata=param_obj
    print("DEBUGGING TRACKS")
    #print(jsondata)
    if jsondata.get('organism') is not None:
         if isinstance(jsondata['organism'], str):
             jsondata['organism'] = str(int(jsondata['organism']))
    #if jsondata.get('startbase') is not None:
         #if isinstance(jsondata['startbase'], str):
             #jsondata['startbase'] = int(jsondata['startbase'])
    #if jsondata.get('stopbase') is not None:
         #if isinstance(jsondata['stopbase'], str):
             #jsondata['stopbase'] = int(jsondata['stopbase'])
    #if jsondata.get('len') is not None:
         #if isinstance(jsondata['len'], str):
             #jsondata['len'] = int(jsondata['len'])
    if jsondata.get('version') is not None:
         if isinstance(jsondata['version'], str):
             jsondata['version'] = str(float(jsondata['version']))
    print(jsondata)
    # jsondata['stopbase'] = 1000000
    # jsondata['stopbase'] = 1000000
    # jsonret = {'status' : -1}
    # jsonret['input_params'] = jsondata
    # # Declare global variable
        
    # global rowht  # thickness of the rows
    # global rowgap  # gap between the lower border of one track and the top border of the next track
    # global minorgap  # gap between rows that belong to the same track;
    # global topoffset  # the top offset to print the base position nos.
    # global horzlevel  # the starting horzlevel of the first track
    # global breadth  # the actual gap between the startbase and the endbase
    # global leftedge  # the starting point of the startbase
    # global rightedge  # the end point of the endbase
    # global connectionBarHt  # the thickness of the connection bar that exons of the same feature
    # global height  # the height of the image drawn
    # global diff  # gap between two vertical lines

    # global dividerLevel  # Starting y coordinate of dividing line

    # global scaffold_present  # 1  = the scaffold is in the database and it has coding regions
    #                         # 0  = the scaffold is in the database but does not have any coding regions
    #                         # -1 = the scaffold in not in the database
    # # endof global variable declaration

    # jsonret['image_params'] = {'length': 1000, 'width': 1300}

        
    # jsonret['contigsColorForQuality'] = Defaults.contigsColorForQuality

        
    # jsonret['vline'] = {'top': topoffset,
    #                     'bottom': height+topoffset,
    #                     'left': leftedge,
    #                     'right': rightedge,
    #                     'minor_step': diff,
    #                     'major_step': 50,
    #                     'border_color': 'darkgreen',
    #                     'minor_axis_color': 'grey',
    #                     'major_axis_color': 'lightgreen'
    #                     }

        

    # jsonret['top_label'] = browserUIHandlers.get_organism(jsondata['organism'], jsondata['version'])

    # # Display the proper view of the data
    # # $scaffold_present = & changeView(\ % FORM);
    # changeView_val = browserUIHandlers.changeView(jsondata)
    # jsonret['changeView'] = changeView_val

    # jsonret_D3Drawing = ConvertToD3format(jsonret)
    # jsonret_D3Drawing['scaffold_dnld'] = changeView_val['intermediate']['getScaffold']['features']
    # #jsonret_D3Drawing['changeView'] = changeView_val
    # resp=jsonret_D3Drawing
    # uncomment if not required    



    if  ext.lower() in valid_extension:
        
        records=GFFparse(gff_file)
        for key,val in records.items():
            for item in val:
                print(item.keys())
                link={}
                link.update({'startbase':item['start'],'len':item['end']-item['start'],'feature_id':item['id'],'link':'lnkNonCoding'})
                #link.update({'startbase':item['start'],'len':item['end']-item['start'],'feature_id':jsondata['organism'],'link':'lnkNonCoding'})
                link.update(jsondata)
                item.update({'link':link})
        upload_tracks={'upload_tracks':records}
        #respFinal={**upload_tracks,**resp}
        respFinal=upload_tracks
        #f=open('output.txt','w')
        #print(respFinal,file=f)
        #f.close()
        fs.delete(gff_file)
        
        return Response(respFinal)
    else:
        return Response('File Not Valid')




@api_view(['POST'])
def chromosomePageUI(request):
    #print(request.body)
    #expected json for payload
    #{"startbase":"1","stopbase":"150000","label":"Albugo laibachii Nc14 (V1.0)","organism":"890382","version":"1","star":"","scaffold":"Scaffold_1"}



    jsondata = massage_request_json(request)
    
    #CHANGE_DATARANGE for changing the start/stopbase hardcoding values
    jsondata['stopbase'] = 1000000

    jsonret = {'status' : -1}
    jsonret['input_params'] = jsondata
    # Declare global variable
    
    global rowht  # thickness of the rows
    global rowgap  # gap between the lower border of one track and the top border of the next track
    global minorgap  # gap between rows that belong to the same track;
    global topoffset  # the top offset to print the base position nos.
    global horzlevel  # the starting horzlevel of the first track
    global breadth  # the actual gap between the startbase and the endbase
    global leftedge  # the starting point of the startbase
    global rightedge  # the end point of the endbase
    global connectionBarHt  # the thickness of the connection bar that exons of the same feature
    global height  # the height of the image drawn
    global diff  # gap between two vertical lines

    global dividerLevel  # Starting y coordinate of dividing line

    global scaffold_present  # 1  = the scaffold is in the database and it has coding regions
                             # 0  = the scaffold is in the database but does not have any coding regions
                             # -1 = the scaffold in not in the database
    # endof global variable declaration

    '''
    # Defining image attributes as globals..
    our($image, $lightyellow, $darkgrey, $blue, $white, $darkgreen, $lightgreen, $green, $red, $black, $grey, $yellow, $pink, $brown,$khaki,$pink1,$maroon, $contigsColor)
    our % contigsColorForQuality
    our $imagefile_name;
    our $downloadFile_name;
    our $cgi_session_id = $FORM{'id'};
    our($firebrick,$orange,$gold,$olive,$spring_green,$aqua,$violet,$sandy,$chocolate,$crimson,$gray_1,$Lime,$golden_rod,$lawn_green,$pale_green,$pale_turquoise,$dark_olive_green,$wheat,$peach_puff);  # for synteny
    
    # creating a new image, allocating its area
    $image = new GD::Image(1000, 1030);
    '''
    jsonret['image_params'] = {'length': 1000, 'width': 1300}

    '''
    # allocating some colors
    # the background is set to the first allocated color
    $white = $image->colorAllocate(255, 255, 255);
    $lightyellow = $image->colorAllocate(250, 250, 210);
    # $blue = $image->colorAllocate(0,0,255);
    $blue = $image->colorAllocate(0, 122, 203);
    $darkgreen = $image->colorAllocate(0, 255, 0);
    $lightgreen = $image->colorAllocate(220, 255, 220);
    # $green = $image->colorAllocate(0,255,200);
    $green = $image->colorAllocate(81, 229, 18);
    $red = $image->colorAllocate(255, 0, 0);
    $pink = $image->colorAllocate(255, 0, 255);
    $black = $image->colorAllocate(0, 0, 0);
    $grey = $image->colorAllocate(200, 200, 200);
    $darkgrey = $image->colorAllocate(105, 105, 105);
    $yellow = $image->colorAllocate(255, 255, 0);
    $brown = $image->colorAllocate(175, 115, 0);
    $khaki = $image->colorAllocate(240, 177, 29);
    $pink1 =$image->colorAllocate(240, 60, 222);
    $maroon =$image->colorAllocate(232, 18, 104);
    $white = $image->colorAllocate(255, 255, 255);
    $lightyellow = $image->colorAllocate(250, 250, 210);
    # $blue = $image->colorAllocate(0,0,255);
    $blue = $image->colorAllocate(0, 122, 203);
    $darkgreen = $image->colorAllocate(0, 255, 0);
    $lightgreen = $image->colorAllocate(220, 255, 220);
    # $green = $image->colorAllocate(0,255,200);
    $green = $image->colorAllocate(81, 229, 18);
    $red = $image->colorAllocate(255, 0, 0);
    $pink = $image->colorAllocate(255, 0, 255);
    $black = $image->colorAllocate(0, 0, 0);
    $grey = $image->colorAllocate(200, 200, 200);
    $darkgrey = $image->colorAllocate(105, 105, 105);
    $yellow = $image->colorAllocate(255, 255, 0);
    $brown = $image->colorAllocate(175, 115, 0);
    $khaki = $image->colorAllocate(240, 177, 29);
    $pink1 =$image->colorAllocate(240, 60, 222);
    $maroon =$image->colorAllocate(232, 18, 104);
    
    # color code for synteny data start
    $firebrick =$image->colorAllocate(178, 34, 34);
    $orange =$image->colorAllocate(255, 69, 0);
    $gold =$image->colorAllocate(255, 215, 0);
    $olive =$image->colorAllocate(128, 128, 0);
    # $spring_green=$image->colorAllocate(0,255,127);
    $spring_green =$image->colorAllocate(102, 0, 51);
    
    # $aqua=$image->colorAllocate(127,255,212);
    $aqua =$image->colorAllocate(0, 0, 153);
    
    $violet =$image->colorAllocate(148, 0, 211);
    # $sandy=$image->colorAllocate(244,164,96);
    $sandy =$image->colorAllocate(0, 51, 51);
    $chocolate =$image->colorAllocate(210, 105, 30);
    $crimson =$image->colorAllocate(100, 149, 237);
    $gray_1 =$image->colorAllocate(128, 128, 128);
    $Lime =$image->colorAllocate(0, 128, 128);
    $golden_rod =$image->colorAllocate(218, 165, 32);
    $lawn_green =$image->colorAllocate(124, 252, 0);
    # $pale_green=$image->colorAllocate(152,251,152);
    
    $pale_green =$image->colorAllocate(72, 61, 139);
    $pale_turquoise =$image->colorAllocate(139, 0, 139);
    # $pale_turquoise=$image->colorAllocate(175,238,238);
    $dark_olive_green =$image->colorAllocate(85, 107, 47);
    $wheat =$image->colorAllocate(60, 179, 113);
    # $peach_puff=$image->colorAllocate(255,218,185);
    $peach_puff =$image->colorAllocate(95, 158, 160);
    
    # color code for synteny data end
    '''


    '''
    % contigsColorForQuality = (1 = > $red,  # Best Blat_Alignment_Quality_ID
    2 = > $violet,
    3 = > $aqua,
    4 = > $black  # Worst Blat_Alignment_Quality_ID
    '''
    jsonret['contigsColorForQuality'] = Defaults.contigsColorForQuality

    '''
    # making the background transparent and image interlaced
    $image->transparent($white);
    $image->interlaced('false');
    
    # making the left and right boundary line and also faded lines inbetween
    $image->line( $leftedge, $topoffset, $leftedge, $height + $topoffset, $darkgreen);
    $image->line( $rightedge, $topoffset, $rightedge, $height + $topoffset, $darkgreen);

    #  For drawing vertical scales
    for (my $i = $leftedge + $diff; $i < $rightedge; $i = $i + $diff)
        if ($i % 50 == 0)
            $image->line( $i, $topoffset, $i, $height + $topoffset, $grey);
        else
            $image->line( $i, $topoffset, $i, $height + $topoffset, $lightgreen);
    '''
    jsonret['vline'] = {'top': topoffset,
                        'bottom': height+topoffset,
                        'left': leftedge,
                        'right': rightedge,
                        'minor_step': diff,
                        'major_step': 50,
                        'border_color': 'darkgreen',
                        'minor_axis_color': 'grey',
                        'major_axis_color': 'lightgreen'
                        }

    '''
    $imagefile_name = $cgi_session_id."_browser.png";
    $downloadFile_name = $cgi_session_id."_download.txt";
    print "<map name=\"maptest\" class=\"map_class\" >";
    '''

    jsonret['top_label'] = browserUIHandlers.get_organism(jsondata['organism'], jsondata['version'])

    # Display the proper view of the data
    # $scaffold_present = & changeView(\ % FORM);
    changeView_val = browserUIHandlers.changeView(jsondata)
    jsonret['changeView'] = changeView_val

    jsonret_D3Drawing = ConvertToD3format(jsonret)
    jsonret_D3Drawing['scaffold_dnld'] = changeView_val['intermediate']['getScaffold']['features']
    #jsonret_D3Drawing['changeView'] = changeView_val
    #json_for_gff_uploader=jsonret_D3Drawing
    return Defaults.FinalResponse(jsonret_D3Drawing)


###################################################
# helper Functions (internally called) for viewing chromosome page
###################################################
def _createHeadingTrack(label):
    track = {'trackName': label,
             'trackType': 'stranded',
             'visible': True,
             'showLabels': True,
             'items': [],
             #TODO others ...
            }
    return track

def _createNormalTrack(label, arr_rect, is_strandred):
    track = {'trackName': label,
             'trackType': 'stranded',
             'visible': True,
             'inner_radius': 80,
             'outer_radius': 120,
             'trackFeatures': 'complex',
             'featureThreshold': 7000000,
             'mouseover_callback': 'islandPopup',
             'mouseout_callback': 'islandPopupClear',
             'linear_mouseclick': [
                 'linearPopup',
                 'linearClick'
             ],
             'showLabels': True,
             'showTooltip': True,
             }

    track['items'] = []


    if is_strandred == 1:
        track['trackType'] = 'stranded'
    else:
        track['trackType'] = 'track'

    for rect in arr_rect:
        one_item = {'id': rect['id'],
                    'start': rect['l'],
                    'end' : rect['r'],
                    'name': rect['name']
                    }
        if rect.get('color') is not None:
            one_item['color'] = rect['color']
        if rect.get('arrow') is not None:
            one_item['arrow'] = rect['arrow']
        if rect.get('link') is not None:
            one_item['link'] = rect['link']

        if is_strandred == 1:
            if rect.get('h') == 120:
                one_item['strand'] = 1
            else:
                one_item['strand'] = -1

        track['items'].append(one_item)

    return track


def ConvertToD3format(input_json):
    output_json = {'input_params': input_json['input_params'],
                   'top_label': input_json['top_label'],
                   'contigsColorForQuality': input_json['contigsColorForQuality'],
                   'tracks': []
                   }
    arr_drawing = input_json['changeView']['drawing']


    for track_class in arr_drawing:

        #heading type
        label_heading = track_class.get('label-heading')
        if label_heading is not None:
            one_track = _createHeadingTrack(label_heading)
            output_json['tracks'].append(one_track)
        # end of heading type

        # tracks
        arr_track = track_class.get('tracks')
        stranded = 0
        if arr_track is None:
            # simple track_class - NonCoding and Gene Models
            # Rects can be added
            if track_class.get('stranded') is not None:
                stranded = 1
            one_track = _createNormalTrack(track_class['label'], track_class['Rects'], stranded)
            output_json['tracks'].append(one_track)
        else:
            # composite track_class - tRNA+repaet, LASTZ alignment, BLAT ...
            # Get rects from individual tracks
            for track in arr_track:
                # Rects can be added
                one_track = _createNormalTrack(track['label'], track['Rects'], stranded)
                output_json['tracks'].append(one_track)
            # end of for track in arr_track
        # end of if simple or composite track_class

    # end of for track_class in arr_drawing:

    return output_json

###################################################
# END helper Functions (internally called) for viewing chromosome page
###################################################

###################################################
# Helper Functions (internally called) for viewing details page
###################################################

def call_EXE_fickett_loglkhd(codon_usage, ID, sequence, window_size, fickett_out_filename, log_out_filename):
    # Generate sequence file (input)
    # my $sequence_input_file = "/tmp/images/bd_sequence_input_file_" . $id;
    # Write sequence data to file
    #   open SEQOUT, ">$sequence_input_file" or die "Could not open file: $sequence_input_file";
    #   print SEQOUT $info1[0][6];
    #   close SEQOUT;

    # Delete all the files inside IICB/Graph    
    for file_ in os.listdir(Defaults.STORAGE_PATH):
        file_path = os.path.join(Defaults.STORAGE_PATH, file_)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    

    seq_filename = Defaults.STORAGE_PATH + "bd_sequence_input_file_" + str(ID)
    print("Writing seqfile:" + seq_filename)
    with open(seq_filename, 'w') as fp:
        fp.write(sequence)

    # Run fickett EXE - creates output fie
    #for loglikelihood
    codon_filename = Defaults.CODON_PATH + str(codon_usage)
    program_name = Defaults.EXE_PATH + "loglikelihood"
    arguments = ["-s", seq_filename, \
             "-m", codon_filename, \
             "-w", str(window_size), \
             "-web", \
             "-o", log_out_filename]
    print("Log out file:" + log_out_filename)
    command = [program_name]
    command.extend(arguments)
    output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]

    # for fickett
    program_name = Defaults.EXE_PATH + "fickett"
    arguments = ["-s", seq_filename, \
             "-o", fickett_out_filename]
    print("Fickett out file:" + fickett_out_filename)
    command = [program_name]
    command.extend(arguments)
    output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
    return


###################################################
# Helper Functions (internally called) for viewing details page
###################################################

###################################################
# Function to call for sequence detail page (non-coding details)
###################################################
# 

@api_view(['POST'])
def sequenceDetailUI(request):
    #print(request.body)
    jsondata = massage_request_json(request)

    jsonret = {'status' : -1}
    jsonret['input_params'] = jsondata
    

    # non- coding region
    '''Expected JSON payload
    {
        "organism": 67593,
        "scaffold": "Scaffold_1"
        "version": 1,
        "startbase": 1,
        "len": 150000,
    }
    '''
    if jsondata['link'] == "lnkNonCoding":   
        jsonret['Description'] = "Non coding region"
        result_json = function.get_non_coding_sequence(jsondata['organism'], jsondata['scaffold'], jsondata['version'], \
                         jsondata['startbase'], jsondata['len'])
        # <div class="id_name"> Location : </div>
        # <div class="content"> $org_name:$FORM{'StartPosition'}- $end_position</div>
        end_pos = jsondata['startbase'] + jsondata['len']
        jsonret['Location'] = result_json['org_name'] + ":" + str(jsondata['startbase']) + "-" + str(end_pos)
        jsonret['Table'] = []
        jsonret['Sequence_len'] = result_json['len']
        jsonret['Sequence'] = result_json['req_str']

        # Gene models
        '''Expected JSON payload
        {
            "organism":890382,
            "len": 58,   # this is ID
            "version": 1,
            "link": "lnkCoding"
        } '''
    elif jsondata['link'] == "lnkCoding":
        ID = jsondata['len']  # ID is passed as len here
        ver = jsondata['version']
        taxon_id = jsondata['organism']
        
            
        
        # @info1 = &GetCommonFeatures(1,$FORM{'ID'},$FORM{'organism'});   #for information about gene
        info1 = function._getCommonFeatures(1, ID, taxon_id)['features']
        info2 = function._getCommonFeatures(2, ID, taxon_id)['features']
        info5 = function._getCommonFeatures(5, info1[0][0], taxon_id)['features']  # Used by FprintScan
        info6 = function._getCommonFeatures(6, info1[0][0], taxon_id)['features']  # Used by Profile scan
        info7 = function._getCommonFeatures(7, info1[0][0], taxon_id)['features']  # Used by HMMSmart
        info11 = function._getCommonFeatures(11, info1[0][0], taxon_id)['features']  # Used by InterPro
        info12 = function._getCommonFeatures(12, info1[0][0], taxon_id)['features']  # Used by GO
        info15 = function._getCommonFeatures(15, info1[0][0], taxon_id)['features']
        info16 = function._getCommonFeatures(16, info1[0][0], taxon_id)['features']

        organism_label = browserUIHandlers.get_organism(taxon_id, ver)
        jsonret['Organism_name'] = organism_label 
        #header portion
        # <div class="id_name"> Transcript Name : </div>
        # <div class="content"> $info1[0][3]</div>
        jsonret['Trans_name'] = info1[0][3]
        
        # my $start_range=$info1[0][1]-1000;
        # my $end_range=$info1[0][2]+1000;
        start_range = info1[0][1] - 1000
        stop_range = info1[0][2] + 1000

        # <div class="id_name"> Location : </div>
        # <div class="content"> 
        # <a href="/cgi-bin/eumicrobedb/browserUI.cgi?scaffold=$info1[0][8]
        #                  &startbase=$start_range&stopbase=$end_range&organism=$FORM{'organism'}
        #                  &version=$FORM{'version'}&action=refresh&action_params=1">
        #         $info1[0][8] : $info1[0][1] - $info1[0][2]</a>
        # </div>
        

        jsonret['Location'] = info1[0][8] + ":" + str(info1[0][1]) + "-" + str(info1[0][2])
        # link same json as in tree/list nodes
        jsonret['Location_link'] = {'label': organism_label,
                                    'scaffold': info1[0][8],
                                    'organism': taxon_id,
                                    'version': ver,
                                    'star': "*", #not impotant here
                                    'startbase': start_range,
                                    'stopbase': stop_range
                                    }
        # if($info1[0][5] ==0)
        #       $orientation="(+)";
        #else
        #       $orientation="(-)";
        if info1[0][5] == 0:
            jsonret['Orientation'] = "(+)"
        else:
            jsonret['Orientation'] = "(-)"

        #my $no_of_exon=$#info2+1;
        jsonret['ExonsNum'] = len(info2) #+ 1

        # <div class="id_name"> Description : </div>
        # <div class="content">$info1[0][7] </div>
        jsonret['Description'] = info1[0][7]
        
        jsonret['Comments'] = []
        if len(info15) >= 0:
            jsonret['Comments'].append("This protein is a Signal Peptide")
        else:
            jsonret['Comments'].append("This protein is Not Signal Peptide")

        if len(info16) >= 0:
            jsonret['Comments'].append("This protein has transmembrane domain")
        else:
            jsonret['Comments'].append("This protein does Not have transmembrane domain")

        if info1[0][11] == 3:
            jsonret['Comments'].append("Not Reviewed")
        else:
            email_ref =  "<a href='mailto:" + info1[0][13] + "'>" + info1[0][12] + "</a>"
            jsonret['Comments'].append("Reviewed by " + email_ref + "</div>")

        jsonret['NCBIlink'] = "http://www.ncbi.nlm.nih.GOv/blast/Blast.cgi?" + \
                      "QUERY="+info1[0][6]+"&" + \
                      "DATABASE=nr&HITLIST_SIZE=10&FILTER=L&EXPECT=10&FORMAT_TYPE=HTML&PROGRAM=blastn&" + \
                      "CLIENT=web&SERVICE=plain&NCBI_GI=on&PAGE=Nucleotides&AUTO_FORMAT=Fullauto&" + \
                      "SHOW_OVERVIEW=yes&CMD=Put"

        # my $sequence_len = length($info1[0][6]);
        sequence_len = len(info1[0][6])
        window_size = 120
        if sequence_len < 150:
            window_size = math.ceil(sequence_len/3.0);


        # Call log likelihood and fickett executeables here
        # Creates output files log_out_filename and sequence_out_filename, respectively
        log_out_filename = Defaults.STORAGE_PATH + "bd_log_output_file_" + str(ID)
        fickett_out_filename = Defaults.STORAGE_PATH + "bd_fickett_output_file_" + str(ID)

        codon_usage = taxon_id   # $FORM{'organism'}
        call_EXE_fickett_loglkhd(codon_usage, ID, info1[0][6], window_size, fickett_out_filename, log_out_filename)
        jsonret['Param4SciTab'] = {'ID': ID, 'sequence':info1[0][6]}

        #graphs
        # plot_gene(\@info2,"/tmp/images/$id.png",$log_output_file,$fickett_output_file,$sequence_len)
        jsonret['scaffold_pos'] = function._plot_gene(info2)
        #add link parameters for scaffold_pos
        #print "<AREA SHAPE=rect COORDS=\"100,75,900,90\" 
        #       HREF=\"/cgi-bin/eumicrobedb/sequence1.cgi?ID=$FORM{'ID'}&organism=$FORM{'organism'}&version=$FORM{'version'}
        #              &gene_id=$info1[0][0]&gene_desc=$info1[0][7]&scaffold=$info1[0][9]\">";
        # parameters to call scaffoldPosLinkUI API
        jsonret['scaffold_pos_link'] = {'ID': ID,
                                        'organism': taxon_id,
                                        'ver': ver,
                                        'gene_id': info1[0][0],
                                        'gene_desc': info1[0][7],
                                        'scaffold': info1[0][9]
                                        }
        jsonret['Flickett_res'] = function._get_fickett_data(fickett_out_filename)  # array of arrays [timestamp, series1, series2]
        jsonret['LogLkhd_res']  = function._get_loglikehood_data(log_out_filename)  # array of arrays [timestamp, series1, series2, ...]
        #functional annotation 
        jsonret['HmmSmart'] = function._get_HMMSMART_data(taxon_id, ID, sequence_len, info7)
        jsonret['GO'] = function._get_GO_data(taxon_id, ID, sequence_len, info12) 
        jsonret['ProfileScan'] = function._get_ProfileScan_data(taxon_id, ID, sequence_len, info6)
        jsonret['InterPro']    = function._get_InterPro_data(taxon_id, ID, sequence_len, info11)
        jsonret['FprintScan']  = function._get_FprintScan_data(taxon_id, ID, sequence_len, info5)

    elif jsondata['link'] == 'promo':  
        ID = jsondata['feature_id'] 
        ver = jsondata['version']
        taxon_id = jsondata['organism']

        track_info1 = function._getCommonFeatures(23, ID, taxon_id)['features']
        jsonret['Description'] = track_info1[0][4]
        #if($track_info1[0][8] ne "") {
        #   print <<EOF;
        #       <div class ="id1">      
        #       <div class="id_name"> Attribute : </div>
        #       <div class="content"> $track_info1[0][8]</div>
        #       </div>
        #   EOF
        #}
        if len(track_info1[0][8]) > 0:
            jsonret['Attirbute'] = track_info1[0][8]

        
        jsonret['Table'] = []
        #my $len1 = length($track_info1[0][5]);
        jsonret['Sequence_len'] = len(track_info1[0][5])
        jsonret['Sequence'] = track_info1[0][5]

    elif jsondata['link'] == 'estlink': 
        ID = jsondata['feature_id'] 
        ver = jsondata['version']
        taxon_id = jsondata['organism']

        #@track_info1 = &getcommonfeature(4,$FORM{'organism'},$FORM{'ID'});
        #taxon_id = jsondata['organism']
        # NOTE: taxon_id, ID has revresed sequence
        #track_info1 = function._getCommonFeatures(4, taxon_id, ID)['features']
        track_info1 = function._getCommonFeatures(44, ID, taxon_id)['features']
        jsonret['Description'] = 'EST'
        jsonret['Table'] = []
        #my $len1 = length($track_info1[0][8])
        jsonret['Sequence_len'] = len(track_info1[0][8])
        jsonret['Sequence'] = track_info1[0][8]

    elif jsondata['link'] == 'syntenylink': 
        #print(jsonret)
        jsonret['Description'] = "From Genome Similarity Track"
        result_json = function.get_non_coding_sequence(jsondata['organism'], jsondata['scaffold'], jsondata['version'], \
                         jsondata['startbase'], jsondata['len'])
        # <div class="id_name"> Location : </div>
        # <div class="content"> $org_name:$FORM{'StartPosition'}- $end_position</div>
        end_pos = jsondata['startbase'] + jsondata['len']
        jsonret['Location'] = result_json['org_name'] + ":" + str(jsondata['startbase']) + "-" + str(end_pos)
        jsonret['Sequence_len'] = result_json['len']
        jsonret['Sequence'] = result_json['req_str']
        tab_res = function._GetSyntenyDetails(1, jsondata['organism'], jsondata['version'], jsondata['scaffold'], \
                                                          jsondata['startbase'], jsondata['startbase']+jsondata['len'])['features']

        jsonret['Table'] = []
        for i in tab_res:
            #print "<td><a href=/cgi-bin/eumicrobedb/browserDetail.cgi?ID=$arr[$i][8]&organism=$FORM{'organism'}&version=$FORM{'version'}>$arr[$i][9]</a></td>";
            #"print "<td><a>$arr[$i][11]</a></td>";

            one_item = {'Trans': i[9],
                        'Func': i[11] }
            # Link to Gene models page
            #Expected JSON payload
            #{
            #   'link': "lnkCoding",
            #   "organism":890382,
            #   "len": 58,   # this is ID
            #   "version": 1
            #}
            href_link = {'link': "lnkCoding",
                         "organism":jsondata['organism'],
                         "len": i[8],   # this is ID
                         "version": jsondata['version']
                        }
            one_item['Link'] = href_link
            jsonret['Table'].append(one_item)
    
    #elif jsondata['link'] == 'gfflink': - TODO

    #dump to an output file
    with open("sequenceDetailUI.out", "w+") as fpRes:
        fpRes.write("sequenceDetailUI returns:\n")
        fpRes.write(json.dumps(jsonret))
    print("sequenceDetailUI complete")

    return Defaults.FinalResponse(jsonret)

@api_view(['POST'])
def scaffoldPosLinkUI(request):    
    #print(request.body)

    """Expected JSON payload
    {
        "organism": 890382,
        "ID": 58,
        "gene_id": 556,
        "ver": 1,
        "gene_desc": "protocadherinlike protein putative",
        "scaffold": 890382
    }
    """
    
    """Expected JSON return
    {
        "Scaffold": "Scaffold_1",
        "Gene_id": "Albla_Nc14000210"
        "Description": "protocadherinlike protein putative",
        "PredGene": "ATGGGA....TGTACATTAG",
        "PredGene_len": 43352,
        "ProteinSeq": "ATGGGAAC...GATGTACATTAG",
        "ProteinSeq_len": 43352,
        "CDS": "ATGGGAAC....GTACATTAG",
        "CDS_len": 43352,
    }
    """    
    #Store the JSON structure
    jsondata = massage_request_json(request)
    ID = jsondata['ID']
    organism = jsondata['organism']
    version = jsondata['ver']
    gene_id = jsondata['gene_id']
    gene_desc = jsondata['gene_desc']
    scaffold = jsondata['scaffold']

    jsonret = function._get_plot_gene_link(ID, organism, version, gene_id, gene_desc, scaffold)
    return Defaults.FinalResponse(jsonret)

@api_view(['POST'])
def sciTabUI(request):    
    #print(request.body)

    """Expected JSON payload
    {
        "function": "name_of_function",
        "ID": 67593,
        "sequence": "xxxx"
    }
    """
    
    """Expected JSON return
    {
        "status"  :  0   |   1   |   2   |   3
        "filename": null |  ex   |  ex   | ex,ex,... 
        "filetype": null |  txt  |  png  | txt,png,... 
    }
    """    
    #Store the JSON structure
    jsondata = massage_request_json(request)
    #Decode the JSON structure and store in variables
    sci_func = jsondata['function']
    ID = jsondata['ID']
    seq = jsondata['sequence']

    jsonret = {'status' : -1}
    jsonret['input_params'] = jsondata
    # Generate sequence file (input)
    # my $sequence_input_file = "/tmp/images/bd_sequence_input_file_" . $id;
    # Write sequence data to file
    #   open SEQOUT, ">$sequence_input_file" or die "Could not open file: $sequence_input_file";
    #   print SEQOUT $info1[0][6];
    #   close SEQOUT;

    sequence_filename = Defaults.STORAGE_PATH + "sequence_file_" + str(ID)
    print("Writing seqfile:" + sequence_filename)
    #Create the sequence file
    with open(sequence_filename, 'w+') as fp:
        fp.write(seq)
 
    #os.chdir(present_dir)
    output_dir = Defaults.SCI_OUT_PATH
    # Variable to store the command to be executed
    cmd = ""
    
    print("\nfunction:", sci_func)
    angular_src_dir = ""
    
    if  sci_func == "plotorf":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "plotorf -sequence "+ sequence_filename +" -start ATG -stop TAA,TAG,TGA -graph png -gdirectory " +  angular_src_dir \
               + " -goutfile plotorf_" + str(ID) + " -auto >" + Defaults.STORAGE_PATH+"error1"
        
        
    
    elif sci_func == "prettyseq":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "prettyseq -sequence "+ sequence_filename +" -table 0 -ruler -plabel -nlabel -width 60 -odirectory2 " + angular_src_dir \
               + " -outfile prettyseq_" + str(ID) + " -auto"
        
        
        
    elif sci_func == "remap":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "remap -sequence "+ sequence_filename +" -enzymes all -sitelen 4 -mincuts 1 -maxcuts 2000000000 -nosingle -blunt -sticky -ambiguity -noplasmid -nomethylation -commercial -table 0 -frame 6 -odirectory2 " + angular_src_dir + " -outfile remapdata_" + str(ID) + " -cutlist -noflatreformat -limit -translation -reverse -nothreeletter -nonumber -width 60 -length 0 -margin 10 -name -description -offset 1 -nohtml" + " -auto"
        
        

    elif sci_func == "showpep":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "showpep -sequence "+  sequence_filename +" -odirectory2 " + angular_src_dir \
               + " -outfile showpep_" + str(ID) + " -name -description -offset 1 -nothreeletter -nonumber -format 2 -auto"
        

    elif sci_func == "sixpack":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "sixpack -sequence "+ sequence_filename +" -table 0 -firstorf -lastorf -nomstart -odirectory2 " + angular_src_dir \
               + " -outfile sixpack_" + str(ID) + " -osdirectory " + output_dir + " -outseq fasta::outseq_" + str(ID) +" -reverse -orfminsize 1 -number -width 60 -length 0 -margin 10 -name -description -offset 1 -nohtml" + " -auto"
        
        
        
    elif sci_func == "revseq":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "revseq -sequence "+ sequence_filename +" -reverse -complement -tag -osdirectory2 " + angular_src_dir \
                + " -outseq fasta::rev_" + str(ID) + " -auto"
        
        

    elif sci_func == "banana":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "banana -sequence " + sequence_filename +" -anglesfile Eangles_tri.dat -graph png -residuesperline 70 -odirectory " + angular_src_dir \
              + " -outfile banana.profile_" + str(ID) + " -gdirectory " + angular_src_dir + " -goutfile banana_" + str(ID) + " -auto >" + angular_src_dir+"er"       
        
       
    
    elif sci_func == "btwisted":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "btwisted -sequence " + sequence_filename +" -odirectory2 " + angular_src_dir + " -outfile bitwisted_" + str(ID) + " -auto"
        

        
        
    elif sci_func == "sirna":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "sirna -sequence " + sequence_filename +" -nopoliii -noaa -nott -polybase -rdirectory2 " + angular_src_dir + " -outfile sirna_" + str(ID) + " -rformat table -osdirectory3 " + angular_src_dir + " -outseq fasta::sirnaseq_" + str(ID) +" -nocontext " + " -auto"
       


    elif sci_func == "cai":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "cai -seqall " + sequence_filename +" -cfile Eyeast_cai.cut -outfile cai_" + str(ID) + " -odirectory2 " + angular_src_dir + " -auto"
        
        
        
    elif sci_func == "cusp":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "cusp -sequence " + sequence_filename +" -odirectory2 " + angular_src_dir + " -outfile cusp_" + str(ID) + " -auto"
        
        
            
    elif sci_func == "cpgplot":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "cpgplot -sequence " + sequence_filename +" -window 100 -minlen 200 -minoe 0.6 -minpc 50. -odirectory2 " + angular_src_dir + " -outfile cpg_out_" + str(ID) + " -gdirectory " + angular_src_dir + " -plot -graph png -goutfile cpg_plot_" + str(ID) + " -obsexp -cg -pc -ofdirectory3 " + angular_src_dir + " -outfeat cpg_feat_" + str(ID) + " -offormat gff -noofsingle " + " -auto >" + angular_src_dir +"eo"
    
        

    elif sci_func == "geecee":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "geecee -sequence " + sequence_filename +" -odirectory2 " + angular_src_dir + " -outfile geecee_" + str(ID) + " -auto"
        
        

    elif sci_func == "eprimer32":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "eprimer32 -sequence " + sequence_filename +" -odirectory2 " + angular_src_dir + " -sid1 seq -outfile eprime_" + str(ID) + " -auto"
        
        

    elif sci_func == "tfscan":
        #Construct path for media directory of angular
        angular_src_dir = Defaults.SCI_OUT_PATH + sci_func
        #Remove directory
        shutil.rmtree(angular_src_dir, ignore_errors = True)
        #Make directory
        os.mkdir(angular_src_dir)
        #Construct Command for execution
        cmd = "tfscan -sequence " + sequence_filename +" -menu V -mismatch 0 -minlength 1 -rdirectory2 " + angular_src_dir + " -outfile tfscan_" + str(ID) + " -rformat seqtable " + " -auto"
        
        
        
    ## Firing commands        
    # Print the command to be executed for debugging
    print("\nSCI_FUNC: "+ cmd)
    # Execute the command
    subprocess.Popen(cmd, shell=True)
    # Lists for storing file name and extensions
    file_list =[]        
    ext_list = []
    filename_list = []
    no_ext_flag = False
    # Wait for the scientific program to complete
    time.sleep(5.0)
    # Store the list of files inside
    file_list = os.listdir(angular_src_dir)        
    # Store the name of files and extensions in two different lists
    for file_ in file_list: 
        f_name_with_ext = str(file_)
        # Extract the name of the file
        #f_name = f_name_with_ext[:f_name_with_ext.rfind(".")] 
        
        if "." in f_name_with_ext:
            f_name = f_name_with_ext[:f_name_with_ext.rfind(".")]
            
            # Extract the extension of the file
            ext = f_name_with_ext[len(f_name)+1:]
            
            # HAS TO BE MADE GENERIC
            if ext != "png":
                f_name = f_name_with_ext
                ext = "txt"
        else:            
            f_name = f_name_with_ext
            ext = "none"
            no_ext_flag = True
        
        # Update the list of names and extensions
        filename_list.append(f_name)
        ext_list.append(ext)
          
    # Print the lists for debugging
    print("file list : ",file_list)
    print(filename_list)
    print(ext_list)
        
    # Flags for extension checking
    txt_flag = False
    png_flag = False
    status_code = 0

    # Check if .png extension exists
    if "png" in ext_list:
        png_flag = True
    # Check if .txt extension exists
    if "txt" in ext_list or no_ext_flag:
        txt_flag = True
    # Check if both .txt and .png extension exists
    if png_flag and txt_flag:
        status_code = 3
        print ("TXT and PNG")
    # Set status code
    elif not png_flag:       #txt_flag and not png_flag:
        status_code = 1
        print ("TXT")
    # Set status code
    elif png_flag and not txt_flag:
        status_code = 2
        print("PNG")
    # Variables for JSON return
    resp_string_name = ""
    resp_string_ext = ""
    # Loop to construct the JSON response 
    for name_, ext_ in zip(filename_list, ext_list):
        resp_string_name += "," + name_
        resp_string_ext += "," + ext_
    # Create the response string
    resp_string_name = resp_string_name[1:]
    resp_string_ext  = resp_string_ext [1:]
    # Print the JSON formats
    print(status_code)
    print(resp_string_name)
    print(resp_string_ext)

    # Construction of return JSON 
    jsonret = {'status' : status_code}
    jsonret['filename'] = resp_string_name
    jsonret['type'] = resp_string_ext
        
    # Return the JSON response  
    return Defaults.FinalResponse({'status' : status_code, 'filename': resp_string_name, 'type': resp_string_ext})



## PARAM: 'gene_name': 'Albla_Nc14125180', 'organism_name': '890382-1'
@api_view(['POST'])
def QueryByGeneName(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"startbase":"1","stopbase":"150000","label":"Albugo laibachii Nc14 (V1.0)","organism":"890382","version":"1","star":"","scaffold":"Scaffold_1"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********%s", res_data)

    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********%s", organism_name)
    
    version_name =  str(res_data['organism_name']).split('-')[1]
    version_name =  str(res_data['organism_name']).split('-')[1]
    print("\n********** Version Name *********%s", version_name)

    gene_name = str(res_data['gene_name'])
    gene_name = re.sub(r"[(),[']", '', str(gene_name))
    print("\n********** Gene Name *********%s", gene_name)
    
    db = DBUtils.MariaConnection('DOTS')
    sql_parameterized_query = "select g.gene_id, g.name, g.description, nl.start_min, nl.end_min, ns.source_id, ns.taxon_id,ns.sequence_version,nf.na_sequence_id,nf.name,nf.na_feature_id  from gene g, geneinstance gi, nafeatureimp nf, nalocation nl, externalnasequence ns WHERE g.name LIKE '" + gene_name + "' AND gi.gene_id = g.gene_id AND nf.na_feature_id = gi.na_feature_id AND nl.na_feature_id = nf.na_feature_id AND nf.na_sequence_id = ns.na_sequence_id AND ns.taxon_id = '" + organism_name + "' AND sequence_version = '" + version_name + "'";
    result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query)
    DBUtils.MariaClose(db)
    
    return Defaults.FinalResponse({'query': result_search_query})

      
@api_view(['POST'])
def QueryByPrimaryAnnotation(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"organism_name":"890382-1","primary_annotation":"actin"}

    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********{}".format(organism_name))

    ####  %kinase%
    primary_annotation = re.sub(r"[(),[']", '', str(res_data['primary_annotation']))
    primary_annotation = '%' + primary_annotation + '%'
    print("primary_annotation{}".format(primary_annotation))

    db = DBUtils.MariaConnection('DOTS')    
    sql_search_query = "select ns.name, ns.na_sequence_id, ns.taxon_id, tr.product, orr.species, orr.taxon_id, orr.version from externalnasequence ns, transcript tr, oomycetes_cgl_sres.organism orr where ns.na_sequence_id = tr.na_sequence_id and orr.taxon_id= ns.taxon_id and orr.version = ns.sequence_version and ns.taxon_id = '" + organism_name + "' and tr.product like '" + primary_annotation + "'";  ####'%kinase%'";    
    result_search_query = DBUtils.MariaGetData(db, sql_search_query)
    DBUtils.MariaClose(db)

    return Defaults.FinalResponse({'query': result_search_query})


@api_view(['POST'])
def QueryByGenomeLocation(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"organism_name":"890382-1","genome_location":"Scaffold_2:4000-50000"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********{}".format(organism_name))
    
    version_name =  str(res_data['organism_name']).split('-')[1]
    print("\n********** Version Name *********{}".format(version_name))

    ## e.g Scaffold_2:4000-50000
    source_id = str(res_data['genome_location']).split(':')[0]
    genome_location = str(res_data['genome_location']).split(':')[1]
    genome_location_start_base = str(genome_location).split('-')[0]
    genome_location_start_base = re.sub(r"[(),[']", '', str(genome_location_start_base))

    genome_location_end_base = str(genome_location).split('-')[1]
    genome_location_end_base = re.sub(r"[(),[']", '', str(genome_location_end_base))
  
    print("\n********** genome Location *********\n") 
    print("source_id {0} START {1} END {2}".format(source_id, genome_location_start_base, genome_location_end_base))

    db = DBUtils.MariaConnection('DOTS')
    sql_parameterized_query = "select nf.na_feature_id,nf.name, nl.start_min,nl.end_min,ens.description, ens.taxon_id,ens.source_id,ens.sequence_version,nf.na_sequence_id,nf.string8,nf.string13 from externalnasequence ens, nalocation nl,nafeatureimp nf where ens.taxon_id = '" + organism_name + "' and ens.sequence_version = '" + version_name + "' and ens.source_id = '" + source_id + "' and ens.sequence_type_id != 1 and nf.subclass_view not like '%CDS%' and nf.subclass_view not like '%GeneFeature%' and nf.subclass_view not like '%exonfeature%' and nf.na_sequence_id=ens.na_sequence_id and nl.na_feature_id=nf.na_feature_id and (nl.start_min between '" + genome_location_start_base + "' and '" + genome_location_end_base + "' or nl.end_min between '" + genome_location_start_base + "' and '" + genome_location_end_base + "') order by nl.start_min";
    result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query)    
    DBUtils.MariaClose(db)

    return Defaults.FinalResponse({'query': result_search_query})


@api_view(['POST'])
def QueryByConservedRegions(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"organism_name":"890382-1","genome_location":"Scaffold_2:4000-50000"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********{}".format(organism_name))
    
    version_name =  str(res_data['organism_name']).split('-')[1]
    print("\n********** Version Name *********{}".format(version_name))

    ## e.g Scaffold_2:4000-50000
    source_id = str(res_data['genome_location']).split(':')[0]
    genome_location = str(res_data['genome_location']).split(':')[1]
    genome_location_start_base = str(genome_location).split('-')[0]
    genome_location_start_base = re.sub(r"[(),[']", '', str(genome_location_start_base))

    genome_location_end_base = str(genome_location).split('-')[1]
    genome_location_end_base = re.sub(r"[(),[']", '', str(genome_location_end_base))
  
    print("\n********** genome Location *********\n")
    print("source_id {} START {} END {}".format(source_id, genome_location_start_base, genome_location_end_base))

    db = DBUtils.MariaConnection('DOTS')
    
    sql_parameterized_query ="select en.na_sequence_id,orr.species,orr.strain from externalnasequence en, oomycetes_cgl_sres.organism orr where en.taxon_id = '" + organism_name + "' and en.sequence_version = '" + version_name + "' and en.source_id = '" + source_id + "'  and en.sequence_type_id=1 and orr.taxon_id = '" + organism_name + "'"    
    result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query)    
    
    sequence_id = result_search_query[:][0]
    print("***** Sequence_id ****{}\n".format(sequence_id))
    
    na_sequence_id = result_search_query[0][0]
    na_sequence_id = re.sub(r"[(),[']", '', str(na_sequence_id))
    print("na_sequence_id{}".format(na_sequence_id))   # 329298
    
    target_organism = re.sub(r"[(),[']", '', str(result_search_query[0][1])) + ' ' + re.sub(r"[(),[']", '', str(result_search_query[0][2]))   
    target_organism = re.sub(r"[(),[']", '', str(target_organism))

    ##final_result = []    
    sql_parameterized_query_2 = "select sa.target_start, sa.target_end, sa.query_start, sa.query_end, sa.is_reversed, sa.target_na_sequence_id, sa.query_taxon_id, sa.target_taxon_id, ena.source_id, ena.sequence_version,orr.species, orr.strain FROM samalignment sa, externalnasequence ena, oomycetes_cgl_sres.organism orr where sa.target_na_sequence_id = '" + na_sequence_id + "' and sa.query_taxon_id != '" + organism_name + "' and (sa.target_start BETWEEN '" + genome_location_start_base + "' and '" + genome_location_end_base + "' OR sa.target_end BETWEEN '" + genome_location_start_base + "' and '" + genome_location_end_base + "' OR (sa.target_start <= '" + genome_location_start_base + "' and sa.target_end >= '" + genome_location_end_base + "')) and ena.na_sequence_id=sa.query_na_sequence_id and orr.taxon_id=sa.query_taxon_id and orr.version=sa.q_version"
    result_search_query_2 = DBUtils.MariaGetData(db, sql_parameterized_query_2)
    DBUtils.MariaClose(db)
    
  ##  return JsonResponse({'query': result_search_query_2})

    jsonReturns = {'query': result_search_query_2, 'target_organism': target_organism, 'source_id' : source_id}
    print("jsonReturns{}".format(jsonReturns))
    return Defaults.FinalResponse(jsonReturns)


@api_view(['POST'])
def QueryByKEGGorthologyid(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"organism_name":"890382-1","kegg_id":"179"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********{}".format(organism_name))

    version_name =  str(res_data['organism_name']).split('-')[1]
    version_name =  str(version_name).split('\']')[0]
##    version_name = re.sub(r"[(),[]']", '', str(version_name))
    print("\n********** Version Name *********{}".format(version_name))
    
    ## e.g Scaffold_2:4000-50000
    kegg_id = re.sub(r"[(),[']", '', str(res_data['kegg_id']))
    kegg_id = '%' + kegg_id + '%'
    print("kegg_id%s", kegg_id)
    
    f_string ="(pd.taxon_id = '" + organism_name + "' and pd.version = '" + version_name + "')";    
    print("kegg_id{0} f_string{1}".format(kegg_id,f_string))    
    
    db = DBUtils.MariaConnection('DOTS')
    sql_search_query = "select pd.name, pd.na_sequence_id, pd.ko_id, pd.name, orr.species, pd.url from pathway_data pd, oomycetes_cgl_sres.organism orr where orr.taxon_id = pd.taxon_id and orr.version = pd.version and (pd.taxon_id = '" + organism_name + "' and pd.version = '" + version_name + "') and pd.ko_id like '" + kegg_id + "'";     ##'%" + kegg_id + "%' ";    

    ##sql_search_query = "select pd.name, pd.na_sequence_id, pd.ko_id, pd.name,orr.species, pd.url from pathway_data pd , oomycetes_cgl_sres.organism orr  where orr.taxon_id= pd.taxon_id and orr.version = pd.version and ( or (pd.taxon_id = '" + organism_name + "' and pd.version = '" + version_name + "')) and pd.ko_id like '" + kegg_id + "'";     ##'%" + kegg_id + "%' ";    
##    sql_search_query = "select pd.name, pd.na_sequence_id, pd.ko_id, pd.name,orr.species, pd.url from pathway_data pd , oomycetes_cgl_sres.organism orr  where orr.taxon_id= pd.taxon_id and orr.version = pd.version and '" + f_string + "' and pd.ko_id like '" + kegg_id + "'";     ##'%" + kegg_id + "%' ";    
    print("sql_search_query -------------{}\n".format(sql_search_query))
    result_search_query = DBUtils.MariaGetData(db, sql_search_query)
    DBUtils.MariaClose(db)

    return Defaults.FinalResponse({'query': result_search_query})

####select pd.name, pd.na_sequence_id, pd.ko_id, pd.name,orr.species, pd.url from pathway_data pd , oomycetes_cgl_sres.organism orr  where orr.taxon_id= pd.taxon_id and orr.version = pd.version and ((pd.taxon_id = '890382' and pd.version = '1')) and pd.ko_id like '%K08269%'



@api_view(['POST'])
def QueryByclusterid(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"cluster_id":"179"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    cluster_id = str(res_data['cluster_id'])
    print("\n********** Cluster_id *********{}".format(cluster_id))
   
    db = DBUtils.MariaConnection('DOTS')
    
    sql_search_query = "SELECT pc.gene_id, gi.description , orr.species,ns.na_sequence_id,ns.sequence_version,ns.taxon_id,pc.cluster_id,ns.name FROM `protein_cluster` pc, oomycetes_cgl_sres.organism orr, geneinstance gi, externalnasequence ns, nafeatureimp nf WHERE cluster_id = '" + cluster_id +"' and gi.gene_id=pc.gene_id and nf.na_feature_id=gi.na_feature_id and ns.na_sequence_id= nf.na_sequence_id AND orr.taxon_id = ns.taxon_id and orr.version=ns.sequence_version";
    result_search_query = DBUtils.MariaGetData(db, sql_search_query)
    DBUtils.MariaClose(db)
    
    return Defaults.FinalResponse({'query': result_search_query, 
                         'cluster': {'id': cluster_id, 
                                     'image':'group'+str(cluster_id)+'.dnd.png'
                                     }
                        })


@api_view(['POST'])
def QueryByclusterdescription(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"cluster_description":"condensin complex"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    cluster_description = str(res_data['cluster_description'])
    cluster_description = '%' + cluster_description + '%'
    print("\n********** Cluster_id *********{}".format(cluster_description))

    db = DBUtils.MariaConnection('DOTS')
    sql_search_query = "SELECT pc.gene_id, gi.description, orr.species,ns.na_sequence_id,ns.sequence_version,ns.taxon_id,pc.cluster_id,ns.name FROM `protein_cluster` pc, oomycetes_cgl_sres.organism orr, geneinstance gi, externalnasequence ns, nafeatureimp nf WHERE gi.gene_id=pc.gene_id  and nf.na_feature_id=gi.na_feature_id and ns.na_sequence_id= nf.na_sequence_id and gi.description like '" + cluster_description + "' AND orr.taxon_id = pc.taxon_id and orr.version=ns.sequence_version";
    result_search_query = DBUtils.MariaGetData(db, sql_search_query)
    DBUtils.MariaClose(db)

    return Defaults.FinalResponse({'query': result_search_query})


@api_view(['POST'])
def QueryByProteinDomainmotiffunction(request):
    print=settings.LOGGER.debug
    #expected json payload
    #{"organism_name":"890382-1","protein_domain":"tRNA-binding"}
    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))
    
    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********{}".format(organism_name))

    version_name =  str(res_data['organism_name']).split('-')[1]
    version_name =  str(version_name).split('\']')[0]
##    version_name = re.sub(r"[(),[]']", '', str(version_name))
    print("\n********** Version Name *********{}".format(version_name))
    
    ## e.g Scaffold_2:4000-50000
    protein_domain = re.sub(r"[(),[']", '', str(res_data['protein_domain']))
    protein_domain = '%' + protein_domain + '%'
    print("protein_domain{}".format(protein_domain))

##    f_string ="(pd.taxon_id = '" + organism_name + "' and pd.version = '" + version_name + "')";    

    result_search_query = []
    db = DBUtils.MariaConnection('DOTS')
    sql_search_query = "select na_sequence_id, name, domain_name, taxon_ID, sequence_version, species from pdomain_join where domain_name like '" + protein_domain + "' and (taxon_ID = '" + organism_name + "' and sequence_version = '" + version_name + "')"
    result_search_query = DBUtils.MariaGetData(db, sql_search_query)
    DBUtils.MariaClose(db)

    return Defaults.FinalResponse({'query': result_search_query})


@api_view(['POST'])
def QueryBySecretomeTMHMM(request):
    print=settings.LOGGER.debug
    #expected jason payload
    #{"organism_name":"890382-1","output":"SECRETOME"}

    res_data = json.loads(request.body.decode("utf-8"))
    print("\n********** request *********{}".format(res_data))

    organism_name = str(res_data['organism_name']).split('-')[0]
    organism_name = re.sub(r"[(),[']", '', str(organism_name))
    print("\n********** Organism Name *********{}".format(organism_name))
    
    version_name =  str(res_data['organism_name']).split('-')[1]
    version_name =  str(res_data['organism_name']).split('-')[1]
    print("\n********** Version Name *********{}".format(version_name))
    
    result_search_query = []
    result_header = []
    db = DBUtils.MariaConnection('DOTS')
#    sql_parameterized_query = "";
#    result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query)    
#    DBUtils.MariaClose(db)


    if res_data['output'] == 'SECRETOME':
        sql_parameterized_query = "select g.name, c.taxon_id,c.`NN-score`, c.odds, c.weighted_score,nf.na_sequence_id from SECRETOME c,gene g,geneinstance gi, nafeatureimp nf, externalnasequence ena where c.taxon_ID = '" + organism_name + "' and gi.gene_id=c.gene_id and gi.gene_id = g.gene_id and nf.na_feature_id=gi.na_feature_id and ena.na_sequence_id=nf.na_sequence_id and ena.sequence_version= '" + version_name + "'";
        result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query) 
        result_header = ['Transcript Name', 'NN-score', 'odds', 'weighted Score']

    if res_data['output'] == 'PROP':
        sql_parameterized_query = "select g.name, c.taxon_id,c.position, c.context, c.score,nf.na_sequence_id from PROP c,gene g,geneinstance gi,nafeatureimp nf, externalnasequence ena where c.taxon_ID = '" + organism_name + "' and gi.gene_id=c.gene_id and gi.gene_id = g.gene_id and nf.na_feature_id=gi.na_feature_id and ena.na_sequence_id=nf.na_sequence_id and ena.sequence_version = '" + version_name + "' and c.score >= 0.5";
        result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query) 
        result_header = ['Transcript Name', 'position', 'context', 'score']
    
    if res_data['output'] == 'PSORT':
        sql_parameterized_query = "select g.name, c.taxon_id,c.type, c.score, c.psort_ID,nf.na_sequence_id from PSORT c,gene g,geneinstance gi,nafeatureimp nf, externalnasequence ena where c.taxon_ID = '" + organism_name + "' and gi.gene_id=c.gene_id and gi.gene_id = g.gene_id and nf.na_feature_id=gi.na_feature_id and ena.na_sequence_id=nf.na_sequence_id and ena.sequence_version = '" + version_name + "'";
        result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query) 
        result_header = ['Transcript Name', 'type', 'score', 'psort_ID']
        
    if res_data['output'] == 'SignalP':
        sql_parameterized_query = "select g.name, c.taxon_id,c.`Y-score`, c.`D-score`, c.`Y-pos`,nf.na_sequence_id from signalP c,gene g,geneinstance gi,nafeatureimp nf,externalnasequence ena where c.taxon_ID = '" + organism_name + "' and gi.gene_id=c.gene_id and gi.gene_id = g.gene_id and nf.na_feature_id=gi.na_feature_id and ena.na_sequence_id=nf.na_sequence_id and ena.sequence_version = '" + version_name + "'";
        result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query) 
        result_header = ['Transcript Name', 'Y-score', 'D-score', 'Y-pos']

    if res_data['output'] == 'TMHMM':
        sql_parameterized_query = "select g.name, c.taxon_id,c.Inside, c.Outside, c.TMhelix,nf.na_sequence_id from TMHMM c,gene g,geneinstance gi,nafeatureimp nf, externalnasequence ena where c.taxon_ID = '" + organism_name + "' and gi.gene_id=c.gene_id and gi.gene_id = g.gene_id and nf.na_feature_id=gi.na_feature_id and ena.na_sequence_id=nf.na_sequence_id and ena.sequence_version = '" + version_name + "'";
        result_search_query = DBUtils.MariaGetData(db, sql_parameterized_query) 
        result_header = ['Transcript Name', 'Inside', 'Outside', 'TMhelix']
        
        
    return Defaults.FinalResponse({'query': result_search_query, 'result_header': result_header})

'''
if($function == 'PROP')
{
	$sql="select g.name, c.taxon_id,c.position, c.context, c.score,nf.na_sequence_id from PROP c,gene g,geneinstance gi,nafeatureimp nf, externalnasequence ena where c.taxon_ID = '" + organism_name + "' and gi.gene_id=c.gene_id and gi.gene_id = g.gene_id and nf.na_feature_id=gi.na_feature_id and ena.na_sequence_id=nf.na_sequence_id and ena.sequence_version= '" + version_name + "' and c.score >= 0.5";
	
 
 	$row1="Transcript Name";
	$row2="position";
	$row3="context";
	$row4="score";
	#print "$sql <br>";
}	
'''

## @Function: return the column index and title of Outcome of Selected Tab ##
def selectTabContentIndex(tabIndex,title=None):
#    print("\n\nTab index : ", tabIndex)

    if tabIndex == 1:
        tab_result_idx = [1,2,6]
        tab_result_title = ["Transcript Name", 
                            "Function/Comments", 
                            "Taxon ID"]        
    if tabIndex == 2:
        tab_result_idx = [0,2,3,4]
        tab_result_title = ["Transcript Name",	
                            "Taxon ID", 
                            "Function/Comments", 
                            "Organism"]
        tab_dict = dict(zip(tab_result_title, tab_result_idx))
        
    if tabIndex == 3:
        tab_result_idx = [9,1,10,5]
        tab_result_title = ["Transcript Name",
                            "Gene feature",
                            "Function/Comments", 
                            "Taxon ID"]
        tab_dict = dict(zip(tab_result_title, tab_result_idx))
                            
    if tabIndex == 4:
        tab_result_idx = [1,2,3,5]
        tab_result_title = ["Target Organism",
                            "Target Scaffold:Location",
                            "Query organism", 
                            "Query Scaffold:Location"]

    if tabIndex == 8:
        tab_result_idx = [1,2,3,5]
        tab_result_title = ["Transcript Name",
                            "Function/Comments",
                            "Taxon ID", 
                            "Organism"]
        tab_dict = dict(zip(tab_result_title, tab_result_idx))
                            

    if tabIndex == 9:
        tab_result_idx = [0,2,3,4]
        tab_result_title = ["Transcript Name",
                            "NN-score	",
                            "odds",
                            "weighted Score"]
        tab_dict = dict(zip(tab_result_title, tab_result_idx))
                            
                        
    if tabIndex > 9:
        tab_result_idx = []
        tab_result_title = []
        for count,ele in enumerate(title):
            tab_result_idx.append(count)
            tab_result_title.append(ele)
        tab_dict = dict(zip(tab_result_title, tab_result_idx))
        print("\n\n==================NEWLY PERFORMED DICTIONARY==================={}\n".format(tab_dict))
       

    return tab_result_idx, tab_result_title, tab_dict

def dataframe_make(tab_index,query_list,title):
    
    Query1_index,Query1_title,Query1_mapped_dict=selectTabContentIndex(tab_index,title)
    
    print("\n\nQuery1_Header%s",{val:key for (key, val) in Query1_mapped_dict.items()})
    df = pd.DataFrame(query_list)[Query1_index]
    columns={val:key for (key, val) in Query1_mapped_dict.items()}
    df.rename(columns=columns,inplace=True)
    return df
    
# def make_union(df1,df2):
#     return pd.concat([df1,df2],ignore_index=True).reset_index(drop='True').fillna('')
def make_union(df1,df2):
    df_new=pd.merge(df1,df2,on='Transcript Name',how='outer')
    ls=[item for item in df_new.columns.tolist() if re.search('_x$',item)]
    print('\n\nDEBUGGING UNION')
    feature_list=list(map(lambda x:(x,x[:-2]+'_y'),ls))
    for item in feature_list:
        df_new[str(item[0][:-2])]=df_new[str(item[0])].fillna(df_new[item[1]])
    feature_list=list(sum(feature_list,()))
    print(feature_list)
    df_new.drop(feature_list,axis=1,inplace=True)
    #df_new=pd.to_numeric(df_new).astype(df1.dtypes)
    #df_new=df_new[feature_list-null_columns].astype(dict(df1.dtypes))
    #print(dict1.update(dict2))
    #print(dict(df_new.dtypes))
    print(df1.dtypes)
    print(df2.dtypes)
    df2=df2.apply(lambda x:x.astype('float64') if x.dtype == "int64" else x)
    df1=df1.apply(lambda x:x.astype('float64') if x.dtype == "int64" else x)
    #df2=df2.astype(dict(df1.dtypes))
    df_new=df_new.astype(dict(df1.dtypes))
    print(df1.dtypes)
    print(df_new.dtypes)
    return df_new.fillna('')


def make_intersection(df1,df2):
    df_new=pd.merge(df1,df2,how='inner',indicator=False,on='Transcript Name')
    ls=[item for item in df_new.columns.tolist() if re.search('_x$',item)]
    feature_list=list(map(lambda x:(x,x[:-2]+'_y'),ls))
    for item in feature_list:
         df_new[str(item[0][:-2])]=df_new[str(item[0])].fillna(df_new[item[1]])
    feature_list=list(sum(feature_list,()))
    df_new.drop(feature_list,axis=1,inplace=True)
    df_new=df_new.astype(dict(df1.dtypes))
    print(df_new)
    return df_new.fillna('').astype('str')
def make_difference(df1,df2):
    return pd.concat([df1,df2,df2],sort=False).drop_duplicates(keep=False).fillna('')
###############################################################################################
##### @PARAM: SET UNION Operation: Tab_1_Contents, Tab_2_Contents, Tab_1_Index, Tab_2_Index   #####

################################################################################################
#
#
################################################################################################
###### @PARAM: SET INTERSECTION Operation: Tab_1_Contents, Tab_2_Contents, Tab_1_Index, Tab_2_Index   #####

###############################################################################################


###############################################################################################
##### @PARAM: SET DIFFERENCE Operation: Tab_1_Contents, Tab_2_Contents, Tab_1_Index, Tab_2_Index   #####


@api_view(['POST'])
def ProcessQueries(request):
    #requested json payload
    #{"query_1_tab":3,"query_1":[[3273,"repeat",8546,8553,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,360,"",""],[3274,"repeat",9455,9462,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,361,"",""],[2492,"mRNA",15341,15652,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,270,"Albla_Nc14002490",""],[3266,"mRNA",17934,18269,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,358,"Albla_Nc14002500",""],[2552,"mRNA",18193,19398,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,278,"Albla_Nc14002510","conserved hypothetical protein"],[3275,"repeat",21759,21766,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,362,"",""],[3196,"mRNA",26635,26961,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,347,"Albla_Nc14002520",""],[2888,"mRNA",27112,28039,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,309,"Albla_Nc14002530",""],[3028,"mRNA",28949,29341,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,326,"Albla_Nc14002540",""],[3176,"mRNA",33508,34095,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,343,"Albla_Nc14002550","conserved hypothetical protein"],[2978,"mRNA",35451,35930,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,320,"Albla_Nc14002560","ribosomal protein L38 putative"],[3653,"mRNA",35994,38240,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,428,"Albla_Nc14002570","conserved hypothetical protein"],[2918,"mRNA",37777,43187,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,313,"Albla_Nc14002580","conserved unknown protein putative"],[2662,"mRNA",43382,45400,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,290,"Albla_Nc14002590","hypothetical protein LOC100382497"],[2846,"mRNA",45432,49149,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,306,"Albla_Nc14002600","protein phosphatase 2 putative"],[3150,"mRNA",49306,50679,"Organism = Albugo laibachii Nc14, Version = 1",890382,"Scaffold_2",1,340,"Albla_Nc14002610","serine/threonineprotein phosphatase 2A regulatory subunit B' putative"]],"query1_header":[],"query_2_tab":8,"query_2":[[3113,"Albla_Nc14028110","tRNA-binding domain",890382,1,"Albugo laibachii"],[3861,"Albla_Nc14034350","tRNA-binding domain",890382,1,"Albugo laibachii"],[5633,"Albla_Nc14050650","tRNA-binding domain",890382,1,"Albugo laibachii"]],"query2_header":[],"operator":"union"}




#    print("DEBUGGING")    
    res_data = json.loads(request.body.decode("utf-8"))
    # print("\n\nResponse",res_data) 
    # print("\n\nQuery1",res_data['query_1']) 
    # print("\n\nQuery2",res_data['query_2']) 
    # print("DATAFRAME")
    if res_data['query_1_tab']<=9 and res_data['query_2_tab']<=9:
        query1_df=dataframe_make(res_data['query_1_tab'],res_data['query_1'],title=None)
        query2_df=dataframe_make(res_data['query_2_tab'],res_data['query_2'],title=None)
        #print(query1_df)
        #print(query2_df)
    elif res_data['query_1_tab']>9 and res_data['query_2_tab']<=9:
        #pass
        tab_result_title= res_data['query1_header']
        #resultantQuery_idx,resultantQuery_title,resultantQuery_dict=selectTabContentIndex(res_data['query_1_tab'],tab_result_title)
        query1_df=dataframe_make(res_data['query_1_tab'],res_data['query_1'],tab_result_title)
        query2_df=dataframe_make(res_data['query_2_tab'],res_data['query_2'],title=None)

    elif res_data['query_1_tab']<=9 and res_data['query_2_tab']>9:
        #pass
        tab_result_title= res_data['query2_header']
        #resultantQuery_idx,resultantQuery_title,resultantQuery_dict=selectTabContentIndex(res_data['query_1_tab'],tab_result_title)
        query1_df=dataframe_make(res_data['query_1_tab'],res_data['query_1'],title=None)
        query2_df=dataframe_make(res_data['query_2_tab'],res_data['query_2'],tab_result_title)
    elif res_data['query_1_tab']>9 and res_data['query_2_tab']>9:
        #pass
        tab_result_title= res_data['query1_header']
        #resultantQuery_idx,resultantQuery_title,resultantQuery_dict=selectTabContentIndex(res_data['query_1_tab'],tab_result_title)
        query1_df=dataframe_make(res_data['query_1_tab'],res_data['query_1'],title=tab_result_title)
        tab_result_title= res_data['query2_header']
        query2_df=dataframe_make(res_data['query_2_tab'],res_data['query_2'],tab_result_title)
    
    # if  res_data['query_1_tab']>9:  
    #      tab_result_title= res_data['query1_header']
    #      resultantQuery_idx,resultantQuery_title,resultantQuery_dict=selectTabContentIndex(res_data['query_1_tab'],tab_result_title)
        
    #     print("Debugging query1 header",res_data['query1_header'])
    #     print("Debdugging query1",res_data['query_1'])
    #     print("Debugging query2 header",res_data['query2_header'])
    #     print("")
    #     print("Debdugging query2",res_data['query_2'])
    #     print("Resultant Query")
    #     print(resultantQuery_dict)
        
    #     #Query_index, Query_title, Query_mapped_dict=selectTabContentIndex(res_data['query1_tab'],tab_result_title)
        
    # if  res_data['query_2_tab']>9:
    #     tab_result_title= res_data['query2_header']
    #     resultantQuery_idx,resultantQuery_title,resultantQuery_dict=selectTabContentIndex(res_data['query_2_tab'],tab_result_title)
    #     print("Debugging query2 header",res_data['query2_header'])
    #     print("Debdugging query2",res_data['query_2'])
    #     print("Debugging query1 header",res_data['query1_header'])
    #     print("Debdugging query1",res_data['query_1'])
    #     print("Resultant Query")
    #     print(resultantQuery_dict)
#        Query_index, Query_title, Query_mapped_dict=selectTabContentIndex(res_data['query2_tab'],tab_result_title)
#    print(tab_result_title)
    print("\n************************ request ***************************{}\n".format(res_data))
    
    resultant_list = []
    final_list =[]

#    print("***** Initial_data ****** \n\n  QUERY 1:\n", res_data['query_1'], "\n\n  QUERY 2:\n", res_data['query_2'])
#    if res_data['query_1_tab'] >9 or res_data['query_2_tab']>9:
#        
#    selectTabContentIndex(res_data,res_data['query_1_tab'])
        
#============================================UNION=========================================================#

    if res_data['operator'] == 'union':
        print('union')
        resultant_df=make_union(query1_df,query2_df)
        final_list=resultant_df.values.tolist()
        unique_title_list=resultant_df.columns.tolist()
        #print(final_list)
        #print(unique_title_list)


        # if len(res_data['query_1']) <= len(res_data['query_2']):
        #     Smaller_Query_Index = res_data['query_1_tab']
        #     Bigger_Query_Index  = res_data['query_2_tab']
        #     Smaller_Query = res_data['query_1']
        #     Smaller_Query_Copy = Smaller_Query
        #     Bigger_Query  = res_data['query_2']
        #     Bigger_Query_Copy = copy.deepcopy(Bigger_Query)
        #     Smaller_Query_Title=res_data['query1_header']
        #     Bigger_Query_Title=res_data['query2_header']
        # else:
        #     Smaller_Query_Index = res_data['query_2_tab']
        #     Bigger_Query_Index  = res_data['query_1_tab']
        #     Smaller_Query = res_data['query_2']
        #     Smaller_Query_Copy = Smaller_Query
        #     Bigger_Query  = res_data['query_1']
        #     Bigger_Query_Copy = copy.deepcopy(Bigger_Query)
        #     Smaller_Query_Title=res_data['query2_header']
        #     Bigger_Query_Title=res_data['query1_header']

        # # For debugging, please remove when done
        # print("\n\nSize of Query 1: ",len(res_data['query_1']))
        # print("\n\nSize of Query 2: ",len(res_data['query_2']))

        # print("\n\nID : ", id(Smaller_Query), "               -               ", id(Smaller_Query_Copy))
            
        # if (Smaller_Query_Index > 9) and (Bigger_Query_Index<=9):
        #     print("\n\nSmaller Resultant\n")
        #     Smaller_Query_index, Smaller_Query_title, Smaller_Query_mapped_dict=selectTabContentIndex(Smaller_Query_Index,Smaller_Query_Title)
        #     Bigger_Query_index, Bigger_Query_title, Bigger_Query_mapped_dict = selectTabContentIndex(Bigger_Query_Index)


        # elif Smaller_Query_Index <= 9 and Bigger_Query_Index > 9:
        #     print("\n\nBigger Resultant\n")
        #     Smaller_Query_index, Smaller_Query_title, Smaller_Query_mapped_dict=selectTabContentIndex(Smaller_Query_Index,title=None)
        #     Bigger_Query_index, Bigger_Query_title, Bigger_Query_mapped_dict = selectTabContentIndex(Bigger_Query_Index,Bigger_Query_Title)
        #     print("\n\nBigger Query Dictionary for 1st condition\n",Bigger_Query_mapped_dict)

        # elif (Smaller_Query_Index > 9) and (Bigger_Query_Index>9):
        #     print("\n\nBoth Smaller & Bigger Resultant\n")
        #     Smaller_Query_index, Smaller_Query_title, Smaller_Query_mapped_dict=selectTabContentIndex(Smaller_Query_Index,Smaller_Query_Title)
        #     Bigger_Query_index, Bigger_Query_title, Bigger_Query_mapped_dict = selectTabContentIndex(Bigger_Query_Index,Bigger_Query_Title)
        # else:
        #     print("\n\nNo new Resultant Query\n")
        #     Smaller_Query_index, Smaller_Query_title, Smaller_Query_mapped_dict = selectTabContentIndex(Smaller_Query_Index)
        #     Bigger_Query_index, Bigger_Query_title, Bigger_Query_mapped_dict = selectTabContentIndex(Bigger_Query_Index)
        
        # print("\n\n=====================Smaller title========================\n")
        # print(Smaller_Query_title)
        # print("\n\n===================Debugging smaller=======================\n")
        # print(Smaller_Query)   
        # print("\n\n===================Bigger title============================\n")
        # print(Bigger_Query_title)
        # print("\n\n===================Debugging bigger========================\n")
        # print(Bigger_Query)

        # # Variable to store unique list name of union function
        # unique_title_list = list(set(Smaller_Query_title).union(set(Bigger_Query_title)))

        # # Set Transcript Name to the first ID of the list
        # for count, ele in enumerate(unique_title_list):
        #     if ele == "Transcript Name":
        #         unique_title_list[count], unique_title_list[0] = unique_title_list[0], ele
        # print("\n\n*****************Unique title list*****************\n",unique_title_list)
         
        # print("\n\n========================Executing Query check for UNION=========================\n")

        # print("\n\nRANGE OF SMALLER QUERY : ", len(Smaller_Query))
        # print("\n\nRANGE OF BIGGER QUERY : ", len(Bigger_Query), "\n")

        # # Check For similarities in Both the list 
        # for ele in range(len(Smaller_Query)):
        #     # print("Element 1 : ",Smaller_Query[ele][Smaller_Query_index[0]])
        #     for ele2 in range(len(Bigger_Query)):
        #         # print(ele2)
        #         # print("Element 2 : ",Bigger_Query[ele2][Bigger_Query_index[0]])
        #         if Smaller_Query[ele][Smaller_Query_index[0]] == Bigger_Query[ele2][Bigger_Query_index[0]]:
        #             for title in range(len(unique_title_list)):
        #                 if unique_title_list[title] in Smaller_Query_mapped_dict:
        #                     value = Smaller_Query_mapped_dict[unique_title_list[title]]
        #                     resultant_list.append(Smaller_Query[ele][value])
        #                     del Bigger_Query_Copy[ele2]
        #                     del Smaller_Query_Copy[ele]
                    
        #                 else:
        #                     value = Bigger_Query_mapped_dict[unique_title_list[title]]
        #                     resultant_list.append(Bigger_Query[ele][value])
        #                     del Bigger_Query_Copy[ele2]
        #                     del Smaller_Query_Copy[ele]
                        
        #                 final_list.append(resultant_list)
        #                 resultant_list = []
        
        # # Check if anything unique is left in the first list
        # if len(Smaller_Query_Copy) > 0:
        #     for ele in range(len(Smaller_Query_Copy)):
        #         for title in range(len(unique_title_list)):
        #             if unique_title_list[title] in Smaller_Query_mapped_dict:
        #                 value = Smaller_Query_mapped_dict[unique_title_list[title]]
        #                 resultant_list.append(Smaller_Query_Copy[ele][value])
                    
        #             else:
        #                 resultant_list.append("")
                        
        #         final_list.append(resultant_list)
        #         resultant_list = []
                
        # # Check what is left in the other list
        # if len(Bigger_Query_Copy) > 0:
        #     for ele in range(len(Bigger_Query_Copy)):
        #         for title in range(len(unique_title_list)):
        #             if unique_title_list[title] in Bigger_Query_mapped_dict:
        #                 value = Bigger_Query_mapped_dict[unique_title_list[title]]
        #                 resultant_list.append(Bigger_Query_Copy[ele][value])
        #             else:
        #                 resultant_list.append("")
                        
        #         final_list.append(resultant_list)
        #         resultant_list = []

        # print("\n\n================FINAL LIST=================\n",final_list)
        # print("\n\n================HEADER=================\n",unique_title_list)


#============================================================================================================#        


#============================================INTERSECTION====================================================#

    if res_data['operator'] == 'intersection':
        print("intersection")
        resultant_df=make_intersection(query1_df,query2_df)
        final_list=resultant_df.values.tolist()
        unique_title_list=resultant_df.columns.tolist()
        #print(final_list)
        #print(unique_title_list)
#         if len(res_data['query_1']) <= len(res_data['query_2']):
#             Smaller_Query_Index = res_data['query_1_tab']
#             Bigger_Query_Index  = res_data['query_2_tab']
#             Smaller_Query = res_data['query_1']
#             Smaller_Query_Copy = Smaller_Query
#             Bigger_Query  = res_data['query_2']
#         else:
#             Smaller_Query_Index = res_data['query_2_tab']
#             Bigger_Query_Index  = res_data['query_1_tab']
#             Smaller_Query = res_data['query_2']
#             Smaller_Query_Copy = Smaller_Query
#             Bigger_Query  = res_data['query_1']
            
#         Smaller_Query_index, Smaller_Query_title, Smaller_Query_mapped_dict = selectTabContentIndex(Smaller_Query_Index)
#         Bigger_Query_index, Bigger_Query_title, Bigger_Query_mapped_dict = selectTabContentIndex(Bigger_Query_Index)
        
#         # Variable to store unique list name of union function
#         unique_title_list = list(set(Smaller_Query_title).union(set(Bigger_Query_title)))
    
#         # Set Transcript Name to the first ID of the list
#         for count, ele in enumerate(unique_title_list):
#             if ele == "Transcript Name":
#                 unique_title_list[count], unique_title_list[0] = unique_title_list[0], ele
# #        print(unique_title_list)
         
#         # Check For similarities in Both the list 
#         for ele in range(len(Smaller_Query)):
#             for ele2 in range(len(Bigger_Query)):
#                 if Smaller_Query[ele][Smaller_Query_index[0]] == Bigger_Query[ele2][Bigger_Query_index[0]]:
#                     for title in range(len(unique_title_list)):
#                         if unique_title_list[title] in Smaller_Query_mapped_dict:
#                             value = Smaller_Query_mapped_dict[unique_title_list[title]]
#                             resultant_list.append(Smaller_Query[ele][value])
#                             del Bigger_Query[ele2]
#                             del Smaller_Query_Copy[ele]
                    
#                         else:
#                             value = Bigger_Query_mapped_dict[unique_title_list[title]]
#                             resultant_list.append(Bigger_Query[ele][value])
#                             del Bigger_Query[ele2]
#                             del Smaller_Query_Copy[ele]
                        
#                         final_list.append(resultant_list)
#                         resultant_list = []
                
        # Check if there is anything common or not
#        if len(final_list) == 0:
#            for title in range(len(unique_title_list)):
#                resultant_list.append("")
#            final_list.append(resultant_list) 

#============================================================================================================#


#==============================================DIFFERENCE====================================================#

    if res_data['operator'] == 'difference':
        print("difference")
        resultant_df=make_difference(query1_df,query2_df)
        final_list=resultant_df.values.tolist()
        unique_title_list=resultant_df.columns.tolist()
        #print(final_list)
        #print(unique_title_list)
#         Smaller_Query_Index = res_data['query_1_tab']
#         Bigger_Query_Index  = res_data['query_2_tab']
#         Smaller_Query = res_data['query_1']
#         Smaller_Query_Copy = Smaller_Query
#         Bigger_Query  = res_data['query_2']
        
#         Smaller_Query_index, Smaller_Query_title, Smaller_Query_mapped_dict = selectTabContentIndex(Smaller_Query_Index)
#         Bigger_Query_index, Bigger_Query_title, Bigger_Query_mapped_dict = selectTabContentIndex(Bigger_Query_Index)
        
#         # Variable to store unique list name of union function
#         unique_title_list = Smaller_Query_title
    
#         # Set Transcript Name to the first ID of the list
#         for count, ele in enumerate(unique_title_list):
#             if ele == "Transcript Name":
#                 unique_title_list[count], unique_title_list[0] = unique_title_list[0], ele
# #        print(unique_title_list)
         
#         # Check For similarities in Both the list 
#         for ele in range(len(Smaller_Query)):
#             for ele2 in range(len(Bigger_Query)):    
#                 if Smaller_Query[ele][Smaller_Query_index[0]] == Bigger_Query[ele2][Bigger_Query_index[0]]:
#                     del Smaller_Query_Copy[ele]
                        
        
#         # Check if anything unique is left in the first list
#         if len(Smaller_Query_Copy) > 0:
#             for ele in range(len(Smaller_Query_Copy)):
#                 for title in range(len(unique_title_list)):
#                     if unique_title_list[title] in Smaller_Query_mapped_dict:
#                         value = Smaller_Query_mapped_dict[unique_title_list[title]]
#                         resultant_list.append(Smaller_Query_Copy[ele][value])
                    
#                     else:
#                         resultant_list.append("")
#                 final_list.append(resultant_list)
#                 resultant_list = []
                        
#        else:
#            resultant_list = []
#            for title in range(len(unique_title_list)):
#                resultant_list.append("")
#                        
#            final_list.append(resultant_list)
#            resultant_list = []
                
#============================================================================================================#


    jsonReturns = {'result': final_list, 'header': unique_title_list}
    return Defaults.FinalResponse(jsonReturns)
   
   
   
'''    
    for idx_q1 in range(len(res_data['query_1'])):
        for idx_q2 in range(len(res_data['query_2'])):
            union_result = UNION_opt_perform(res_data['query_1'][idx_q1], res_data['query_2'][idx_q2], res_data['query_1_tab'], res_data['query_2_tab'])
            final_result.append(union_result)


    query_1_index, query_1_title = selectTabContentIndex(res_data['query_1_tab'])
    query_2_index, query_2_title = selectTabContentIndex(res_data['query_2_tab'])

    final_result_title = []    
    for query_idx in range(len(query_1_index)):
        final_result_title.append(query_1_title[query_idx])
        for query_idx_2 in range(len(query_2_index)):
            if query_2_index[query_idx_2] not in query_1_index:
                final_result_title.append(query_2_title[query_idx_2])
                break
                
        jsonReturns = {'result': final_result, 'header': final_result_title}
    return JsonResponse(jsonReturns)

'''
    
#    print("query_1_title", query_1_title, "query_2_title", query_2_title)
    #if matched_pos != -1:
#    final_result_title = query_1_title + query_2_title
 
        
            ##union_result, union_result_title = UNION_opt_arr(res_data['query_1'][idx_q1], res_data['query_2'][idx_q2], res_data['query_1_tab'], res_data['query_2_tab'])
    
    #final_result_title = union_result_title
    
    #print("UNION Result:", union_result)
    #print("Title of UNION Result:", union_result_title)
    #jsonReturns = {'result': union_result, 'header': union_result_title}
 
    


@api_view(['POST'])
def ProcessQueriesOld(request):
    res_data = json.loads(request.body.decode("utf-8"))
#    print("\n********** request *********", res_data)
    result_1 = []
    result_2 = []
    ##intersection_id = []
    
    if res_data['query_1_tab'] == "4":
        for idx in range(len(res_data['query_1'])):
            result_1.append(res_data['query_1'][idx][8])    
            result_1.append(res_data['query_1'][idx][10])
            result_1.append(res_data['query_1'][idx][7])  ## common

    if res_data['query_2_tab'] == "9":
        for idx in range(len(res_data['query_1'])):
            result_2.append(res_data['query_2'][idx][0])
            result_2.append(res_data['query_2'][idx][2])
            result_2.append(res_data['query_2'][idx][3])
            result_2.append(res_data['query_2'][idx][4])
            result_2.append(res_data['query_2'][idx][1])  ## common
    
    
    ##print("result_1", result_1, "\nresult_2", result_2)
    result = []
    for idx in range(len(result_1)):
        for idnx in range(len(result_2)):
            if idx == idnx:
                ##res = result_1[idx] + result_2[idnx]
                result.append(idx)                
                continue
#    f_res = []        
#    for idx in range(len(result)):
#        f_res.append(res_data['query_1'][idx][result[idx]])
##        f_res.append(res_data['query_2'][idx][result[idx]])
     
#    intersection_id.append(intersection(result_1, result_2))   
##    if len(intersection_id) > 0:         
##    jsonReturns = {'query': intersection_id}
  

####    jsonReturns = {'query': intersection_id}  
    jsonReturns = {'query': list(set(result_1).union(result_2))}
    return Defaults.FinalResponse(jsonReturns)



'''
t1 = ['Albla_Nc14089220', 890382, 0.501, 1.099, 0.002, 10113]
t2 = ['Albla_Nc14088890', 890382, 0.501, 1.133, 0.002, 10078]
'''

##### @PARAM: Tab_1_Contents, Tab_2_Contents, Tab_1_Index, Tab_2_Index   #####
def UNION_opt(query_tab1, query_tab2, tab_1_index, tab_2_index):
    final_result = []
    join_result = []    
    append_trigger = -1
    query_1_index, query_1_title = selectTabContentIndex(tab_1_index)
    query_2_index, query_2_title = selectTabContentIndex(tab_2_index)
    print("query_1_index%s", query_1_index)
    print("query_2_index%s", query_2_index)

    for idx_q1 in range(len(query_tab1)):
        join_result = []
#        print("TESTing", query_tab1[idx_q1])
        for idx_q2 in range(len(query_tab2)):
#            print("TESTing", query_tab2[idx_q2])
            for idx1 in len(range(query_tab1[idx_q1])):
                for idx2 in len(range(query_tab2[idx_q2])):
                    append_trigger = 0
                    if query_tab1[idx_q1][idx1] == query_tab2[idx_q2][idx2]:
                        #print("RESULT:", idx1, ':', query_tab1[idx1], " ---- ", idx2, ':', query_tab2[idx2])
                        for query_idx in range(len(query_1_index)):
                            join_result.append(query_tab1[idx_q1][query_1_index[query_idx]])
                        for query_idx in range(len(query_2_index)):
                            if query_2_index[query_idx] not in query_1_index:
                                join_result.append(query_tab2[idx_q2][query_2_index[query_idx]])
                        print("CHECK: %s", join_result)                        
                        final_result.append(join_result)
                        join_result = []
                        append_trigger = -1
                        break
                if append_trigger == -1:
                    break

    
    for idx1 in query_tab1[0]:
        for idx2 in query_tab2[0]:
            append_trigger = 0
            result_title = []
            if query_tab1[0][idx1] == query_tab2[0][idx2]:
                for query_idx in range(len(query_1_index)):
                    result_title.append(query_1_title[query_idx])
                for query_idx in range(len(query_2_index)):
                    if query_2_index[query_idx] not in query_1_index:
                        result_title.append(query_2_title[query_idx])
                append_trigger = -1
                break
            if append_trigger == -1:
                break
        if append_trigger == -1:
            break

    return final_result, result_title


##### @PARAM: Tab_1_Contents, Tab_2_Contents, Tab_1_Index, Tab_2_Index   #####
def UNION_opt_arr(query_tab1, query_tab2, tab_1_index, tab_2_index):
    final_result = []
    join_result = []    
    append_trigger = -1
    query_1_index, query_1_title = selectTabContentIndex(tab_1_index)
    query_2_index, query_2_title = selectTabContentIndex(tab_2_index)
    print("query_1_index%s", query_1_index)
    print("query_2_index%s", query_2_index)
    
    for idx1 in range(len(query_tab1)):
        for idx2 in range(len(query_tab2)):
            append_trigger = 0
            if query_tab1[idx1] == query_tab2[idx2]:
                #print("RESULT:", idx1, ':', query_tab1[idx1], " ---- ", idx2, ':', query_tab2[idx2])
                for query_idx in range(len(query_1_index)):
                    join_result.append(query_tab1[query_1_index[query_idx]])
                for query_idx in range(len(query_2_index)):
                    if query_2_index[query_idx] not in query_1_index:
                        join_result.append(query_tab2[query_2_index[query_idx]])
                final_result.append(join_result)
                join_result = []        
                append_trigger = -1
                break
        if append_trigger == -1:
            break

    for idx1 in range(len(query_tab1)):
        for idx2 in range(len(query_tab2)):
            append_trigger = 0
            result_title = []
            if query_tab1[idx1] == query_tab2[idx2]:
                for query_idx in range(len(query_1_index)):
                    result_title.append(query_1_title[query_idx])
                for query_idx in range(len(query_2_index)):
                    if query_2_index[query_idx] not in query_1_index:
                        result_title.append(query_2_title[query_idx])
                append_trigger = -1
                break
            if append_trigger == -1:
                break
        if append_trigger == -1:
            break

    return final_result, result_title
