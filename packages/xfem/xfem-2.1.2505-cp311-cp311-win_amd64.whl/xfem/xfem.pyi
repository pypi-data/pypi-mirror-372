from __future__ import annotations
import ngsolve.comp
import ngsolve.fem
import ngsolve.la
import pyngcore.pyngcore
import typing
__all__: list[str] = ['ANY', 'BOTTOM', 'BitArrayCF', 'CDOM_IF', 'CDOM_NEG', 'CDOM_POS', 'COMBINED_DOMAIN_TYPE', 'CSpaceTimeFESpace', 'CXFESpace', 'CompoundBitArray', 'CompoundProlongation', 'CreateTimeRestrictedGF', 'CutDifferentialSymbol', 'CutInfo', 'DOMAIN_TYPE', 'ElementAggregation', 'ExtensionEmbedding', 'FALLBACK', 'FIRST', 'FacetPatchDifferentialSymbol', 'GCC3FE', 'GetDofsOfElements', 'GetDofsOfFacets', 'GetElementsWithNeighborFacets', 'GetElementsWithSharedVertex', 'GetFacetsWithNeighborTypes', 'GlobalNgsxfemVariables', 'HASNEG', 'HASPOS', 'IF', 'INTERVAL', 'IntegrateX', 'IntegrationPointExtrema', 'InterpolateToP1', 'MultiLevelsetCutInfo', 'NEG', 'NO', 'OPTIMAL', 'P1Prolongation', 'P2CutProlongation', 'P2Prolongation', 'POS', 'PatchwiseSolve', 'ProjectShift', 'QUAD_DIRECTION_POLICY', 'ReferenceTimeVariable', 'RefineAtLevelSet', 'Restrict', 'RestrictGFInTime', 'RestrictedBilinearFormComplex', 'RestrictedBilinearFormDouble', 'SFESpace', 'ScalarTimeFE', 'SpaceTimeFESpace', 'SpaceTimeInterpolateToP1', 'SpaceTimeVTKOutput', 'SymbolicCutBFI', 'SymbolicCutLFI', 'SymbolicFacetPatchBFI', 'TIME_DOMAIN_TYPE', 'TOP', 'TimeVariableCoefficientFunction', 'UNCUT', 'XFESpace', 'XToNegPos', 'dn', 'fix_tref_coef', 'fix_tref_gf', 'fix_tref_proxy', 'ngsxfemglobals', 'shifted_eval']
class BitArrayCF(ngsolve.fem.CoefficientFunction):
    """
    
    CoefficientFunction that evaluates a BitArray. On elements with an index i where the BitArray
    evaluates to true the CoefficientFunction will evaluate as 1, otherwise as 0.
    
    Similar functionality (also for facets) can be obtained with IndicatorCF.
    """
    def __init__(self, bitarray: pyngcore.pyngcore.BitArray) -> None:
        ...
class COMBINED_DOMAIN_TYPE:
    """
    Members:
    
      NO
    
      CDOM_NEG
    
      CDOM_POS
    
      UNCUT
    
      CDOM_IF
    
      HASNEG
    
      HASPOS
    
      ANY
    """
    ANY: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.ANY: 7>
    CDOM_IF: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.CDOM_IF: 4>
    CDOM_NEG: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.CDOM_NEG: 1>
    CDOM_POS: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.CDOM_POS: 2>
    HASNEG: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.HASNEG: 5>
    HASPOS: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.HASPOS: 6>
    NO: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.NO: 0>
    UNCUT: typing.ClassVar[COMBINED_DOMAIN_TYPE]  # value = <COMBINED_DOMAIN_TYPE.UNCUT: 3>
    __members__: typing.ClassVar[dict[str, COMBINED_DOMAIN_TYPE]]  # value = {'NO': <COMBINED_DOMAIN_TYPE.NO: 0>, 'CDOM_NEG': <COMBINED_DOMAIN_TYPE.CDOM_NEG: 1>, 'CDOM_POS': <COMBINED_DOMAIN_TYPE.CDOM_POS: 2>, 'UNCUT': <COMBINED_DOMAIN_TYPE.UNCUT: 3>, 'CDOM_IF': <COMBINED_DOMAIN_TYPE.CDOM_IF: 4>, 'HASNEG': <COMBINED_DOMAIN_TYPE.HASNEG: 5>, 'HASPOS': <COMBINED_DOMAIN_TYPE.HASPOS: 6>, 'ANY': <COMBINED_DOMAIN_TYPE.ANY: 7>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class CSpaceTimeFESpace(ngsolve.comp.FESpace):
    def IsTimeNodeActive(self, arg0: int) -> bool:
        """
        Return bool whether node is active
        """
    def SetOverrideTime(self, arg0: bool) -> None:
        """
        Set flag to or not to override the time variable
        """
    def SetTime(self, arg0: float) -> None:
        """
        Set the time variable
         Also sets override time
        """
    def TimeFE_nodes(self) -> list:
        """
        Return nodes of time FE
        """
    def k_t(self) -> int:
        """
        Return order of the time FE
        """
    @property
    def spaceFES(self) -> ngsolve.comp.FESpace:
        """
        get space FESpace
        """
class CXFESpace(ngsolve.comp.FESpace):
    """
    
    XFESpace-class [For documentation of the XFESpace-constructor see help(XFESpace)]:
    
    Extended finite element space. Takes a basis FESpace and creates an enrichment space based on cut
    information.  The cut information is provided by a CutInfo object or - if a level set function is
    only provided - a CutInfo object is created. The enrichment doubles the unknowns on all cut elements
    and assigns to them a sign (NEG/POS). One of the differential operators neg(...) or pos(...)
    evaluates like the basis function of the origin space, the other one as zero for every basis
    function. Away from cut elements no basis function is supported.
    """
    def BaseDofOfXDof(self, arg0: int) -> int:
        """
        To an unknown of the extended space, get the corresponding unknown of the base FESpace.
        
        Parameters
        
        i : int
          degree of freedom 
        """
    def GetCutInfo(self) -> CutInfo:
        """
        Get Information of cut geometry
        """
    def GetDomainNrs(self, arg0: int) -> ...:
        """
        Get Array of Domains (Array of NEG/POS) of degrees of freedom of the extended FESpace on one element.
        
        Parameters
        
        elnr : int
          element number
        """
    def GetDomainOfDof(self, arg0: int) -> DOMAIN_TYPE:
        """
        Get Domain (NEG/POS) of a degree of freedom of the extended FESpace.
        
        Parameters
        
        i : int
          degree of freedom 
        """
class CompoundProlongation(ngsolve.comp.Prolongation):
    """
    prolongation for compound spaces
    """
    def AddProlongation(self, p1prol: ngsolve.comp.Prolongation) -> None:
        ...
    def Prolongate(self, finelevel: int, vec: ngsolve.la.BaseVector) -> None:
        ...
    def Restrict(self, finelevel: int, vec: ngsolve.la.BaseVector) -> None:
        ...
    def Update(self, fespace: ngsolve.comp.FESpace) -> None:
        ...
    def __init__(self, compoundFESpace: ngsolve.comp.FESpace) -> None:
        ...
