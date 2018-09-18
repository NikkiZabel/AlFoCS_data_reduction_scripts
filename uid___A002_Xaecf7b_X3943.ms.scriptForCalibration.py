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

import casadef

if applyonly != True: es = aU.stuffForScienceDataReduction() 


if re.search('^5.1.1', casadef.casa_version) == None:
 sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 5.1.1')


# CALIBRATE_AMPLI: 
# CALIBRATE_ATMOSPHERE: FCC207,J0334-4008
# CALIBRATE_BANDPASS: J0334-4008
# CALIBRATE_DIFFGAIN: 
# CALIBRATE_FLUX: J0334-4008
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0336-3616
# CALIBRATE_POINTING: J0334-4008
# OBSERVE_CHECK: 
# OBSERVE_TARGET: FCC117,FCC198,FCC206,FCC207,FCC261,FCC302,FCC306,FCC316,FCC32,FCC332,FCC44,FCC_102,FCC_120

# Using reference antenna = DA65

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_Xaecf7b_X3943.ms') == False:
    importasdm('uid___A002_Xaecf7b_X3943', asis='Antenna Station Receiver Source CalAtmosphere CalWVR CorrelatorMode SBSummary', bdfflags=True, lazy=True, process_caldevice=False)
    if not os.path.exists('uid___A002_Xaecf7b_X3943.ms.flagversions'):
      print 'ERROR in importasdm. Output MS is probably not useful. Will stop here.'
      thesteps = []
  if applyonly != True: es.fixForCSV2555('uid___A002_Xaecf7b_X3943.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_Xaecf7b_X3943.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.listobs')
  listobs(vis = 'uid___A002_Xaecf7b_X3943.ms',
    listfile = 'uid___A002_Xaecf7b_X3943.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms',
    mode = 'manual',
    spw = '5~12,17~26',
    autocorr = True,
    flagbackup = False)
  
  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = False)
  
  flagcmd(vis = 'uid___A002_Xaecf7b_X3943.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_Xaecf7b_X3943.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_Xaecf7b_X3943.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.wvr') 
  
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.wvrgcal') 
  
  # Warning: more than one integration time found on science data, I'm picking the lowest value. Please check this is right.
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xaecf7b_X3943.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.wvr',
    spw = [19, 21, 23, 25],
    toffset = 0,
    tie = ['FCC_120,J0336-3616', 'FCC117,J0336-3616', 'FCC261,J0336-3616', 'FCC198,J0336-3616', 'FCC206,J0336-3616', 'FCC207,J0336-3616', 'FCC316,J0336-3616', 'FCC_102,J0336-3616', 'FCC332,J0336-3616', 'FCC306,J0336-3616', 'FCC44,J0336-3616', 'FCC32,J0336-3616', 'FCC302,J0336-3616'],
    statsource = 'FCC32')
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_Xaecf7b_X3943.ms.wvr', spw='19', antenna='DA65',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_Xaecf7b_X3943.ms.wvr.plots/uid___A002_Xaecf7b_X3943.ms.wvr') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.tsys') 
  gencal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.tsys',
    caltype = 'tsys')
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms.tsys',
    mode = 'manual',
    spw = '17:0~3;124~127,19:0~3;124~127,21:0~3;124~127,23:0~3;124~127',
    flagbackup = False)
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_Xaecf7b_X3943.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='92.1875%',showfdm=True, showBasebandNumber=True, showimage=False, 
    field='', figfile='uid___A002_Xaecf7b_X3943.ms.tsys.plots.overlayTime/uid___A002_Xaecf7b_X3943.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaecf7b_X3943.ms.tsys', msName='uid___A002_Xaecf7b_X3943.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Warning: no baseline run found for following antenna(s): ['DA49', 'DA41', 'DA54', 'DV20'].
  
  # Position for antenna DV19 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV18 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA65 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA48 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA61 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA45 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA44 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV12 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV14 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA43 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV16 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV23 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA63 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV15 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna PM04 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV11 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV22 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Note: the correction for antenna DA52 is larger than 2mm.
  
  # Position for antenna DA52 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA50 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA51 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV25 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV06 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DA59 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Note: the correction for antenna DV03 is larger than 2mm.
  
  # Position for antenna DV03 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV01 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV17 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV21 is derived from baseline run made on 2016-01-17 04:48:51.
  
  # Position for antenna DV24 is derived from baseline run made on 2016-01-17 04:48:51.
  
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.antpos') 
  gencal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA43,DA44,DA45,DA48,DA50,DA51,DA52,DA59,DA61,DA63,DA65,DV01,DV03,DV06,DV11,DV12,DV14,DV15,DV16,DV17,DV18,DV19,DV21,DV22,DV23,DV24,DV25,PM04',
  #  parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    parameter = [-2.79286e-04,2.46991e-04,2.72502e-04,-4.32809e-04,4.42698e-04,4.25654e-04,-1.41645e-05,-2.45379e-04,-2.15204e-04,-1.38686e-04,1.75296e-04,2.80635e-04,-3.06111e-04,-4.90461e-04,-1.63374e-04,-2.55717e-04,5.24833e-04,1.39601e-04,2.52368e-04,-3.01022e-03,-1.25258e-03,-1.16093e-04,-4.50502e-04,-2.39999e-04,-2.44996e-04,7.86517e-04,4.98506e-04,-1.82066e-04,-9.90175e-05,-2.58773e-05,-4.43929e-04,6.81223e-04,1.88472e-04,1.72469e-04,4.73794e-04,8.43625e-04,1.08866e-03,-2.84396e-03,-1.91613e-03,-2.29872e-04,-6.71560e-04,-9.65228e-05,-1.59555e-04,-1.96314e-04,-1.86523e-05,-3.99087e-05,4.19831e-04,8.25250e-05,-4.38537e-04,1.30207e-03,5.98512e-04,-1.00967e-04,5.03072e-04,5.18858e-04,-6.55585e-05,-3.62731e-04,1.75914e-04,-9.94805e-07,6.84715e-05,-3.05240e-04,-1.56684e-04,6.10239e-04,4.44800e-04,-2.52092e-04,3.09928e-04,1.82044e-04,1.64870e-04,1.51620e-04,1.80525e-04,-2.62999e-04,-3.55477e-04,-2.79241e-04,9.07761e-05,4.04096e-04,1.87916e-04,1.56164e-04,4.10643e-04,2.52755e-04,-1.59566e-04,3.37291e-04,4.77534e-04,-1.69117e-04,7.46297e-04,4.41332e-04])
  
  
  # antenna x_offset y_offset z_offset total_offset baseline_date
  # DV03     1.08866e-03   -2.84396e-03   -1.91613e-03    3.59789e-03      2016-01-17 04:48:51
  # DA52     2.52368e-04   -3.01022e-03   -1.25258e-03    3.27018e-03      2016-01-17 04:48:51
  # DV14    -4.38537e-04    1.30207e-03    5.98512e-04    1.49864e-03      2016-01-17 04:48:51
  # DV01     1.72469e-04    4.73794e-04    8.43625e-04    9.82817e-04      2016-01-17 04:48:51
  # DA61    -2.44996e-04    7.86517e-04    4.98506e-04    9.62882e-04      2016-01-17 04:48:51
  # PM04    -1.69117e-04    7.46297e-04    4.41332e-04    8.83365e-04      2016-01-17 04:48:51
  # DA65    -4.43929e-04    6.81223e-04    1.88472e-04    8.34661e-04      2016-01-17 04:48:51
  # DV18    -1.56684e-04    6.10239e-04    4.44800e-04    7.71226e-04      2016-01-17 04:48:51
  # DA44    -4.32809e-04    4.42698e-04    4.25654e-04    7.51323e-04      2016-01-17 04:48:51
  # DV15    -1.00967e-04    5.03072e-04    5.18858e-04    7.29718e-04      2016-01-17 04:48:51
  # DV06    -2.29872e-04   -6.71560e-04   -9.65228e-05    7.16345e-04      2016-01-17 04:48:51
  # DV25    -1.59566e-04    3.37291e-04    4.77534e-04    6.06025e-04      2016-01-17 04:48:51
  # DA50    -3.06111e-04   -4.90461e-04   -1.63374e-04    6.00789e-04      2016-01-17 04:48:51
  # DA51    -2.55717e-04    5.24833e-04    1.39601e-04    6.00274e-04      2016-01-17 04:48:51
  # DA59    -1.16093e-04   -4.50502e-04   -2.39999e-04    5.23478e-04      2016-01-17 04:48:51
  # DV22    -2.62999e-04   -3.55477e-04   -2.79241e-04    5.22980e-04      2016-01-17 04:48:51
  # DV24     1.56164e-04    4.10643e-04    2.52755e-04    5.06853e-04      2016-01-17 04:48:51
  # DA43    -2.79286e-04    2.46991e-04    2.72502e-04    4.61803e-04      2016-01-17 04:48:51
  # DV23     9.07761e-05    4.04096e-04    1.87916e-04    4.54803e-04      2016-01-17 04:48:51
  # DV19    -2.52092e-04    3.09928e-04    1.82044e-04    4.39028e-04      2016-01-17 04:48:51
  # DV12    -3.99087e-05    4.19831e-04    8.25250e-05    4.29722e-04      2016-01-17 04:48:51
  # DV16    -6.55585e-05   -3.62731e-04    1.75914e-04    4.08432e-04      2016-01-17 04:48:51
  # DA48    -1.38686e-04    1.75296e-04    2.80635e-04    3.58773e-04      2016-01-17 04:48:51
  # DA45    -1.41645e-05   -2.45379e-04   -2.15204e-04    3.26686e-04      2016-01-17 04:48:51
  # DV17    -9.94805e-07    6.84715e-05   -3.05240e-04    3.12827e-04      2016-01-17 04:48:51
  # DV21     1.64870e-04    1.51620e-04    1.80525e-04    2.87680e-04      2016-01-17 04:48:51
  # DV11    -1.59555e-04   -1.96314e-04   -1.86523e-05    2.53663e-04      2016-01-17 04:48:51
  # DA63    -1.82066e-04   -9.90175e-05   -2.58773e-05    2.08859e-04      2016-01-17 04:48:51
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_Xaecf7b_X3943.ms', tsystable = 'uid___A002_Xaecf7b_X3943.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '0',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: J0336-3616 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '1',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC32 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '2',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC44 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '3',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC117 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '4',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC198 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '5',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC206 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '6',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '7',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC316 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '8',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC302 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '9',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC_102 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '10',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC_120 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '11',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC261 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '12',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC306 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '13',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  # Note: FCC332 didn't have any Tsys measurement, so I used the one made on FCC207. This is probably Ok.
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms',
    field = '14',
    spw = '19,21,23,25',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.tsys', 'uid___A002_Xaecf7b_X3943.ms.wvr', 'uid___A002_Xaecf7b_X3943.ms.antpos'],
    gainfield = ['7', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = True,
    flagbackup = False)
  
  
  
  if applyonly != True: es.getCalWeightStats('uid___A002_Xaecf7b_X3943.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split') 
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.flagversions') 
  
  split(vis = 'uid___A002_Xaecf7b_X3943.ms',
    outputvis = 'uid___A002_Xaecf7b_X3943.ms.split',
    datacolumn = 'corrected',
    spw = '19,21,23,25',
    keepflags = True)
  
  

