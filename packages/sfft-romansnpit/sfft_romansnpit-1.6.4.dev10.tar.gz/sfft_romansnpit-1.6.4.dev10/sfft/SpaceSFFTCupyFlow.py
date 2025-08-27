# IMPORTS Standard
import cupy as cp
import numpy as np

# IMPORTS Internal
from sfft.PureCupyCustomizedPacket import PureCupy_Customized_Packet
from sfft.utils.PureCupyFFTKits import PureCupy_FFTKits
from sfft.utils.PatternRotationCalculator import PatternRotation_Calculator
from sfft.utils.PureCupyDeCorrelationCalculator import PureCupy_DeCorrelation_Calculator
from sfft.utils.ResampKits import Cupy_ZoomRotate
from sfft.utils.ResampKits import Cupy_Resampling
from sfft.utils.SkyLevelEstimator import SkyLevel_Estimator
from sfft.utils.SFFTSolutionReader import Realize_MatchingKernel

__last_update__ = "2025-06-17"
__author__ = "Lei Hu <leihu@andrew.cmu.edu>"

class SpaceSFFT_CupyFlow:
    """Run A Cupy WorkFlow for SFFT subtraction"""

    def __init__(self, hdr_target, hdr_object, 
                 target_skyrms, object_skyrms, 
                 PixA_target_GPU, PixA_object_GPU,
                 PixA_targetVar_GPU, PixA_objectVar_GPU,
                 PixA_target_DMASK_GPU, PixA_object_DMASK_GPU, 
                 PSF_target_GPU, PSF_object_GPU,
                 sci_is_target=True,
                 GKerHW=9, KerPolyOrder=2, BGPolyOrder=0, ConstPhotRatio=True, 
                 CUDA_DEVICE_4SUBTRACT='0', GAIN=1.0, RANDOM_SEED=10086):
        """Do things.

        Parameters
        ----------
           hdr_target: astropy header
              The target image has the coordinate system to which we are
              resampling.  This is that image's header.  SFFT will use the following keywords from the header:
                * All WCS keywords (including LONPOLE)
                * NAXIS1
                * NAXIS2

           hdr_object: astropy header
              Original (unresampled) header of the image to be resampled to match target.

           target_skyrms: float

           object_skyrms: float

           PixA_target_GPU: cupy array (float64)
              2d image data of target, indexed by x, y.  (Note that raw
              data read from fits files are indexed y, x; transpose to
              get this.)

           PixA_object_GPU: cupy array (float64)
              2d image data of original image, indexed by x, y.

           PixA_targetVar_GPU: cupy array (float64)
              2d image variance of original image, indexed by x, y.

           PixA_objectVar_GPU: cupy array (float64)
              2d image variance of original image, indexed by x, y. 

           PixA_target_DMASK_GPU: cupy array (bool)
              2d detection mask for target image
        
           PixA_object_DMASK_GPU: cupy array (bool)
              2d detection mask for unresampled object image

           PSF_target_GPU: cupy array (float64)
              2d PSF model; axis lengths must be odd.  center of PSF is
              center of center pixel.

           PSF_object_GPU: cupy array (float64)
              object PSF

           sci_is_target : bool
              If True, will subtract object - target.  If false, will subtract target - object.

           GKerHW: int
              Matching kernel half-width (full width is 2*GkerHW + 1 )
           
           KerPolyOrder: int
              Order of spatial variation in kernel

           BGPolyOrder: int
              Order of differential background 2d polynomial.  (Usually
              just leave this 0, we assume the image is sky subtracted.)

           ConstPhotRatio: bool
              Assume relative zeropoints of target and (resampled)
              object have no spatial variation.

           CUDA_DEVICE_4SUBTRACT: str, default '0'
              Which CUDA device to use.

           GAIN: float
              e-/ADU gain for both images.  (So, poisson noise, σ_adu = √(gain) * adu.)

           RANDOM_SEED: int default 10086
              Random seed to use to CR.resamp_projection_sip.  TODO :
              make it so that when this is None, a "real" random seed is
              generated.

        """

        assert PixA_target_GPU.flags['C_CONTIGUOUS']
        assert PixA_object_GPU.flags['C_CONTIGUOUS']
        
        assert PixA_target_DMASK_GPU.flags['C_CONTIGUOUS']
        assert PixA_object_DMASK_GPU.flags['C_CONTIGUOUS']
        
        assert PSF_target_GPU.flags['C_CONTIGUOUS']
        assert PSF_object_GPU.flags['C_CONTIGUOUS']

        self.hdr_target = hdr_target
        self.hdr_object = hdr_object

        self.target_skyrms = target_skyrms
        self.object_skyrms = object_skyrms

        self.PixA_target_GPU = PixA_target_GPU
        self.PixA_object_GPU = PixA_object_GPU

        if PixA_targetVar_GPU.dtype != cp.float64:
            PixA_targetVar_GPU = PixA_targetVar_GPU.astype(cp.float64)
        self.PixA_targetVar_GPU = PixA_targetVar_GPU
        if PixA_objectVar_GPU.dtype != cp.float64:
            PixA_objectVar_GPU = PixA_objectVar_GPU.astype(cp.float64)
        self.PixA_objectVar_GPU = PixA_objectVar_GPU

        if PixA_target_DMASK_GPU.dtype != cp.float64:
            PixA_target_DMASK_GPU = PixA_target_DMASK_GPU.astype(cp.float64)
        self.PixA_target_DMASK_GPU = PixA_target_DMASK_GPU
        if PixA_object_DMASK_GPU.dtype != cp.float64:
            PixA_object_DMASK_GPU = PixA_object_DMASK_GPU.astype(cp.float64)
        self.PixA_object_DMASK_GPU = PixA_object_DMASK_GPU

        self.PSF_target_GPU = PSF_target_GPU
        self.PSF_object_GPU = PSF_object_GPU

        self.sci_is_target = sci_is_target
        self.GKerHW = GKerHW
        self.KerPolyOrder = KerPolyOrder
        self.BGPolyOrder = BGPolyOrder
        self.ConstPhotRatio = ConstPhotRatio
        self.CUDA_DEVICE_4SUBTRACT = CUDA_DEVICE_4SUBTRACT
        self.GAIN = GAIN
        self.RANDOM_SEED = 10086


    def resampling_image_mask_psf( self ):
        # * step 0. run resampling for input object image, variance image, mask, and PSF
        CR = Cupy_Resampling(RESAMP_METHOD="BILINEAR", VERBOSE_LEVEL=1)
        XX_proj_GPU, YY_proj_GPU = CR.resamp_projection_sip(hdr_obj=self.hdr_object,
                                                            hdr_targ=self.hdr_target,
                                                            NSAMP=1024,
                                                            RANDOM_SEED=self.RANDOM_SEED)
        
        # check if projection completely outside of target image
        # TODO: this check is currently not smart...
        NTX = int(self.hdr_target["NAXIS1"])
        NTY = int(self.hdr_target["NAXIS2"])
        NPIX_INNER = cp.sum(cp.logical_and( cp.logical_and(XX_proj_GPU >= 0.5, XX_proj_GPU < NTX+0.5),
                                            cp.logical_and(YY_proj_GPU >= 0.5, YY_proj_GPU < NTY+0.5) ))
        assert NPIX_INNER > 0, "SFFT Error: Projection of object image is completely outside of target image!"

        # Object image:
        PixA_Eobj_GPU, EProjDict = CR.frame_extension(XX_proj_GPU=XX_proj_GPU,
                                                      YY_proj_GPU=YY_proj_GPU, 
                                                      PixA_obj_GPU=self.PixA_object_GPU,
                                                      PAD_FILL_VALUE=0.,
                                                      NAN_FILL_VALUE=0.)

        self.PixA_resamp_object_GPU = CR.resampling(PixA_Eobj_GPU=PixA_Eobj_GPU,
                                                    EProjDict=EProjDict,
                                                    USE_SHARED_MEMORY=False)

        # Variance image:
        PixA_EobjVar_GPU, EProjDict_Var = CR.frame_extension(XX_proj_GPU=XX_proj_GPU,
                                                             YY_proj_GPU=YY_proj_GPU, 
                                                             PixA_obj_GPU=self.PixA_objectVar_GPU,
                                                             PAD_FILL_VALUE=0.,
                                                             NAN_FILL_VALUE=0.)

        self.PixA_resamp_objectVar_GPU = CR.resampling(PixA_Eobj_GPU=PixA_EobjVar_GPU,
                                                       EProjDict=EProjDict,
                                                       USE_SHARED_MEMORY=False)

        # Mask:
        PixA_Eobj_GPU, EProjDict = CR.frame_extension(XX_proj_GPU=XX_proj_GPU,
                                                      YY_proj_GPU=YY_proj_GPU, 
                                                      PixA_obj_GPU=self.PixA_object_DMASK_GPU,
                                                      PAD_FILL_VALUE=0.,
                                                      NAN_FILL_VALUE=0.)

        del XX_proj_GPU
        del YY_proj_GPU
        
        self.PixA_resamp_object_DMASK_GPU = CR.resampling(PixA_Eobj_GPU=PixA_Eobj_GPU,
                                                          EProjDict=EProjDict,
                                                          USE_SHARED_MEMORY=False)
        self.BlankMask_GPU = self.PixA_resamp_object_GPU == 0.


        # PSF:
        PATTERN_ROTATE_ANGLE = PatternRotation_Calculator.PRC(hdr_obj=self.hdr_object, hdr_targ=self.hdr_target)

        self.PSF_resamp_object_GPU = Cupy_ZoomRotate.CZR(PixA_obj_GPU=self.PSF_object_GPU,
                                                         ZOOM_SCALE_X=1.,
                                                         ZOOM_SCALE_Y=1.,
                                                         OUTSIZE_PARIRY_X='UNCHANGED',
                                                         OUTSIZE_PARIRY_Y='UNCHANGED',
                                                         PATTERN_ROTATE_ANGLE=PATTERN_ROTATE_ANGLE,
                                                         RESAMP_METHOD='BILINEAR',
                                                         PAD_FILL_VALUE=0.,
                                                         NAN_FILL_VALUE=0.,
                                                         THREAD_PER_BLOCK=8,
                                                         USE_SHARED_MEMORY=False,
                                                         VERBOSE_LEVEL=2)

    def cross_convolution( self ):
        # * step 1. cross convolution
        self.PixA_Ctarget_GPU = PureCupy_FFTKits.FFT_CONVOLVE(PixA_Inp_GPU=self.PixA_target_GPU,
                                                              KERNEL_GPU=self.PSF_resamp_object_GPU, 
                                                              PAD_FILL_VALUE=0.,
                                                              NAN_FILL_VALUE=None,
                                                              NORMALIZE_KERNEL=True,
                                                              FORCE_OUTPUT_C_CONTIGUOUS=True,
                                                              FFT_BACKEND="Cupy")

        self.PixA_Cresamp_object_GPU = PureCupy_FFTKits.FFT_CONVOLVE(PixA_Inp_GPU=self.PixA_resamp_object_GPU,
                                                                     KERNEL_GPU=self.PSF_target_GPU,
                                                                     PAD_FILL_VALUE=0.,
                                                                     NAN_FILL_VALUE=None,
                                                                     NORMALIZE_KERNEL=True,
                                                                     FORCE_OUTPUT_C_CONTIGUOUS=True,
                                                                     FFT_BACKEND="Cupy")

    def sfft_subtraction( self ):
        # * step 2. sfft subtraction
        LYMASK_BKG_GPU = cp.logical_or(self.PixA_target_DMASK_GPU == 0, self.PixA_resamp_object_DMASK_GPU < 0.1)   # background-mask

        NaNmask_Ctarget_GPU = cp.isnan(self.PixA_Ctarget_GPU)
        NaNmask_Cresamp_object_GPU = cp.isnan(self.PixA_Cresamp_object_GPU)
        if NaNmask_Ctarget_GPU.any() or NaNmask_Cresamp_object_GPU.any():
            NaNmask_GPU = cp.logical_or(NaNmask_Ctarget_GPU, NaNmask_Cresamp_object_GPU)
            ZeroMask_GPU = cp.logical_or(NaNmask_GPU, LYMASK_BKG_GPU)
        else:
            ZeroMask_GPU = LYMASK_BKG_GPU

        del LYMASK_BKG_GPU
            
        PixA_mCtarget_GPU = self.PixA_Ctarget_GPU.copy()
        PixA_mCtarget_GPU[ZeroMask_GPU] = 0.

        PixA_mCresamp_object_GPU = self.PixA_Cresamp_object_GPU.copy()
        PixA_mCresamp_object_GPU[ZeroMask_GPU] = 0.

        del ZeroMask_GPU
        
        # trigger sfft subtraction
        if self.sci_is_target:
            PixA_REF_GPU = self.PixA_Cresamp_object_GPU
            PixA_SCI_GPU = self.PixA_Ctarget_GPU
            PixA_mREF_GPU = PixA_mCresamp_object_GPU
            PixA_mSCI_GPU = PixA_mCtarget_GPU
        else:
            PixA_REF_GPU = self.PixA_Ctarget_GPU
            PixA_SCI_GPU = self.PixA_Cresamp_object_GPU
            PixA_mREF_GPU = PixA_mCtarget_GPU
            PixA_mSCI_GPU = PixA_mCresamp_object_GPU
        
        self.Solution_GPU, self.PixA_DIFF_GPU = PureCupy_Customized_Packet.PCCP(
            PixA_REF_GPU=PixA_REF_GPU,
            PixA_SCI_GPU=PixA_SCI_GPU,
            PixA_mREF_GPU=PixA_mREF_GPU,
            PixA_mSCI_GPU=PixA_mSCI_GPU,
            ForceConv='REF' if self.sci_is_target else 'NEW',
            GKerHW=self.GKerHW,
            KerPolyOrder=self.KerPolyOrder,
            BGPolyOrder=self.BGPolyOrder,
            ConstPhotRatio=self.ConstPhotRatio, 
            CUDA_DEVICE_4SUBTRACT=self.CUDA_DEVICE_4SUBTRACT
        )
        self.PixA_DIFF_GPU[self.BlankMask_GPU] = 0.

    def find_decorrelation( self ):
        # * step 3. perform decorrelation in Fourier domain
        # extract matching kernel at the center
        N0, N1 = self.PixA_DIFF_GPU.shape
        L0, L1 = 2*self.GKerHW + 1, 2*self.GKerHW + 1
        DK = self.KerPolyOrder
        Fpq = int((self.BGPolyOrder+1)*(self.BGPolyOrder+2)/2)
        XY_q = np.array([[N0/2.+0.5, N1/2.+0.5]])

        self.Solution = cp.asnumpy(self.Solution_GPU)
        MATCH_KERNEL_GPU = cp.array(Realize_MatchingKernel(XY_q=XY_q).FromArray(
            Solution=self.Solution, N0=N0, N1=N1, L0=L0, L1=L1, DK=DK, Fpq=Fpq
        )[0], dtype=cp.float64)

        # NOTE -- assuming below that the resampled object image has the same
        #   skyrms as the original object image.  (This is ~OK.)
        self.FKDECO_GPU = PureCupy_DeCorrelation_Calculator.PCDC(NX_IMG=N0,
                                                                 NY_IMG=N1,
                                                                 KERNEL_GPU_JQueue=[self.PSF_target_GPU], 
                                                                 BKGSIG_JQueue=[self.object_skyrms],
                                                                 KERNEL_GPU_IQueue=[self.PSF_resamp_object_GPU],
                                                                 BKGSIG_IQueue=[self.target_skyrms], 
                                                                 MATCH_KERNEL_GPU=MATCH_KERNEL_GPU,
                                                                 REAL_OUTPUT=False,
                                                                 REAL_OUTPUT_SIZE=None, 
                                                                 NORMALIZE_OUTPUT=True,
                                                                 VERBOSE_LEVEL=2)


    def apply_decorrelation( self, img ):
        # do decorrelation

        padxl = 0
        padyl = 0
        padxh = 0
        padyh = 0
        # Implicitly assuming img is smaller here
        if img.shape != self.FKDECO_GPU.shape:
            padx = self.FKDECO_GPU.shape[0] - img.shape[0]
            padxl = padx // 2
            padxh = padx - padxl
            pady = self.FKDECO_GPU.shape[1] - img.shape[1]
            padyl = pady // 2
            padyh = pady - padyl
            img = cp.pad( img, ( (padxl, padxh), (padyl, padyh) ) )
            
        Fdecor = cp.fft.fft2( img )
        decorimg = cp.fft.ifft2( Fdecor * self.FKDECO_GPU ).real

        return decorimg[ padxl:(decorimg.shape[0]-padxh) , padyl:(decorimg.shape[1]-padyh) ]
        
        # FPixA_DIFF_GPU = cp.fft.fft2(self.PixA_DIFF_GPU)
        # self.PixA_DCDIFF_GPU = cp.fft.ifft2(FPixA_DIFF_GPU * FKDECO_GPU).real

    # def noise_decorrelation_snr_estimation( self, bkgsig ):
        # This function is both broken and possibly not necessary since we have the score image. 
        # * step 4. noise decorrelation & SNR estimation 
        # roughly estimate the SNR map for the decorrelated difference image
        # WARNING: the noise propagation is highly simplified.

        # Note: we ignored the background noise change by resampling
        # self.BKGSIG_resamp_object = self.hdr_object['BKG_SIG']
        # self.BKGSIG_target = self.hdr_target['BKG_SIG']

        # PixA_vartarget_GPU = cp.clip(self.PixA_target_GPU/GAIN, a_min=0.0, a_max=None) + self.BKGSIG_target**2
        # PixA_varresamp_object_GPU = cp.clip(self.PixA_resamp_object_GPU/GAIN, a_min=0.0, a_max=None) + self.BKGSIG_resamp_object**2
        # self.PixA_NDIFF_GPU = cp.sqrt(PixA_vartarget_GPU + PixA_varresamp_object_GPU)
        # self.PixA_DSNR_GPU = PixA_DCDIFF_GPU / PixA_NDIFF_GPU

        # return PixA_DIFF_GPU, PixA_DCDIFF_GPU, PixA_DSNR_GPU

    def create_score_image( self ):
        
        # retrieve the decorrelated PSF
        # Note: here we assume the same pixel size for PSF and imgaes.
        NX, NY = self.PixA_target_GPU.shape
        PSF_object_CSZ_GPU = PureCupy_FFTKits.KERNEL_CSZ(KERNEL_GPU=self.PSF_object_GPU, NX_IMG=NX, NY_IMG=NY)
        PSF_target_CSZ_GPU = PureCupy_FFTKits.KERNEL_CSZ(KERNEL_GPU=self.PSF_target_GPU, NX_IMG=NX, NY_IMG=NY)
        FPSF_dDIFF_GPU = cp.fft.fft2(PSF_object_CSZ_GPU) * cp.fft.fft2(PSF_target_CSZ_GPU) * self.FKDECO_GPU

        # apply the decorrelation on difference image again (redundant, a workaround) 
        FPixA_DIFF_GPU = cp.fft.fft2( self.PixA_DIFF_GPU )
        FPixA_dDIFF_GPU = FPixA_DIFF_GPU * self.FKDECO_GPU

        FPixA_SCORE_GPU = FPixA_dDIFF_GPU * cp.conj(FPSF_dDIFF_GPU)
        PixA_SCORE_GPU = cp.fft.ifft2(FPixA_SCORE_GPU).real

        # an ad-hoc correction to make score image has standrd Gaussian distribution at background
        skysig_SCORE = SkyLevel_Estimator.SLE(PixA_obj=cp.asnumpy(PixA_SCORE_GPU))[1]
        PixA_SCORE_GPU /= skysig_SCORE

        return PixA_SCORE_GPU

    def create_variance_image( self ):

        assert self.PixA_targetVar_GPU.flags['C_CONTIGUOUS']
        assert self.PixA_resamp_objectVar_GPU.flags['C_CONTIGUOUS']

        # calculate variance image for (un-decorrelated) difference image
        NX, NY = self.PixA_target_GPU.shape
        PSF_object_CSZ_GPU = PureCupy_FFTKits.KERNEL_CSZ(KERNEL_GPU=self.PSF_object_GPU, NX_IMG=NX, NY_IMG=NY)
        PSF_target_CSZ_GPU = PureCupy_FFTKits.KERNEL_CSZ(KERNEL_GPU=self.PSF_target_GPU, NX_IMG=NX, NY_IMG=NY)

        # Note: convolve a squared kernel on the variance image to get the variance of the convolved image
        # Note: let's skip the matching kernel here, as it is expected to be a minor compensation.
        FPixA_DIFFVar_GPU = cp.fft.fft2(self.PixA_resamp_objectVar_GPU) * cp.fft.fft2(PSF_target_CSZ_GPU ** 2) + \
            cp.fft.fft2(self.PixA_targetVar_GPU) * cp.fft.fft2(PSF_object_CSZ_GPU ** 2)
        
        FPixA_dDIFFVar_GPU = FPixA_DIFFVar_GPU * cp.fft.fft2(cp.fft.ifft2(self.FKDECO_GPU) ** 2)
        PixA_dDIFFVar_GPU = cp.fft.ifft2(FPixA_dDIFFVar_GPU).real
        
        return PixA_dDIFFVar_GPU

    # Do we need this?  We should just unreference the object
    def cleanup( self ):
        pass
        # TODO
        # del self.hdr_target
        # del self.hdr_object
        # del self.PixA_target_GPU
        # del self.PixA_object_GPU
        # del self.PixA_target_DMASK_GPU
        # del self.PixA_object_DMASK_GPU
        # del self.PSF_target_GPU
        # del self.PSF_object_GPU
        # del self.GKerHW
        # del self.KerPolyOrder
        # del self.BGPolyOrder
        # del self.ConstPhotRatio
        # del self.CUDA_DEVICE_4SUBTRACT
        # del self.GAIN
        # del self.which_convolve
        # del self.RANDOM_SEED
        # del self.PixA_resamp_object_GPU        
        # del self.PixA_resamp_object_DMASK_GPU
        # del self.BlankMask_GPU
        # del self.PSF_resamp_object_GPU
        # del self.PixA_Ctarget_GPU
        # del self.PixA_Cresamp_object_GPU
