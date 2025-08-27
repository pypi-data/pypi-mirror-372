import time
import math
import numpy as np
import os.path as pa
from scipy import signal
from astropy.io import fits
from scipy.interpolate import BSpline
from astropy.convolution import convolve, convolve_fft
from sfft.utils.meta.MultiProc import Multi_Proc
# version: Dec 01, 2023

# WARNING: THIS MODULE IS STILL BEING DEVELOPED AND LOT OF IMPROVEMENT NOT IMPLETEMENTED YET!
__author__ = "Lei Hu <leihu@andrew.cmu.edu>"
__version__ = "v2.0dev"

class SingleSFFTConfigure_Cupy:
    @staticmethod
    def SSCC(NX, NY, KerHW=8, KerSpType='Polynomial', KerSpDegree=2, KerIntKnotX=[], KerIntKnotY=[], \
        SEPARATE_SCALING=True, ScaSpType='Polynomial', ScaSpDegree=0, ScaIntKnotX=[], ScaIntKnotY=[], \
        BkgSpType='Polynomial', BkgSpDegree=2, BkgIntKnotX=[], BkgIntKnotY=[], \
        REGULARIZE_KERNEL=False, IGNORE_LAPLACIAN_KERCENT=True, XY_REGULARIZE=None, WEIGHT_REGULARIZE=None, \
        LAMBDA_REGULARIZE=1e-6, MAX_THREADS_PER_BLOCK=8, MINIMIZE_GPU_MEMORY_USAGE=False, VERBOSE_LEVEL=2):

        import cupy as cp

        N0, N1 = int(NX), int(NY)
        w0, w1 = int(KerHW), int(KerHW)

        SCALE = np.float64(1/(N0*N1))     # Scale of Image-Size
        SCALE_L = np.float64(1/SCALE)     # Reciprocal Scale of Image-Size

        # kernel spatial variation
        DK = int(KerSpDegree)
        assert DK >= 0
        assert KerSpType in ['Polynomial', 'B-Spline']
        if KerSpType == 'B-Spline' and DK == 0:
            assert len(KerIntKnotX) == 0  # otherwise, discontinuity
            assert len(KerIntKnotY) == 0  # otherwise, discontinuity
        
        # scaling spatial variation
        if SEPARATE_SCALING:
            DS = int(ScaSpDegree)
            assert DS >= 0
            assert ScaSpType in ['Polynomial', 'B-Spline']
            if ScaSpType == 'B-Spline' and DS == 0:
                assert len(ScaIntKnotX) == 0  # otherwise, discontinuity
                assert len(ScaIntKnotY) == 0  # otherwise, discontinuity

        # Remarks on SCALING_MODE
        # SEPARATE_SCALING & ScaSpDegree >>>      SCALING_MODE
        #        N         &     any     >>>       'ENTANGLED'
        #        Y         &      0      >>>   'SEPARATE-CONSTANT'
        #        Y         &     > 0     >>>   'SEPARATE-VARYING'

        SCALING_MODE = None
        if not SEPARATE_SCALING:
            SCALING_MODE = 'ENTANGLED'
        elif ScaSpDegree == 0:
            SCALING_MODE = 'SEPARATE-CONSTANT'
        else: SCALING_MODE = 'SEPARATE-VARYING'
        assert SCALING_MODE is not None

        if SCALING_MODE == 'SEPARATE-CONSTANT':
            assert KerSpDegree != 0   # otherwise, reduced to ENTANGLED

        if SCALING_MODE == 'SEPARATE-VARYING':
            # force to activate MINIMIZE_GPU_MEMORY_USAGE
            assert MINIMIZE_GPU_MEMORY_USAGE

            if KerSpType == 'Polynomial' and ScaSpType == 'Polynomial':
                assert ScaSpDegree != KerSpDegree   # otherwise, reduced to ENTANGLED
            
            if KerSpType == 'B-Spline' and ScaSpType == 'B-Spline':
                if np.all(KerIntKnotX == ScaIntKnotX) and np.all(KerIntKnotY == ScaIntKnotY):
                    assert ScaSpDegree != KerSpDegree   # otherwise, reduced to ENTANGLED
        
        # background spatial variation
        DB = int(BkgSpDegree)
        assert DB >= 0
        assert BkgSpType in ['Polynomial', 'B-Spline']
        if BkgSpType == 'B-Spline' and BkgSpDegree == 0:
            assert len(BkgIntKnotX) == 0  # otherwise, discontinuity
            assert len(BkgIntKnotY) == 0  # otherwise, discontinuity

        # NOTE input image should not has dramatically small size
        assert N0 > MAX_THREADS_PER_BLOCK and N1 > MAX_THREADS_PER_BLOCK

        if REGULARIZE_KERNEL:
            assert XY_REGULARIZE is not None
            assert len(XY_REGULARIZE.shape) == 2 and XY_REGULARIZE.shape[1] == 2

        if VERBOSE_LEVEL in [1, 2]:
            print('\n --//--//--//--//-- TRIGGER SFFT COMPILATION [Cupy] --//--//--//--//-- ')

            if KerSpType == 'Polynomial':
                print('\n ---//--- Polynomial Kernel | KerSpDegree %d | KerHW %d ---//---' %(KerSpDegree, KerHW))
                if not SEPARATE_SCALING:
                    print('\n ---//--- [ENTANGLED] Polynomial Scaling | KerSpDegree %d ---//---' %KerSpDegree)

            if KerSpType == 'B-Spline':
                print('\n ---//--- B-Spline Kernel | Internal Knots %d,%d | KerSpDegree %d | KerHW %d ---//---' \
                      %(len(KerIntKnotX), len(KerIntKnotY), KerSpDegree, KerHW))
                if not SEPARATE_SCALING: 
                    print('\n ---//--- [ENTANGLED] B-Spline Scaling | Internal Knots %d,%d | KerSpDegree %d ---//---' \
                          %(len(KerIntKnotX), len(KerIntKnotY), KerSpDegree))
            
            if SEPARATE_SCALING:
                if ScaSpType == 'Polynomial':
                    print('\n ---//--- [SEPARATE] Polynomial Scaling | ScaSpDegree %d ---//---' %ScaSpDegree)
                
                if ScaSpType == 'B-Spline':
                    print('\n ---//--- [SEPARATE] B-Spline Scaling | Internal Knots %d,%d | ScaSpDegree %d ---//---' \
                          %(len(ScaIntKnotX), len(ScaIntKnotY), ScaSpDegree))
            
            if BkgSpType == 'Polynomial':
                print('\n ---//--- Polynomial Background | BkgSpDegree %d ---//---' %BkgSpDegree)
            
            if BkgSpType == 'B-Spline':
                print('\n ---//--- B-Spline Background | Internal Knots %d,%d | BkgSpDegree %d ---//---' \
                    %(len(BkgIntKnotX), len(BkgIntKnotY), BkgSpDegree))

        SFFTParam_dict = {}
        SFFTParam_dict['KerHW'] = KerHW
        SFFTParam_dict['KerSpType'] = KerSpType
        SFFTParam_dict['KerSpDegree'] = KerSpDegree
        SFFTParam_dict['KerIntKnotX'] = KerIntKnotX
        SFFTParam_dict['KerIntKnotY'] = KerIntKnotY

        SFFTParam_dict['SEPARATE_SCALING'] = SEPARATE_SCALING
        if SEPARATE_SCALING:
            SFFTParam_dict['ScaSpType'] = ScaSpType
            SFFTParam_dict['ScaSpDegree'] = ScaSpDegree
            SFFTParam_dict['ScaIntKnotX'] = ScaIntKnotX
            SFFTParam_dict['ScaIntKnotY'] = ScaIntKnotY

        SFFTParam_dict['BkgSpType'] = BkgSpType
        SFFTParam_dict['BkgSpDegree'] = BkgSpDegree
        SFFTParam_dict['BkgIntKnotX'] = BkgIntKnotX
        SFFTParam_dict['BkgIntKnotY'] = BkgIntKnotY

        SFFTParam_dict['REGULARIZE_KERNEL'] = REGULARIZE_KERNEL
        SFFTParam_dict['IGNORE_LAPLACIAN_KERCENT'] = IGNORE_LAPLACIAN_KERCENT
        SFFTParam_dict['XY_REGULARIZE'] = XY_REGULARIZE
        SFFTParam_dict['WEIGHT_REGULARIZE'] = WEIGHT_REGULARIZE
        SFFTParam_dict['LAMBDA_REGULARIZE'] = LAMBDA_REGULARIZE

        SFFTParam_dict['MAX_THREADS_PER_BLOCK'] = MAX_THREADS_PER_BLOCK
        SFFTParam_dict['MINIMIZE_GPU_MEMORY_USAGE'] = MINIMIZE_GPU_MEMORY_USAGE
        
        # * Make a dictionary for SFFT parameters
        L0 = 2*w0+1                                       # matching-kernel XSize
        L1 = 2*w1+1                                       # matching-kernel YSize
        Fab = L0*L1                                       # dof for index ab

        if KerSpType == 'Polynomial':
            Fi, Fj = -1, -1                               # not independent, placeholder
            Fij = ((DK+1)*(DK+2))//2                      # dof for matching-kernel polynomial index ij 
        
        if KerSpType == 'B-Spline':
            Fi = len(KerIntKnotX) + KerSpDegree + 1       # dof for matching-kernel B-spline index i (control points/coefficients)
            Fj = len(KerIntKnotY) + KerSpDegree + 1       # dof for matching-kernel B-spline index j (control points/coefficients)
            Fij = Fi*Fj                                   # dof for matching-kernel B-spline index ij
        
        if BkgSpType == 'Polynomial':
            Fp, Fq = -1, -1                               # not independent, placeholder
            Fpq = ((DB+1)*(DB+2))//2                      # dof for diff-background polynomial index pq 
        
        if BkgSpType == 'B-Spline':
            Fp = len(BkgIntKnotX) + BkgSpDegree + 1       # dof for diff-background B-spline index p (control points/coefficients)
            Fq = len(BkgIntKnotY) + BkgSpDegree + 1       # dof for diff-background B-spline index q (control points/coefficients)  
            Fpq = Fp*Fq                                   # dof for diff-background B-spline index pq

        if SCALING_MODE == 'SEPARATE-VARYING':
            if ScaSpType == 'Polynomial':
                ScaFi, ScaFj = -1, -1                     # not independent, placeholder
                ScaFij = ((DS+1)*(DS+2))//2               # effective dof for scaling polynomial index ij
            
            if ScaSpType == 'B-Spline':
                ScaFi = len(ScaIntKnotX) + ScaSpDegree + 1    # dof for scaling B-spline index i (control points/coefficients)
                ScaFj = len(ScaIntKnotY) + ScaSpDegree + 1    # dof for scaling B-spline index j (control points/coefficients)
                ScaFij = ScaFi*ScaFj                          # effective dof for scaling B-spline index ij
            
            # Remarks on the scaling effective dof
            # I. current version not support scaling effective dof no higher than kernel variation.
            #    for simplicity, we use trivail zero basis as placeholder so that 
            #    the apparent dof of scaling and kernel are consistent.
            # II. ScaFij = Fij is allowed, e.g.m, B-Spline, same degree and 
            #     same number of internal knots but at different positions.

            assert ScaFij <= Fij
        
        Fijab = Fij*Fab                                   # Linear-System Major side-length
        FOMG, FGAM, FTHE = Fij**2, Fij*Fpq, Fij           # OMG / GAM / THE has shape (dof, N0, N1)
        FPSI, FPHI, FDEL = Fpq*Fij, Fpq**2, Fpq           # PSI / PHI / DEL has shape (dof, N0, N1)
        NEQ = Fij*Fab+Fpq                                 # Linear-System side-length
        
        NEQt = NEQ
        if SCALING_MODE == 'SEPARATE-CONSTANT':
            NEQt = NEQ-Fij+1                    # tweaked Linear-System side-length for constant scaling

        if SCALING_MODE == 'SEPARATE-VARYING':
            NEQt = NEQ-(Fij-ScaFij)             # tweaked Linear-System side-length for polynomial-varying scaling

        SFFTParam_dict['N0'] = N0               # a.k.a, NX
        SFFTParam_dict['N1'] = N1               # a.k.a, NY
        SFFTParam_dict['w0'] = w0               # a.k.a, KerHW
        SFFTParam_dict['w1'] = w1               # a.k.a, KerHW
        SFFTParam_dict['DK'] = DK               # a.k.a, KerSpDegree
        SFFTParam_dict['DB'] = DB               # a.k.a, BkgSpDegree
        if SEPARATE_SCALING: 
            SFFTParam_dict['DS'] = DS           # a.k.a, ScaSpDegree

        SFFTParam_dict['SCALE'] = SCALE
        SFFTParam_dict['SCALE_L'] = SCALE_L

        SFFTParam_dict['L0'] = L0
        SFFTParam_dict['L1'] = L1
        SFFTParam_dict['Fab'] = Fab
        SFFTParam_dict['Fi'] = Fi
        SFFTParam_dict['Fj'] = Fj
        SFFTParam_dict['Fij'] = Fij
        SFFTParam_dict['Fp'] = Fp
        SFFTParam_dict['Fq'] = Fq
        SFFTParam_dict['Fpq'] = Fpq

        if SCALING_MODE == 'SEPARATE-VARYING':
            SFFTParam_dict['ScaFi'] = ScaFi
            SFFTParam_dict['ScaFj'] = ScaFj
            SFFTParam_dict['ScaFij'] = ScaFij        
        SFFTParam_dict['Fijab'] = Fijab
        
        SFFTParam_dict['FOMG'] = FOMG
        SFFTParam_dict['FGAM'] = FGAM
        SFFTParam_dict['FTHE'] = FTHE
        SFFTParam_dict['FPSI'] = FPSI
        SFFTParam_dict['FPHI'] = FPHI
        SFFTParam_dict['FDEL'] = FDEL
        
        SFFTParam_dict['NEQ'] = NEQ
        SFFTParam_dict['NEQt'] = NEQt

        # * Load SFFT CUDA modules
        #   NOTE: Generally, a kernel function is defined without knowledge about Grid-Block-Thread Management.
        #         However, we need to know the size of threads per block if SharedMemory is called.

        SFFTModule_dict = {}
        # ************************************ Spatial Variation ************************************ #

        # <*****> produce spatial coordinate X/Y/oX/oY-map <*****> #
        _refdict = {'N0': N0, 'N1': N1}
        _funcstr = r"""
        extern "C" __global__ void kmain(int PixA_X_GPU[%(N0)s][%(N1)s], int PixA_Y_GPU[%(N0)s][%(N1)s], 
            double PixA_CX_GPU[%(N0)s][%(N1)s], double PixA_CY_GPU[%(N0)s][%(N1)s])
        {
            int ROW = blockIdx.x*blockDim.x+threadIdx.x;
            int COL = blockIdx.y*blockDim.y+threadIdx.y;
            
            int N0 = %(N0)s;
            int N1 = %(N1)s;
            
            if (ROW < N0 && COL < N1) {
                double cx = (ROW + 1.0) / N0;  
                double cy = (COL + 1.0) / N1;
                PixA_X_GPU[ROW][COL] = ROW;
                PixA_Y_GPU[ROW][COL] = COL;
                PixA_CX_GPU[ROW][COL] = cx;
                PixA_CY_GPU[ROW][COL] = cy;
            }
        }
        """
        _code = _funcstr % _refdict
        _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
        SFFTModule_dict['SpatialCoord'] = _module

        # <*****> produce Iij <*****> #
        if KerSpType == 'Polynomial':
            
            _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij}
            _funcstr = r"""
            extern "C" __global__ void kmain(int REF_ij_GPU[%(Fij)s][2],
                double PixA_CX_GPU[%(N0)s][%(N1)s], double PixA_CY_GPU[%(N0)s][%(N1)s],
                double PixA_I_GPU[%(N0)s][%(N1)s], double SPixA_Iij_GPU[%(Fij)s][%(N0)s][%(N1)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
            
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int Fij = %(Fij)s;
                
                if (ROW < N0 && COL < N1) {
                    for(int ij = 0; ij < Fij; ++ij) {
                        int i = REF_ij_GPU[ij][0];
                        int j = REF_ij_GPU[ij][1];
                        double poly = pow(PixA_CX_GPU[ROW][COL], i) * pow(PixA_CY_GPU[ROW][COL], j);
                        SPixA_Iij_GPU[ij][ROW][COL] = PixA_I_GPU[ROW][COL] * poly;
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['KerSpatial'] = _module
        
        if KerSpType == 'B-Spline':
            
            _refdict = {'N0': N0, 'N1': N1, 'Fi': Fi, 'Fj': Fj, 'Fij': Fij}
            _funcstr = r"""
            extern "C" __global__ void kmain(int REF_ij_GPU[%(Fij)s][2],
                double KerSplBasisX_GPU[%(Fi)s][%(N0)s], double KerSplBasisY_GPU[%(Fj)s][%(N1)s],
                double PixA_I_GPU[%(N0)s][%(N1)s], double SPixA_Iij_GPU[%(Fij)s][%(N0)s][%(N1)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
            
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int Fij = %(Fij)s;
                
                if (ROW < N0 && COL < N1) {
                    for(int ij = 0; ij < Fij; ++ij) {
                        int i = REF_ij_GPU[ij][0];
                        int j = REF_ij_GPU[ij][1];
                        double spl = KerSplBasisX_GPU[i][ROW] * KerSplBasisY_GPU[j][COL];
                        SPixA_Iij_GPU[ij][ROW][COL] = PixA_I_GPU[ROW][COL] * spl;
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['KerSpatial'] = _module
        
        if SCALING_MODE == 'SEPARATE-VARYING':

            if ScaSpType == 'Polynomial':

                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij}
                _funcstr = r"""
                extern "C" __global__ void kmain(int ScaREF_ij_GPU[%(Fij)s][2],
                    double PixA_CX_GPU[%(N0)s][%(N1)s], double PixA_CY_GPU[%(N0)s][%(N1)s],
                    double PixA_I_GPU[%(N0)s][%(N1)s], double ScaSPixA_Iij_GPU[%(Fij)s][%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    
                    if (ROW < N0 && COL < N1) {
                        for(int ij = 0; ij < Fij; ++ij) {
                            int i = ScaREF_ij_GPU[ij][0];
                            int j = ScaREF_ij_GPU[ij][1];

                            if (i >= 0 && j >= 0) {
                                double poly = pow(PixA_CX_GPU[ROW][COL], i) * pow(PixA_CY_GPU[ROW][COL], j);
                                ScaSPixA_Iij_GPU[ij][ROW][COL] = PixA_I_GPU[ROW][COL] * poly;
                            }

                            if (i == -1 || j == -1) {
                                ScaSPixA_Iij_GPU[ij][ROW][COL] = 0.0;
                            } 
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['ScaSpatial'] = _module

            if ScaSpType == 'B-Spline':

                _refdict = {'N0': N0, 'N1': N1, 'Fi': Fi, 'Fj': Fj, 'Fij': Fij}
                _funcstr = r"""
                extern "C" __global__ void kmain(int ScaREF_ij_GPU[%(Fij)s][2],
                    double ScaSplBasisX_GPU[%(Fi)s][%(N0)s], double ScaSplBasisY_GPU[%(Fj)s][%(N1)s],
                    double PixA_I_GPU[%(N0)s][%(N1)s], double ScaSPixA_Iij_GPU[%(Fij)s][%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    
                    if (ROW < N0 && COL < N1) {
                        for(int ij = 0; ij < Fij; ++ij) {
                            int i = ScaREF_ij_GPU[ij][0];
                            int j = ScaREF_ij_GPU[ij][1];
                            double spl = ScaSplBasisX_GPU[i][ROW] * ScaSplBasisY_GPU[j][COL];
                            ScaSPixA_Iij_GPU[ij][ROW][COL] = PixA_I_GPU[ROW][COL] * spl;
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['ScaSpatial'] = _module
        
        # <*****> produce Tpq <*****> #
        if BkgSpType == 'Polynomial':

            _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq}
            _funcstr = r"""
            extern "C" __global__ void kmain(int REF_pq_GPU[%(Fpq)s][2],
                double PixA_CX_GPU[%(N0)s][%(N1)s], double PixA_CY_GPU[%(N0)s][%(N1)s],
                double SPixA_Tpq_GPU[%(Fpq)s][%(N0)s][%(N1)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
            
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int Fpq = %(Fpq)s;
                
                if (ROW < N0 && COL < N1) {
                    for(int pq = 0; pq < Fpq; ++pq) {
                        int p = REF_pq_GPU[pq][0];
                        int q = REF_pq_GPU[pq][1];
                        double poly_bterm = pow(PixA_CX_GPU[ROW][COL], p) * pow(PixA_CY_GPU[ROW][COL], q);
                        SPixA_Tpq_GPU[pq][ROW][COL] = poly_bterm;
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['BkgSpatial'] = _module
        
        if BkgSpType == 'B-Spline':

            _refdict = {'N0': N0, 'N1': N1, 'Fp': Fp, 'Fq': Fq, 'Fpq': Fpq}
            _funcstr = r"""
            extern "C" __global__ void kmain(int REF_pq_GPU[%(Fpq)s][2],
                double BkgSplBasisX_GPU[%(Fp)s][%(N0)s], double BkgSplBasisY_GPU[%(Fq)s][%(N1)s],
                double SPixA_Tpq_GPU[%(Fpq)s][%(N0)s][%(N1)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
            
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int Fpq = %(Fpq)s;
                
                if (ROW < N0 && COL < N1) {
                    for(int pq = 0; pq < Fpq; ++pq) {
                        int p = REF_pq_GPU[pq][0];
                        int q = REF_pq_GPU[pq][1];
                        double spl_kterm = BkgSplBasisX_GPU[p][ROW] * BkgSplBasisY_GPU[q][COL];
                        SPixA_Tpq_GPU[pq][ROW][COL] = spl_kterm;
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['BkgSpatial'] = _module

        # ************************************ Constuct Linear System ************************************ #

        # <*****> OMEGA & GAMMA & PSI & PHI & THETA & DELTA <*****> #
        if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:

            if not MINIMIZE_GPU_MEMORY_USAGE:
                
                # ** Hadamard Product [OMEGA]
                # NOTE: As N0, N1 > MAX_THREADS_PER_BLOCK, here TpB == MAX_THREADS_PER_BLOCK
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FOMG': FOMG, 'TpB': MAX_THREADS_PER_BLOCK}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_iji0j0_GPU[%(FOMG)s][2],
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex HpOMG_GPU[%(FOMG)s][%(N0)s][%(N1)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int FOMG = %(FOMG)s;

                    __shared__ cuDoubleComplex ShSPixA_FIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int ij = 0; ij < Fij; ++ij){
                            ShSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y] = SPixA_FIij_GPU[ij][ROW][COL];
                        }
                    }

                    __shared__ cuDoubleComplex ShSPixA_CFIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int ij = 0; ij < Fij; ++ij){
                            ShSPixA_CFIij_GPU[ij][threadIdx.x][threadIdx.y] = SPixA_CFIij_GPU[ij][ROW][COL];
                        }
                    }
                    __syncthreads();

                    if (ROW < N0 && COL < N1) {
                        for(int i8j8ij = 0; i8j8ij < FOMG; ++i8j8ij){
                            
                            int i8j8 = SREF_iji0j0_GPU[i8j8ij][0];
                            int ij = SREF_iji0j0_GPU[i8j8ij][1];

                            HpOMG_GPU[i8j8ij][ROW][COL] = cuCmul(ShSPixA_FIij_GPU[i8j8][threadIdx.x][threadIdx.y], 
                                ShSPixA_CFIij_GPU[ij][threadIdx.x][threadIdx.y]);
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_OMG'] = _module

                # ** Fill Linear-System [OMEGA]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fab': Fab, 'Fijab': Fijab, 'FOMG': FOMG, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    double PreOMG_GPU[%(FOMG)s][%(N0)s][%(N1)s], double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fijab = %(Fijab)s;
                    
                    if (ROW < Fijab && COL < Fijab) {
                        
                        // INDEX Analysis
                        int i8j8 = SREF_ijab_GPU[ROW][0];
                        int a8b8 = SREF_ijab_GPU[ROW][1];
                        int ij = SREF_ijab_GPU[COL][0];
                        int ab = SREF_ijab_GPU[COL][1];

                        int a8 = REF_ab_GPU[a8b8][0];
                        int b8 = REF_ab_GPU[a8b8][1];
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        int idx = i8j8 * Fij + ij;

                        // Define Mod_N0(rho), Mod_N1(eps)
                        float tmp = 0.0;
                        tmp = fmod(float(a8), float(N0));
                        if (tmp < 0.0) {tmp += float(N0);}
                        int MODa8 = tmp;

                        tmp = fmod(float(b8), float(N1));
                        if (tmp < 0.0) {tmp += float(N1);}
                        int MODb8 = tmp;

                        tmp = fmod(float(-a), float(N0));
                        if (tmp < 0.0) {tmp += float(N0);}
                        int MOD_a = tmp;

                        tmp = fmod(float(-b), float(N1));
                        if (tmp < 0.0) {tmp += float(N1);}
                        int MOD_b = tmp;

                        tmp = fmod(float(a8-a), float(N0));
                        if (tmp < 0.0) {tmp += float(N0);}
                        int MODa8_a = tmp;

                        tmp = fmod(float(b8-b), float(N1));
                        if (tmp < 0.0) {tmp += float(N1);}
                        int MODb8_b = tmp;

                        // Fill Linear System [A-component]
                        if ((a8 != 0 || b8 != 0) && (a != 0 || b != 0)) {
                            LHMAT_GPU[ROW][COL] = - PreOMG_GPU[idx][MODa8][MODb8]
                                                - PreOMG_GPU[idx][MOD_a][MOD_b] 
                                                + PreOMG_GPU[idx][MODa8_a][MODb8_b] 
                                                + PreOMG_GPU[idx][0][0];
                        }

                        if ((a8 == 0 && b8 == 0) && (a != 0 || b != 0)) {
                            LHMAT_GPU[ROW][COL] = PreOMG_GPU[idx][MOD_a][MOD_b] - PreOMG_GPU[idx][0][0];
                        }

                        if ((a8 != 0 || b8 != 0) && (a == 0 && b == 0)) {
                            LHMAT_GPU[ROW][COL] = PreOMG_GPU[idx][MODa8][MODb8] - PreOMG_GPU[idx][0][0];
                        }

                        if ((a8 == 0 && b8 == 0) && (a == 0 && b == 0)) {
                            LHMAT_GPU[ROW][COL] = PreOMG_GPU[idx][0][0];
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_OMG'] = _module

                # ** Hadamard Product [GAMMA]
                # NOTE: As N0, N1 > MAX_THREADS_PER_BLOCK, here TpB == MAX_THREADS_PER_BLOCK
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FGAM': FGAM, 'TpB': MAX_THREADS_PER_BLOCK}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_ijpq_GPU[%(FGAM)s][2], 
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex HpGAM_GPU[%(FGAM)s][%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fpq = %(Fpq)s;
                    int FGAM = %(FGAM)s;
                    
                    __shared__ cuDoubleComplex ShSPixA_FIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int ij = 0; ij < Fij; ++ij){
                            ShSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y] = SPixA_FIij_GPU[ij][ROW][COL];
                        }
                    }

                    __shared__ cuDoubleComplex ShSPixA_CFTpq_GPU[%(Fpq)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int pq = 0; pq < Fpq; ++pq){
                            ShSPixA_CFTpq_GPU[pq][threadIdx.x][threadIdx.y] = SPixA_CFTpq_GPU[pq][ROW][COL];
                        }
                    }
                    __syncthreads();
                    
                    if (ROW < N0 && COL < N1) {        
                        for(int i8j8pq = 0; i8j8pq < FGAM; ++i8j8pq){

                            int i8j8 = SREF_ijpq_GPU[i8j8pq][0];
                            int pq = SREF_ijpq_GPU[i8j8pq][1];

                            HpGAM_GPU[i8j8pq][ROW][COL] = cuCmul(ShSPixA_FIij_GPU[i8j8][threadIdx.x][threadIdx.y], 
                                ShSPixA_CFTpq_GPU[pq][threadIdx.x][threadIdx.y]);
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_GAM'] = _module

                # ** Fill Linear-System [GAMMA]
                _refdict = {'N0': N0, 'N1': N1, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, 'FGAM': FGAM, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    double PreGAM_GPU[%(FGAM)s][%(N0)s][%(N1)s], double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;
                    
                    if (ROW < Fijab && COL < Fpq) {
                        
                        // INDEX Analysis
                        int i8j8 = SREF_ijab_GPU[ROW][0];
                        int a8b8 = SREF_ijab_GPU[ROW][1];
                        int pq = COL;

                        int a8 = REF_ab_GPU[a8b8][0];
                        int b8 = REF_ab_GPU[a8b8][1];
                        int idx = i8j8 * Fpq + pq;
                        int cCOL = Fijab + COL;              // add offset

                        // Define Mod_N0(rho), Mod_N1(eps)
                        float tmp = 0.0;
                        tmp = fmod(float(a8), float(N0));
                        if (tmp < 0.0) {tmp += float(N0);}
                        int MODa8 = tmp;

                        tmp = fmod(float(b8), float(N1));
                        if (tmp < 0.0) {tmp += float(N1);}
                        int MODb8 = tmp;

                        // Fill Linear System [B-component]
                        if (a8 != 0 || b8 != 0) {
                            LHMAT_GPU[ROW][cCOL] = PreGAM_GPU[idx][MODa8][MODb8] - PreGAM_GPU[idx][0][0];
                        }

                        if (a8 == 0 && b8 == 0) {
                            LHMAT_GPU[ROW][cCOL] = PreGAM_GPU[idx][0][0];
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_GAM'] = _module

                # ** Hadamard Product [PSI]
                # NOTE: As N0, N1 > MAX_THREADS_PER_BLOCK, here TpB == MAX_THREADS_PER_BLOCK
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FPSI': FPSI, 'TpB': MAX_THREADS_PER_BLOCK}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqij_GPU[%(FPSI)s][2],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex HpPSI_GPU[%(FPSI)s][%(N0)s][%(N1)s]) 
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int Fij = %(Fij)s;
                    int FPSI = %(FPSI)s;
                    
                    __shared__ cuDoubleComplex ShSPixA_FTpq_GPU[%(Fpq)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int pq = 0; pq < Fpq; ++pq){
                            ShSPixA_FTpq_GPU[pq][threadIdx.x][threadIdx.y] = SPixA_FTpq_GPU[pq][ROW][COL];
                        }
                    }

                    __shared__ cuDoubleComplex ShSPixA_CFIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int ij = 0; ij < Fij; ++ij){
                            ShSPixA_CFIij_GPU[ij][threadIdx.x][threadIdx.y] = SPixA_CFIij_GPU[ij][ROW][COL];
                        }
                    }
                    __syncthreads();

                    if (ROW < N0 && COL < N1) {
                        for(int p8q8ij = 0; p8q8ij < FPSI; ++p8q8ij){
                            
                            int p8q8 = SREF_pqij_GPU[p8q8ij][0];
                            int ij = SREF_pqij_GPU[p8q8ij][1];

                            HpPSI_GPU[p8q8ij][ROW][COL] = cuCmul(ShSPixA_FTpq_GPU[p8q8][threadIdx.x][threadIdx.y], 
                                ShSPixA_CFIij_GPU[ij][threadIdx.x][threadIdx.y]);
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PSI'] = _module

                # ** Fill Linear-System [PSI]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, 'FPSI': FPSI, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    double PrePSI_GPU[%(FPSI)s][%(N0)s][%(N1)s], double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;

                    if (ROW < Fpq && COL < Fijab) {

                        // INDEX Analysis
                        int cROW = Fijab + ROW;              // add offset
                        int p8q8 = ROW;
                        int ij = SREF_ijab_GPU[COL][0];
                        int ab = SREF_ijab_GPU[COL][1];
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        int idx = p8q8 * Fij + ij;

                        // Define Mod_N0(rho), Mod_N1(eps)
                        float tmp = 0.0;
                        tmp = fmod(float(-a), float(N0));
                        if (tmp < 0.0) {tmp += float(N0);}
                        int MOD_a = tmp;

                        tmp = fmod(float(-b), float(N1));
                        if (tmp < 0.0) {tmp += float(N1);}
                        int MOD_b = tmp;
                        
                        // Fill Linear System [B#-component]
                        if (a != 0 || b != 0) {
                            LHMAT_GPU[cROW][COL] = PrePSI_GPU[idx][MOD_a][MOD_b] - PrePSI_GPU[idx][0][0];
                        }

                        if (a == 0 && b == 0) {
                            LHMAT_GPU[cROW][COL] = PrePSI_GPU[idx][0][0];
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_PSI'] = _module

                # ** Hadamard Product [PHI]
                # NOTE: As N0, N1 > MAX_THREADS_PER_BLOCK, here TpB == MAX_THREADS_PER_BLOCK
                _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'FPHI': FPHI, 'TpB': MAX_THREADS_PER_BLOCK}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqp0q0_GPU[%(FPHI)s][2], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s],  
                    cuDoubleComplex HpPHI_GPU[%(FPHI)s][%(N0)s][%(N1)s]) 
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int FPHI = %(FPHI)s;

                    __shared__ cuDoubleComplex ShSPixA_FTpq_GPU[%(Fpq)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int pq = 0; pq < Fpq; ++pq){
                            ShSPixA_FTpq_GPU[pq][threadIdx.x][threadIdx.y] = SPixA_FTpq_GPU[pq][ROW][COL];
                        }
                    }

                    __shared__ cuDoubleComplex ShSPixA_CFTpq_GPU[%(Fpq)s][%(TpB)s][%(TpB)s];
                    if (ROW < N0 && COL < N1) {
                        for(int pq = 0; pq < Fpq; ++pq){
                            ShSPixA_CFTpq_GPU[pq][threadIdx.x][threadIdx.y] = SPixA_CFTpq_GPU[pq][ROW][COL];
                        }
                    }
                    __syncthreads();
                    
                    if (ROW < N0 && COL < N1) {
                        for(int p8q8pq = 0; p8q8pq < FPHI; ++p8q8pq){
                            
                            int p8q8 = SREF_pqp0q0_GPU[p8q8pq][0];
                            int pq = SREF_pqp0q0_GPU[p8q8pq][1];

                            HpPHI_GPU[p8q8pq][ROW][COL] = cuCmul(ShSPixA_FTpq_GPU[p8q8][threadIdx.x][threadIdx.y], 
                                ShSPixA_CFTpq_GPU[pq][threadIdx.x][threadIdx.y]);
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PHI'] = _module

                # ** Fill Linear-System [PHI]
                _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'Fijab': Fijab, 'FPHI': FPHI, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(double PrePHI_GPU[%(FPHI)s][%(N0)s][%(N1)s], 
                    double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;

                    if (ROW < Fpq && COL < Fpq) {
                        
                        // INDEX Analysis
                        int cROW = Fijab + ROW;              // add offset
                        int cCOL = Fijab + COL;              // add offset
                        
                        int p8q8 = ROW;
                        int pq = COL;
                        int idx = p8q8 * Fpq + pq;

                        // Fill Linear System [C-component]
                        LHMAT_GPU[cROW][cCOL] = PrePHI_GPU[idx][0][0];
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_PHI'] = _module

            if MINIMIZE_GPU_MEMORY_USAGE:

                # ** Hadamard Product [OMEGA]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FOMG': FOMG}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_iji0j0_GPU[%(FOMG)s][2],
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpOMG_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {
                        
                        int i8j8 = SREF_iji0j0_GPU[cIdx][0];
                        int ij = SREF_iji0j0_GPU[cIdx][1];

                        cHpOMG_GPU[ROW][COL] = cuCmul(SPixA_FIij_GPU[i8j8][ROW][COL], 
                            SPixA_CFIij_GPU[ij][ROW][COL]);
                    
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_OMG'] = _module

                # ** Fill Linear-System [OMEGA]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fab': Fab, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    int cIdx, double cPreOMG_GPU[%(N0)s][%(N1)s], double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fijab = %(Fijab)s;
                    
                    if (ROW < Fijab && COL < Fijab) {
                        
                        // INDEX Analysis
                        int i8j8 = SREF_ijab_GPU[ROW][0];
                        int a8b8 = SREF_ijab_GPU[ROW][1];
                        int ij = SREF_ijab_GPU[COL][0];
                        int ab = SREF_ijab_GPU[COL][1];

                        int a8 = REF_ab_GPU[a8b8][0];
                        int b8 = REF_ab_GPU[a8b8][1];
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        int idx = i8j8 * Fij + ij;

                        if (idx == cIdx) {
                        
                            // Define Mod_N0(rho), Mod_N1(eps)
                            float tmp = 0.0;
                            tmp = fmod(float(a8), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MODa8 = tmp;

                            tmp = fmod(float(b8), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MODb8 = tmp;

                            tmp = fmod(float(-a), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MOD_a = tmp;

                            tmp = fmod(float(-b), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MOD_b = tmp;

                            tmp = fmod(float(a8-a), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MODa8_a = tmp;

                            tmp = fmod(float(b8-b), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MODb8_b = tmp;

                            // Fill Linear System [A-component]
                            if ((a8 != 0 || b8 != 0) && (a != 0 || b != 0)) {
                                LHMAT_GPU[ROW][COL] = - cPreOMG_GPU[MODa8][MODb8]
                                                    - cPreOMG_GPU[MOD_a][MOD_b] 
                                                    + cPreOMG_GPU[MODa8_a][MODb8_b] 
                                                    + cPreOMG_GPU[0][0];
                            }

                            if ((a8 == 0 && b8 == 0) && (a != 0 || b != 0)) {
                                LHMAT_GPU[ROW][COL] = cPreOMG_GPU[MOD_a][MOD_b] - cPreOMG_GPU[0][0];
                            }

                            if ((a8 != 0 || b8 != 0) && (a == 0 && b == 0)) {
                                LHMAT_GPU[ROW][COL] = cPreOMG_GPU[MODa8][MODb8] - cPreOMG_GPU[0][0];
                            }

                            if ((a8 == 0 && b8 == 0) && (a == 0 && b == 0)) {
                                LHMAT_GPU[ROW][COL] = cPreOMG_GPU[0][0];
                            }
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_OMG'] = _module

                # ** Hadamard Product [GAMMA]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FGAM': FGAM}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_ijpq_GPU[%(FGAM)s][2], 
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpGAM_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    
                    if (ROW < N0 && COL < N1) {
                    
                        int i8j8 = SREF_ijpq_GPU[cIdx][0];
                        int pq = SREF_ijpq_GPU[cIdx][1];

                        cHpGAM_GPU[ROW][COL] = cuCmul(SPixA_FIij_GPU[i8j8][ROW][COL], 
                            SPixA_CFTpq_GPU[pq][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_GAM'] = _module

                # ** Fill Linear-System [GAMMA]
                _refdict = {'N0': N0, 'N1': N1, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    int cIdx, double cPreGAM_GPU[%(N0)s][%(N1)s], double LHMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;
                    
                    if (ROW < Fijab && COL < Fpq) {
                        
                        // INDEX Analysis
                        int i8j8 = SREF_ijab_GPU[ROW][0];
                        int a8b8 = SREF_ijab_GPU[ROW][1];
                        int pq = COL;

                        int a8 = REF_ab_GPU[a8b8][0];
                        int b8 = REF_ab_GPU[a8b8][1];
                        int idx = i8j8 * Fpq + pq;
                        int cCOL = Fijab + COL;              // add offset

                        if (idx == cIdx) {

                            // Define Mod_N0(rho), Mod_N1(eps)
                            float tmp = 0.0;
                            tmp = fmod(float(a8), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MODa8 = tmp;

                            tmp = fmod(float(b8), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MODb8 = tmp;

                            // Fill Linear System [B-component]
                            if (a8 != 0 || b8 != 0) {
                                LHMAT_GPU[ROW][cCOL] = cPreGAM_GPU[MODa8][MODb8] - cPreGAM_GPU[0][0];
                            }

                            if (a8 == 0 && b8 == 0) {
                                LHMAT_GPU[ROW][cCOL] = cPreGAM_GPU[0][0];
                            }
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_GAM'] = _module

                # ** Hadamard Product [PSI]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FPSI': FPSI}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqij_GPU[%(FPSI)s][2],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpPSI_GPU[%(N0)s][%(N1)s])
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {
    
                        int p8q8 = SREF_pqij_GPU[cIdx][0];
                        int ij = SREF_pqij_GPU[cIdx][1];

                        cHpPSI_GPU[ROW][COL] = cuCmul(SPixA_FTpq_GPU[p8q8][ROW][COL], 
                            SPixA_CFIij_GPU[ij][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PSI'] = _module

                # ** Fill Linear-System [PSI]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    int cIdx, double cPrePSI_GPU[%(N0)s][%(N1)s], double LHMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;

                    if (ROW < Fpq && COL < Fijab) {

                        // INDEX Analysis
                        int cROW = Fijab + ROW;              // add offset
                        int p8q8 = ROW;
                        int ij = SREF_ijab_GPU[COL][0];
                        int ab = SREF_ijab_GPU[COL][1];
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        int idx = p8q8 * Fij + ij;

                        if (idx == cIdx) {

                            // Define Mod_N0(rho), Mod_N1(eps)
                            float tmp = 0.0;
                            tmp = fmod(float(-a), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MOD_a = tmp;

                            tmp = fmod(float(-b), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MOD_b = tmp;
                            
                            // Fill Linear System [B#-component]
                            if (a != 0 || b != 0) {
                                LHMAT_GPU[cROW][COL] = cPrePSI_GPU[MOD_a][MOD_b] - cPrePSI_GPU[0][0];
                            }

                            if (a == 0 && b == 0) {
                                LHMAT_GPU[cROW][COL] = cPrePSI_GPU[0][0];
                            }
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_PSI'] = _module

                # ** Hadamard Product [PHI]
                _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'FPHI': FPHI}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqp0q0_GPU[%(FPHI)s][2], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s],  
                    int cIdx, cuDoubleComplex cHpPHI_GPU[%(N0)s][%(N1)s])
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int FPHI = %(FPHI)s;

                    if (ROW < N0 && COL < N1) {
                    
                        int p8q8 = SREF_pqp0q0_GPU[cIdx][0];
                        int pq = SREF_pqp0q0_GPU[cIdx][1];

                        cHpPHI_GPU[ROW][COL] = cuCmul(SPixA_FTpq_GPU[p8q8][ROW][COL], 
                            SPixA_CFTpq_GPU[pq][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PHI'] = _module

                # ** Fill Linear-System [PHI]
                _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int cIdx, double cPrePHI_GPU[%(N0)s][%(N1)s],
                    double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;

                    if (ROW < Fpq && COL < Fpq) {
                        
                        // INDEX Analysis
                        int cROW = Fijab + ROW;              // add offset
                        int cCOL = Fijab + COL;              // add offset
                        
                        int p8q8 = ROW;
                        int pq = COL;
                        int idx = p8q8 * Fpq + pq;

                        if (idx == cIdx) {
                        
                            // Fill Linear System [C-component]
                            LHMAT_GPU[cROW][cCOL] = cPrePHI_GPU[0][0];
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_PHI'] = _module

            # ** Hadamard Product [THETA]
            _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FTHE': FTHE}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                cuDoubleComplex PixA_CFJ_GPU[%(N0)s][%(N1)s], cuDoubleComplex HpTHE_GPU[%(FTHE)s][%(N0)s][%(N1)s])
            {    
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int FTHE = %(FTHE)s;

                if (ROW < N0 && COL < N1) {
                    for(int i8j8 = 0; i8j8 < FTHE; ++i8j8){
                        HpTHE_GPU[i8j8][ROW][COL] = cuCmul(PixA_CFJ_GPU[ROW][COL], SPixA_FIij_GPU[i8j8][ROW][COL]);
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['HadProd_THE'] = _module

            # ** Fill Linear-System [THETA]  
            _refdict = {'N0': N0, 'N1': N1, 'NEQ': NEQ, 'Fijab': Fijab, 'Fab': Fab, 'FTHE': FTHE}
            _funcstr = r"""
            extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                double PreTHE_GPU[%(FTHE)s][%(N0)s][%(N1)s], double RHb_GPU[%(NEQ)s]) 
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int Fijab = %(Fijab)s;

                if (ROW < Fijab && COL == 0) {

                    // INDEX Analysis
                    int i8j8 = SREF_ijab_GPU[ROW][0];
                    int a8b8 = SREF_ijab_GPU[ROW][1];
                    int a8 = REF_ab_GPU[a8b8][0];
                    int b8 = REF_ab_GPU[a8b8][1];
                    int idx = i8j8;

                    // Define Mod_N0(rho), Mod_N1(eps)
                    float tmp = 0.0;
                    tmp = fmod(float(a8), float(N0));
                    if (tmp < 0.0) {tmp += float(N0);}
                    int MODa8 = tmp;

                    tmp = fmod(float(b8), float(N1));
                    if (tmp < 0.0) {tmp += float(N1);}
                    int MODb8 = tmp;
                    
                    // Fill Linear System [D-component]
                    if (a8 != 0 || b8 != 0) {
                        RHb_GPU[ROW] = PreTHE_GPU[idx][MODa8][MODb8] - PreTHE_GPU[idx][0][0];
                    }

                    if (a8 == 0 && b8 == 0) {
                        RHb_GPU[ROW] = PreTHE_GPU[idx][0][0];
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['FillLS_THE'] = _module

            # ** Hadamard Product [DELTA]
            _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'FDEL': FDEL}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                cuDoubleComplex PixA_CFJ_GPU[%(N0)s][%(N1)s], cuDoubleComplex HpDEL_GPU[%(FDEL)s][%(N0)s][%(N1)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int FDEL = %(FDEL)s;

                if (ROW < N0 && COL < N1) {
                    for(int p8q8 = 0; p8q8 < FDEL; ++p8q8){
                        HpDEL_GPU[p8q8][ROW][COL] = 
                            cuCmul(PixA_CFJ_GPU[ROW][COL], SPixA_FTpq_GPU[p8q8][ROW][COL]);
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['HadProd_DEL'] = _module

            # ** Fill Linear-System [DELTA]
            _refdict = {'N0': N0, 'N1': N1, 'NEQ': NEQ, 'Fpq': Fpq, 'Fijab': Fijab, 'FDEL': FDEL}
            _funcstr = r"""
            extern "C" __global__ void kmain(double PreDEL_GPU[%(FDEL)s][%(N0)s][%(N1)s], 
                double RHb_GPU[%(NEQ)s]) 
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                int Fpq = %(Fpq)s;
                int Fijab = %(Fijab)s;

                if (ROW < Fpq && COL == 0) {
                    // INDEX Analysis
                    int cROW = Fijab + ROW;              // add offset
                    int idx = ROW;                       // i.e. p8q8

                    // Fill Linear System [E-component]
                    RHb_GPU[cROW] = PreDEL_GPU[idx][0][0];
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['FillLS_DEL'] = _module

        if SCALING_MODE == 'SEPARATE-VARYING':
            assert MINIMIZE_GPU_MEMORY_USAGE # Force
            
            if MINIMIZE_GPU_MEMORY_USAGE:
            
                # ** Hadamard Product [OMEGA_11]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FOMG': FOMG}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_iji0j0_GPU[%(FOMG)s][2],
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpOMG11_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {
                        
                        int i8j8 = SREF_iji0j0_GPU[cIdx][0];
                        int ij = SREF_iji0j0_GPU[cIdx][1];

                        cHpOMG11_GPU[ROW][COL] = cuCmul(SPixA_FIij_GPU[i8j8][ROW][COL], 
                            SPixA_CFIij_GPU[ij][ROW][COL]);
                    
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_OMG11'] = _module

                # ** Hadamard Product [OMEGA_01]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FOMG': FOMG}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_iji0j0_GPU[%(FOMG)s][2],
                    cuDoubleComplex ScaSPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpOMG01_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {
                        
                        int i8j8 = SREF_iji0j0_GPU[cIdx][0];
                        int ij = SREF_iji0j0_GPU[cIdx][1];

                        cHpOMG01_GPU[ROW][COL] = cuCmul(ScaSPixA_FIij_GPU[i8j8][ROW][COL], 
                            SPixA_CFIij_GPU[ij][ROW][COL]);
                    
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_OMG01'] = _module

                # ** Hadamard Product [OMEGA_10]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FOMG': FOMG}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_iji0j0_GPU[%(FOMG)s][2],
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex ScaSPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpOMG10_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {
                        
                        int i8j8 = SREF_iji0j0_GPU[cIdx][0];
                        int ij = SREF_iji0j0_GPU[cIdx][1];

                        cHpOMG10_GPU[ROW][COL] = cuCmul(SPixA_FIij_GPU[i8j8][ROW][COL], 
                            ScaSPixA_CFIij_GPU[ij][ROW][COL]);
                    
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_OMG10'] = _module

                # ** Hadamard Product [OMEGA_00]  # TODO: redundant, only one element used.
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FOMG': FOMG}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_iji0j0_GPU[%(FOMG)s][2],
                    cuDoubleComplex ScaSPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex ScaSPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpOMG00_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {
                        
                        int i8j8 = SREF_iji0j0_GPU[cIdx][0];
                        int ij = SREF_iji0j0_GPU[cIdx][1];

                        cHpOMG00_GPU[ROW][COL] = cuCmul(ScaSPixA_FIij_GPU[i8j8][ROW][COL], 
                            ScaSPixA_CFIij_GPU[ij][ROW][COL]);
                    
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_OMG00'] = _module

                # ** Fill Linear-System [OMEGA]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fab': Fab, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    int cIdx, double cPreOMG11_GPU[%(N0)s][%(N1)s], double cPreOMG01_GPU[%(N0)s][%(N1)s], 
                    double cPreOMG10_GPU[%(N0)s][%(N1)s], double cPreOMG00_GPU[%(N0)s][%(N1)s], 
                    double LHMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fijab = %(Fijab)s;
                    
                    if (ROW < Fijab && COL < Fijab) {
                        
                        // INDEX Analysis
                        int i8j8 = SREF_ijab_GPU[ROW][0];
                        int a8b8 = SREF_ijab_GPU[ROW][1];
                        int ij = SREF_ijab_GPU[COL][0];
                        int ab = SREF_ijab_GPU[COL][1];

                        int a8 = REF_ab_GPU[a8b8][0];
                        int b8 = REF_ab_GPU[a8b8][1];
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        int idx = i8j8 * Fij + ij;

                        if (idx == cIdx) {
                        
                            // Define Mod_N0(rho), Mod_N1(eps)
                            float tmp = 0.0;
                            tmp = fmod(float(a8), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MODa8 = tmp;

                            tmp = fmod(float(b8), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MODb8 = tmp;

                            tmp = fmod(float(-a), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MOD_a = tmp;

                            tmp = fmod(float(-b), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MOD_b = tmp;

                            tmp = fmod(float(a8-a), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MODa8_a = tmp;

                            tmp = fmod(float(b8-b), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MODb8_b = tmp;

                            // Fill Linear System [A-component]
                            if ((a8 != 0 || b8 != 0) && (a != 0 || b != 0)) {
                                LHMAT_GPU[ROW][COL] = - cPreOMG11_GPU[MODa8][MODb8]
                                                      - cPreOMG11_GPU[MOD_a][MOD_b] 
                                                      + cPreOMG11_GPU[MODa8_a][MODb8_b] 
                                                      + cPreOMG11_GPU[0][0];
                            }

                            if ((a8 == 0 && b8 == 0) && (a != 0 || b != 0)) {
                                LHMAT_GPU[ROW][COL] = cPreOMG01_GPU[MOD_a][MOD_b] 
                                                      - cPreOMG01_GPU[0][0];
                            }

                            if ((a8 != 0 || b8 != 0) && (a == 0 && b == 0)) {
                                LHMAT_GPU[ROW][COL] = cPreOMG10_GPU[MODa8][MODb8] 
                                                      - cPreOMG10_GPU[0][0];
                            }

                            if ((a8 == 0 && b8 == 0) && (a == 0 && b == 0)) {
                                LHMAT_GPU[ROW][COL] = cPreOMG00_GPU[0][0];
                            }
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_OMG'] = _module

                # ** Hadamard Product [GAMMA_1]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FGAM': FGAM}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_ijpq_GPU[%(FGAM)s][2], 
                    cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpGAM1_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    
                    if (ROW < N0 && COL < N1) {
                    
                        int i8j8 = SREF_ijpq_GPU[cIdx][0];
                        int pq = SREF_ijpq_GPU[cIdx][1];

                        cHpGAM1_GPU[ROW][COL] = cuCmul(SPixA_FIij_GPU[i8j8][ROW][COL], 
                            SPixA_CFTpq_GPU[pq][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_GAM1'] = _module

                # ** Hadamard Product [GAMMA_0]  # TODO: redundant, only one element used.
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FGAM': FGAM}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_ijpq_GPU[%(FGAM)s][2], 
                    cuDoubleComplex ScaSPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpGAM0_GPU[%(N0)s][%(N1)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    
                    if (ROW < N0 && COL < N1) {
                    
                        int i8j8 = SREF_ijpq_GPU[cIdx][0];
                        int pq = SREF_ijpq_GPU[cIdx][1];

                        cHpGAM0_GPU[ROW][COL] = cuCmul(ScaSPixA_FIij_GPU[i8j8][ROW][COL], 
                            SPixA_CFTpq_GPU[pq][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_GAM0'] = _module

                # ** Fill Linear-System [GAMMA]
                _refdict = {'N0': N0, 'N1': N1, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    int cIdx, double cPreGAM1_GPU[%(N0)s][%(N1)s], double cPreGAM0_GPU[%(N0)s][%(N1)s], 
                    double LHMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;
                    
                    if (ROW < Fijab && COL < Fpq) {
                        
                        // INDEX Analysis
                        int i8j8 = SREF_ijab_GPU[ROW][0];
                        int a8b8 = SREF_ijab_GPU[ROW][1];
                        int pq = COL;

                        int a8 = REF_ab_GPU[a8b8][0];
                        int b8 = REF_ab_GPU[a8b8][1];
                        int idx = i8j8 * Fpq + pq;
                        int cCOL = Fijab + COL;       // add offset

                        if (idx == cIdx) {

                            // Define Mod_N0(rho), Mod_N1(eps)
                            float tmp = 0.0;
                            tmp = fmod(float(a8), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MODa8 = tmp;

                            tmp = fmod(float(b8), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MODb8 = tmp;

                            // Fill Linear System [B-component]
                            if (a8 != 0 || b8 != 0) {
                                LHMAT_GPU[ROW][cCOL] = cPreGAM1_GPU[MODa8][MODb8] 
                                                       - cPreGAM1_GPU[0][0];
                            }

                            if (a8 == 0 && b8 == 0) {
                                LHMAT_GPU[ROW][cCOL] = cPreGAM0_GPU[0][0];
                            }
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_GAM'] = _module

                # ** Hadamard Product [PSI_1]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FPSI': FPSI}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqij_GPU[%(FPSI)s][2],
                    cuDoubleComplex SPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpPSI1_GPU[%(N0)s][%(N1)s])
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {

                        int p8q8 = SREF_pqij_GPU[cIdx][0];
                        int ij = SREF_pqij_GPU[cIdx][1];

                        cHpPSI1_GPU[ROW][COL] = cuCmul(SPixA_FTpq_GPU[p8q8][ROW][COL], 
                            SPixA_CFIij_GPU[ij][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PSI1'] = _module

                # ** Hadamard Product [PSI_0]  # TODO: redundant, only one element used.
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fpq': Fpq, 'FPSI': FPSI}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqij_GPU[%(FPSI)s][2],
                    cuDoubleComplex ScaSPixA_CFIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    int cIdx, cuDoubleComplex cHpPSI0_GPU[%(N0)s][%(N1)s])
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;

                    if (ROW < N0 && COL < N1) {

                        int p8q8 = SREF_pqij_GPU[cIdx][0];
                        int ij = SREF_pqij_GPU[cIdx][1];

                        cHpPSI0_GPU[ROW][COL] = cuCmul(SPixA_FTpq_GPU[p8q8][ROW][COL], 
                            ScaSPixA_CFIij_GPU[ij][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PSI0'] = _module

                # ** Fill Linear-System [PSI]
                _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                    int cIdx, double cPrePSI1_GPU[%(N0)s][%(N1)s], double cPrePSI0_GPU[%(N0)s][%(N1)s], 
                    double LHMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fij = %(Fij)s;
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;

                    if (ROW < Fpq && COL < Fijab) {

                        // INDEX Analysis
                        int cROW = Fijab + ROW;              // add offset
                        int p8q8 = ROW;
                        int ij = SREF_ijab_GPU[COL][0];
                        int ab = SREF_ijab_GPU[COL][1];
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        int idx = p8q8 * Fij + ij;

                        if (idx == cIdx) {

                            // Define Mod_N0(rho), Mod_N1(eps)
                            float tmp = 0.0;
                            tmp = fmod(float(-a), float(N0));
                            if (tmp < 0.0) {tmp += float(N0);}
                            int MOD_a = tmp;

                            tmp = fmod(float(-b), float(N1));
                            if (tmp < 0.0) {tmp += float(N1);}
                            int MOD_b = tmp;
                            
                            // Fill Linear System [B#-component]
                            if (a != 0 || b != 0) {
                                LHMAT_GPU[cROW][COL] = cPrePSI1_GPU[MOD_a][MOD_b] 
                                                       - cPrePSI1_GPU[0][0];
                            }

                            if (a == 0 && b == 0) {
                                LHMAT_GPU[cROW][COL] = cPrePSI0_GPU[0][0];
                            }
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_PSI'] = _module

                # ** Hadamard Product [PHI]
                _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'FPHI': FPHI}
                _funcstr = r"""
                #include "cuComplex.h"
                extern "C" __global__ void kmain(int SREF_pqp0q0_GPU[%(FPHI)s][2], 
                    cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                    cuDoubleComplex SPixA_CFTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s],  
                    int cIdx, cuDoubleComplex cHpPHI_GPU[%(N0)s][%(N1)s])
                {    
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int N0 = %(N0)s;
                    int N1 = %(N1)s;
                    int Fpq = %(Fpq)s;
                    int FPHI = %(FPHI)s;

                    if (ROW < N0 && COL < N1) {
                    
                        int p8q8 = SREF_pqp0q0_GPU[cIdx][0];
                        int pq = SREF_pqp0q0_GPU[cIdx][1];

                        cHpPHI_GPU[ROW][COL] = cuCmul(SPixA_FTpq_GPU[p8q8][ROW][COL], 
                            SPixA_CFTpq_GPU[pq][ROW][COL]);
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
                SFFTModule_dict['HadProd_PHI'] = _module

                # ** Fill Linear-System [PHI]
                _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'Fijab': Fijab, 'NEQ': NEQ}
                _funcstr = r"""
                extern "C" __global__ void kmain(int cIdx, double cPrePHI_GPU[%(N0)s][%(N1)s],
                    double LHMAT_GPU[%(NEQ)s][%(NEQ)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;
                    
                    int Fpq = %(Fpq)s;
                    int Fijab = %(Fijab)s;

                    if (ROW < Fpq && COL < Fpq) {
                        
                        // INDEX Analysis
                        int cROW = Fijab + ROW;              // add offset
                        int cCOL = Fijab + COL;              // add offset
                        
                        int p8q8 = ROW;
                        int pq = COL;
                        int idx = p8q8 * Fpq + pq;

                        if (idx == cIdx) {
                        
                            // Fill Linear System [C-component]
                            LHMAT_GPU[cROW][cCOL] = cPrePHI_GPU[0][0];
                        }
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['FillLS_PHI'] = _module

            # ** Hadamard Product [THETA_1]
            _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FTHE': FTHE}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                cuDoubleComplex PixA_CFJ_GPU[%(N0)s][%(N1)s], cuDoubleComplex HpTHE1_GPU[%(FTHE)s][%(N0)s][%(N1)s])
            {    
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int FTHE = %(FTHE)s;

                if (ROW < N0 && COL < N1) {
                    for(int i8j8 = 0; i8j8 < FTHE; ++i8j8){
                        HpTHE1_GPU[i8j8][ROW][COL] = cuCmul(PixA_CFJ_GPU[ROW][COL], 
                            SPixA_FIij_GPU[i8j8][ROW][COL]);
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['HadProd_THE1'] = _module

            # ** Hadamard Product [THETA_0]  # TODO: redundant, only one element used.
            _refdict = {'N0': N0, 'N1': N1, 'Fij': Fij, 'FTHE': FTHE}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(cuDoubleComplex ScaSPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s],
                cuDoubleComplex PixA_CFJ_GPU[%(N0)s][%(N1)s], cuDoubleComplex HpTHE0_GPU[%(FTHE)s][%(N0)s][%(N1)s])
            {    
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int FTHE = %(FTHE)s;

                if (ROW < N0 && COL < N1) {
                    for(int i8j8 = 0; i8j8 < FTHE; ++i8j8){
                        HpTHE0_GPU[i8j8][ROW][COL] = cuCmul(PixA_CFJ_GPU[ROW][COL], 
                            ScaSPixA_FIij_GPU[i8j8][ROW][COL]);
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['HadProd_THE0'] = _module

            # ** Fill Linear-System [THETA]  
            _refdict = {'N0': N0, 'N1': N1, 'NEQ': NEQ, 'Fijab': Fijab, 'Fab': Fab, 'FTHE': FTHE}
            _funcstr = r"""
            extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2], 
                double PreTHE1_GPU[%(FTHE)s][%(N0)s][%(N1)s], double PreTHE0_GPU[%(FTHE)s][%(N0)s][%(N1)s], 
                double RHb_GPU[%(NEQ)s]) 
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int Fijab = %(Fijab)s;

                if (ROW < Fijab && COL == 0) {

                    // INDEX Analysis
                    int i8j8 = SREF_ijab_GPU[ROW][0];
                    int a8b8 = SREF_ijab_GPU[ROW][1];
                    int a8 = REF_ab_GPU[a8b8][0];
                    int b8 = REF_ab_GPU[a8b8][1];
                    int idx = i8j8;

                    // Define Mod_N0(rho), Mod_N1(eps)
                    float tmp = 0.0;
                    tmp = fmod(float(a8), float(N0));
                    if (tmp < 0.0) {tmp += float(N0);}
                    int MODa8 = tmp;

                    tmp = fmod(float(b8), float(N1));
                    if (tmp < 0.0) {tmp += float(N1);}
                    int MODb8 = tmp;
                    
                    // Fill Linear System [D-component]
                    if (a8 != 0 || b8 != 0) {
                        RHb_GPU[ROW] = PreTHE1_GPU[idx][MODa8][MODb8] 
                                       - PreTHE1_GPU[idx][0][0];
                    }

                    if (a8 == 0 && b8 == 0) {
                        RHb_GPU[ROW] = PreTHE0_GPU[idx][0][0];
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['FillLS_THE'] = _module

            # ** Hadamard Product [DELTA]
            _refdict = {'N0': N0, 'N1': N1, 'Fpq': Fpq, 'FDEL': FDEL}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                cuDoubleComplex PixA_CFJ_GPU[%(N0)s][%(N1)s], cuDoubleComplex HpDEL_GPU[%(FDEL)s][%(N0)s][%(N1)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int FDEL = %(FDEL)s;

                if (ROW < N0 && COL < N1) {
                    for(int p8q8 = 0; p8q8 < FDEL; ++p8q8){
                        HpDEL_GPU[p8q8][ROW][COL] = 
                            cuCmul(PixA_CFJ_GPU[ROW][COL], SPixA_FTpq_GPU[p8q8][ROW][COL]);
                    }
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['HadProd_DEL'] = _module

            # ** Fill Linear-System [DELTA]
            _refdict = {'N0': N0, 'N1': N1, 'NEQ': NEQ, 'Fpq': Fpq, 'Fijab': Fijab, 'FDEL': FDEL}
            _funcstr = r"""
            extern "C" __global__ void kmain(double PreDEL_GPU[%(FDEL)s][%(N0)s][%(N1)s], 
                double RHb_GPU[%(NEQ)s]) 
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                int Fpq = %(Fpq)s;
                int Fijab = %(Fijab)s;

                if (ROW < Fpq && COL == 0) {
                    // INDEX Analysis
                    int cROW = Fijab + ROW;              // add offset
                    int idx = ROW;                       // i.e. p8q8

                    // Fill Linear System [E-component]
                    RHb_GPU[cROW] = PreDEL_GPU[idx][0][0];
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['FillLS_DEL'] = _module

        # <*****> regularize matrix <*****> #
        if REGULARIZE_KERNEL:

            _refdict = {'Fab': Fab}
            _funcstr = r"""
            extern "C" __global__ void kmain(int LAPMAT_GPU[%(Fab)s][%(Fab)s],
                int RRF_GPU[%(Fab)s], int CCF_GPU[%(Fab)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int Fab = %(Fab)s;

                if (ROW < Fab && COL < Fab) {
                    if (ROW != COL) {

                        int r1 = RRF_GPU[ROW];
                        int c1 = CCF_GPU[ROW];
                        int r2 = RRF_GPU[COL];
                        int c2 = CCF_GPU[COL];

                        if (r2 == r1-1 && c2 == c1) {
                            LAPMAT_GPU[ROW][COL] = -1;
                        }
                        if (r2 == r1+1 && c2 == c1) {
                            LAPMAT_GPU[ROW][COL] = -1;
                        }
                        if (r2 == r1 && c2 == c1-1) {
                            LAPMAT_GPU[ROW][COL] = -1;
                        }
                        if (r2 == r1 && c2 == c1+1) {
                            LAPMAT_GPU[ROW][COL] = -1;
                        }   
                    }
                }
            }
            """

            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['fill_lapmat_nondiagonal'] = _module

            c0 = w0*L1+w1
            _refdict = {'Fab': Fab, 'c0': c0}
            _funcstr = r"""
            extern "C" __global__ void kmain(int iREGMAT_GPU[%(Fab)s][%(Fab)s],
                int LTLMAT_GPU[%(Fab)s][%(Fab)s])
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;

                int Fab = %(Fab)s;
                int c0 = %(c0)s;

                if (ROW < Fab && COL < Fab) {
                    
                    if (ROW != c0 && COL != c0) {
                        iREGMAT_GPU[ROW][COL] = LTLMAT_GPU[ROW][COL] + LTLMAT_GPU[COL][ROW]
                                                - LTLMAT_GPU[c0][ROW] - LTLMAT_GPU[c0][COL]
                                                - LTLMAT_GPU[ROW][c0] - LTLMAT_GPU[COL][c0]
                                                + 2 * LTLMAT_GPU[c0][c0];
                    }
                    
                    if (ROW != c0 && COL == c0) {
                        iREGMAT_GPU[ROW][COL] = LTLMAT_GPU[ROW][c0] + LTLMAT_GPU[c0][ROW] 
                                                - 2 * LTLMAT_GPU[c0][c0];
                    }
                    
                    if (ROW == c0 && COL != c0) {
                        iREGMAT_GPU[ROW][COL] = LTLMAT_GPU[COL][c0] + LTLMAT_GPU[c0][COL]
                                                - 2 * LTLMAT_GPU[c0][c0];
                    }
                    
                    if (ROW == c0 && COL == c0) {
                        iREGMAT_GPU[ROW][COL] = 2 * LTLMAT_GPU[c0][c0];
                    }
                }
            }
            """

            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['fill_iregmat'] = _module

            if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:

                SCALE2 = SCALE**2
                _refdict = {'Fij': Fij, 'Fab': Fab, 'Fijab': Fijab, 'NEQ': NEQ, 'SCALE2': SCALE2, 'RemSymbol': '%'}
                _funcstr = r"""
                extern "C" __global__ void kmain(int iREGMAT_GPU[%(Fab)s][%(Fab)s],
                    double SSTMAT_GPU[%(Fij)s][%(Fij)s], 
                    double REGMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int Fijab = %(Fijab)s;
                    int Fab = %(Fab)s;
                    double SCALE2 = %(SCALE2)s;
                    
                    if (ROW < Fijab && COL < Fijab) {
                        int k = ROW / Fab;
                        int c = ROW %(RemSymbol)s Fab;
                        int k8 = COL / Fab;
                        int c8 = COL %(RemSymbol)s Fab;
                        
                        REGMAT_GPU[ROW][COL] = SCALE2 * SSTMAT_GPU[k][k8] * iREGMAT_GPU[c][c8];
                    }
                }
                """

                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['fill_regmat'] = _module
            
            if SCALING_MODE == 'SEPARATE-VARYING':
                
                c0 = w0*L1+w1
                SCALE2 = SCALE**2
                _refdict = {'Fij': Fij, 'Fab': Fab, 'c0': c0, 'Fijab': Fijab, 'NEQ': NEQ, 'SCALE2': SCALE2, 'RemSymbol': '%'}
                _funcstr = r"""
                extern "C" __global__ void kmain(int iREGMAT_GPU[%(Fab)s][%(Fab)s],
                    double SSTMAT_GPU[%(Fij)s][%(Fij)s], 
                    double CSSTMAT_GPU[%(Fij)s][%(Fij)s],
                    double DSSTMAT_GPU[%(Fij)s][%(Fij)s],
                    double REGMAT_GPU[%(NEQ)s][%(NEQ)s])
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;

                    int Fab = %(Fab)s;
                    int c0 = %(c0)s;
                    int Fijab = %(Fijab)s;
                    double SCALE2 = %(SCALE2)s;
                    
                    if (ROW < Fijab && COL < Fijab) {
                        int k = ROW / Fab;
                        int c = ROW %(RemSymbol)s Fab;
                        int k8 = COL / Fab;
                        int c8 = COL %(RemSymbol)s Fab;
                        
                        if (c != c0 && c8 != c0) {
                            REGMAT_GPU[ROW][COL] = SCALE2 * SSTMAT_GPU[k][k8] * iREGMAT_GPU[c][c8];
                        }

                        if (c != c0 && c8 == c0) {
                            REGMAT_GPU[ROW][COL] = SCALE2 * CSSTMAT_GPU[k][k8] * iREGMAT_GPU[c][c8];
                        }
                        
                        if (c == c0 && c8 != c0) {
                            REGMAT_GPU[ROW][COL] = SCALE2 * CSSTMAT_GPU[k8][k] * iREGMAT_GPU[c][c8];
                        }
                        
                        if (c == c0 && c8 == c0) {
                            REGMAT_GPU[ROW][COL] = SCALE2 * DSSTMAT_GPU[k][k8] * iREGMAT_GPU[c][c8];
                        }
                    }
                }
                """

                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['fill_regmat'] = _module

        # <*****> Tweak Linear-System & Restore Solution <*****> #
        if SCALING_MODE == 'SEPARATE-CONSTANT':

            if KerSpType == 'Polynomial':
                
                _refdict = {'NEQ': NEQ, 'NEQt': NEQt}
                _funcstr = r"""
                extern "C" __global__ void kmain(double LHMAT_GPU[%(NEQ)s][%(NEQ)s], double RHb_GPU[%(NEQ)s], 
                    int PresIDX_GPU[%(NEQt)s], double LHMAT_tweaked_GPU[%(NEQt)s][%(NEQt)s], 
                    double RHb_tweaked_GPU[%(NEQt)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;  // row index of tweakedLS
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;  // column index of tweakedLS
                    int NEQt = %(NEQt)s;

                    if (ROW < NEQt && COL < NEQt) {
                        int PresROW = PresIDX_GPU[ROW];  // row index of LS
                        int PresCOL = PresIDX_GPU[COL];  // column index of LS
                        LHMAT_tweaked_GPU[ROW][COL] = LHMAT_GPU[PresROW][PresCOL];
                    }

                    if (ROW < NEQt && COL == 0) {
                        int PresROW = PresIDX_GPU[ROW];  // row index of LS
                        RHb_tweaked_GPU[ROW] = RHb_GPU[PresROW];
                    }
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['TweakLS'] = _module

            if KerSpType == 'B-Spline':
                
                _refdict = {'Fij': Fij, 'NEQ': NEQ, 'NEQt': NEQt}
                _funcstr = r"""
                extern "C" __global__ void kmain(double LHMAT_GPU[%(NEQ)s][%(NEQ)s], double RHb_GPU[%(NEQ)s], 
                    int PresIDX_GPU[%(NEQt)s], int ij00_GPU[%(Fij)s], double LHMAT_tweaked_GPU[%(NEQt)s][%(NEQt)s], 
                    double RHb_tweaked_GPU[%(NEQt)s]) 
                {
                    int ROW = blockIdx.x*blockDim.x+threadIdx.x;  // row index of tweakedLS
                    int COL = blockIdx.y*blockDim.y+threadIdx.y;  // column index of tweakedLS

                    int NEQt = %(NEQt)s;
                    int Fij = %(Fij)s;
                    int keyIdx = ij00_GPU[0];  // key index (ijab = 0000) of LS (tweakedLS)

                    if (ROW == keyIdx && COL != keyIdx && COL < NEQt) {
                        double cum1 = 0.0;
                        for(int ij = 0; ij < Fij; ++ij){
                            int ridx = ij00_GPU[ij];         // row index of LS
                            int PresCOL = PresIDX_GPU[COL];  // column index of LS   
                            cum1 += LHMAT_GPU[ridx][PresCOL];
                        }
                        LHMAT_tweaked_GPU[ROW][COL] = cum1;
                    }
                    
                    if (ROW != keyIdx && ROW < NEQt && COL == keyIdx) {
                        double cum2 = 0.0;
                        for(int ij = 0; ij < Fij; ++ij){
                            int PresROW = PresIDX_GPU[ROW];  // row index of LS
                            int cidx = ij00_GPU[ij];         // column index of LS
                            cum2 += LHMAT_GPU[PresROW][cidx];
                        }
                        LHMAT_tweaked_GPU[ROW][COL] = cum2;
                    }

                    if (ROW == keyIdx && COL == keyIdx) {
                        double cum3 = 0.0;
                        for(int ij = 0; ij < Fij; ++ij){
                            for(int i8j8 = 0; i8j8 < Fij; ++i8j8){
                                int ridx = ij00_GPU[ij];    // row index of LS
                                int cidx = ij00_GPU[i8j8];  // column index of LS
                                cum3 += LHMAT_GPU[ridx][cidx];
                            }
                        }
                        LHMAT_tweaked_GPU[ROW][COL] = cum3;
                    }

                    if (ROW != keyIdx && ROW < NEQt && COL != keyIdx && COL < NEQt) {
                        int PresROW = PresIDX_GPU[ROW];  // row index of LS
                        int PresCOL = PresIDX_GPU[COL];  // column index of LS
                        LHMAT_tweaked_GPU[ROW][COL] = LHMAT_GPU[PresROW][PresCOL];
                    }

                    if (ROW == keyIdx && COL == 0) {
                        double cum4 = 0.0;
                        for(int ij = 0; ij < Fij; ++ij){
                            int ridx = ij00_GPU[ij];  // row index of LS
                            cum4 += RHb_GPU[ridx];
                        }
                        RHb_tweaked_GPU[ROW] = cum4;
                    }

                    if (ROW != keyIdx && ROW < NEQt && COL == 0) {
                        int PresROW = PresIDX_GPU[ROW];  // row index of LS 
                        RHb_tweaked_GPU[ROW] = RHb_GPU[PresROW];
                    }
                    
                }
                """
                _code = _funcstr % _refdict
                _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
                SFFTModule_dict['TweakLS'] = _module
            
            _refdict = {'NEQ': NEQ, 'NEQt': NEQt}
            _funcstr = r"""
            extern "C" __global__ void kmain(double Solution_tweaked_GPU[%(NEQt)s], 
                int PresIDX_GPU[%(NEQt)s], double Solution_GPU[%(NEQ)s]) 
            {    
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;  // row index of tweakedLS
                int COL = blockIdx.y*blockDim.y+threadIdx.y;  // trivial
                int NEQt = %(NEQt)s;
                
                if (ROW < NEQt && COL == 0) {
                    int PresROW = PresIDX_GPU[ROW];  // row index of LS
                    Solution_GPU[PresROW] = Solution_tweaked_GPU[ROW];
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['Restore_Solution'] = _module

        if SCALING_MODE == 'SEPARATE-VARYING' and NEQt < NEQ:
            
            _refdict = {'NEQ': NEQ, 'NEQt': NEQt}
            _funcstr = r"""
            extern "C" __global__ void kmain(double LHMAT_GPU[%(NEQ)s][%(NEQ)s], double RHb_GPU[%(NEQ)s], 
                int PresIDX_GPU[%(NEQt)s], double LHMAT_tweaked_GPU[%(NEQt)s][%(NEQt)s], 
                double RHb_tweaked_GPU[%(NEQt)s]) 
            {
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;  // row index of tweakedLS
                int COL = blockIdx.y*blockDim.y+threadIdx.y;  // column index of tweakedLS
                int NEQt = %(NEQt)s;

                if (ROW < NEQt && COL < NEQt) {
                    int PresROW = PresIDX_GPU[ROW];  // row index of LS
                    int PresCOL = PresIDX_GPU[COL];  // column index of LS
                    LHMAT_tweaked_GPU[ROW][COL] = LHMAT_GPU[PresROW][PresCOL];
                }

                if (ROW < NEQt && COL == 0) {
                    int PresROW = PresIDX_GPU[ROW];  // row index of LS
                    RHb_tweaked_GPU[ROW] = RHb_GPU[PresROW];
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['TweakLS'] = _module

            _refdict = {'NEQ': NEQ, 'NEQt': NEQt}
            _funcstr = r"""
            extern "C" __global__ void kmain(double Solution_tweaked_GPU[%(NEQt)s], 
                int PresIDX_GPU[%(NEQt)s], double Solution_GPU[%(NEQ)s]) 
            {    
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;  // row index of tweakedLS
                int COL = blockIdx.y*blockDim.y+threadIdx.y;  // trivial
                int NEQt = %(NEQt)s;
                
                if (ROW < NEQt && COL == 0) {
                    int PresROW = PresIDX_GPU[ROW];  // row index of LS
                    Solution_GPU[PresROW] = Solution_tweaked_GPU[ROW];
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=False)
            SFFTModule_dict['Restore_Solution'] = _module
        
        # ************************************ Construct Difference ************************************ #

        # <*****> Construct difference in Fourier space <*****> #
        if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:

            # NOTE: As N0, N1 > MAX_THREADS_PER_BLOCK, here TpB == MAX_THREADS_PER_BLOCK
            _refdict = {'N0': N0, 'N1': N1, 'L0': L0, 'L1': L1, 'w0': w0, 'w1': w1, \
                        'Fij': Fij, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, \
                        'SCALE': SCALE, 'TpB': MAX_THREADS_PER_BLOCK}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2],  
                cuDoubleComplex a_ijab_GPU[%(Fijab)s], 
                cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                cuDoubleComplex Kab_Wla_GPU[%(L0)s][%(N0)s][%(N1)s], 
                cuDoubleComplex Kab_Wmb_GPU[%(L1)s][%(N0)s][%(N1)s], 
                cuDoubleComplex b_pq_GPU[%(Fpq)s], 
                cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                cuDoubleComplex PixA_FJ_GPU[%(N0)s][%(N1)s], 
                cuDoubleComplex PixA_FDIFF_GPU[%(N0)s][%(N1)s])
            {       
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int w0 = %(w0)s;
                int w1 = %(w1)s;
                int Fij = %(Fij)s;
                int Fab = %(Fab)s;
                int Fpq = %(Fpq)s;

                double One_re = 1.0;
                double Zero_re = 0.0;
                double Zero_im = 0.0;
                double SCALE_re = %(SCALE)s;
                cuDoubleComplex ZERO = make_cuDoubleComplex(Zero_re, Zero_im);
                cuDoubleComplex ONE = make_cuDoubleComplex(One_re, Zero_im);
                cuDoubleComplex SCA = make_cuDoubleComplex(SCALE_re, Zero_im);
                cuDoubleComplex PVAL = ZERO;
                cuDoubleComplex PVAL_FKab = ZERO;

                __shared__ cuDoubleComplex ShSPixA_FIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                if (ROW < N0 && COL < N1) {
                    for(int ij = 0; ij < Fij; ++ij){
                        ShSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y] = SPixA_FIij_GPU[ij][ROW][COL];
                    }
                }
                __syncthreads();

                if (ROW < N0 && COL < N1) {

                    PVAL = ZERO;
                    PVAL_FKab = ZERO;

                    for(int ab = 0; ab < Fab; ++ab){
                    
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        
                        if (a == 0 && b == 0) {
                            PVAL_FKab = SCA;
                        }
                        
                        if (a != 0 || b != 0) {
                            PVAL_FKab = cuCmul(SCA, cuCsub(cuCmul(Kab_Wla_GPU[w0 + a][ROW][COL], 
                                Kab_Wmb_GPU[w1 + b][ROW][COL]), ONE));
                        }

                        for(int ij = 0; ij < Fij; ++ij){
                            int ijab = ij * Fab + ab;
                            PVAL = cuCadd(PVAL, cuCmul(cuCmul(a_ijab_GPU[ijab], 
                                ShSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y]), PVAL_FKab));
                        }
                    }

                    for(int pq = 0; pq < Fpq; ++pq){
                        PVAL = cuCadd(PVAL, cuCmul(b_pq_GPU[pq], 
                            SPixA_FTpq_GPU[pq][ROW][COL]));
                    }
                    
                    PixA_FDIFF_GPU[ROW][COL] = cuCsub(PixA_FJ_GPU[ROW][COL], PVAL);
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['Construct_FDIFF'] = _module

        if SCALING_MODE == 'SEPARATE-VARYING':

            # NOTE: As N0, N1 > MAX_THREADS_PER_BLOCK, here TpB == MAX_THREADS_PER_BLOCK
            _refdict = {'N0': N0, 'N1': N1, 'L0': L0, 'L1': L1, 'w0': w0, 'w1': w1, \
                        'Fij': Fij, 'Fab': Fab, 'Fpq': Fpq, 'Fijab': Fijab, \
                        'SCALE': SCALE, 'TpB': MAX_THREADS_PER_BLOCK}
            _funcstr = r"""
            #include "cuComplex.h"
            extern "C" __global__ void kmain(int SREF_ijab_GPU[%(Fijab)s][2], int REF_ab_GPU[%(Fab)s][2],  
                cuDoubleComplex a_ijab_GPU[%(Fijab)s], 
                cuDoubleComplex SPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                cuDoubleComplex ScaSPixA_FIij_GPU[%(Fij)s][%(N0)s][%(N1)s], 
                cuDoubleComplex Kab_Wla_GPU[%(L0)s][%(N0)s][%(N1)s], 
                cuDoubleComplex Kab_Wmb_GPU[%(L1)s][%(N0)s][%(N1)s], 
                cuDoubleComplex b_pq_GPU[%(Fpq)s], 
                cuDoubleComplex SPixA_FTpq_GPU[%(Fpq)s][%(N0)s][%(N1)s], 
                cuDoubleComplex PixA_FJ_GPU[%(N0)s][%(N1)s], 
                cuDoubleComplex PixA_FDIFF_GPU[%(N0)s][%(N1)s])
            {       
                int ROW = blockIdx.x*blockDim.x+threadIdx.x;
                int COL = blockIdx.y*blockDim.y+threadIdx.y;
                
                int N0 = %(N0)s;
                int N1 = %(N1)s;
                int w0 = %(w0)s;
                int w1 = %(w1)s;
                int Fij = %(Fij)s;
                int Fab = %(Fab)s;
                int Fpq = %(Fpq)s;

                double One_re = 1.0;
                double Zero_re = 0.0;
                double Zero_im = 0.0;
                double SCALE_re = %(SCALE)s;
                cuDoubleComplex ZERO = make_cuDoubleComplex(Zero_re, Zero_im);
                cuDoubleComplex ONE = make_cuDoubleComplex(One_re, Zero_im);
                cuDoubleComplex SCA = make_cuDoubleComplex(SCALE_re, Zero_im);
                cuDoubleComplex PVAL = ZERO;
                cuDoubleComplex PVAL_FKab = ZERO;

                __shared__ cuDoubleComplex ShSPixA_FIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                if (ROW < N0 && COL < N1) {
                    for(int ij = 0; ij < Fij; ++ij){
                        ShSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y] = SPixA_FIij_GPU[ij][ROW][COL];
                    }
                }

                __shared__ cuDoubleComplex ShScaSPixA_FIij_GPU[%(Fij)s][%(TpB)s][%(TpB)s];
                if (ROW < N0 && COL < N1) {
                    for(int ij = 0; ij < Fij; ++ij){
                        ShScaSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y] = ScaSPixA_FIij_GPU[ij][ROW][COL];
                    }
                }

                __syncthreads();

                if (ROW < N0 && COL < N1) {

                    PVAL = ZERO;
                    PVAL_FKab = ZERO;

                    for(int ab = 0; ab < Fab; ++ab){
                    
                        int a = REF_ab_GPU[ab][0];
                        int b = REF_ab_GPU[ab][1];
                        
                        if (a == 0 && b == 0) {
                            PVAL_FKab = SCA;

                            for(int ij = 0; ij < Fij; ++ij){
                                int ijab = ij * Fab + ab;
                                PVAL = cuCadd(PVAL, cuCmul(cuCmul(a_ijab_GPU[ijab], 
                                    ShScaSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y]), PVAL_FKab));
                            }
                        }
                        
                        if (a != 0 || b != 0) {
                            PVAL_FKab = cuCmul(SCA, cuCsub(cuCmul(Kab_Wla_GPU[w0 + a][ROW][COL], 
                                Kab_Wmb_GPU[w1 + b][ROW][COL]), ONE));

                            for(int ij = 0; ij < Fij; ++ij){
                                int ijab = ij * Fab + ab;
                                PVAL = cuCadd(PVAL, cuCmul(cuCmul(a_ijab_GPU[ijab], 
                                    ShSPixA_FIij_GPU[ij][threadIdx.x][threadIdx.y]), PVAL_FKab));
                            }
                        }
                    }

                    for(int pq = 0; pq < Fpq; ++pq){
                        PVAL = cuCadd(PVAL, cuCmul(b_pq_GPU[pq], 
                            SPixA_FTpq_GPU[pq][ROW][COL]));
                    }
                    
                    PixA_FDIFF_GPU[ROW][COL] = cuCsub(PixA_FJ_GPU[ROW][COL], PVAL);
                }
            }
            """
            _code = _funcstr % _refdict
            _module = cp.RawModule(code=_code, backend=u'nvcc', translate_cucomplex=True)
            SFFTModule_dict['Construct_FDIFF'] = _module

        SFFTConfig = (SFFTParam_dict, SFFTModule_dict)
        if VERBOSE_LEVEL in [1, 2]:
            print('\n --//--//--//--//-- EXIT SFFT COMPILATION --//--//--//--//-- ')

        return SFFTConfig

class SingleSFFTConfigure:
    @staticmethod
    def SSC(NX, NY, KerHW=8, KerSpType='Polynomial', KerSpDegree=2, KerIntKnotX=[], KerIntKnotY=[], \
        SEPARATE_SCALING=True, ScaSpType='Polynomial', ScaSpDegree=0, ScaIntKnotX=[], ScaIntKnotY=[], \
        BkgSpType='Polynomial', BkgSpDegree=2, BkgIntKnotX=[], BkgIntKnotY=[], \
        REGULARIZE_KERNEL=False, IGNORE_LAPLACIAN_KERCENT=True, XY_REGULARIZE=None, WEIGHT_REGULARIZE=None, \
        LAMBDA_REGULARIZE=1e-6, BACKEND_4SUBTRACT='Cupy', MAX_THREADS_PER_BLOCK=8, \
        MINIMIZE_GPU_MEMORY_USAGE=False, NUM_CPU_THREADS_4SUBTRACT=8, VERBOSE_LEVEL=2):

        """
        # Compile Functions for SFFT
        #
        # Arguments:
        # -NX: Image size along X (pix)                                                        | e.g., 1024
        # -NY: Image size along Y (pix)                                                        | e.g., 1024
        # -KerHW: Kernel half width for compilation                                            | e.g., 8
        #
        # -KerSpType: Spatial varaition type of matching kernel                                | ['Polynomial', 'B-Spline']
        # -KerSpDegree: Polynomial/B-Spline degree of kernel spatial varaition                 | [0, 1, 2, 3]
        # -KerIntKnotX: Internal knots of kernel B-Spline spatial varaition along X            | e.g., [256., 512., 768.]
        # -KerIntKnotY: Internal knots of kernel B-Spline spatial varaition along Y            | e.g., [256., 512., 768.]
        #
        # -SEPARATE_SCALING: separate convolution scaling or entangled with matching kernel?   | [True, False]
        # -ScaSpType: Spatial varaition type of convolution scaling                            | ['Polynomial', 'B-Spline']
        # -ScaSpDegree: Polynomial/B-Spline degree of convolution scaling                      | [0, 1, 2, 3]
        # -ScaIntKnotX: Internal knots of scaling B-Spline spatial varaition along X           | e.g., [256., 512., 768.]
        # -ScaIntKnotY: Internal knots of scaling B-Spline spatial varaition along Y           | e.g., [256., 512., 768.]
        #
        # -BkgSpType: Spatial varaition type of differential background                        | ['Polynomial', 'B-Spline']
        # -BkgSpDegree: Polynomial/B-Spline degree of background spatial varaition             | [0, 1, 2, 3]
        # -BkgIntKnotX: Internal knots of background B-Spline spatial varaition along X        | e.g., [256., 512., 768.]
        # -BkgIntKnotY: Internal knots of background B-Spline spatial varaition along Y        | e.g., [256., 512., 768.]
        # 
        # -REGULARIZE_KERNEL: Regularize matching kernel by applying penalty on                | [True, False]
        #    kernel's second derivates using Laplacian matrix
        # -IGNORE_LAPLACIAN_KERCENT: zero out the rows of Laplacian matrix                     | [True, False]
        #    corresponding the kernel center pixels by zeros. 
        #    If True, the regularization will not impose any penalty 
        #    on a delta-function-like matching kernel
        # -XY_REGULARIZE: The coordinates at which the matching kernel regularized.            | e.g., np.array([[64., 64.], 
        #    Numpy array of (x, y) with shape (N_points, 2),                                   |                 [256., 256.]]) 
        #    where x in (0.5, NX+0.5) and y in (0.5, NY+0.5)
        # -WEIGHT_REGULARIZE: The weights of the coordinates sampled for regularization.       | e.g., np.array([1.0, 2.0, ...])
        #    Numpy array of weights with shape (N_points)
        #    -WEIGHT_REGULARIZE = None means uniform weights of 1.0
        # -LAMBDA_REGULARIZE: Tunning paramater lambda for regularization                      | e.g., 1e-6
        #    it controls the strength of penalty on kernel overfitting
        #
        # -BACKEND_4SUBTRACT: The backend with which you perform SFFT subtraction              | ['Cupy', 'Numpy']
        # -MAX_THREADS_PER_BLOCK: Maximum Threads per Block for CUDA configuration             | e.g., 8
        # -MINIMIZE_GPU_MEMORY_USAGE: Minimize the GPU Memory Usage?                           | [True, False]
        # -NUM_CPU_THREADS_4SUBTRACT: The number of CPU threads for Numpy-SFFT subtraction     | e.g., 8
        #
        # -VERBOSE_LEVEL: The level of verbosity, can be 0/1/2: QUIET/NORMAL/FULL              | [0, 1, 2]
        #
        """
        
        if BACKEND_4SUBTRACT == 'Cupy':

            SFFTConfig = SingleSFFTConfigure_Cupy.SSCC(NX=NX, NY=NY, KerHW=KerHW, KerSpType=KerSpType, \
                KerSpDegree=KerSpDegree, KerIntKnotX=KerIntKnotX, KerIntKnotY=KerIntKnotY, \
                SEPARATE_SCALING=SEPARATE_SCALING, ScaSpType=ScaSpType, ScaSpDegree=ScaSpDegree, \
                ScaIntKnotX=ScaIntKnotX, ScaIntKnotY=ScaIntKnotY, BkgSpType=BkgSpType, \
                BkgSpDegree=BkgSpDegree, BkgIntKnotX=BkgIntKnotX, BkgIntKnotY=BkgIntKnotY, \
                REGULARIZE_KERNEL=REGULARIZE_KERNEL, IGNORE_LAPLACIAN_KERCENT=IGNORE_LAPLACIAN_KERCENT, \
                XY_REGULARIZE=XY_REGULARIZE, WEIGHT_REGULARIZE=WEIGHT_REGULARIZE, LAMBDA_REGULARIZE=LAMBDA_REGULARIZE, \
                MAX_THREADS_PER_BLOCK=MAX_THREADS_PER_BLOCK, MINIMIZE_GPU_MEMORY_USAGE=MINIMIZE_GPU_MEMORY_USAGE, \
                VERBOSE_LEVEL=VERBOSE_LEVEL)
        
        if BACKEND_4SUBTRACT == 'Numpy':
            print('MeLOn ERROR: Numpy backend is not supported for B-Spline SFFT in current version! Will implement in future!')
            SFFTConfig = None
        
        return SFFTConfig

class ElementalSFFTSubtract_Cupy:
    @staticmethod
    def ESSC(PixA_I, PixA_J, SFFTConfig, SFFTSolution=None, Subtract=False, \
        VERBOSE_LEVEL=2):
        
        import cupy as cp
        import cupyx.scipy.linalg as cpx_linalg

        def LSSolver(A_GPU, b_GPU):
            lu_piv_GPU = cpx_linalg.lu_factor(A_GPU, overwrite_a=False, check_finite=True)
            x_GPU = cpx_linalg.lu_solve(lu_piv_GPU, b_GPU)
            return x_GPU
        
        def Create_BSplineBasis(N, IntKnot, BSplineDegree):
            BSplineBasis = []
            PixCoord = (1.0+np.arange(N))/N
            Knot = np.concatenate(([0.5]*(BSplineDegree+1), IntKnot, [N+0.5]*(BSplineDegree+1)))/N
            Nc = len(IntKnot) + BSplineDegree + 1    # number of control points/coeffcients
            for idx in range(Nc):
                Coeff = (np.arange(Nc) == idx).astype(float)
                BaseFunc = BSpline(t=Knot, c=Coeff, k=BSplineDegree, extrapolate=False)
                BSplineBasis.append(BaseFunc(PixCoord))
            BSplineBasis = np.array(BSplineBasis)
            return BSplineBasis
        
        def Create_BSplineBasis_Req(N, IntKnot, BSplineDegree, ReqCoord):
            BSplineBasis_Req = []
            Knot = np.concatenate(([0.5]*(BSplineDegree+1), IntKnot, [N+0.5]*(BSplineDegree+1)))/N
            Nc = len(IntKnot) + BSplineDegree + 1    # number of control points/coeffcients
            for idx in range(Nc):
                Coeff = (np.arange(Nc) == idx).astype(float)
                BaseFunc = BSpline(t=Knot, c=Coeff, k=BSplineDegree, extrapolate=False)
                BSplineBasis_Req.append(BaseFunc(ReqCoord))
            BSplineBasis_Req = np.array(BSplineBasis_Req)
            return BSplineBasis_Req
        
        ta = time.time()
        # * Read SFFT parameters
        SFFTParam_dict, SFFTModule_dict = SFFTConfig

        KerHW = SFFTParam_dict['KerHW']
        KerSpType = SFFTParam_dict['KerSpType']
        KerSpDegree = SFFTParam_dict['KerSpDegree']
        KerIntKnotX = SFFTParam_dict['KerIntKnotX']
        KerIntKnotY = SFFTParam_dict['KerIntKnotY']

        SEPARATE_SCALING = SFFTParam_dict['SEPARATE_SCALING']
        if SEPARATE_SCALING:
            ScaSpType = SFFTParam_dict['ScaSpType']
            ScaSpDegree = SFFTParam_dict['ScaSpDegree']
            ScaIntKnotX = SFFTParam_dict['ScaIntKnotX']
            ScaIntKnotY = SFFTParam_dict['ScaIntKnotY']

        BkgSpType = SFFTParam_dict['BkgSpType']
        BkgSpDegree = SFFTParam_dict['BkgSpDegree']
        BkgIntKnotX = SFFTParam_dict['BkgIntKnotX']
        BkgIntKnotY = SFFTParam_dict['BkgIntKnotY']
        
        REGULARIZE_KERNEL = SFFTParam_dict['REGULARIZE_KERNEL']
        IGNORE_LAPLACIAN_KERCENT = SFFTParam_dict['IGNORE_LAPLACIAN_KERCENT']
        XY_REGULARIZE = SFFTParam_dict['XY_REGULARIZE']
        WEIGHT_REGULARIZE = SFFTParam_dict['WEIGHT_REGULARIZE']
        LAMBDA_REGULARIZE = SFFTParam_dict['LAMBDA_REGULARIZE']

        MAX_THREADS_PER_BLOCK = SFFTParam_dict['MAX_THREADS_PER_BLOCK']
        MINIMIZE_GPU_MEMORY_USAGE = SFFTParam_dict['MINIMIZE_GPU_MEMORY_USAGE']

        SCALING_MODE = None
        if not SEPARATE_SCALING:
            SCALING_MODE = 'ENTANGLED'
        elif ScaSpDegree == 0:
            SCALING_MODE = 'SEPARATE-CONSTANT'
        else: SCALING_MODE = 'SEPARATE-VARYING'
        assert SCALING_MODE is not None

        if VERBOSE_LEVEL in [1, 2]:
            print('\n --//--//--//--//-- TRIGGER SFFT SUBTRACTION [Cupy] --//--//--//--//-- ')

            if KerSpType == 'Polynomial':
                print('\n ---//--- Polynomial Kernel | KerSpDegree %d | KerHW %d ---//---' %(KerSpDegree, KerHW))
                if not SEPARATE_SCALING:
                    print('\n ---//--- [ENTANGLED] Polynomial Scaling | KerSpDegree %d ---//---' %KerSpDegree)

            if KerSpType == 'B-Spline':
                print('\n ---//--- B-Spline Kernel | Internal Knots %d,%d | KerSpDegree %d | KerHW %d ---//---' \
                      %(len(KerIntKnotX), len(KerIntKnotY), KerSpDegree, KerHW))
                if not SEPARATE_SCALING: 
                    print('\n ---//--- [ENTANGLED] B-Spline Scaling | Internal Knots %d,%d | KerSpDegree %d ---//---' \
                          %(len(KerIntKnotX), len(KerIntKnotY), KerSpDegree))
            
            if SEPARATE_SCALING:
                if ScaSpType == 'Polynomial':
                    print('\n ---//--- [SEPARATE] Polynomial Scaling | ScaSpDegree %d ---//---' %ScaSpDegree)
                
                if ScaSpType == 'B-Spline':
                    print('\n ---//--- [SEPARATE] B-Spline Scaling | Internal Knots %d,%d | ScaSpDegree %d ---//---' \
                          %(len(ScaIntKnotX), len(ScaIntKnotY), ScaSpDegree))
            
            if BkgSpType == 'Polynomial':
                print('\n ---//--- Polynomial Background | BkgSpDegree %d ---//---' %BkgSpDegree)
            
            if BkgSpType == 'B-Spline':
                print('\n ---//--- B-Spline Background | Internal Knots %d,%d | BkgSpDegree %d ---//---' \
                    %(len(BkgIntKnotX), len(BkgIntKnotY), BkgSpDegree))

        N0 = SFFTParam_dict['N0']               # a.k.a, NX
        N1 = SFFTParam_dict['N1']               # a.k.a, NY
        w0 = SFFTParam_dict['w0']               # a.k.a, KerHW
        w1 = SFFTParam_dict['w1']               # a.k.a, KerHW
        DK = SFFTParam_dict['DK']               # a.k.a, KerSpDegree
        DB = SFFTParam_dict['DB']               # a.k.a, BkgSpDegree
        if SEPARATE_SCALING: 
            DS = SFFTParam_dict['DS']           # a.k.a, PolyScaSpDegree

        SCALE = SFFTParam_dict['SCALE']
        SCALE_L = SFFTParam_dict['SCALE_L']

        L0 = SFFTParam_dict['L0']
        L1 = SFFTParam_dict['L1']
        Fab = SFFTParam_dict['Fab']
        Fi = SFFTParam_dict['Fi']
        Fj = SFFTParam_dict['Fj']
        Fij = SFFTParam_dict['Fij']
        Fp = SFFTParam_dict['Fp']
        Fq = SFFTParam_dict['Fq']
        Fpq = SFFTParam_dict['Fpq']

        if SCALING_MODE == 'SEPARATE-VARYING':
            ScaFi = SFFTParam_dict['ScaFi']
            ScaFj = SFFTParam_dict['ScaFj']
            ScaFij = SFFTParam_dict['ScaFij']
        Fijab = SFFTParam_dict['Fijab']
        
        FOMG = SFFTParam_dict['FOMG']
        FGAM = SFFTParam_dict['FGAM']
        FTHE = SFFTParam_dict['FTHE']
        FPSI = SFFTParam_dict['FPSI']
        FPHI = SFFTParam_dict['FPHI']
        FDEL = SFFTParam_dict['FDEL']
        
        NEQ = SFFTParam_dict['NEQ']
        NEQt = SFFTParam_dict['NEQt']

        # check input image size 
        assert PixA_I.shape == (N0, N1) and PixA_J.shape == (N0, N1)
        
        # * Grid-Block-Thread Managaement [Pixel-Level]
        GPUManage = lambda NT: ((NT-1)//MAX_THREADS_PER_BLOCK + 1, min(NT, MAX_THREADS_PER_BLOCK))
        BpG_PIX0, TpB_PIX0 = GPUManage(N0)
        BpG_PIX1, TpB_PIX1 = GPUManage(N1)
        BpG_PIX, TpB_PIX = (BpG_PIX0, BpG_PIX1), (TpB_PIX0, TpB_PIX1, 1)

        # * Define First-order MultiIndex Reference
        if KerSpType == 'Polynomial':
            REF_ij = np.array([(i, j) for i in range(DK+1) for j in range(DK+1-i)]).astype(np.int32)
        if KerSpType == 'B-Spline':
            REF_ij = np.array([(i, j) for i in range(Fi) for j in range(Fj)]).astype(np.int32)

        if BkgSpType == 'Polynomial':
            REF_pq = np.array([(p, q) for p in range(DB+1) for q in range(DB+1-p)]).astype(np.int32)
        if BkgSpType == 'B-Spline':
            REF_pq = np.array([(p, q) for p in range(Fp) for q in range(Fq)]).astype(np.int32)
        REF_ab = np.array([(a_pos-w0, b_pos-w1) for a_pos in range(L0) for b_pos in range(L1)]).astype(np.int32)

        REF_pq_GPU = cp.array(REF_pq)
        REF_ij_GPU = cp.array(REF_ij)
        REF_ab_GPU = cp.array(REF_ab)

        if SCALING_MODE == 'SEPARATE-VARYING':
            
            if ScaSpType == 'Polynomial':
                ScaREF_ij = np.array(
                    [(i, j) for i in range(DS+1) for j in range(DS+1-i)] \
                    + [(-1, -1)] * (Fij - ScaFij)
                ).astype(np.int32)
                ScaREF_ij_GPU = cp.array(ScaREF_ij)

            if ScaSpType == 'B-Spline':
                ScaREF_ij = np.array(
                    [(i, j) for i in range(ScaFi) for j in range(ScaFj)] \
                    + [(-1, -1)] * (Fij - ScaFij)
                ).astype(np.int32)
                ScaREF_ij_GPU = cp.array(ScaREF_ij)

        # * Define Second-order MultiIndex Reference
        SREF_iji0j0 = np.array([(ij, i0j0) for ij in range(Fij) for i0j0 in range(Fij)]).astype(np.int32)
        SREF_pqp0q0 = np.array([(pq, p0q0) for pq in range(Fpq) for p0q0 in range(Fpq)]).astype(np.int32)
        SREF_ijpq = np.array([(ij, pq) for ij in range(Fij) for pq in range(Fpq)]).astype(np.int32)
        SREF_pqij = np.array([(pq, ij) for pq in range(Fpq) for ij in range(Fij)]).astype(np.int32)
        SREF_ijab = np.array([(ij, ab) for ij in range(Fij) for ab in range(Fab)]).astype(np.int32)

        SREF_iji0j0_GPU = cp.array(SREF_iji0j0)
        SREF_pqp0q0_GPU = cp.array(SREF_pqp0q0)
        SREF_ijpq_GPU = cp.array(SREF_ijpq)
        SREF_pqij_GPU = cp.array(SREF_pqij)
        SREF_ijab_GPU = cp.array(SREF_ijab)

        # * Indices related to Constant Scaling Case
        ij00 = np.arange(w0 * L1 + w1, Fijab, Fab).astype(np.int32)
        ij00_GPU = cp.array(ij00)

        t0 = time.time()
        # * Read input images as C-order arrays
        if not PixA_I.flags['C_CONTIGUOUS']:
            PixA_I = np.ascontiguousarray(PixA_I, np.float64)
            PixA_I_GPU = cp.array(PixA_I)
        else: PixA_I_GPU = cp.array(PixA_I.astype(np.float64))
        
        if not PixA_J.flags['C_CONTIGUOUS']:
            PixA_J = np.ascontiguousarray(PixA_J, np.float64)
            PixA_J_GPU = cp.array(PixA_J)
        else: PixA_J_GPU = cp.array(PixA_J.astype(np.float64))
        dt0 = time.time() - t0
        
        # * Symbol Convention Notes
        #   X (x) / Y (y) ----- pixel row / column index
        #   CX (cx) / CY (cy) ----- ScaledFortranCoord of pixel (x, y) center   
        #   e.g. pixel (x, y) = (3, 5) corresponds (cx, cy) = (4.0/N0, 6.0/N1)
        #   NOTE cx / cy is literally \mathtt{x} / \mathtt{y} in SFFT paper.
        #   NOTE Without special definition, MeLOn convention refers to X (x) / Y (y) as FortranCoord.

        # * Get Spatial Coordinates
        t1 = time.time()
        PixA_X_GPU = cp.zeros((N0, N1), dtype=np.int32)      # row index, [0, N0)
        PixA_Y_GPU = cp.zeros((N0, N1), dtype=np.int32)      # column index, [0, N1)
        PixA_CX_GPU = cp.zeros((N0, N1), dtype=np.float64)   # coordinate.x
        PixA_CY_GPU = cp.zeros((N0, N1), dtype=np.float64)   # coordinate.y 

        _module = SFFTModule_dict['SpatialCoord']
        _func = _module.get_function('kmain')
        _func(args=(PixA_X_GPU, PixA_Y_GPU, PixA_CX_GPU, PixA_CY_GPU), block=TpB_PIX, grid=BpG_PIX)

        # <*****> produce Iij <*****> #
        SPixA_Iij_GPU = cp.zeros((Fij, N0, N1), dtype=np.float64)
        if KerSpType == 'Polynomial':
            _module = SFFTModule_dict['KerSpatial']
            _func = _module.get_function('kmain')
            _func(args=(REF_ij_GPU, PixA_CX_GPU, PixA_CY_GPU, PixA_I_GPU, SPixA_Iij_GPU), \
                block=TpB_PIX, grid=BpG_PIX)
        
        if KerSpType == 'B-Spline':
            KerSplBasisX = Create_BSplineBasis(N=N0, IntKnot=KerIntKnotX, BSplineDegree=DK).astype(np.float64)
            KerSplBasisY = Create_BSplineBasis(N=N1, IntKnot=KerIntKnotY, BSplineDegree=DK).astype(np.float64)
            KerSplBasisX_GPU = cp.array(KerSplBasisX)
            KerSplBasisY_GPU = cp.array(KerSplBasisY)

            _module = SFFTModule_dict['KerSpatial']
            _func = _module.get_function('kmain')
            _func(args=(REF_ij_GPU, KerSplBasisX_GPU, KerSplBasisY_GPU, PixA_I_GPU, SPixA_Iij_GPU), \
                block=TpB_PIX, grid=BpG_PIX)

        if SCALING_MODE == 'SEPARATE-VARYING':

            if ScaSpType == 'Polynomial':
                ScaSPixA_Iij_GPU = cp.zeros((Fij, N0, N1), dtype=np.float64)
                _module = SFFTModule_dict['ScaSpatial']
                _func = _module.get_function('kmain')
                _func(args=(ScaREF_ij_GPU, PixA_CX_GPU, PixA_CY_GPU, PixA_I_GPU, ScaSPixA_Iij_GPU), \
                    block=TpB_PIX, grid=BpG_PIX)

            if ScaSpType == 'B-Spline':
                ScaSplBasisX = Create_BSplineBasis(N=N0, IntKnot=ScaIntKnotX, BSplineDegree=DS).astype(np.float64)
                ScaSplBasisY = Create_BSplineBasis(N=N1, IntKnot=ScaIntKnotY, BSplineDegree=DS).astype(np.float64)
                ScaSplBasisX_GPU = cp.array(ScaSplBasisX)
                ScaSplBasisY_GPU = cp.array(ScaSplBasisY)

                ScaSPixA_Iij_GPU = cp.zeros((Fij, N0, N1), dtype=np.float64)
                _module = SFFTModule_dict['ScaSpatial']
                _func = _module.get_function('kmain')
                _func(args=(ScaREF_ij_GPU, ScaSplBasisX_GPU, ScaSplBasisY_GPU, PixA_I_GPU, ScaSPixA_Iij_GPU), \
                    block=TpB_PIX, grid=BpG_PIX)

        del PixA_I_GPU

        # <*****> produce Tpq <*****> #
        SPixA_Tpq_GPU = cp.zeros((Fpq, N0, N1), dtype=np.float64)
        if BkgSpType == 'Polynomial':
            _module = SFFTModule_dict['BkgSpatial']
            _func = _module.get_function('kmain')
            _func(args=(REF_pq_GPU, PixA_CX_GPU, PixA_CY_GPU, SPixA_Tpq_GPU), \
                block=TpB_PIX, grid=BpG_PIX)
        
        if BkgSpType == 'B-Spline':
            BkgSplBasisX = Create_BSplineBasis(N=N0, IntKnot=BkgIntKnotX, BSplineDegree=DB).astype(np.float64)
            BkgSplBasisY = Create_BSplineBasis(N=N1, IntKnot=BkgIntKnotY, BSplineDegree=DB).astype(np.float64)
            BkgSplBasisX_GPU = cp.array(BkgSplBasisX)
            BkgSplBasisY_GPU = cp.array(BkgSplBasisY)

            _module = SFFTModule_dict['BkgSpatial']
            _func = _module.get_function('kmain')
            _func(args=(REF_pq_GPU, BkgSplBasisX_GPU, BkgSplBasisY_GPU, SPixA_Tpq_GPU), \
                block=TpB_PIX, grid=BpG_PIX)
        
        dt1 = time.time() - t1
        t2 = time.time()

        # * Make DFT of J, Iij, Tpq and their conjugates
        PixA_FJ_GPU = cp.empty((N0, N1), dtype=np.complex128)
        PixA_FJ_GPU[:, :] = PixA_J_GPU.astype(np.complex128)
        PixA_FJ_GPU[:, :] = cp.fft.fft2(PixA_FJ_GPU)
        PixA_FJ_GPU[:, :] *= SCALE

        SPixA_FIij_GPU = cp.empty((Fij, N0, N1), dtype=np.complex128)
        SPixA_FIij_GPU[:, :, :] = SPixA_Iij_GPU.astype(np.complex128)
        for k in range(Fij): 
            SPixA_FIij_GPU[k: k+1] = cp.fft.fft2(SPixA_FIij_GPU[k: k+1])
        SPixA_FIij_GPU[:, :] *= SCALE

        SPixA_FTpq_GPU = cp.empty((Fpq, N0, N1), dtype=np.complex128)
        SPixA_FTpq_GPU[:, :, :] = SPixA_Tpq_GPU.astype(np.complex128)
        for k in range(Fpq): 
            SPixA_FTpq_GPU[k: k+1] = cp.fft.fft2(SPixA_FTpq_GPU[k: k+1])
        SPixA_FTpq_GPU[:, :] *= SCALE

        del PixA_J_GPU
        del SPixA_Iij_GPU
        del SPixA_Tpq_GPU

        PixA_CFJ_GPU = cp.conj(PixA_FJ_GPU)
        SPixA_CFIij_GPU = cp.conj(SPixA_FIij_GPU)
        SPixA_CFTpq_GPU = cp.conj(SPixA_FTpq_GPU)

        if SCALING_MODE == 'SEPARATE-VARYING':
            # TODO: this variable can be too GPU memory consuming
            ScaSPixA_FIij_GPU = cp.empty((Fij, N0, N1), dtype=np.complex128)
            ScaSPixA_FIij_GPU[:, :, :] = ScaSPixA_Iij_GPU.astype(np.complex128)
            for k in range(ScaFij):
                ScaSPixA_FIij_GPU[k: k+1] = cp.fft.fft2(ScaSPixA_FIij_GPU[k: k+1])
            ScaSPixA_FIij_GPU[:, :] *= SCALE

            del ScaSPixA_Iij_GPU
            ScaSPixA_CFIij_GPU = cp.conj(ScaSPixA_FIij_GPU)
        
        dt2 = time.time() - t2
        dta = time.time() - ta

        if VERBOSE_LEVEL in [1, 2]:
            print('\nMeLOn CheckPoint: SFFT-SUBTRACTION Preliminary Steps takes [%.4fs]' %dta)

        if VERBOSE_LEVEL in [2]:
            print('/////   a   ///// Read Input Images  (%.4fs)' %dt0)
            print('/////   b   ///// Spatial Polynomial (%.4fs)' %dt1)
            print('/////   c   ///// DFT-%d             (%.4fs)' %(1 + Fij + Fpq, dt2))

        # * Consider The Major Sources of the Linear System 
        #    OMEGA_i8j8ij   &    DELTA_i8j8pq    ||   THETA_i8j8
        #    PSI_p8q8ij     &    PHI_p8q8pq      ||   DELTA_p8q8
        #
        # - Remarks
        #    a. They have consistent form: Greek(rho, eps) = PreGreek(Mod_N0(rho), Mod_N1(eps))
        #    b. PreGreek = s * Re[DFT(HpGreek)], where HpGreek = GLH * GRH and s is some real-scale
        #    c. Considering the subscripted variables, HpGreek/PreGreek is Complex/Real 3D with shape (F_Greek, N0, N1)
        
        if SFFTSolution is not None:
            Solution = SFFTSolution 
            Solution_GPU = cp.array(Solution.astype(np.float64))
            a_ijab_GPU = Solution_GPU[: Fijab]
            b_pq_GPU = Solution_GPU[Fijab: ]

        if SFFTSolution is None:
            tb = time.time()

            # * Grid-Block-Thread Managaement [for Greek]
            BpG_OMG0, TpB_OMG0 = GPUManage(Fijab)
            BpG_OMG1, TpB_OMG1 = GPUManage(Fijab)
            BpG_OMG, TpB_OMG = (BpG_OMG0, BpG_OMG1), (TpB_OMG0, TpB_OMG1, 1)

            BpG_GAM0, TpB_GAM0 = GPUManage(Fijab)
            BpG_GAM1, TpB_GAM1 = GPUManage(Fpq)
            BpG_GAM, TpB_GAM = (BpG_GAM0, BpG_GAM1), (TpB_GAM0, TpB_GAM1, 1)

            BpG_THE0, TpB_THE0 = GPUManage(Fijab)
            BpG_THE, TpB_THE = (BpG_THE0, 1), (TpB_THE0, 1, 1)

            BpG_PSI0, TpB_PSI0 = GPUManage(Fpq)
            BpG_PSI1, TpB_PSI1 = GPUManage(Fijab)
            BpG_PSI, TpB_PSI = (BpG_PSI0, BpG_PSI1), (TpB_PSI0, TpB_PSI1, 1)

            BpG_PHI0, TpB_PHI0 = GPUManage(Fpq)
            BpG_PHI1, TpB_PHI1 = GPUManage(Fpq)
            BpG_PHI, TpB_PHI = (BpG_PHI0, BpG_PHI1), (TpB_PHI0, TpB_PHI1, 1)

            BpG_DEL0, TpB_DEL0 = GPUManage(Fpq)
            BpG_DEL, TpB_DEL = (BpG_DEL0, 1), (TpB_DEL0, 1, 1)

            if REGULARIZE_KERNEL:

                BpG_LAP0, TpB_LAP0 = GPUManage(Fab)
                BpG_LAP1, TpB_LAP1 = GPUManage(Fab)
                BpG_LAP, TpB_LAP = (BpG_LAP0, BpG_LAP1), (TpB_LAP0, TpB_LAP1, 1)

                BpG_iREG0, TpB_iREG0 = GPUManage(Fab)
                BpG_iREG1, TpB_iREG1 = GPUManage(Fab)
                BpG_iREG, TpB_iREG = (BpG_iREG0, BpG_iREG1), (TpB_iREG0, TpB_iREG1, 1)

                BpG_REG0, TpB_REG0 = GPUManage(Fijab)
                BpG_REG1, TpB_REG1 = GPUManage(Fijab)
                BpG_REG, TpB_REG = (BpG_REG0, BpG_REG1), (TpB_REG0, TpB_REG1, 1)

            LHMAT_GPU = cp.empty((NEQ, NEQ), dtype=np.float64)
            RHb_GPU = cp.empty(NEQ, dtype=np.float64)

            t3 = time.time()
            if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:

                if not MINIMIZE_GPU_MEMORY_USAGE:

                    # <*****> Establish Linear System through OMEGA <*****> #
                    
                    # a. Hadamard Product for OMEGA [HpOMG]
                    _module = SFFTModule_dict['HadProd_OMG']
                    _func = _module.get_function('kmain')
                    HpOMG_GPU = cp.empty((FOMG, N0, N1), dtype=np.complex128)
                    _func(args=(SREF_iji0j0_GPU, SPixA_FIij_GPU, SPixA_CFIij_GPU, HpOMG_GPU), \
                        block=TpB_PIX, grid=BpG_PIX)

                    # b. PreOMG = SCALE * Re[DFT(HpOMG)]
                    for k in range(FOMG):
                        HpOMG_GPU[k: k+1] = cp.fft.fft2(HpOMG_GPU[k: k+1])
                    HpOMG_GPU *= SCALE

                    PreOMG_GPU = cp.empty((FOMG, N0, N1), dtype=np.float64)
                    PreOMG_GPU[:, :, :] = HpOMG_GPU.real
                    PreOMG_GPU[:, :, :] *= SCALE
                    del HpOMG_GPU

                    # c. Fill Linear System with PreOMG
                    _module = SFFTModule_dict['FillLS_OMG']
                    _func = _module.get_function('kmain')
                    _func(args=(SREF_ijab_GPU, REF_ab_GPU, PreOMG_GPU, LHMAT_GPU), \
                        block=TpB_OMG, grid=BpG_OMG)
                    del PreOMG_GPU

                    dt3 = time.time() - t3
                    t4 = time.time()

                    # <*****> Establish Linear System through GAMMA <*****> #

                    # a. Hadamard Product for GAMMA [HpGAM]
                    _module = SFFTModule_dict['HadProd_GAM']
                    _func = _module.get_function('kmain')
                    HpGAM_GPU = cp.empty((FGAM, N0, N1), dtype=np.complex128)
                    _func(args=(SREF_ijpq_GPU, SPixA_FIij_GPU, SPixA_CFTpq_GPU, HpGAM_GPU), \
                        block=TpB_PIX, grid=BpG_PIX)

                    # b. PreGAM = 1 * Re[DFT(HpGAM)]
                    for k in range(FGAM):
                        HpGAM_GPU[k: k+1] = cp.fft.fft2(HpGAM_GPU[k: k+1])
                    HpGAM_GPU *= SCALE

                    PreGAM_GPU = cp.empty((FGAM, N0, N1), dtype=np.float64)
                    PreGAM_GPU[:, :, :] = HpGAM_GPU.real
                    del HpGAM_GPU

                    # c. Fill Linear System with PreGAM
                    _module = SFFTModule_dict['FillLS_GAM']
                    _func = _module.get_function('kmain')
                    _func(args=(SREF_ijab_GPU, REF_ab_GPU, PreGAM_GPU, LHMAT_GPU), \
                        block=TpB_GAM, grid=BpG_GAM)
                    del PreGAM_GPU
                    
                    dt4 = time.time() - t4
                    t5 = time.time()
                    
                    # <*****> Establish Linear System through PSI <*****> #

                    # a. Hadamard Product for PSI [HpPSI]
                    _module = SFFTModule_dict['HadProd_PSI']
                    _func = _module.get_function('kmain')
                    HpPSI_GPU = cp.empty((FPSI, N0, N1), dtype=np.complex128)
                    _func(args=(SREF_pqij_GPU, SPixA_CFIij_GPU, SPixA_FTpq_GPU, HpPSI_GPU), \
                        block=TpB_PIX, grid=BpG_PIX)

                    # b. PrePSI = 1 * Re[DFT(HpPSI)]
                    for k in range(FPSI):
                        HpPSI_GPU[k: k+1] = cp.fft.fft2(HpPSI_GPU[k: k+1])
                    HpPSI_GPU *= SCALE

                    PrePSI_GPU = cp.empty((FPSI, N0, N1), dtype=np.float64)
                    PrePSI_GPU[:, :, :] = HpPSI_GPU.real
                    del HpPSI_GPU

                    # c. Fill Linear System with PrePSI
                    _module = SFFTModule_dict['FillLS_PSI']
                    _func = _module.get_function('kmain')
                    _func(args=(SREF_ijab_GPU, REF_ab_GPU, PrePSI_GPU, LHMAT_GPU), \
                        block=TpB_PSI, grid=BpG_PSI)
                    del PrePSI_GPU

                    dt5 = time.time() - t5
                    t6 = time.time()

                    # <*****> Establish Linear System through PHI <*****> #

                    # a. Hadamard Product for PHI  [HpPHI]
                    _module = SFFTModule_dict['HadProd_PHI']
                    _func = _module.get_function('kmain')
                    HpPHI_GPU = cp.empty((FPHI, N0, N1), dtype=np.complex128)
                    _func(args=(SREF_pqp0q0_GPU, SPixA_FTpq_GPU, SPixA_CFTpq_GPU, HpPHI_GPU), \
                        block=TpB_PIX, grid=BpG_PIX)

                    # b. PrePHI = SCALE_L * Re[DFT(HpPHI)]
                    for k in range(FPHI):
                        HpPHI_GPU[k: k+1] = cp.fft.fft2(HpPHI_GPU[k: k+1])
                    HpPHI_GPU *= SCALE

                    PrePHI_GPU = cp.empty((FPHI, N0, N1), dtype=np.float64)
                    PrePHI_GPU[:, :, :] = HpPHI_GPU.real
                    PrePHI_GPU[:, :, :] *= SCALE_L
                    del HpPHI_GPU

                    # c. Fill Linear System with PrePHI
                    _module = SFFTModule_dict['FillLS_PHI']
                    _func = _module.get_function('kmain')
                    _func(args=(PrePHI_GPU, LHMAT_GPU), block=TpB_PHI, grid=BpG_PHI)
                    del PrePHI_GPU

                if MINIMIZE_GPU_MEMORY_USAGE:

                    # <*****> Establish Linear System through OMEGA <*****> #

                    for cIdx in range(FOMG):

                        # a. Hadamard Product for OMEGA [HpOMG]
                        _module = SFFTModule_dict['HadProd_OMG']
                        _func = _module.get_function('kmain')
                        cHpOMG_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_iji0j0_GPU, SPixA_FIij_GPU, SPixA_CFIij_GPU, cIdx, cHpOMG_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)
                        
                        # b. PreOMG = SCALE * Re[DFT(HpOMG)]
                        cHpOMG_GPU = cp.fft.fft2(cHpOMG_GPU)
                        cHpOMG_GPU *= SCALE

                        cPreOMG_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreOMG_GPU[:, :] = cHpOMG_GPU.real
                        cPreOMG_GPU[:, :] *= SCALE
                        del cHpOMG_GPU

                        # c. Fill Linear System with PreOMG
                        _module = SFFTModule_dict['FillLS_OMG']
                        _func = _module.get_function('kmain')
                        _func(args=(SREF_ijab_GPU, REF_ab_GPU, cIdx, cPreOMG_GPU, LHMAT_GPU), \
                            block=TpB_OMG, grid=BpG_OMG)
                        del cPreOMG_GPU

                    dt3 = time.time() - t3
                    t4 = time.time()

                    # <*****> Establish Linear System through GAMMA <*****> #

                    for cIdx in range(FGAM):

                        # a. Hadamard Product for GAMMA [HpGAM]
                        _module = SFFTModule_dict['HadProd_GAM']
                        _func = _module.get_function('kmain')
                        cHpGAM_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_ijpq_GPU, SPixA_FIij_GPU, SPixA_CFTpq_GPU, cIdx, cHpGAM_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b. PreGAM = 1 * Re[DFT(HpGAM)]
                        cHpGAM_GPU = cp.fft.fft2(cHpGAM_GPU)
                        cHpGAM_GPU *= SCALE

                        cPreGAM_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreGAM_GPU[:, :] = cHpGAM_GPU.real
                        del cHpGAM_GPU

                        # c. Fill Linear System with PreGAM
                        _module = SFFTModule_dict['FillLS_GAM']
                        _func = _module.get_function('kmain')
                        _func(args=(SREF_ijab_GPU, REF_ab_GPU, cIdx, cPreGAM_GPU, LHMAT_GPU), \
                            block=TpB_GAM, grid=BpG_GAM)
                        del cPreGAM_GPU

                    dt4 = time.time() - t4
                    t5 = time.time()

                    # <*****> Establish Linear System through PSI <*****> #

                    for cIdx in range(FPSI):

                        # a. Hadamard Product for PSI [HpPSI]
                        _module = SFFTModule_dict['HadProd_PSI']
                        _func = _module.get_function('kmain')
                        cHpPSI_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_pqij_GPU, SPixA_CFIij_GPU, SPixA_FTpq_GPU, cIdx, cHpPSI_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b. PrePSI = 1 * Re[DFT(HpPSI)]
                        cHpPSI_GPU = cp.fft.fft2(cHpPSI_GPU)
                        cHpPSI_GPU *= SCALE

                        cPrePSI_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPrePSI_GPU[:, :] = cHpPSI_GPU.real
                        del cHpPSI_GPU

                        # c. Fill Linear System with PrePSI
                        _module = SFFTModule_dict['FillLS_PSI']
                        _func = _module.get_function('kmain')
                        _func(args=(SREF_ijab_GPU, REF_ab_GPU, cIdx, cPrePSI_GPU, LHMAT_GPU), \
                            block=TpB_PSI, grid=BpG_PSI)
                        del cPrePSI_GPU

                    dt5 = time.time() - t5
                    t6 = time.time()

                    # <*****> Establish Linear System through PHI <*****> #

                    for cIdx in range(FPHI):

                        # a. Hadamard Product for PHI  [HpPHI]
                        _module = SFFTModule_dict['HadProd_PHI']
                        _func = _module.get_function('kmain')
                        cHpPHI_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_pqp0q0_GPU, SPixA_FTpq_GPU, SPixA_CFTpq_GPU, cIdx, cHpPHI_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b. PrePHI = SCALE_L * Re[DFT(HpPHI)]
                        cHpPHI_GPU = cp.fft.fft2(cHpPHI_GPU)
                        cHpPHI_GPU *= SCALE

                        cPrePHI_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPrePHI_GPU[:, :] = cHpPHI_GPU.real
                        cPrePHI_GPU[:, :] *= SCALE_L
                        del cHpPHI_GPU

                        # c. Fill Linear System with PrePHI
                        _module = SFFTModule_dict['FillLS_PHI']
                        _func = _module.get_function('kmain')
                        _func(args=(cIdx, cPrePHI_GPU, LHMAT_GPU), block=TpB_PHI, grid=BpG_PHI)
                        del cPrePHI_GPU
                
                dt6 = time.time() - t6
                t7 = time.time()

                # <*****> Establish Linear System through THETA & DELTA <*****> #

                # a1. Hadamard Product for THETA [HpTHE]
                _module = SFFTModule_dict['HadProd_THE']
                _func = _module.get_function('kmain')
                HpTHE_GPU = cp.empty((FTHE, N0, N1), dtype=np.complex128)
                _func(args=(SPixA_FIij_GPU, PixA_CFJ_GPU, HpTHE_GPU), block=TpB_PIX, grid=BpG_PIX)

                # a2. Hadamard Product for DELTA [HpDEL]
                _module = SFFTModule_dict['HadProd_DEL']
                _func = _module.get_function('kmain')
                HpDEL_GPU = cp.empty((FDEL, N0, N1), dtype=np.complex128)
                _func(args=(SPixA_FTpq_GPU, PixA_CFJ_GPU, HpDEL_GPU), block=TpB_PIX, grid=BpG_PIX)

                # b1. PreTHE = 1 * Re[DFT(HpTHE)]
                # b2. PreDEL = SCALE_L * Re[DFT(HpDEL)]
                for k in range(FTHE):
                    HpTHE_GPU[k: k+1] = cp.fft.fft2(HpTHE_GPU[k: k+1])
                HpTHE_GPU[:, :, :] *= SCALE
                
                for k in range(FDEL):
                    HpDEL_GPU[k: k+1] = cp.fft.fft2(HpDEL_GPU[k: k+1])
                HpDEL_GPU[:, :, :] *= SCALE

                PreTHE_GPU = cp.empty((FTHE, N0, N1), dtype=np.float64)
                PreTHE_GPU[:, :, :] = HpTHE_GPU.real
                del HpTHE_GPU
                
                PreDEL_GPU = cp.empty((FDEL, N0, N1), dtype=np.float64)
                PreDEL_GPU[:, :, :] = HpDEL_GPU.real
                PreDEL_GPU[:, :, :] *= SCALE_L
                del HpDEL_GPU
                
                # c1. Fill Linear System with PreTHE
                _module = SFFTModule_dict['FillLS_THE']
                _func = _module.get_function('kmain')
                _func(args=(SREF_ijab_GPU, REF_ab_GPU, PreTHE_GPU, RHb_GPU), \
                    block=TpB_THE, grid=BpG_THE)
                del PreTHE_GPU

                # c2. Fill Linear System with PreDEL
                _module = SFFTModule_dict['FillLS_DEL']
                _func = _module.get_function('kmain')
                _func(args=(PreDEL_GPU, RHb_GPU), block=TpB_DEL, grid=BpG_DEL)
                del PreDEL_GPU

            if SCALING_MODE == 'SEPARATE-VARYING':
                assert MINIMIZE_GPU_MEMORY_USAGE
                
                if MINIMIZE_GPU_MEMORY_USAGE:

                    # <*****> Establish Linear System through OMEGA <*****> #

                    for cIdx in range(FOMG):    
                        
                        # a11. Hadamard Product for OMEGA_11 [HpOMG11]
                        _module = SFFTModule_dict['HadProd_OMG11']
                        _func = _module.get_function('kmain')
                        cHpOMG11_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_iji0j0_GPU, SPixA_FIij_GPU, SPixA_CFIij_GPU, cIdx, cHpOMG11_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)
                        
                        # b11. PreOMG11 = SCALE * Re[DFT(HpOMG11)]
                        cHpOMG11_GPU = cp.fft.fft2(cHpOMG11_GPU)
                        cHpOMG11_GPU *= SCALE

                        cPreOMG11_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreOMG11_GPU[:, :] = cHpOMG11_GPU.real
                        cPreOMG11_GPU[:, :] *= SCALE
                        del cHpOMG11_GPU

                        # a01. Hadamard Product for OMEGA_01 [HpOMG01]
                        _module = SFFTModule_dict['HadProd_OMG01']
                        _func = _module.get_function('kmain')
                        cHpOMG01_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_iji0j0_GPU, ScaSPixA_FIij_GPU, SPixA_CFIij_GPU, cIdx, cHpOMG01_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)
                        
                        # b01. PreOMG01 = SCALE * Re[DFT(HpOMG01)]
                        cHpOMG01_GPU = cp.fft.fft2(cHpOMG01_GPU)
                        cHpOMG01_GPU *= SCALE

                        cPreOMG01_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreOMG01_GPU[:, :] = cHpOMG01_GPU.real
                        cPreOMG01_GPU[:, :] *= SCALE
                        del cHpOMG01_GPU

                        # a10. Hadamard Product for OMEGA_10 [HpOMG10]
                        _module = SFFTModule_dict['HadProd_OMG10']
                        _func = _module.get_function('kmain')
                        cHpOMG10_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_iji0j0_GPU, SPixA_FIij_GPU, ScaSPixA_CFIij_GPU, cIdx, cHpOMG10_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)
                        
                        # b10. PreOMG10 = SCALE * Re[DFT(HpOMG10)]
                        cHpOMG10_GPU = cp.fft.fft2(cHpOMG10_GPU)
                        cHpOMG10_GPU *= SCALE

                        cPreOMG10_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreOMG10_GPU[:, :] = cHpOMG10_GPU.real
                        cPreOMG10_GPU[:, :] *= SCALE
                        del cHpOMG10_GPU

                        # a00. Hadamard Product for OMEGA_00 [HpOMG00]
                        _module = SFFTModule_dict['HadProd_OMG00']
                        _func = _module.get_function('kmain')
                        cHpOMG00_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_iji0j0_GPU, ScaSPixA_FIij_GPU, ScaSPixA_CFIij_GPU, cIdx, cHpOMG00_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)
                        
                        # b00. PreOMG00 = SCALE * Re[DFT(HpOMG00)]
                        cHpOMG00_GPU = cp.fft.fft2(cHpOMG00_GPU)
                        cHpOMG00_GPU *= SCALE

                        cPreOMG00_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreOMG00_GPU[:, :] = cHpOMG00_GPU.real
                        cPreOMG00_GPU[:, :] *= SCALE
                        del cHpOMG00_GPU

                        # c. Fill Linear System with PreOMG
                        _module = SFFTModule_dict['FillLS_OMG']
                        _func = _module.get_function('kmain')
                        _func(args=(SREF_ijab_GPU, REF_ab_GPU, cIdx, \
                            cPreOMG11_GPU, cPreOMG01_GPU, cPreOMG10_GPU, cPreOMG00_GPU, LHMAT_GPU), \
                            block=TpB_OMG, grid=BpG_OMG)
                        
                        del cPreOMG11_GPU
                        del cPreOMG01_GPU
                        del cPreOMG10_GPU
                        del cPreOMG00_GPU

                    dt3 = time.time() - t3
                    t4 = time.time()

                    # <*****> Establish Linear System through GAMMA <*****> #

                    for cIdx in range(FGAM):

                        # a1. Hadamard Product for GAMMA_1 [HpGAM1]
                        _module = SFFTModule_dict['HadProd_GAM1']
                        _func = _module.get_function('kmain')
                        cHpGAM1_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_ijpq_GPU, SPixA_FIij_GPU, SPixA_CFTpq_GPU, cIdx, cHpGAM1_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b1. PreGAM1 = 1 * Re[DFT(HpGAM1)]
                        cHpGAM1_GPU = cp.fft.fft2(cHpGAM1_GPU)
                        cHpGAM1_GPU *= SCALE

                        cPreGAM1_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreGAM1_GPU[:, :] = cHpGAM1_GPU.real
                        del cHpGAM1_GPU
                        
                        # a0. Hadamard Product for GAMMA_0 [HpGAM0]
                        _module = SFFTModule_dict['HadProd_GAM0']
                        _func = _module.get_function('kmain')
                        cHpGAM0_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_ijpq_GPU, ScaSPixA_FIij_GPU, SPixA_CFTpq_GPU, cIdx, cHpGAM0_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b0. PreGAM0 = 1 * Re[DFT(HpGAM0)]
                        cHpGAM0_GPU = cp.fft.fft2(cHpGAM0_GPU)
                        cHpGAM0_GPU *= SCALE

                        cPreGAM0_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPreGAM0_GPU[:, :] = cHpGAM0_GPU.real
                        del cHpGAM0_GPU

                        # c. Fill Linear System with PreGAM
                        _module = SFFTModule_dict['FillLS_GAM']
                        _func = _module.get_function('kmain')
                        _func(args=(SREF_ijab_GPU, REF_ab_GPU, cIdx, cPreGAM1_GPU, cPreGAM0_GPU, LHMAT_GPU), \
                            block=TpB_GAM, grid=BpG_GAM)
                        
                        del cPreGAM1_GPU
                        del cPreGAM0_GPU

                    dt4 = time.time() - t4
                    t5 = time.time()

                    # <*****> Establish Linear System through PSI <*****> #

                    for cIdx in range(FPSI):

                        # a1. Hadamard Product for PSI_1 [HpPSI1]
                        _module = SFFTModule_dict['HadProd_PSI1']
                        _func = _module.get_function('kmain')
                        cHpPSI1_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_pqij_GPU, SPixA_CFIij_GPU, SPixA_FTpq_GPU, cIdx, cHpPSI1_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b1. PrePSI1 = 1 * Re[DFT(HpPSI1)]
                        cHpPSI1_GPU = cp.fft.fft2(cHpPSI1_GPU)
                        cHpPSI1_GPU *= SCALE

                        cPrePSI1_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPrePSI1_GPU[:, :] = cHpPSI1_GPU.real
                        del cHpPSI1_GPU

                        # a0. Hadamard Product for PSI_0 [HpPSI0]
                        _module = SFFTModule_dict['HadProd_PSI0']
                        _func = _module.get_function('kmain')
                        cHpPSI0_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_pqij_GPU, ScaSPixA_CFIij_GPU, SPixA_FTpq_GPU, cIdx, cHpPSI0_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b1. PrePSI0 = 1 * Re[DFT(HpPSI0)]
                        cHpPSI0_GPU = cp.fft.fft2(cHpPSI0_GPU)
                        cHpPSI0_GPU *= SCALE

                        cPrePSI0_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPrePSI0_GPU[:, :] = cHpPSI0_GPU.real
                        del cHpPSI0_GPU

                        # c. Fill Linear System with PrePSI
                        _module = SFFTModule_dict['FillLS_PSI']
                        _func = _module.get_function('kmain')
                        _func(args=(SREF_ijab_GPU, REF_ab_GPU, cIdx, cPrePSI1_GPU, cPrePSI0_GPU, LHMAT_GPU), \
                            block=TpB_PSI, grid=BpG_PSI)
                        
                        del cPrePSI1_GPU
                        del cPrePSI0_GPU

                    dt5 = time.time() - t5
                    t6 = time.time()

                    # <*****> Establish Linear System through PHI <*****> #

                    for cIdx in range(FPHI):
                        # a. Hadamard Product for PHI [HpPHI]
                        _module = SFFTModule_dict['HadProd_PHI']
                        _func = _module.get_function('kmain')
                        cHpPHI_GPU = cp.empty((N0, N1), dtype=np.complex128)
                        _func(args=(SREF_pqp0q0_GPU, SPixA_FTpq_GPU, SPixA_CFTpq_GPU, cIdx, cHpPHI_GPU), \
                            block=TpB_PIX, grid=BpG_PIX)

                        # b. PrePHI = SCALE_L * Re[DFT(HpPHI)]
                        cHpPHI_GPU = cp.fft.fft2(cHpPHI_GPU)
                        cHpPHI_GPU *= SCALE

                        cPrePHI_GPU = cp.empty((N0, N1), dtype=np.float64)
                        cPrePHI_GPU[:, :] = cHpPHI_GPU.real
                        cPrePHI_GPU[:, :] *= SCALE_L
                        del cHpPHI_GPU

                        # c. Fill Linear System with PrePHI
                        _module = SFFTModule_dict['FillLS_PHI']
                        _func = _module.get_function('kmain')
                        _func(args=(cIdx, cPrePHI_GPU, LHMAT_GPU), block=TpB_PHI, grid=BpG_PHI)
                        del cPrePHI_GPU

                dt6 = time.time() - t6
                t7 = time.time()
                
                # <*****> Establish Linear System through THETA & DELTA <*****> #

                # a1. Hadamard Product for THETA_1 [HpTHE1]
                _module = SFFTModule_dict['HadProd_THE1']
                _func = _module.get_function('kmain')
                HpTHE1_GPU = cp.empty((FTHE, N0, N1), dtype=np.complex128)
                _func(args=(SPixA_FIij_GPU, PixA_CFJ_GPU, HpTHE1_GPU), block=TpB_PIX, grid=BpG_PIX)

                # a0. Hadamard Product for THETA_0 [HpTHE0]
                _module = SFFTModule_dict['HadProd_THE0']
                _func = _module.get_function('kmain')
                HpTHE0_GPU = cp.empty((FTHE, N0, N1), dtype=np.complex128)
                _func(args=(ScaSPixA_FIij_GPU, PixA_CFJ_GPU, HpTHE0_GPU), block=TpB_PIX, grid=BpG_PIX)

                # x. Hadamard Product for DELTA [HpDEL]
                _module = SFFTModule_dict['HadProd_DEL']
                _func = _module.get_function('kmain')
                HpDEL_GPU = cp.empty((FDEL, N0, N1), dtype=np.complex128)
                _func(args=(SPixA_FTpq_GPU, PixA_CFJ_GPU, HpDEL_GPU), block=TpB_PIX, grid=BpG_PIX)

                # b1. PreTHE1 = 1 * Re[DFT(HpTHE1)]
                # b0. PreTHE0 = 1 * Re[DFT(HpTHE0)]
                # y. PreDEL = SCALE_L * Re[DFT(HpDEL)]

                for k in range(FTHE):
                    HpTHE1_GPU[k: k+1] = cp.fft.fft2(HpTHE1_GPU[k: k+1])
                HpTHE1_GPU[:, :, :] *= SCALE

                PreTHE1_GPU = cp.empty((FTHE, N0, N1), dtype=np.float64)
                PreTHE1_GPU[:, :, :] = HpTHE1_GPU.real
                del HpTHE1_GPU

                for k in range(FTHE):
                    HpTHE0_GPU[k: k+1] = cp.fft.fft2(HpTHE0_GPU[k: k+1])
                HpTHE0_GPU[:, :, :] *= SCALE

                PreTHE0_GPU = cp.empty((FTHE, N0, N1), dtype=np.float64)
                PreTHE0_GPU[:, :, :] = HpTHE0_GPU.real
                del HpTHE0_GPU

                for k in range(FDEL):
                    HpDEL_GPU[k: k+1] = cp.fft.fft2(HpDEL_GPU[k: k+1])
                HpDEL_GPU[:, :, :] *= SCALE

                PreDEL_GPU = cp.empty((FDEL, N0, N1), dtype=np.float64)
                PreDEL_GPU[:, :, :] = HpDEL_GPU.real
                PreDEL_GPU[:, :, :] *= SCALE_L
                del HpDEL_GPU

                # c. Fill Linear System with PreTHE
                _module = SFFTModule_dict['FillLS_THE']
                _func = _module.get_function('kmain')
                _func(args=(SREF_ijab_GPU, REF_ab_GPU, PreTHE1_GPU, PreTHE0_GPU, RHb_GPU), \
                    block=TpB_THE, grid=BpG_THE)
                
                del PreTHE1_GPU
                del PreTHE0_GPU

                # z. Fill Linear System with PreDEL
                _module = SFFTModule_dict['FillLS_DEL']
                _func = _module.get_function('kmain')
                _func(args=(PreDEL_GPU, RHb_GPU), block=TpB_DEL, grid=BpG_DEL)
                del PreDEL_GPU
                
            dt7 = time.time() - t7
            t8 = time.time()

            # <*****> Regularize Linear System <*****> #

            if REGULARIZE_KERNEL:
                
                NREG = XY_REGULARIZE.shape[0]
                CX_REG = XY_REGULARIZE[:, 0]/N0
                CY_REG = XY_REGULARIZE[:, 1]/N1

                if KerSpType == 'Polynomial':

                    SPMAT = np.array([
                        CX_REG**i * CY_REG**j 
                        for i in range(DK+1) for j in range(DK+1-i)
                    ])

                if KerSpType == 'B-Spline':
                    KerSplBasisX_REG = Create_BSplineBasis_Req(N=N0, IntKnot=KerIntKnotX, BSplineDegree=DK, ReqCoord=CX_REG)
                    KerSplBasisY_REG = Create_BSplineBasis_Req(N=N1, IntKnot=KerIntKnotY, BSplineDegree=DK, ReqCoord=CY_REG)
                    
                    SPMAT = np.array([
                        KerSplBasisX_REG[i] * KerSplBasisY_REG[j]
                        for i in range(Fi) for j in range(Fj)
                    ])

                SPMAT_GPU = cp.array(SPMAT, dtype=np.float64)

                if SCALING_MODE == 'SEPARATE-VARYING':

                    if ScaSpType == 'Polynomial':

                        ScaSPMAT = np.array([
                            CX_REG**i * CY_REG**j 
                            for i in range(DS+1) for j in range(DS+1-i)
                        ])

                    if ScaSpType == 'B-Spline':
                        ScaSplBasisX_REG = Create_BSplineBasis_Req(N=N0, IntKnot=ScaIntKnotX, BSplineDegree=DS, ReqCoord=CX_REG)
                        ScaSplBasisY_REG = Create_BSplineBasis_Req(N=N1, IntKnot=ScaIntKnotY, BSplineDegree=DS, ReqCoord=CY_REG)
                        
                        ScaSPMAT = np.array([
                            ScaSplBasisX_REG[i] * ScaSplBasisY_REG[j]
                            for i in range(ScaFi) for j in range(ScaFj)
                        ])
                    
                    # placeholder
                    if ScaFij < Fij:
                        ScaSPMAT = np.concatenate((
                            ScaSPMAT, 
                            np.zeros((Fij-ScaFij, NREG), dtype=np.float64)
                            ), axis=0
                        )

                    ScaSPMAT_GPU = cp.array(ScaSPMAT, dtype=np.float64)

                if WEIGHT_REGULARIZE is None:
                    SSTMAT_GPU = cp.matmul(SPMAT_GPU, SPMAT_GPU.T)/NREG   # symmetric
                    if SCALING_MODE == 'SEPARATE-VARYING':
                        CSSTMAT_GPU = cp.matmul(SPMAT_GPU, ScaSPMAT_GPU.T)/NREG     # C: Cross
                        DSSTMAT_GPU = cp.matmul(ScaSPMAT_GPU, ScaSPMAT_GPU.T)/NREG  # D: Double, symmetric

                if WEIGHT_REGULARIZE is not None:
                    # weighted average over regularization points
                    WSPMAT = np.diag(WEIGHT_REGULARIZE)
                    WSPMAT /= np.sum(WEIGHT_REGULARIZE)  # normalize to have unit sum
                    WSPMAT_GPU = cp.array(WSPMAT, dtype=np.float64)

                    SSTMAT_GPU = cp.matmul(cp.matmul(SPMAT_GPU, WSPMAT_GPU), SPMAT_GPU.T)   # symmetric
                    if SCALING_MODE == 'SEPARATE-VARYING':
                        CSSTMAT_GPU = cp.matmul(cp.matmul(SPMAT_GPU, WSPMAT_GPU), ScaSPMAT_GPU.T)   # C: Cross
                        DSSTMAT_GPU = cp.matmul(cp.matmul(ScaSPMAT_GPU, WSPMAT_GPU), ScaSPMAT_GPU.T)   # D: Double, symmetric

                # Create Laplacian Matrix
                LAPMAT = np.zeros((Fab, Fab)).astype(np.int32)
                RR, CC = np.mgrid[0: L0, 0: L1]
                RRF = RR.flatten().astype(np.int32)
                CCF = CC.flatten().astype(np.int32)

                AdCOUNT = signal.correlate2d(
                    np.ones((L0, L1)), 
                    np.array([[0, 1, 0],
                              [1, 0, 1],
                              [0, 1, 0]]),
                    mode='same', 
                    boundary='fill',
                    fillvalue=0
                ).astype(np.int32)

                # fill diagonal elements
                KIDX = np.arange(Fab)
                LAPMAT[KIDX, KIDX] = AdCOUNT.flatten()[KIDX]

                LAPMAT_GPU = cp.array(LAPMAT, dtype=np.int32)
                RRF_GPU = cp.array(RRF, dtype=np.int32)
                CCF_GPU = cp.array(CCF, dtype=np.int32)

                # fill non-diagonal 
                _module = SFFTModule_dict['fill_lapmat_nondiagonal']
                _func = _module.get_function('kmain')
                _func(args=(LAPMAT_GPU, RRF_GPU, CCF_GPU), block=TpB_LAP, grid=BpG_LAP)

                # zero-out kernel-center rows of laplacian matrix
                # FIXME: one can multiply user-defined weights of kernel pixels 
                if IGNORE_LAPLACIAN_KERCENT:
                    
                    LAPMAT_GPU[(w0-1)*L1+w1, :] = 0.0 
                    LAPMAT_GPU[w0*L1+w1-1, :] = 0.0
                    LAPMAT_GPU[w0*L1+w1, :] = 0.0
                    LAPMAT_GPU[w0*L1+w1+1, :] = 0.0
                    LAPMAT_GPU[(w0+1)*L1+w1, :] = 0.0

                LTLMAT_GPU = cp.matmul(LAPMAT_GPU.T, LAPMAT_GPU)   # symmetric
                
                # Create iREGMAT
                iREGMAT_GPU = cp.zeros((Fab, Fab), dtype=np.int32)
                _module = SFFTModule_dict['fill_iregmat']    
                _func = _module.get_function('kmain')
                _func(args=(iREGMAT_GPU, LTLMAT_GPU), block=TpB_iREG, grid=BpG_iREG)

                # Create REGMAT
                REGMAT_GPU = cp.zeros((NEQ, NEQ), dtype=np.float64)
                if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:
                    _module = SFFTModule_dict['fill_regmat']    
                    _func = _module.get_function('kmain')
                    _func(args=(iREGMAT_GPU, SSTMAT_GPU, REGMAT_GPU), block=TpB_REG, grid=BpG_REG)

                if SCALING_MODE == 'SEPARATE-VARYING':
                    _module = SFFTModule_dict['fill_regmat']    
                    _func = _module.get_function('kmain')
                    _func(args=(iREGMAT_GPU, SSTMAT_GPU, CSSTMAT_GPU, DSSTMAT_GPU, REGMAT_GPU), 
                          block=TpB_REG, grid=BpG_REG)

                # UPDATE LHMAT
                LHMAT_GPU += LAMBDA_REGULARIZE * REGMAT_GPU
            
            # <*****> Tweak Linear System <*****> #

            if SCALING_MODE == 'ENTANGLED' or (SCALING_MODE == 'SEPARATE-VARYING' and NEQt == NEQ):
                pass

            if SCALING_MODE == 'SEPARATE-CONSTANT':
                
                LHMAT_tweaked_GPU = cp.empty((NEQt, NEQt), dtype=np.float64)
                RHb_tweaked_GPU = cp.empty(NEQt, dtype=np.float64)

                PresIDX = np.setdiff1d(np.arange(NEQ), ij00[1:], assume_unique=True).astype(np.int32)
                assert np.all(PresIDX[:-1] < PresIDX[1:])
                assert PresIDX[ij00[0]] == ij00[0]
                PresIDX_GPU = cp.array(PresIDX)

                BpG_tweak_PA, TpB_tweak_PA = GPUManage(NEQt)   # per axis
                BpG_tweak, TpB_tweak = (BpG_tweak_PA, BpG_tweak_PA), (TpB_tweak_PA, TpB_tweak_PA, 1)

                if KerSpType == 'Polynomial':
                    _module = SFFTModule_dict['TweakLS']
                    _func = _module.get_function('kmain')
                    _func(args=(LHMAT_GPU, RHb_GPU, PresIDX_GPU, LHMAT_tweaked_GPU, \
                        RHb_tweaked_GPU), block=TpB_tweak, grid=BpG_tweak)
                
                if KerSpType == 'B-Spline':
                    _module = SFFTModule_dict['TweakLS']
                    _func = _module.get_function('kmain')
                    _func(args=(LHMAT_GPU, RHb_GPU, PresIDX_GPU, ij00_GPU, \
                        LHMAT_tweaked_GPU, RHb_tweaked_GPU), block=TpB_tweak, grid=BpG_tweak)
            
            if SCALING_MODE == 'SEPARATE-VARYING' and NEQt < NEQ:

                LHMAT_tweaked_GPU = cp.empty((NEQt, NEQt), dtype=np.float64)
                RHb_tweaked_GPU = cp.empty(NEQt, dtype=np.float64)

                PresIDX = np.setdiff1d(np.arange(NEQ), ij00[ScaFij:], assume_unique=True).astype(np.int32)
                assert np.all(PresIDX[:-1] < PresIDX[1:])
                assert PresIDX[ij00[0]] == ij00[0]
                PresIDX_GPU = cp.array(PresIDX)

                BpG_tweak_PA, TpB_tweak_PA = GPUManage(NEQt)   # per axis
                BpG_tweak, TpB_tweak = (BpG_tweak_PA, BpG_tweak_PA), (TpB_tweak_PA, TpB_tweak_PA, 1)
                
                _module = SFFTModule_dict['TweakLS']
                _func = _module.get_function('kmain')
                _func(args=(LHMAT_GPU, RHb_GPU, PresIDX_GPU, LHMAT_tweaked_GPU, \
                    RHb_tweaked_GPU), block=TpB_tweak, grid=BpG_tweak)
            
            # <*****> Solve Linear System & Restore Solution <*****> #

            if SCALING_MODE == 'ENTANGLED' or (SCALING_MODE == 'SEPARATE-VARYING' and NEQt == NEQ):
                Solution_GPU = LSSolver(A_GPU=LHMAT_GPU, b_GPU=RHb_GPU)

            if SCALING_MODE == 'SEPARATE-CONSTANT':
                Solution_tweaked_GPU = LSSolver(A_GPU=LHMAT_tweaked_GPU, b_GPU=RHb_tweaked_GPU)
                
                BpG_restore, TpB_restore = GPUManage(NEQt)
                BpG_restore, TpB_restore = (BpG_restore, 1), (TpB_restore, 1, 1)

                if KerSpType == 'Polynomial':
                    Solution_GPU = cp.zeros(NEQ, dtype=np.float64)
                
                if KerSpType == 'B-Spline':
                    Solution_GPU = cp.zeros(NEQ, dtype=np.float64)
                    Solution_GPU[ij00[1:]] = Solution_tweaked_GPU[ij00[0]]

                _module = SFFTModule_dict['Restore_Solution']
                _func = _module.get_function('kmain')
                _func(args=(Solution_tweaked_GPU, PresIDX_GPU, Solution_GPU), \
                    block=TpB_restore, grid=BpG_restore)

            if SCALING_MODE == 'SEPARATE-VARYING' and NEQt < NEQ:
                Solution_tweaked_GPU = LSSolver(A_GPU=LHMAT_tweaked_GPU, b_GPU=RHb_tweaked_GPU)
                
                BpG_restore, TpB_restore = GPUManage(NEQt)
                BpG_restore, TpB_restore = (BpG_restore, 1), (TpB_restore, 1, 1)

                Solution_GPU = cp.zeros(NEQ, dtype=np.float64)
                _module = SFFTModule_dict['Restore_Solution']
                _func = _module.get_function('kmain')
                _func(args=(Solution_tweaked_GPU, PresIDX_GPU, Solution_GPU), \
                    block=TpB_restore, grid=BpG_restore)

            a_ijab_GPU = Solution_GPU[: Fijab]
            b_pq_GPU = Solution_GPU[Fijab: ]
            Solution = cp.asnumpy(Solution_GPU)

            dt8 = time.time() - t8
            dtb = time.time() - tb

            if VERBOSE_LEVEL in [1, 2]:
                print('\nMeLOn CheckPoint: SFFT-SUBTRACTION Establish & Solve Linear System takes [%.4fs]' %dtb)

            if VERBOSE_LEVEL in [2]:
                print('/////   d   ///// Establish OMG                       (%.4fs)' %dt3)
                print('/////   e   ///// Establish GAM                       (%.4fs)' %dt4)
                print('/////   f   ///// Establish PSI                       (%.4fs)' %dt5)
                print('/////   g   ///// Establish PHI                       (%.4fs)' %dt6)
                print('/////   h   ///// Establish THE & DEL                 (%.4fs)' %dt7)
                print('/////   i   ///// Solve Linear System                 (%.4fs)' %dt8)

        # <*****> Perform Subtraction  <*****> #
        PixA_DIFF = None
        if Subtract:
            tc = time.time()
            t9 = time.time()

            # Calculate Kab components
            Wl_GPU = cp.exp((-2j*np.pi/N0) * PixA_X_GPU.astype(np.float64))    # row index l, [0, N0)
            Wm_GPU = cp.exp((-2j*np.pi/N1) * PixA_Y_GPU.astype(np.float64))    # column index m, [0, N1)
            Kab_Wla_GPU = cp.empty((L0, N0, N1), dtype=np.complex128)
            Kab_Wmb_GPU = cp.empty((L1, N0, N1), dtype=np.complex128)

            if w0 == w1:
                wx = w0   # a little bit faster
                for aob in range(-wx, wx+1):
                    Kab_Wla_GPU[aob + wx] = Wl_GPU ** aob    # offset 
                    Kab_Wmb_GPU[aob + wx] = Wm_GPU ** aob    # offset 
            else:
                for a in range(-w0, w0+1): 
                    Kab_Wla_GPU[a + w0] = Wl_GPU ** a        # offset 
                for b in range(-w1, w1+1): 
                    Kab_Wmb_GPU[b + w1] = Wm_GPU ** b        # offset 
            
            dt9 = time.time() - t9
            t10 = time.time()

            # Construct Difference in Fourier Space
            if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:
                _module = SFFTModule_dict['Construct_FDIFF']
                _func = _module.get_function('kmain')     
                PixA_FDIFF_GPU = cp.empty((N0, N1), dtype=np.complex128)
                _func(args=(SREF_ijab_GPU, REF_ab_GPU, a_ijab_GPU.astype(np.complex128), \
                    SPixA_FIij_GPU, Kab_Wla_GPU, Kab_Wmb_GPU, b_pq_GPU.astype(np.complex128), \
                    SPixA_FTpq_GPU, PixA_FJ_GPU, PixA_FDIFF_GPU), block=TpB_PIX, grid=BpG_PIX)
                
            if SCALING_MODE == 'SEPARATE-VARYING':
                _module = SFFTModule_dict['Construct_FDIFF']
                _func = _module.get_function('kmain')     
                PixA_FDIFF_GPU = cp.empty((N0, N1), dtype=np.complex128)
                _func(args=(SREF_ijab_GPU, REF_ab_GPU, a_ijab_GPU.astype(np.complex128), \
                    SPixA_FIij_GPU, ScaSPixA_FIij_GPU, Kab_Wla_GPU, Kab_Wmb_GPU, b_pq_GPU.astype(np.complex128), \
                    SPixA_FTpq_GPU, PixA_FJ_GPU, PixA_FDIFF_GPU), block=TpB_PIX, grid=BpG_PIX)
            
            # Get Difference & Reconstructed Images
            PixA_DIFF_GPU = SCALE_L * cp.fft.ifft2(PixA_FDIFF_GPU)
            PixA_DIFF = cp.asnumpy(PixA_DIFF_GPU.real)
            
            dt10 = time.time() - t10
            dtc = time.time() - tc

            if VERBOSE_LEVEL in [1, 2]:
                print('\nMeLOn CheckPoint: SFFT-SUBTRACTION Perform Subtraction takes [%.4fs]' %dtc)
            
            if VERBOSE_LEVEL in [2]:
                print('/////   j   ///// Calculate Kab         (%.4fs)' %dt9)
                print('/////   k   ///// Construct DIFF        (%.4fs)' %dt10)
        
        if VERBOSE_LEVEL in [1, 2]:
            print('\n --||--||--||--||-- EXIT SFFT SUBTRACTION [Cupy] --||--||--||--||-- ')

        return Solution, PixA_DIFF

class ElementalSFFTSubtract:
    @staticmethod
    def ESS(PixA_I, PixA_J, SFFTConfig, SFFTSolution=None, Subtract=False, \
        BACKEND_4SUBTRACT='Cupy', NUM_CPU_THREADS_4SUBTRACT=8, VERBOSE_LEVEL=2):

        if BACKEND_4SUBTRACT == 'Cupy':
            Solution, PixA_DIFF = ElementalSFFTSubtract_Cupy.ESSC(PixA_I=PixA_I, PixA_J=PixA_J, \
                SFFTConfig=SFFTConfig, SFFTSolution=SFFTSolution, Subtract=Subtract, \
                VERBOSE_LEVEL=VERBOSE_LEVEL)

        if BACKEND_4SUBTRACT == 'Numpy':
            print('MeLOn ERROR: Numpy backend is not supported for B-Spline SFFT in current version! Will implement in future!')
        
        return Solution, PixA_DIFF

class GeneralSFFTSubtract:
    @staticmethod
    def GSS(PixA_I, PixA_J, PixA_mI, PixA_mJ, SFFTConfig, ContamMask_I=None, \
        BACKEND_4SUBTRACT='Cupy', NUM_CPU_THREADS_4SUBTRACT=8, VERBOSE_LEVEL=2):

        """
        # Perform image subtraction on I & J with SFFT parameters solved from mI & mJ
        #
        # Arguments:
        # -PixA_I: Image I that will be convolved [NaN-Free]                                    
        # -PixA_J: Image J that won't be convolved [NaN-Free]                                   
        # -PixA_mI: Masked version of Image I. 'same' means it is identical with I [NaN-Free]  
        # -PixA_mJ: Masked version of Image J. 'same' means it is identical with J [NaN-Free]
        # -SFFTConfig: Configurations of SFFT
        #
        # -ContamMask_I: Contamination Mask of Image I (e.g., Saturation and Bad pixels)
        # -BACKEND_4SUBTRACT: The backend with which you perform SFFT subtraction              | ['Cupy', 'Numpy']
        # -NUM_CPU_THREADS_4SUBTRACT: The number of CPU threads for Numpy-SFFT subtraction     | e.g., 8
        # -VERBOSE_LEVEL: The level of verbosity, can be 0/1/2: QUIET/NORMAL/FULL              | [0, 1, 2]
        #
        """
        
        SFFT_BANNER = r"""
                                __    __    __    __
                               /  \  /  \  /  \  /  \
                              /    \/    \/    \/    \
            █████████████████/  /██/  /██/  /██/  /█████████████████████████
                            /  / \   / \   / \   / \  \____
                           /  /   \_/   \_/   \_/   \    o \__,
                          / _/                       \_____/  `
                          |/
        
                      █████████  ███████████ ███████████ ███████████        
                     ███░░░░░███░░███░░░░░░█░░███░░░░░░█░█░░░███░░░█            
                    ░███    ░░░  ░███   █ ░  ░███   █ ░ ░   ░███  ░ 
                    ░░█████████  ░███████    ░███████       ░███    
                     ░░░░░░░░███ ░███░░░█    ░███░░░█       ░███    
                     ███    ░███ ░███  ░     ░███  ░        ░███    
                    ░░█████████  █████       █████          █████   
                     ░░░░░░░░░  ░░░░░       ░░░░░          ░░░░░         
        
                    Saccadic Fast Fourier Transform (SFFT) algorithm
                    sfft (v1.*) supported by @LeiHu
        
                    GitHub: https://github.com/thomasvrussell/sfft
                    Related Paper: https://arxiv.org/abs/2109.09334
                    
            ████████████████████████████████████████████████████████████████
            
            """
        
        if VERBOSE_LEVEL in [2]:
            print(SFFT_BANNER)
        
        # * Check Size of input images
        tmplst = [PixA_I.shape, PixA_J.shape, PixA_mI.shape, PixA_mI.shape]
        if len(set(tmplst)) > 1:
            raise Exception('MeLOn ERROR: Input images should have same size!')
        
        # * Subtraction Solution derived from input masked image-pair
        Solution = ElementalSFFTSubtract.ESS(PixA_I=PixA_mI, PixA_J=PixA_mJ, SFFTConfig=SFFTConfig, \
            SFFTSolution=None, Subtract=False, BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, \
            NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, VERBOSE_LEVEL=VERBOSE_LEVEL)[0]
            
        # * Subtraction of the input image-pair (use above solution)
        PixA_DIFF = ElementalSFFTSubtract.ESS(PixA_I=PixA_I, PixA_J=PixA_J, SFFTConfig=SFFTConfig, \
            SFFTSolution=Solution, Subtract=True, BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, \
            NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, VERBOSE_LEVEL=VERBOSE_LEVEL)[1]
        
        # * Identify propagated contamination region through convolving I
        ContamMask_CI = None
        if ContamMask_I is not None:
            tSolution = Solution.copy()
            Fpq = SFFTConfig[0]['Fpq']
            tSolution[-Fpq:] = 0.0

            _tmpI = ContamMask_I.astype(np.float64)
            _tmpJ = np.zeros(PixA_J.shape).astype(np.float64)
            _tmpD = ElementalSFFTSubtract.ESS(PixA_I=_tmpI, PixA_J=_tmpJ, SFFTConfig=SFFTConfig, \
                SFFTSolution=tSolution, Subtract=True, BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, \
                NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, VERBOSE_LEVEL=VERBOSE_LEVEL)[1]
            
            FTHRESH = -0.001  # emperical value
            ContamMask_CI = _tmpD < FTHRESH
        
        return Solution, PixA_DIFF, ContamMask_CI

class BSpline_Packet:
    @staticmethod
    def BSP(FITS_REF, FITS_SCI, FITS_mREF, FITS_mSCI, FITS_DIFF=None, FITS_Solution=None, \
        ForceConv='REF', GKerHW=8, KerSpType='Polynomial', KerSpDegree=2, KerIntKnotX=[], KerIntKnotY=[], \
        SEPARATE_SCALING=True, ScaSpType='Polynomial', ScaSpDegree=0, ScaIntKnotX=[], ScaIntKnotY=[], \
        BkgSpType='Polynomial', BkgSpDegree=2, BkgIntKnotX=[], BkgIntKnotY=[], \
        REGULARIZE_KERNEL=False, IGNORE_LAPLACIAN_KERCENT=True, XY_REGULARIZE=None, 
        WEIGHT_REGULARIZE=None, LAMBDA_REGULARIZE=1e-6, BACKEND_4SUBTRACT='Cupy', \
        CUDA_DEVICE_4SUBTRACT='0', MAX_THREADS_PER_BLOCK=8, MINIMIZE_GPU_MEMORY_USAGE=False, \
        NUM_CPU_THREADS_4SUBTRACT=8, VERBOSE_LEVEL=2):
        
        """
        * Parameters of Customized SFFT
        # @ Customized: use a customized masked image-pair and skip the built-in preprocessing image masking.
        #
        # ----------------------------- Computing Enviornment --------------------------------- #
        
        -BACKEND_4SUBTRACT ['Cupy']         # 'Cupy' or 'Numpy'.
                                            # Cupy backend require GPU(s) capable of performing double-precision calculations,
                                            # while Numpy backend is a pure CPU-based backend for sfft subtraction.
                                            # The Cupy backend is generally much faster than Numpy backend.
                                            # NOTE: 'Pycuda' backend is no longer supported since sfft v1.4.0.

        -CUDA_DEVICE_4SUBTRACT ['0']        # it specifies certain GPU device (index) to conduct the subtraction task.
                                            # the GPU devices are usually numbered 0 to N-1 (you may use command nvidia-smi to check).
                                            # NOTE: the argument only works for Cupy backend.

        -MAX_THREADS_PER_BLOCK [8]          # Maximum Threads per Block for CUDA configuration.
                                            # Emperically, the default 8 is generally a good choice.
                                            # NOTE: if one gets error "Entry function 'kmain' uses too much shared data",
                                            #       which means the device cannot provide enough GPU shared memory, 
                                            #       one can try a lower MAX_THREADS_PER_BLOCK, e.g., 4 or 2, to fix.
                                            # NOTE: the argument only works for Cupy backend.

        -MINIMIZE_GPU_MEMORY_USAGE [False]  # Minimize the GPU Memory Usage? can be True or False
                                            # NOTE: doing so (True) can efficiently reduce the total GPU memory usage, 
                                            #       while it would also largely affect the speed of sfft. Please activate this 
                                            #       memory-friendly mode only when memory is insufficient!
                                            # NOTE: the argument only works for Cupy backend.

        -NUM_CPU_THREADS_4SUBTRACT [8]      # it specifies the number of CPU threads used for sfft subtraction within Numpy backend.
                                            # Numpy backend sfft is implemented with pyFFTW and numba, that allow for 
                                            # parallel computing on CPUs.
                                            # NOTE: the argument only works for Numpy backend.
        
        # ----------------------------- SFFT Subtraction --------------------------------- #

        -ForceConv ['REF']                  # it determines which image will be convolved, can be 'REF' or 'SCI'.
                                            # here ForceConv CANNOT be 'AUTO'!

        -GKerHW [8]                         # the given kernel half-width (pix). 

        # spatial variation of matching kernel

        -KerSpType ['Polynomial']           # 'Polynomial' or 'B-Spline'
                                            # Spatial Varaition Type of Matching Kernel

        -KerSpDegree [2]                    # Polynomial / B-Spline Degree of Kernel Spatial Varaition

        -KerIntKnotX [[]]                   # Internal Knots of Kernel B-Spline Spatial Varaition along X

        -KerIntKnotY [[]]                   # Internal Knots of Kernel B-Spline Spatial Varaition along Y

        -ScaSpType ['Polynomial']           # 'Polynomial' or 'B-Spline'
                                            # Spatial Varaition Type of Matching Kernel

        # spatial variation of convolution scaling

        -SEPARATE_SCALING [True]            # True or False
                                            # True: Convolution Scaling (kernel sum) is a separate varaible
                                            # False: Convolution Scaling is entangled with matching kernel

        -ScaSpType ['Polynomial']           # 'Polynomial' or 'B-Spline'
                                            # Spatial Varaition Type of Convolution Scaling

        -ScaSpDegree [0]                    # Polynomial / B-Spline Degree of Scaling Spatial Varaition

        -ScaIntKnotX [[]]                   # Internal Knots of Scaling B-Spline Spatial Varaition along X

        -ScaIntKnotY [[]]                   # Internal Knots of Scaling B-Spline Spatial Varaition along Y

        P.S. the default configuration means a constant convolution scaling!

        # spatial variation of differential background

        -BkgSpType ['Polynomial']           # 'Polynomial' or 'B-Spline'
                                            # Spatial Varaition Type of Differential Background

        -BkgSpDegree [2]                    # Polynomial / B-Spline Degree of Background Spatial Varaition

        -BkgIntKnotX [[]]                   # Internal Knots of Background B-Spline Spatial Varaition along X

        -BkgIntKnotY [[]]                   # Internal Knots of Background B-Spline Spatial Varaition along Y


        # kernel regularization

        -REGULARIZE_KERNEL [False]          # Regularize matching kernel by applying penalty on
                                            # kernel's second derivates using Laplacian matrix

        -IGNORE_LAPLACIAN_KERCENT [True]    # zero out the rows of Laplacian matrix
                                            # corresponding the kernel center pixels by zeros. 
                                            # If True, the regularization will not impose any penalty 
                                            # on a delta-function-like matching kernel

        -XY_REGULARIZE [None]               # The coordinates at which the matching kernel regularized.
                                            # Numpy array of (x, y) with shape (N_points, 2), 
                                            # where x in (0.5, NX+0.5) and y in (0.5, NY+0.5)

        -WEIGHT_REGULARIZE [None]           # The weights of the coordinates sampled for regularization.
                                            # Use 1d numpy array with shape (XY_REGULARIZE.shape[0])
                                            # Note: -WEIGHT_REGULARIZE = None means uniform weights of 1.0

        -LAMBDA_REGULARIZE [1e-6]           # Tunning paramater lambda for regularization
                                            # it controls the strength of penalty on kernel overfitting

        # ----------------------------- Input & Output --------------------------------- #

        -FITS_REF []                        # File path of input reference image.

        -FITS_SCI []                        # File path of input science image.

        -FITS_mREF []                       # File path of input masked reference image (NaN-free).

        -FITS_mSCI []                       # File path of input masked science image (NaN-free).

        -FITS_DIFF [None]                   # File path of output difference image.

        -FITS_Solution [None]               # File path of the solution of the linear system.
                                            # it is an array of (..., a_ijab, ... b_pq, ...).

        # ----------------------------- Miscellaneous --------------------------------- #
        
        -VERBOSE_LEVEL [2]                  # The level of verbosity, can be [0, 1, 2]
                                            # 0/1/2: QUIET/NORMAL/FULL mode

        # Important Notice:
        #
        # a): if reference is convolved in SFFT (-ForceConv='REF'), then DIFF = SCI - Convolved_REF
        #     [the difference image is expected to have PSF & flux zero-point consistent with science image]
        #
        # b): if science is convolved in SFFT (-ForceConv='SCI'), then DIFF = Convolved_SCI - REF
        #     [the difference image is expected to have PSF & flux zero-point consistent with reference image]
        #
        # Remarks: this convention is to guarantee that transients emerge on science image 
        #          always show a positive signal on difference images.
        #
        """

        # * Read input images
        PixA_REF = fits.getdata(FITS_REF, ext=0).T
        PixA_SCI = fits.getdata(FITS_SCI, ext=0).T
        PixA_mREF = fits.getdata(FITS_mREF, ext=0).T
        PixA_mSCI = fits.getdata(FITS_mSCI, ext=0).T

        if not PixA_REF.flags['C_CONTIGUOUS']:
            PixA_REF = np.ascontiguousarray(PixA_REF, np.float64)
        else: PixA_REF = PixA_REF.astype(np.float64)

        if not PixA_SCI.flags['C_CONTIGUOUS']:
            PixA_SCI = np.ascontiguousarray(PixA_SCI, np.float64)
        else: PixA_SCI = PixA_SCI.astype(np.float64)

        if not PixA_mREF.flags['C_CONTIGUOUS']:
            PixA_mREF = np.ascontiguousarray(PixA_mREF, np.float64)
        else: PixA_mREF = PixA_mREF.astype(np.float64)

        if not PixA_mSCI.flags['C_CONTIGUOUS']:
            PixA_mSCI = np.ascontiguousarray(PixA_mSCI, np.float64)
        else: PixA_mSCI = PixA_mSCI.astype(np.float64)

        NaNmask_U = None
        NaNmask_REF = np.isnan(PixA_REF)
        NaNmask_SCI = np.isnan(PixA_SCI)
        if NaNmask_REF.any() or NaNmask_SCI.any():
            NaNmask_U = np.logical_or(NaNmask_REF, NaNmask_SCI)

        assert np.sum(np.isnan(PixA_mREF)) == 0
        assert np.sum(np.isnan(PixA_mSCI)) == 0
        
        assert ForceConv in ['REF', 'SCI']
        ConvdSide = ForceConv
        KerHW = GKerHW

        # * Choose GPU device for Cupy backend
        if BACKEND_4SUBTRACT == 'Cupy':
            import cupy as cp
            device = cp.cuda.Device(int(CUDA_DEVICE_4SUBTRACT))
            device.use()
        
        # * Compile Functions in SFFT Subtraction
        if VERBOSE_LEVEL in [0, 1, 2]:
            print('MeLOn CheckPoint: TRIGGER Function Compilations of SFFT-SUBTRACTION!')

        Tcomp_start = time.time()
        SFFTConfig = SingleSFFTConfigure.SSC(NX=PixA_REF.shape[0], NY=PixA_REF.shape[1], KerHW=KerHW, \
            KerSpType=KerSpType, KerSpDegree=KerSpDegree, KerIntKnotX=KerIntKnotX, KerIntKnotY=KerIntKnotY, \
            SEPARATE_SCALING=SEPARATE_SCALING, ScaSpType=ScaSpType, ScaSpDegree=ScaSpDegree, \
            ScaIntKnotX=ScaIntKnotX, ScaIntKnotY=ScaIntKnotY, BkgSpType=BkgSpType, \
            BkgSpDegree=BkgSpDegree, BkgIntKnotX=BkgIntKnotX, BkgIntKnotY=BkgIntKnotY, \
            REGULARIZE_KERNEL=REGULARIZE_KERNEL, IGNORE_LAPLACIAN_KERCENT=IGNORE_LAPLACIAN_KERCENT, \
            XY_REGULARIZE=XY_REGULARIZE, WEIGHT_REGULARIZE=WEIGHT_REGULARIZE, \
            LAMBDA_REGULARIZE=LAMBDA_REGULARIZE, BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, \
            MAX_THREADS_PER_BLOCK=MAX_THREADS_PER_BLOCK, MINIMIZE_GPU_MEMORY_USAGE=MINIMIZE_GPU_MEMORY_USAGE, \
            NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, VERBOSE_LEVEL=VERBOSE_LEVEL)

        if VERBOSE_LEVEL in [1, 2]:
            _message = 'FUNCTION COMPILATIONS OF SFFT-SUBTRACTION TAKES [%.3f s]' %(time.time() - Tcomp_start)
            print('\nMeLOn Report: %s \n' %_message)

        # * Perform SFFT Subtraction
        if ConvdSide == 'REF':
            PixA_mI, PixA_mJ = PixA_mREF, PixA_mSCI
            if NaNmask_U is not None:
                PixA_I, PixA_J = PixA_REF.copy(), PixA_SCI.copy()
                PixA_I[NaNmask_U] = PixA_mI[NaNmask_U]
                PixA_J[NaNmask_U] = PixA_mJ[NaNmask_U]
            else: PixA_I, PixA_J = PixA_REF, PixA_SCI

        if ConvdSide == 'SCI':
            PixA_mI, PixA_mJ = PixA_mSCI, PixA_mREF
            if NaNmask_U is not None:
                PixA_I, PixA_J = PixA_SCI.copy(), PixA_REF.copy()
                PixA_I[NaNmask_U] = PixA_mI[NaNmask_U]
                PixA_J[NaNmask_U] = PixA_mJ[NaNmask_U]
            else: PixA_I, PixA_J = PixA_SCI, PixA_REF
        
        if VERBOSE_LEVEL in [0, 1, 2]:
            print('MeLOn CheckPoint: TRIGGER SFFT-SUBTRACTION!')

        Tsub_start = time.time()
        _tmp = GeneralSFFTSubtract.GSS(PixA_I=PixA_I, PixA_J=PixA_J, PixA_mI=PixA_mI, PixA_mJ=PixA_mJ, \
            SFFTConfig=SFFTConfig, ContamMask_I=None, BACKEND_4SUBTRACT=BACKEND_4SUBTRACT, \
            NUM_CPU_THREADS_4SUBTRACT=NUM_CPU_THREADS_4SUBTRACT, VERBOSE_LEVEL=VERBOSE_LEVEL)

        Solution, PixA_DIFF = _tmp[:2]
        if VERBOSE_LEVEL in [1, 2]:
            _message = 'SFFT-SUBTRACTION TAKES [%.3f s]' %(time.time() - Tsub_start)
            print('\nMeLOn Report: %s \n' %_message)
        
        # * Modifications on the difference image
        #   a) when REF is convolved, DIFF = SCI - Conv(REF)
        #      PSF(DIFF) is coincident with PSF(SCI), transients on SCI are positive signal in DIFF
        #   b) when SCI is convolved, DIFF = Conv(SCI) - REF
        #      PSF(DIFF) is coincident with PSF(REF), transients on SCI are still positive signal in DIFF

        if NaNmask_U is not None:
            # ** Mask Union-NaN region
            PixA_DIFF[NaNmask_U] = np.nan
        
        if ConvdSide == 'SCI': 
            # ** Flip difference when science is convolved
            PixA_DIFF = -PixA_DIFF
        
        # * Save difference image
        if FITS_DIFF is not None:
            with fits.open(FITS_SCI) as hdl:
                hdl[0].data[:, :] = PixA_DIFF.T
                hdl[0].header['NAME_REF'] = (pa.basename(FITS_REF), 'SFFT')
                hdl[0].header['NAME_SCI'] = (pa.basename(FITS_SCI), 'SFFT')
                hdl[0].header['BEND4SUB'] = (BACKEND_4SUBTRACT, 'SFFT')
                hdl[0].header['CONVD'] = (ConvdSide, 'SFFT')
                hdl[0].header['KERHW'] = (KerHW, 'SFFT')

                hdl[0].header['KSPTYPE'] = (str(KerSpType), 'SFFT')
                hdl[0].header['KSPDEG'] = (KerSpDegree, 'SFFT')
                hdl[0].header['NKIKX'] = (len(KerIntKnotX), 'SFFT')
                for i, knot in enumerate(KerIntKnotX):
                    hdl[0].header['KIKX%d' %i] = (knot, 'SFFT')
                hdl[0].header['NKIKY'] = (len(KerIntKnotY), 'SFFT')
                for i, knot in enumerate(KerIntKnotY):
                    hdl[0].header['KIKY%d' %i] = (knot, 'SFFT')

                hdl[0].header['SEPSCA'] = (str(SEPARATE_SCALING), 'SFFT')
                if SEPARATE_SCALING:
                    hdl[0].header['SSPTYPE'] = (str(ScaSpType), 'SFFT')
                    hdl[0].header['SSPDEG'] = (ScaSpDegree, 'SFFT')
                    hdl[0].header['NSIKX'] = (len(ScaIntKnotX), 'SFFT')
                    for i, knot in enumerate(ScaIntKnotX):
                        hdl[0].header['SIKX%d' %i] = (knot, 'SFFT')
                    hdl[0].header['NSIKY'] = (len(ScaIntKnotY), 'SFFT')
                    for i, knot in enumerate(ScaIntKnotY):
                        hdl[0].header['SIKY%d' %i] = (knot, 'SFFT')

                hdl[0].header['BSPTYPE'] = (str(BkgSpType), 'SFFT')
                hdl[0].header['BSPDEG'] = (BkgSpDegree, 'SFFT')
                hdl[0].header['NBIKX'] = (len(BkgIntKnotX), 'SFFT')
                for i, knot in enumerate(BkgIntKnotX):
                    hdl[0].header['BIKX%d' %i] = (knot, 'SFFT')
                hdl[0].header['NBIKY'] = (len(BkgIntKnotY), 'SFFT')
                for i, knot in enumerate(BkgIntKnotY):
                    hdl[0].header['BIKY%d' %i] = (knot, 'SFFT')
                
                hdl[0].header['BSPTYPE'] = (str(BkgSpType), 'SFFT')
                hdl[0].header['BSPDEG'] = (BkgSpDegree, 'SFFT')
                hdl[0].header['NBIKX'] = (len(BkgIntKnotX), 'SFFT')
                for i, knot in enumerate(BkgIntKnotX):
                    hdl[0].header['BIKX%d' %i] = (knot, 'SFFT')
                hdl[0].header['NBIKY'] = (len(BkgIntKnotY), 'SFFT')
                for i, knot in enumerate(BkgIntKnotY):
                    hdl[0].header['BIKY%d' %i] = (knot, 'SFFT')
                
                hdl[0].header['REGKER'] = (str(REGULARIZE_KERNEL), 'SFFT')
                hdl[0].header['ILKC'] = (str(IGNORE_LAPLACIAN_KERCENT), 'SFFT')
                if XY_REGULARIZE is None: hdl[0].header['NREG'] = (-1, 'SFFT')
                else: hdl[0].header['NREG'] = (XY_REGULARIZE.shape[0], 'SFFT')
                if WEIGHT_REGULARIZE is None: hdl[0].header['REGW'] = ('UNIFORM', 'SFFT')
                else: hdl[0].header['REGW'] = ('SPECIFIED', 'SFFT')
                hdl[0].header['REGLAMB'] = (LAMBDA_REGULARIZE, 'SFFT')
                hdl.writeto(FITS_DIFF, overwrite=True)
        
        # * Save solution array
        if FITS_Solution is not None:
            
            phdu = fits.PrimaryHDU()
            phdu.header['NAME_REF'] = (pa.basename(FITS_REF), 'SFFT')
            phdu.header['NAME_SCI'] = (pa.basename(FITS_SCI), 'SFFT')
            phdu.header['BEND4SUB'] = (BACKEND_4SUBTRACT, 'SFFT')
            phdu.header['CONVD'] = (ConvdSide, 'SFFT')
            phdu.header['KERHW'] = (KerHW, 'SFFT')
        
            phdu.header['KSPTYPE'] = (str(KerSpType), 'SFFT')
            phdu.header['KSPDEG'] = (KerSpDegree, 'SFFT')
            phdu.header['NKIKX'] = (len(KerIntKnotX), 'SFFT')
            for i, knot in enumerate(KerIntKnotX):
                phdu.header['KIKX%d' %i] = (knot, 'SFFT')
            phdu.header['NKIKY'] = (len(KerIntKnotY), 'SFFT')
            for i, knot in enumerate(KerIntKnotY):
                phdu.header['KIKY%d' %i] = (knot, 'SFFT')

            phdu.header['SEPSCA'] = (str(SEPARATE_SCALING), 'SFFT')
            if SEPARATE_SCALING:
                phdu.header['SSPTYPE'] = (str(ScaSpType), 'SFFT')
                phdu.header['SSPDEG'] = (ScaSpDegree, 'SFFT')
                phdu.header['NSIKX'] = (len(ScaIntKnotX), 'SFFT')
                for i, knot in enumerate(ScaIntKnotX):
                    phdu.header['SIKX%d' %i] = (knot, 'SFFT')
                phdu.header['NSIKY'] = (len(ScaIntKnotY), 'SFFT')
                for i, knot in enumerate(ScaIntKnotY):
                    phdu.header['SIKY%d' %i] = (knot, 'SFFT')

            phdu.header['BSPTYPE'] = (str(BkgSpType), 'SFFT')
            phdu.header['BSPDEG'] = (BkgSpDegree, 'SFFT')
            phdu.header['NBIKX'] = (len(BkgIntKnotX), 'SFFT')
            for i, knot in enumerate(BkgIntKnotX):
                phdu.header['BIKX%d' %i] = (knot, 'SFFT')
            phdu.header['NBIKY'] = (len(BkgIntKnotY), 'SFFT')
            for i, knot in enumerate(BkgIntKnotY):
                phdu.header['BIKY%d' %i] = (knot, 'SFFT')
            
            phdu.header['REGKER'] = (str(REGULARIZE_KERNEL), 'SFFT')
            phdu.header['ILKC'] = (str(IGNORE_LAPLACIAN_KERCENT), 'SFFT')
            if XY_REGULARIZE is None: phdu.header['NREG'] = (-1, 'SFFT')
            else: phdu.header['NREG'] = (XY_REGULARIZE.shape[0], 'SFFT')
            if WEIGHT_REGULARIZE is None: phdu.header['REGW'] = ('UNIFORM', 'SFFT')
            else: phdu.header['REGW'] = ('SPECIFIED', 'SFFT')
            phdu.header['REGLAMB'] = (LAMBDA_REGULARIZE, 'SFFT')
            
            phdu.header['N0'] = (SFFTConfig[0]['N0'], 'SFFT')
            phdu.header['N1'] = (SFFTConfig[0]['N1'], 'SFFT')
            phdu.header['W0'] = (SFFTConfig[0]['w0'], 'SFFT')
            phdu.header['W1'] = (SFFTConfig[0]['w1'], 'SFFT')
            phdu.header['DK'] = (SFFTConfig[0]['DK'], 'SFFT')
            phdu.header['DB'] = (SFFTConfig[0]['DB'], 'SFFT')
            if SEPARATE_SCALING: 
                phdu.header['DS'] = (SFFTConfig[0]['DS'], 'SFFT')
            
            phdu.header['L0'] = (SFFTConfig[0]['L0'], 'SFFT')
            phdu.header['L1'] = (SFFTConfig[0]['L1'], 'SFFT')
            phdu.header['FAB'] = (SFFTConfig[0]['Fab'], 'SFFT')
            phdu.header['FI'] = (SFFTConfig[0]['Fi'], 'SFFT')
            phdu.header['FJ'] = (SFFTConfig[0]['Fj'], 'SFFT')
            phdu.header['FIJ'] = (SFFTConfig[0]['Fij'], 'SFFT')
            phdu.header['FP'] = (SFFTConfig[0]['Fp'], 'SFFT')
            phdu.header['FQ'] = (SFFTConfig[0]['Fq'], 'SFFT')
            phdu.header['FPQ'] = (SFFTConfig[0]['Fpq'], 'SFFT')
        
            if SEPARATE_SCALING and ScaSpDegree > 0:
                phdu.header['SCAFI'] = (SFFTConfig[0]['ScaFi'], 'SFFT')
                phdu.header['SCAFJ'] = (SFFTConfig[0]['ScaFj'], 'SFFT')
                phdu.header['SCAFIJ'] = (SFFTConfig[0]['ScaFij'], 'SFFT')
            phdu.header['FIJAB'] = (SFFTConfig[0]['Fijab'], 'SFFT')
            
            phdu.header['NEQ'] = (SFFTConfig[0]['NEQ'], 'SFFT')
            phdu.header['NEQT'] = (SFFTConfig[0]['NEQt'], 'SFFT')
            PixA_Solution = Solution.reshape((-1, 1))
            phdu.data = PixA_Solution.T
            fits.HDUList([phdu]).writeto(FITS_Solution, overwrite=True)
        
        return Solution, PixA_DIFF

class Read_SFFTSolution:

    def __init__(self):

        """
        # Notes on the representation of a spatially-varying kernel (SVK)
        # 
        # (1) SFFT Format: 
        #     SVK_xy = sum_ab (Ac_xyab * K_ab)
        #            = sum_ab (Ac_xyab * K_ab) | KERNEL: (a, b) != (0, 0)
        #              + Ac_xy00 * K_00        | SCALING: (a, b) == (0, 0)
        #
        #     > SFFT can have separate KERNEL / SCALING in Polynomial / B-Spline form.
        #       Polynomial: Ac_xyab = sum_ij (ac_ijab * x^i * y^j)
        #       B-Spline:   Ac_xyab = sum_ij (ac_ijab * BSP_i(x) * BSP_j(y))
        #
        #     > Use the following two dictionaries to store the parameters
        #       KERNEL: SfftKerDict[(i, j)][a, b] = ac_ijab, where (a, b) != (0, 0)
        #       SCALING: SfftScaDict[(i, j)] = ac_ij00
        #
        #     NOTE: K_ab is modified delta basis (see the SFFT paper).
        #           Ac (ac) is the symbol A (a) with circle hat in SFFT paper, note that ac = a/(N0*N1).
        #           BSP_i(x) is the i-th B-Spline base function along X
        #           BSP_j(x) is the j-th B-Spline base function along Y
        #
        #     NOTE: For "ENTANGLED" SCALING or "SEPARATE-CONSTANT" SCALING
        #           one can solely use SfftKerDict to represent SVK by allowing (a, b) == (0, 0)
        #           no additional variation form need to be involved.
        #    
        #     NOTE: Although (x, y) are the integer indices of a pixel in SFFT paper,
        #           we actually use a scaled image coordinate (i.e., ScaledFortranCoor) of
        #           pixel center in our implementation. Note that above equations allow for 
        #           all possible image coordinates (not just pixel center).
        #
        # (2) Standard Format:
        #     SVK_xy = sum_ab (B_xyab * D_ab)
        #
        #     > Standard have entangled KERNEL & SCALING
        #       Polynomial: B_xyab = sum_ij (b_ijab * x^i * y^j)
        #       B-Spline:   B_xyab = sum_ij (b_ijab * BSP_i(x) * BSP_j(y))
        #     
        #     > Use the dictionary to store the parameters
        #       StandardKerDict[(i, j)][a, b] = b_ijab
        #
        #     NOTE: D_ab is standard Cartesian delta basis. Likewise, 
        #           (x, y) is ScaledFortranCoor that allows for all possible image coordinates.
        #
        # P.S. Coordinate Example: Given Pixel Location at (row=3, column=5) in an image of size (1024, 2048)
        #      FortranCoor = (4.0, 6.0) | ScaledFortranCoor = (4.0/1024, 6.0/2048)
        #
        # P.S. In principle, a and b are in the range of [-w0, w0 + 1) and [-w1 , w1+ 1), respectively.
        #      However, Sfft_dict[(i, j)] or Standard_dict[(i, j)] has to be a matrix with 
        #      non-negative indices starting from 0. In practice, the indices were tweaked 
        #      as [a, b] > [a + w0, b + w1].
        #
        """

        pass
    
    def FromArray(self, Solution, KerSpType, N0, N1, DK, L0, L1, Fi, Fj, Fpq, \
        SEPARATE_SCALING, ScaSpType, DS, ScaFi, ScaFj):

        # Remarks on SCALING_MODE
        # SEPARATE_SCALING & ScaSpDegree >>>      SCALING_MODE
        #        N         &     any     >>>       'ENTANGLED'
        #        Y         &      0      >>>   'SEPARATE-CONSTANT'
        #        Y         &     > 0     >>>   'SEPARATE-VARYING'

        SCALING_MODE = None
        if not SEPARATE_SCALING:
            SCALING_MODE = 'ENTANGLED'
        elif DS == 0:
            SCALING_MODE = 'SEPARATE-CONSTANT'
        else: SCALING_MODE = 'SEPARATE-VARYING'
        assert SCALING_MODE is not None

        Fab = L0*L1
        w0, w1 = (L0-1)//2, (L1-1)//2

        REF_ab = np.array([
            (a_pos - w0, b_pos - w1) \
            for a_pos in range(L0) for b_pos in range(L1)
        ]).astype(int)

        if KerSpType == 'Polynomial':
            Fij = ((DK+1)*(DK+2))//2
            REF_ij = np.array([
                (i, j) \
                for i in range(DK+1) for j in range(DK+1-i)
            ]).astype(int)
        
        if KerSpType == 'B-Spline':
            Fij = Fi*Fj
            REF_ij = np.array([
                (i, j) \
                for i in range(Fi) for j in range(Fj)
            ]).astype(int)
        
        Fijab = Fij*Fab
        SREF_ijab = np.array([
            (ij, ab) \
            for ij in range(Fij) for ab in range(Fab)
        ]).astype(int)

        if SCALING_MODE == 'SEPARATE-VARYING':

            if ScaSpType == 'Polynomial':
                ScaFij = ((DS+1)*(DS+2))//2
                ScaREF_ij = np.array(
                    [(i, j) for i in range(DS+1) for j in range(DS+1-i)] \
                    + [(-1, -1)] * (Fij - ScaFij)
                ).astype(int)

            if ScaSpType == 'B-Spline':
                ScaFij = ScaFi*ScaFj
                ScaREF_ij = np.array(
                    [(i, j) for i in range(ScaFi) for j in range(ScaFj)] \
                    + [(-1, -1)] * (Fij - ScaFij)
                ).astype(int)

        a_ijab = Solution[:-Fpq]      # drop differential background
        ac_ijab = a_ijab / (N0*N1)    # convert a to ac

        SfftKerDict = {}
        if KerSpType == 'Polynomial':
            for i in range(DK+1):
                for j in range(DK+1-i):
                    SfftKerDict[(i, j)] = np.zeros((L0, L1)).astype(float)
        
        if KerSpType == 'B-Spline':
            for i in range(Fi):
                for j in range(Fj):
                    SfftKerDict[(i, j)] = np.zeros((L0, L1)).astype(float)
        
        SfftScaDict = None
        if SCALING_MODE == 'SEPARATE-VARYING':
            
            SfftScaDict = {}
            if KerSpType == 'Polynomial':
                for i in range(DS+1):
                    for j in range(DS+1-i):
                        SfftScaDict[(i, j)] = 0.0
            
            if KerSpType == 'B-Spline':
                for i in range(ScaFi):
                    for j in range(ScaFj):
                        SfftScaDict[(i, j)] = 0.0

        for idx in range(Fijab):
            ij, ab = SREF_ijab[idx]
            a, b = REF_ab[ab]
            i, j = REF_ij[ij]

            if SCALING_MODE in ['ENTANGLED', 'SEPARATE-CONSTANT']:
                SfftKerDict[(i, j)][a+w0, b+w1] = ac_ijab[idx]

            if SCALING_MODE == 'SEPARATE-VARYING':
                if a == 0 and b == 0:
                    SfftKerDict[(i, j)][a+w0, b+w1] = np.nan                    
                    i8, j8 = ScaREF_ij[ij]
                    if i8 != -1 and j8 != -1:
                        SfftScaDict[(i8, j8)] = ac_ijab[idx]
                else:
                    SfftKerDict[(i, j)][a+w0, b+w1] = ac_ijab[idx]
            
        return SfftKerDict, SfftScaDict

    def FromFITS(self, FITS_Solution):
        
        Solution = fits.getdata(FITS_Solution, ext=0)[0]
        phdr = fits.getheader(FITS_Solution, ext=0)
        
        KerSpType = phdr['KSPTYPE']
        N0, N1 = int(phdr['N0']), int(phdr['N1'])
        DK = int(phdr['DK'])
        
        L0, L1 = int(phdr['L0']), int(phdr['L1'])
        Fi, Fj = int(phdr['FI']), int(phdr['FJ'])
        Fpq = int(phdr['FPQ'])

        SEPARATE_SCALING = phdr['SEPSCA'] == 'True'
        ScaSpType, DS = None, None
        if SEPARATE_SCALING:
            ScaSpType = phdr['SSPTYPE']
            DS = int(phdr['SSPDEG'])

        ScaFi, ScaFj = None, None
        if SEPARATE_SCALING and DS > 0:
            ScaFi = int(phdr['SCAFI'])
            ScaFj = int(phdr['SCAFJ'])

        SfftKerDict, SfftScaDict = self.FromArray(Solution=Solution, KerSpType=KerSpType, \
            N0=N0, N1=N1, DK=DK, L0=L0, L1=L1, Fi=Fi, Fj=Fj, Fpq=Fpq, \
            SEPARATE_SCALING=SEPARATE_SCALING, ScaSpType=ScaSpType, DS=DS, ScaFi=ScaFi, ScaFj=ScaFj)

        return SfftKerDict, SfftScaDict

class BSpline_MatchingKernel:

    def __init__(self, XY_q, VERBOSE_LEVEL=2):
        self.XY_q = XY_q
        self.VERBOSE_LEVEL = VERBOSE_LEVEL

    def FromArray(self, Solution, KerSpType, KerIntKnotX, KerIntKnotY, N0, N1, DK, L0, L1, Fi, Fj, Fpq, \
        SEPARATE_SCALING, ScaSpType, ScaIntKnotX, ScaIntKnotY, DS, ScaFi, ScaFj):

        # convert requested coordinates
        sXY_q = self.XY_q.astype(float)   # input requested coordinates in FortranCoor [global convention]
        sXY_q[:, 0] /= N0                 # convert to ScaledFortranCoor [local convention]
        sXY_q[:, 1] /= N1                 # convert to ScaledFortranCoor [local convention]

        # read SFFTSolution as dictionaries
        SfftKerDict, SfftScaDict = Read_SFFTSolution().FromArray(Solution=Solution, KerSpType=KerSpType, \
            N0=N0, N1=N1, DK=DK, L0=L0, L1=L1, Fi=Fi, Fj=Fj, Fpq=Fpq, \
            SEPARATE_SCALING=SEPARATE_SCALING, ScaSpType=ScaSpType, DS=DS, ScaFi=ScaFi, ScaFj=ScaFj)

        # realize kernels at given coordinates        
        def Create_BSplineBasis_Req(N, IntKnot, BSplineDegree, ReqCoord):
            BSplineBasis_Req = []
            Knot = np.concatenate(([0.5]*(BSplineDegree+1), IntKnot, [N+0.5]*(BSplineDegree+1)))/N
            Nc = len(IntKnot) + BSplineDegree + 1    # number of control points/coeffcients
            for idx in range(Nc):
                Coeff = (np.arange(Nc) == idx).astype(float)
                BaseFunc = BSpline(t=Knot, c=Coeff, k=BSplineDegree, extrapolate=False)
                BSplineBasis_Req.append(BaseFunc(ReqCoord))
            BSplineBasis_Req = np.array(BSplineBasis_Req)
            return BSplineBasis_Req

        w0, w1 = (L0-1)//2, (L1-1)//2

        if KerSpType == 'Polynomial':

            KerBASE = np.array([
                sXY_q[:, 0]**i * sXY_q[:, 1]**j \
                for i in range(DK+1) for j in range(DK+1-i)
            ])  # (Fij, NPOINT)

            KerCOEFF = np.array([
                SfftKerDict[(i, j)] \
                for i in range(DK+1) for j in range(DK+1-i)
            ])  # (Fij, KerNX, KerNY)

            KerStack = np.tensordot(KerBASE, KerCOEFF, (0, 0))   # (NPOINT, KerNX, KerNY)
        
        if KerSpType == 'B-Spline':

            KerSplBasisX_q = Create_BSplineBasis_Req(N=N0, IntKnot=KerIntKnotX, BSplineDegree=DK, ReqCoord=sXY_q[:, 0])
            KerSplBasisY_q = Create_BSplineBasis_Req(N=N1, IntKnot=KerIntKnotY, BSplineDegree=DK, ReqCoord=sXY_q[:, 1])

            KerBASE = np.array([
                KerSplBasisX_q[i] * KerSplBasisY_q[j] \
                for i in range(Fi) for j in range(Fj)
            ])  # (Fij, NPOINT)

            KerCOEFF = np.array([
                SfftKerDict[(i, j)] \
                for i in range(Fi) for j in range(Fj)
            ])  # (Fij, KerNX, KerNY)

            KerStack = np.tensordot(KerBASE, KerCOEFF, (0, 0))   # (NPOINT, KerNX, KerNY)
            
        # convert specific coefficients to kernel pixels (Note that sfft uses modified delta basis)
        if SfftScaDict is None:
            KerCENT = KerStack[:, w0, w1].copy()
            KerCENT -= np.sum(KerStack, axis=(1,2)) - KerStack[:, w0, w1]
            KerStack[:, w0, w1] = KerCENT   # UPDATE

        if SfftScaDict is not None:

            if ScaSpType == 'Polynomial':

                ScaBASE = np.array([
                    sXY_q[:, 0]**i * sXY_q[:, 1]**j \
                    for i in range(DS+1) for j in range(DS+1-i)
                ])  # (ScaFij, NPOINT)

                ScaCOEFF = np.array([
                    SfftScaDict[(i, j)] \
                    for i in range(DS+1) for j in range(DS+1-i)
                ])  # (ScaFij)

                KerCENT = np.matmul(ScaCOEFF.reshape((1, -1)), ScaBASE)[0]   # (NPOINT)
                KerCENT -= np.nansum(KerStack, axis=(1,2))
                KerStack[:, w0, w1] = KerCENT  # UPDATE
            
            if ScaSpType == 'B-Spline':
            
                ScaSplBasisX_q = Create_BSplineBasis_Req(N=N0, IntKnot=ScaIntKnotX, BSplineDegree=DS, ReqCoord=sXY_q[:, 0])
                ScaSplBasisY_q = Create_BSplineBasis_Req(N=N1, IntKnot=ScaIntKnotY, BSplineDegree=DS, ReqCoord=sXY_q[:, 1])

                ScaBASE = np.array([
                    ScaSplBasisX_q[i] * ScaSplBasisY_q[j] \
                    for i in range(ScaFi) for j in range(ScaFj)
                ])  # (ScaFij, NPOINT)

                ScaCOEFF = np.array([
                    SfftScaDict[(i, j)] \
                    for i in range(ScaFi) for j in range(ScaFj)
                ])  # (ScaFij)

                KerCENT = np.matmul(ScaCOEFF.reshape((1, -1)), ScaBASE)[0]   # (NPOINT)
                KerCENT -= np.nansum(KerStack, axis=(1,2))
                KerStack[:, w0, w1] = KerCENT  # UPDATE
        
        return KerStack
    
    def FromFITS(self, FITS_Solution):

        phdr = fits.getheader(FITS_Solution, ext=0)
        KerHW = phdr['KERHW']
        KerSpType = phdr['KSPTYPE']
        KerIntKnotX = [phdr['KIKX%d' %i] for i in range(phdr['NKIKX'])]
        KerIntKnotY = [phdr['KIKY%d' %i] for i in range(phdr['NKIKY'])]

        N0, N1 = int(phdr['N0']), int(phdr['N1'])
        DK = int(phdr['DK'])
        
        L0, L1 = int(phdr['L0']), int(phdr['L1'])
        Fi, Fj = int(phdr['FI']), int(phdr['FJ'])
        Fpq = int(phdr['FPQ'])

        SEPARATE_SCALING = phdr['SEPSCA'] == 'True'
        ScaSpType, DS = None, None
        ScaIntKnotX, ScaIntKnotY = None, None
        if SEPARATE_SCALING:
            ScaSpType = phdr['SSPTYPE']
            DS = int(phdr['SSPDEG'])
            ScaIntKnotX = [phdr['SIKX%d' %i] for i in range(phdr['NSIKX'])]
            ScaIntKnotY = [phdr['SIKY%d' %i] for i in range(phdr['NSIKY'])]

        ScaFi, ScaFj = None, None
        if SEPARATE_SCALING and DS > 0:
            ScaFi = int(phdr['SCAFI'])
            ScaFj = int(phdr['SCAFJ'])

        if self.VERBOSE_LEVEL in [1, 2]:
            print('\n --//--//--//--//-- SFFT CONFIGURATION --//--//--//--//-- ')

            if KerSpType == 'Polynomial':
                print('\n ---//--- Polynomial Kernel | KerSpDegree %d | KerHW %d ---//---' %(DK, KerHW))
                if not SEPARATE_SCALING:
                    print('\n ---//--- [ENTANGLED] Polynomial Scaling | KerSpDegree %d ---//---' %DK)

            if KerSpType == 'B-Spline':
                print('\n ---//--- B-Spline Kernel | Internal Knots %d,%d | KerSpDegree %d | KerHW %d ---//---' \
                      %(len(KerIntKnotX), len(KerIntKnotY), DK, KerHW))
                if not SEPARATE_SCALING: 
                    print('\n ---//--- [ENTANGLED] B-Spline Scaling | Internal Knots %d,%d | KerSpDegree %d ---//---' \
                          %(len(KerIntKnotX), len(KerIntKnotY), DK))
            
            if SEPARATE_SCALING:
                if ScaSpType == 'Polynomial':
                    print('\n ---//--- [SEPARATE] Polynomial Scaling | ScaSpDegree %d ---//---' %DS)
                
                if ScaSpType == 'B-Spline':
                    print('\n ---//--- [SEPARATE] B-Spline Scaling | Internal Knots %d,%d | ScaSpDegree %d ---//---' \
                          %(len(ScaIntKnotX), len(ScaIntKnotY), DS))

        Solution = fits.getdata(FITS_Solution, ext=0)[0]
        KerStack = self.FromArray(Solution=Solution, KerSpType=KerSpType, \
            KerIntKnotX=KerIntKnotX, KerIntKnotY=KerIntKnotY, N0=N0, N1=N1, \
            DK=DK, L0=L0, L1=L1, Fi=Fi, Fj=Fj, Fpq=Fpq, SEPARATE_SCALING=SEPARATE_SCALING, \
            ScaSpType=ScaSpType, ScaIntKnotX=ScaIntKnotX, ScaIntKnotY=ScaIntKnotY, \
            DS=DS, ScaFi=ScaFi, ScaFj=ScaFj)
        
        return KerStack

class ConvKernel_Convertion:

    """
    # * Remarks on Convolution Theorem
    #    NOTE on Symbols: L theoretically can be even / odd, recall w = (L-1)//2 & w' = L//2 and w+w' = L-1
    #    a. To make use of FFT with convolution theorem, it is necessary to convert convolution-kernel 
    #        with relatively small size by Circular-Shift & tail-Zero-padding (CSZ) to align the Image-Size.
    #    b. If we have an image elementwise-multiplication FI * FK, where FI and FK are conjugate symmetric,
    #        Now we want to get its convolution counterpart in real space, we can calculate the convolution kernel by iCSZ on IDFT(FK).
    #        In this process, we have to check the lost weight by size truncation, if the lost weight is basically inappreciable, 
    #        the equivalent convolution is a good approximation.
    #
    """

    def CSZ(ConvKernel, N0, N1):
        L0, L1 = ConvKernel.shape  
        w0, w1 = (L0-1) // 2, (L1-1) // 2      
        pd0, pd1 = N0 - L0, N1 - L1
        TailZP = np.lib.pad(ConvKernel, ((0, pd0), (0, pd1)), 'constant', constant_values=(0, 0))    # Tail-Zero-Padding
        KIMG_CSZ = np.roll(np.roll(TailZP, -w0, axis=0), -w1, axis=1)    # Circular-Shift
        return KIMG_CSZ

    def iCSZ(KIMG, L0, L1):
        N0, N1 = KIMG.shape
        w0, w1 = (L0-1) // 2, (L1-1) // 2
        KIMG_iCSZ = np.roll(np.roll(KIMG, w1, axis=1), w0, axis=0)    # inverse Circular-Shift
        ConvKernel = KIMG_iCSZ[:L0, :L1]    # Tail-Truncation 
        lost_weight = 1.0 - np.sum(np.abs(ConvKernel)) / np.sum(np.abs(KIMG_iCSZ))
        return ConvKernel, lost_weight

class BSpline_DeCorrelation:
    @staticmethod
    def BDC(MK_JLst, SkySig_JLst, MK_ILst=[], SkySig_ILst=[], MK_Fin=None, \
        KERatio=2.0, DENO_CLIP_RATIO=100000.0, VERBOSE_LEVEL=2):
        
        """
        # * Remarks on Input
        #   i. Image-Stacking Mode: NumI = 0
        #      MK_Fin will not work, NumJ >= 2 and NOT all J's kernel are None
        #   ii. Image-Subtraction Mode: NumI & NumJ >= 1
        #       NOT all (I / J / Fin) kernel are None
        #
        # * Remarks on difference flip
        #   D = REF - SCI * K
        #   fD = SCI * K - REF = fREF - fSCI * K
        #   NOTE: fD and D have consistent decorrelation kernel
        #         as Var(REF) = Var(fREF) and Var(SCI) = Var(fSCI)
        #
        # * Remarks on DeCorrelation Kernel Size
        #   The DeCorrelation Kernel is derived in Fourier Space, but it is not proper to directly 
        #   perform DeCorrelation in Fourier Space (equivalently, perform a convolution with Kernel-Size = Image-Size).
        #   a. convolution (and resampling) process has very local effect, it is unnecesseary to use a large decorrelation kernel.
        #   b. if we use a large decorrelation kernel, you will find only very few engery distributed at outskirt regions, 
        #      however, the low weight can degrade the decorrelation convolution by the remote saturated pixels.
        #
        """

        NumI, NumJ = len(MK_ILst), len(MK_JLst)
        if NumI == 0: 
            Mode = 'Image-Stacking'
            if NumJ < 2: 
                _error_message = 'Image-Stacking Mode requires at least 2 J-images!'
                raise Exception('MeLOn ERROR: %s' %_error_message)
            if np.sum([MKj is not None for MKj in MK_JLst]) == 0:
                _error_message = 'Image-Stacking Mode requires at least 1 not-None J-kernel!'
                raise Exception('MeLOn ERROR: %s' %_error_message)

        if NumI >= 1:
            Mode = 'Image-Subtraction'
            if NumJ == 0: 
                _error_message = 'Image-Subtraction Mode requires at least 1 I-image & 1 J-image!'
                raise Exception('MeLOn ERROR: %s' %_error_message)
            if np.sum([MK is not None for MK in MK_JLst+MK_ILst+[MK_Fin]]) == 0:
                _error_message = 'Image-Subtraction Mode requires at least 1 not-None J/I/Fin-kernel!'
                raise Exception('MeLOn ERROR: %s' %_error_message)
        
        MK_Queue = MK_JLst.copy()
        if Mode == 'Image-Subtraction': MK_Queue += [MK_Fin] + MK_ILst
        L0_KDeCo = int(round(KERatio * np.max([MK.shape[0] for MK in MK_Queue if MK is not None])))
        L1_KDeCo = int(round(KERatio * np.max([MK.shape[1] for MK in MK_Queue if MK is not None])))
        if L0_KDeCo%2 == 0: L0_KDeCo += 1
        if L1_KDeCo%2 == 0: L1_KDeCo += 1

        if VERBOSE_LEVEL in [1, 2]:
            _message = 'DeCorrelation Kernel with size [%d, %d]' %(L0_KDeCo, L1_KDeCo)
            print('MeLOn CheckPoint: %s' %_message)

        # trivial image size, just typically larger than the kernel size.
        N0 = 2 ** (math.ceil(np.log2(np.max([MK.shape[0] for MK in MK_Queue if MK is not None])))+1)
        N1 = 2 ** (math.ceil(np.log2(np.max([MK.shape[1] for MK in MK_Queue if MK is not None])))+1)
        
        # construct the DeNonimator (a real-positive map) in Fourier Space
        uMK = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]]).astype(float)
        def Get_JTerm(MKj, skysig):
            if MKj is not None: KIMG_CSZ = ConvKernel_Convertion.CSZ(MKj, N0, N1)
            if MKj is None: KIMG_CSZ = ConvKernel_Convertion.CSZ(uMK, N0, N1)
            kft = np.fft.fft2(KIMG_CSZ)
            kft2 = (np.conj(kft) * kft).real
            term = (skysig**2 * kft2) / NumJ**2
            return term
        
        if MK_Fin is not None: KIMG_CSZ = ConvKernel_Convertion.CSZ(MK_Fin, N0, N1)
        if MK_Fin is None: KIMG_CSZ = ConvKernel_Convertion.CSZ(uMK, N0, N1)
        kft = np.fft.fft2(KIMG_CSZ)
        kft2_Fin = (np.conj(kft) * kft).real

        def Get_ITerm(MKi, skysig):
            if MKi is not None: KIMG_CSZ = ConvKernel_Convertion.CSZ(MKi, N0, N1)
            if MKi is None: KIMG_CSZ = ConvKernel_Convertion.CSZ(uMK, N0, N1)
            kft = np.fft.fft2(KIMG_CSZ)
            kft2 = (np.conj(kft) * kft).real
            term = (skysig**2 * kft2 * kft2_Fin) / NumI**2 
            return term
        
        DeNo = 0.0
        for MKj, skysig in zip(MK_JLst, SkySig_JLst):
            DeNo += Get_JTerm(MKj, skysig)
        if Mode == 'Image-Subtraction':
            for MKi, skysig in zip(MK_ILst, SkySig_ILst):
                DeNo += Get_ITerm(MKi, skysig)

        # clipping to avoid too small denominator
        if VERBOSE_LEVEL in [2]:
            print('MeLOn CheckPoint: Initial Max/Min [%.1f] in Denominator Map' \
                %(np.max(DeNo)/np.min(DeNo)))
        
        DENO_CLIP_THRESH = np.max(DeNo)/DENO_CLIP_RATIO
        DENO_CLIP_MASK = DeNo < DENO_CLIP_THRESH
        DeNo[DENO_CLIP_MASK] = DENO_CLIP_THRESH

        if VERBOSE_LEVEL in [2]:
            print('MeLOn CheckPoint: DENOMINATOR CLIPPING TWEAKED [%s] PIXELS' \
                %('{:.2%}'.format(np.sum(DENO_CLIP_MASK)/(N0*N1))))

        FDeCo = np.sqrt(1.0 / DeNo)        # real & conjugate-symmetric
        DeCo = np.fft.ifft2(FDeCo).real    # no imaginary part
        KDeCo, lost_weight = ConvKernel_Convertion.iCSZ(DeCo, L0_KDeCo, L1_KDeCo)
        KDeCo = KDeCo / np.sum(KDeCo)      # rescale to have Unit kernel sum

        if VERBOSE_LEVEL in [1, 2]:
            _message = 'Tail-Truncation Lost-Weight [%.4f %s] (Absolute Percentage Error)' %(lost_weight*100, '%')
            print('MeLOn CheckPoint: %s' %_message)

        return KDeCo

class BSpline_GridConvolve:
    def __init__(self, PixA_obj, AllocatedL, KerStack, \
        nan_fill_value=0.0, use_fft=False, normalize_kernel=True):

        """
        # * Remarks on Grid-wise Spave-Varying Convolution
        #   Allocated LabelMap has same shape with PixA_obj to show the image segmentation (Compact-Box!)
        #   Kernel-Stack gives corresponding convolution kernel for each label
        #   For each segment, we would extract Esegment according to the label with a extended boundary
        #   Perform convolution and then send the values within this segment to output image.
        
        # * A Typcical Example of AllocatedL & KerStack
        
        TiHW = 10
        N0, N1 = 1024, 1024

        lab = 0
        TiN = 2*TiHW+1
        XY_TiC = []
        AllocatedL = np.zeros((N0, N1), dtype=int)
        for xs in np.arange(0, N0, TiN):
            xe = np.min([xs+TiN, N0])
            for ys in np.arange(0, N1, TiN):
                ye = np.min([ys+TiN, N1])
                AllocatedL[xs: xe, ys: ye] = lab
                x_q = 0.5 + xs + (xe - xs)/2.0   # tile-center (x)
                y_q = 0.5 + ys + (ye - ys)/2.0   # tile-center (y)
                XY_TiC.append([x_q, y_q])
                lab += 1
        XY_TiC = np.array(XY_TiC)
        
        """

        PixA_in = PixA_obj.copy()
        PixA_in[np.isnan(PixA_in)] = nan_fill_value
        self.PixA_in = PixA_in
        
        self.AllocatedL = AllocatedL
        self.KerStack = KerStack
        self.use_fft = use_fft
        self.normalize_kernel = normalize_kernel

    def GSVC_CPU(self, nproc=32):
        
        N0, N1 = self.PixA_in.shape
        Nseg, L0, L1 = self.KerStack.shape
        w0 = int((L0-1)/2)
        w1 = int((L1-1)/2)
        IBx, IBy = w0+1, w1+1
        
        def func_conv(idx):
            Ker = self.KerStack[idx]
            lX, lY = np.where(self.AllocatedL == idx)
            xs, xe = lX.min(), lX.max()
            ys, ye = lY.min(), lY.max()

            xEs, xEe = max([0, xs-IBx]), min([N0-1, xe+IBx])
            yEs, yEe = max([0, ys-IBy]), min([N1-1, ye+IBy])
            PixA_Emini = self.PixA_in[xEs: xEe+1, yEs: yEe+1]

            if not self.use_fft:
                _CPixA = convolve(PixA_Emini, Ker, boundary='fill', \
                    fill_value=0.0, normalize_kernel=self.normalize_kernel)
            else:
                _CPixA = convolve_fft(PixA_Emini, Ker, boundary='fill', \
                    fill_value=0.0, normalize_kernel=self.normalize_kernel)
            
            fragment = _CPixA[xs-xEs: (xs-xEs)+(xe+1-xs), ys-yEs: (ys-yEs)+(ye+1-ys)]
            xyrg = xs, xe+1, ys, ye+1
            return xyrg, fragment

        taskid_lst = np.arange(Nseg)
        mydict = Multi_Proc.MP(taskid_lst=taskid_lst, func=func_conv, nproc=nproc, mode='mp')

        PixA_GRID_SVConv = np.zeros((N0, N1)).astype(float)
        for idx in taskid_lst:
            xyrg, fragment = mydict[idx]
            PixA_GRID_SVConv[xyrg[0]: xyrg[1], xyrg[2]: xyrg[3]] = fragment
        
        return PixA_GRID_SVConv
    
    def GSVC_GPU(self, CUDA_DEVICE='0', CLEAN_GPU_MEMORY=False, nproc=32):
        
        import cupy as cp
        from cupyx.scipy.signal import fftconvolve, convolve2d
        device = cp.cuda.Device(int(CUDA_DEVICE))
        device.use()

        if CLEAN_GPU_MEMORY:
            mempool = cp.get_default_memory_pool()
            pinned_mempool = cp.get_default_pinned_memory_pool()
            mempool.free_all_blocks()
            pinned_mempool.free_all_blocks()

        N0, N1 = self.PixA_in.shape
        Nseg, L0, L1 = self.KerStack.shape
        w0 = int((L0-1)/2)
        w1 = int((L1-1)/2)
        IBx, IBy = w0+1, w1+1

        PixA_in_GPU = cp.array(self.PixA_in, dtype=np.float64)
        if not self.normalize_kernel:
            KerStack_GPU = cp.array(self.KerStack, dtype=np.float64)
        else:
            sums = np.sum(self.KerStack, axis=(1,2))
            KerStack_GPU = cp.array(self.KerStack / sums[:, np.newaxis, np.newaxis], dtype=np.float64)

        def func_getIdx(idx):
            lX, lY = np.where(self.AllocatedL == idx)
            xs, xe = lX.min(), lX.max()
            ys, ye = lY.min(), lY.max()
            xEs, xEe = max([0, xs-IBx]), min([N0-1, xe+IBx])
            yEs, yEe = max([0, ys-IBy]), min([N1-1, ye+IBy])
            return (xs, xe, ys, ye, xEs, xEe, yEs, yEe)

        taskid_lst = np.arange(Nseg)
        IdxDICT = Multi_Proc.MP(taskid_lst=taskid_lst, func=func_getIdx, nproc=nproc, mode='mp')

        PixA_GRID_SVConv_GPU = cp.zeros((N0, N1), dtype=np.float64)
        if self.use_fft:
            for idx in range(Nseg):
                Ker_GPU = KerStack_GPU[idx]
                xs, xe, ys, ye, xEs, xEe, yEs, yEe = IdxDICT[idx]
                PixA_Emini_GPU = PixA_in_GPU[xEs: xEe+1, yEs: yEe+1]
                _CPixA_GPU = fftconvolve(PixA_Emini_GPU, Ker_GPU, mode='same')  # as if boundary filled by 0.0
                fragment_GPU = _CPixA_GPU[xs-xEs: (xs-xEs)+(xe+1-xs), ys-yEs: (ys-yEs)+(ye+1-ys)]
                PixA_GRID_SVConv_GPU[xs: xe+1, ys: ye+1] = fragment_GPU
                
        if not self.use_fft:
            for idx in range(Nseg):
                Ker_GPU = KerStack_GPU[idx]
                xs, xe, ys, ye, xEs, xEe, yEs, yEe = IdxDICT[idx]
                PixA_Emini_GPU = PixA_in_GPU[xEs: xEe+1, yEs: yEe+1]
                _CPixA_GPU = convolve2d(PixA_Emini_GPU, Ker_GPU, mode='same', boundary='fill', fillvalue=0.0)
                fragment_GPU = _CPixA_GPU[xs-xEs: (xs-xEs)+(xe+1-xs), ys-yEs: (ys-yEs)+(ye+1-ys)]
                PixA_GRID_SVConv_GPU[xs: xe+1, ys: ye+1] = fragment_GPU
        PixA_GRID_SVConv = cp.asnumpy(PixA_GRID_SVConv_GPU)

        return PixA_GRID_SVConv