print "# Calibration"

# Listobs, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.listobs')
  listobs(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    listfile = 'uid___A002_Xaecf7b_X3943.ms.split.listobs')
  
  
  if not os.path.exists('uid___A002_Xaecf7b_X3943.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  #Flagging shadowed data  
  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'shadow',
    flagbackup = False)
  
  #Flagging edge channels  
  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = False)

  #The data for DV23 are off compared to the other data when looking at the 
  #amp vs. uv dist plot for the flux calibrator (data points lie lower), in 
  #spw 1,3, and 4. 
  #From the tsys plots, this antenna has an increased temperature. Flag all
  #data for this antenna.
  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'manual',
    antenna = 'DV23',
    flagbackup = False) 

  #The data for nearly all antennas in scan 54 look irregular compared to the
  #other scans.
  #It is unclear whether the data in just this scan are affected or whether
  #other data in adjacent scans are also affected.  To be conservative, flag 
  #all data for all antennas between the previous and next phase 
  #calibrator observations.
  flagdata(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'manual',
    scan='38~70',
    flagbackup = False) 
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    standard = 'manual',
    field = 'J0334-4008',
    fluxdensity = [0.821965610291, 0, 0, 0],
    spix = -0.548138815829,
    reffreq = '107.917152856GHz')
  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.split.ap_pre_bandpass',
    field = '0', # J0334-4008
    spw = '0:0~127,1:0~127,2:0~127,3:0~3839',
    scan = '1,3',
    solint = 'int',
    refant = 'DA65',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaecf7b_X3943.ms.split.ap_pre_bandpass', msName='uid___A002_Xaecf7b_X3943.ms.split', interactive=False) 

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.split.bandpass',
    field = '0', # J0334-4008
    scan = '1,3',
    solint = 'inf,20MHz',
    combine = 'scan',
    refant = 'DA65',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_Xaecf7b_X3943.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaecf7b_X3943.ms.split.bandpass', msName='uid___A002_Xaecf7b_X3943.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.split.phase_int',
    field = '0~1', # J0334-4008,J0336-3616
    solint = 'int',
    refant = 'DA65',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaecf7b_X3943.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaecf7b_X3943.ms.split.phase_int', msName='uid___A002_Xaecf7b_X3943.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.split.ampli_inf',
    field = '0~1', # J0334-4008,J0336-3616
    solint = 'inf',
    refant = 'DA65',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.split.bandpass', 'uid___A002_Xaecf7b_X3943.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaecf7b_X3943.ms.split.ampli_inf', msName='uid___A002_Xaecf7b_X3943.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_Xaecf7b_X3943.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.split.ampli_inf',
    fluxtable = 'uid___A002_Xaecf7b_X3943.ms.split.flux_inf',
    reference = '0') # J0334-4008
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_Xaecf7b_X3943.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_Xaecf7b_X3943.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    caltable = 'uid___A002_Xaecf7b_X3943.ms.split.phase_inf',
    field = '0~1', # J0334-4008,J0336-3616
    solint = 'inf',
    refant = 'DA65',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_Xaecf7b_X3943.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_Xaecf7b_X3943.ms.split.phase_inf', msName='uid___A002_Xaecf7b_X3943.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0']: # J0334-4008
    applycal(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
      field = str(i),
      gaintable = ['uid___A002_Xaecf7b_X3943.ms.split.bandpass', 'uid___A002_Xaecf7b_X3943.ms.split.phase_int', 'uid___A002_Xaecf7b_X3943.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = True,
      flagbackup = False)
  
  applycal(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    field = '1,2~14', # FCC_120,FCC117,FCC261,FCC198,FCC206,FCC207,FCC316,FCC_102,FCC332,FCC306,FCC44,FCC32,FCC302
    gaintable = ['uid___A002_Xaecf7b_X3943.ms.split.bandpass', 'uid___A002_Xaecf7b_X3943.ms.split.phase_inf', 'uid___A002_Xaecf7b_X3943.ms.split.flux_inf'],
    gainfield = ['', '1', '1'], # J0336-3616
    interp = 'linear,linear',
    calwt = True,
    flagbackup = False)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.cal') 
  os.system('rm -rf uid___A002_Xaecf7b_X3943.ms.split.cal.flagversions') 
  
  listOfIntents = ['CALIBRATE_BANDPASS#ON_SOURCE',
   'CALIBRATE_FLUX#ON_SOURCE',
   'CALIBRATE_PHASE#ON_SOURCE',
   'CALIBRATE_WVR#AMBIENT',
   'CALIBRATE_WVR#HOT',
   'CALIBRATE_WVR#OFF_SOURCE',
   'CALIBRATE_WVR#ON_SOURCE',
   'OBSERVE_TARGET#ON_SOURCE']
  
  split(vis = 'uid___A002_Xaecf7b_X3943.ms.split',
    outputvis = 'uid___A002_Xaecf7b_X3943.ms.split.cal',
    datacolumn = 'corrected',
    intent = ','.join(listOfIntents),
    keepflags = True)
  
  

# Save flags after applycal
mystep = 19
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_Xaecf7b_X3943.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')
  
  

