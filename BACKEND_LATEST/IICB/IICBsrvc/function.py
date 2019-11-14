from django.http import JsonResponse
from django.core import serializers
import os
import array
import json
from . import DBUtils
from . import Defaults


from django.conf import settings
print=settings.LOGGER.info # once in each module

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#from . import browserDrawing

#helper functions
def valid_exon_ends(start, end):
    if start is None:
        return False
    if end is None:
        return False
    if start == -1 or end == -1:
        return False
    if start >= end:
        return False
    return True

#new helper functions defined

def _createclean2Darry(results):
    '''
    undef @ features;
    while (my @ arry = $sth->fetchrow_array())
        my @ temp;

        foreach my $line( @ arry)
            if (defined  $line)
                push @ temp, $line;
            else
                push @ temp, -1;  # set to -1 when any element is missing
        push @ features, [ @ temp];
    '''
    features = []
    for arry in results:
        temp = []
        for line in arry:
            if line is not None:
                temp.append(line)
            else:
                temp.append(-1)
        # end of for line in arry:
        features.append(temp)
    # end for arry in results:
    return features

#end new helper functions defined

def getACname():
    #NOT CALLED
    return None

def _getLen(organism, scaffold, version):
    retlen = 0
    #my $sql = "select * from externalnasequence where taxon_ID=$organism and source_ID='$scaffold' and sequence_type_ID=1 and sequence_version='$version'";
    sql = "select * from externalnasequence where taxon_ID="\
          +str(organism) + " and source_ID='" + str(scaffold) + "' and sequence_type_ID=1 "\
          "and sequence_version='" + str(version) + "'";

    db = DBUtils.MariaConnection('DOTS')
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)
    #print(results)

    #while (my @ arry = $sth->fetchrow_array())
    #   $len =$arry[9];
    if len(results) > 0:
        retlen = results[0][9]

    return retlen;

#
# Function call from browserDetail.cgi
#
def _getCommonFeatures(id, na_sequence_id, organism):
    jsonret = {'status':-1}

    #my $id =$_[0];
    #my $na_sequence_id= $_[1];
    #my $organism= $_[2];
    

    sql = ""
    if id == 1: #for information about gene
        sql = "SELECT nl.na_feature_id, nl.start_min, nl.end_min, en.name, en.length, nl.is_reversed, en.sequence, \
                      nf.string4,en.source_ID,en.taxon_id,en.sequence_version,rs.review_status_ID,rs.name,rs.email_id \
                      FROM externalnasequence en, nafeatureimp nf, nalocation nl, oomycetes_cgl_sres.reviewstatus rs \
                      WHERE en.na_sequence_id = " + str(na_sequence_id) + \
                      " AND nf.na_sequence_id = en.na_sequence_id \
                        AND nf.name = 'gene' AND nl.na_feature_id = nf.na_feature_id \
                        AND rs.review_status_ID=nf.review_status_id"

    elif id == 2:#for information about exons
        sql = "SELECT nl.na_feature_id,nl.start_min,nl.end_min,nl.is_reversed \
                              FROM nafeature nf ,nalocation nl \
                         WHERE nf.na_sequence_id = " + str(na_sequence_id) + \
                                 " AND nf.name='exon' AND nl.na_feature_id = nf.na_feature_id \
                           ORDER BY nl.start_min"


    elif id == 3:#for HmmPfam
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant, c.prediction_id, c.pval_exp \
                           FROM geneinstance gi,rna r,protein p,proteininstance pi, HmmPfam c \
                               WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                                 " AND r.gene_ID=gi.gene_ID \
                                    AND p.rna_ID=r.rna_ID AND pi.protein_ID=p.protein_ID \
                                       AND c.protein_instance_id=pi.protein_instance_ID \
                                        ORDER BY c.location_start"


    elif id == 4:#for Super Family Prediction
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                       FROM geneinstance gi,rna r,protein p,proteininstance pi, SuperFamily c \
                           WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                            " AND r.gene_ID=gi.gene_ID \
                              AND p.rna_ID=r.rna_ID \
                                AND pi.protein_ID=p.protein_ID \
                                   AND c.protein_instance_id=pi.protein_instance_ID \
                                       ORDER BY c.location_start"
    elif id == 44: # copied form getCommonFeature (WITHOUT s) from function.cgi for ESTLink
        #     my $id=$_[0];
       # my $organism= $_[1];
       # my $scaffold =$_[2];
        #$sql="select * from externalnasequence where taxon_id=$organism and source_id = '$scaffold'";
        sql="SELECT * from externalnasequence where taxon_id=" + str(organism) + \
                  " AND source_id = '" + na_sequence_id + "'" 

    elif id == 5: #for Fprint Scan
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                     FROM geneinstance gi,rna r,protein p,proteininstance pi, FprintScan c \
                          WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                             " AND r.gene_ID=gi.gene_ID \
                                AND p.rna_ID=r.rna_ID \
                                    AND pi.protein_ID=p.protein_ID \
                                      AND c.protein_instance_id=pi.protein_instance_ID \
                                          ORDER BY c.location_start"


    elif id == 6: # for ProfileScan
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                       FROM geneinstance gi,rna r,protein p,proteininstance pi, ProfileScan c \
                             WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                                 " AND r.gene_ID=gi.gene_ID \
                                     AND p.rna_ID=r.rna_ID \
                                         AND pi.protein_ID=p.protein_ID \
                                             AND c.protein_instance_id=pi.protein_instance_ID \
                                                  ORDER BY c.location_start"


    elif id == 7: # for HmmSmart
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                      FROM geneinstance gi,rna r,protein p,proteininstance pi, HmmSmart c \
                            WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                              " AND r.gene_ID=gi.gene_ID \
                                   AND p.rna_ID=r.rna_ID \
                                       AND pi.protein_ID=p.protein_ID \
                                          AND c.protein_instance_id=pi.protein_instance_ID \
                                                 ORDER BY c.location_start"

    elif id == 8: # for HmmTigr
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                     FROM geneinstance gi,rna r,protein p,proteininstance pi, HmmTigr c \
                          WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                             " AND r.gene_ID=gi.gene_ID \
                                 AND p.rna_ID=r.rna_ID \
                                    AND pi.protein_ID=p.protein_ID \
                                        AND c.protein_instance_id=pi.protein_instance_ID \
                                              ORDER BY c.location_start"

    elif id == 9: #for HmmPanther
        sql= "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                   FROM geneinstance gi,rna r,protein p,proteininstance pi, HmmPanther c \
                        WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                           " AND r.gene_ID=gi.gene_ID \
                              AND p.rna_ID=r.rna_ID \
                                  AND pi.protein_ID=p.protein_ID \
                                     AND c.protein_instance_id=pi.protein_instance_ID \
                                           ODER BY c.location_start"

    elif id == 10: #for Gene3D
        sql = "SELECT c.location_start, c.location_stop, c.domain_name, c.pval_mant,c.prediction_id, c.pval_exp \
                     FROM geneinstance gi,rna r,protein p,proteininstance pi, Gene3D c \
                         WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                            " AND r.gene_ID=gi.gene_ID \
                                AND p.rna_ID=r.rna_ID \
                                   AND pi.protein_ID=p.protein_ID \
                                      AND c.protein_instance_id=pi.protein_instance_ID \
                                             ORDER BY c.location_start" 

    elif id == 11: #for interpro
        sql = "SELECT  distinct c.domain_name, c.prediction_id \
                        FROM geneinstance gi,rna r,protein p,proteininstance pi, InterPro c \
                  WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                             " AND r.gene_ID=gi.gene_ID \
                                 AND p.rna_ID=r.rna_ID \
                                    AND pi.protein_ID=p.protein_ID \
                                        AND c.protein_instance_id=pi.protein_instance_ID"                                             

    elif id == 12: # for GO
        sql = "SELECT DISTINCT g.name, g.acc, gcc.name \
                      FROM oomycetes_cgl_sres.go_term g, proteininstance pi, geneinstance gi, proteininstancefeature c, rna r, protein p, \
                             oomycetes_cgl_sres.goevidencecode gcc \
                                 WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                                      " AND r.gene_ID = gi.gene_ID \
                                           AND p.rna_ID = r.rna_ID \
                                               AND pi.protein_ID = p.protein_ID \
                                                   AND c.protein_instance_id = pi.protein_instance_ID \
                                                       AND g.acc = c.go_id \
                                                           AND gcc.description = c.go_id"


    elif id == 13: #for Protein
        sql = "SELECT na_feature_id, text1 \
                     FROM  `nafeatureimp` \
                WHERE na_sequence_id = " + str(na_sequence_id) + \
                  " AND name LIKE  '%mRNA%'"
 
    elif id == 14: # for Protein
        sql = "SELECT has_initial_exon, has_final_exon FROM genefeature WHERE na_feature_id = " + str(na_sequence_id)


    elif id == 22: #for information about exons old part
        sql = "SELECT nl.start_min,nl.end_min,nl.is_reversed,nl.na_feature_id \
                     FROM nafeature nf ,nalocation nl \
                WHERE nf.na_sequence_id = "+ str(na_sequence_id) + \
                           " AND nf.name='exon' \
                          AND nl.na_feature_id=nf.na_feature_id \
                          ORDER BY nl.start_min"


    elif id == 23: #information about feature by feature id from nafeatureimp
        sql = "SELECT naf.na_feature_id,naf.na_sequence_id,nl.start_min,nl.end_min,naf.subclass_view, \
                     substr(ns1.sequence,nl.start_min,nl.end_min-nl.start_min) AS sequence,ns.source_id,ns.taxon_id,naf.string18 \
                        FROM nafeatureimp naf,nalocation nl,externalnasequence ns,externalnasequence ns1 \
                           WHERE naf.na_feature_id = " + str(na_sequence_id) + \
                               " AND nl.na_feature_id=naf.na_feature_id \
                                   AND ns.na_sequence_id=naf.na_sequence_id \
                                     AND ns1.taxon_id=ns.taxon_id \
                                        AND ns1.sequence_version=ns.sequence_version \
                                           AND ns1.source_id=ns.source_id \
                                              AND ns1.sequence_type_id=1"                                 

                                                  
    elif id == 15: #signalp information
        sql = "SELECT distinct c.gene_ID, c.taxon_ID, c.`Y-score`, c.`D-score`, c.`Y-pos` \
                     FROM geneinstance gi, signalP c \
                        WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                          " AND c.gene_id=gi.gene_id"


    elif id == 16: #TMHMM information
        sql = "SELECT c.gene_ID, c.taxon_ID, c.Inside, c.Outside, c.TMhelix \
                     FROM geneinstance gi, TMHMM c \
                        WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                          " AND c.gene_id=gi.gene_id"


    elif id == 17: #SECRETOME information
        sql = "SELECT  distinct c.gene_ID, c.taxon_ID, c.`NN-score`, c.odds, c.weighted_score \
                     FROM geneinstance gi, SECRETOME c \
                         WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                            " AND c.gene_id=gi.gene_id"

    elif id == 18: #PROP information
        sql = "SELECT  distinct c.gene_ID, c.taxon_ID, c.position, c.context,c.score \
                    FROM geneinstance gi, PROP c \
                        WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                           " AND c.gene_id=gi.gene_id AND c.score >= 0.5"

    elif id == 19: #PSORT information
        sql = "SELECT  distinct c.gene_ID, c.taxon_ID, c.type, c.score \
                     FROM geneinstance gi, PSORT c \
                        WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                          " AND c.gene_id=gi.gene_id"


    elif id == 20: #for KO_ID information
        sql = "SELECT distinct t.`KO_ID`, p.`url`,ns.taxon_id \
                     FROM transcript t, pathway p, externalnasequence ns \
                        WHERE p.url REGEXP t.KO_ID \
                          AND p.taxon_id = ns.taxon_id \
                             AND t.na_sequence_id = ns.na_sequence_id \
                                AND ns.na_sequence_id = " + str(na_sequence_id)


    elif id == 21: #for ortholog
        sql = "SELECT pi.cluster_id, pi.gene_id \
                    FROM geneinstance gi, protein_cluster pi \
                        WHERE gi.na_feature_id = " + str(na_sequence_id) + \
                           " AND gi.gene_id = pi.gene_id"


    elif id == 25: #for information about CDS
        sql = "SELECT nl.start_min,nl.end_min,nl.is_reversed,nl.na_feature_id \
                     FROM nafeature nf ,nalocation nl \
                        WHERE nf.na_sequence_id = " + str(na_sequence_id) + \
                          " AND nf.name='CDS' \
                             AND nl.na_feature_id=nf.na_feature_id \
                                ORDER BY nl.start_min"


    db = DBUtils.MariaConnection('DOTS')
    print("SQL in _getCommonF:" + str(id) + ": " + sql) 
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)

    features = _createclean2Darry(results)
    jsonret['features'] = features
    jsonret['status'] = len(results)

    return jsonret


