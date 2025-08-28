"""

(ngs)xfem
=========

A module for unfitted finite element discretizations in NGSolve

Submodules:
xfem.cutmg ... MultiGrid for CutFEM
xfem.lsetcurving ... isoparametric unfitted FEM
xfem.lset_spacetime ... isoparametric unfitted space-time FEM
xfem.mlset ... multiple level sets
xfem.utils ... some example level set geometries
"""
from __future__ import annotations
import functools
from functools import partial
import ngsolve as ngsolve
from ngsolve.comp import FESpace
from ngsolve.comp import GridFunction
from ngsolve.comp import H1
from ngsolve.comp import Integrate as ngsolve_Integrate
from ngsolve.comp import L2
from ngsolve.comp import LinearForm
from ngsolve.comp import ProxyFunction
from ngsolve.comp import Set as ngsolveSet
from ngsolve.comp import SymbolicBFI as ngsolve_SymbolicBFI
from ngsolve.comp import SymbolicLFI as ngsolve_SymbolicLFI
from ngsolve.fem import CoefficientFunction
from ngsolve.fem import IfPos
from ngsolve.fem import Parameter
from ngsolve.internal import Center
from ngsolve.internal import Move
from ngsolve.internal import Rotate
from ngsolve.internal import SnapShot
from ngsolve.internal import TclVariables
from ngsolve.internal import VideoAddFrame
from ngsolve.internal import VideoFinalize
from ngsolve.internal import VideoStart
from ngsolve.internal import Zoom
import os as os
from pyngcore.pyngcore import BitArray
from xfem.xfem import BitArrayCF
from xfem.xfem import COMBINED_DOMAIN_TYPE
from xfem.xfem import CSpaceTimeFESpace
from xfem.xfem import CXFESpace
from xfem.xfem import CompoundBitArray
from xfem.xfem import CompoundProlongation
from xfem.xfem import CreateTimeRestrictedGF
from xfem.xfem import CutDifferentialSymbol
from xfem.xfem import CutInfo
from xfem.xfem import DOMAIN_TYPE
from xfem.xfem import ElementAggregation
from xfem.xfem import ExtensionEmbedding
from xfem.xfem import FacetPatchDifferentialSymbol
from xfem.xfem import GCC3FE
from xfem.xfem import GetDofsOfElements
from xfem.xfem import GetDofsOfFacets
from xfem.xfem import GetElementsWithNeighborFacets
from xfem.xfem import GetElementsWithSharedVertex
from xfem.xfem import GetFacetsWithNeighborTypes
from xfem.xfem import GlobalNgsxfemVariables
from xfem.xfem import IntegrateX
from xfem.xfem import IntegrationPointExtrema
from xfem.xfem import InterpolateToP1
from xfem.xfem import MultiLevelsetCutInfo
from xfem.xfem import P1Prolongation
from xfem.xfem import P2CutProlongation
from xfem.xfem import P2Prolongation
from xfem.xfem import PatchwiseSolve
from xfem.xfem import ProjectShift
from xfem.xfem import QUAD_DIRECTION_POLICY
from xfem.xfem import ReferenceTimeVariable
from xfem.xfem import RefineAtLevelSet
from xfem.xfem import Restrict
from xfem.xfem import RestrictGFInTime
from xfem.xfem import RestrictedBilinearFormComplex
from xfem.xfem import RestrictedBilinearFormDouble
from xfem.xfem import SFESpace
from xfem.xfem import ScalarTimeFE
from xfem.xfem import SpaceTimeFESpace
from xfem.xfem import SpaceTimeInterpolateToP1
from xfem.xfem import SpaceTimeVTKOutput
from xfem.xfem import SymbolicCutBFI
from xfem.xfem import SymbolicCutLFI
from xfem.xfem import SymbolicFacetPatchBFI
from xfem.xfem import TIME_DOMAIN_TYPE
from xfem.xfem import TimeVariableCoefficientFunction
from xfem.xfem import XFESpace
from xfem.xfem import XToNegPos
from xfem.xfem import dn
from xfem.xfem import fix_tref_coef
from xfem.xfem import fix_tref_gf
from xfem.xfem import fix_tref_proxy
from xfem.xfem import shifted_eval
from . import _version
from . import xfem
__all__: list[str] = ['ANY', 'AggEmbedding', 'BOTTOM', 'BitArray', 'BitArrayCF', 'CDOM_IF', 'CDOM_NEG', 'CDOM_POS', 'COMBINED_DOMAIN_TYPE', 'CSpaceTimeFESpace', 'CXFESpace', 'Center', 'CoefficientFunction', 'CompoundBitArray', 'CompoundProlongation', 'CreateTimeRestrictedGF', 'CutDifferentialSymbol', 'CutInfo', 'CutRatioGF', 'DOMAIN_TYPE', 'DrawDC', 'DrawDiscontinuous_std', 'DrawDiscontinuous_webgui', 'DummyScene', 'ElementAggregation', 'ExtensionEmbedding', 'FALLBACK', 'FESpace', 'FIRST', 'FacetPatchDifferentialSymbol', 'GCC3FE', 'GetDofsOfElements', 'GetDofsOfFacets', 'GetElementsWithNeighborFacets', 'GetElementsWithSharedVertex', 'GetFacetsWithNeighborTypes', 'GlobalNgsxfemVariables', 'GridFunction', 'H1', 'HAS', 'HASNEG', 'HASPOS', 'IF', 'INTERVAL', 'IfPos', 'IndicatorCF', 'Integrate', 'IntegrateX', 'Integrate_X_special_args', 'IntegrationPointExtrema', 'InterpolateToP1', 'IsCut', 'L2', 'LinearForm', 'MakeDiscontinuousDraw', 'Move', 'MultiLevelsetCutInfo', 'NEG', 'NO', 'NoDeformation', 'OPTIMAL', 'P1Prolongation', 'P2CutProlongation', 'P2Prolongation', 'POS', 'Parameter', 'PatchwiseSolve', 'ProjectShift', 'ProxyFunction', 'QUAD_DIRECTION_POLICY', 'ReferenceTimeVariable', 'RefineAtLevelSet', 'Restrict', 'RestrictGFInTime', 'RestrictedBilinearForm', 'RestrictedBilinearFormComplex', 'RestrictedBilinearFormDouble', 'Rotate', 'SFESpace', 'ScalarTimeFE', 'SnapShot', 'SpaceTimeFESpace', 'SpaceTimeInterpolateToP1', 'SpaceTimeSet', 'SpaceTimeVTKOutput', 'SpaceTimeWeakSet', 'SymbolicBFI', 'SymbolicBFIWrapper', 'SymbolicCutBFI', 'SymbolicCutLFI', 'SymbolicFacetPatchBFI', 'SymbolicLFI', 'SymbolicLFIWrapper', 'TIME_DOMAIN_TYPE', 'TOP', 'TclVariables', 'TimeSlider_Draw', 'TimeSlider_DrawDC', 'TimeVariableCoefficientFunction', 'UNCUT', 'VOL', 'VideoAddFrame', 'VideoFinalize', 'VideoStart', 'XFESpace', 'XToNegPos', 'Zoom', 'all_combined_domain_types', 'all_domain_types', 'clipping_variables', 'dCut', 'dFacetPatch', 'ddtref', 'dmesh', 'dn', 'dt', 'dtref', 'dummy_scene', 'dx', 'dxtref', 'extend', 'extend_grad', 'fix_t', 'fix_t_coef', 'fix_t_gf', 'fix_t_proxy', 'fix_tref', 'fix_tref_coef', 'fix_tref_gf', 'fix_tref_proxy', 'kappa', 'neg', 'neg_grad', 'ngsolve', 'ngsolveSet', 'ngsolve_Integrate', 'ngsolve_SymbolicBFI', 'ngsolve_SymbolicLFI', 'ngsxfemglobals', 'os', 'partial', 'pos', 'pos_grad', 'shifted_eval', 'tref', 'viewoptions', 'viewoptions_variables', 'visoptions', 'visoptions_variables', 'xfem']
class DummyScene:
    def Redraw(self, blocking = False):
        ...
    def __init__(self):
        ...
