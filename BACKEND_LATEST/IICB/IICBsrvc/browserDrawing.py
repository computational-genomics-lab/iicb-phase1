#from django.http import JsonResponse
#from django.core import serializers
import os
import mysql.connector
import array
import json
#from django.http import response
#from rest_framework.decorators import api_view
#from . import DBUtils
from . import function
from . import Defaults
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from django.conf import settings


print=settings.LOGGER.info # once in each module
print("Logging is configured in browserDrawing.")



#Functions called from browserUIHandlers.py
def _addNonCodingTracks(start_base, end_base, organism_name, version, exons_r, scaffold):

    NonCodingTracks = {'label': 'Non-Coding Regions'}
    feature_rects = []
    prevEndexon = -1
    prevfeatureID = -1
    last_end_base = -1

    for i in exons_r:
        if function.valid_exon_ends(i[1], i[2]) == False:
            continue

        # currfeatureID = $exons_r->[$i][5];
        currfeatureID = i[5]

        if currfeatureID != prevfeatureID:
            '''
            if (not defined($prevEndexon) )  # for drawing non-coding part from the start
            {
                if ($start_base < $exons_r->[$i][1])
                {
                    $image->filledRectangle($leftedge, $horzlevelGaps, 
                        $leftedge + ($exons_r->[$i][1]-$start_base) *$fraction, $horzlevelGaps + $rowht, $green);
                    $coordstring = join(",",$leftedge, $horzlevelGaps, $leftedge + (
                        $exons_r->[$i][1]-$start_base) *$fraction, $horzlevelGaps + $rowht);
                    & printMapping($coordstring, 'Non Coding Region',$exons_r->[$i][5],$organism_name,
                        $version,$detail_Link,$start_base,$exons_r->[$i][1] -$start_base,$scaffold);
                }
            }
            '''
            if prevEndexon < 0:
                feature = {'l': start_base,
                           'r': i[1],
                           'id': i[5],
                           'name': 'Non Coding region',
                           'link': ''}
                feature['link'] = Defaults.GetQualifiedLinkJSON('lnkNonCoding', START=start_base,
                                                                LEN=i[1] - start_base,
                                                                ORGANISM_NO=organism_name, VERSION=version,
                                                                SCAFFOLD=scaffold,
                                                                COLLAPSE=0, FEATURE_ID=i[5])

                feature_rects.append(feature)

            '''
            if ($prevEndexon != 0 && $prevEndexon < $exons_r->[$i][1])
            {
                $image->filledRectangle($leftedge + ($prevEndexon-$start_base) *$fraction, $horzlevelGaps, 
                    $leftedge + ($exons_r->[$i][1]-$start_base) *$fraction, $horzlevelGaps + $rowht, $green);
                $coordstring = join(",",$leftedge + ($prevEndexon-$start_base) *$fraction, $horzlevelGaps, $leftedge + (
                    $exons_r->[$i][1]-$start_base) *$fraction, $horzlevelGaps + $rowht);
                & printMapping($coordstring, 'Non Coding Region',$exons_r->[$i][5],$organism_name,$version,$detail_Link,
                    $prevEndexon,$exons_r->[$i][1] -$prevEndexon,$scaffold);
            }
            '''
            if prevEndexon != 0 and prevEndexon < i[1]:
                feature = {'l': prevEndexon, 'r': i[1], 'id': i[5], 'name': 'Non Coding region'}
                feature['link'] = Defaults.GetQualifiedLinkJSON('lnkNonCoding', START=prevEndexon, LEN=i[1] - prevEndexon,
                                    ORGANISM_NO=organism_name, VERSION=version, SCAFFOLD=scaffold,
                                    COLLAPSE=0, FEATURE_ID=i[5])
                feature_rects.append(feature)
        # end of if currfeatureID != prevfeatureID
        '''
        if ($exons_r->[$i][2] > $prevEndexon)
            $prevEndexon = $exons_r->[$i][2] + 1;
        $last_end_base =$exons_r->[$i][2];
        $prevfeatureID = $currfeatureID;
        '''
        if i[2] > prevEndexon:
            prevEndexon = i[2] + 1
        last_end_base = i[2]
        prevfeatureID = currfeatureID
    # end of for i in exons_r['features']

    if last_end_base >0 and last_end_base < end_base:
        '''
        my $new_start_loc =$last_end_base -$start_base;
        if (not defined($last_end_base))
            $new_start_loc=0;;

        $image->filledRectangle($leftedge+$new_start_loc * $fraction, $horzlevelGaps, $leftedge+($end_base-$start_base) * $fraction, $horzlevelGaps + $rowht, $green);
        $coordstring = join(",", $leftedge+$new_start_loc * $fraction, $horzlevelGaps, $leftedge+($end_base-$start_base) * $fraction, $horzlevelGaps + $rowht);
        & printMapping($coordstring, 'Non Coding Region', $exons_r->[$i][5], $organism_name, $version, $detail_Link, $last_end_base, $end_base-$last_end_base, $scaffold);
        '''
        new_start_loc = last_end_base - start_base
        if new_start_loc < 0:
            new_start_loc = 0
        feature = {'l': new_start_loc, 'r': end_base, 'id': i[5], 'name': 'Non Coding region'}
        feature['link'] = Defaults.GetQualifiedLinkJSON('lnkNonCoding', START=last_end_base, LEN=end_base - last_end_base,
                                                    ORGANISM_NO=organism_name, VERSION=version, SCAFFOLD=scaffold,
                                                    COLLAPSE=0, FEATURE_ID=i[5])
        feature_rects.append(feature)
    #end of if last_end_base < end_base:

    NonCodingTracks['Rects'] = feature_rects

    return NonCodingTracks