######################

def _GetSyntenyDetails(ID, data_id, data_version, scaffold, start_base, end_base):

    #my $id =$_[0];
    #my $data_id=$_[1];
    #my $data_version=$_[2];
    #my $scaffold=$_[3];
    #my $start_base=$_[4];
    #my $end_base=$_[5];


    jsonret = {'status':-1}
    sql = ""
    if ID  == 1: #for information about gene
        sql = "select nf.na_feature_id,nf.name, nl.start_min,nl.end_min,ens.description, \
               ens.taxon_id,ens.source_id,ens.sequence_version,nf.na_sequence_id,nf.string8, ens.name, nf.string13 \
               from externalnasequence ens,nalocation nl,nafeatureimp nf \
               where ens.taxon_id=" + str(data_id) + \
               " and ens.sequence_version=" + str(data_version) + \
               " and ens.source_id='"+str(scaffold) + "'" + \
               " and nf.subclass_view not like '%CDS%'"    + \
               " and nf.subclass_view not like '%GeneFeature%'"+ \
               " and nf.subclass_view not like '%exonfeature%'"+ \
               " and nf.subclass_view not like '%REPEAT%'"+ \
               " and nf.na_sequence_id=ens.na_sequence_id"+ \
               " and nl.na_feature_id=nf.na_feature_id" + \
               " and ((nl.start_min between " + str(start_base) + " and " + str(end_base) + ") or (nl.end_min between "+str(start_base) + " and " + str(end_base) + ") or (" + str(end_base) +" between nl.start_min and nl.end_min))" + \
               " order by nl.start_min"


    print("SQL in GetSyntenyDetails: "+sql)
    db = DBUtils.MariaConnection('DOTS')
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)
    print("RESULTS LEN:{}".format(len(results)))
    
    
    #while ( my @arry = $sth->fetchrow_array()) {
    #       my @temp;
    #       foreach my $line (@arry) {
    #               if ( defined  $line ) {
    #                       push @temp, $line;
    #               } else {
    #                       push @temp, -1;   # set to -1 when any element is missing         
    #               }
    #       }
    #       push @features, [ @temp ];
    #}
    #return @features;
    

    features = _createclean2Darry(results)
    jsonret['features'] = features
    jsonret['status'] = len(results)

    return jsonret

######################