class NoDeformation:
    """
    
    Dummy deformation class. Does nothing to the mesh. Has two dummy members:
      * lset_p1 : ngsolve.GridFunction
        The piecewise linear level set function 
      * deform : ngsolve.GridFunction
        A zero GridFunction (for compatibility with netgen Draw(... deformation=))
    Has method
      * self.CalcDeformation()
        Convenience function  for code compatibility with LevelSetMeshAdaptation class
        
    """
    def CalcDeformation(self, levelset):
        """
        
                P1 interpolation of levelset function for compatibility with
                
        """
    def __enter__(self):
        ...
    def __exit__(self, type, value, tb):
        ...
    def __init__(self, mesh = None, levelset = None, warn = True):
        ...
def AggEmbedding(EA, fes, deformation = None, heapsize = 1000000):
    """
    
        Computes and returns embedding matrix for a patchwise polynomial extension 
        (realized through ghost penalties), 
        followed by averaging if some dofs are shared by multiple patches.
    
        Parameters
    
        elagg : ElementAggregation
          ElementAggregation instace defining the patches which are aggregated into a single element
    
        fes : ngsolve.FESpace
          The finite element space which is aggregated. 
        
        deformation : ngsolve.GridFunction [mesh.dim]
          The mesh deformation (needed for Ghost penalty assembly)
    
        heapsize : int
            heapsize for local computations.
        
    """
