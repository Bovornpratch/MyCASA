import os
import glob
import sys
import json


class CheckOverlap:
    def __init__(self, project_dir, outdir='./overlap_ms/'):
        
        # init
        self.project_dir=project_dir
        self.outdir=outdir
        
        self.project_id=self.project_dir.split('/')[-1]
        self.json_list=glob.glob(self.project_dir+'/*.json')
        self.json_list.sort()
        
        
    def _check_spw():
        pass
    
    def execute_check(self):
        
        odir=os.path.join(self.outdir,self.project_id)
        os.makedirs(odir, exist_ok=True)
        msdict={}
        targ_list=[]
        for ijson in self.json_list:
            with open(ijson, 'r') as f:
                jdict = json.load(f)
                msfile=os.path.basename(jdict['msfile'])
                msdict[msfile]=jdict
                targ_list+=list(jdict['targets'].keys())
                
        ms_files=msdict.keys()
        targ_list=list(set(targ_list))
        
        for targ in targ_list:
            cc_ms_list=[]
            for ms in ms_files:
                ms_targs=msdict[ms]['targets']
                if targ in ms_targs:
                    cc_ms_list.append(ms)
                    
            # check spectral windows
            cc_ms_list.append('') 
            
            ofile=f'{self.project_id}_{targ}.list'
            opath=os.path.join(odir,ofile)
            with open(opath, 'w') as f:
                f.write('\n'.join(cc_ms_list))

prj_dir=str(sys.argv[1])
out_dir=str(sys.argv[2])


checkObj=CheckOverlap(project_dir=prj_dir, outdir=out_dir)
checkObj.execute_check()