def _getfeatures(organism, scaffold, version, startbase, stopbase):
    jsonret = {'status':-1}
    db = DBUtils.MariaConnection('DOTS')
    '''
    my $qryExonPlot="SELECT nl.na_location_id, nl.start_min, nl.end_min, nl.is_reversed, nl.loc_order, tran.na_feature_id, en.length, tran.string4, en.na_sequence_id, nl.is_excluded,tran.review_status_ID
    FROM externalnasequence en, nalocation nl, nafeatureimp tran
    WHERE en.taxon_id =$organism
    AND en.sequence_version =$version
    and en.source_ID='$scaffold'
    AND en.na_sequence_id = tran.na_sequence_id
    AND nl.na_feature_id = tran.na_feature_id
    and ((nl.start_min between $startbase and $stopbase) or (nl.end_min between $startbase and $stopbase) or ($stopbase between nl.start_min and nl.end_min))
    AND tran.name =  'gene'
    ORDER BY nl.start_min";
    '''
    qryExonPlot = "SELECT nl.na_location_id, nl.start_min, nl.end_min, nl.is_reversed, nl.loc_order, tran.na_feature_id, en.length, tran.string4, en.na_sequence_id, nl.is_excluded,tran.review_status_ID FROM externalnasequence en, nalocation nl, nafeatureimp tran " \
        + " WHERE en.taxon_id = " + str(organism) \
        + " AND en.sequence_version =" + str(version) \
        + " and en.source_ID='" + str(scaffold) + "'"\
        + " AND en.na_sequence_id = tran.na_sequence_id AND nl.na_feature_id = tran.na_feature_id " \
        + " and ((nl.start_min between " + str(startbase) + " and " + str (stopbase) + ")" \
        + " or (nl.end_min between " + str(startbase) + " and " + str(stopbase) +")" \
        + " or (" + str(stopbase) + " between nl.start_min and nl.end_min))" \
        + " AND tran.name =  'gene'" \
        + " ORDER BY nl.start_min"
    print("SQL in getfeatures: " + qryExonPlot)
    results = DBUtils.MariaGetData(db, qryExonPlot)
    DBUtils.MariaClose(db)

    '''
    undef @ features;
    while (my @ arry = $sth->fetchrow_array())
        my @ temp;

        foreach my $line( @ arry)
            if (defined  $line)
                push @ temp, $line;
            else
                push @ temp, -1;  # set to -1 when any element is missing
        push @ features, [ @ temp];
    '''
    features = _createclean2Darry(results)

    jsonret['features'] = features
    jsonret['status'] = 4
    return jsonret


def _getScaffold(organism, scaffold, version):
    jsonret = {'status':-1}
    '''
    my $qryExonPlot = "select sequence ,na_sequence_id
        from externalnasequence where
        taxon_id =$organism
        and source_id = '$scaffold'
        and sequence_type_id = 1
        and sequence_version = '$version'";
    my $sth = $dbh->prepare($qryExonPlot);
    $sth->execute | | die "error in executing query";
    '''
    db = DBUtils.MariaConnection('DOTS')
    qryExonPlot = "select sequence ,na_sequence_id from externalnasequence where " \
                " taxon_id = " + str(organism) + \
                " and source_id = '" + str(scaffold) + "'" + \
                " and sequence_type_id = 1" +\
                " and sequence_version = '" + str(version) + "'"
    results = DBUtils.MariaGetData(db, qryExonPlot)
    DBUtils.MariaClose(db)

    '''
    undef @ features;
    while (my @ arry = $sth->fetchrow_array())
        my @ temp;
        foreach my $line( @ arry)
            if (defined  $line)
                push @ temp, $line;
            else
                push @ temp, -1;  # set to -1 when any element is missing         
    
        push @ features, [ @ temp];

    return @features;
    '''
    features = _createclean2Darry(results)
    jsonret['features'] = features
    jsonret['status'] = 5
    return jsonret

# Not called from anywhere
def getnewfeatures():
    #NOT CALLED
    return None

# Not called from anywhere
def get_exon_info():
    #NOT CALLED
    return None


def _trp_info(id, organism, scaffold, version):
    jsonret = {'status': -1}
    '''

    my $dbh = DBI->connect($Defaults::db_ConnString1,$Defaults::db_UserName, $Defaults::db_Password, { RaiseError => 1, AutoCommit => 0}) || die "Error connecting to server";
            my $sql;
            if($id==1)
            {
    '''
    db = DBUtils.MariaConnection('DOTS')
    sql = "select nl.na_location_id,nl.start_min,nl.end_min,nl.is_reversed,nl.loc_order,nf.na_feature_id,"+\
          " en.length,en.na_sequence_id,nl.is_excluded,nf.subclass_view,en.taxon_id,nf.string18"+\
          " from externalnasequence en,nalocation nl ,nafeatureimp nf"+\
          " where en.source_ID='" + str(scaffold)+ \
          "' and en.taxon_id =" + str(organism)+\
          " and en.sequence_version="+str(version)+\
          " and nf.na_sequence_id=en.na_sequence_id"+\
          " and( nf.subclass_view like '%tRNA%'"+\
          " or nf.subclass_view like '%REPEAT%'"+\
          " or nf.subclass_view like '%promoter%' "+\
          " or nf.subclass_view like '%Transposon%')" +\
          " and nl.na_feature_id =nf.na_feature_id"+\
          " order by nl.start_min"
    print("SQL in trp_info: "+sql)
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)
    '''       
    #print "$sql\n";
        $dbh->{'LongReadLen'} = $Defaults::db_MaxFetchSize;
        $dbh->{'LongTruncOk'} = $Defaults::db_TruncateOnLong;

        my $sth = $dbh->prepare($sql);

        $sth->execute || die "error in executing query";
        undef %trp1;
        while ( my @arry = $sth->fetchrow_array())
        {
                my @temp;

                foreach my $line (@arry)
                {
                        if ( defined  $line )
                        {
                                push @temp, $line;
                        }
                        else
                        {
                                push @temp, -1;   # set to -1 when any element is missing
                        }
                }
                #print "$temp[5] <br>";
                push @features, [ @temp ];

                push(@{$trp1{$temp[9]}},[ @temp ]);


        }
        $sth->finish;
        $dbh->disconnect;
        return %trp1;
    '''

    ########## TODO : results to be accumulated into an array for tRNA, repeat etc.
    features = _createclean2Darry(results)
    trpl = {}

    for temp in features:
        # Adds temp array to the key 'temp[9]' in dict trpl
        if trpl.get(str(temp[9])) is None:
            trpl[str(temp[9])] = []
        trpl[str(temp[9])].append(temp)
    jsonret['trpl'] = trpl
    jsonret['status'] = 6
    return jsonret


def _get_synteny_info(id, na_sequence_id, taxon, startbase, stopbase):
    jsonret = {'status': -1}
    '''
    my $dbh = DBI->connect($Defaults::db_ConnString1,$Defaults::db_UserName, 
              $Defaults::db_Password, { RaiseError => 1, AutoCommit => 0}) || die "Error connecting to server";
    
    
    '''
    db = DBUtils.MariaConnection('DOTS')
    '''
    "SELECT org.species, sa.query_start, sa.query_end, sa.is_reversed, sa.target_na_sequence_id, sa.query_taxon_id, sa.target_taxon_id, ena.source_id, sa.q_version,org.strain,sa.target_start,sa.target_end,sa.score,sa.evalue FROM externalnasequence ena, samalignment sa,oomycetes_cgl_sres.organism org WHERE sa.target_na_sequence_id =$na_sequence_id and sa.query_taxon_id !=$taxon AND sa.query_na_sequence_id = ena.na_sequence_id and org.taxon_id=sa.query_taxon_id and org.version=ena.sequence_version
     and ((sa.target_start between $startbase and $stopbase) or (sa.target_end between $startbase and $stopbase) or 
     ($stopbase between sa.target_start and sa.target_end)) ORDER BY sa.target_start"
    '''
    sql = "SELECT org.species, sa.query_start, sa.query_end, sa.is_reversed, sa.target_na_sequence_id, " + \
          " sa.query_taxon_id, sa.target_taxon_id, ena.source_id, sa.q_version,org.strain,sa.target_start," + \
          " sa.target_end,sa.score,sa.evalue " + \
          " FROM externalnasequence ena, samalignment sa," + \
          " oomycetes_cgl_sres.organism org WHERE " + \
          " sa.target_na_sequence_id =" + str(na_sequence_id) + " and " + \
          " sa.query_taxon_id != " + str(taxon) + " AND " + \
          " sa.query_na_sequence_id = ena.na_sequence_id " + \
          " and org.taxon_id=sa.query_taxon_id " + \
          " and org.version=ena.sequence_version " + \
          " and ((sa.target_start between "+str(startbase)+" and " + str(stopbase)+")" + \
          " or (sa.target_end between "+str(startbase)+" and " + str(stopbase)+")" + \
          " or (" + str(stopbase) + " between sa.target_start and sa.target_end)) ORDER BY sa.target_start"
    print("SQL in get_synteny_info:" + sql)

    #TODO: commented next line only for testing
    #results = [[1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10]]
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)

    features = _createclean2Darry(results)

    # push( @ {$synteny{$temp[5]}->{$temp[7]}}, [ @ temp]);
    synteny = {}

    for temp in features:
        # Adds temp array to dict synenty, (to represent sparse 2D array)
        #synteny[str(temp[5])+"_"+str(temp[7])] = temp
        if synteny.get(temp[5]) is None:
            synteny[temp[5]] = []
        synteny[temp[5]].append({str(temp[7]): temp})
    jsonret['synteny'] = synteny
    jsonret['status'] = 8
    return jsonret


