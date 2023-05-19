import os
import sys
import itertools
sys.dont_write_bytecode = True

#IMPORT MODULES FROM OTHER DIR
sys.path.insert(0, os.getcwd().replace("condor",""))
sys.path.insert(0, os.getcwd().replace("HistNano/condor",""))
from Inputs import *
from JobsNano_cff import Samples_2023C 

if not os.path.exists("tmpSub/log"):
    os.makedirs("tmpSub/log")
condorLogDir = "log"
tarFile = "tmpSub/EgammaNanoTnP.tar.gz"
if os.path.exists(tarFile):
	os.system("rm %s"%tarFile)
os.system("tar -zcvf %s --exclude=../../../EgammaNanoTnP/.git/ --exclude=../../HistNano/condor ../../../EgammaNanoTnP "%tarFile)
os.system("cp runMakeHist.sh tmpSub/")
common_command = \
'Universe   = vanilla\n\
should_transfer_files = YES\n\
when_to_transfer_output = ON_EXIT\n\
Transfer_Input_Files = EgammaNanoTnP.tar.gz, runMakeHist.sh\n\
x509userproxy        = /uscms/home/rverma/x509up_u56634\n\
Output = %s/log_$(cluster)_$(process).stdout\n\
Error  = %s/log_$(cluster)_$(process).stderr\n\
Log    = %s/log_$(cluster)_$(process).condor\n\n'%(condorLogDir, condorLogDir, condorLogDir)
#use_x509userproxy = true\n\

#----------------------------------------
#Create jdl files
#----------------------------------------
subFile = open('tmpSub/condorSubmit.sh','w')
for year in Years: 
    samples = eval("Samples_%s"%year)
    jdlName = 'submitJobs_%s.jdl'%(year)
    jdlFile = open('tmpSub/%s'%jdlName,'w')
    jdlFile.write('Executable =  runMakeHist.sh \n')
    jdlFile.write(common_command)
    outDir="%s/%s"%(outDir, year)
    os.system("eos root://cmseos.fnal.gov mkdir -p %s"%outDir) 
    jdlFile.write("X=$(step)+1\n")
    
    for sampleName, nJobEvt in samples.items():
        nJob = nJobEvt[0]
        args =  'Arguments  = %s %s $INT(X) %i %s\n' %(year, sampleName, nJob, outDir)
        args += "Queue %i\n\n"%nJob
        jdlFile.write(args)
    
    subFile.write("condor_submit %s\n"%jdlName)
	#print "condor_submit jdl/%s"%jdlFile
    jdlFile.close() 
subFile.close()