class CutDifferentialSymbol(ngsolve.comp.DifferentialSymbol):
    """
    
    CutDifferentialSymbol that allows to formulate linear, bilinear forms and integrals on
    level set domains in an intuitive form:
    
    Example use case:
    
      dCut = CutDifferentialSymbol(VOL)
      dx = dCut(lset,NEG)
      a = BilinearForm(...)
      a += u * v * dx
    
    Note that the most important options are set in the second line when the basic
    CutDifferentialSymbol is further specified.
    """
    def __call__(self, levelset_domain: dict, definedon: ngsolve.comp.Region | str | None = None, vb: ngsolve.comp.VorB = ..., element_boundary: bool = False, element_vb: ngsolve.comp.VorB = ..., skeleton: bool = False, deformation: ngsolve.comp.GridFunction = None, definedonelements: pyngcore.pyngcore.BitArray = None) -> CutDifferentialSymbol:
        """
        The call of a CutDifferentialSymbol allows to specify what is needed to specify the 
        integration domain. It returns a new CutDifferentialSymbol.
        
        Parameters:
        
        levelset_domain (dict) : specifies the level set domain.
        definedon (Region or Array) : specifies on which part of the mesh (in terms of regions)
          the current form shall be defined.
        vb (VOL/BND/BBND/BBBND) : Where does the integral take place from point of view 
          of the mesh.
        element_boundary (bool) : Does the integral take place on the boundary of an element-
        element_vb (VOL/BND/BBND/BBBND) : Where does the integral take place from point of view
          of an element.
        skeleton (bool) : is it an integral on facets (the skeleton)?
        deformation (GridFunction) : which mesh deformation shall be applied (default : None)
        definedonelements (BitArray) : Set of elements or facets where the integral shall be
          defined.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructor of CutDifferentialSymbol.
        
          Argument: none
        """
    @typing.overload
    def __init__(self, arg0: ngsolve.comp.VorB) -> None:
        """
        Constructor of CutDifferentialSymbol.
        
          Argument: VOL_or_BND (boundary or volume form?).
        """
    def __rmul__(self, arg0: float) -> CutDifferentialSymbol:
        ...
    def order(self, order: int) -> CutDifferentialSymbol:
        ...
    @property
    def vb(self) -> ngsolve.comp.VorB:
        """
        Volume of boundary?
        """
    @vb.setter
    def vb(self, arg1: ngsolve.comp.VorB) -> ngsolve.comp.VorB:
        ...
class CutInfo:
    """
    
    A CutInfo stores and organizes cut informations in the mesh with respect to a level set function. 
    Elements (BND / VOL) and facets can be either cut elements or in the positive (POS) or negative
    (NEG) part of the domain. A CutInfo provides information about the cut configuration in terms of
    BitArrays and Vectors of Ratios. (Internally also domain_types for different mesh nodes are stored.)
    """
    def GetCutRatios(self, VOL_or_BND: ngsolve.comp.VorB = ...) -> ngsolve.la.BaseVector:
        """
        Returns Vector of the ratios between the measure of the NEG domain on a (boundary) element and the
        full (boundary) element
        """
    def GetElementsOfType(self, domain_type: typing.Any = ..., VOL_or_BND: ngsolve.comp.VorB = ...) -> pyngcore.pyngcore.BitArray:
        """
        Returns BitArray that is true for every element that has the 
        corresponding combined domain type 
        (NO/NEG/POS/UNCUT/IF/HASNEG/HASPOS/ANY)
        """
    def GetElementsWithThresholdContribution(self, domain_type: typing.Any = ..., threshold: float = 1.0, VOL_or_BND: ngsolve.comp.VorB = ...) -> pyngcore.pyngcore.BitArray:
        """
        Returns BitArray marking the elements where the cut ratio is greater or equal to the given 
        threshold.
        
        Parameters
        
        domain_type : ENUM
            Check POS or NEG elements.
        
        threshold : float
            Mark elements with cut ratio (volume of domain_type / volume background mesh) greater or equal to threshold.
        
        VOL_or_BND : ngsolve.comp.VorB
            input VOL, BND, ..
        """
    def GetFacetsOfType(self, domain_type: typing.Any = ...) -> pyngcore.pyngcore.BitArray:
        """
        Returns BitArray that is true for every facet that has the 
        corresponding combined domain type 
        (NO/NEG/POS/UNCUT/IF/HASNEG/HASPOS/ANY)
        """
    def Mesh(self) -> ngsolve.comp.Mesh:
        """
        Returns mesh of CutInfo
        """
    def Update(self, levelset: ngsolve.fem.CoefficientFunction, subdivlvl: int = 0, time_order: int = -1, heapsize: int = 1000000) -> None:
        """
        Updates a CutInfo based on a level set function.
        
        Parameters
        
        levelset : ngsolve.CoefficientFunction
          level set function w.r.t. which the CutInfo is generated
        
        subdivlvl : int
          subdivision for numerical integration
        
        time_order : int
          order in time that is used in the integration in time to check for cuts and the ratios. This is
          only relevant for space-time discretizations.
        """
    def __init__(self, mesh: ngsolve.comp.Mesh, levelset: typing.Any = None, subdivlvl: int = 0, time_order: int = -1, heapsize: int = 1000000) -> None:
        """
        Creates a CutInfo based on a level set function and a mesh.
        
        Parameters
        
        mesh : Mesh
        
        levelset : ngsolve.CoefficientFunction / None
          level set funciton w.r.t. which the CutInfo is created
        
        time_order : int
          order in time that is used in the integration in time to check for cuts and the ratios. This is
          only relevant for space-time discretizations.
        """
class DOMAIN_TYPE:
    """
    Members:
    
      POS
    
      NEG
    
      IF
    """
    IF: typing.ClassVar[DOMAIN_TYPE]  # value = <DOMAIN_TYPE.IF: 2>
    NEG: typing.ClassVar[DOMAIN_TYPE]  # value = <DOMAIN_TYPE.NEG: 0>
    POS: typing.ClassVar[DOMAIN_TYPE]  # value = <DOMAIN_TYPE.POS: 1>
    __members__: typing.ClassVar[dict[str, DOMAIN_TYPE]]  # value = {'POS': <DOMAIN_TYPE.POS: 1>, 'NEG': <DOMAIN_TYPE.NEG: 0>, 'IF': <DOMAIN_TYPE.IF: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ElementAggregation:
    """
    
    ElementAggregation does the following:  
      It collects patches of elements that allow to stabilize bad cut elements by at least one
      good element (the root element).
    )
    """
    def Update(self, root_elements: pyngcore.pyngcore.BitArray, bad_elements: pyngcore.pyngcore.BitArray, heapsize: int = 1000000) -> None:
        """
        Updates a Element Aggregation based ...
        """
    def __init__(self, mesh: ngsolve.comp.Mesh, root_elements: typing.Any = None, bad_elements: typing.Any = None, heapsize: int = 1000000) -> None:
        """
        Creates a ElementAggregation based on a mesh, a list of root and a list of bad elements.
        """
    @property
    def element_to_patch(self) -> list:
        """
        vector mapping elements to (non-trivial) patches
        """
    @property
    def els_in_nontrivial_patch(self) -> pyngcore.pyngcore.BitArray:
        """
        BitArray that is true for every element that is part of a (non-trivial) patch
        """
    @property
    def els_in_trivial_patch(self) -> pyngcore.pyngcore.BitArray:
        """
        BitArray that is true for every element that is not part of a (non-trivial) patch
        """
    @property
    def facet_to_patch(self) -> list:
        """
        vector mapping facets to (non-trivial) patches
        """
    @property
    def patch_interior_facets(self) -> pyngcore.pyngcore.BitArray:
        """
        BitArray that is true for every facet that is *inside* an aggregation cluster
        """
