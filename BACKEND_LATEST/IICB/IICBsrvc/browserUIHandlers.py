from django.http import JsonResponse
from django.core import serializers
import os
import mysql.connector
import array
import json
from django.http import response
from rest_framework.decorators import api_view
from . import DBUtils
from . import function
from . import browserDrawing
from . import Defaults
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from django.conf import settings
print=settings.LOGGER.info # once in each module
print("Logging is configured in browserUIHandlers.")




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

def changeView(jsondata):
    print(jsondata)

    jsonret = {'status':-1}
    gaps = {}
    intermediate_data = {}
    drawing = []  # array of dict
    # $len = getLen($FORM_r->{'organism'},$FORM_r->{'scaffold'},$FORM_r->{'version'})
    intermediate_data['len'] = function._getLen(jsondata['organism'], jsondata['scaffold'], jsondata['version'])

    # exons = getfeatures($FORM_r->{'organism'},$FORM_r->{'scaffold'},$FORM_r->{'version'},$FORM_r->{'startbase'},$FORM_r->{'stopbase'});
    #intermediate_data['exons'] = function._getfeatures(jsondata['organism'], jsondata['scaffold'], jsondata['version'], jsondata['startbase'], jsondata['stopbase'])
    exons = function._getfeatures(jsondata['organism'], jsondata['scaffold'], jsondata['version'],
                                  jsondata['startbase'], jsondata['stopbase'])
    intermediate_data['exons'] = exons

    # drawing codes
    # addNonCodingTracks($FORM_r->{'startbase'},$FORM_r->{'stopbase'},$FORM_r->{'organism'},$FORM_r->{'version'},
    #                             exons, $lnkNonCoding,$FORM_r->{'scaffold'});
    NonCodingTracks = browserDrawing._addNonCodingTracks(jsondata['startbase'],jsondata['stopbase'],
                                jsondata['organism'],jsondata['version'], exons['features'], jsondata['scaffold'])
    drawing.append(NonCodingTracks)


    # addCodingTracks($FORM_r->{'startbase'},$FORM_r->{'stopbase'},$FORM_r->{'organism'},\
    #               $FORM_r->{'version'},\@gaps,\@exons,$lnkCoding);
    codingTracks = browserDrawing._addCodingTracks(jsondata['startbase'],jsondata['stopbase'],
                                jsondata['organism'], jsondata['version'], gaps, exons['features'])
    drawing.append(codingTracks)

    # This Part is for to create Scaffold Data
    # scaffold_info = getScaffold($FORM_r->{'organism'},$FORM_r->{'scaffold'},$FORM_r->{'version'});
    intermediate_data['getScaffold'] = function._getScaffold(jsondata['organism'],jsondata['scaffold'],jsondata['version'])
    scaffold_info = intermediate_data['getScaffold']['features']
    #TODO - remove the following line - added just for test
    #scaffold_info = [[1, 2], [2, 3], [3, 4]]

    # tRNA,REPEATS,PROMOTER start
    # my % trp = & trp_info(1,$FORM_r->{'organism'},$FORM_r->{'scaffold'},$FORM_r->{'version'});
    # if (% trp)
    #    & TPRTrack($FORM_r->{'startbase'},$FORM_r->{'stopbase'},$FORM_r->{'organism'},$FORM_r->{'version'}, % trp,$otherlink,$contig_count);

    intermediate_data['trp'] = function._trp_info(1,jsondata['organism'],jsondata['scaffold'],jsondata['version'])

    #'promo': "/cgi-bin/eumicrobedb/promo.cgi?ID=::FEATURE_ID::&organism=::ORGANISM_NO::&version=::VERSION::&collapse=::COLLAPSE::",
    contig_count = 0

    # _TPRTrack is a drawing function
    if intermediate_data['trp']['status'] > 0:
        otherlink = 'promo'
        TPRTrack_val = function._TPRTrack(jsondata['startbase'],jsondata['stopbase'], \
                                                 jsondata['organism'],jsondata['version'], \
                                                 intermediate_data['trp']['trpl'], otherlink, contig_count)
        contig_count = TPRTrack_val['contig_count']
        drawing.append(TPRTrack_val)
    
    # trp_count = keys % trp;
    # contig_count =$contig_count + $trp_count;
    trp_count = len(intermediate_data['trp']['trpl'])
    intermediate_data['trp_count'] = trp_count
    contig_count = contig_count + trp_count
    intermediate_data['contig_count'] = contig_count

    # Synteny Track start
    # synteny = get_synteny_info(1,$scaffold_info[0][1],$FORM_r->{'organism'},$FORM_r->{'startbase'},$FORM_r->{'stopbase'});
    #if (synteny)
    #    $contig_count + +;
    #    SyntenyTracks($FORM_r->{'startbase'},$FORM_r->{'stopbase'},\ % synteny,$syntenylink,$FORM_r->{'scaffold'},$contig_count);
    #
    # $count_synteny = keys % synteny;
    # dict synenty is to represent sparse 2D array, Index is of the format <row>_<col>
    intermediate_data['get_synteny_info'] = function. _get_synteny_info(1, scaffold_info[0][1], \
            jsondata['organism'],jsondata['startbase'],jsondata['stopbase'])
    synteny = intermediate_data['get_synteny_info']['synteny']

    # drawing function of Synteny tracks
    if intermediate_data['get_synteny_info']['status'] > 0:
        contig_count = contig_count + 1

        syntenylink = 'syntenylink'

        SyntenyTracks_val = function._SyntenyTracks(jsondata['startbase'],jsondata['stopbase'], \
                synteny, syntenylink, jsondata['scaffold'], contig_count);
        #
        contig_count = SyntenyTracks_val['contig_count']
        drawing.append(SyntenyTracks_val)
    
    count_synteny = len(synteny)
    intermediate_data['count_synteny'] = count_synteny

    base_start = 0
    if contig_count == 0:
        base_start = 130
    elif contig_count == 1:
        base_start = 170
    elif contig_count == 2:
        base_start = 230
    elif contig_count == 3:
        base_start = 260
    elif contig_count == 4:
        base_start = 320

    synteny_end = base_start + count_synteny*(24)+10

    # my %contig =&get_est(1,$scaffold_info[0][1]);
    get_est_val = function._get_est(1, scaffold_info[0][1])
    intermediate_data['get_est'] = get_est_val

    # drawing function of est
    if get_est_val['status'] > 0:
        contig_count = contig_count + 1

        # &EstTracks($FORM_r->{'startbase'},$FORM_r->{'stopbase'},\%contig,$estlink,$field[1],$contig_count,$synteny_end);
        estlink = 'estlink'
        field1 = 0 #UNUSED in _EstTracks
        config = get_est_val['synenty']
        estTracks = function._EstTracks(jsondata['startbase'],jsondata['stopbase'], config, estlink, \
                                                    field1, contig_count, synteny_end)
        contig_count = estTracks['contig_count']
        drawing.append(estTracks)
    
    intermediate_data['contig_count3'] = contig_count

    jsonret['intermediate'] = intermediate_data
    jsonret['drawing'] = drawing
    jsonret['Status'] = len(exons)
    return jsonret


#
# For Chromosome page - get the string to show with the menubar
# Called from browserUI.cgi as get_organism(organism, version)
#
def get_organism(taxon, version):
    # get_organism defined in function_new.cgi

    #my $dbh = DBI->connect($Defaults::db_ConnString,$Defaults::db_UserName, $Defaults::db_Password, {
    #    RaiseError = > 1, AutoCommit = > 0}) | | die "Error connecting to server";
    db = DBUtils.MariaConnection('SRES')

    #my $sql = "select * from organism where taxon_ID=$taxon and version=$version";
    sql = "select * from organism where taxon_ID=" + str(taxon) + " and version=" + str(version)
    #$sth->execute | | die "error in executing query";
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)

    #while (my @ arry = $sth->fetchrow_array())
    #    print "$arry[2] $arry[3] (V$arry[12])";

    if len(results) > 0:
        return results[0][2] + " " + results[0][3] + " (V" + str(results[0][12]) + ")"
    return "NO-NAME found"

#
# For Chromosome page - get the string to scaffold link
# Referenced from browserUI.cgi as
# href="/cgi-bin/eumicrobedb/downloadScaffold.cgi?id=$cgi_session_id"
#
def get_scaffold_link():
    # SHOULD BE replaced with print as pdf
    return None