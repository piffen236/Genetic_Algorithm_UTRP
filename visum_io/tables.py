# -------------------------------------------------------------------------------
# Name:        visum_io.tables
# Purpose:
#
# Author:      joffa
#
# Created:     01-07-2015
# Copyright:   (c) joffa 2015
# Licence:     <your licence>
# -------------------------------------------------------------------------------
from collections import OrderedDict

import pandas as pd
import os
import datetime

TABLE_ORDER = ['VERSION',
               'INFO',
               'POICATEGORY',
               'USERATTDEF',
               'TIMEVARYINGATTDEF',
               'CALENDARPERIOD',
               'VALIDDAYS',
               'HOLIDAYS',
               'NETWORK',
               'TSYS',
               'MODE',
               'DEMANDSEGMENT',
               'FARESYSTEM',
               'TRANSFERFARE',
               'FAREMODEL',
               'VEHUNIT',
               'VEHCOMB',
               'VEHUNITTOVEHCOMB',
               'DIRECTION',
               'POINT',
               'EDGE',
               'EDGEITEM',
               'FACE',
               'FACEITEM',
               'SURFACE',
               'SURFACEITEM',
               'MAINNODE',
               'NODE',
               'MITIGATIONOPTIONITEM',
               'MAINZONE',
               'ZONE',
               'TOLLSYSTEM',
               'LINKTYPE',
               'TURNSTANDARD',
               'LINK',
               'LINKPOLY',
               'TURN',
               'MAINTURN',
               'MAJORFLOW',
               'CONNECTOR',
               'OPERATOR',
               'TERRITORY',
               'STOP',
               'STOPAREA',
               'STOPPOINT',
               'MAINLINE',
               'LINE',
               'SYSROUTE',
               'SYSROUTEITEM',
               'SYSROUTEVEHTIME',
               'LINEROUTE',
               'LINEROUTEITEM',
               'TIMEPROFILE',
               'TIMEPROFILEITEM',
               'VEHJOURNEY',
               'VEHJOURNEYITEM',
               'VEHJOURNEYSECTION',
               'CHAINEDUPVEHJOURNEYSECTION',
               'TRANSFERWALKTIMESTOPAREA',
               'TRANSFERWALKTIMETSYS',
               'TRANSFERWALKTIMEDIRLINE',
               'TRANSFERWALKTIMETP',
               'TRANSFERWAITTIMETSYS',
               'TRANSFERWAITTIMETP',
               'VEHJOURNEYCOUPLESECTION',
               'VEHJOURNEYCOUPLESECTIONITEM',
               'COUNTLOCATION',
               'DETECTOR',
               'MATRIXTOLL',
               'FAREZONE',
               'STOPTOFAREZONE',
               'TICKETTYPE',
               'FARESUPPLEMENTITEM',
               'DISTANCEFAREITEM',
               'ZONECOUNTFAREITEM',
               'FROMTOZONEFAREITEM',
               'SHORTFAREITEM',
               'TICKETTYPETODSEGFARESYSTEM',
               'BLOCKVERSION',
               'BLOCK',
               'BLOCKITEMTYPE',
               'BLOCKITEM',
               'COORDGRP',
               'COORDGRPITEM',
               'PROPAGATIONLINKINFO',
               'POIOFCAT_1',
               'POIOFCAT_2',
               'POIOFCAT_3',
               'POIOFCAT_4',
               'POIOFCAT_5',
               'POIOFCAT_6',
               'POIOFCAT_7',
               'POIOFCAT_8',
               'POIOFCAT_9',
               'POIOFCAT_10',
               'POIOFCAT_11',
               'POIOFCAT_12',
               'POIOFCAT_13',
               'POIOFCAT_14',
               'POIOFCAT_15',
               'POIOFCAT_16',
               'POIOFCAT_17',
               'POIOFCAT_18',
               'POIOFCAT_19',
               'POIOFCAT_20',
               'POIOFCAT_21',
               'POIOFCAT_22',
               'POIOFCAT_23',
               'POIOFCAT_24',
               'POIOFCAT_25',
               'POIOFCAT_26',
               'POIOFCAT_27',
               'POIOFCAT_28',
               'POIOFCAT_29',
               'POIOFCAT_30',
               'POIOFCAT_31',
               'POIOFCAT_32',
               'POIOFCAT_33',
               'POIOFCAT_34',
               'POIOFCAT_35',
               'POIOFCAT_36',
               'POIOFCAT_37',
               'POIOFCAT_38',
               'POIOFCAT_39',
               'POIOFCAT_40',
               'POIOFCAT_41',
               'POIOFCAT_42',
               'POIOFCAT_43',
               'POIOFCAT_44',
               'POIOFCAT_45',
               'POIOFCAT_46',
               'POIOFCAT_47',
               'POIOFCAT_48',
               'POIOFCAT_49',
               'POIOFCAT_50',
               'POITONODE',
               'POITOLINK',
               'POITOPOICAT',
               'POITOPOI',
               'POITOSTOPAREA',
               'POITOSTOPPOINT',
               'SCREENLINE',
               'SCREENLINEPOLY',
               'STAGETEMPLATE',
               'STAGETEMPLATEITEM',
               'STAGETEMPLATESET',
               'STAGETEMPLATESETITEM',
               'SIGNALGROUPTEMPLATE',
               'SIGNALGROUPTEMPLATEITEM',
               'SIGNALGROUPTEMPLATETOSTAGETEMPLATE',
               'SIGNALCOORDGROUP',
               'SIGNALCONTROL',
               'SIGNALCONTROLTONODE',
               'SIGNALGROUP',
               'STAGE',
               'STAGEITEM',
               'INTERGREEN',
               'LANETEMPLATE',
               'CROSSWALKTEMPLATE',
               'LEGTEMPLATE',
               'LEGTEMPLATEITEM',
               'CROSSWALKTEMPLATETOLEGTEMPLATE',
               'GEOMETRYTEMPLATE',
               'GEOMETRYTEMPLATEITEM',
               'LEG',
               'LANE',
               'LANETURN',
               'SIGNALGROUPTOLANETURN',
               'CROSSWALK',
               'SIGNALGROUPTOCROSSWALK',
               'DETECTORTOCROSSWALK',
               'DETECTORTOLANE',
               'PATHSET',
               'PATH',
               'PATHITEM',
               'FLEETCOMPOSITION',
               'FLEETCOMPOSITIONTOVEHICLESTRATUM',
               'NODETIMEVARYINGATT',
               'MAINNODETIMEVARYINGATT',
               'LINKTIMEVARYINGATT',
               'TURNTIMEVARYINGATT',
               'MAINTURNTIMEVARYINGATT',
               'DEMANDSEGTIMEVARYINGATT',
               'RBCPATTERN',
               'RBCSEQUENCE',
               'RBCPATTERNTIME',
               'RBCSGCONFLICT',
               'RBCOVERLAP',
               'RBCPREEMPTINPUT',
               'RBCSCCOMMUNICATION',
               'RBCPREEMPT',
               'RBCTRANSITSG',
               'RBCTRANSITINPUT',
               'RBCPATTERNSIGNALGROUP',
               'ALIAS']