def CutRatioGF(cutinfo):
    """
    
    Ratio between negative and full part of an element. Vector taken from CutInfo and put into a
    piecewise constant GridFunction.
        
    """
def DrawDiscontinuous_std(StdDraw, levelset, fneg, fpos, *args, **kwargs):
    ...
def DrawDiscontinuous_webgui(WebGuiDraw, levelset, fneg, fpos, *args, **kwargs):
    ...
def HAS(domain_type):
    """
    
    For a given domain_type return the combined domain type that 
    includes all elements that have a part in the domain type.
        
    """
def IndicatorCF(mesh, ba, facets = False):
    """
    
    Returns a CoefficientFunction that evaluates a BitArray. On elements/facets with an index i where
    the BitArray evaluates to true the CoefficientFunction will evaluate as 1, otherwise as 0. Similar
    functionality (only on elements) can be obtained with BitArrayCF.
        
    """
def Integrate(levelset_domain = None, *args, **kwargs):
    """
    
    Integrate-wrapper. If a dictionary 'levelset_domain' is provided integration will be done on the
    level set part of the mesh. The dictionary contains the level set function (CoefficientFunciton or
    GridFunction) and the domain-type (NEG/POS/IF). If the dictionary is not provided, the standard
    Integrate function from NGSolve will be called.
    
    Parameters
    
    levelset_domain : dictionary
      entries:
      * "levelset": 
        singe level set : ngsolve.CoefficientFunction
          CoefficientFunction that describes the geometry. In the best case lset is a GridFunction of an
          FESpace with scalar continuous piecewise (multi-) linear basis functions.
        multiple level sets: tuple(ngsolve.GridFunction)
          Tuple of GridFunctions that describe the geometry.
      * "domain_type" :
        single level set: {NEG,POS,IF} (ENUM) 
          Integration on the domain where either:
          * the level set function is negative (NEG)
          * the level set function is positive (POS)
          * the level set function is zero     (IF )
        multiple level sets: {tuple({ENUM}), list(tuple(ENUM)), DomainTypeArray}
          Integration on the domains specified
      * "subdivlvl" : int
        On simplex meshes a subtriangulation is created on which the level set function lset is
        interpolated piecewise linearly. Based on this approximation, the integration rule is
        constructed. Note: this argument only works on simplices.
      * "order" : int
        (default: entry does not exist or value -1)
        overwrites "order"-arguments in the integration (affects only spatial integration)
      * "time_order" : int 
        defines integration order in time (for space-time integrals only)
      * "quad_dir_policy" : {FIRST, OPTIMAL, FALLBACK} (ENUM)
        Integration direction policy for iterated integrals approach
        * first direction is used unless not applicable (FIRST)
        * best direction (in terms of transformation constant) is used (OPTIMAL)
        * subdivision into simplices is always used (FALLBACK)
    
    mesh :
      Mesh to integrate on (on some part)
    
    cf : ngsolve.CoefficientFunction
      the integrand
    
    order : int (default = 5)
      integration order. Can be overruled by "order"-entry of the levelset_domain dictionary.
    
    time_order : int (default = -1)
      integration order in time (for space-time integration), default: -1 (no space-time integrals)
    
    region_wise : bool
      (only active for non-levelset version)
    
    element_wise : bool
      integration result is return per element
    
    deformation : gridfunction (or None)
      deformation of the mesh (only active if levelset_domain is not None)
    
    ip_container : list (or None)
      a list to store integration points (for debugging or visualization purposes only!)
    
    heapsize : int
      heapsize for local computations.
        
    """
def Integrate_X_special_args(levelset_domain = {}, cf = None, mesh = None, VOL_or_BND = ..., order = 5, time_order = -1, region_wise = False, element_wise = False, heapsize = 1000000, deformation = None, ip_container = None):
    """
    
    Integrate_X_special_args should not be called directly.
    See documentation of Integrate.
        
    """