def _get_est(id, na_sequence_id):
    # oomycetes_cgl_dots
    jsonret = {'status': -1}

    features = []
    synenty = {}

    if id == 1:
        db = DBUtils.MariaConnection('DOTS')
        sql_query = "select distinct ena.name, ba.number_of_spans, ba.target_start, " \
                    "ba.is_reversed, ba.blat_alignment_quality_id, ba.blocksizes," \
                    "ba.tstarts,ena.sequence,ba.query_taxon_id,ena.sequence_version," \
                    "ba.target_taxon_id,org.species from externalnasequence ena, " \
                    "blatalignment ba,oomycetes_cgl_sres.organism org where ba.target_na_sequence_id="
        sql_query = sql_query + str(na_sequence_id) + " and ba.query_na_sequence_id=ena.na_sequence_id " \
                                      "and org.taxon_id=ba.query_taxon_id " \
                                      "order by ba.target_start"
        #   TODO: replace "1" by str(na_sequence_id) in prev line
        print("SQL in get_est: " + sql_query)
        est_list = DBUtils.MariaGetData(db, sql_query)
        DBUtils.MariaClose(db)

        #while (my @ arry = $sth->fetchrow_array())
        #   my @ temp;
        #   foreach my $line( @ arry)
        #       if (defined  $line)
        #           push @ temp, $line;
        #       else
        #           push @ temp, -1;  # set to -1 when any element is missing
        #   print "$temp[5] <br>";
        #   push @ features, [ @ temp];
        #   push( @ {$synteny{$temp[8]}}, [ @ temp]);
        features = _createclean2Darry(est_list)
        for temp in features:
            # Adds temp array to the key 'temp[8]' in dict synenty
            synenty[str(temp[8])] = temp

        #jsonret['est_list'] = est_list
        jsonret['synenty'] = synenty
        jsonret['status'] = 10
        return jsonret
    return jsonret

##########################################
# start drawing functions
#
def _TPRTrack(startbase, stopbase, organism, version, exons_r, otherlink, contig_count):

    # drawing function
    trp = exons_r
    init_track = 135
    gap = 30

    color = 'blue'
    j = 1
    TRPTracks = {}
    TRPTracks['tracks'] = []
    TRPTracks['contig_count'] = contig_count

    # Start of main for loop
    for key in trp:
        leftstring = key
        if leftstring == 'tRNA':
            color = 'pink'
        elif leftstring == 'PROMOTOR':
            color = 'maroon'
        elif leftstring == 'REPEAT':
            color = 'khaki'

        one_track = {'label': leftstring}
        one_track['color'] = color

        arr_items = trp[key]
        arr_rects = []
        horzlevelCoding = init_track + j * gap

        # Start of inner loop
        for one_item in arr_items:

            if valid_exon_ends(one_item[1], one_item[2]) == False:
                continue
            feature = {'l': one_item[1], 'r': one_item[2], 'h': horzlevelCoding, 'id': one_item[5], 'color': color}
            feature['link'] = Defaults.GetQualifiedLinkJSON('promo', START=one_item[7], LEN=one_item[8],
                                                         VERSION=version, COLLAPSE=0, FEATURE_ID=one_item[5])
            feature['link']['organism'] = organism
            feature['name'] = leftstring
            if one_item[3] == 1:
                feature['arrow'] = 'l'
            else:
                feature['arrow'] = 'r'
            arr_rects.append(feature)
        # end of inner loop


        one_track['Rects'] = arr_rects
        TRPTracks['tracks'].append(one_track)
        j = j + 1
    # end of main for loop

    return TRPTracks



# These are drawing functions
def _SyntenyTracks(startbase, stopbase, exons_r, detail_Link, scaffold, track_pos):
    SyntenyTracks = {'label-heading': 'LASTZ alignment'}
    SyntenyTracks['tracks'] = []
    SyntenyTracks['contig_count'] = 999

    TrackColorMap = {100:'red',
                     90: 'violet',
                     80: 'aqua',
                     70: 'black',
                     60: 'Lime'}

    horzlevelCoding = 0
    rowht_1 = 5
    synteny1 = exons_r
    i = 1

    #for my $taxon(keys % synteny1)
    #{
    for taxon in synteny1:
        # taxon is "4781" or similar
        #for my $scaffold(keys % {$synteny1{$taxon}})
        #{
        arr_scaffolds = synteny1[taxon]
        any_scaffold_key = list(arr_scaffolds[0].keys())[0]
        any_scaffold = arr_scaffolds[0][any_scaffold_key]
        one_track = {'label': any_scaffold[0] + " " + any_scaffold[9]}
        one_track['Rects'] = []

        for scaffold_dict in arr_scaffolds:
            scaffold_key = list(scaffold_dict.keys())[0]
            scaffold = scaffold_dict[scaffold_key]
            #print(scaffold)
            # scaffold has a value like this
            '''
            scaffold = ['Pythium aphanidermatum',  //index 0
                             56738,                //index 1  - start location
                             58683,                //index 2  - end location
                             0,
                             1,
                             1223555,              //index 5  - organism No
                             890382,               //index 6
                             'Scaffold_125',        
                             1.0,                  //index 8 - version
                             'DAOMBR4440',         //index 9
                             30838,                //index 10 - start pos
                             32486,                //index 11 - end pos
                             60,                   //index 12
                             '1'
                        ]
            '''
            scaffold_rect = {}

            #my @ pos = @ {$synteny1{$taxon}{$scaffold}};


            '''
            # main drawing part start
            base_start;
            my $synteny_gap=24;

            if ($track_pos == 0)
                $base_start=140;
            elsif($track_pos == 1)
                $base_start=180;
            elsif($track_pos == 2)
                $base_start=220;
            elsif($track_pos == 3)
                $base_start=250;
            else
                $base_start=280;
            '''
            base_start = 0
            synteny_gap = 24
            if track_pos == 0:
                base_start=140
            elif track_pos == 1:
                base_start=180
            elif track_pos == 2:
                base_start=220
            elif track_pos == 3:
                base_start=250
            else:
                base_start=280


            count = len(arr_scaffolds)
            track_color = ''

            #for my $k ( 0..$  # pos)
            #{
            '''
                # print "hi $pos[$k][3] ";
                if ( defined  $pos[$k][10] & & defined  $pos[$k][11])
                {
                    if ($pos[$k][12] == 100 )
                        $track_color=$red;
                    elsif($pos[$k][12] == 90 )
                        $track_color=$violet;
                    elsif($pos[$k][12] == 80 )
                        $track_color=$aqua;
                    elsif($pos[$k][12] == 70 )
                        $track_color=$black;
                    elsif($pos[$k][12] == 60 )
                        $track_color=$Lime;
                }
            '''
            dict_color = TrackColorMap.get(scaffold[12])
            if dict_color is not None:
                track_color = dict_color

            '''
                if ( $pos[$k][11] < 0 | | $pos[$k][10] < 0 )  # skipping cases where the start or end of an exon is missing.
                    next;
                @ temp = & getStartBaseEndBase($start_base, $end_base, $pos[$k][10], $pos[$k][11]);
                if ($temp[0][0] == -1)
                    next;
                else
                {
                    $pos[$k][10] = $temp[0][0];
                    $pos[$k][11] = $temp[0][1];
                }
                if ( $pos[$k][11] > $pos[$k][10] )
                {
                    $start_min=$leftedge+ ($pos[$k][10] -  $start_base) * $fraction;
                    $end_min=$leftedge+ ($pos[$k][11] -$start_base) * $fraction;

                    $image->filledRectangle($start_min, $horzlevelCoding, $end_min, $horzlevelCoding + $rowht_1, $track_color);
                    $coordstring = join(",", $start_min, $horzlevelCoding, $end_min, $horzlevelCoding + $rowht_1);

                    & printMapping($coordstring, "$pos[$k][0]:$scaffold:$pos[$k][1]-$pos[$k][2]", $pos[$k][8], $pos[$k][5], $pos[$k][8], $detail_Link, $pos[$k][1], $pos[$k][2]-$pos[$k][1], $pos[$k][7]);

                }
            '''
            if valid_exon_ends(scaffold[10], scaffold[11]) == False:
                continue
            scaffold_rect['l'] = scaffold[10]
            scaffold_rect['r'] = scaffold[11]
            scaffold_rect['h'] = horzlevelCoding
            scaffold_rect['color'] = track_color
            # "$pos[$k][0]:$scaffold:$pos[$k][1]-$pos[$k][2]"
            scaffold_rect['name'] = scaffold[0] + ":" + scaffold_key + ":" + \
                                     str(scaffold[1]) + "-" + str(scaffold[2])
            scaffold_rect['link'] = Defaults.GetQualifiedLinkJSON('syntenylink', \
                        START = scaffold[1], LEN = scaffold[2] - scaffold[1], \
                        ORGANISM_NO = scaffold[5], VERSION = scaffold[8], SCAFFOLD = scaffold[7], \
                        COLLAPSE = 0)
            scaffold_rect['id'] = scaffold[1]   # NOTE: Start position is used as ID

            #} //end of for my $k ( 0..$  # pos)

            '''
            my $poly = new GD::Polygon;
            if ($pos[$k][3] == 1)
            {
                $poly->addPt( $leftedge + ( $pos[$k][10] - $start_base ) * $fraction, $horzlevelCoding );
                $poly->addPt( $leftedge + ( $pos[$k][10] - $start_base ) * $fraction, $horzlevelCoding + $rowht_1 );
                $poly->addPt( $leftedge + ( $pos[$k][10] - $start_base ) * $fraction - 3, $horzlevelCoding + $rowht_1 / 2 );
                $image->filledPolygon( $poly, $track_color );
            }
            else
            {
                $poly->addPt( $leftedge + ( $pos[$k][11] - $start_base ) * $fraction, $horzlevelCoding );
                $poly->addPt( $leftedge + ( $pos[$k][11] - $start_base ) * $fraction, $horzlevelCoding + $rowht_1 );
                $poly->addPt( $leftedge + ( $pos[$k][11] - $start_base ) * $fraction + 3, $horzlevelCoding + $rowht_1 / 2 );
                $image->filledPolygon( $poly, $track_color );

            }
            '''
            if scaffold[3] == 1:
                scaffold_rect['arrow'] = 'l'
            else:
                scaffold_rect['arrow'] = 'r'
            # main drawing part end

            one_track['Rects'].append(scaffold_rect)

        # endof of for scaffold_key in arr_scaffolds
        SyntenyTracks['tracks'].append(one_track)

        i += 1
    #end of for taxon in synteny1:
    #}

    return SyntenyTracks




