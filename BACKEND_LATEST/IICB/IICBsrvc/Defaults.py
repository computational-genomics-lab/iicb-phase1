from django.http import JsonResponse

from django.conf import settings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



print=settings.LOGGER.info # once in each module
print("Logging is configured in Defaults.")

import configparser,os
config = configparser.ConfigParser()
#CONFIGURATION='/home/azure/configuration.ini'
config.read(settings.CONFIGURATION)

STORAGE_PATH=config.get('folders','IICB_Graph')+'/'
CODON_PATH=config.get('folders','CODON_PATH')+'/'
EXE_PATH=config.get('folders','EXE_PATH')+'/'
SCI_OUT_PATH=config.get('folders','SCI_OUT_PATH')+'/'
ABOUT_US_PATH=config.get('folders','ABOUT_US_PATH')+'/'
DOWNLOAD_PATH=config.get('folders','DOWNLOAD_PATH')+'/'


# STORAGE_PATH  = "/home/azure/IICB_Graph/"
# CODON_PATH    = "/home/azure/Downloads/Executables/"
# EXE_PATH      = "/home/azure/Downloads/Executables/"
# SCI_OUT_PATH  = "/var/www/html/media/SCI_OUT/"     #"/home/azure/IICB_Graph/"   #This path must be exposed to outside client 
# ABOUT_US_PATH = "/var/www/html/media/ABOUT_US/"
# DOWNLOAD_PATH = "/var/www/html/media/DOWNLOAD/"




DefLinks = {'noncodeing': "/eumicrobedb/noncoding.cgi",
         'lnkNonCoding': "/cgi-bin/eumicrobedb/noncoding.cgi?StartPosition=::START::&Length=::LEN::&organism=::ORGANISM_NO::&version=::VERSION::&scaffold=::SCAFFOLD::&collapse=::COLLAPSE::",
         'lnkCoding': "/cgi-bin/eumicrobedb/browserDetail.cgi?ID=::FEATURE_ID::&organism=::ORGANISM_NO::&version=::VERSION::&collapse=::COLLAPSE::",
         'promo': "/cgi-bin/eumicrobedb/promo.cgi?ID=::FEATURE_ID::&organism=::ORGANISM_NO::&version=::VERSION::&collapse=::COLLAPSE::",
         'estlink': "/cgi-bin/eumicrobedb/est.cgi?ID=::FEATURE_ID::&organism=::ORGANISM_NO::&version=::VERSION::&organism1=::START::&collapse=::COLLAPSE::",
         'syntenylink': "/cgi-bin/eumicrobedb/synteny.cgi?StartPosition=::START::&Length=::LEN::&organism=::ORGANISM_NO::&version=::VERSION::&scaffold=::SCAFFOLD::&collapse=::COLLAPSE::",
         'gfflink': "/cgi-bin/eumicrobedb/gff.cgi?StartPosition=::START::&Length=::LEN::&organism=::ORGANISM_NO::&version=::VERSION::&scaffold=::SCAFFOLD::&collapse=::COLLAPSE::"
         }


def FinalResponse(response):
    resp = JsonResponse(response)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def GetQualifiedLink(linkName, START = 0, LEN = 0, ORGANISM_NO = None, VERSION = None, SCAFFOLD = None, COLLAPSE = 0, FEATURE_ID = 0):
    #StartPosition=::START::
    #organism1=::START::
    #Length=::LEN::
    #organism=::ORGANISM_NO::
    #version=::VERSION::
    #scaffold=::SCAFFOLD::
    #collapse=::COLLAPSE::
    #ID=::FEATURE_ID::

    link = DefLinks[linkName]
    if link is None:
        return None
    if START is not None:
        link = link.replace('::START::', str(START))
    if LEN is not None:
        link = link.replace('::LEN::', str(LEN))
    if ORGANISM_NO is not None:
        link = link.replace('::ORGANISM_NO::', str(ORGANISM_NO))
    if VERSION is not None:
        link = link.replace('::VERSION::', str(VERSION))
    if SCAFFOLD is not None:
        link = link.replace('::SCAFFOLD::', SCAFFOLD)
    if COLLAPSE is not None:
        link = link.replace('::COLLAPSE::', str(COLLAPSE))
    if FEATURE_ID is not None:
        link = link.replace('::FEATURE_ID::', str(FEATURE_ID))

    return link

def GetQualifiedLinkJSON(linkName, START = 0, LEN = 0, ORGANISM_NO = None, VERSION = None, SCAFFOLD = None, COLLAPSE = 0, FEATURE_ID = 0):
    #StartPosition=::START::
    #organism1=::START::
    #Length=::LEN::
    #organism=::ORGANISM_NO::
    #version=::VERSION::
    #scaffold=::SCAFFOLD::
    #collapse=::COLLAPSE::
    #ID=::FEATURE_ID::

    jsonRet = {'link': linkName}

    link = DefLinks[linkName]
    if link is None:
        return None

    if START is not None:
        jsonRet['startbase'] = START
    else:
        jsonRet['startbase'] = 1
    if LEN is not None:
        jsonRet['len'] = LEN
    else:
        jsonRet['len'] = 1


    if ORGANISM_NO is not None:
        jsonRet['organism'] = str(ORGANISM_NO)
    if VERSION is not None:
        jsonRet['version'] = str(VERSION)
    if SCAFFOLD is not None:
        jsonRet['scaffold'] = str(SCAFFOLD)
    if COLLAPSE is not None:
        jsonRet['collapse'] = COLLAPSE
    if FEATURE_ID is not None:
        jsonRet['feature_id'] = FEATURE_ID

    return jsonRet

'''
% contigsColorForQuality = (1 = > $red,  # Best Blat_Alignment_Quality_ID
2 = > $violet,
3 = > $aqua,
4 = > $black  # Worst Blat_Alignment_Quality_ID
'''
# index 0 is UNUSED
contigsColorForQuality = [{'quality': 0, 'color': 'green', 'RGB': '0,255,0'},
                          {'quality': 1, 'color': 'red', 'RGB': '255,0,0'},
                          {'quality': 2, 'color': 'violet', 'RGB': '148,0,211'},
                          {'quality': 3, 'color': 'aqua', 'RGB': '127,255,212'},
                          {'quality': 4, 'color': 'black', 'RGB': '0,0,0'},
                          ]