def IsCut(mesh, lset_approx, subdivlvl = 0):
    """
    
    GridFunction that is 1 on cut elements, 0 otherwise (deprecated). Use CutInfo-functionality (perhaps
    combined with BitArrayCF).
        
    """
def MakeDiscontinuousDraw(Draw):
    """
    
    Generates a Draw-like visualization function. If Draw is from the webgui, a special evaluator is used to draw a pixel-sharp discontinuity otherwise an IfPos-CoefficientFunction is used.     
        
    """
def RestrictedBilinearForm(space = None, name = 'blf', element_restriction = None, facet_restriction = None, trialspace = None, testspace = None, **kwargs):
    """
    
        Creates a restricted bilinear form, which is bilinear form with a reduced MatrixGraph
        compared to the usual BilinearForm. BitArray(s) define on which elements/facets entries will be
        created.
    
        Use cases:
    
          * ghost penalty type stabilization:
            Facet-stabilization that are introduced only act on a few facets in the mesh. By providing the
            information on the corresponding facets, these additional couplings will only be introduced
            where necessary.
    
          * fictitious domain methods (domain decomposition methods):
            When PDE problems are only solved on a part of a domain while a finite element space is used
            that is still defined on the whole domain, a BitArray can be used to mark the 'active' part of
            the mesh. 
    
        Parameters
    
        space: ngsolve.FESpace
          finite element space on which the bilinear form is defined. If trial space and test space are different 
          they can be specified using the trialspace and testspace arguments.
    
        name : string
          name of the bilinear form
    
        element_restriction : ngsolve.BitArray
          BitArray defining the 'active mesh' element-wise
    
        facet_restriction : ngsolve.BitArray
          BitArray defining the 'active facets'. This is only relevant if FESpace has DG-terms (dgjumps=True)
        
        trialspace : ngsolve.FESpace
          finite element space on which the bilinear form is defined
          (trial space).
        
        testspace : ngsolve.FESpace
          finite element space on which the bilinear form is defined
          (test space).
    
        kwargs : keyword arguments
          kwargs are pasre to flags and passed to bilinearform 
        
    """
def SpaceTimeSet(self, cf, *args, **kwargs):
    """
    
    Overrides the NGSolve version of Set in case of a space-time FESpace.
    In this case the usual Set() is used on each nodal dof in time.
        
    """
def SpaceTimeWeakSet(gfu_e, cf, space_fes):
    """
    
    Ondocumented feature
        
    """
def SymbolicBFIWrapper(levelset_domain = None, *args, **kwargs):
    """
    
    Wrapper around SymbolicBFI to allow for integrators on level set domains (see also
    SymbolicCutBFI). The dictionary contains the level set function (CoefficientFunciton or
    GridFunction) and the domain-type (NEG/POS/IF). If the dictionary is not provided, the standard
    SymbolicBFI function from NGSolve will be called.
    
    Parameters
    
    levelset_domain : dictionary
      entries:
      * "levelset": 
        singe level set : ngsolve.CoefficientFunction
          CoefficientFunction that describes the geometry. In the best case lset is a GridFunction of an
          FESpace with scalar continuous piecewise (multi-) linear basis functions.
        multiple level sets: tuple(ngsolve.GridFunction)
          Tuple of GridFunctions that describe the geometry.
      * "domain_type" :
        single level set: {NEG,POS,IF} (ENUM) 
          Integration on the domain where either:
          * the level set function is negative (NEG)
          * the level set function is positive (POS)
          * the level set function is zero     (IF )
        multiple level sets: {tuple({ENUM}), list(tuple(ENUM)), DomainTypeArray}
          Integration on the domains specified
      * "subdivlvl" : int
        On simplex meshes a subtriangulation is created on which the level set function lset is
        interpolated piecewise linearly. Based on this approximation, the integration rule is
        constructed. Note: this argument only works on simplices.
      * "order" : int
        (default: entry does not exist or value -1)
        overwrites "order"-arguments in the integration
      * "quad_dir_policy" : {FIRST, OPTIMAL, FALLBACK} (ENUM)
        Integration direction policy for iterated integrals approach
        * first direction is used unless not applicable (FIRST)
        * best direction (in terms of transformation constant) is used (OPTIMAL)
        * subdivision into simplices is always used (FALLBACK)
    
    Other Parameters :
    
      form : ngsolve.CoefficientFunction
        form to integrate
    
      VOL_or_BND : {VOL,BND}
        integrator is defined in the volume or boundary
    
      element_boundary : boolean
        Integration of the boundary of an element
        (not active for level set domains)
    
      skeleton : boolean
        Integration over element-interface
    
      definedon : Region
        Domain description on where the integrator is defined
    
      definedonelements: BitArray
        BitArray that allows integration only on elements or facets (if skeleton=True) that are marked
        True.
    
      deformation : GridFunction
        Specify a specific mesh deformation for a bilinear form
    
      order : int
        Modifies the order of the quadrature rule used. This is overruled by "order"-entry of the 
        levelset_domain dictionary, if the dictionary entry exists.
    
      time_order : int
        order in time that is used in the space-time integration. time_order=-1 means that no space-time
        rule will be applied. This is only relevant for space-time discretizations.
    """