def read_net_att_file(filename, sep=None):
    """Reads a Visum .NET or .ATT file
        Returns a dict with pandas dataframe for each table
        sep = separator, defaults to ; for .NET files and \t for .ATT files
    """
    if sep == None:
        if os.path.splitext(filename)[1].lower() == '.att':
            sep = '\t'
        else:
            sep = ';'

    tables = []
    with open(filename, 'rb') as f:
        ln_nr = 0
        for ln in f:
            if len(ln) > 0:

                if ln[0] == '*':
                    pass
                elif ln[0] == '$':
                    if ln != '$VISION\r\n':
                        # New table
                        ##                        print ln
                        ##                        return ln
                        curr_table = {'name': ln.split(':')[0][1:],
                                      'cols': ln.split(':')[1].rstrip().split(';'),
                                      'firstrow': ln_nr}
                elif ln == '\r\n':
                    # Empty row
                    curr_table['lastrow'] = ln_nr
                    tables.append(curr_table)
            ln_nr += 1
    lastrow = ln_nr
    result = {}
    for t in tables:
        ##        print t['name']
        ##        print t['firstrow']
        ##        print t['lastrow']
        ##
        ##        skiprows = range(0,t['firstrow']+1) + range(t['lastrow']+1,lastrow)
        ##        print skiprows[:15]
        ##        return skiprows
        result[t['name']] = pd.read_csv(filename,
                                        sep=sep,
                                        skiprows=range(0, t['firstrow']) + range(t['lastrow'] + 1, lastrow), header=0,
                                        names=t['cols'])
    return result


def write_net_att_file(table_dict, filename, sep=None, encoding='iso-8859-15'):
    """
    Writes a Visum .NET or .ATT file

    :param table_dict:
    :param filename: The file name to save the tables in
    :param sep: separator, defaults to ; for .NET files and \\t for .ATT files
    :param encoding: encoding of the file. Defaults to iso-8859-15
    :return:
    """

    filetype = os.path.splitext(filename)[1][1:].upper()

    if sep is None:
        if filetype == u'ATT':
            sep = '\t'
        else:
            sep = ';'

    if u'VERSION' not in table_dict:
        table_dict[u'VERSION'] = pd.DataFrame(
            OrderedDict(
                [(u'VERSNR', [10.000]), (u'FILETYPE', [filetype]), (u'LANGUAGE', [u'ENG']), (u'UNIT', [u'KM'])]))

    if len(table_dict) > 2 and filetype == u'ATT':
        raise ValueError(u'Can only save one table to an .att-file')

    with open(filename, 'wb') as f:
        # Write header
        lns = [u'$VISION',
               u'* KTH Royal Institute of Technology Stockholm',
               u'*',
               u'* %s' % datetime.date.today().isoformat(),
               u'*']
        lns = [u'%s\n' % ln for ln in lns]
        lns = [ln.encode(encoding=encoding) for ln in lns]
        f.writelines(lns)
        ts = table_dict.keys()
        ts = sorted(ts, key=lambda t: TABLE_ORDER.index(t))
        for t in ts:
            lns = [u'',
                   u'*',
                   u'* Table: %s' % t,
                   u'*',
                   u'$%s:%s' % (t, sep.join(table_dict[t].columns))]
            lns = [u'%s\n' % ln for ln in lns]
            lns = [ln.encode(encoding=encoding) for ln in lns]
            f.writelines(lns)
            table_dict[t].to_csv(f, sep=sep, index=False, header=False, encoding=encoding)
