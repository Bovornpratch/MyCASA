
import os
import sys
import json
import numpy as np


cfg_temp={"input_ms": None,
          "field":None,
          "image_par":{"tc_specmode" : "cube",
                       "tc_imsize": 800,
                       "tc_cell": 0.1,
                       "tc_start": None,
                       "tc_width": 33,
                       "tc_end": None}}

ims=str(sys.argv[1])
outdir=str(sys.argv[2])
os.makedirs(outdir, exist_ok=True)

msfile=os.path.basename(ims)
ofile=ims.split('.ms')[0]+'.cat'

# open ms fetch spw
ms.open(ims)
spwd=ms.getspectralwindowinfo()
ms.close()

obs=listobs(ims)
field_list=[ i for i in obs.keys() if 'field_' in i ]
target_list=[obs[i]['name'] for i in field_list]

print(f'Input MS: {msfile} ')
# find minimum and maximum frequency
msmd.open(ims)

for field in field_list:
    cfg_dict=cfg_temp.copy()
    fp=obs[field]
    tname=fp['name']
    
    cfg_dict['input_ms']=os.path.abspath(ims)
    cfg_dict['field']=tname
    
    # check if calibrator
    # meow
    tindex=int(field.replace('field_',''))
    tspw=[int(i) for i in msmd.spwsforfield(tindex)]

    fcen, bwid=[],[]
    for i in tspw:
        tf=spwd[str(i)]['RefFreq']/1e9
        tb=spwd[str(i)]['TotalWidth']/1e9
        
        # check if valud spw
        if np.abs(tb)<1.9:
            fcen.append(tf)
            bwid.append(np.abs(tb))
            
    fcen, bwid=np.array(fcen), np.array(bwid)
    
    
    #print(tname, np.min(fcen-(bwid)), np.max(fcen+(bwid)))  
    fs=np.round(np.min(fcen-(bwid)),1)
    fe=np.round(np.max(fcen+(bwid)),1)
    
    # set image par
    cfg_dict['image_par']['tc_start']=fs
    cfg_dict['image_par']['tc_end']=fe

    # other stuff
    if 'J' in tname:
        print(f'{tname} is a calibrator, skipping')
    else:
        print(f'Name : {tname}, freq : {fs} to {fe}')
        
        outcfg=os.path.join(outdir, tname+'.json')
        with open(outcfg, 'w') as f:
            json.dump(cfg_dict, f)
            #print(cfg_dict, file=f)