def _EstTracks(startbase, stopbase, est_val, estlink, field1, contig_count, synteny_end):
    #field1 unused
    #synteny_end unused
    horzlevelContigs = 0
    currHorzlevelContigs =0

    currfeatureID = 0
    prevfeatureID = 0
    prevEndexon = 0
    prevEndTstarts = 0
    newContig = 0

    visiblelb = startbase
    visiblerb = stopbase
    track_pos = contig_count

    syntenyend = synteny_end + 25
    gap = 30
    synteny1 = est_val
    estTracks = {'label-heading': "BLAT alignment to unigenes",
                 'contig_count': contig_count}
    estTracks['tracks'] = []

    i = 1

    for taxon in synteny1:
        pos = synteny1[taxon]
        trackname = pos[11]
        currHorzlevelContigs = 0
        one_track = {'label': trackname}
        one_track['Rects'] = []

        if pos[5] is None or pos[6] is None:
            continue

        # split into multiple rects
        blocksizes = pos[5].split(",")
        tstarts = pos[6].split(",")
        #print("DBG[ESTTracks]: tstarts:" + pos[6] + " blocksizes:"+pos[5])
        newContig = 1
        global contigsColorForQuality
        contigsColor = Defaults.contigsColorForQuality[pos[4]]['color']

        # start of for value in tstarts:
        for j in range(len(tstarts)):
            #print("DBG[ESTTracks]:[" + str(j) + "] start_pos:" + tstarts[j] + " block_size:"+blocksizes[j])

            if tstarts[j] is None or len(tstarts[j]) == 0:
                continue
            if blocksizes[j] is None or len(blocksizes[j]) == 0:
                continue

            start_pos = int(tstarts[j])
            block_size = int(blocksizes[j])

            # not a new contig so make the connection bar
            '''
            if ($newContig == 0)  # not a new contig so make the connection bar
            {
                $image->filledRectangle($leftedge + (
                        $prevEndTstarts-$visiblelb) *$fraction, $currHorzlevelContigs + ($rowht / 2) - (
                        $connectionBarHt / 2), $leftedge + (
                        $temp[0][0]-$visiblelb) *$fraction, $currHorzlevelContigs + ($rowht / 2) + (
                        $connectionBarHt / 2), $contigsColor);
            }
            else
            {
                if ($temp[0][0] < $prevEndTstarts)  # if there is an overlap between the new contig and the old contig 
                    # $currHorzlevelContigs = $currHorzlevelContigs + $rowht + 5;   # then push the horz level of the new contig a little down
                else
                    $currHorzlevelContigs = $horzlevelContigs;  # else set the horz level of the new contig as the same level as $horzlevelContigs
            }
            '''
            if newContig == 0:
                global leftedge
                connection_bar_rect = {'l': prevEndTstarts,
                                        'r': start_pos,
                                        'color': contigsColor}
                one_track['connection_bar'] = connection_bar_rect
            else:
                if start_pos >= prevEndTstarts:
                    currHorzlevelContigs = horzlevelContigs

            #$currHorzlevelContigs = $horzlevelContigs;
            currHorzlevelContigs = horzlevelContigs

            # make the inividual elements of a contig
            '''
            $image->filledRectangle($leftedge + (
                        $temp[0][0] - $visiblelb) * $fraction, $currHorzlevelContigs, $leftedge + (
                        $temp[0][1] - $visiblelb) * $fraction, $currHorzlevelContigs + $rowht, $contigsColor);
                    $coordstring = join(",",$leftedge + (
                        $temp[0][0] - $visiblelb) * $fraction, $currHorzlevelContigs, $leftedge + (
                        $temp[0][1] - $visiblelb) * $fraction,  $currHorzlevelContigs + $rowht);
                    # print  "coordinate string is : $coordstring <br>";
                    & printMapping($coordstring,$pos[0][0],$pos[0][0],$pos[0][8],$pos[0][9],$detail_Link,$pos[0][8]);
            '''

            pos_rect = {'l': start_pos,
                        'r': start_pos + block_size,
                        'color': contigsColor}
            pos_rect['link'] = Defaults.GetQualifiedLinkJSON('estlink', \
                                    START = pos[8], ORGANISM_NO = pos[8], VERSION = pos[9], \
                                    COLLAPSE = 0, FEATURE_ID = pos[0])
            pos_rect['id'] = pos[2]
            pos_rect['name'] = pos[0]

            # draw triangle:to indicate reversed or not
            '''
            my $poly = new GD::Polygon;
            if ($pos[0][3] == 1)  # is_reversed = 1
            {
                $poly->addPt( $leftedge + ($temp[0][0] - $visiblelb) * $fraction, $currHorzlevelContigs );
                $poly->addPt( $leftedge + ($temp[0][0] - $visiblelb) * $fraction, $currHorzlevelContigs + $rowht );
                $poly->addPt( $leftedge + (
                $temp[0][0] - $visiblelb) * $fraction - 3, $currHorzlevelContigs + $rowht / 2 );
                $image->filledPolygon( $poly, $contigsColor );
            }
            else
            {
                $poly->addPt( $leftedge + ($temp[0][1] - $visiblelb) * $fraction, $currHorzlevelContigs );
                $poly->addPt( $leftedge + ($temp[0][1] - $visiblelb) * $fraction, $currHorzlevelContigs + $rowht );
                $poly->addPt( $leftedge + (
                $temp[0][1] - $visiblelb) * $fraction + 3, $currHorzlevelContigs + $rowht / 2 );
                $image->filledPolygon( $poly, $contigsColor );
            }
            '''
            if pos[3] == 1:
                pos_rect['arrow'] = 'r'
            else:
                pos_rect['arrow'] = 'l'

            one_track['Rects'].append(pos_rect)


            #$prevEndTstarts = $temp[0][1];
            #$newContig = 0;
            prevEndTstarts = start_pos + block_size
            newContig = 0

        # end of for j in range(len(tstarts))

        estTracks['tracks'].append(one_track)
        i = i + 1
    # end of for taxon in synteny1


    return estTracks