class FacetPatchDifferentialSymbol(ngsolve.comp.DifferentialSymbol):
    """
    
    FacetPatchDifferentialSymbol that allows to formulate integrals on facet patches.
    Example use case:
    
      dFacetPatch = FacetPatchDifferentialSymbol(VOL)
      dw = dFacetPatch(definedonelements = ...)
      a = BilinearForm(...)
      a += (u-u.Other()) * (v-v.Other()) * dw
    
    """
    def __call__(self, definedon: ngsolve.comp.Region | str | None = None, element_boundary: bool = False, element_vb: ngsolve.comp.VorB = ..., skeleton: bool = False, deformation: ngsolve.comp.GridFunction = None, definedonelements: pyngcore.pyngcore.BitArray = None, time_order: int = -1, tref: float | None = None) -> FacetPatchDifferentialSymbol:
        """
        The call of a FacetPatchDifferentialSymbol allows to specify what is needed to specify the 
        integration domain of an integral that runs over the volume patch of each facet. 
        It returns a new CutDifferentialSymbol.
        
        Parameters:
        
        definedon (Region or Array) : specifies on which part of the mesh (in terms of regions)
          the current form shall be defined.
        element_boundary (bool) : Does the integral take place on the boundary of an element-
        element_vb (VOL/BND/BBND/BBBND) : Where does the integral take place from point of view
          of an element.
        skeleton (bool) : is it an integral on facets (the skeleton)?
        deformation (GridFunction) : which mesh deformation shall be applied (default : None)
        definedonelements (BitArray) : Set of elements or facets where the integral shall be
          defined.
        time_order (int) : integration order in time (for space-time) (default : -1).
        tref (float) : turn space integral into space-time integral with fixed time tref.
        """
    def __init__(self, arg0: ngsolve.comp.VorB) -> None:
        """
        Constructor of FacetPatchDifferentialSymbol.
        
          Argument: VOL_or_BND (boundary or volume form?).
        """
    def __rmul__(self, arg0: float) -> FacetPatchDifferentialSymbol:
        ...
class GCC3FE(ScalarTimeFE):
    def __init__(self, skip_first_nodes: bool = False, only_first_nodes: bool = False) -> None:
        """
        docu missing
        """
class GlobalNgsxfemVariables:
    """
    
    The class GlobalNgsxfemVariables provides Python-access to several internal
    parameters and options used by different subprocedures of ngsxfem. For "mainstream"
    application cases, it should not be required to change parameters here. Most cases
    where this class is practically relevant will be debugging or special applications,
    like investigations in a regime of total error below ~1e-8.
    
    Properties:
    
    eps_spacetime_lset_perturbation : double
        When handling cut topologies, it is sometimes cumbersome to include the case
        of a lset value of exactly 0. Hence, the value will be set to eps_spacetime_lset_perturbation
        in the routine for generating space-time quadrature rules in case its absolute value is smaller.
        Default: 1e-14
    
    eps_spacetime_cutrule_bisection : double
        For high temporal orders, the space-time quadrature rule will apply a bisection
        method to find those time points with topology changes. This parameters controls
        how small 2 times the value must be in order to be counted as a root.
        Default: 1e-15
    
    eps_P1_perturbation : double
        Similar to eps_spacetime_lset_perturbation, but for the P1 interpolation routine.
        Default: 1e-14
    
    eps_spacetime_fes_node : double
        When a Gridfunction is restricted, the given time point is compared to the nodes
        of the finite element, such that those node values can be extracted directly in
        a matching case. This parameters controlls how far a deviation will still be counted
        as coincidence.
        Default: 1e-9
    
    
     
    """
    do_naive_timeint: bool
    eps_P1_perturbation: float
    eps_facetpatch_ips: float
    eps_shifted_eval: float
    eps_spacetime_cutrule_bisection: float
    eps_spacetime_fes_node: float
    eps_spacetime_lset_perturbation: float
    fixed_point_maxiter_shifted_eval: int
    max_dist_newton: float
    naive_timeint_order: int
    naive_timeint_subdivs: int
    newton_maxiter: int
    non_conv_warn_msg_lvl: int
    simd_eval: bool
    def MultiplyAllEps(self, arg0: float) -> None:
        ...
    def Output(self) -> None:
        ...
    def SetDefaults(self) -> None:
        ...
    def SwitchSIMD(self, arg0: bool) -> None:
        ...