def SymbolicLFIWrapper(levelset_domain = None, *args, **kwargs):
    """
    
    Wrapper around SymbolicLFI to allow for integrators on level set domains (see also
    SymbolicCutLFI). The dictionary contains the level set function (CoefficientFunciton or
    GridFunction) and the domain-type (NEG/POS/IF). If the dictionary is not provided, the standard
    SymbolicLFI function from NGSolve will be called.
    
    Parameters
    
    levelset_domain : dictionary
      entries:
      * "levelset": 
        singe level set : ngsolve.CoefficientFunction
          CoefficientFunction that describes the geometry. In the best case lset is a GridFunction of an
          FESpace with scalar continuous piecewise (multi-) linear basis functions.
        multiple level sets: tuple(ngsolve.GridFunction)
          Tuple of GridFunctions that describe the geometry.
      * "domain_type" :
        single level set: {NEG,POS,IF} (ENUM) 
          Integration on the domain where either:
          * the level set function is negative (NEG)
          * the level set function is positive (POS)
          * the level set function is zero     (IF )
        multiple level sets: {tuple({ENUM}), list(tuple(ENUM)), DomainTypeArray}
          Integration on the domains specified
      * "subdivlvl" : int
        On simplex meshes a subtriangulation is created on which the level set function lset is
        interpolated piecewise linearly. Based on this approximation, the integration rule is
        constructed. Note: this argument only works on simplices.
      * "order" : int
        (default: entry does not exist or value -1)
        overwrites "order"-arguments in the integration
      * "quad_dir_policy" : {FIRST, OPTIMAL, FALLBACK} (ENUM)
        Integration direction policy for iterated integrals approach
        * first direction is used unless not applicable (FIRST)
        * best direction (in terms of transformation constant) is used (OPTIMAL)
        * subdivision into simplices is always used (FALLBACK)
    
    Other Parameters :
    
      form : ngsolve.CoefficientFunction
        form to integrate
    
      VOL_or_BND : {VOL,BND}
        integrator is defined in the volume or boundary
    
      element_boundary : boolean
        Integration of the boundary of an element
        (not active for level set domains)
    
      skeleton : boolean
        Integration over element-interface
    
      definedon : Region
        Domain description on where the integrator is defined
    
      definedonelements: BitArray
        BitArray that allows integration only on elements or facets (if skeleton=True) that are marked
        True.
    
      deformation : GridFunction
          Specify a specific mesh deformation for a linear form
    
      order : int
        Modifies the order of the quadrature rule used. This is overruled by "order"-entry of the 
        levelset_domain dictionary, if the dictionary entry exists.
    
      time_order : int
        order in time that is used in the space-time integration. time_order=-1 means that no space-time
        rule will be applied. This is only relevant for space-time discretizations. Note that
        time_order can only be active if the key "time_order" of the levelset_domain is not set (or -1)
    """
def TimeSlider_Draw(cf, mesh, *args, **kwargs):
    ...
def TimeSlider_DrawDC(cf1, cf2, cf3, mesh, *args, **kwargs):
    ...
