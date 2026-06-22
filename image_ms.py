import os
import sys
import json
import glob
import shutil
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as conts


class ImageField:
    def __init__(self, input_ms, outdir = './', field = '0',
                 suffix=None,
                 tc_specmode='cube', tc_niter=500, tc_cell=0.1, tc_imsize = 800, 
                 tc_weighting = 'natural', tc_robust=0.5,
                 tc_gridder='standard', tc_deconvolver='hogbom',
                 tc_gain=0.1, tc_nsigma=2.0, 
                 tc_cycleniter= 10, tc_cyclefactor=1,
                 tc_minpsffraction=0.05, tc_maxpsffraction=0.8, 
                 tc_pblimit=0.10,
                 # spec parameters
                 tc_start=95, tc_end=105, tc_width=50,
                 tc_reffreq=100):

        # define I/O
        self.input_ms = input_ms
        self.basename = os.path.basename(self.input_ms)
        self.outdir = outdir
        self.field = field

        if suffix  is None:
            suff=''
        else:
            suff=f'_{suffix}'

        # output image name
        self.imagename = f'{self.field}'+suff #Output images
        self.interactive = False

        # tclean parameters
        # define specmode
        self.tc_specmode = tc_specmode

        # define specmode
        self.tc_specmode = tc_specmode
        self.tc_niter = tc_niter
        self.tc_cell = str(tc_cell)+'arcsec'
        self.tc_imsize = tc_imsize
        self.tc_weighting = tc_weighting
        self.tc_robust = tc_robust

        # Gridding and CLEAN algorithm choice. All of these, to begin with, are standard inputs,
        # so we do not actually need to input them, but we will here for completeness.
        self.tc_gridder = tc_gridder
        self.tc_deconvolver = tc_deconvolver
        self.tc_gain = tc_gain
        self.tc_threshold = "" # we don't set exit thresold
        # Set global threshold for the residual image max in nsigma*rms to stop iterations
        self.tc_nsigma =tc_nsigma

        # Max number of minor cycle iterations per major cycle.
        # Set to -1 initially as we will decide iteratively in interactive mode.
        self.tc_cycleniter = tc_cycleniter
        # Used to determine minor cycle threshold. Factor multiplied by the maximum dirty beam
        # sidelobe level to calculate when to trigger major cycle.
        self.tc_cyclefactor = tc_cyclefactor
        # Used to determine minor cycle threshold. If max dirty beam sidelobe level is less than
        # this, use 5% as a threshold to trigger major cycle. Lower boundary for major cycle trigger.
        self.tc_minpsffraction = tc_minpsffraction
        # Used to determine minor cycle threshold. If max dirty beam sidelobe level is more than this,
        # use 80% as a threshold to trigger major cycle. Upper boundary for major cycle trigger.
        self.tc_maxpsffraction = tc_maxpsffraction
        # Primary beam limit sets the size of the field where valid data is included in the field-of-view
        # The primary beam size is set by the antenna size (7 m for SMA antennas).
        # Roughly speaking, the noise level goes as 1 / pb decreasing radially outward.
        self.tc_pblimit = tc_pblimit

        # specmode specific pars
        # mfs mode
        self.tc_reffreq=tc_reffreq
        
        # cube mode
        self.tc_width=tc_width 
        self.tc_start=tc_start
        self.tc_end=tc_end
        
        
        # calculate number of channels
        self.nchans= int((self.tc_end-self.tc_start)/(self.tc_width/1000))
        # image masking pars set up mas
        xcen,ycen=int(self.tc_imsize/2), int(self.tc_imsize/2)
        rad = 0.8*(self.tc_imsize/2)
        self.tc_mask = f'circle[[{xcen}pix,{ycen}pix], {rad}pix]'
    
    #def update_from_dict(self, pdict):
    #    self.__dict__.update(pdict)
        
    def _cont_tclean(self, of, iters):
        raise NotImplementedError("Meow")

        
    def _cube_tclean(self, of, iters):
        
        tclean(vis=self.input_ms,
	           imagename=of,
	           field=self.field,
               datacolumn='corrected',
	           interactive=self.interactive,
	           niter=iters,
	           cell=self.tc_cell,
	           imsize=self.tc_imsize,
	           weighting=self.tc_weighting,
	           robust=self.tc_robust,
	           gridder=self.tc_gridder,
	           deconvolver=self.tc_deconvolver,
	           gain=self.tc_gain,
	           threshold=self.tc_threshold,
	           nsigma=self.tc_nsigma,
	           cycleniter=self.tc_cycleniter,
	           cyclefactor=self.tc_cyclefactor,
	           minpsffraction=self.tc_minpsffraction,
	           maxpsffraction=self.tc_maxpsffraction,
	           specmode=self.tc_specmode, 
               width=f"{self.tc_width}MHz",
               start=f'{self.tc_start}GHz',
               nchan=self.nchans,
               #mask=self.tc_mask,
               usemask='pb', pbmask=0.80,)

    
    def execute_tclean(self, of, iters):

        print('Running tclean')
        if self.tc_specmode=='cube':
            img_func=self._cube_tclean
        elif self.tc_specmode=='mfs':
            img_func=self._cont_tclean
        else:
            raise NotImplementedError("Meow")
        # run the imaging
        img_func(of, iters)
        
    def exportfits(self, ima):
        fima=ima+'.fits'
        exportfits(imagename=ima, fitsimage=fima, 
                   overwrite=True)
        
    def run_imaging(self):
        # create dirty image
        odir = self.outdir
        # remove prevous data
        cflag = os.path.exists(odir)
        if cflag:
            shutil.rmtree(odir)
        
        os.makedirs(odir, exist_ok=True)
        # set up image spec type
        if self.tc_specmode=='cube':
            print("Running Spec imaging mode")
            self.dname= os.path.join(self.outdir, self.field+'_dirty_cube')
            self.cname= os.path.join(self.outdir, self.field+'_clean_cube')
            print(f"Image:{self.tc_start}-{self.tc_end} GHz")
            print(f"Using:{self.nchans} channels {self.tc_width}MHz wide")

        elif self.tc_specmode=='mfs':
            print("Running Continuum imaging mode")
            self.dname= os.path.join(self.outdir, self.field+'_dirty_cont')
            self.cname= os.path.join(self.outdir, self.field+'_clean_cont')
        else:
            raise NotImplementedError("Meow")
            
        print(f'Read in {self.input_ms}')
        print(f'saving results to {self.outdir}')
        print(f'saving dirty beam to {os.path.basename(self.dname)}')
        print(f'saving clean beam to {os.path.basename(self.cname)}')
        print(f'Cleaning {self.field}')
        
        # create dirty beam
        print(f"Imaging {self.tc_imsize} pixels with {self.tc_cell} sampling")
        self.execute_tclean(self.dname, 0)
        
        # create cleaned image
        print('Creating cleaned image')
        self.execute_tclean(self.cname, self.tc_niter)

        # Passband correction
        impbcor(imagename=self.cname+'.image',
                pbimage=self.cname+'.pb',
                outfile=self.cname+'.pbcorr.image',)
        
        # export to fits
        of_list=glob.glob(os.path.join(self.outdir, self.field+'*'))
        for file in of_list:
            self.exportfits(file)
        