def gff_track():
    #NOT CALLED
    return None

def display_string1(str_ref, loc_ref, utr_ref):
    #TODO - from web_utility.pm
    return str_ref

def display_string_arijit1(str_ref, loc_ref, utr_ref, p1, p2):
    #TODO - from web_utility.pm
    return str_ref

def display_string_cds(str_ref, loc_ref, utr_ref, p1, p2):
    #TODO - from web_utility.pm
    return str_ref

# called from scaffoldPosLinkUI, for gene coding- links to scaffold postion boxes
# function copied from sequence1.cgi
# /cgi-bin/eumicrobedb/sequence1.cgi?ID=$FORM{'ID'}&organism=$FORM{'organism'}&version=$FORM{'version'}
#              &gene_id=$info1[0][0]&gene_desc=$info1[0][7]&scaffold=$info1[0][9]
def _get_plot_gene_link(ID, organism, version, gene_id, gene_desc, scaffold):
    json_ret = {}
    #my @seq =       &GetCommonFeatures(1,$FORM{'ID'},$FORM{'organism'});
    seq = _getCommonFeatures(1,ID,organism)['features']
    #@feature = &GetCommonFeatures(22, $FORM{'ID'},$FORM{'organism'});    #for information about exons
    feature = _getCommonFeatures(22, ID, organism)['features']
    #my @CDS = &GetCommonFeatures(25, $FORM{'ID'}, $FORM{'organism'});
    CDS = _getCommonFeatures(25, ID, organism)['features']
    #my $rows      = scalar(@feature); # This returns the number of rows the first query returns
    rows = len(feature)
    #my @protein   = &GetCommonFeatures(13,$FORM{'ID'},$FORM{'organism'}); # returns protein sequence    
    protein   = _getCommonFeatures(13, ID, organism)['features']
    #my @utr =&GetCommonFeatures(14,$FORM{'gene_id'},$FORM{'organism'}); # returns UTR
    utr = _getCommonFeatures(14, gene_id, organism)['features']

    #print "<tr><td><b>Scaffold :</b> $seq[0][8]</td></tr>";
    #print "<tr><td><b>Gene_id  :</b> $seq[0][3]</td></tr>";
    #print "<tr><td><b>Description :</b> $FORM{'gene_desc'}</td></tr>";
    json_ret['Scaffold'] = seq[0][8]
    json_ret['Gene_id'] = seq[0][3]
    json_ret['Description'] = gene_desc
    
    #my $out = &display_string1($seq[0][6],\@feature,\@utr);
    #my $out1= &display_string_arijit1($seq[0][6], \@CDS, \@utr, $seq[0][5],$seq[0][1]);
    #my $out_cds = &display_string_cds($seq[0][6], \@CDS, \@utr, $seq[0][5],$seq[0][1]);
    out = display_string1(seq[0][6],feature,utr)
    out1= display_string_arijit1(seq[0][6], CDS, utr, seq[0][5], seq[0][1])
    out_cds = display_string_cds(seq[0][6], CDS, utr, seq[0][5], seq[0][1])
    
    #my $seqLen = length($seq[0][6]);
    seqLen = len(seq[0][6])
    #&usrheader("Predicted Gene Model: $seqLen bases (green marked regions are exons, white marked are introns)","F0F8FF","0");
    #print "<tr><td><pre>$out</pre></td></tr>";
    json_ret['PredGene_len'] = seqLen
    json_ret['PredGene'] = out

    #my $cds_len=length($out_cds);
    cds_len = len(out_cds)
    #&usrheader("Predicted CDS: Length $cds_len","F0F8FF","0");
    json_ret['CDS_len'] = cds_len
    json_ret['CDS'] = out_cds

    #my $len=length($out1);
    out1_len = len(out1)
    #&usrheader("Protein Sequence: Length $len","F0F8FF","0");
    json_ret['ProteinSeq_len'] = out1_len
    json_ret['ProteinSeq'] = out1

    return json_ret

# called from sequenceDetailUI, for gene coding
def _plot_gene(gene_coordref):

    gene_coord = gene_coordref
    
    json_ret = {}
    json_ret['strand'] = "(-)"
    if gene_coord[0][3] == 0:
        json_ret['strand'] = "(+)"

    # my $exon= scalar(@gene_coord);
    # This will have the total length of gene(exon + intron)
    # my $gene_length = $gene_coord[$exon-1][2] - $gene_coord[0][1];
    exon = len(gene_coord)
    gene_length = gene_coord[exon - 1][2] - gene_coord[0][1]

     
    xbegin = 0
    json_ret['rect'] = []
    json_ret['lines'] = []
    print("\n\nI AM HERE=====%s", exon)
    #for(my $i=0;$i<$exon;$i++){
    for i in range(exon):
        #my $diff=$gene_coord[$i][2] - $gene_coord[$i][1];
        #$diff *= $fraction;  # Here get the proportionate value
        diff = gene_coord[i][2] - gene_coord[i][1]
        
        #$image->string(gdSmallFont,$xbegin,($ybegin-30),$gene_coord[$i][1],$red); # Start position of exon on scaffold
        vert_l_top_label = str(gene_coord[i][1])
        #$image->string(gdSmallFont,($xbegin),($ybegin-20),"|",$red);
        #$image->string(gdSmallFont,($xbegin),($ybegin-10),"|",$red);
        #$image->string(gdSmallFont,($xbegin),($ybegin+10),"|",$red);
        #$image->string(gdSmallFont,($xbegin),($ybegin+20),"|",$red);
        vert_l_coord = xbegin
        #$image->string(gdSmallFont,($xbegin),($ybegin+30),($gene_coord[$i][1]-$gene_coord[0][1]),$red);
        vert_l_bot_label = str(gene_coord[i][1]-gene_coord[0][1])
        #$image->filledRectangle($xbegin,$ybegin,($xbegin+$diff),($ybegin+$offset),$purple);
        rect_l = xbegin
        rect_r = xbegin + diff
        #$image->string(gdSmallFont,($xbegin+$diff-(length($gene_coord[$i][2])*5)),($ybegin-20),$gene_coord[$i][2],$blue); #End position of exon in scaffold
        vert_r_top_label = str(gene_coord[i][2])
        #$image->string(gdSmallFont,($xbegin+$diff-(length(($gene_coord[$i][2]-$gene_coord[$i][1]))*5)),($ybegin+20),($gene_coord[$i][2]-$gene_coord[0][1]),$blue); #End position of exon in scaffold
        vert_r_bot_label = str(gene_coord[i][2] - gene_coord[0][1])
        #$image->string(gdSmallFont,($xbegin+$diff),($ybegin-10),"|",$blue);
        #$image->string(gdSmallFont,($xbegin+$diff),($ybegin+10),"|",$blue);
        vert_r_coord = xbegin + diff
         
        one_box = {'vert_l_top_label':vert_l_top_label,
                   'vert_l_bot_label':vert_l_bot_label,
                   'vert_l_coord': vert_l_coord,
                   'rect_l': rect_l,
                   'rect_r': rect_r,
                   'vert_r_top_label': vert_r_top_label,
                   'vert_r_bot_label': vert_r_bot_label,
                   'vert_r_coord': vert_r_coord
                  }
        print("\n\n=====================ONE BOX======================{}\n".format(one_box))
        json_ret['rect'].append(one_box)

        #$xbegin += $diff;
        xbegin = xbegin + diff
        
        # This is the line joining the exons
        #if($gene_coord[$i+1][1])
        if i < exon-1:
            if gene_coord[i+1][1] != 0:
            #{
            
                #my $diff1=$gene_coord[$i+1][1] - $gene_coord[$i][2];
                #$diff1 *= $fraction;
                diff1 = gene_coord[i+1][1] - gene_coord[i][2]
                #$image->line(($xbegin),($ybegin+8),($xbegin+$diff1),($ybegin+8),$orange);
                horz_l_coord_l = xbegin
                horz_l_coord_r = xbegin + diff1
                #$xbegin += $diff1;
                xbegin = xbegin + diff1
                
                one_line = {'l': horz_l_coord_l, 'r': horz_l_coord_r}
                json_ret['lines'].append(one_line)
            
            #}
    #}
        
    return json_ret