def dCut(levelset, domain_type, order = None, subdivlvl = None, time_order = -1, levelset_domain = None, **kwargs):
    """
    
        Differential symbol for cut integration.
    
        Parameters
        ----------
        levelset : ngsolve.GridFunction
            The level set fct. describing the geometry 
            (desirable: P1 approximation).
        domain_type : {POS, IF, NEG, mlset.DomainTypeArray}
            The domain type of interest.
        order : int
            Modify the order of the integration rule used.
        subdivlvl : int
            Number of additional subdivision used on cut elements to
            generate the cut quadrature rule. Note: subdivlvl >0 only
            makes sense if you don't provide a P1 level set function
            and no isoparametric mapping is used.
        definedon : Region
            Domain description on where the integrator is defined.
        vb : {VOL, BND, BBND}
            Integration on mesh volume or its (B)boundary. Default: VOL
            (if combined with skeleton=True VOL refers to interior facets
                                            BND refers to boundary facets)
        element_boundary : bool
            Integration on each element boundary. Default: False
        element_vb : {VOL, BND, BBND}
            Integration on each element or its (B)boundary. Default: VOL
            (is overwritten by element_boundary if element_boundary 
            is True)
        skeleton : bool
            Integration over element-interface. Default: False.
        deformation : ngsolve.GridFunction
            Mesh deformation that is applied. Default: None.
        definedonelements : ngsolve.BitArray
            Allows integration only on elements or facets (if skeleton=True)
            that are marked True. Default: None.
        time_order : int
            Order in time that is used in the space-time integration.
            Default: time_order=-1 means that no space-time rule will be
            applied. This is only relevant for space-time discretizations.
        tref : float
            turns a spatial integral resulting in spatial integration rules
            into a space-time quadrature rule with fixed reference time tref
        levelset_domain : dict
            description of integration domain through a dictionary 
            (deprecated).
    
        Returns
        -------
            CutDifferentialSymbol(VOL)
        
    """
def dFacetPatch(**kwargs):
    """
    
        Differential symbol for facet patch integrators.
    
        Parameters
        ----------
        definedon : Region
            Domain description on where the integrator is defined.
        deformation : ngsolve.GridFunction
            Mesh deformation that is applied during integration. Default: None.
        definedonelements : ngsolve.BitArray
            Allows integration only on a set of facets
            that are marked True. Default: None.
        time_order : int
            Order in time that is used in the space-time integration.
            Default: time_order=-1 means that no space-time rule will be
            applied. This is only relevant for space-time discretizations.
        tref : double
            Turn spatial integration into space-time integration with 
            fixed time tref.
    
        Returns
        -------
          FacetPatchDifferentialSymbol(VOL)
        
    """
def ddtref(func):
    """
    
    Evaluates the 2nd time derivative (w.r.t. the reference time interval) of a Space-Time function.
        
    """
def dmesh(mesh = None, *args, **kwargs):
    """
    
        Differential symbol for the integration over all elements in the mesh.
    
        Parameters
        ----------
        mesh : ngsolve.Mesh
            The spatial mesh.
            The domain type of interest.
        definedon : Region
            Domain description on where the integrator is defined.
        element_boundary : bool
            Integration on each element boundary. Default: False
        element_vb : {VOL, BND, BBND}
            Integration on each element or its (B)boundary. Default: VOL
            (is overwritten by element_boundary if element_boundary 
            is True)
        skeleton : bool
            Integration over element-interface. Default: False.
        deformation : ngsolve.GridFunction
            Mesh deformation. Default: None.
        definedonelements : ngsolve.BitArray
            Allows integration only on elements or facets (if skeleton=True)
            that are marked True. Default: None.
        tref : float
            turns a spatial integral resulting in spatial integration rules
            into a space-time quadrature rule with fixed reference time tref
    
        Return
        ------
            CutDifferentialSymbol(VOL)
        
    """
def dt(func):
    """
    
    Deprecated: use "dtref" instead
        
    """
def dtref(func):
    """
    
    Evaluates the time derivative (w.r.t. the reference time interval) of a Space-Time function.
        
    """
def dxtref(mesh, order = None, time_order = -1, **kwargs):
    """
    
        Differential symbol for the integration over all elements extruded by
        the reference interval [0,1] to space-time prisms.
    
        Parameters
        ----------
        mesh : ngsolve.Mesh
            The spatial mesh.
            The domain type of interest.
        order : int
            Modify the order of the integration rule used.
        definedon : Region
            Domain description on where the integrator is defined.
        vb : {VOL, BND, BBND}
            Integration on domains volume or boundary. Default: VOL
            (if combined with skeleton VOL means interior facets,
                                       BND means boundary facets)
        element_boundary : bool
            Integration on each element boundary. Default: False
        element_vb : {VOL, BND, BBND}
            Integration on each element or its (B)boundary. Default: VOL
            (is overwritten by element_boundary if element_boundary 
            is True)
        skeleton : bool
            Integration over element-interface. Default: False.
        deformation : ngsolve.GridFunction
            Mesh deformation. Default: None.
        definedonelements : ngsolve.BitArray
            Allows integration only on elements or facets (if skeleton=True)
            that are marked True. Default: None.
        time_order : int
            Order in time that is used in the space-time integration.
            Default: time_order=-1 means that no space-time rule will be
            applied. This is only relevant for space-time discretizations.
    
        Return
        ------
            CutDifferentialSymbol(VOL)
        
    """