class MultiLevelsetCutInfo:
    """
    
    A minimal version of a CutInfo that allows for several levelsets and a list of tuples of domain_types.
    """
    def GetElementsOfType(self, domain_type: typing.Any, VOL_or_BND: ngsolve.comp.VorB = ..., heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
        """
        Returns BitArray that is true for every element that has the 
        corresponding domain type. This BitArray remains attached to the mlci class
        instance and is updated on mlci.Update(lsets).
        
        Parameters
        
        domain_type : {tuple(ENUM), list(tuple(ENUM)), DomainTypeArray}
          Description of the domain.
        
        heapsize : int = 1000000
          heapsize of local computations.
        """
    def GetElementsWithContribution(self, domain_type: typing.Any, VOL_or_BND: ngsolve.comp.VorB = ..., heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
        """
        Returns BitArray that is true for every element that has the 
        a contribution to the corresponding level set domain. This BitArray 
        remains attached to the mlci class instance and is updated on 
        mlci.Update(lsets).
        
        Parameters
        
        domain_type : {tuple(ENUM), list(tuple(ENUM)), DomainTypeArray}
          Description of the domain.
        
        heapsize : int = 1000000
          heapsize of local computations.
        """
    def Mesh(self) -> ngsolve.comp.Mesh:
        """
        Returns mesh of CutInfo.
        """
    def Update(self, levelsets: typing.Any, heapsize: int = 1000000) -> None:
        """
        Updates the tuple of levelsets behind the MultiLevelsetCutInfo and 
        recomputes any element marker arrays which have been created with this
        instance.
        
        Parameters
        
        levelsets : tuple(ngsolve.GridFunction)
          tuple of GridFunctions w.r.t. which elements are marked.
        
        heapsize : int = 1000000
          heapsize of local computations
        """
    def __init__(self, mesh: ngsolve.comp.Mesh, levelset: typing.Any) -> None:
        """
        Creates a MultiLevelsetCutInfo based on a mesh and a tuple of levelsets.
        
        Parameters
        
        mesh : 
          mesh
        
        levelsets : tuple(ngsolve.GridFunction)
          tuple of GridFunctions w.r.t. which elements are marked 
        """
class P1Prolongation(ngsolve.comp.Prolongation):
    """
    
    Prolongation for P1-type spaces (with possibly inactive dofs) --- 
    As is asks the fespace for dofs to vertices at several occasions the 
    current implementation is not very fast and should be primarily used
    for prototype and testing...
    """
    def Update(self, space: ngsolve.comp.FESpace) -> None:
        ...
    def __init__(self, mesh: ngsolve.comp.Mesh) -> None:
        ...
class P2CutProlongation(ngsolve.comp.Prolongation):
    """
    
    Prolongation for P2 spaces (with possibly inactive dofs) --- 
    As is asks the fespace for dofs to vertices at several occasions the 
    current implementation is not very fast and should be primarily used
    for prototype and testing...
    """
    def Update(self, space: ngsolve.comp.FESpace) -> None:
        ...
    def __init__(self, mesh: ngsolve.comp.Mesh) -> None:
        ...
class P2Prolongation(ngsolve.comp.Prolongation):
    """
    
    Prolongation for P2 spaces (with possibly inactive dofs) --- 
    As is asks the fespace for dofs to vertices at several occasions the 
    current implementation is not very fast and should be primarily used
    for prototype and testing...
    """
    def Update(self, space: ngsolve.comp.FESpace) -> None:
        ...
    def __init__(self, mesh: ngsolve.comp.Mesh) -> None:
        ...
class QUAD_DIRECTION_POLICY:
    """
    Members:
    
      FIRST
    
      OPTIMAL
    
      FALLBACK
    """
    FALLBACK: typing.ClassVar[QUAD_DIRECTION_POLICY]  # value = <QUAD_DIRECTION_POLICY.FALLBACK: 2>
    FIRST: typing.ClassVar[QUAD_DIRECTION_POLICY]  # value = <QUAD_DIRECTION_POLICY.FIRST: 0>
    OPTIMAL: typing.ClassVar[QUAD_DIRECTION_POLICY]  # value = <QUAD_DIRECTION_POLICY.OPTIMAL: 1>
    __members__: typing.ClassVar[dict[str, QUAD_DIRECTION_POLICY]]  # value = {'FIRST': <QUAD_DIRECTION_POLICY.FIRST: 0>, 'OPTIMAL': <QUAD_DIRECTION_POLICY.OPTIMAL: 1>, 'FALLBACK': <QUAD_DIRECTION_POLICY.FALLBACK: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Restrict(ngsolve.comp.Compress):
    """
    Wrapper Finite Element Spaces.
    The restricted fespace is a wrapper around a standard fespace which removes dofs from marked elements.
    
    Parameters:
    
    fespace : ngsolve.comp.FESpace
        finite element space
    
    active_els : BitArray or None
        Only use dofs from these elements
    """
    def GetBaseSpace(self) -> ngsolve.comp.FESpace:
        ...
    def __getstate__(self) -> tuple:
        ...
    def __init__(self, fespace: ngsolve.comp.FESpace, active_elements: typing.Any = None) -> None:
        ...
    def __setstate__(self, arg0: tuple) -> None:
        ...
    @property
    def active_elements(self) -> pyngcore.pyngcore.BitArray:
        """
        active elements
        """
    @active_elements.setter
    def active_elements(self, arg1: pyngcore.pyngcore.BitArray) -> None:
        ...
class RestrictedBilinearFormComplex(ngsolve.comp.BilinearForm):
    """
    BilinearForm restricted on a set of elements and facets.
    """
    @typing.overload
    def __init__(self, space: ngsolve.comp.FESpace, name: str = 'bfa', element_restriction: typing.Any = None, facet_restriction: typing.Any = None, **kwargs) -> None:
        """
        A restricted bilinear form is a bilinear form with a reduced MatrixGraph
        compared to the usual BilinearForm. BitArray(s) define on which elements/facets entries will be
        created.
        
        Use cases:
        
         * ghost penalty type stabilization:
            Facet-stabilization that are introduced only act on a few facets in the mesh. By providing the
            information on the corresponding facets, these additional couplings will only be introduced
            where necessary.
        
         * fictitious domain methods:
            When PDE problems are only solved on a part of a domain while a finite element space is used
            that is still defined on the whole domain, a BitArray can be used to mark the 'active' part of
            the mesh.
        
        Parameters
        
        space (trialspace) : ngsolve.FESpace
          finite element space on which the bilinear form is defined 
          (trial space and (if no test space is defined) test space).
        
        testspace : ngsolve.FESpace
          finite element space on which the bilinear form is defined
          (test space).
        
        name : string
          name of the bilinear form
        
        element_restriction : ngsolve.BitArray
          BitArray defining the 'active mesh' element-wise
        
        facet_restriction : ngsolve.BitArray
          BitArray defining the 'active facets'. This is only relevant if FESpace has DG-terms (dgjumps=True)
        
        kwargs : keyword args 
          additional arguments that are passed to bilinear form (in form of flags)
        """
    @typing.overload
    def __init__(self, trialspace: ngsolve.comp.FESpace, testspace: ngsolve.comp.FESpace, name: str = 'bfa', element_restriction: typing.Any = None, facet_restriction: typing.Any = None, **kwargs) -> None:
        """
        A restricted bilinear form is a bilinear form with a reduced MatrixGraph
        compared to the usual BilinearForm. BitArray(s) define on which elements/facets entries will be
        created.
        
        Use cases:
        
         * ghost penalty type stabilization:
            Facet-stabilization that are introduced only act on a few facets in the mesh. By providing the
            information on the corresponding facets, these additional couplings will only be introduced
            where necessary.
        
         * fictitious domain methods:
            When PDE problems are only solved on a part of a domain while a finite element space is used
            that is still defined on the whole domain, a BitArray can be used to mark the 'active' part of
            the mesh.
        
        Parameters
        
        space (trialspace) : ngsolve.FESpace
          finite element space on which the bilinear form is defined 
          (trial space and (if no test space is defined) test space).
        
        testspace : ngsolve.FESpace
          finite element space on which the bilinear form is defined
          (test space).
        
        name : string
          name of the bilinear form
        
        element_restriction : ngsolve.BitArray
          BitArray defining the 'active mesh' element-wise
        
        facet_restriction : ngsolve.BitArray
          BitArray defining the 'active facets'. This is only relevant if FESpace has DG-terms (dgjumps=True)
        
        kwargs : keyword args 
          additional arguments that are passed to bilinear form (in form of flags)
        """
    @property
    def element_restriction(self) -> pyngcore.pyngcore.BitArray:
        """
        element restriction
        """
    @element_restriction.setter
    def element_restriction(self, arg1: pyngcore.pyngcore.BitArray) -> None:
        ...
    @property
    def facet_restriction(self) -> pyngcore.pyngcore.BitArray:
        """
        facet restriction
        """
    @facet_restriction.setter
    def facet_restriction(self, arg1: pyngcore.pyngcore.BitArray) -> None:
        ...
class RestrictedBilinearFormDouble(ngsolve.comp.BilinearForm):
    """
    BilinearForm restricted on a set of elements and facets.
    """
    @typing.overload
    def __init__(self, space: ngsolve.comp.FESpace, name: str = 'bfa', element_restriction: typing.Any = None, facet_restriction: typing.Any = None, **kwargs) -> None:
        """
        A restricted bilinear form is a bilinear form with a reduced MatrixGraph
        compared to the usual BilinearForm. BitArray(s) define on which elements/facets entries will be
        created.
        
        Use cases:
        
         * ghost penalty type stabilization:
            Facet-stabilization that are introduced only act on a few facets in the mesh. By providing the
            information on the corresponding facets, these additional couplings will only be introduced
            where necessary.
        
         * fictitious domain methods:
            When PDE problems are only solved on a part of a domain while a finite element space is used
            that is still defined on the whole domain, a BitArray can be used to mark the 'active' part of
            the mesh.
        
        Parameters
        
        space (trialspace) : ngsolve.FESpace
          finite element space on which the bilinear form is defined 
          (trial space and (if no test space is defined) test space).
        
        testspace : ngsolve.FESpace
          finite element space on which the bilinear form is defined
          (test space).
        
        name : string
          name of the bilinear form
        
        element_restriction : ngsolve.BitArray
          BitArray defining the 'active mesh' element-wise
        
        facet_restriction : ngsolve.BitArray
          BitArray defining the 'active facets'. This is only relevant if FESpace has DG-terms (dgjumps=True)
        
        kwargs : keyword args 
          additional arguments that are passed to bilinear form (in form of flags)
        """
    @typing.overload
    def __init__(self, trialspace: ngsolve.comp.FESpace, testspace: ngsolve.comp.FESpace, name: str = 'bfa', element_restriction: typing.Any = None, facet_restriction: typing.Any = None, **kwargs) -> None:
        """
        A restricted bilinear form is a bilinear form with a reduced MatrixGraph
        compared to the usual BilinearForm. BitArray(s) define on which elements/facets entries will be
        created.
        
        Use cases:
        
         * ghost penalty type stabilization:
            Facet-stabilization that are introduced only act on a few facets in the mesh. By providing the
            information on the corresponding facets, these additional couplings will only be introduced
            where necessary.
        
         * fictitious domain methods:
            When PDE problems are only solved on a part of a domain while a finite element space is used
            that is still defined on the whole domain, a BitArray can be used to mark the 'active' part of
            the mesh.
        
        Parameters
        
        space (trialspace) : ngsolve.FESpace
          finite element space on which the bilinear form is defined 
          (trial space and (if no test space is defined) test space).
        
        testspace : ngsolve.FESpace
          finite element space on which the bilinear form is defined
          (test space).
        
        name : string
          name of the bilinear form
        
        element_restriction : ngsolve.BitArray
          BitArray defining the 'active mesh' element-wise
        
        facet_restriction : ngsolve.BitArray
          BitArray defining the 'active facets'. This is only relevant if FESpace has DG-terms (dgjumps=True)
        
        kwargs : keyword args 
          additional arguments that are passed to bilinear form (in form of flags)
        """
    @property
    def element_restriction(self) -> pyngcore.pyngcore.BitArray:
        """
        element restriction
        """
    @element_restriction.setter
    def element_restriction(self, arg1: pyngcore.pyngcore.BitArray) -> None:
        ...
    @property
    def facet_restriction(self) -> pyngcore.pyngcore.BitArray:
        """
        facet restriction
        """
    @facet_restriction.setter
    def facet_restriction(self, arg1: pyngcore.pyngcore.BitArray) -> None:
        ...
class ScalarTimeFE(ngsolve.fem.FiniteElement):
    def __init__(self, order: int = 0, skip_first_nodes: bool = False, only_first_nodes: bool = False, skip_first_node: bool = False, only_first_node: bool = False) -> None:
        """
        Creates a nodal Finite element in time on the interval [0,1].
        Internally, Gauss-Lobatto integration points are exploited for that.
        
        Parameters
        
        order : int
        The polynomial order of the discretisation. That controlls the number of
        points in the time interval. See Gauss-Lobatto points for further details.
        Orders up to 5 are given by explicit closed formulas, beyond that an
        iterative construction is applied.
        
        skip_first_nodes : bool
        This will create the time finite element without the first node at t=0.
        That feature comes in handy for several CG like implementations in time.
        Also see only_first_node.
        
        only_first_nodes : bool
        This will create the time finite element with only the first node at t=0.
        That feature comes in handy for several CG like implementations in time.
        Also see skip_first_node.
        """
    def __mul__(self, arg0: ngsolve.comp.FESpace) -> CSpaceTimeFESpace:
        ...
class SpaceTimeVTKOutput:
    @typing.overload
    def Do(self, vb: ngsolve.comp.VorB = ..., t_start: float = 0, t_end: float = 1) -> None:
        ...
    @typing.overload
    def Do(self, vb: ngsolve.comp.VorB = ..., t_start: float = 0, t_end: float = 1, drawelems: pyngcore.pyngcore.BitArray) -> None:
        ...
    def __init__(self, ma: ngsolve.comp.Mesh, coefs: list = [], names: list = [], filename: str = 'vtkout', subdivision_x: int = 0, subdivision_t: int = 0, only_element: int = -1) -> None:
        ...
class TIME_DOMAIN_TYPE:
    """
    Members:
    
      BOTTOM
    
      TOP
    
      INTERVAL
    """
    BOTTOM: typing.ClassVar[TIME_DOMAIN_TYPE]  # value = <TIME_DOMAIN_TYPE.BOTTOM: 0>
    INTERVAL: typing.ClassVar[TIME_DOMAIN_TYPE]  # value = <TIME_DOMAIN_TYPE.INTERVAL: 2>
    TOP: typing.ClassVar[TIME_DOMAIN_TYPE]  # value = <TIME_DOMAIN_TYPE.TOP: 1>
    __members__: typing.ClassVar[dict[str, TIME_DOMAIN_TYPE]]  # value = {'BOTTOM': <TIME_DOMAIN_TYPE.BOTTOM: 0>, 'TOP': <TIME_DOMAIN_TYPE.TOP: 1>, 'INTERVAL': <TIME_DOMAIN_TYPE.INTERVAL: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TimeVariableCoefficientFunction(ngsolve.fem.CoefficientFunction):
    @staticmethod
    def __init__() -> TimeVariableCoefficientFunction:
        ...
    def FixTime(self, arg0: float) -> None:
        ...
    def IsFixed(self) -> bool:
        ...
    def UnfixTime(self) -> None:
        ...
def CompoundBitArray(balist: list) -> pyngcore.pyngcore.BitArray:
    """
    Takes a list of BitArrays and merges them to one larger BitArray. Can be useful for
    CompoundFESpaces.
    """
def CreateTimeRestrictedGF(gf: ngsolve.comp.GridFunction, reference_time: float = 0.0) -> ngsolve.comp.GridFunction:
    """
    Create spatial-only Gridfunction corresponding to a fixed time.
    """
def ExtensionEmbedding(elagg: ElementAggregation, fes: ngsolve.comp.FESpace, bf: ngsolve.comp.SumOfIntegrals, heapsize: int = 1000000) -> ngsolve.la.SparseMatrixdouble:
    """
    Computes the embedding matrix for an extension minimizing a described energy on 
    patched (followed by averaging if some dofs are shared by multiple patches)
    
    Parameters:
    
    elagg : ElementAggregation
      ElementAggregation instace defining the patches which are aggregated into a single element
    
    fes : ngsolve.FESpace
      The finite element space which is aggregated. 
    
    bf : ngsolve.SumOfIntegrals
      The bilinear form describing the energy to be minized
    """
def GetDofsOfElements(space: ngsolve.comp.FESpace, a: pyngcore.pyngcore.BitArray, heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
    """
    Given a BitArray marking some elements in a
    mesh extract all unknowns that are supported
    on these elements as a BitArray.
    
    Parameters:
    
    space : ngsolve.FESpace
      finite element space from which the 
      corresponding dofs should be extracted
    
    a : ngsolve.BitArray
      BitArray for marked elements
    
    heapsize : int
      heapsize of local computations.
    """
def GetDofsOfFacets(space: ngsolve.comp.FESpace, a: pyngcore.pyngcore.BitArray, heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
    """
    Given a BitArray marking some facets in a
    mesh extract all unknowns that are associated
    to these facets as a BitArray.
    
    Parameters:
    
    space : ngsolve.FESpace
      finite element space from which the 
      corresponding dofs should be extracted
    
    a : ngsolve.BitArray
      BitArray for marked Facets
    
    heapsize : int
      heapsize of local computations.
    """
def GetElementsWithNeighborFacets(mesh: ngsolve.comp.Mesh, a: pyngcore.pyngcore.BitArray, heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
    """
    Given a BitArray marking some facets extract
    a BitArray of elements that are neighboring
    these facets
    
    Parameters:
    
    mesh : 
      mesh
    
    a : ngsolve.BitArray
      BitArray for marked facets
    
    heapsize : int
      heapsize of local computations.
    """
def GetElementsWithSharedVertex(mesh: ngsolve.comp.Mesh, a: pyngcore.pyngcore.BitArray, heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
    ...
def GetFacetsWithNeighborTypes(mesh: ngsolve.comp.Mesh, a: pyngcore.pyngcore.BitArray, bnd_val_a: bool = True, bnd_val_b: bool = True, use_and: bool = True, b: typing.Any = None, heapsize: int = 1000000) -> pyngcore.pyngcore.BitArray:
    """
    Given a mesh and two BitArrays (if only one is provided these are set to be equal) facets will be
    marked (in terms of BitArrays) depending on the BitArray-values on the neighboring elements. The
    BitArrays are complemented with flags for potential boundary values for the BitArrays. The decision
    on every facet is now based on the values a and b (left and right) where a or b can also be obtained
    from the BitArray boundary values.
    The result is:
      result =    (a(left) and b(right)) 
               or (b(left) and a(right)) 
    or 
      result =    (a(left) or b(right)) 
               or (b(left) or a(right)) 
    
    Parameters:
    
    mesh : 
      mesh
    
    a : ngsolve.BitArray
      first BitArray 
    
    b : ngsolve.BitArray / None
      second BitArray. If None, b=a
    
    bnd_val_a : boolean
      BitArray-replacement for a if a(left) or a(right) is not valid (at the boundary)
    
    bnd_val_a : boolean
      BitArray-replacement for b if b(left) or b(right) is not valid (at the boundary)
    
    use_and : boolean
      use 'and'-relation to evaluate the result. Otherwise use 'or'-relation 
    
    heapsize : int
      heapsize of local computations.
    """
def IntegrateX(levelset_domain: dict, mesh: ngsolve.comp.Mesh, cf: ngsolve.fem.CoefficientFunction = ..., deformation: typing.Any = None, ip_container: typing.Any = None, element_wise: bool = False, heapsize: int = 1000000) -> typing.Any:
    """
    Integrate on a level set domains. The accuracy of the integration is 'order' w.r.t. a (multi-)linear
    approximation of the level set function. At first, this implies that the accuracy will, in general,
    only be second order. However, if the isoparametric approach is used (cf. lsetcurving functionality)
    this will be improved.
    
    Parameters
    
    levelset_domain : dictionary which provides levelsets, domain_types and integration specifica:
      important keys are "levelset", "domain_type", "order", the remainder are additional:
    
        "levelset" : ngsolve.CoefficientFunction or a list thereof
          CoefficientFunction that describes the geometry. In the best case lset is a GridFunction of an
          FESpace with scalar continuous piecewise (multi-) linear basis functions.
    
    
        "order" : int
          integration order.
    
        "domain_type" : {NEG,POS,IF} (ENUM) or a list (of lists) thereof
          Integration on the domain where either:
          * the level set function is negative (NEG)
          * the level set function is positive (POS)
          * the level set function is zero     (IF )
    
        "subdivlvl" : int
          On simplex meshes a subtriangulation is created on which the level set function lset is
          interpolated piecewise linearly. Based on this approximation, the integration rule is
          constructed. Note: this argument only works on simplices without space-time and without 
          multiple levelsets.
    
        "time_order" : int
          integration order in time for space-time integration
    
        "quad_dir_policy" : int
          policy for the selection of the order of integration directions
    
    mesh : 
      Mesh to integrate on (on some part) 
    
    cf : ngsolve.CoefficientFunction
      the integrand
    
    deformation : gridfunction (or None)
      deformation of the mesh
    
    ip_container : list (or None)
      a list to store integration points (for debugging or visualization purposes)
    
    element_wise : bool
      result will return the integral w.r.t. each element individually.
    
    heapsize : int
      heapsize for local computations.
    """
def IntegrationPointExtrema(levelset_domain: dict, mesh: ngsolve.comp.Mesh, cf: ngsolve.fem.CoefficientFunction = ..., heapsize: int = 1000000) -> tuple:
    """
    Determine minimum and maximum on integration points on a level set domain. The sampling uses the same
    integration rule as in Integrate and is determined by 'order' w.r.t. a (multi-)linear
    approximation of the level set function. At first, this implies that the accuracy will, in general,
    only be second order. However, if the isoparametric approach is used (cf. lsetcurving functionality)
    this will be improved.
    
    Parameters
    
    levelset_domain : dictionary which provides levelsets, domain_types and integration specifica:
      important keys are "levelset", "domain_type", "order", the remainder are additional:
    
        "levelset" : ngsolve.CoefficientFunction or a list thereof
          CoefficientFunction that describes the geometry. In the best case lset is a GridFunction of an
          FESpace with scalar continuous piecewise (multi-) linear basis functions.
    
    
        "order" : int
          integration order.
    
        "domain_type" : {NEG,POS,IF} (ENUM) or a list (of lists) thereof
          Integration on the domain where either:
          * the level set function is negative (NEG)
          * the level set function is positive (POS)
          * the level set function is zero     (IF )
    
        "subdivlvl" : int
          On simplex meshes a subtriangulation is created on which the level set function lset is
          interpolated piecewise linearly. Based on this approximation, the integration rule is
          constructed. Note: this argument only works on simplices without space-time and without 
          multiple levelsets.
    
        "time_order" : int
          integration order in time for space-time integration
    
        "quad_dir_policy" : int
          policy for the selection of the order of integration directions
    
    mesh : 
      Mesh to integrate on (on some part) 
    
    cf : ngsolve.CoefficientFunction
      the integrand
    
    heapsize : int
      heapsize for local computations.
    """
@typing.overload
def InterpolateToP1(gf_ho: ngsolve.comp.GridFunction = 0, gf_p1: ngsolve.comp.GridFunction = 0, eps_perturbation: float = 1e-14, heapsize: int = 1000000) -> None:
    """
    Takes the vertex values of a GridFunction (also possible with a CoefficentFunction) and puts them
    into a piecewise (multi-) linear function.
    
    Parameters
    
    gf_ho : ngsolve.GridFunction
      Function to interpolate
    
    gf_p1 : ngsolve.GridFunction
      Function to interpolate to (should be P1)
    
    eps_perturbation : float
      If the absolute value if the function is smaller than eps_perturbation, it will be set to
      eps_perturbation. Thereby, exact and close-to zeros at vertices are avoided (Useful to reduce cut
      configurations for level set based methods).
    
    heapsize : int
      heapsize of local computations.
    """
@typing.overload
def InterpolateToP1(coef: ngsolve.fem.CoefficientFunction, gf: ngsolve.comp.GridFunction, eps_perturbation: float = 1e-14, heapsize: int = 1000000) -> None:
    """
    Takes the vertex values of a CoefficentFunction) and puts them into a piecewise (multi-) linear
    function.
    
    Parameters
    
    coef : ngsolve.CoefficientFunction
      Function to interpolate
    
    gf_p1 : ngsolve.GridFunction
      Function to interpolate to (should be P1)
    
    eps_perturbation : float
      If the absolute value if the function is smaller than eps_perturbation, it will be set to
      eps_perturbation. Thereby, exact and close-to zeros at vertices are avoided (Useful to reduce cut
      configurations for level set based methods).
    
    heapsize : int
      heapsize of local computations.
    """
def PatchwiseSolve(elagg: ElementAggregation, fes: ngsolve.comp.FESpace, bf: ngsolve.comp.SumOfIntegrals, lf: ngsolve.comp.SumOfIntegrals, heapsize: int = 1000000) -> ngsolve.la.BaseVector:
    """
    Solve patch-wise problem based on the patches provided by the element aggregation input.
    
    Parameters
    
    elagg: ElementAggregatetion
      The instance defining the patches
    
    fes : FESpace
      The finite element space on which the local solve is performed.
    
    bf : SumOfIntegrals
      Integrators defining the matrix problem.
    
    lf : SumOfIntegrals
      Integrators defining the right-hand side.
    """
def ProjectShift(lset_ho: ngsolve.comp.GridFunction = 0, lset_p1: ngsolve.comp.GridFunction = 0, deform: ngsolve.comp.GridFunction = 0, qn: ngsolve.fem.CoefficientFunction = 0, active_elements: typing.Any = None, blending: ngsolve.fem.CoefficientFunction = 0, lower: float = 0.0, upper: float = 0.0, threshold: float = 1.0, heapsize: int = 1000000) -> None:
    ...
def ReferenceTimeVariable() -> TimeVariableCoefficientFunction:
    """
    This is the time variable. Call tref = ReferenceTimeVariable() to have a symbolic variable
    for the time like x,y,z for space. That can be used e.g. in lset functions for unfitted methods.
    Note that one would typically use tref in [0,1] as one time slab, leading to a call like
    t = told + delta_t * tref, when tref is our ReferenceTimeVariable.
    ngsxfem.__init__ defines tref.
    """
def RefineAtLevelSet(gf: ngsolve.comp.GridFunction = 0, lower: float = 0.0, upper: float = 0.0, heapsize: int = 1000000) -> None:
    """
    Mark mesh for refinement on all elements where the piecewise linear level set function lset_p1 has
    values in the interval [lower,upper] (default [0,0]).
    
    Parameters
    
    gf : ngsolve.GridFunction
      Scalar piecewise (multi-)linear Gridfunction
    
    lower : float
      smallest level set value of interest
    
    upper : float
      largest level set value of interest
    
    heapsize : int
      heapsize of local computations.
    """
def RestrictGFInTime(spacetime_gf: ngsolve.comp.GridFunction, reference_time: float = 0.0, space_gf: ngsolve.comp.GridFunction) -> None:
    """
    Extract Gridfunction corresponding to a fixed time from a space-time GridFunction.
    """
def SFESpace(arg0: ngsolve.comp.Mesh, arg1: ngsolve.fem.CoefficientFunction, arg2: int, arg3: dict) -> ngsolve.comp.FESpace:
    """
    This is a special finite elemetn space which is a 1D polynomial along the zero level of the linearly
    approximated level set function lset and constantly extended in normal directions to this.
    """
def SpaceTimeFESpace(spacefes: ngsolve.comp.FESpace, timefe: ngsolve.fem.FiniteElement, dirichlet: typing.Any = None, heapsize: int = 1000000, **kwargs) -> ...:
    """
    This function creates a SpaceTimeFiniteElementSpace based on a spacial FE space and a time Finite element
    Roughly, this is the tensor product between those two arguments. Further arguments specify several details.
    
    Parameters
    
    spacefes : ngsolve.FESpace
      This is the spacial finite element used for the space-time discretisation.
      Both scalar and vector valued spaces might be used. An example would be
      spacefes = H1(mesh, order=order) for given mesh and order.
    
    timefe : ngsolve.FiniteElement
      This is the time finite element for the space-time discretisation. That is
      essentially a simple finite element on the unit interval. There is a class
      ScalarTimeFE to create something fitting here. For example, one could call
      timefe = ScalarTimeFE(order) to create a time finite element of order order.
    
    dirichlet : list or string
      The boundary of the space domain which should have Dirichlet boundary values.
      Specification policy is the same as with the usual space finite element spaces.
    
    heapsize : int
      Size of the local heap of this class. Increase this if you observe errors which look
      like a heap overflow.
    
    dgjumps : bool  
    """
def SpaceTimeInterpolateToP1(spacetime_cf: ngsolve.fem.CoefficientFunction, time: ngsolve.fem.CoefficientFunction, spacetime_gf: ngsolve.comp.GridFunction) -> None:
    """
    Interpolate nodal in time (possible high order) and nodal in space (P1).
    """
def SymbolicCutBFI(levelset_domain: dict, form: ngsolve.fem.CoefficientFunction, VOL_or_BND: ngsolve.comp.VorB = ..., element_boundary: bool = False, skeleton: bool = False, definedon: typing.Any = None, definedonelements: typing.Any = None, deformation: typing.Any = None) -> ngsolve.fem.BFI:
    """
    see documentation of SymbolicBFI (which is a wrapper)
    """
def SymbolicCutLFI(levelset_domain: dict, form: ngsolve.fem.CoefficientFunction, VOL_or_BND: ngsolve.comp.VorB = ..., element_boundary: bool = False, skeleton: bool = False, definedon: typing.Any = None, definedonelements: typing.Any = None, deformation: typing.Any = None) -> ngsolve.fem.LFI:
    """
    see documentation of SymbolicLFI (which is a wrapper)
    """
def SymbolicFacetPatchBFI(form: ngsolve.fem.CoefficientFunction, force_intorder: int = -1, time_order: int = -1, skeleton: bool = True, definedonelements: typing.Any = None, deformation: typing.Any = None) -> ngsolve.fem.BFI:
    """
    Integrator on facet patches. Two versions are possible:
    * Either (skeleton=False) an integration on the element patch consisting of two neighboring elements is applied, 
    * or (skeleton=True) the integration is applied on the facet. 
    
    Parameters
    
    form : ngsolve.CoefficientFunction
      var form to integrate
    
    force_intorder : int
      (only active in the facet patch case (skeleton=False)) use this integration order in the integration
    
    skeleton : boolean
      decider on facet patch vs facet integration
    
    definedonelements : ngsolve.BitArray/None
      array which decides on which facets the integrator should be applied
    
    time_order : int
      order in time that is used in the space-time integration. time_order=-1 means that no space-time
      rule will be applied. This is only relevant for space-time discretizations.
    """
def XFESpace(basefes: ngsolve.comp.FESpace, cutinfo: typing.Any = None, lset: typing.Any = None, flags: dict = {}, heapsize: int = 1000000) -> ...:
    """
    Constructor for XFESpace [For documentation of XFESpace-class see help(CXFESpace)]:
    
    Extended finite element space. Takes a basis FESpace and creates an enrichment space based on cut
    information. The cut information is provided by a CutInfo object or - if a level set function is
    only provided - a CutInfo object is created. The enrichment doubles the unknowns on all cut elements
    and assigns to them a sign (NEG/POS). One of the differential operators neg(...) or pos(...)
    evaluates like the basis function of the origin space, the other one as zero for every basis
    function. Away from cut elements no basis function is supported.
    
    Parameters
    
    basefes : ngsolve.FESpace
      basic FESpace to be extended
    
    cutinfo : xfem.CutInfo / None
      Information on the cut configurations (cut elements, sign of vertices....)
    
    lset : ngsolve.CoefficientFunction / None
      level set function to construct own CutInfo (if no CutInfo is provided)
    
    flags : Flags
      additional FESpace-flags
    
    heapsize : int
      heapsize of local computations.
    """
def XToNegPos(arg0: ngsolve.comp.GridFunction, arg1: ngsolve.comp.GridFunction) -> None:
    """
    Takes a GridFunction of an extended FESpace, i.e. a compound space of V and VX = XFESpace(V) and
    interpretes it as a function in the CompoundFESpace of V and V. Updates the values of the vector of
    the corresponding second GridFunction.
    """
@typing.overload
def dn(proxy: ngsolve.comp.ProxyFunction, order: int, comp: typing.Any = -1, hdiv: bool = False) -> ngsolve.comp.ProxyFunction:
    """
    Normal derivative of higher order. This is evaluated via numerical differentiation which offers only
    limited accuracy (~ 1e-7).
    
    Parameters
    
    proxy : ngsolve.ProxyFunction
      test / trialfunction to the the normal derivative of
    
    order : int
      order of derivative (in normal direction)
    
    comp : int
      component of proxy if test / trialfunction is a component of a compound or vector test / trialfunction
    
    hdiv : boolean
      assumes scalar FEs if false, otherwise assumes hdiv
    """
@typing.overload
def dn(gf: ngsolve.comp.GridFunction, order: int) -> ngsolve.fem.CoefficientFunction:
    """
    Normal derivative of higher order for a GridFunction. This is evaluated via numerical
    differentiation which offers only limited accuracy (~ 1e-7).
    
    Parameters
    
    gf : ngsolve.GridFunction
      (scalar) GridFunction to the the normal derivative of
    
    order : int
      order of derivative (in normal direction)
    """
def fix_tref_coef(arg0: ngsolve.fem.CoefficientFunction, arg1: typing.Any) -> ngsolve.fem.CoefficientFunction:
    """
    fix_t fixes the evaluated time to a fixed value.
    
    Parameters
    
    self: ngsolve.CoefficientFunction
      CoefficientFunction in which the time should be fixed
      
    time: Parameter or double
      Value the time should become (if Parameter, the value can be adjusted later on)
    """
def fix_tref_gf(gf: ngsolve.comp.GridFunction, time: float = 0.0) -> ngsolve.fem.CoefficientFunction:
    """
    fix_t fixes the time (ReferenceTimeVariable) of a given expression.
    This is the variant for a gridfunction.
    
    Parameters
    
    self: ngsolve.GridFunction
      Gridfunction in which the time should be fixed
      
    time: double
      Value the time should become
    """
def fix_tref_proxy(proxy: ngsolve.comp.ProxyFunction, time: float, comp: typing.Any = -1, use_FixAnyTime: bool = False) -> ngsolve.comp.ProxyFunction:
    ...
def shifted_eval(gf: ngsolve.comp.GridFunction, back: typing.Any = None, forth: typing.Any = None) -> ngsolve.fem.CoefficientFunction:
    """
    Returns a CoefficientFunction that evaluates Gridfunction gf at a shifted location, s.t. the
    original function to gf, gf: x -> f(x) is changed to cf: x -> f(s(x)) where z = s(x) is the shifted
    location that is computed ( pointwise ) from:
    
         Psi_back(z) = Psi_forth(x),
    < = >            z = Inv(Psi_back)( Psi_forth(x) )
    < = >            s = Inv(Psi_back) o Psi_forth(x)
    
    To compute z = s(x) a fixed point iteration is used.
    
    ATTENTION: 
    ==========
    
    If s(x) leaves the the element that the integration point x is defined on, it will *NOT* change the
    element but result in an integration point that lies outside of the physical element.
    
    Parameters
    
    back : ngsolve.GridFunction
      transformation describing Psi_back as I + d_back where d_back is the deformation (can be None).
    
    forth : ngsolve.GridFunction
      transformation describing Psi_forth as I + d_forth where d_forth is the deformation (can be None).
    
    ASSUMPTIONS: 
    ============
    - 2D or 3D mesh
    """
ANY: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.ANY: 7>
BOTTOM: TIME_DOMAIN_TYPE  # value = <TIME_DOMAIN_TYPE.BOTTOM: 0>
CDOM_IF: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.CDOM_IF: 4>
CDOM_NEG: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.CDOM_NEG: 1>
CDOM_POS: COMBINED_DOMAIN_TYPE  # value = <COMBINED_DOMAIN_TYPE.CDOM_POS: 2>
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
ngsxfemglobals: GlobalNgsxfemVariables  # value = <xfem.xfem.GlobalNgsxfemVariables object>