# called from _get_HMMSMART_data
def plot_domain(domain, name, prot_len, id): 

    json_ret = {'name': name}
    json_ret['rects'] = []
    json_ret['texts'] = []
    json_ret['lines'] = []
    ## This is to stop proceeding to next stages if scalar(@domain) is 0
    if len(domain) == 0:
        return

    # This marks the beginning and end of the plot
    xbegin = 75 # Image begin x coordinate
    xend   = 400 # Image end X coordinate
    ybegin = 40  # y-axis beginning
    offset = 15  # This is the width of the bar

    # This will have the number of domains the protein has
    prot_dom = len(domain)

    # This will have the total length of gene(exon + intron)
    #fraction    = (xend - xbegin)/prot_len

    # Now draw the gene coordinates
    # Draw line first  
    #diff2 = fraction * domain[0][0];
    diff2 = domain[0][0];

    #$image->filledRectangle($xbegin,($ybegin+7),($xbegin+$diff2),($ybegin+10),$orange);
    one_rect = {'l': xbegin, 't': ybegin+7, 'r': xbegin + diff2, 'b': ybegin+10, 'color': "orange"}
    json_ret['rects'].append(one_rect)
    
    xbegin = xbegin + diff2;


    for i in range(prot_dom):
        diff=domain[i][1] - domain[i][0]

        # This plots the length difference
        #$image->string(gdSmallFont,($xbegin+3),($ybegin+15),$diff,$black);
        one_str = {'label': str(diff), 'l': xbegin+3, 't': ybegin+15, 'col':'black'}
        json_ret['texts'].append(one_str)

        # Start position of exon on scaffold
        #$image->string(gdSmallFont,$xbegin,($ybegin-20),$domain[$i][0],$blue); 
        one_str = {'label': str(domain[i][0]), 'l': xbegin, 't': ybegin-20, 'col':'blue'}
        json_ret['texts'].append(one_str)
        #$image->string(gdSmallFont,($xbegin),($ybegin-10),"|",$blue);
        one_rect = {'l': xbegin, 't': ybegin-10, 'r': xbegin, 'b': ybegin, 'color': "blue"}
        json_ret['rects'].append(one_rect)

        # Draw the exon on scaffold
        #$image->filledRectangle($xbegin,$ybegin,($xbegin+$diff),($ybegin+$offset),$green);
        one_rect = {'l': xbegin, 't': ybegin, 'r': xbegin+diff, 'b': ybegin+offset, 'color': "green"}
        json_ret['rects'].append(one_rect)

        # End position of exon in scaffold
        #$image->string(gdSmallFont,($xbegin+$diff),($ybegin-20),$domain[$i][1],$blue); 
        one_str = {'label': str(domain[i][1]), 'l': xbegin+diff, 't': ybegin-20, 'col':'blue'}
        json_ret['texts'].append(one_str)
        #$image->string(gdSmallFont,($xbegin+$diff),($ybegin-10),"|",$blue);
        one_rect = {'l': xbegin+diff, 't': ybegin-10, 'r': xbegin+diff, 'b': ybegin, 'color': "blue"}
        json_ret['rects'].append(one_rect)

        xbegin = xbegin + diff;

        # This is the line joining the exons
        #if($domain[$i+1][0]){
        #    my $diff1=$domain[$i+1][0] - $domain[$i][1];
        #    $diff1 *= $fraction;
        #    $image->filledRectangle(($xbegin),($ybegin+7),($xbegin+$diff1),($ybegin+10),$orange);
        #    $xbegin += $diff1;
        #}
        if i+1 < len(domain): #check if i+1 is within bound
            if domain[i+1][0] != 0:
                diff1 = domain[i+1][0] - domain[i][1]
                #$image->filledRectangle(($xbegin),($ybegin+7),($xbegin+$diff1),($ybegin+10),$orange);
                one_rect = {'l': xbegin, 't': ybegin+7, 'r': xbegin+diff1, 'b': ybegin+10, 'color': "orange"}
                json_ret['rects'].append(one_rect)
                xbegin = xbegin + diff1;
    # end of for i in range(prot_dom):

    # last part of the line
    #my $diff3 = $fraction * ($prot_len - $domain[$i][1]);
    diff3 = prot_len - xbegin # end of last domain, updated in var xbegin in the above for loop

    #$image ->filledRectangle($xbegin,($ybegin + 7),($xbegin + $diff3), ($ybegin+10),$orange);
    one_rect = {'l': xbegin, 't': ybegin+7, 'r': xbegin+diff3, 'b': ybegin+10, 'color': "orange"}
    json_ret['rects'].append(one_rect)

    return json_ret



# called from sequenceDetailUI, for gene coding
def _get_loglikehood_data(log_file):
    # has 7 columns [timestamp, series1, series 2, ..., series 6]
    with open(log_file, 'r') as fp:
        lines = fp.readlines()
    ret_array = []
    for line in lines:
        ret_array.append(line.strip().split())   
    return ret_array
    

# called from sequenceDetailUI, for gene coding
def _get_fickett_data(fckt_file):
    # has 3 columns [timestamp, series1, series 2]
    with open(fckt_file, 'r') as fp:
        lines = fp.readlines()
    ret_array = []
    for line in lines:
        ret_array.append(line.strip().split())   
    return ret_array

def get_non_coding_sequence(organism, scaffold, version, start, length):
    #my $StartPosition=$FORM{'StartPosition'};
    #my $len = $FORM{'Length'};
    #my $organism = $FORM{'organism'};
    #my $end_position=$FORM{'StartPosition'}+ $FORM{'Length'};

    retlen=0
    print("get_non_coding_sequence start, len:{0},{1}".format(start, length))
    sql = "select * from externalnasequence where taxon_ID="\
          +str(organism) + " and source_ID='" + str(scaffold) + "' and sequence_type_ID=1 "\
          "and sequence_version='" + str(version) + "'";
    print("SQL in get_non_coding_sequence: "+sql)
    db = DBUtils.MariaConnection('DOTS')
    results = DBUtils.MariaGetData(db, sql)
    DBUtils.MariaClose(db)
    print("RESULTS LEN:{}".format(len(results)))
    
    '''
    while (@row = $sth->fetchrow_array)
    {
        my $req_str = $row[8];
    $org_name=$row[6];
        $req_str1= substr($req_str,$StartPosition,$len);
    }
    '''
    org_name = ""
    req_str  = ""
    for row in results:
        req_str = row[8]
        org_name = row[6]
        req_str1 = req_str[start:start+length]
    print("Got seq len:{}".format(len(req_str)))
    print("Got seq len1:{}".format(len(req_str1)))

    ret_json = {'org_name': org_name,
                'req_str': req_str1,
                'len': len(req_str1)}
    return ret_json

