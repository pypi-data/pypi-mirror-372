import time
import warnings
import numpy as np
import os.path as pa
from astropy.io import fits
import scipy.ndimage as ndimage
from astropy.table import Column
from sfft.AutoSparsePrep import Auto_SparsePrep
from sfft.utils.SFFTSolutionReader import Realize_FluxScaling
from sfft.sfftcore.SFFTSubtract import GeneralSFFTSubtract
from sfft.sfftcore.SFFTConfigure import SingleSFFTConfigure
# version: Mar 18, 2023

__author__ = "Lei Hu <leihu@andrew.cmu.edu>"
__version__ = "v1.4"

class Easy_SparsePacket:
    @staticmethod
    def ESP(FITS_REF, FITS_SCI, FITS_DIFF=None, FITS_Solution=None, ForceConv='AUTO', GKerHW=None, \
        KerHWRatio=2.0, KerHWLimit=(2, 20), KerPolyOrder=2, BGPolyOrder=0, ConstPhotRatio=True, \
        MaskSatContam=False, GAIN_KEY='GAIN', SATUR_KEY='ESATUR', BACK_TYPE='MANUAL', BACK_VALUE=0.0, \
        BACK_SIZE=64, BACK_FILTERSIZE=3, DETECT_THRESH=2.0, ANALYSIS_THRESH=2.0, DETECT_MINAREA=5, \
        DETECT_MAXAREA=0, DEBLEND_MINCONT=0.005, BACKPHOTO_TYPE='LOCAL', ONLY_FLAGS=[0], BoundarySIZE=30, \
        XY_PriorSelect=None, Hough_MINFR=0.1, Hough_PeakClip=0.7, BeltHW=0.2, PointSource_MINELLIP=0.3, \
        MatchTol=None, MatchTolFactor=3.0, COARSE_VAR_REJECTION=True, CVREJ_MAGD_THRESH=0.12, \
        ELABO_VAR_REJECTION=True, EVREJ_RATIO_THREH=5.0, EVREJ_SAFE_MAGDEV=0.04, StarExt_iter=4, \
        XY_PriorBan=None, PostAnomalyCheck=False, PAC_RATIO_THRESH=5.0, BACKEND_4SUBTRACT='Cupy', \
        CUDA_DEVICE_4SUBTRACT='0', NUM_CPU_THREADS_4SUBTRACT=8, VERBOSE_LEVEL=2):
        
        """
        # NOTE: This function is to Perform Sparse-Flavor SFFT for a single task:
        #       Cupy backend: do preprocessing on one CPU thread, and perform subtraction on one GPU device.
        #       Numpy backend: do preprocessing on one CPU thread, and perform subtraction with pyFFTW and Numba 
        #                      using multiple threads (-NUM_CPU_THREADS_4SUBTRACT).

        * Parameters for Sparse-Flavor SFFT [single task]

        # ----------------------------- Computing Enviornment --------------------------------- #

        -BACKEND_4SUBTRACT ['Cupy']     # 'Cupy' or 'Numpy'. 
                                        # Cupy backend require GPU(s) that is capable of performing double-precision calculations,
                                        # while Numpy backend is a pure CPU-based backend for sfft subtraction.
                                        # NOTE: 'Pycuda' backend is no longer supported since sfft v1.4.0.
        
        -CUDA_DEVICE_4SUBTRACT ['0']    # it specifies certain GPU device (index) to conduct the subtraction task.
                                        # the GPU devices are usually numbered 0 to N-1 (you may use command nvidia-smi to check).
                                        # this argument becomes trivial for Numpy backend.

        -NUM_CPU_THREADS_4SUBTRACT [8]  # it specifies the number of CPU threads used for sfft subtraction in Numpy backend.
                                        # SFFT in Numpy backend has been implemented with pyFFTW and numba, 
                                        # that allow for parallel computing on CPUs. Of course, the Numpy 
                                        # backend is generally much slower than GPU backends.
        
        # ----------------------------- Preprocessing with Source Selection for Image-Masking --------------------------------- #

        # > Configurations for SExtractor

        -GAIN_KEY ['GAIN']             # SExtractor Parameter GAIN_KEY
                                       # i.e., keyword of GAIN in FITS header (of reference & science)

        -SATUR_KEY ['ESATUR']          # SExtractor Parameter SATUR_KEY
                                       # i.e., keyword of effective saturation in FITS header (of reference & science)
                                       # Remarks: one may think 'SATURATE' is a more common keyword name for saturation level.
                                       #          However, note that Sparse-Flavor SFFT requires sky-subtracted images as inputs, 
                                       #          we need to use the 'effective' saturation level after the sky-subtraction.
                                       #          e.g., set ESATURA = SATURATE - (SKY + 10*SKYSIG)

        -BACK_TYPE ['MANUAL']          # SExtractor Parameter BACK_TYPE = [AUTO or MANUAL].
                                       # As Sparse-Flavor-SFFT requires the input images being sky-subtracted,
                                       # the default setting uses zero-background (i.e., BACK_TYPE='MANUAL' & BACK_VALUE=0.0).
                                       # However, one may also use BACK_TYPE='AUTO' for some specific cases
                                       # E.g., point sources located at the outskirts of a bright galaxy will have a relatively
                                       #       high local background. Even if the image has been sky-subtracted properly, 
                                       #       SExtractor can only detect it when you set BACK_TYPE='AUTO'.
         
        -BACK_VALUE [0.0]              # SExtractor Parameter BACK_VALUE (only work for BACK_TYPE='MANUAL')

        -BACK_SIZE [64]                # SExtractor Parameter BACK_SIZE

        -BACK_FILTERSIZE [3]           # SExtractor Parameter BACK_FILTERSIZE

        -DETECT_THRESH [2.0]           # SExtractor Parameter DETECT_THRESH
                                       # NOTE: One may notice that the default DETECT_THRESH in SExtractor is 1.5,
                                       #       Using a 'cold' detection threshold here is to speed up SExtractor.
                                       #       Although DETECT_THRESH = 2.0 means we will miss the faint-end sources with 
                                       #       SNR < 9 (approximately), the cost is generally acceptable for source selection.

        -ANALYSIS_THRESH [2.0]         # SExtractor Parameter ANALYSIS_THRESH
                                       # NOTE: By default, let -ANALYSIS_THRESH = -DETECT_THRESH

        -DETECT_MINAREA [5]            # SExtractor Parameter DETECT_MINAREA
        
        -DETECT_MAXAREA [0]            # SExtractor Parameter DETECT_MAXAREA

        -DEBLEND_MINCONT [0.005]       # SExtractor Parameter DEBLEND_MINCONT (typically, 0.001 - 0.005)

        -BACKPHOTO_TYPE ['LOCAL']      # SExtractor Parameter BACKPHOTO_TYPE

        -ONLY_FLAGS [0]                # Restrict SExtractor Output Photometry Catalog by Source FLAGS
                                       # Common FLAGS (Here None means no restrictions on FLAGS):
                                       # 1: aperture photometry is likely to be biased by neighboring sources 
                                       #    or by more than 10% of bad pixels in any aperture
                                       # 2: the object has been deblended
                                       # 4: at least one object pixel is saturated

        -BoundarySIZE [30]             # Restrict SExtractor Output Photometry Catalog by Dropping Sources at Boundary 
                                       # NOTE: This would help to avoid selecting sources too close to image boundary. 

        # > Configurations for Source-Selction
        #
        # Remarks on two modes 
        #   [HOUGH-AUTO] MODE: Source-Selection based on SExtractor & Hough Transformation, following Hu, et al. (2022).
        #   [SEMI-AUTO] MODE:  Source-Selection directly make use of a prior-selected source list.
        #

        -XY_PriorSelect [None]         # a Numpy array of pixels coordinates, with shape (N, 2) (e.g., [[x0, y0], [x1, y1], ...])
                                       # this allows sfft to us a prior source selection to solve the subtraction.
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [SEMI-AUTO] MODE

        -Hough_MINFR [0.1]             # The lower bound of FLUX_RATIO for line feature detection using Hough transformation.
                                       # Setting a proper lower bound can avoid to detect some line features by chance,
                                       # which are not contributed from point sources but resides in the small-FLUX_RATIO region.
                                       # NOTE: Recommended values of Hough_MINFR: 0.1 ~ 1.0
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE

        -Hough_PeakClip [0.7]          # It determines the lower bound of the sensitivity of the line feature detection.
                                       # NOTE: When the point-source-belt is not very pronounced (e.g., in galaxy dominated fields),
                                       #       one may consider to reduce the parameter from default 0.7 to, says, ~ 0.4.
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE
    
        -BeltHW [0.2]                  # The half-width of point-source-belt detected by Hough Transformation.
                                       # Remarks: if you want to tune this parameter, it is helpful to draw 
                                       #          a figure of MAG_AUTO against FLUX_RADIUS.
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE :::: determine point-source-belt

        -PointSource_MINELLIP [0.3]    # An additiona Restriction on ELLIPTICITY (ELLIPTICITY < PointSource_MINELLIP) 
                                       # for point sources.
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE :::: determine point-sources

        -MatchTol [None]               # Given separation tolerance (pix) for source matching 
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE :::: Cross-Match between REF & SCI
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [SEMI-AUTO] MODE :::: Cross-Match between REF & SCI AND
                                       #       Cross-Match between the prior selection and mean image coordinates of matched REF-SCI sources.

        -MatchTolFactor [3.0]          # The separation tolerance (pix) for source matching calculated by FWHM,
                                       # MatchTol = np.sqrt((FWHM_REF/MatchTolFactor)**2 + (FWHM_SCI/MatchTolFactor)**2)
                                       # @ Given precise WCS, one can use a high MatchTolFactor ~3.0
                                       # @ For very sparse fields where WCS can be inaccurate, 
                                       #   one can loosen the tolerance with a low MatchTolFactor ~1.0
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE :::: Cross-Match between REF & SCI
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [SEMI-AUTO] MODE :::: Cross-Match between REF & SCI AND
                                       #       Cross-Match between the prior selection and mean image coordinates of matched REF-SCI sources.

        -COARSE_VAR_REJECTION [True]   # Activate Coarse Variable Rejection (CVREJ) or not.
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE 

        -CVREJ_MAGD_THRESH [0.12]      # CVREJ kicks out the obvious variables by the difference of 
                                       # instrument magnitudes (MAG_AUTO) measured on reference and science, i.e., 
                                       # MAG_AUTO_SCI - MAG_AUTO_REF. A source with difference highly deviated from
                                       # the median level of the field stars will be rejected from the source selection.
                                       # -CVREJ_MAGD_THRESH is the deviation magnitude threshold. 
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE 
        
        -ELABO_VAR_REJECTION [True]    # WARNING: EVREJ REQUIRES CORRECT GAIN IN FITS HEADER!
                                       # Activate Elaborate Variable Rejection (EVREJ) or not.
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE 

        -EVREJ_RATIO_THREH [5.0]       # EVREJ kicks out the variables by the photometric uncertainties
                                       # (SExtractor FLUXERR_AUTO) measured on reference and science.
                                       # The flux change of a stationary object from reference to science 
                                       # is a predictable probability ditribution. EVREJ will reject the 
                                       # -EVREJ_RATIO_THREH * SIGMA outliers of the probability distribution.
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE 

        -EVREJ_SAFE_MAGDEV [0.04]      # A protection to avoid EVREJ overkilling. EVREJ would not reject
                                       # a source if the difference of instrument magnitudes is deviated
                                       # from the median level within -EVREJ_SAFE_MAGDEV magnitude.
                                       # NOTE: ONLY WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE 
                                       #
                                       # @ Why does EVREJ overkill?
                                       # i) The calculated flux change is entangled with the error of 
                                       #    the constant photometric scaling used by EVREJ.
                                       # ii) SExtractor FLUXERR can be in accurate, especially at the bright end.
                                       # see more details in sfft.Auto_SparsePrep.HoughAutoMask

        -StarExt_iter [4]              # Our image mask is determined by the SExtractor check image SEGMENTATION 
                                       # of the selected sources. note that some pixels (e.g., outskirt region of a galaxy) 
                                       # harbouring signal may be not SExtractor-detectable due to the nature of 
                                       # the thresholding-based detection method (see NoiseChisel paper for more details). 
                                       # we want to include the missing light at outskirt region to contribute to
                                       # parameter-solving process, then a simple mask dilation is introduced.
                                       # -StarExt_iter means the iteration times of the dilation process.
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE :::: mask dilation
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [SEMI-AUTO] MODE :::: mask dilation

        -XY_PriorBan [None]            # a Numpy array of pixels coordinates, with shape (N, 2) (e.g., [[x0, y0], [x1, y1], ...])
                                       # this allows us to feed the prior knowledge about the varibility cross the field.
                                       # if you already get a list of variables (transients) and would like SFFT not to select
                                       # them to solve the subtraction, you can tell SFFT their coordinates through -XY_PriorBan.
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [HOUGH-AUTO] MODE :::: mask refinement
                                       # NOTE: IT WORKS FOR Auto-Sparse-Prep [SEMI-AUTO] MODE :::: mask refinement

        # ----------------------------- SFFT Subtraction --------------------------------- #

        -ForceConv ['AUTO']         # it determines which image will be convolved, can be 'REF', 'SCI' and 'AUTO'.
                                    # -ForceConv = 'AUTO' means SFFT will determine the convolution direction according to 
                                    # FWHM_SCI and FWHM_REF: the image with better seeing will be convolved to avoid deconvolution.

        -GKerHW [None]              # the given kernel half-width, None means the kernel size will be 
                                    # automatically determined by -KerHWRatio (to be seeing-related). 

        -KerHWRatio [2.0]           # the ratio between FWHM and the kernel half-width
                                    # KerHW = int(KerHWRatio * Max(FWHM_REF, FWHM_SCI))

        -KerHWLimit [(2, 20)]       # the lower & upper bounds for kernel half-width 
                                    # KerHW is updated as np.clip(KerHW, KerHWLimit[0], KerHWLimit[1]) 
                                    # Remarks: this is useful for a survey since it can constrain the peak GPU memory usage.

        -KerPolyOrder [2]           # Polynomial degree of kernel spatial variation, can be [0,1,2,3].

        -BGPolyOrder [0]            # Polynomial degree of differential-background spatial variation, can be [0,1,2,3].
                                    # NOTE: this argument is trivial for Sparse-Flavor SFFT as input images have been sky subtracted.
                                    #       simply use a flat differential background (it will very close to 0 in the sfft solution). 

        -ConstPhotRatio [True]      # Constant photometric ratio between images? can be True or False
                                    # ConstPhotRatio = True: the sum of convolution kernel is restricted 
                                    #   to be a constant across the field. 
                                    # ConstPhotRatio = False: the flux scaling between images is modeled
                                    #   by a polynomial with degree -KerPolyOrder.

        -MaskSatContam [False]      # Mask saturation-contaminated regions on difference image ? can be True or False
                                    # NOTE the pixels enclosed in the regions are replaced by NaN.

        # ----------------------------- Post Subtraction --------------------------------- #

        -PostAnomalyCheck [False]   # WARNING: PAC REQUIRES CORRECT GAIN IN FITS HEADER!
                                    # Post Anomaly Check (PAC) is to find the missing variables in the source selection 
                                    # on the difference image. Like EVREJ, it depends on the photometric uncertainties 
                                    # given by SExtractor FLUXERR_AUTO of reference and science image.
                                    # As image subtraction can get a more accurate photometric scaling between reference 
                                    # and science than that in EVREJ, PA is a even more 'elaborate' way to identify variables.
                                    # NOTE: one can make use of the Post-Anomalies as the Prior-Ban-Sources 
                                    #       to refine the subtraction (run second-time subtraction).
        
        -PAC_RATIO_THRESH [5.0]     # PAC will identify the -PAC_RATIO_THRESH * SIGMA outliers of the 
                                    # probability distribution as missing variables.
        
        # ----------------------------- Input & Output --------------------------------- #

        -FITS_REF []                # File path of input reference image

        -FITS_SCI []                # File path of input science image

        -FITS_DIFF [None]           # File path of output difference image

        -FITS_Solution [None]       # File path of the solution of the linear system 
                                    # it is an array of (..., a_ijab, ... b_pq, ...)

        # ----------------------------- Miscellaneous --------------------------------- #
        
        -VERBOSE_LEVEL [2]          # The level of verbosity, can be [0, 1, 2]
                                    # 0/1/2: QUIET/NORMAL/FULL mode

        # Important Notice:
        #
        # a): if reference is convolved in SFFT, then DIFF = SCI - Convolved_REF.
        #     [difference image is expected to have PSF & flux zero-point consistent with science image]
        #     e.g., -ForceConv='REF' or -ForceConv='AUTO' when reference has better seeing.
        #
        # b): if science is convolved in SFFT, then DIFF = Convolved_SCI - REF
        #     [difference image is expected to have PSF & flux zero-point consistent with reference image]
        #     e.g., -ForceConv='SCI' or -ForceConv='AUTO' when science has better seeing.
        #
        # Remarks: this convention is to guarantee that a transient emerge on science image 
        #          always shows itself as a positive signal on the difference images.

        """
        
        # * Perform Auto Sparse-Prep
        if VERBOSE_LEVEL in [2]:
            warnings.warn('\nMeLOn REMINDER: Input images for sparse-flavor sfft should be SKY-SUBTRACTED!')
        
        _ASP = Auto_SparsePrep(FITS_REF=FITS_REF, FITS_SCI=FITS_SCI, GAIN_KEY=GAIN_KEY, SATUR_KEY=SATUR_KEY, \
            BACK_TYPE=BACK_TYPE, BACK_VALUE=BACK_VALUE, BACK_SIZE=BACK_SIZE, BACK_FILTERSIZE=BACK_FILTERSIZE, \
            DETECT_THRESH=DETECT_THRESH, ANALYSIS_THRESH=ANALYSIS_THRESH, DETECT_MINAREA=DETECT_MINAREA, \
            DETECT_MAXAREA=DETECT_MAXAREA, DEBLEND_MINCONT=DEBLEND_MINCONT, BACKPHOTO_TYPE=BACKPHOTO_TYPE, \
            ONLY_FLAGS=ONLY_FLAGS, BoundarySIZE=BoundarySIZE, VERBOSE_LEVEL=VERBOSE_LEVEL)

        if XY_PriorSelect is None:
            IMAGE_MASK_METHOD = 'HOUGH-AUTO'
            if VERBOSE_LEVEL in [0, 1, 2]:
                print('MeLOn CheckPoint: TRIGGER Sparse-Flavor Auto Preprocessing [%s] MODE!' %IMAGE_MASK_METHOD)

            SFFTPrepDict = _ASP.HoughAutoMask(Hough_MINFR=Hough_MINFR, Hough_PeakClip=Hough_PeakClip, \
                BeltHW=BeltHW, PointSource_MINELLIP=PointSource_MINELLIP, MatchTol=MatchTol, MatchTolFactor=MatchTolFactor, \
                COARSE_VAR_REJECTION=COARSE_VAR_REJECTION, CVREJ_MAGD_THRESH=CVREJ_MAGD_THRESH, \
                ELABO_VAR_REJECTION=ELABO_VAR_REJECTION, EVREJ_RATIO_THREH=EVREJ_RATIO_THREH, \
                EVREJ_SAFE_MAGDEV=EVREJ_SAFE_MAGDEV, StarExt_iter=StarExt_iter, XY_PriorBan=XY_PriorBan)
        else:
            IMAGE_MASK_METHOD = 'SEMI-AUTO'
            if VERBOSE_LEVEL in [0, 1, 2]:
                print('MeLOn CheckPoint: TRIGGER Sparse-Flavor Auto Preprocessing [%s] MODE!' %IMAGE_MASK_METHOD)
            
            SFFTPrepDict = _ASP.SemiAutoMask(XY_PriorSelect=XY_PriorSelect, MatchTol=MatchTol, \
                MatchTolFactor=MatchTolFactor, StarExt_iter=StarExt_iter, XY_PriorBan=XY_PriorBan)

        # * Determine ConvdSide & KerHW
        FWHM_REF = SFFTPrepDict['FWHM_REF']
        FWHM_SCI = SFFTPrepDict['FWHM_SCI']

        assert ForceConv in ['AUTO', 'REF', 'SCI']
        if ForceConv == 'AUTO':
            if FWHM_SCI >= FWHM_REF: ConvdSide = 'REF'
            else: ConvdSide = 'SCI'
        else: ConvdSide = ForceConv

        if GKerHW is None:
            FWHM_La = np.max([FWHM_REF, FWHM_SCI])
            KerHW = int(np.clip(KerHWRatio * FWHM_La, KerHWLimit[0], KerHWLimit[1]))
        else: KerHW = GKerHW

        # * Choose GPU device for Cupy backend
        if BACKEND_4SUBTRACT == 'Cupy':
            import cupy as cp
            device = cp.cuda.Device(int(CUDA_DEVICE_4SUBTRACT))
            device.use()
        
        # * Compile Functions in SFFT Subtraction
        PixA_REF = SFFTPrepDict['PixA_REF']
        PixA_SCI = SFFTPrepDict['PixA_SCI']

        if VERBOSE_LEVEL in [0, 1, 2]:
            print('MeLOn CheckPoint: TRIGGER Function Compilations of SFFT-SUBTRACTION!')

        Tcomp_start = time.time()
        SFFTConfig = SingleSFFTConfigure.SSC(NX=PixA_REF.shape[0], NY=PixA_REF.shape[1], KerHW=KerHW, \
            KerPolyOrder=KerPolyOrder, BGPolyOrder=BGPolyOrder, ConstPhotRatio=ConstPhotRatio, \
            BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, \
            VERBOSE_LEVEL=VERBOSE_LEVEL)
        
        if VERBOSE_LEVEL in [1, 2]:
            _message = 'Function Compilations of SFFT-SUBTRACTION '
            _message += 'TAKES [%.3f s]!' %(time.time() - Tcomp_start)
            print('\nMeLOn Report: %s' %_message)
        
        # * Perform SFFT Subtraction
        SatMask_REF = SFFTPrepDict['REF-SAT-Mask']
        SatMask_SCI = SFFTPrepDict['SCI-SAT-Mask']
        NaNmask_U = SFFTPrepDict['Union-NaN-Mask']
        PixA_mREF = SFFTPrepDict['PixA_mREF']
        PixA_mSCI = SFFTPrepDict['PixA_mSCI']

        if ConvdSide == 'REF':
            PixA_mI, PixA_mJ = PixA_mREF, PixA_mSCI
            if NaNmask_U is not None:
                PixA_I, PixA_J = PixA_REF.copy(), PixA_SCI.copy()
                PixA_I[NaNmask_U] = PixA_mI[NaNmask_U]
                PixA_J[NaNmask_U] = PixA_mJ[NaNmask_U]
            else: PixA_I, PixA_J = PixA_REF, PixA_SCI
            if MaskSatContam: 
                ContamMask_I = SatMask_REF
                ContamMask_J = SatMask_SCI
            else: ContamMask_I = None

        if ConvdSide == 'SCI':
            PixA_mI, PixA_mJ = PixA_mSCI, PixA_mREF
            if NaNmask_U is not None:
                PixA_I, PixA_J = PixA_SCI.copy(), PixA_REF.copy()
                PixA_I[NaNmask_U] = PixA_mI[NaNmask_U]
                PixA_J[NaNmask_U] = PixA_mJ[NaNmask_U]
            else: PixA_I, PixA_J = PixA_SCI, PixA_REF
            if MaskSatContam: 
                ContamMask_I = SatMask_SCI
                ContamMask_J = SatMask_REF
            else: ContamMask_I = None

        if VERBOSE_LEVEL in [0, 1, 2]:
            print('MeLOn CheckPoint: TRIGGER SFFT-SUBTRACTION!')

        Tsub_start = time.time()
        _tmp = GeneralSFFTSubtract.GSS(PixA_I=PixA_I, PixA_J=PixA_J, PixA_mI=PixA_mI, PixA_mJ=PixA_mJ, \
            SFFTConfig=SFFTConfig, ContamMask_I=ContamMask_I, BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, \
            NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, VERBOSE_LEVEL=VERBOSE_LEVEL)
        
        Solution, PixA_DIFF, ContamMask_CI = _tmp
        if VERBOSE_LEVEL in [1, 2]:
            _message = 'SFFT-SUBTRACTION TAKES [%.3f s]!' %(time.time() - Tsub_start)
            print('\nMeLOn Report: %s' %_message)
        
        # ** adjust the sign of difference image 
        #    NOTE: Our convention is to make the transients on SCI always show themselves as positive signal on DIFF
        #    (a) when REF is convolved, DIFF = SCI - Conv(REF)
        #    (b) when SCI is convolved, DIFF = Conv(SCI) - REF

        if ConvdSide == 'SCI':
            PixA_DIFF = -PixA_DIFF

        if VERBOSE_LEVEL in [1, 2]:
            if ConvdSide == 'REF':
                _message = 'Reference Image is Convolved in SFFT-SUBTRACTION [DIFF = SCI - Conv(REF)]!'
                print('MeLOn CheckPoint: %s' %_message)

            if ConvdSide == 'SCI':
                _message = 'Science Image is Convolved in SFFT-SUBTRACTION [DIFF = Conv(SCI) - REF]!'
                print('MeLOn CheckPoint: %s' %_message)

        # ** estimate the flux scaling through the convolution of image subtraction
        #    NOTE: if photometric ratio is not constant (ConstPhotRatio=False), we measure of a grid
        #          of coordinates to estimate the flux scaling and its fluctuation (polynomial form).
        #    NOTE: here we set the tile-size of the grid about 64 x 64 pix, but meanwhile, 
        #          we also require the tiles should no less than 6 along each axis.

        N0, N1 = SFFTConfig[0]['N0'], SFFTConfig[0]['N1']
        L0, L1 = SFFTConfig[0]['L0'], SFFTConfig[0]['L1']
        DK, Fpq = SFFTConfig[0]['DK'], SFFTConfig[0]['Fpq']

        if ConstPhotRatio:
            SFFT_FSCAL_NSAMP = 1
            XY_q = np.array([[N0/2.0, N1/2.0]]) + 0.5
            RFS = Realize_FluxScaling(XY_q=XY_q)
            SFFT_FSCAL_q = RFS.FromArray(Solution=Solution, N0=N0, N1=N1, L0=L0, L1=L1, DK=DK, Fpq=Fpq)
            SFFT_FSCAL_MEAN, SFFT_FSCAL_SIG = SFFT_FSCAL_q[0], 0.0
        
        if not ConstPhotRatio:
            TILESIZE_X, TILESIZE_Y = 64, 64    # FIXME emperical/arbitrary values
            NTILE_X = np.max([round(N0/TILESIZE_X), 6])
            NTILE_Y = np.max([round(N1/TILESIZE_Y), 6])
            GX = np.linspace(0.5, N0+0.5, NTILE_X+1)
            GY = np.linspace(0.5, N1+0.5, NTILE_Y+1)
            YY, XX = np.meshgrid(GY, GX)
            XY_q = np.array([XX.flatten(), YY.flatten()]).T
            SFFT_FSCAL_NSAMP = XY_q.shape[0]
            
            RFS = Realize_FluxScaling(XY_q=XY_q)
            SFFT_FSCAL_q = RFS.FromArray(Solution=Solution, N0=N0, N1=N1, L0=L0, L1=L1, DK=DK, Fpq=Fpq)
            SFFT_FSCAL_MEAN, SFFT_FSCAL_SIG = np.mean(SFFT_FSCAL_q), np.std(SFFT_FSCAL_q)

        PHOT_FSCAL = 10**(SFFTPrepDict['MAG_OFFSET']/-2.5)  # FLUX_SCI/FLUX_REF
        if ConvdSide == 'SCI': PHOT_FSCAL = 1.0/PHOT_FSCAL

        if VERBOSE_LEVEL in [1, 2]:
            _message = 'The Flux Scaling through the Convolution of SFFT-SUBTRACTION '
            _message += '[%.6f +/- %.6f] from [%d] positions!\n' %(SFFT_FSCAL_MEAN, SFFT_FSCAL_SIG, SFFT_FSCAL_NSAMP)
            _message += 'P.S. The approximated Flux Scaling from Photometry [%.6f].' %PHOT_FSCAL
            print('MeLOn CheckPoint: %s' %_message)
        
        # ** run post anomaly check (PAC)
        if PostAnomalyCheck:

            """
            # Remarks on the Post Anomaly Check (PAC)
            # [1] One may notice that Elaborate Variable Rejection (EVREJ) also use SExtractor 
            #     photometric errors to identify variables. However, PAC should be more accurate than EVREJ.
            #     NOTE: Bright transients (compared with its host) can be also identified by PAC.
            #
            # [2] distribution mean: image subtraction is expected to have better accuracy on the determination 
            #     of the photometric scaling, compared with the constant MAG_OFFSET in EVREJ. As a result,
            #     the flux change counted on the difference image is likely more 'real' than that in EVREJ.
            #
            # [3] distribution variance: SExtractor FLUXERR_AUTO can be inaccurate, and the convolution effect
            #     on the photometric errors has been simplified as multiplying an average flux scaling on an image.
            #
            """

            if VERBOSE_LEVEL in [2]:
                warnings.warn('\nMeLOn REMINDER: Post-Anomaly Check requires CORRECT GAIN in FITS HEADER!')

            AstSEx_SS = SFFTPrepDict['SExCatalog-SubSource']
            SFFTLmap = SFFTPrepDict['SFFT-LabelMap']
            
            # ** Only consider the Non-Prior-Banned SubSources
            if 'MASK_PriorBan' in AstSEx_SS.colnames:
                nPBMASK_SS = ~np.array(AstSEx_SS['MASK_PriorBan'])
                AstSEx_vSS = AstSEx_SS[nPBMASK_SS]
            else: AstSEx_vSS = AstSEx_SS
            
            # ** Estimate expected variance of Non-Prior-Banned SubSources on the difference
            FLUXERR_vSSr = np.array(AstSEx_vSS['FLUXERR_AUTO_REF'])
            FLUXERR_vSSs = np.array(AstSEx_vSS['FLUXERR_AUTO_SCI'])

            if ConvdSide == 'REF':
                sFLUXERR_vSSr = FLUXERR_vSSr * SFFT_FSCAL_MEAN
                ExpDVAR_vSS = sFLUXERR_vSSr**2 + FLUXERR_vSSs**2

            if ConvdSide == 'SCI':
                sFLUXERR_vSSs = FLUXERR_vSSs * SFFT_FSCAL_MEAN
                ExpDVAR_vSS = FLUXERR_vSSr**2 + sFLUXERR_vSSs**2

            # ** Measure the ratios of Non-Prior-Banned SubSources on the difference for PAC
            SEGL_vSS = np.array(AstSEx_vSS['SEGLABEL']).astype(int)
            DFSUM_vSS = ndimage.labeled_comprehension(PixA_DIFF, SFFTLmap, SEGL_vSS, np.sum, float, 0.0)
            RATIO_vSS = DFSUM_vSS / np.clip(np.sqrt(ExpDVAR_vSS), a_min=1e-8, a_max=None)
            PAMASK_vSS = np.abs(RATIO_vSS) > PAC_RATIO_THRESH

            if VERBOSE_LEVEL in [1, 2]:
                _message = 'Identified [%d] PostAnomaly SubSources [> %.2f sigma] ' %(np.sum(PAMASK_vSS), PAC_RATIO_THRESH)
                _message += 'out of [%d] Non-Prior-Banned SubSources!\n' %(len(AstSEx_vSS))
                _message += 'P.S. there are [%d] Prior-Banned SubSources!' %(len(AstSEx_SS) - len(AstSEx_vSS))
                print('\nMeLOn CheckPoint: %s' %_message)
            
            # ** Record the results (decorate AstSEx_SS in SFFTPrepDict)
            if 'MASK_PriorBan' in AstSEx_SS.colnames:
                ExpDVAR_SS = np.nan * np.ones(len(AstSEx_SS))       # NOTE Prior-Ban is trivial NaN
                DFSUM_SS = np.nan * np.ones(len(AstSEx_SS))         # NOTE Prior-Ban is trivial NaN
                RATIO_SS = np.nan * np.ones(len(AstSEx_SS))         # NOTE Prior-Ban is trivial NaN
                PAMASK_SS = np.zeros(len(AstSEx_SS)).astype(bool)   # NOTE Prior-Ban is trivial False
                
                ExpDVAR_SS[nPBMASK_SS] = ExpDVAR_vSS
                DFSUM_SS[nPBMASK_SS] = DFSUM_vSS
                RATIO_SS[nPBMASK_SS] = RATIO_vSS
                PAMASK_SS[nPBMASK_SS] = PAMASK_vSS
            else: 
                ExpDVAR_SS = ExpDVAR_vSS
                DFSUM_SS = DFSUM_vSS
                RATIO_SS = RATIO_vSS
                PAMASK_SS = PAMASK_vSS

            AstSEx_SS.add_column(Column(ExpDVAR_SS, name='ExpDVAR_PostAnomaly'))
            AstSEx_SS.add_column(Column(DFSUM_SS, name='DFSUM_PostAnomaly'))
            AstSEx_SS.add_column(Column(RATIO_SS, name='RATIO_PostAnomaly'))
            AstSEx_SS.add_column(Column(PAMASK_SS, name='MASK_PostAnomaly'))
        
        # ** final tweaks on the difference image
        if NaNmask_U is not None:
            PixA_DIFF[NaNmask_U] = np.nan   # Mask Union-NaN regions
        
        if MaskSatContam:
            ContamMask_DIFF = np.logical_or(ContamMask_CI, ContamMask_J)
            PixA_DIFF[ContamMask_DIFF] = np.nan   # Mask Saturation-Contaminated regions
        
        # * Save difference image
        if FITS_DIFF is not None:

            """
            # Remarks on header of difference image
            # [1] In general, the FITS header of difference image would mostly be inherited from science image.
            #
            # [2] when science image is convolved, we turn to set GAIN_DIFF = GAIN_SCI / SFFT_FSCAL_MEAN (unit: e-/ADU)
            #     so that one can correctly convert ADU to e- for a transient appears on science image.
            #     WARNING: for a transient appears on reference image, GAIN_DIFF = GAIN_SCI is correct.
            #              we should keep in mind that GAIN_DIFF is not an absolute instrumental value.
            #     WARNING: one can only estimate the Poission noise from the science transient via GIAN_DIFF.
            #              the Poission noise from the background source (host galaxy) can enhance the 
            #              background noise at the position of the transient. photometry softwares which 
            #              only take background noise and transient Possion noise into account would tend 
            #              to overestimate the SNR of the transient.
            # 
            # [3] when science image is convolved, we turn to set SATURA_DIFF = SATURA_SCI * SFFT_FSCAL_MEAN         
            #     WARNING: it is still not a good idea to use SATURA_DIFF to identify the SATURATION regions
            #              on difference image. more appropriate way is masking the saturation contaminated 
            #              regions on difference image (MaskSatContam=True), or alternatively, leave them  
            #              alone and using AI stamp classifier to reject saturation-related bogus.
            #
            """

            _hdl = fits.open(FITS_SCI)
            _hdl[0].data[:, :] = PixA_DIFF.T

            _hdl[0].header['NAME_REF'] = (pa.basename(FITS_REF), 'MeLOn: SFFT')
            _hdl[0].header['NAME_SCI'] = (pa.basename(FITS_SCI), 'MeLOn: SFFT')
            _hdl[0].header['FWHM_REF'] = (FWHM_REF, 'MeLOn: SFFT')
            _hdl[0].header['FWHM_SCI'] = (FWHM_SCI, 'MeLOn: SFFT')
            _hdl[0].header['KERORDER'] = (KerPolyOrder, 'MeLOn: SFFT')
            _hdl[0].header['BGORDER'] = (BGPolyOrder, 'MeLOn: SFFT')
            _hdl[0].header['CPHOTR'] = (str(ConstPhotRatio), 'MeLOn: SFFT')
            _hdl[0].header['KERHW'] = (KerHW, 'MeLOn: SFFT')
            _hdl[0].header['CONVD'] = (ConvdSide, 'MeLOn: SFFT')

            if ConvdSide == 'SCI':
                GAIN_SCI = _hdl[0].header[GAIN_KEY]
                SATUR_SCI = _hdl[0].header[SATUR_KEY]
                GAIN_DIFF = GAIN_SCI / SFFT_FSCAL_MEAN
                SATUR_DIFF = SATUR_SCI * SFFT_FSCAL_MEAN

                _hdl[0].header[GAIN_KEY] = (GAIN_DIFF, 'MeLOn: SFFT')
                _hdl[0].header[SATUR_KEY] = (SATUR_DIFF, 'MeLOn: SFFT')

            _hdl.writeto(FITS_DIFF, overwrite=True)
            _hdl.close()
        
        # * Save solution array
        if FITS_Solution is not None:
            phdu = fits.PrimaryHDU()
            phdu.header['N0'] = (SFFTConfig[0]['N0'], 'MeLOn: SFFT')
            phdu.header['N1'] = (SFFTConfig[0]['N1'], 'MeLOn: SFFT')
            phdu.header['DK'] = (SFFTConfig[0]['DK'], 'MeLOn: SFFT')
            phdu.header['DB'] = (SFFTConfig[0]['DB'], 'MeLOn: SFFT')
            phdu.header['L0'] = (SFFTConfig[0]['L0'], 'MeLOn: SFFT')
            phdu.header['L1'] = (SFFTConfig[0]['L1'], 'MeLOn: SFFT')
            
            phdu.header['FIJ'] = (SFFTConfig[0]['Fij'], 'MeLOn: SFFT')
            phdu.header['FAB'] = (SFFTConfig[0]['Fab'], 'MeLOn: SFFT')
            phdu.header['FPQ'] = (SFFTConfig[0]['Fpq'], 'MeLOn: SFFT')
            phdu.header['FIJAB'] = (SFFTConfig[0]['Fijab'], 'MeLOn: SFFT')

            PixA_Solution = Solution.reshape((-1, 1))
            phdu.data = PixA_Solution.T
            fits.HDUList([phdu]).writeto(FITS_Solution, overwrite=True)

        return PixA_DIFF, SFFTPrepDict, Solution, SFFT_FSCAL_MEAN, SFFT_FSCAL_SIG