def extend(func):
    """
    
    Evaluates the XFiniteElement-function independent of the level set domains.
    
    Note:
    This will lead to the same behavior as the function that the XFiniteElement-function is based
    on.
        
    """
def extend_grad(func):
    """
    
    Evaluates the gradient of an XFiniteElement-function independent of the level set domains.
    
    Note:
    This will lead to the same behavior as the function that the XFiniteElement-function is based on.
        
    """
def fix_t(obj, time, *args, **kwargs):
    """
    
      Deprecated: use "fix_tref" instead
      
    """
def fix_t_coef(obj, time, *args, **kwargs):
    ...
def fix_t_gf(obj, time, *args, **kwargs):
    ...
def fix_t_proxy(obj, time, *args, **kwargs):
    ...
def fix_tref(obj, time, *args, **kwargs):
    """
    
    Takes a (possibly space-time) CoefficientFunction and fixes the temporal
    variable to `time` and return this as a new CoefficientFunction.
    Note that all operations are done on the unit interval it is the 
    reference time that is fixed. 
        
    """
def kappa(mesh, lset_approx, subdivlvl = 0):
    """
    
    Tuple of ratios between negative/positive and full
    part of an element (deprecated).
        
    """
def neg(func):
    """
    
    Evaluates an XFiniteElement-function assuming a negative level set domain.
    
    Note:
    This can lead to non-zero values also in domains where the level set function is non-negative.
        
    """
def neg_grad(func):
    """
    
    Evaluates the gradient of an XFiniteElement-function assuming a negative level set domain.
    
    Note:
    This can lead to non-zero values also in domains where the level set function is non-negative.
        
    """
def pos(func):
    """
    
    Evaluates an XFiniteElement-function assuming a positive level set domain.
    
    Note:
    This can lead to non-zero values also in domains where the level set function is non-positive.
        
    """
def pos_grad(func):
    """
    
    Evaluates the gradient of an XFiniteElement-function assuming a positive level set domain.
    
    Note:
    This can lead to non-zero values also in domains where the level set function is non-positive.
        
    """
