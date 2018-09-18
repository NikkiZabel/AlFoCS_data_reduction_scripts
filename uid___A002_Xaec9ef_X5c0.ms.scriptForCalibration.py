# ALMA Data Reduction Script

# Calibration

thesteps = []
step_title = {0: 'Import of the ASDM',
              1: 'Fix of SYSCAL table times',
              2: 'listobs',
              3: 'A priori flagging',
              4: 'Generation and time averaging of the WVR cal table',
              5: 'Generation of the Tsys cal table',
              6: 'Generation of the antenna position cal table',
              7: 'Application of the WVR, Tsys and antpos cal tables',
              8: 'Split out science SPWs and time average',
              9: 'Listobs, and save original flags',
              10: 'Initial flagging',
              11: 'Putting a model for the flux calibrator(s)',
              12: 'Save flags before bandpass cal',
              13: 'Bandpass calibration',
              14: 'Save flags before gain cal',
              15: 'Gain calibration',
              16: 'Save flags before applycal',
              17: 'Application of the bandpass and gain cal tables',
              18: 'Split out corrected column',
              19: 'Save flags after applycal'}

if 'applyonly' not in globals(): applyonly = False
try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

import re

import os

if applyonly != True: es = aU.stuffForScienceDataReduction() 


#if re.search('^4.6.0', casadef.casa_version) == None:
# sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 4.6.0')


# CALIBRATE_AMPLI: 
# CALIBRATE_ATMOSPHERE: J0334-4008,NGC1427A,Uranus
# CALIBRATE_BANDPASS: J0334-4008
# CALIBRATE_FLUX: Uranus
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0336-3616
# CALIBRATE_POINTING: J0058+0620,J0334-4008,J0336-3616
# OBSERVE_CHECK: 
# OBSERVE_TARGET: ESO358-G063,NGC1351A,NGC1380,NGC1427A,NGC1436

