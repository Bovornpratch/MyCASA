import os
import sys
import numpy as np
import json

ims=str(sys.argv[1])


msfile=os.path.basename(ims)
print(f'Checking {msfile}')
ofile=ims.split('.ms')[0]+'.json'

obs=listobs(ims)
field_list=[ i for i in obs.keys() if 'field_' in i ]

# open ms fetch spw
ms.open(ims)
spw_dict=ms.getspectralwindowinfo()
ms.close()

msmd.open(ims)
outdict={'msfile': ims,
         'projid': msmd.projects(), 
         'targets': {}}

for field in field_list:
    fp=obs[field]
    tname=fp['name']
    ra,dec = fp['direction']['m0']['value'], fp['direction']['m1']['value']
    ra,dec = ra/np.pi*180., dec/np.pi*180.

    tindex=int(field.replace('field_',''))
    tspw=[int(i) for i in msmd.spwsforfield(tindex)]
    
    tspw_meta={}
    for j in tspw:
        ospw=spw_dict[str(j)]
        tspw_meta[j]={'reffreq':ospw['RefFreq']/1e9,
                      'bandwidth':ospw['TotalWidth']/1e9,
                      'chanwidth':ospw['ChanWidth']/1e6}
    
    #spw=None
    tdict={'index':tindex,
           'name': tname, 'ra': ra, 'dec':dec,
           'spw':tspw, 'spw_meta': tspw_meta }
    outdict['targets'][tname] = tdict


msmd.close()

    
with open(ofile, "w") as f:
    json.dump(outdict, f)