ANY: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.ANY: 7>
BOTTOM: TIME_DOMAIN_TYPE  # value = <TIME_DOMAIN_TYPE.BOTTOM: 0>
CDOM_IF: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.CDOM_IF: 4>
CDOM_NEG: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.CDOM_NEG: 1>
CDOM_POS: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.CDOM_POS: 2>
DrawDC: functools.partial  # value = functools.partial(<function DrawDiscontinuous_std at 0x107e90a40>, <built-in method Draw of PyCapsule object at 0x107e59a40>)
FALLBACK: QUAD_DIRECTION_POLICY  # value = <QUAD_DIRECTION_POLICY.FALLBACK: 2>
FIRST: QUAD_DIRECTION_POLICY  # value = <QUAD_DIRECTION_POLICY.FIRST: 0>
HASNEG: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.HASNEG: 5>
HASPOS: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.HASPOS: 6>
IF: DOMAIN_TYPE  # value = <DOMAIN_TYPE.IF: 2>
INTERVAL: TIME_DOMAIN_TYPE  # value = <TIME_DOMAIN_TYPE.INTERVAL: 2>
NEG: DOMAIN_TYPE  # value = <DOMAIN_TYPE.NEG: 0>
NO: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.NO: 0>
OPTIMAL: QUAD_DIRECTION_POLICY  # value = <QUAD_DIRECTION_POLICY.OPTIMAL: 1>
POS: DOMAIN_TYPE  # value = <DOMAIN_TYPE.POS: 1>
TOP: TIME_DOMAIN_TYPE  # value = <TIME_DOMAIN_TYPE.TOP: 1>
UNCUT: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.UNCUT: 3>
VOL: ngsolve.comp.VorB  # value = <VorB.VOL: 0>
__version__: str = '2.1.2505.dev19'
_dCut_raw: CutDifferentialSymbol  # value = <xfem.xfem.CutDifferentialSymbol object>
_dFacetPatch_raw: FacetPatchDifferentialSymbol  # value = <xfem.xfem.FacetPatchDifferentialSymbol object>
all_combined_domain_types: list  # value = [<COMBINED_DOMAIN_TYPE.NO: 0>, <COMBINED_DOMAIN_TYPE.CDOM_NEG: 1>, <COMBINED_DOMAIN_TYPE.CDOM_POS: 2>, <COMBINED_DOMAIN_TYPE.UNCUT: 3>, <COMBINED_DOMAIN_TYPE.CDOM_IF: 4>, <COMBINED_DOMAIN_TYPE.HASNEG: 5>, <COMBINED_DOMAIN_TYPE.HASPOS: 6>, <COMBINED_DOMAIN_TYPE.ANY: 7>]
all_domain_types: list  # value = [<DOMAIN_TYPE.NEG: 0>, <DOMAIN_TYPE.POS: 1>, <DOMAIN_TYPE.IF: 2>]
clipping_variables: list = ['nx', 'ny', 'nz', 'dist', 'dist2', 'enable', 'onlydomain', 'notdomain']
dummy_scene: DummyScene  # value = <xfem.DummyScene object>
dx: ngsolve.comp.DifferentialSymbol  # value = <ngsolve.comp.DifferentialSymbol object>
ngsxfemglobals: GlobalNgsxfemVariables  # value = <xfem.xfem.GlobalNgsxfemVariables object>
tref: TimeVariableCoefficientFunction  # value = <xfem.xfem.TimeVariableCoefficientFunction object>
viewoptions: ngsolve.internal.TclVariables  # value = <ngsolve.internal.TclVariables object>
viewoptions_variables: list = ['specpointvlen', 'colormeshsize', 'whitebackground', 'drawcoordinatecross', 'drawcolorbar', 'drawnetgenlogo', 'stereo', 'shrink', 'drawfilledtrigs', 'drawedges', 'drawbadels', 'centerpoint', 'drawelement', 'drawoutline', 'drawtets', 'drawtetsdomain', 'drawprisms', 'drawpyramids', 'drawhexes', 'drawidentified', 'drawpointnumbers', 'drawedgenumbers', 'drawfacenumbers', 'drawelementnumbers', 'drawdomainsurf', 'drawededges', 'drawedpoints', 'drawedpointnrs', 'drawedtangents', 'drawededgenrs', 'drawmetispartition', 'drawcurveproj', 'drawcurveprojedge', 'usecentercoords', 'centerx', 'centery', 'centerz', 'drawspecpoint', 'specpointx', 'specpointy', 'specpointz']
visoptions: ngsolve.internal.TclVariables  # value = <ngsolve.internal.TclVariables object>
visoptions_variables: list = ['usetexture', 'invcolor', 'imaginary', 'lineartexture', 'numtexturecols', 'showclipsolution', 'showsurfacesolution', 'drawfieldlines', 'drawpointcurves', 'numfieldlines', 'fieldlinesrandomstart', 'fieldlinesstartarea', 'fieldlinesstartareap1x', 'fieldlinesstartareap1y', 'fieldlinesstartareap1z', 'fieldlinesstartareap2x', 'fieldlinesstartareap2y', 'fieldlinesstartareap2z', 'fieldlinesstartface', 'fieldlinesfilename', 'fieldlinestolerance', 'fieldlinesrktype', 'fieldlineslength', 'fieldlinesmaxpoints', 'fieldlinesthickness', 'fieldlinesvecfunction', 'fieldlinesphase', 'fieldlinesonlyonephase', 'lineplotfile', 'lineplotsource', 'lineplotusingx', 'lineplotusingy', 'lineplotautoscale', 'lineplotxmin', 'lineplotxmax', 'lineplotymin', 'lineplotymax', 'lineplotcurrentnum', 'lineplotinfos', 'lineplotselected', 'lineplotselector', 'lineplotcolor', 'lineplotsizex', 'lineplotsizey', 'lineplotselectedeval', 'lineplotdatadescr', 'lineplotxcoordselector', 'lineplotycoordselector', 'evaluatefilenames', 'evaluatefiledescriptions', 'clipsolution', 'scalfunction', 'vecfunction', 'evaluate', 'gridsize', 'xoffset', 'yoffset', 'autoscale', 'redrawperiodic', 'logscale', 'mminval', 'mmaxval', 'isolines', 'isosurf', 'subdivisions', 'numiso', 'autoredraw', 'autoredrawtime', 'simulationtime', 'multidimcomponent', 'deformation', 'scaledeform1', 'scaledeform2']
SymbolicBFI = SymbolicBFIWrapper
SymbolicLFI = SymbolicLFIWrapper
