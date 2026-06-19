import sys
import os

inp_file=str(sys.argv[1])
out_file=str(sys.argv[2])


class ConcatMS:
    def __init__(self, input_file, output_ms='./concat_ms.ms', field=None):
        self.input_file=input_file
        self.output_ms=output_ms
        
        # internal stuff
        self.ms_list=self._fetch_ms()
        
        
    def _fetch_ms(self):
        
        with open(self.input_file, 'r') as f:
            olist=[i.strip('\n') for i in f.readlines()]
        
        return olist
    
    def execute(self):
        # concat the stuff
        concat(vis=self.ms_list, concatvis=self.output_ms,)
        
ccobj=ConcatMS(input_file=inp_file, output_ms=out_file)
ccobj.execute()