# Using reference antenna = DA65

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_Xaec9ef_X5c0.ms') == False:
    importasdm('uid___A002_Xaec9ef_X5c0', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=True, process_caldevice=False)
  if applyonly != True: es.fixForCSV2555('uid___A002_Xaec9ef_X5c0.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xaec9ef_X5c0.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.listobs')
  listobs(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    listfile = 'uid___A002_Xaec9ef_X5c0.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    mode = 'manual',
    spw = '5~12,17~26',
    autocorr = True,
    flagbackup = False)
  
  flagdata(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = False)
  
  flagcmd(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xaec9ef_X5c0.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.wvrgcal') 
  
  # Warning: more than one integration time found on science data, I'm picking the lowest value. Please check this is right.
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xaec9ef_X5c0.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.wvr',
    spw = [19, 21, 23, 25],
    toffset = 0,
    tie = ['ESO358-G063,J0336-3616', 'NGC1427A,J0336-3616', 'NGC1351A,J0336-3616', 'NGC1380,J0336-3616', 'NGC1436,J0336-3616'],
    statsource = 'NGC1436')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xaec9ef_X5c0.ms.wvr', spw='19', antenna='DA65',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xaec9ef_X5c0.ms.wvr.plots/uid___A002_Xaec9ef_X5c0.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.tsys') 
  gencal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.tsys',
    caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xaec9ef_X5c0.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = False)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xaec9ef_X5c0.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=False, 
    field='', figfile='uid___A002_Xaec9ef_X5c0.ms.tsys.plots.overlayTime/uid___A002_Xaec9ef_X5c0.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.tsys', msName='uid___A002_Xaec9ef_X5c0.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Position for antenna DA61 is derived from baseline run made on 2015-11-22 10:37:22.
  
  # Note: no baseline run found for antenna DA62.
  
  # Note: the correction for antenna DA52 is larger than 2mm.
  
  # Position for antenna DA52 is derived from baseline run made on 2015-12-16 10:36:49.
  
  # Position for antenna DA54 is derived from baseline run made on 2015-11-22 10:37:22.
  
  # Note: no baseline run found for antenna DV07.
  
  # Position for antenna DA59 is derived from baseline run made on 2015-11-22 10:37:22.
  
  # Note: the correction for antenna DV03 is larger than 2mm.
  
  # Position for antenna DV03 is derived from baseline run made on 2015-12-18 05:37:51.
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.antpos') 
  gencal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA52,DA54,DA59,DA61,DV03',
    parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  #  parameter = [4.10999e-04,-1.98424e-03,-2.09411e-04,3.51765e-05,-3.22489e-05,3.93549e-05,-7.65598e-05,2.19242e-04,-7.63880e-05,-4.65158e-05,1.85439e-04,-6.51274e-05,9.42926e-04,-2.45067e-03,-1.61322e-03])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DV03     9.42926e-04   -2.45067e-03   -1.61322e-03    3.08178e-03      2015-12-18 05:37:51
  # DA52     4.10999e-04   -1.98424e-03   -2.09411e-04    2.03715e-03      2015-12-16 10:36:49
  # DA59    -7.65598e-05    2.19242e-04   -7.63880e-05    2.44466e-04      2015-11-22 10:37:22
  # DA61    -4.65158e-05    1.85439e-04   -6.51274e-05    2.01973e-04      2015-11-22 10:37:22
  # DA54     3.51765e-05   -3.22489e-05    3.93549e-05    6.18562e-05      2015-11-22 10:37:22
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xaec9ef_X5c0.ms', tsystable = 'uid___A002_Xaec9ef_X5c0.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '0',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J0058+0620 didn't have any Tsys measurement, and I couldn't find any close measurement. But this is not a science target, so this is probably Ok.
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '2',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J0336-3616 didn't have any Tsys measurement, so I used the one made on NGC1427A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '3',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['9', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: NGC1436 didn't have any Tsys measurement, so I used the one made on NGC1427A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '4~8,22~23',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['9', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '9~12,24~26',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['9', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: ESO358-G063 didn't have any Tsys measurement, so I used the one made on NGC1427A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '13~16,27~27',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['9', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: NGC1351A didn't have any Tsys measurement, so I used the one made on NGC1427A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '17~18,28~28',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['9', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: NGC1380 didn't have any Tsys measurement, so I used the one made on NGC1427A. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    field = '19~21',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.tsys', 'uid___A002_Xaec9ef_X5c0.ms.wvr', 'uid___A002_Xaec9ef_X5c0.ms.antpos'],
    gainfield = ['9', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xaec9ef_X5c0.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split') 
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.flagversions') 
  
  split(vis = 'uid___A002_Xaec9ef_X5c0.ms',
    outputvis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    datacolumn = 'corrected',
    spw = '19,21,23,25',
    keepflags = True)
  
  

print "# Calibration"

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.listobs')
  listobs(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    listfile = 'uid___A002_Xaec9ef_X5c0.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xaec9ef_X5c0.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  flagdata(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    mode = 'shadow',
    flagbackup = False)
  
  # Flagging edge channels
  flagdata(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = False)

  #There is a jump in phase for all baselines with DV03 between scan 15 and 
  #scan 22. Before scan 15 and after scan 22 the phase is flat. Both phase 
  #calibrations are still useful, but the data in between both scans needs to 
  #be flagged, because we don't know what happens in between. 
  flagdata(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    mode = 'manual',
    spw = '3',
    scan = '16~21',
    flagbackup = False)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    field = '2', # Uranus
    spw = '0,1,2,3',
    standard = 'Butler-JPL-Horizons 2012')
  
  if applyonly != True:
    os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.setjy.field*.png') 
    for i in ['2']:
      plotms(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
        xaxis = 'uvdist',
        yaxis = 'amp',
        ydatacolumn = 'model',
        field = str(i),
        spw = '0,1,2,3',
        avgchannel = '9999',
        coloraxis = 'spw',
        plotfile = 'uid___A002_Xaec9ef_X5c0.ms.split.setjy.field'+i+'.png')
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.ap_pre_bandpass',
    field = '0', # J0334-4008
    spw = '0:0~128,1:0~128,2:0~128,3:0~3840',
    scan = '1,3',
    solint = 'int',
    refant = 'DA65',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.ap_pre_bandpass', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.bandpass',
    field = '0', # J0334-4008
    scan = '1,3',
    solint = 'inf,20MHz',
    combine = 'scan',
    refant = 'DA65',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xaec9ef_X5c0.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.bandpass', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Note: the Solar system object used for flux calibration is highly resolved on some baselines.
  # Note: we will first determine the flux of the phase calibrator(s) on a subset of antennas.
  
  delmod('uid___A002_Xaec9ef_X5c0.ms.split',field='3')
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.phase_short_int') 
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.phase_short_int',
    field = '2', # Uranus
    selectdata = True,
    antenna = 'DA41,DA48,DA49,DA50,DA51,DA52,DA53,DA54,DA55,DA58,DA59,DA61,DA62,DA63,DA65,DV01,DV02,DV03,DV07,DV09,DV11,DV12,DV15,DV16,DV17,DV18,DV19,DV20,DV22,DV23,DV24,DV25&',
    solint = 'int',
    refant = 'DA65',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaec9ef_X5c0.ms.split.bandpass')
  
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.phase_short_int',
    field = '0,3', # J0334-4008,J0336-3616
    selectdata = True,
    solint = 'int',
    refant = 'DA65',
    gaintype = 'G',
    calmode = 'p',
    append = True,
    gaintable = 'uid___A002_Xaec9ef_X5c0.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.phase_short_int', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.ampli_short_inf') 
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.ampli_short_inf',
    field = '0,2,3', # J0334-4008,Uranus,J0336-3616
    selectdata = True,
    solint = 'inf',
    refant = 'DA65',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.split.bandpass', 'uid___A002_Xaec9ef_X5c0.ms.split.phase_short_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.ampli_short_inf', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.flux_short_inf') 
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xaec9ef_X5c0.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.ampli_short_inf',
    fluxtable = 'uid___A002_Xaec9ef_X5c0.ms.split.flux_short_inf',
    reference = '2') # Uranus
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.ampli_short_inf', removeOutliers=True, msName='uid___A002_Xaec9ef_X5c0.ms', writeToFile=True, preavg=10000)
  
  f = open('uid___A002_Xaec9ef_X5c0.ms.split.fluxscale')
  fc = f.readlines()
  f.close()
  
  for phaseCalName in ['J0336-3616']:
    for i in range(len(fc)):
      if fc[i].find('Flux density for '+phaseCalName) != -1 and re.search('in SpW=[0-9]+(?: \(.*?\))? is: [0-9]+\.[0-9]+', fc[i], re.DOTALL|re.IGNORECASE) != None:
        line = (re.search('in SpW=[0-9]+(?: \(.*?\))? is: [0-9]+\.[0-9]+', fc[i], re.DOTALL|re.IGNORECASE)).group(0)
        spwId = (line.split('='))[1].split()[0]
        flux = float((line.split(':'))[1].split()[0])
        setjy(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
          field = phaseCalName.replace(';','*;').split(';')[0],
          spw = spwId,
          standard = 'manual',
          fluxdensity = [flux,0,0,0])
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.phase_int',
    field = '0,2,3', # J0334-4008,Uranus,J0336-3616
    solint = 'int',
    refant = 'DA65',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaec9ef_X5c0.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.phase_int', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.flux_inf') 
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.flux_inf',
    field = '0,2,3', # J0334-4008,Uranus,J0336-3616
    solint = 'inf',
    refant = 'DA65',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.split.bandpass', 'uid___A002_Xaec9ef_X5c0.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.flux_inf', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    caltable = 'uid___A002_Xaec9ef_X5c0.ms.split.phase_inf',
    field = '0,2,3', # J0334-4008,Uranus,J0336-3616
    solint = 'inf',
    refant = 'DA65',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaec9ef_X5c0.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaec9ef_X5c0.ms.split.phase_inf', msName='uid___A002_Xaec9ef_X5c0.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '2']: # J0334-4008,Uranus
    applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xaec9ef_X5c0.ms.split.bandpass', 'uid___A002_Xaec9ef_X5c0.ms.split.phase_int', 'uid___A002_Xaec9ef_X5c0.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = True,
      flagbackup = False)
  
  applycal(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    field = '3,4~28', # ESO358-G063,NGC1427A,NGC1351A,NGC1380,NGC1436
    gaintable = ['uid___A002_Xaec9ef_X5c0.ms.split.bandpass', 'uid___A002_Xaec9ef_X5c0.ms.split.phase_inf', 'uid___A002_Xaec9ef_X5c0.ms.split.flux_inf'],
    gainfield = ['', '3', '3'], # J0336-3616
    interp = 'linear,linear',
    calwt = True,
    flagbackup = False)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.cal') 
  os.system('rm -rf uid___A002_Xaec9ef_X5c0.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#AMBIENT',
   'CALIBRATE_WVR#HOT',
   'CALIBRATE_WVR#OFF_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  split(vis = 'uid___A002_Xaec9ef_X5c0.ms.split',
    outputvis = 'uid___A002_Xaec9ef_X5c0.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = True)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaec9ef_X5c0.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