class ImageMS:
    def __init__(self, inp_cfg, out_dir):
        
        self.inp_cfg=inp_cfg
        self.out_dir=out_dir
    
        # internal stuff
        with open(self.inp_cfg, 'r') as file:
            self.cfg_dict = json.load(file)
            
        self.inp_ms=self.cfg_dict['input_ms']
        self.ms_name=os.path.basename(self.inp_ms.split('.ms')[0])

        self.field_list=self.fetch_field_list()
        self.image_par=self.cfg_dict['image_par']
        
    def fetch_field_list(self):
        if isinstance(self.cfg_dict['field'], list):
            fout=self.cfg_dict['field']  
        elif isinstance(self.cfg_dict['field'], str):
            fout=[self.cfg_dict['field']]
        else:
            raise AssertionError('Unknown field format')
        return fout
        
    def RunImaging(self):
        
        for field in self.field_list:
            print(field)
            odir=os.path.join(self.out_dir, self.ms_name, field)
            os.makedirs(odir, exist_ok=True)
            fobj=ImageField(input_ms=self.inp_ms, 
                            outdir = odir, field = field,
                            **self.image_par)
            #fobj.update_from_dict()
            fobj.run_imaging()
            

if __name__ == '__main__':    
    input_cfg = str(sys.argv[1])
    output_dir = str(sys.argv[2])        
    
    imaobj=ImageMS(inp_cfg=input_cfg,
                   out_dir=output_dir)
    imaobj.RunImaging()