def _get_HMMSMART_data(taxon_id, ID, seq_len, info):
    json_ret = {}
    
    #HMMSmart Prediction
    '''
    $count=@info7;

    &plot_domain(\@info7,"hmmsmart",$len,$id1);

    if($count == 0){
      print "<center><i> *** None *** </i></center>";
    } else{ 
          print "<table align=\"center\"><tr><th width=60%><b>HmmSmart prediction</b></th><th width=20%><b>P-Val</b></th><th><b>prediction_id</b></th></tr>";
          for($i=0;$i<$count;$i++){
              print "<tr>";
              for($j=2;$j <5;$j++){
                 if($j == 4){
                     print "<td><a href=\"http://smart.embl-heidelberg.de/smart/do_annotation.pl?BLAST=DUMMY&ACC=$info7[$i][$j]\">$info7[$i][$j]</a></td>";
            I    } else{
                     print "<td>$info7[$i][$j]</td>";
                 }
              }
              print "</tr>";
           }
           my $hmmimg = $id1."_hmmsmart.png";
           print "<tr>";
           print "<center><img src=\"/images/$hmmimg\"></center>";
           print "</tr></table>";
    }

    '''
    count = len(info)
    if count == 0:
        json_ret['Text'] = "*** None ***"
        return json_ret

    json_ret['Plot'] = plot_domain(info,"HMMSmart",seq_len,ID)

    json_ret['Table_headers'] = ["HmmSmart prediction", "P-val", "prediction_id"]
    json_ret['Table_link_on_col'] = 3 # count 1 based - 3=3rd column
    json_ret['Table_rows'] = []
    for i in range(count):
        one_row = {'vals': [info[i][2], info[i][3], info[i][4]],
                   'link': "http://smart.embl-heidelberg.de/smart/do_annotation.pl?BLAST=DUMMY&ACC=" + info[i][4]}
        json_ret['Table_rows'].append(one_row)

    return json_ret

def _get_GO_data(taxon_id, ID, seq_len, info):
    json_ret = {}

    '''
    $count=@info12;
    if($count == 0){
        print "<center><i> *** None *** </i></center>";
    } else{
        print "<table align=\"center\"><tr><th width=40%><b>Biological Process</b></th><th width=45%><b>GO ID</b></th><th><b>Prediction Method</b></th></tr>";
        for($i=0;$i<$count;$i++){
            print "<tr>";
            print "<td width=\"40%\" align=\"center\">$info12[$i][0]</td>";
            print "<td width=\"15%\" align=\"center\"><a href=\"http://www.ebi.ac.uk/ego/QuickGO?mode=display&entry=$info12[$i][1]\">$info12[$i][1]</a></td>";
            print "<td width=\"10%\" align=\"left\">$info12[$i][2]</td>";
       
      
            print "</tr>";
        }
        print "</td></tr>";
    }
    print "</table>";
    '''

    count = len(info)
    if count == 0:
        json_ret['Text'] = "*** None ***"
        return json_ret

    json_ret['Table_headers'] = ["Biological Process", "GO ID", "Prediction Method"]
    json_ret['Table_link_on_col'] = 2 # count 1 based - 2=2nd column
    json_ret['Table_rows'] = []
    for i in range(count):
        one_row = {'vals': [info[i][0], info[i][1], info[i][2]],
                   'link': "http://smart.embl-heidelberg.de/smart/do_annotation.pl?BLAST=DUMMY&ACC=" + info[i][1]}
        json_ret['Table_rows'].append(one_row)

    return json_ret

def _get_ProfileScan_data(taxon_id, ID, seq_len, info):
    json_ret = {}
    '''
    $count=@info6;
    &plot_domain(\@info6,"profilescan",$len,$id1);
    
    if($count == 0){
        print "<center><i> *** None *** </i></center>";
    } else{
        print "<table align=\"center\"><tr><th width=60%><b>Profile scan prediction</b></th><th width=20%><b>P-Val</b></th><th><b>prediction_id</b></th></tr>";
        for($i=0;$i<$count;$i++){
            print "<tr>";
            for($j=2;$j <5;$j++){
                if($j == 4){
                    print "<td><a href=\"http://prosite.expasy.org/$info6[$i][$j]\">$info6[$i][$j]</a></td>";
                } else{
                    print "<td>$info6[$i][$j]</td>";
                }
            }
            print "</tr>";
        }
        my $profileimg = $id1 ."_profilescan.png";
        print "<tr>";
        print "<center><img src=\"/images/$profileimg\"></center>";
        print "</tr></table>";
    }
    '''
    count = len(info)
    if count == 0:
        json_ret['Text'] = "*** None ***"
        return json_ret

    json_ret['Plot'] = plot_domain(info,"profilescan",seq_len,ID)

    json_ret['Table_headers'] = ["Profile scan prediction", "P-val", "prediction_id"]
    json_ret['Table_link_on_col'] = 3 # count 1 based - 3=3rd column
    json_ret['Table_rows'] = []
    for i in range(count):
        one_row = {'vals': [info[i][2], info[i][3], info[i][4]],
                   'link': "http://prosite.expasy.org/"+ info[i][4]}
        json_ret['Table_rows'].append(one_row)

    return json_ret

def _get_InterPro_data(taxon_id, ID, seq_len, info):
    json_ret = {}
    '''
    $count= @info11;

    if($count == 0){
      print "<center><i> *** None *** </i></center>";
    } else{
        print "<table align=\"center\"><tr><th width=80%><b>Interpro Domain name</b></th><th><b>prediction_id</b></th></tr>";
        for($i=0;$i<($count);$i++){
            print "<tr>";
            for($j=0;$j <2;$j++){
                if($j == 1){
                    print "<td><a href=\"http://www.ebi.ac.uk/interpro/entry/$info11[$i][$j]\">$info11[$i][$j]</a></td>";
                } else{
                    print "<td>$info11[$i][$j]</td>";
                }
            }
            print "</tr>";
       }
       print "</table>";
    }
    '''

    count = len(info)
    if count == 0:
        json_ret['Text'] = "*** None ***"
        return json_ret

    json_ret['Table_headers'] = ["Interpro Domain nameBiological Procese", "prediction_id"]
    json_ret['Table_link_on_col'] = 2 # count 1 based - 2=2nd column
    json_ret['Table_rows'] = []
    for i in range(count):
        one_row = {'vals': [info[i][0], info[i][1]],
                   'link': "http://www.ebi.ac.uk/interpro/entry/"+ info[i][1]}
        json_ret['Table_rows'].append(one_row)

    return json_ret

def _get_FprintScan_data(taxon_id, ID, seq_len, info):
    json_ret = {}
    '''
    $count=@info5;
    &plot_domain(\@info5,"fprintscan",$len,$id1);

    if($count == 0){
        print "<center><i> *** None *** </i></center>";
    } else{
        print "<table align=\"center\"><tr><th width=60%>fprintscan prediction</b></th><th width=20%><b>P-Val</b></th><th><b>prediction_id</b></th></tr>";
        for($i=0;$i<$count;$i++){
            print "<tr>";
            for($j=2;$j <5;$j++){
                if($j == 4){
                     print "<td><a href=\"http://umber.sbs.man.ac.uk/cgi-bin/dbbrowser/PRINTS/DoPRINTS.pl?cmd_a=Display&qua_a=/Type&fun_a=Text&qst_a=$info5[$i][$j]&disp=2\">$info5[$i][$j]</a></td>";
                } else{
                     print "<td>$info5[$i][$j]</td>";
                }
            }
            print "</tr>";
        }
        my $fprintimg = $id1."_fprintscan.png";
        print "<tr>";
        print "<center><img src=\"/images/$fprintimg\"></center>";
        print "</tr></table>";
    }
    '''
    count = len(info)
    if count == 0:
        json_ret['Text'] = "*** None ***"
        return json_ret

    json_ret['Plot'] = plot_domain(info,"fprintscan",seq_len,ID)

    json_ret['Table_headers'] = ["fprintscan prediction", "P-val", "prediction_id"]
    json_ret['Table_link_on_col'] = 3 # count 1 based - 3=3rd column
    json_ret['Table_rows'] = []
    for i in range(count):
        link = "http://umber.sbs.man.ac.uk/cgi-bin/dbbrowser/PRINTS/DoPRINTS.pl?cmd_a=Display&qua_a=/Type&fun_a=Text&qst_a=" \
                   + info[i][4] + "&disp=2"
        one_row = {'vals': [info[i][2], info[i][3], info[i][4]],
                   'link': link}
        json_ret['Table_rows'].append(one_row)

    return json_ret


def get_tab():
    # Not required
    return None