def _addCodingTracks(start_base, end_base, organism_name, version, gaps_r, exons_r):
    # start local variables
    horzlevelGaps = 0
    coordstring = 0  # To be used by mapping
    detail_Link = 0  # To be used by mapping

    currfeatureID = 0
    prevfeatureID = 0
    prevEndexon = 0
    prevEndTstarts = 0
    count = 0  # the number of exons in the current scaffold
    flag = 0

    # end local variables

    #$image->string(gdLargeFont, 10, $horzlevelCoding, "Gene Models ", $blue);
    CodingTracks = {'label': 'Gene Models', 'stranded': 1}
    feature_rects = []

    #print("DBG [addCodingTracks]: exon len" + str(len(exons_r)))
    for i in exons_r:
        #print("DBG [addCodingTracks]: i:" + str(i) + "(" + str(i[1])+","+str(i[2])+")")
        if function.valid_exon_ends(i[1], i[2]) == False:
            continue
        '''
        if ($exons_r->[$i][10] != 3)
            $color =$red;
        else
            $color =$blue;
        '''
        color = 'blue'
        if i[10] != 3:
            color = 'red'

        #$currfeatureID = $exons_r->[$i][5];
        currfeatureID = i[5]

        '''
        if ($prevEndexon > $exons_r->[$i][1] and $flag == 1)
        {
            $flag = 0;
            $horzlevelCoding = 135;
            # print "$exons_r->[$i][1]<br>";
        }
        else
        {
            $horzlevelCoding = 120;
            $flag = 1;
        }
        '''
        if prevEndexon > i[1] and flag == 1:
            flag = 0
            horzlevelCoding = 135
        else:
            flag = 1
            horzlevelCoding = 120

        '''
        # $horzlevelCoding =  12* $rowht + $minorgap;

        $start_min =$leftedge + ($exons_r->[$i][1] -  $start_base) *$fraction;
        $end_min =$leftedge + ($exons_r->[$i][2] -$start_base) *$fraction;

        $image->filledRectangle($start_min, $horzlevelCoding, $end_min, $horzlevelCoding + $rowht, $color);
        # This portion is only for Print Mapping
        $coordstring = join(",",$start_min, $horzlevelCoding, $end_min, $horzlevelCoding + $rowht);
        & printMapping($coordstring,$exons_r->[$i][7],$exons_r->[$i][8],$organism_name,$version,$detail_Link);
        '''
        feature = {'l': i[1], 'r': i[2], 'h': horzlevelCoding, 'id': i[5], 'color': color, 'name':i[7]}
        feature['link'] = Defaults.GetQualifiedLinkJSON('lnkCoding', LEN=i[8], #START=i[1], 
                                                ORGANISM_NO=organism_name, VERSION=version,
                                                COLLAPSE=0, FEATURE_ID=i[5])

        #
        #draw start or end arrow
        #
        '''
        my $poly = new GD::Polygon;
        if ($exons_r->[$i][3] == 1)
        {
            $poly->addPt( $leftedge + ($exons_r->[$i][1] - $start_base) * $fraction, $horzlevelCoding );
            $poly->addPt( $leftedge + ($exons_r->[$i][1] - $start_base) * $fraction, $horzlevelCoding + $rowht );
            $poly->addPt( $leftedge + (
                $exons_r->[$i][1] - $start_base) * $fraction - 3, $horzlevelCoding + $rowht / 2 );
            $image->filledPolygon( $poly, $color );
        }
        else
        {
            $poly->addPt( $leftedge + ($exons_r->[$i][2] - $start_base) * $fraction, $horzlevelCoding );
            $poly->addPt( $leftedge + ($exons_r->[$i][2] - $start_base) * $fraction, $horzlevelCoding + $rowht );
            $poly->addPt( $leftedge + (
                $exons_r->[$i][2] - $start_base) * $fraction + 3, $horzlevelCoding + $rowht / 2 );
            $image->filledPolygon( $poly, $color );
        }
        '''
        # Indicate whether to draw arrowhead on Left side or right side
        if i[3] == 1:
            feature['arrow'] = 'l'
        else:
            feature['arrow'] = 'r'

        #$prevEndexon = $exons_r->[$i][2];
        #$prevfeatureID = $currfeatureID;
        prevEndexon = i[2]
        prevfeatureID = currfeatureID

        feature_rects.append(feature)

    # end of for i in exons_r:
    CodingTracks['Rects'] = feature_rects
    return CodingTracks


def _getStartBaseEndBase(start_base, end_base, featureidLeftBase, featureidRightBase):
    maxStarts = 0
    minEnds = 0

    if start_base <= featureidLeftBase:
        maxStarts = featureidLeftBase
    else:
        maxStarts = start_base

    # find the minimum of the end bases among $end_base and $featureidRightBase
    if end_base >= featureidRightBase:
        minEnds = featureidRightBase
    else:
        minEnds = end_base

    if maxStarts >= minEnds:
        return [-1, -1]
    else:
        return [maxStarts,minEnds]
