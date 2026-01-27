# This file is auto-generated. Do not edit directly.
from typing import Any, List, Union, Dict, Optional, Literal

ReturnType = Literal["entry", "polymer_entity", "non_polymer_entity", "polymer_instance", "assembly"]
ServiceType = Literal["text", "full_text", "sequence", "seqmotif", "structure", "chemical"]
OperatorType = Literal[
    "exact_match", "contains_phrase", "contains_words", "not_contains_phrase", 
    "greater", "greater_or_equal", "less", "less_or_equal", "range", "exists", "in"
]

# --- Node Architecture ---
class SearchNode:
    """Base class for all RCSB Search API nodes."""
    def __and__(self, other: 'SearchNode') -> 'GroupNode':
        return GroupNode("and", [self, other])

    def __or__(self, other: 'SearchNode') -> 'GroupNode':
        return GroupNode("or", [self, other])

    def to_dict(self) -> dict:
        raise NotImplementedError

class GroupNode(SearchNode):
    def __init__(self, operator: str, nodes: List[SearchNode]):
        self.operator = operator
        self.nodes = []
        for node in nodes:
            if isinstance(node, GroupNode) and node.operator == operator:
                self.nodes.extend(node.nodes)
            else:
                self.nodes.append(node)

    def to_dict(self) -> dict:
        return {
            "type": "group",
            "logical_operator": self.operator,
            "nodes": [node.to_dict() for node in self.nodes]
        }

class TerminalNode(SearchNode):
    def __init__(self, service: ServiceType, parameters: dict, label: str = None):
        self.service = service
        self.parameters = parameters
        self.label = label

    def to_dict(self) -> dict:
        node = {"type": "terminal", "service": self.service, "parameters": self.parameters}
        if self.label:
            node["label"] = self.label
        return node

class Attribute:
    """Represents a searchable field path (e.g., rcsb_entry_info.resolution_combined)."""
    def __init__(self, path: str, doc: str = ""):
        self._path = path
        self.__doc__ = doc

    def _op(self, operator: str, value: Any = None) -> TerminalNode:
        params = {"attribute": self._path, "operator": operator}
        if value is not None:
            params["value"] = value
        return TerminalNode("text", params)

    def equals(self, val: Any) -> TerminalNode: return self._op("exact_match", val)
    def contains(self, val: str) -> TerminalNode: return self._op("contains_phrase", val)
    def contains_words(self, val: str) -> TerminalNode: return self._op("contains_words", val)
    def greater_than(self, val: Union[int, float]) -> TerminalNode: return self._op("greater", val)
    def greater_or_equal(self, val: Union[int, float]) -> TerminalNode: return self._op("greater_or_equal", val)
    def less_than(self, val: Union[int, float]) -> TerminalNode: return self._op("less", val)
    def less_or_equal(self, val: Union[int, float]) -> TerminalNode: return self._op("less_or_equal", val)
    def range(self, min_val: Any, max_val: Any) -> TerminalNode: return self._op("range", [min_val, max_val])
    def in_set(self, val_list: List[Any]) -> TerminalNode: return self._op("in", val_list)
    def exists(self) -> TerminalNode: return self._op("exists")

# --- Service Helper Functions ---

def FullTextQuery(value: str) -> TerminalNode:
    """
    Global keyword search across all indexed text fields.
    Example: FullTextQuery("aspirin")
    """
    return TerminalNode("full_text", {"value": value})

def SequenceQuery(value: str, sequence_type: Literal["protein", "dna", "rna"] = "protein", 
                 identity_cutoff: float = 0.9, evalue_cutoff: float = 0.1) -> TerminalNode:
    """
    Sequence similarity search (BLAST-like).
    Args:
        value: The sequence string (one letter code).
        sequence_type: 'protein', 'dna', or 'rna'.
        identity_cutoff: Minimum identity (0.0 - 1.0).
        evalue_cutoff: Maximum E-value.
    """
    return TerminalNode("sequence", {
        "value": value, "sequence_type": sequence_type,
        "identity_cutoff": identity_cutoff, "evalue_cutoff": evalue_cutoff
    })

def MotifQuery(value: str, pattern_type: Literal["simple", "prosite", "regex"] = "simple") -> TerminalNode:
    """
    Sequence motif search.
    Args:
        value: Pattern string (e.g. 'C-x(2,4)-C').
        pattern_type: 'simple', 'prosite', or 'regex'.
    """
    return TerminalNode("seqmotif", {"value": value, "pattern_type": pattern_type})

def StructureMotifQuery(entry_id: str, residue_ids: List[dict], assembly_id: str = "1") -> TerminalNode:
    """
    3D Structure motif search (substructure similarity).
    Args:
        entry_id: PDB ID of the reference structure (e.g., '1MCT').
        residue_ids: List of residues defining the active site/motif.
                     e.g. [{'chain_id': 'A', 'struct_oper_id': '1', 'label_seq_id': 57}]
    """
    return TerminalNode("structure", {
        "value": {
            "entry_id": entry_id,
            "assembly_id": assembly_id,
            "residue_ids": residue_ids
        },
        "operator": "strict_shape_match" # Default operator
    })

def ChemicalQuery(value: str, type: Literal["formula", "descriptor"] = "formula", 
                 match_type: Literal["graph-exact", "graph-relaxed", "fingerprint-similarity", "sub-struct-graph-exact"] = None) -> TerminalNode:
    """
    Chemical formula or structure search (SMILES/InChI).
    Args:
        value: The formula (e.g., 'C8 H10 N4 O2') or descriptor string.
        type: 'formula' or 'descriptor'.
        match_type: Required if type='descriptor'. e.g. 'graph-exact', 'fingerprint-similarity'.
    """
    params = {"value": value, "type": type}
    if match_type:
        params["match_type"] = match_type
    return TerminalNode("chemical", params)

# --- Request Builder ---
class SearchRequest:
    """Wrapper to construct the final JSON payload for the Search API."""
    def __init__(self, query: SearchNode, return_type: ReturnType = "entry"):
        self.query = query
        self.return_type = return_type
        self.options = {}

    def paginate(self, start: int, rows: int):
        self.options["paginate"] = {"start": start, "rows": rows}
        return self

    def sort(self, field: str = "score", direction: Literal["asc", "desc"] = "desc"):
        if "sort" not in self.options: self.options["sort"] = []
        self.options["sort"].append({"sort_by": field, "direction": direction})
        return self

    def to_dict(self) -> dict:
        payload = {
            "query": self.query.to_dict(),
            "return_type": self.return_type
        }
        if self.options:
            payload["request_options"] = self.options
        return payload

# --- Generated Classes ---

class Attr_PdbxEntityNonpoly_8778912838621600994:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """This data item is a pointer to _chem_comp.id in the CHEM_COMP category."""
        return Attribute('pdbx_entity_nonpoly.comp_id')
    @property
    def entity_id(self) -> Attribute:
        """This data item is a pointer to _entity.id in the ENTITY category."""
        return Attribute('pdbx_entity_nonpoly.entity_id')
    @property
    def name(self) -> Attribute:
        """A name for the non-polymer entity"""
        return Attribute('pdbx_entity_nonpoly.name')
    @property
    def rcsb_prd_id(self) -> Attribute:
        """For non-polymer BIRD molecules the BIRD identifier for the entity."""
        return Attribute('pdbx_entity_nonpoly.rcsb_prd_id')

class Attr_RcsbLatestRevision_909480110613895552:
    """"""
    @property
    def major_revision(self) -> Attribute:
        """The major version number of the latest revision."""
        return Attribute('rcsb_latest_revision.major_revision')
    @property
    def minor_revision(self) -> Attribute:
        """The minor version number of the latest revision."""
        return Attribute('rcsb_latest_revision.minor_revision')
    @property
    def revision_date(self) -> Attribute:
        """The release date of the latest revision item."""
        return Attribute('rcsb_latest_revision.revision_date')

class Attr_RcsbNonpolymerEntity_2498174034378417098:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the entity."""
        return Attribute('rcsb_nonpolymer_entity.details')
    @property
    def formula_weight(self) -> Attribute:
        """Formula mass (KDa) of the entity."""
        return Attribute('rcsb_nonpolymer_entity.formula_weight')
    @property
    def pdbx_description(self) -> Attribute:
        """A description of the nonpolymer entity."""
        return Attribute('rcsb_nonpolymer_entity.pdbx_description')
    @property
    def pdbx_number_of_molecules(self) -> Attribute:
        """The number of molecules of the nonpolymer entity in the entry."""
        return Attribute('rcsb_nonpolymer_entity.pdbx_number_of_molecules')

class Attr_AnnotationLineage_2204887306774109602:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_nonpolymer_entity_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_nonpolymer_entity_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_nonpolymer_entity_annotation.annotation_lineage.name')

class Attr_RcsbNonpolymerEntityAnnotation_8352551812836966247:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_nonpolymer_entity_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_nonpolymer_entity_annotation.assignment_version')
    @property
    def comp_id(self) -> Attribute:
        """Non-polymer(ligand) chemical component identifier for the entity."""
        return Attribute('rcsb_nonpolymer_entity_annotation.comp_id')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_nonpolymer_entity_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_nonpolymer_entity_annotation.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_nonpolymer_entity_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_nonpolymer_entity_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_2204887306774109602':
        """"""
        return Attr_AnnotationLineage_2204887306774109602()

class Attr_RcsbNonpolymerEntityContainerIdentifiers_7723152394641565112:
    """"""
    @property
    def asym_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.asym_ids')
    @property
    def auth_asym_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.auth_asym_ids')
    @property
    def chem_ref_def_id(self) -> Attribute:
        """The chemical reference definition identifier for the entity in this container."""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.chem_ref_def_id')
    @property
    def entity_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.entity_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.entry_id')
    @property
    def nonpolymer_comp_id(self) -> Attribute:
        """Non-polymer(ligand) chemical component identifier for the entity in this container."""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.nonpolymer_comp_id')
    @property
    def prd_id(self) -> Attribute:
        """The BIRD identifier for the entity in this container."""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.prd_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers."""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.rcsb_id')
    @property
    def reference_chemical_identifiers_provenance_source(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.reference_chemical_identifiers_provenance_source')
    @property
    def reference_chemical_identifiers_resource_accession(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.reference_chemical_identifiers_resource_accession')
    @property
    def reference_chemical_identifiers_resource_name(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_entity_container_identifiers.reference_chemical_identifiers_resource_name')

class Attr_AdditionalProperties_2327390347434019813:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_nonpolymer_entity_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_entity_feature.additional_properties.values')

class Attr_RcsbNonpolymerEntityFeature_5417306140368469249:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_nonpolymer_entity_feature.assignment_version')
    @property
    def comp_id(self) -> Attribute:
        """Non-polymer(ligand) chemical component identifier for the entity."""
        return Attribute('rcsb_nonpolymer_entity_feature.comp_id')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_nonpolymer_entity_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_nonpolymer_entity_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_nonpolymer_entity_feature.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_nonpolymer_entity_feature.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_nonpolymer_entity_feature.type')
    @property
    def value(self) -> Attribute:
        """The feature value."""
        return Attribute('rcsb_nonpolymer_entity_feature.value')
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_2327390347434019813':
        """"""
        return Attr_AdditionalProperties_2327390347434019813()

class Attr_RcsbNonpolymerEntityFeatureSummary_6813952545237991837:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """Non-polymer(ligand) chemical component identifier for the entity."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.comp_id')
    @property
    def count(self) -> Attribute:
        """The feature count."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.count')
    @property
    def maximum_length(self) -> Attribute:
        """The maximum feature length."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.maximum_length')
    @property
    def maximum_value(self) -> Attribute:
        """The maximum feature value."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.maximum_value')
    @property
    def minimum_length(self) -> Attribute:
        """The minimum feature length."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.minimum_length')
    @property
    def minimum_value(self) -> Attribute:
        """The minimum feature value."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.minimum_value')
    @property
    def type(self) -> Attribute:
        """Type or category of the feature."""
        return Attribute('rcsb_nonpolymer_entity_feature_summary.type')

class Attr_RcsbNonpolymerEntityKeywords_373904751617707870:
    """"""
    @property
    def text(self) -> Attribute:
        """Keywords describing this non-polymer entity."""
        return Attribute('rcsb_nonpolymer_entity_keywords.text')

class Attr_RcsbNonpolymerEntityNameCom_2614432273012680843:
    """"""
    @property
    def name(self) -> Attribute:
        """A common name for the nonpolymer entity."""
        return Attribute('rcsb_nonpolymer_entity_name_com.name')

class Attr_ChemComp_3514688068582236663:
    """"""
    @property
    def formula(self) -> Attribute:
        """The formula for the chemical component. Formulae are written  according to the following rules:   (1) Only recognized element symbols may be used.   (2) Each element symbol is followed by a 'count' number. A count     of '1' may be omitted.   (3) A space or parenthesis must separate each cluster of     (element symbol + count), but in general parentheses are     not used.   (4) The order of elements depends on whether carbon is     present or not. If carbon is present, the order should be:     C, then H, then the other elements in alphabetical order     of their symbol. If carbon is not present, the elements     are listed purely in alphabetic order of their symbol. This     is the 'Hill' system used by Chemical Abstracts."""
        return Attribute('chem_comp.formula')
    @property
    def formula_weight(self) -> Attribute:
        """Formula mass of the chemical component."""
        return Attribute('chem_comp.formula_weight')
    @property
    def id(self) -> Attribute:
        """The value of _chem_comp.id must uniquely identify each item in  the CHEM_COMP list.   For protein polymer entities, this is the three-letter code for  the amino acid.   For nucleic acid polymer entities, this is the one-letter code  for the base."""
        return Attribute('chem_comp.id')
    @property
    def mon_nstd_parent_comp_id(self) -> Attribute:
        """"""
        return Attribute('chem_comp.mon_nstd_parent_comp_id')
    @property
    def name(self) -> Attribute:
        """The full name of the component."""
        return Attribute('chem_comp.name')
    @property
    def one_letter_code(self) -> Attribute:
        """For standard polymer components, the one-letter code for  the component.   For non-standard polymer components, the  one-letter code for parent component if this exists;  otherwise, the one-letter code should be given as 'X'.   Components that derived from multiple parents components  are described by a sequence of one-letter-codes."""
        return Attribute('chem_comp.one_letter_code')
    @property
    def pdbx_ambiguous_flag(self) -> Attribute:
        """A preliminary classification used by PDB to indicate  that the chemistry of this component while described  as clearly as possible is still ambiguous.  Software  tools may not be able to process this component  definition."""
        return Attribute('chem_comp.pdbx_ambiguous_flag')
    @property
    def pdbx_formal_charge(self) -> Attribute:
        """The net integer charge assigned to this component. This is the  formal charge assignment normally found in chemical diagrams."""
        return Attribute('chem_comp.pdbx_formal_charge')
    @property
    def pdbx_initial_date(self) -> Attribute:
        """Date component was added to database."""
        return Attribute('chem_comp.pdbx_initial_date')
    @property
    def pdbx_modified_date(self) -> Attribute:
        """Date component was last modified."""
        return Attribute('chem_comp.pdbx_modified_date')
    @property
    def pdbx_processing_site(self) -> Attribute:
        """This data item identifies the deposition site that processed  this chemical component defintion."""
        return Attribute('chem_comp.pdbx_processing_site')
    @property
    def pdbx_release_status(self) -> Attribute:
        """This data item holds the current release status for the component."""
        return Attribute('chem_comp.pdbx_release_status')
    @property
    def pdbx_replaced_by(self) -> Attribute:
        """Identifies the _chem_comp.id of the component that  has replaced this component."""
        return Attribute('chem_comp.pdbx_replaced_by')
    @property
    def pdbx_replaces(self) -> Attribute:
        """Identifies the _chem_comp.id's of the components  which have been replaced by this component.  Multiple id codes should be separated by commas."""
        return Attribute('chem_comp.pdbx_replaces')
    @property
    def pdbx_subcomponent_list(self) -> Attribute:
        """The list of subcomponents contained in this component."""
        return Attribute('chem_comp.pdbx_subcomponent_list')
    @property
    def three_letter_code(self) -> Attribute:
        """For standard polymer components, the common three-letter code for  the component.   Non-standard polymer components and non-polymer  components are also assigned three-letter-codes.   For ambiguous polymer components three-letter code should  be given as 'UNK'.  Ambiguous ions are assigned the code 'UNX'.  Ambiguous non-polymer components are assigned the code 'UNL'."""
        return Attribute('chem_comp.three_letter_code')
    @property
    def type(self) -> Attribute:
        """For standard polymer components, the type of the monomer.  Note that monomers that will form polymers are of three types:  linking monomers, monomers with some type of N-terminal (or 5')  cap and monomers with some type of C-terminal (or 3') cap."""
        return Attribute('chem_comp.type')

class Attr_PdbxChemCompAudit_4705584761086028783:
    """"""
    @property
    def action_type(self) -> Attribute:
        """The action associated with this audit record."""
        return Attribute('pdbx_chem_comp_audit.action_type')
    @property
    def comp_id(self) -> Attribute:
        """This data item is a pointer to _chem_comp.id in the CHEM_COMP  category."""
        return Attribute('pdbx_chem_comp_audit.comp_id')
    @property
    def date(self) -> Attribute:
        """The date associated with this audit record."""
        return Attribute('pdbx_chem_comp_audit.date')
    @property
    def details(self) -> Attribute:
        """Additional details decribing this change."""
        return Attribute('pdbx_chem_comp_audit.details')
    @property
    def ordinal(self) -> Attribute:
        """This data item is an ordinal index for the  PDBX_CHEM_COMP_AUDIT category."""
        return Attribute('pdbx_chem_comp_audit.ordinal')

class Attr_PdbxChemCompDescriptor_944258368257366730:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """This data item is a pointer to _chem_comp.id in the CHEM_COMP  category."""
        return Attribute('pdbx_chem_comp_descriptor.comp_id')
    @property
    def descriptor(self) -> Attribute:
        """This data item contains the descriptor value for this  component."""
        return Attribute('pdbx_chem_comp_descriptor.descriptor')
    @property
    def program(self) -> Attribute:
        """This data item contains the name of the program  or library used to compute the descriptor."""
        return Attribute('pdbx_chem_comp_descriptor.program')
    @property
    def program_version(self) -> Attribute:
        """This data item contains the version of the program  or library used to compute the descriptor."""
        return Attribute('pdbx_chem_comp_descriptor.program_version')
    @property
    def type(self) -> Attribute:
        """This data item contains the descriptor type."""
        return Attribute('pdbx_chem_comp_descriptor.type')

class Attr_PdbxChemCompFeature_5992594350396210640:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """The component identifier for this feature."""
        return Attribute('pdbx_chem_comp_feature.comp_id')
    @property
    def source(self) -> Attribute:
        """The information source for the component feature."""
        return Attribute('pdbx_chem_comp_feature.source')
    @property
    def type(self) -> Attribute:
        """The component feature type."""
        return Attribute('pdbx_chem_comp_feature.type')
    @property
    def value(self) -> Attribute:
        """The component feature value."""
        return Attribute('pdbx_chem_comp_feature.value')

class Attr_PdbxChemCompIdentifier_5913762028284950543:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """This data item is a pointer to _chem_comp.id in the CHEM_COMP  category."""
        return Attribute('pdbx_chem_comp_identifier.comp_id')
    @property
    def identifier(self) -> Attribute:
        """This data item contains the identifier value for this  component."""
        return Attribute('pdbx_chem_comp_identifier.identifier')
    @property
    def program(self) -> Attribute:
        """This data item contains the name of the program  or library used to compute the identifier."""
        return Attribute('pdbx_chem_comp_identifier.program')
    @property
    def program_version(self) -> Attribute:
        """This data item contains the version of the program  or library used to compute the identifier."""
        return Attribute('pdbx_chem_comp_identifier.program_version')
    @property
    def type(self) -> Attribute:
        """This data item contains the identifier type."""
        return Attribute('pdbx_chem_comp_identifier.type')

class Attr_PdbxFamilyPrdAudit_5629410239400904712:
    """"""
    @property
    def action_type(self) -> Attribute:
        """The action associated with this audit record."""
        return Attribute('pdbx_family_prd_audit.action_type')
    @property
    def annotator(self) -> Attribute:
        """The initials of the annotator creating of modifying the family."""
        return Attribute('pdbx_family_prd_audit.annotator')
    @property
    def date(self) -> Attribute:
        """The date associated with this audit record."""
        return Attribute('pdbx_family_prd_audit.date')
    @property
    def details(self) -> Attribute:
        """Additional details decribing this change."""
        return Attribute('pdbx_family_prd_audit.details')
    @property
    def family_prd_id(self) -> Attribute:
        """This data item is a pointer to _pdbx_reference_molecule_family.family_prd_id in the 	       pdbx_reference_molecule category."""
        return Attribute('pdbx_family_prd_audit.family_prd_id')
    @property
    def processing_site(self) -> Attribute:
        """An identifier for the wwPDB site creating or modifying the family."""
        return Attribute('pdbx_family_prd_audit.processing_site')

class Attr_PdbxPrdAudit_467923765230688021:
    """"""
    @property
    def action_type(self) -> Attribute:
        """The action associated with this audit record."""
        return Attribute('pdbx_prd_audit.action_type')
    @property
    def annotator(self) -> Attribute:
        """The initials of the annotator creating of modifying the molecule."""
        return Attribute('pdbx_prd_audit.annotator')
    @property
    def date(self) -> Attribute:
        """The date associated with this audit record."""
        return Attribute('pdbx_prd_audit.date')
    @property
    def details(self) -> Attribute:
        """Additional details decribing this change."""
        return Attribute('pdbx_prd_audit.details')
    @property
    def prd_id(self) -> Attribute:
        """This data item is a pointer to _pdbx_reference_molecule.prd_id in the 	       pdbx_reference_molecule category."""
        return Attribute('pdbx_prd_audit.prd_id')
    @property
    def processing_site(self) -> Attribute:
        """An identifier for the wwPDB site creating or modifying the molecule."""
        return Attribute('pdbx_prd_audit.processing_site')

class Attr_PdbxReferenceEntityList_4320910281296680440:
    """"""
    @property
    def component_id(self) -> Attribute:
        """The component number of this entity within the molecule."""
        return Attribute('pdbx_reference_entity_list.component_id')
    @property
    def details(self) -> Attribute:
        """Additional details about this entity."""
        return Attribute('pdbx_reference_entity_list.details')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_list.prd_id is a reference  _pdbx_reference_molecule.prd_id in the PDBX_REFERENCE_MOLECULE category."""
        return Attribute('pdbx_reference_entity_list.prd_id')
    @property
    def ref_entity_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_list.ref_entity_id is a unique identifier  the a constituent entity within this reference molecule."""
        return Attribute('pdbx_reference_entity_list.ref_entity_id')
    @property
    def type(self) -> Attribute:
        """Defines the polymer characteristic of the entity."""
        return Attribute('pdbx_reference_entity_list.type')

class Attr_PdbxReferenceEntityPoly_5699906335811438204:
    """"""
    @property
    def db_code(self) -> Attribute:
        """The database code for this source information"""
        return Attribute('pdbx_reference_entity_poly.db_code')
    @property
    def db_name(self) -> Attribute:
        """The database name for this source information"""
        return Attribute('pdbx_reference_entity_poly.db_name')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly.prd_id is a reference 	       _pdbx_reference_entity_list.prd_id in the  PDBX_REFERENCE_ENTITY_LIST category."""
        return Attribute('pdbx_reference_entity_poly.prd_id')
    @property
    def ref_entity_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly.ref_entity_id is a reference  to _pdbx_reference_entity_list.ref_entity_id in PDBX_REFERENCE_ENTITY_LIST category."""
        return Attribute('pdbx_reference_entity_poly.ref_entity_id')
    @property
    def type(self) -> Attribute:
        """The type of the polymer."""
        return Attribute('pdbx_reference_entity_poly.type')

class Attr_PdbxReferenceEntityPolyLink_1611015207283996980:
    """"""
    @property
    def atom_id_1(self) -> Attribute:
        """The atom identifier/name in the first of the two components making  the linkage."""
        return Attribute('pdbx_reference_entity_poly_link.atom_id_1')
    @property
    def atom_id_2(self) -> Attribute:
        """The atom identifier/name in the second of the two components making  the linkage."""
        return Attribute('pdbx_reference_entity_poly_link.atom_id_2')
    @property
    def comp_id_1(self) -> Attribute:
        """The component identifier in the first of the two components making the  linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.mon_id  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
        return Attribute('pdbx_reference_entity_poly_link.comp_id_1')
    @property
    def comp_id_2(self) -> Attribute:
        """The component identifier in the second of the two components making the  linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.mon_id  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
        return Attribute('pdbx_reference_entity_poly_link.comp_id_2')
    @property
    def component_id(self) -> Attribute:
        """The entity component identifier entity containing the linkage."""
        return Attribute('pdbx_reference_entity_poly_link.component_id')
    @property
    def entity_seq_num_1(self) -> Attribute:
        """For a polymer entity, the sequence number in the first of  the two components making the linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.num  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
        return Attribute('pdbx_reference_entity_poly_link.entity_seq_num_1')
    @property
    def entity_seq_num_2(self) -> Attribute:
        """For a polymer entity, the sequence number in the second of  the two components making the linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.num  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
        return Attribute('pdbx_reference_entity_poly_link.entity_seq_num_2')
    @property
    def link_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly_link.link_id uniquely identifies  a linkage within a polymer entity."""
        return Attribute('pdbx_reference_entity_poly_link.link_id')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly_link.prd_id is a reference  _pdbx_reference_entity_list.prd_id in the PDBX_REFERENCE_ENTITY_POLY category."""
        return Attribute('pdbx_reference_entity_poly_link.prd_id')
    @property
    def ref_entity_id(self) -> Attribute:
        """The reference entity id of the polymer entity containing the linkage.   This data item is a pointer to _pdbx_reference_entity_poly.ref_entity_id  in the PDBX_REFERENCE_ENTITY_POLY category."""
        return Attribute('pdbx_reference_entity_poly_link.ref_entity_id')
    @property
    def value_order(self) -> Attribute:
        """The bond order target for the non-standard linkage."""
        return Attribute('pdbx_reference_entity_poly_link.value_order')

class Attr_PdbxReferenceEntityPolySeq_423560373521741291:
    """"""
    @property
    def hetero(self) -> Attribute:
        """A flag to indicate that sequence heterogeneity at this monomer position."""
        return Attribute('pdbx_reference_entity_poly_seq.hetero')
    @property
    def mon_id(self) -> Attribute:
        """This data item is the chemical component identifier of monomer."""
        return Attribute('pdbx_reference_entity_poly_seq.mon_id')
    @property
    def num(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly_seq.num must uniquely and sequentially  identify a record in the PDBX_REFERENCE_ENTITY_POLY_SEQ list.   This value is conforms to author numbering conventions and does not map directly  to the numbering conventions used for _entity_poly_seq.num."""
        return Attribute('pdbx_reference_entity_poly_seq.num')
    @property
    def observed(self) -> Attribute:
        """A flag to indicate that this monomer is observed in the instance example."""
        return Attribute('pdbx_reference_entity_poly_seq.observed')
    @property
    def parent_mon_id(self) -> Attribute:
        """This data item is the chemical component identifier for the parent component corresponding to this monomer."""
        return Attribute('pdbx_reference_entity_poly_seq.parent_mon_id')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly_seq.prd_id is a reference 	       _pdbx_reference_entity_poly.prd_id in the  PDBX_REFERENCE_ENTITY_POLY category."""
        return Attribute('pdbx_reference_entity_poly_seq.prd_id')
    @property
    def ref_entity_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_poly_seq.ref_entity_id is a reference  to _pdbx_reference_entity_poly.ref_entity_id in PDBX_REFERENCE_ENTITY_POLY category."""
        return Attribute('pdbx_reference_entity_poly_seq.ref_entity_id')

class Attr_PdbxReferenceEntitySequence_4279113401125687683:
    """"""
    @property
    def NRP_flag(self) -> Attribute:
        """A flag to indicate a non-ribosomal entity."""
        return Attribute('pdbx_reference_entity_sequence.NRP_flag')
    @property
    def one_letter_codes(self) -> Attribute:
        """The one-letter-code sequence for this entity.  Non-standard monomers are represented as 'X'."""
        return Attribute('pdbx_reference_entity_sequence.one_letter_codes')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_sequence.prd_id is a reference 	       _pdbx_reference_entity_list.prd_id in the  PDBX_REFERENCE_ENTITY_LIST category."""
        return Attribute('pdbx_reference_entity_sequence.prd_id')
    @property
    def ref_entity_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_sequence.ref_entity_id is a reference  to _pdbx_reference_entity_list.ref_entity_id in PDBX_REFERENCE_ENTITY_LIST category."""
        return Attribute('pdbx_reference_entity_sequence.ref_entity_id')
    @property
    def type(self) -> Attribute:
        """The monomer type for the sequence."""
        return Attribute('pdbx_reference_entity_sequence.type')

class Attr_PdbxReferenceEntitySrcNat_2273266908519462102:
    """"""
    @property
    def atcc(self) -> Attribute:
        """The Americal Tissue Culture Collection code for organism from which the entity was isolated."""
        return Attribute('pdbx_reference_entity_src_nat.atcc')
    @property
    def db_code(self) -> Attribute:
        """The database code for this source information"""
        return Attribute('pdbx_reference_entity_src_nat.db_code')
    @property
    def db_name(self) -> Attribute:
        """The database name for this source information"""
        return Attribute('pdbx_reference_entity_src_nat.db_name')
    @property
    def ordinal(self) -> Attribute:
        """The value of _pdbx_reference_entity_src_nat.ordinal distinguishes 	       source details for this entity."""
        return Attribute('pdbx_reference_entity_src_nat.ordinal')
    @property
    def organism_scientific(self) -> Attribute:
        """The scientific name of the organism from which the entity was isolated."""
        return Attribute('pdbx_reference_entity_src_nat.organism_scientific')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_src_nat.prd_id is a reference 	       _pdbx_reference_entity_list.prd_id in the  PDBX_REFERENCE_ENTITY_LIST category."""
        return Attribute('pdbx_reference_entity_src_nat.prd_id')
    @property
    def ref_entity_id(self) -> Attribute:
        """The value of _pdbx_reference_entity_src_nat.ref_entity_id is a reference  to _pdbx_reference_entity_list.ref_entity_id in PDBX_REFERENCE_ENTITY_LIST category."""
        return Attribute('pdbx_reference_entity_src_nat.ref_entity_id')
    @property
    def source(self) -> Attribute:
        """The data source for this information."""
        return Attribute('pdbx_reference_entity_src_nat.source')
    @property
    def source_id(self) -> Attribute:
        """A identifier within the data source for this information."""
        return Attribute('pdbx_reference_entity_src_nat.source_id')
    @property
    def taxid(self) -> Attribute:
        """The NCBI TaxId of the organism from which the entity was isolated."""
        return Attribute('pdbx_reference_entity_src_nat.taxid')

class Attr_PdbxReferenceMolecule_5913335729239546704:
    """"""
    @property
    def chem_comp_id(self) -> Attribute:
        """For entities represented as single molecules, the identifier  corresponding to the chemical definition for the molecule."""
        return Attribute('pdbx_reference_molecule.chem_comp_id')
    @property
    def class_(self) -> Attribute:
        """Broadly defines the function of the entity."""
        return Attribute('pdbx_reference_molecule.class')
    @property
    def class_evidence_code(self) -> Attribute:
        """Evidence for the assignment of _pdbx_reference_molecule.class"""
        return Attribute('pdbx_reference_molecule.class_evidence_code')
    @property
    def compound_details(self) -> Attribute:
        """Special details about this molecule."""
        return Attribute('pdbx_reference_molecule.compound_details')
    @property
    def description(self) -> Attribute:
        """Description of this molecule."""
        return Attribute('pdbx_reference_molecule.description')
    @property
    def formula(self) -> Attribute:
        """The formula for the reference entity. Formulae are written  according to the rules:   1. Only recognised element symbols may be used.   2. Each element symbol is followed by a 'count' number. A count     of '1' may be omitted.   3. A space or parenthesis must separate each element symbol and     its count, but in general parentheses are not used.   4. The order of elements depends on whether or not carbon is     present. If carbon is present, the order should be: C, then     H, then the other elements in alphabetical order of their     symbol. If carbon is not present, the elements are listed     purely in alphabetic order of their symbol. This is the     'Hill' system used by Chemical Abstracts."""
        return Attribute('pdbx_reference_molecule.formula')
    @property
    def formula_weight(self) -> Attribute:
        """Formula mass in daltons of the entity."""
        return Attribute('pdbx_reference_molecule.formula_weight')
    @property
    def name(self) -> Attribute:
        """A name of the entity."""
        return Attribute('pdbx_reference_molecule.name')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule.prd_id is the unique identifier  for the reference molecule in this family.   By convention this ID uniquely identifies the reference molecule in  in the PDB reference dictionary.   The ID has the template form PRD_dddddd (e.g. PRD_000001)"""
        return Attribute('pdbx_reference_molecule.prd_id')
    @property
    def release_status(self) -> Attribute:
        """Defines the current PDB release status for this molecule definition."""
        return Attribute('pdbx_reference_molecule.release_status')
    @property
    def replaced_by(self) -> Attribute:
        """Assigns the identifier of the reference molecule that has replaced this molecule."""
        return Attribute('pdbx_reference_molecule.replaced_by')
    @property
    def replaces(self) -> Attribute:
        """Assigns the identifier for the reference molecule which have been replaced  by this reference molecule.  Multiple molecule identifier codes should be separated by commas."""
        return Attribute('pdbx_reference_molecule.replaces')
    @property
    def represent_as(self) -> Attribute:
        """Defines how this entity is represented in PDB data files."""
        return Attribute('pdbx_reference_molecule.represent_as')
    @property
    def representative_PDB_id_code(self) -> Attribute:
        """The PDB accession code for the entry containing a representative example of this molecule."""
        return Attribute('pdbx_reference_molecule.representative_PDB_id_code')
    @property
    def type(self) -> Attribute:
        """Defines the structural classification of the entity."""
        return Attribute('pdbx_reference_molecule.type')
    @property
    def type_evidence_code(self) -> Attribute:
        """Evidence for the assignment of _pdbx_reference_molecule.type"""
        return Attribute('pdbx_reference_molecule.type_evidence_code')

class Attr_PdbxReferenceMoleculeAnnotation_3720401434528444555:
    """"""
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_annotation.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
        return Attribute('pdbx_reference_molecule_annotation.family_prd_id')
    @property
    def ordinal(self) -> Attribute:
        """This data item distinguishes anotations for this entity."""
        return Attribute('pdbx_reference_molecule_annotation.ordinal')
    @property
    def prd_id(self) -> Attribute:
        """This data item is a pointer to _pdbx_reference_molecule.prd_id in the  PDB_REFERENCE_MOLECULE category."""
        return Attribute('pdbx_reference_molecule_annotation.prd_id')
    @property
    def source(self) -> Attribute:
        """The source of the annoation for this entity."""
        return Attribute('pdbx_reference_molecule_annotation.source')
    @property
    def text(self) -> Attribute:
        """Text describing the annotation for this entity."""
        return Attribute('pdbx_reference_molecule_annotation.text')
    @property
    def type(self) -> Attribute:
        """Type of annotation for this entity."""
        return Attribute('pdbx_reference_molecule_annotation.type')

class Attr_PdbxReferenceMoleculeDetails_5854178980865644353:
    """"""
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_details.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id' in category PDBX_REFERENCE_MOLECULE_FAMILY."""
        return Attribute('pdbx_reference_molecule_details.family_prd_id')
    @property
    def ordinal(self) -> Attribute:
        """The value of _pdbx_reference_molecule_details.ordinal is an ordinal that  distinguishes each descriptive text for this entity."""
        return Attribute('pdbx_reference_molecule_details.ordinal')
    @property
    def source(self) -> Attribute:
        """A data source of this information (e.g. PubMed, Merck Index)"""
        return Attribute('pdbx_reference_molecule_details.source')
    @property
    def source_id(self) -> Attribute:
        """A identifier within the data source for this information."""
        return Attribute('pdbx_reference_molecule_details.source_id')
    @property
    def text(self) -> Attribute:
        """The text of the description of special aspects of the entity."""
        return Attribute('pdbx_reference_molecule_details.text')

class Attr_PdbxReferenceMoleculeFamily_8096817097636067251:
    """"""
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_entity.family_prd_id must uniquely identify a record in the  PDBX_REFERENCE_MOLECULE_FAMILY list.   By convention this ID uniquely identifies the reference family in  in the PDB reference dictionary.   The ID has the template form FAM_dddddd (e.g. FAM_000001)"""
        return Attribute('pdbx_reference_molecule_family.family_prd_id')
    @property
    def name(self) -> Attribute:
        """The entity family name."""
        return Attribute('pdbx_reference_molecule_family.name')
    @property
    def release_status(self) -> Attribute:
        """Assigns the current PDB release status for this family."""
        return Attribute('pdbx_reference_molecule_family.release_status')
    @property
    def replaced_by(self) -> Attribute:
        """Assigns the identifier of the family that has replaced this component."""
        return Attribute('pdbx_reference_molecule_family.replaced_by')
    @property
    def replaces(self) -> Attribute:
        """Assigns the identifier for the family which have been replaced by this family.  Multiple family identifier codes should be separated by commas."""
        return Attribute('pdbx_reference_molecule_family.replaces')

class Attr_PdbxReferenceMoleculeFeatures_5006906081052064742:
    """"""
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_features.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
        return Attribute('pdbx_reference_molecule_features.family_prd_id')
    @property
    def ordinal(self) -> Attribute:
        """The value of _pdbx_reference_molecule_features.ordinal distinguishes 	       each feature for this entity."""
        return Attribute('pdbx_reference_molecule_features.ordinal')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_features.prd_id is a reference 	       _pdbx_reference_molecule.prd_id in the  PDBX_REFERENCE_MOLECULE category."""
        return Attribute('pdbx_reference_molecule_features.prd_id')
    @property
    def source(self) -> Attribute:
        """The information source for the component feature."""
        return Attribute('pdbx_reference_molecule_features.source')
    @property
    def source_ordinal(self) -> Attribute:
        """The value of _pdbx_reference_molecule_features.source_ordinal provides 	       the priority order of features from a particular source or database."""
        return Attribute('pdbx_reference_molecule_features.source_ordinal')
    @property
    def type(self) -> Attribute:
        """The entity feature type."""
        return Attribute('pdbx_reference_molecule_features.type')
    @property
    def value(self) -> Attribute:
        """The entity feature value."""
        return Attribute('pdbx_reference_molecule_features.value')

class Attr_PdbxReferenceMoleculeList_9123781017092751690:
    """"""
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_list.family_prd_id is a reference to  _pdbx_reference_molecule_family.family_prd_id' in category PDBX_REFERENCE_MOLECULE_FAMILY."""
        return Attribute('pdbx_reference_molecule_list.family_prd_id')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_list.prd_id is the unique identifier  for the reference molecule in this family.   By convention this ID uniquely identifies the reference molecule in  in the PDB reference dictionary.   The ID has the template form PRD_dddddd (e.g. PRD_000001)"""
        return Attribute('pdbx_reference_molecule_list.prd_id')

class Attr_PdbxReferenceMoleculeRelatedStructures_4419261954773238425:
    """"""
    @property
    def citation_id(self) -> Attribute:
        """A link to related reference information in the citation category."""
        return Attribute('pdbx_reference_molecule_related_structures.citation_id')
    @property
    def db_accession(self) -> Attribute:
        """The database accession code for the related structure reference."""
        return Attribute('pdbx_reference_molecule_related_structures.db_accession')
    @property
    def db_code(self) -> Attribute:
        """The database identifier code for the related structure reference."""
        return Attribute('pdbx_reference_molecule_related_structures.db_code')
    @property
    def db_name(self) -> Attribute:
        """The database name for the related structure reference."""
        return Attribute('pdbx_reference_molecule_related_structures.db_name')
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_related_structures.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
        return Attribute('pdbx_reference_molecule_related_structures.family_prd_id')
    @property
    def formula(self) -> Attribute:
        """The formula for the reference entity. Formulae are written  according to the rules:   1. Only recognised element symbols may be used.   2. Each element symbol is followed by a 'count' number. A count     of '1' may be omitted.   3. A space or parenthesis must separate each element symbol and     its count, but in general parentheses are not used.   4. The order of elements depends on whether or not carbon is     present. If carbon is present, the order should be: C, then     H, then the other elements in alphabetical order of their     symbol. If carbon is not present, the elements are listed     purely in alphabetic order of their symbol. This is the     'Hill' system used by Chemical Abstracts."""
        return Attribute('pdbx_reference_molecule_related_structures.formula')
    @property
    def name(self) -> Attribute:
        """The chemical name for the structure entry in the related database"""
        return Attribute('pdbx_reference_molecule_related_structures.name')
    @property
    def ordinal(self) -> Attribute:
        """The value of _pdbx_reference_molecule_related_structures.ordinal distinguishes  related structural data for each entity."""
        return Attribute('pdbx_reference_molecule_related_structures.ordinal')

class Attr_PdbxReferenceMoleculeSynonyms_7929125595815704912:
    """"""
    @property
    def family_prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_synonyms.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
        return Attribute('pdbx_reference_molecule_synonyms.family_prd_id')
    @property
    def name(self) -> Attribute:
        """A synonym name for the entity."""
        return Attribute('pdbx_reference_molecule_synonyms.name')
    @property
    def ordinal(self) -> Attribute:
        """The value of _pdbx_reference_molecule_synonyms.ordinal is an ordinal 	       to distinguish synonyms for this entity."""
        return Attribute('pdbx_reference_molecule_synonyms.ordinal')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_reference_molecule_synonyms.prd_id is a reference 	       _pdbx_reference_molecule.prd_id in the  PDBX_REFERENCE_MOLECULE category."""
        return Attribute('pdbx_reference_molecule_synonyms.prd_id')
    @property
    def source(self) -> Attribute:
        """The source of this synonym name for the entity."""
        return Attribute('pdbx_reference_molecule_synonyms.source')

class Attr_RcsbBirdCitation_4986285152268166071:
    """"""
    @property
    def id(self) -> Attribute:
        """The value of _rcsb_bird_citation.id must uniquely identify a record in the  rcsb_bird_citation list."""
        return Attribute('rcsb_bird_citation.id')
    @property
    def journal_abbrev(self) -> Attribute:
        """Abbreviated name of the cited journal as given in the  Chemical Abstracts Service Source Index."""
        return Attribute('rcsb_bird_citation.journal_abbrev')
    @property
    def journal_volume(self) -> Attribute:
        """Volume number of the journal cited; relevant for journal  articles."""
        return Attribute('rcsb_bird_citation.journal_volume')
    @property
    def page_first(self) -> Attribute:
        """The first page of the rcsb_bird_citation; relevant for journal  articles, books and book chapters."""
        return Attribute('rcsb_bird_citation.page_first')
    @property
    def page_last(self) -> Attribute:
        """The last page of the rcsb_bird_citation; relevant for journal  articles, books and book chapters."""
        return Attribute('rcsb_bird_citation.page_last')
    @property
    def pdbx_database_id_DOI(self) -> Attribute:
        """Document Object Identifier used by doi.org to uniquely  specify bibliographic entry."""
        return Attribute('rcsb_bird_citation.pdbx_database_id_DOI')
    @property
    def pdbx_database_id_PubMed(self) -> Attribute:
        """Ascession number used by PubMed to categorize a specific  bibliographic entry."""
        return Attribute('rcsb_bird_citation.pdbx_database_id_PubMed')
    @property
    def rcsb_authors(self) -> Attribute:
        """"""
        return Attribute('rcsb_bird_citation.rcsb_authors')
    @property
    def title(self) -> Attribute:
        """The title of the rcsb_bird_citation; relevant for journal articles, books  and book chapters."""
        return Attribute('rcsb_bird_citation.title')
    @property
    def year(self) -> Attribute:
        """The year of the rcsb_bird_citation; relevant for journal articles, books  and book chapters."""
        return Attribute('rcsb_bird_citation.year')

class Attr_AnnotationLineage_5786027430767607171:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_chem_comp_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_chem_comp_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_chem_comp_annotation.annotation_lineage.name')

class Attr_RcsbChemCompAnnotation_5910187435239757597:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_chem_comp_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_chem_comp_annotation.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_chem_comp_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_chem_comp_annotation.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_chem_comp_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_chem_comp_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_5786027430767607171':
        """"""
        return Attr_AnnotationLineage_5786027430767607171()

class Attr_RcsbChemCompContainerIdentifiers_3544777131158993539:
    """"""
    @property
    def atc_codes(self) -> Attribute:
        """"""
        return Attribute('rcsb_chem_comp_container_identifiers.atc_codes')
    @property
    def comp_id(self) -> Attribute:
        """The chemical component identifier."""
        return Attribute('rcsb_chem_comp_container_identifiers.comp_id')
    @property
    def drugbank_id(self) -> Attribute:
        """The DrugBank identifier corresponding to the chemical component."""
        return Attribute('rcsb_chem_comp_container_identifiers.drugbank_id')
    @property
    def prd_id(self) -> Attribute:
        """The BIRD definition identifier."""
        return Attribute('rcsb_chem_comp_container_identifiers.prd_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for the chemical definition in this container."""
        return Attribute('rcsb_chem_comp_container_identifiers.rcsb_id')
    @property
    def subcomponent_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_chem_comp_container_identifiers.subcomponent_ids')

class Attr_RcsbChemCompDescriptor_2875693885776408658:
    """"""
    @property
    def InChI(self) -> Attribute:
        """Standard IUPAC International Chemical Identifier (InChI) descriptor for the chemical component.     InChI, the IUPAC International Chemical Identifier,    by Stephen R Heller, Alan McNaught, Igor Pletnev, Stephen Stein and Dmitrii Tchekhovskoi,    Journal of Cheminformatics, 2015, 7:23;"""
        return Attribute('rcsb_chem_comp_descriptor.InChI')
    @property
    def InChIKey(self) -> Attribute:
        """Standard IUPAC International Chemical Identifier (InChI) descriptor key  for the chemical component   InChI, the IUPAC International Chemical Identifier,  by Stephen R Heller, Alan McNaught, Igor Pletnev, Stephen Stein and Dmitrii Tchekhovskoi,  Journal of Cheminformatics, 2015, 7:23"""
        return Attribute('rcsb_chem_comp_descriptor.InChIKey')
    @property
    def SMILES(self) -> Attribute:
        """Simplified molecular-input line-entry system (SMILES) descriptor for the chemical component.     Weininger D (February 1988). 'SMILES, a chemical language and information system. 1.    Introduction to methodology and encoding rules'. Journal of Chemical Information and Modeling. 28 (1): 31-6.     Weininger D, Weininger A, Weininger JL (May 1989).    'SMILES. 2. Algorithm for generation of unique SMILES notation',    Journal of Chemical Information and Modeling. 29 (2): 97-101."""
        return Attribute('rcsb_chem_comp_descriptor.SMILES')
    @property
    def SMILES_stereo(self) -> Attribute:
        """Simplified molecular-input line-entry system (SMILES) descriptor for the chemical  component including stereochemical features.   Weininger D (February 1988). 'SMILES, a chemical language and information system. 1.  Introduction to methodology and encoding rules'.  Journal of Chemical Information and Modeling. 28 (1): 31-6.   Weininger D, Weininger A, Weininger JL (May 1989).  'SMILES. 2. Algorithm for generation of unique SMILES notation'.  Journal of Chemical Information and Modeling. 29 (2): 97-101."""
        return Attribute('rcsb_chem_comp_descriptor.SMILES_stereo')
    @property
    def comp_id(self) -> Attribute:
        """The chemical component identifier."""
        return Attribute('rcsb_chem_comp_descriptor.comp_id')

class Attr_RcsbChemCompInfo_7676662344779069623:
    """"""
    @property
    def atom_count(self) -> Attribute:
        """Chemical component total atom count"""
        return Attribute('rcsb_chem_comp_info.atom_count')
    @property
    def atom_count_chiral(self) -> Attribute:
        """Chemical component chiral atom count"""
        return Attribute('rcsb_chem_comp_info.atom_count_chiral')
    @property
    def atom_count_heavy(self) -> Attribute:
        """Chemical component heavy atom count"""
        return Attribute('rcsb_chem_comp_info.atom_count_heavy')
    @property
    def bond_count(self) -> Attribute:
        """Chemical component total bond count"""
        return Attribute('rcsb_chem_comp_info.bond_count')
    @property
    def bond_count_aromatic(self) -> Attribute:
        """Chemical component aromatic bond count"""
        return Attribute('rcsb_chem_comp_info.bond_count_aromatic')
    @property
    def comp_id(self) -> Attribute:
        """The chemical component identifier."""
        return Attribute('rcsb_chem_comp_info.comp_id')
    @property
    def initial_deposition_date(self) -> Attribute:
        """The date the chemical definition was first deposited in the PDB repository."""
        return Attribute('rcsb_chem_comp_info.initial_deposition_date')
    @property
    def initial_release_date(self) -> Attribute:
        """The initial date the chemical definition was released in the PDB repository."""
        return Attribute('rcsb_chem_comp_info.initial_release_date')
    @property
    def release_status(self) -> Attribute:
        """The release status of the chemical definition."""
        return Attribute('rcsb_chem_comp_info.release_status')
    @property
    def revision_date(self) -> Attribute:
        """The date of last revision of the chemical definition."""
        return Attribute('rcsb_chem_comp_info.revision_date')

class Attr_RcsbChemCompRelated_3136262384131889076:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """The value of _rcsb_chem_comp_related.comp_id is a reference to  a chemical component definition."""
        return Attribute('rcsb_chem_comp_related.comp_id')
    @property
    def ordinal(self) -> Attribute:
        """The value of _rcsb_chem_comp_related.ordinal distinguishes  related examples for each chemical component."""
        return Attribute('rcsb_chem_comp_related.ordinal')
    @property
    def related_mapping_method(self) -> Attribute:
        """The method used to establish the resource correspondence."""
        return Attribute('rcsb_chem_comp_related.related_mapping_method')
    @property
    def resource_accession_code(self) -> Attribute:
        """The resource identifier code for the related chemical reference."""
        return Attribute('rcsb_chem_comp_related.resource_accession_code')
    @property
    def resource_name(self) -> Attribute:
        """The resource name for the related chemical reference."""
        return Attribute('rcsb_chem_comp_related.resource_name')

class Attr_RcsbChemCompSynonyms_3609015270641752462:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """The chemical component to which this synonym applies."""
        return Attribute('rcsb_chem_comp_synonyms.comp_id')
    @property
    def name(self) -> Attribute:
        """The synonym of this particular chemical component."""
        return Attribute('rcsb_chem_comp_synonyms.name')
    @property
    def ordinal(self) -> Attribute:
        """This data item is an ordinal index for the  RCSB_CHEM_COMP_SYNONYMS category."""
        return Attribute('rcsb_chem_comp_synonyms.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """The provenance of this synonym."""
        return Attribute('rcsb_chem_comp_synonyms.provenance_source')
    @property
    def type(self) -> Attribute:
        """This data item contains the synonym type."""
        return Attribute('rcsb_chem_comp_synonyms.type')

class Attr_RcsbChemCompTarget_8644528845840450023:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """The value of _rcsb_chem_comp_target.comp_id is a reference to  a chemical component definition."""
        return Attribute('rcsb_chem_comp_target.comp_id')
    @property
    def interaction_type(self) -> Attribute:
        """The type of target interaction."""
        return Attribute('rcsb_chem_comp_target.interaction_type')
    @property
    def name(self) -> Attribute:
        """The chemical component target name."""
        return Attribute('rcsb_chem_comp_target.name')
    @property
    def ordinal(self) -> Attribute:
        """The value of _rcsb_chem_comp_target.ordinal distinguishes  related examples for each chemical component."""
        return Attribute('rcsb_chem_comp_target.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """A code indicating the provenance of the target interaction assignment"""
        return Attribute('rcsb_chem_comp_target.provenance_source')
    @property
    def reference_database_accession_code(self) -> Attribute:
        """The reference identifier code for the target interaction reference."""
        return Attribute('rcsb_chem_comp_target.reference_database_accession_code')
    @property
    def reference_database_name(self) -> Attribute:
        """The reference database name for the target interaction."""
        return Attribute('rcsb_chem_comp_target.reference_database_name')
    @property
    def target_actions(self) -> Attribute:
        """"""
        return Attribute('rcsb_chem_comp_target.target_actions')

class Attr_RcsbSchemaContainerIdentifiers_2309482841021532999:
    """"""
    @property
    def collection_name(self) -> Attribute:
        """Collection name associated with the data in the container."""
        return Attribute('rcsb_schema_container_identifiers.collection_name')
    @property
    def collection_schema_version(self) -> Attribute:
        """Version string for the schema and collection."""
        return Attribute('rcsb_schema_container_identifiers.collection_schema_version')
    @property
    def schema_name(self) -> Attribute:
        """Schema name associated with the data in the container."""
        return Attribute('rcsb_schema_container_identifiers.schema_name')

class Attr_PdbxStructAssembly_23494749422806577:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the macromolecular assembly.                 In the PDB, 'representative helical assembly', 'complete point assembly', 	       'complete icosahedral assembly', 'software_defined_assembly', 'author_defined_assembly', 	       and 'author_and_software_defined_assembly' are considered 'biologically relevant assemblies."""
        return Attribute('pdbx_struct_assembly.details')
    @property
    def id(self) -> Attribute:
        """The value of _pdbx_struct_assembly.id must uniquely identify a record in  the PDBX_STRUCT_ASSEMBLY list."""
        return Attribute('pdbx_struct_assembly.id')
    @property
    def method_details(self) -> Attribute:
        """Provides details of the method used to determine or  compute the assembly."""
        return Attribute('pdbx_struct_assembly.method_details')
    @property
    def oligomeric_count(self) -> Attribute:
        """The number of polymer molecules in the assembly."""
        return Attribute('pdbx_struct_assembly.oligomeric_count')
    @property
    def oligomeric_details(self) -> Attribute:
        """Provides the details of the oligomeric state of the assembly."""
        return Attribute('pdbx_struct_assembly.oligomeric_details')
    @property
    def rcsb_candidate_assembly(self) -> Attribute:
        """Candidate macromolecular assembly.   Excludes the following cases classified in pdbx_struct_asembly.details:   'crystal asymmetric unit', 'crystal asymmetric unit, crystal frame', 'helical asymmetric unit',  'helical asymmetric unit, std helical frame','icosahedral 23 hexamer', 'icosahedral asymmetric unit',  'icosahedral asymmetric unit, std point frame','icosahedral pentamer', 'pentasymmetron capsid unit',  'point asymmetric unit', 'point asymmetric unit, std point frame','trisymmetron capsid unit',   and 'deposited_coordinates'."""
        return Attribute('pdbx_struct_assembly.rcsb_candidate_assembly')
    @property
    def rcsb_details(self) -> Attribute:
        """A filtered description of the macromolecular assembly."""
        return Attribute('pdbx_struct_assembly.rcsb_details')

class Attr_PdbxStructAssemblyAuthEvidence_9042404590181311099:
    """"""
    @property
    def assembly_id(self) -> Attribute:
        """This item references an assembly in pdbx_struct_assembly"""
        return Attribute('pdbx_struct_assembly_auth_evidence.assembly_id')
    @property
    def details(self) -> Attribute:
        """Provides any additional information regarding the evidence of this assembly"""
        return Attribute('pdbx_struct_assembly_auth_evidence.details')
    @property
    def experimental_support(self) -> Attribute:
        """Provides the experimental method to determine the state of this assembly"""
        return Attribute('pdbx_struct_assembly_auth_evidence.experimental_support')
    @property
    def id(self) -> Attribute:
        """Identifies a unique record in pdbx_struct_assembly_auth_evidence."""
        return Attribute('pdbx_struct_assembly_auth_evidence.id')

class Attr_PdbxStructAssemblyGen_6492419249568703958:
    """"""
    @property
    def assembly_id(self) -> Attribute:
        """This data item is a pointer to _pdbx_struct_assembly.id in the  PDBX_STRUCT_ASSEMBLY category."""
        return Attribute('pdbx_struct_assembly_gen.assembly_id')
    @property
    def asym_id_list(self) -> Attribute:
        """"""
        return Attribute('pdbx_struct_assembly_gen.asym_id_list')
    @property
    def oper_expression(self) -> Attribute:
        """Identifies the operation of collection of operations  from category PDBX_STRUCT_OPER_LIST.   Operation expressions may have the forms:    (1)        the single operation 1   (1,2,5)    the operations 1, 2, 5   (1-4)      the operations 1,2,3 and 4   (1,2)(3,4) the combinations of operations              3 and 4 followed by 1 and 2 (i.e.              the cartesian product of parenthetical              groups applied from right to left)"""
        return Attribute('pdbx_struct_assembly_gen.oper_expression')
    @property
    def ordinal(self) -> Attribute:
        """This data item is an ordinal index for the  PDBX_STRUCT_ASSEMBLY category."""
        return Attribute('pdbx_struct_assembly_gen.ordinal')

class Attr_PdbxStructAssemblyProp_1730850938995923140:
    """"""
    @property
    def assembly_id(self) -> Attribute:
        """The identifier for the assembly used in category PDBX_STRUCT_ASSEMBLY."""
        return Attribute('pdbx_struct_assembly_prop.assembly_id')
    @property
    def biol_id(self) -> Attribute:
        """The identifier for the assembly used in category PDBX_STRUCT_ASSEMBLY."""
        return Attribute('pdbx_struct_assembly_prop.biol_id')
    @property
    def type(self) -> Attribute:
        """The property type for the assembly."""
        return Attribute('pdbx_struct_assembly_prop.type')
    @property
    def value(self) -> Attribute:
        """The value of the assembly property."""
        return Attribute('pdbx_struct_assembly_prop.value')

class Attr_PdbxStructOperList_3741840671125252682:
    """"""
    @property
    def id(self) -> Attribute:
        """This identifier code must uniquely identify a  record in the PDBX_STRUCT_OPER_LIST list."""
        return Attribute('pdbx_struct_oper_list.id')
    @property
    def matrix_1_1(self) -> Attribute:
        """The [1][1] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_1_1')
    @property
    def matrix_1_2(self) -> Attribute:
        """The [1][2] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_1_2')
    @property
    def matrix_1_3(self) -> Attribute:
        """The [1][3] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_1_3')
    @property
    def matrix_2_1(self) -> Attribute:
        """The [2][1] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_2_1')
    @property
    def matrix_2_2(self) -> Attribute:
        """The [2][2] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_2_2')
    @property
    def matrix_2_3(self) -> Attribute:
        """The [2][3] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_2_3')
    @property
    def matrix_3_1(self) -> Attribute:
        """The [3][1] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_3_1')
    @property
    def matrix_3_2(self) -> Attribute:
        """The [3][2] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_3_2')
    @property
    def matrix_3_3(self) -> Attribute:
        """The [3][3] element of the 3x3 matrix component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.matrix_3_3')
    @property
    def name(self) -> Attribute:
        """A descriptive name for the transformation operation."""
        return Attribute('pdbx_struct_oper_list.name')
    @property
    def symmetry_operation(self) -> Attribute:
        """The symmetry operation corresponding to the transformation operation."""
        return Attribute('pdbx_struct_oper_list.symmetry_operation')
    @property
    def type(self) -> Attribute:
        """A code to indicate the type of operator."""
        return Attribute('pdbx_struct_oper_list.type')
    @property
    def vector_1(self) -> Attribute:
        """The [1] element of the three-element vector component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.vector_1')
    @property
    def vector_2(self) -> Attribute:
        """The [2] element of the three-element vector component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.vector_2')
    @property
    def vector_3(self) -> Attribute:
        """The [3] element of the three-element vector component of the  transformation operation."""
        return Attribute('pdbx_struct_oper_list.vector_3')

class Attr_AdditionalProperties_1803097747161589805:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_assembly_annotation.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_assembly_annotation.additional_properties.values')

class Attr_RcsbAssemblyAnnotation_6537260788827864652:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_assembly_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_assembly_annotation.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_assembly_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_assembly_annotation.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that assigned the annotation."""
        return Attribute('rcsb_assembly_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_assembly_annotation.type')
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_1803097747161589805':
        """"""
        return Attr_AdditionalProperties_1803097747161589805()

class Attr_RcsbAssemblyContainerIdentifiers_1245167145276486690:
    """"""
    @property
    def assembly_id(self) -> Attribute:
        """Assembly identifier for the container."""
        return Attribute('rcsb_assembly_container_identifiers.assembly_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_assembly_container_identifiers.entry_id')
    @property
    def interface_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_assembly_container_identifiers.interface_ids')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this assembly container formed by  a dash separated concatenation of entry and assembly identifiers."""
        return Attribute('rcsb_assembly_container_identifiers.rcsb_id')

class Attr_AdditionalProperties_5704814570036358136:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_assembly_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_assembly_feature.additional_properties.values')

class Attr_FeaturePositions_6568749982771173754:
    """"""
    @property
    def asym_id(self) -> Attribute:
        """An identifier of polymer chain (label_asym_id) corresponding to the feature assignment."""
        return Attribute('rcsb_assembly_feature.feature_positions.asym_id')
    @property
    def beg_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature begins."""
        return Attribute('rcsb_assembly_feature.feature_positions.beg_seq_id')
    @property
    def end_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature ends."""
        return Attribute('rcsb_assembly_feature.feature_positions.end_seq_id')
    @property
    def struct_oper_list(self) -> Attribute:
        """"""
        return Attribute('rcsb_assembly_feature.feature_positions.struct_oper_list')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_assembly_feature.feature_positions.values')

class Attr_RcsbAssemblyFeature_5968959041198250090:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_assembly_feature.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_assembly_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_assembly_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_assembly_feature.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that assigned the feature."""
        return Attribute('rcsb_assembly_feature.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_assembly_feature.type')
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_5704814570036358136':
        """"""
        return Attr_AdditionalProperties_5704814570036358136()
    @property
    def feature_positions(self) -> 'Attr_FeaturePositions_6568749982771173754':
        """"""
        return Attr_FeaturePositions_6568749982771173754()

class Attr_RcsbAssemblyInfo_5934210934139594148:
    """"""
    @property
    def assembly_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_assembly_info.assembly_id')
    @property
    def atom_count(self) -> Attribute:
        """The assembly non-hydrogen atomic coordinate count."""
        return Attribute('rcsb_assembly_info.atom_count')
    @property
    def branched_atom_count(self) -> Attribute:
        """The assembly non-hydrogen branched entity atomic coordinate count."""
        return Attribute('rcsb_assembly_info.branched_atom_count')
    @property
    def branched_entity_count(self) -> Attribute:
        """The number of distinct branched entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.branched_entity_count')
    @property
    def branched_entity_instance_count(self) -> Attribute:
        """The number of branched instances in the generated assembly data set.  This is the total count of branched entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.branched_entity_instance_count')
    @property
    def deuterated_water_count(self) -> Attribute:
        """The assembly deuterated water molecule count."""
        return Attribute('rcsb_assembly_info.deuterated_water_count')
    @property
    def entry_id(self) -> Attribute:
        """The PDB entry accession code."""
        return Attribute('rcsb_assembly_info.entry_id')
    @property
    def hydrogen_atom_count(self) -> Attribute:
        """The assembly hydrogen atomic coordinate count."""
        return Attribute('rcsb_assembly_info.hydrogen_atom_count')
    @property
    def modeled_polymer_monomer_count(self) -> Attribute:
        """The number of modeled polymer monomers in the assembly coordinate data.  This is the total count of monomers with reported coordinate data for all polymer  entity instances in the generated assembly coordinate data."""
        return Attribute('rcsb_assembly_info.modeled_polymer_monomer_count')
    @property
    def na_polymer_entity_types(self) -> Attribute:
        """Nucleic acid polymer entity type categories describing the generated assembly."""
        return Attribute('rcsb_assembly_info.na_polymer_entity_types')
    @property
    def nonpolymer_atom_count(self) -> Attribute:
        """The assembly non-hydrogen non-polymer entity atomic coordinate count."""
        return Attribute('rcsb_assembly_info.nonpolymer_atom_count')
    @property
    def nonpolymer_entity_count(self) -> Attribute:
        """The number of distinct non-polymer entities in the generated assembly exclusive of solvent."""
        return Attribute('rcsb_assembly_info.nonpolymer_entity_count')
    @property
    def nonpolymer_entity_instance_count(self) -> Attribute:
        """The number of non-polymer instances in the generated assembly data set exclusive of solvent.  This is the total count of non-polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.nonpolymer_entity_instance_count')
    @property
    def num_heterologous_interface_entities(self) -> Attribute:
        """Number of heterologous (both binding sites are different) interface entities"""
        return Attribute('rcsb_assembly_info.num_heterologous_interface_entities')
    @property
    def num_heteromeric_interface_entities(self) -> Attribute:
        """Number of heteromeric (both partners are different polymeric entities) interface entities"""
        return Attribute('rcsb_assembly_info.num_heteromeric_interface_entities')
    @property
    def num_homomeric_interface_entities(self) -> Attribute:
        """Number of homomeric (both partners are the same polymeric entity) interface entities"""
        return Attribute('rcsb_assembly_info.num_homomeric_interface_entities')
    @property
    def num_interface_entities(self) -> Attribute:
        """Number of polymer-polymer interface entities, grouping equivalent interfaces at the entity level (i.e. same entity_ids on either side, with similar but not identical binding sites)"""
        return Attribute('rcsb_assembly_info.num_interface_entities')
    @property
    def num_interfaces(self) -> Attribute:
        """Number of geometrically equivalent (i.e. same asym_ids on either side) polymer-polymer interfaces in the assembly"""
        return Attribute('rcsb_assembly_info.num_interfaces')
    @property
    def num_isologous_interface_entities(self) -> Attribute:
        """Number of isologous (both binding sites are same, i.e. interface is symmetric) interface entities"""
        return Attribute('rcsb_assembly_info.num_isologous_interface_entities')
    @property
    def num_na_interface_entities(self) -> Attribute:
        """Number of nucleic acid-nucleic acid interface entities"""
        return Attribute('rcsb_assembly_info.num_na_interface_entities')
    @property
    def num_prot_na_interface_entities(self) -> Attribute:
        """Number of protein-nucleic acid interface entities"""
        return Attribute('rcsb_assembly_info.num_prot_na_interface_entities')
    @property
    def num_protein_interface_entities(self) -> Attribute:
        """Number of protein-protein interface entities"""
        return Attribute('rcsb_assembly_info.num_protein_interface_entities')
    @property
    def polymer_atom_count(self) -> Attribute:
        """The assembly non-hydrogen polymer entity atomic coordinate count."""
        return Attribute('rcsb_assembly_info.polymer_atom_count')
    @property
    def polymer_composition(self) -> Attribute:
        """Categories describing the polymer entity composition for the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_composition')
    @property
    def polymer_entity_count(self) -> Attribute:
        """The number of distinct polymer entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_entity_count')
    @property
    def polymer_entity_count_DNA(self) -> Attribute:
        """The number of distinct DNA polymer entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_entity_count_DNA')
    @property
    def polymer_entity_count_RNA(self) -> Attribute:
        """The number of distinct RNA polymer entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_entity_count_RNA')
    @property
    def polymer_entity_count_nucleic_acid(self) -> Attribute:
        """The number of distinct nucleic acid polymer entities (DNA or RNA) in the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_entity_count_nucleic_acid')
    @property
    def polymer_entity_count_nucleic_acid_hybrid(self) -> Attribute:
        """The number of distinct hybrid nucleic acid polymer entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_entity_count_nucleic_acid_hybrid')
    @property
    def polymer_entity_count_protein(self) -> Attribute:
        """The number of distinct protein polymer entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.polymer_entity_count_protein')
    @property
    def polymer_entity_instance_count(self) -> Attribute:
        """The number of polymer instances in the generated assembly data set.  This is the total count of polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_entity_instance_count')
    @property
    def polymer_entity_instance_count_DNA(self) -> Attribute:
        """The number of DNA polymer instances in the generated assembly data set.  This is the total count of DNA polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_entity_instance_count_DNA')
    @property
    def polymer_entity_instance_count_RNA(self) -> Attribute:
        """The number of RNA polymer instances in the generated assembly data set.  This is the total count of RNA polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_entity_instance_count_RNA')
    @property
    def polymer_entity_instance_count_nucleic_acid(self) -> Attribute:
        """The number of nucleic acid polymer instances in the generated assembly data set.  This is the total count of nucleic acid polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_entity_instance_count_nucleic_acid')
    @property
    def polymer_entity_instance_count_nucleic_acid_hybrid(self) -> Attribute:
        """The number of hybrid nucleic acide polymer instances in the generated assembly data set.  This is the total count of hybrid nucleic acid polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_entity_instance_count_nucleic_acid_hybrid')
    @property
    def polymer_entity_instance_count_protein(self) -> Attribute:
        """The number of protein polymer instances in the generated assembly data set.  This is the total count of protein polymer entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_entity_instance_count_protein')
    @property
    def polymer_monomer_count(self) -> Attribute:
        """The number of polymer monomers in sample entity instances comprising the assembly data set.  This is the total count of monomers for all polymer entity instances  in the generated assembly coordinate data."""
        return Attribute('rcsb_assembly_info.polymer_monomer_count')
    @property
    def selected_polymer_entity_types(self) -> Attribute:
        """Selected polymer entity type categories describing the generated assembly."""
        return Attribute('rcsb_assembly_info.selected_polymer_entity_types')
    @property
    def solvent_atom_count(self) -> Attribute:
        """The assembly non-hydrogen solvent atomic coordinate count."""
        return Attribute('rcsb_assembly_info.solvent_atom_count')
    @property
    def solvent_entity_count(self) -> Attribute:
        """The number of distinct solvent entities in the generated assembly."""
        return Attribute('rcsb_assembly_info.solvent_entity_count')
    @property
    def solvent_entity_instance_count(self) -> Attribute:
        """The number of solvent instances in the generated assembly data set.  This is the total count of solvent entity instances generated in the assembly coordinate data."""
        return Attribute('rcsb_assembly_info.solvent_entity_instance_count')
    @property
    def total_assembly_buried_surface_area(self) -> Attribute:
        """Total buried surface area calculated as the sum of buried surface areas over all interfaces"""
        return Attribute('rcsb_assembly_info.total_assembly_buried_surface_area')
    @property
    def total_number_interface_residues(self) -> Attribute:
        """Total number of interfacing residues in the assembly, calculated as the sum of interfacing residues over all interfaces"""
        return Attribute('rcsb_assembly_info.total_number_interface_residues')
    @property
    def unmodeled_polymer_monomer_count(self) -> Attribute:
        """The number of unmodeled polymer monomers in the assembly coordinate data. This is  the total count of monomers with unreported coordinate data for all polymer  entity instances in the generated assembly coordinate data."""
        return Attribute('rcsb_assembly_info.unmodeled_polymer_monomer_count')

class Attr_RotationAxes_8376306879268672656:
    """Specifies a single or multiple rotation axes through the same point."""
    @property
    def end(self) -> Attribute:
        """Describes x,y,z coordinates of the end point of the symmetry axis."""
        return Attribute('rcsb_struct_symmetry.rotation_axes.end')
    @property
    def order(self) -> Attribute:
        """The number of times (order of rotation) that a subunit can be repeated by a rotation operation,  being transformed into a new state indistinguishable from its starting state."""
        return Attribute('rcsb_struct_symmetry.rotation_axes.order')
    @property
    def start(self) -> Attribute:
        """Describes x,y,z coordinates of the start point of the symmetry axis."""
        return Attribute('rcsb_struct_symmetry.rotation_axes.start')

class Attr_Members_309511982544221353:
    """"""
    @property
    def asym_id(self) -> Attribute:
        """Internal chain ID used in mmCIF files to uniquely identify structural elements in the asymmetric unit."""
        return Attribute('rcsb_struct_symmetry.clusters.members.asym_id')
    @property
    def pdbx_struct_oper_list_ids(self) -> Attribute:
        """Optional list of operator ids (pdbx_struct_oper_list.id) as appears in pdbx_struct_assembly_gen.oper_expression."""
        return Attribute('rcsb_struct_symmetry.clusters.members.pdbx_struct_oper_list_ids')

class Attr_Clusters_5851386465324518275:
    """Clusters describe grouping of identical subunits."""
    @property
    def members(self) -> 'Attr_Members_309511982544221353':
        """"""
        return Attr_Members_309511982544221353()
    @property
    def avg_rmsd(self) -> Attribute:
        """Average RMSD between members of a given cluster."""
        return Attribute('rcsb_struct_symmetry.clusters.avg_rmsd')

class Attr_RcsbStructSymmetry_2000709393001487832:
    """"""
    @property
    def kind(self) -> Attribute:
        """The granularity at which the symmetry calculation is performed. In 'Global Symmetry' all polymeric  subunits in assembly are used. In 'Local Symmetry' only a subset of polymeric subunits is considered.  In 'Pseudo Symmetry' the threshold for subunits similarity is relaxed."""
        return Attribute('rcsb_struct_symmetry.kind')
    @property
    def oligomeric_state(self) -> Attribute:
        """Oligomeric state refers to a composition of polymeric subunits in quaternary structure.  Quaternary structure may be composed either exclusively of several copies of identical subunits,  in which case they are termed homo-oligomers, or alternatively by at least one copy of different  subunits (hetero-oligomers). Quaternary structure composed of a single subunit is denoted as 'Monomer'."""
        return Attribute('rcsb_struct_symmetry.oligomeric_state')
    @property
    def stoichiometry(self) -> Attribute:
        """"""
        return Attribute('rcsb_struct_symmetry.stoichiometry')
    @property
    def symbol(self) -> Attribute:
        """Symmetry symbol refers to point group or helical symmetry of identical polymeric subunits in Schoenflies notation.  Contains point group symbol (e.g., C2, C5, D2, T, O, I) or H for helical symmetry."""
        return Attribute('rcsb_struct_symmetry.symbol')
    @property
    def type(self) -> Attribute:
        """Symmetry type refers to point group or helical symmetry of identical polymeric subunits.  Contains point group types (e.g. Cyclic, Dihedral) or Helical for helical symmetry."""
        return Attribute('rcsb_struct_symmetry.type')
    @property
    def rotation_axes(self) -> 'Attr_RotationAxes_8376306879268672656':
        """Specifies a single or multiple rotation axes through the same point."""
        return Attr_RotationAxes_8376306879268672656()
    @property
    def clusters(self) -> 'Attr_Clusters_5851386465324518275':
        """Clusters describe grouping of identical subunits."""
        return Attr_Clusters_5851386465324518275()

class Attr_RcsbStructSymmetryLineage_9092103971171207111:
    """"""
    @property
    def depth(self) -> Attribute:
        """Hierarchy depth."""
        return Attribute('rcsb_struct_symmetry_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Automatically assigned ID to uniquely identify the symmetry term in the Protein Symmetry Browser."""
        return Attribute('rcsb_struct_symmetry_lineage.id')
    @property
    def name(self) -> Attribute:
        """A human-readable term describing protein symmetry."""
        return Attribute('rcsb_struct_symmetry_lineage.name')

class Attr_RcsbRepositoryHoldingsCurrent_1988663083059252371:
    """"""
    @property
    def repository_content_types(self) -> Attribute:
        """"""
        return Attribute('rcsb_repository_holdings_current.repository_content_types')

class Attr_RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers_168164911212486505:
    """"""
    @property
    def assembly_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_repository_holdings_current_entry_container_identifiers.assembly_ids')
    @property
    def entry_id(self) -> Attribute:
        """The PDB entry accession code."""
        return Attribute('rcsb_repository_holdings_current_entry_container_identifiers.entry_id')
    @property
    def rcsb_id(self) -> Attribute:
        """The RCSB entry identifier."""
        return Attribute('rcsb_repository_holdings_current_entry_container_identifiers.rcsb_id')
    @property
    def update_id(self) -> Attribute:
        """Identifier for the current data exchange status record."""
        return Attribute('rcsb_repository_holdings_current_entry_container_identifiers.update_id')

class Attr_PdbxStructSpecialSymmetry_6715667423544602245:
    """"""
    @property
    def PDB_model_num(self) -> Attribute:
        """Part of the identifier for the molecular component.  This data item is a pointer to _atom_site.pdbx_PDB_model_num in the ATOM_SITE category."""
        return Attribute('pdbx_struct_special_symmetry.PDB_model_num')
    @property
    def auth_seq_id(self) -> Attribute:
        """Part of the identifier for the molecular component.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
        return Attribute('pdbx_struct_special_symmetry.auth_seq_id')
    @property
    def id(self) -> Attribute:
        """The value of _pdbx_struct_special_symmetry.id must uniquely identify  each item in the PDBX_STRUCT_SPECIAL_SYMMETRY list.   This is an integer serial number."""
        return Attribute('pdbx_struct_special_symmetry.id')
    @property
    def label_asym_id(self) -> Attribute:
        """Part of the identifier for the molecular component.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('pdbx_struct_special_symmetry.label_asym_id')
    @property
    def label_comp_id(self) -> Attribute:
        """Part of the identifier for the molecular component.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('pdbx_struct_special_symmetry.label_comp_id')

class Attr_PdbxVrptSummaryEntityFitToMap_7730038269615328452:
    """"""
    @property
    def PDB_model_num(self) -> Attribute:
        """The unique model number from _atom_site.pdbx_PDB_model_num."""
        return Attribute('pdbx_vrpt_summary_entity_fit_to_map.PDB_model_num')
    @property
    def Q_score(self) -> Attribute:
        """The calculated average Q-score."""
        return Attribute('pdbx_vrpt_summary_entity_fit_to_map.Q_score')
    @property
    def average_residue_inclusion(self) -> Attribute:
        """The average of the residue inclusions for all residues in this instance"""
        return Attribute('pdbx_vrpt_summary_entity_fit_to_map.average_residue_inclusion')

class Attr_PdbxVrptSummaryEntityGeometry_3714083458255245184:
    """"""
    @property
    def PDB_model_num(self) -> Attribute:
        """The unique model number from _atom_site.pdbx_PDB_model_num."""
        return Attribute('pdbx_vrpt_summary_entity_geometry.PDB_model_num')
    @property
    def angles_RMSZ(self) -> Attribute:
        """The overall root mean square of the Z-score for deviations of bond angles in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
        return Attribute('pdbx_vrpt_summary_entity_geometry.angles_RMSZ')
    @property
    def average_residue_inclusion(self) -> Attribute:
        """The average of the residue inclusions for all residues in this instance"""
        return Attribute('pdbx_vrpt_summary_entity_geometry.average_residue_inclusion')
    @property
    def bonds_RMSZ(self) -> Attribute:
        """The overall root mean square of the Z-score for deviations of bond lengths in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
        return Attribute('pdbx_vrpt_summary_entity_geometry.bonds_RMSZ')
    @property
    def num_angles_RMSZ(self) -> Attribute:
        """The number of bond angles compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
        return Attribute('pdbx_vrpt_summary_entity_geometry.num_angles_RMSZ')
    @property
    def num_bonds_RMSZ(self) -> Attribute:
        """The number of bond lengths compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
        return Attribute('pdbx_vrpt_summary_entity_geometry.num_bonds_RMSZ')

class Attr_RcsbNonpolymerEntityInstanceContainerIdentifiers_5240252078881992651:
    """"""
    @property
    def asym_id(self) -> Attribute:
        """Instance identifier for this container."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.asym_id')
    @property
    def auth_asym_id(self) -> Attribute:
        """Author instance identifier for this container."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.auth_asym_id')
    @property
    def auth_seq_id(self) -> Attribute:
        """Residue number for non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.auth_seq_id')
    @property
    def comp_id(self) -> Attribute:
        """Component identifier for non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.comp_id')
    @property
    def entity_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.entity_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.entry_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers."""
        return Attribute('rcsb_nonpolymer_entity_instance_container_identifiers.rcsb_id')

class Attr_AnnotationLineage_4537629850036046226:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_nonpolymer_instance_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_nonpolymer_instance_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_nonpolymer_instance_annotation.annotation_lineage.name')

class Attr_RcsbNonpolymerInstanceAnnotation_3768354779221868650:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_nonpolymer_instance_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_nonpolymer_instance_annotation.assignment_version')
    @property
    def comp_id(self) -> Attribute:
        """Non-polymer (ligand) chemical component identifier."""
        return Attribute('rcsb_nonpolymer_instance_annotation.comp_id')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_nonpolymer_instance_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_nonpolymer_instance_annotation.name')
    @property
    def ordinal(self) -> Attribute:
        """Ordinal identifier for this category"""
        return Attribute('rcsb_nonpolymer_instance_annotation.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_nonpolymer_instance_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_nonpolymer_instance_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_4537629850036046226':
        """"""
        return Attr_AnnotationLineage_4537629850036046226()

class Attr_FeatureValue_2693606835878920674:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """The chemical component identifier for the instance of the feature value."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_value.comp_id')
    @property
    def details(self) -> Attribute:
        """Specific details about the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_value.details')
    @property
    def reference(self) -> Attribute:
        """The reference value of the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_value.reference')
    @property
    def reported(self) -> Attribute:
        """The reported value of the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_value.reported')
    @property
    def uncertainty_estimate(self) -> Attribute:
        """The estimated uncertainty of the reported feature value."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_value.uncertainty_estimate')
    @property
    def uncertainty_estimate_type(self) -> Attribute:
        """The type of estimated uncertainty for the reported feature value."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_value.uncertainty_estimate_type')

class Attr_AdditionalProperties_1627917150522780559:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_nonpolymer_instance_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_nonpolymer_instance_feature.additional_properties.values')

class Attr_RcsbNonpolymerInstanceFeature_3192278488326817956:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_nonpolymer_instance_feature.assignment_version')
    @property
    def comp_id(self) -> Attribute:
        """Component identifier for non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_feature.comp_id')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.name')
    @property
    def ordinal(self) -> Attribute:
        """Ordinal identifier for this category"""
        return Attribute('rcsb_nonpolymer_instance_feature.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature.type')
    @property
    def feature_value(self) -> 'Attr_FeatureValue_2693606835878920674':
        """"""
        return Attr_FeatureValue_2693606835878920674()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_1627917150522780559':
        """"""
        return Attr_AdditionalProperties_1627917150522780559()

class Attr_RcsbNonpolymerInstanceFeatureSummary_2371206104525972356:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """Component identifier for non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.comp_id')
    @property
    def count(self) -> Attribute:
        """The feature count."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.count')
    @property
    def coverage(self) -> Attribute:
        """The fractional feature coverage relative to the full entity sequence."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.coverage')
    @property
    def maximum_length(self) -> Attribute:
        """The maximum feature length."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.maximum_length')
    @property
    def maximum_value(self) -> Attribute:
        """The maximum feature value."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.maximum_value')
    @property
    def minimum_length(self) -> Attribute:
        """The minimum feature length."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.minimum_length')
    @property
    def minimum_value(self) -> Attribute:
        """The minimum feature value."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.minimum_value')
    @property
    def type(self) -> Attribute:
        """Type or category of the feature."""
        return Attribute('rcsb_nonpolymer_instance_feature_summary.type')

class Attr_RcsbNonpolymerInstanceValidationScore_2590341230540896038:
    """"""
    @property
    def RSCC(self) -> Attribute:
        """The real space correlation coefficient (RSCC) for the non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.RSCC')
    @property
    def RSR(self) -> Attribute:
        """The real space R-value (RSR) for the non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.RSR')
    @property
    def alt_id(self) -> Attribute:
        """Alternate conformer identifier for the non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.alt_id')
    @property
    def average_occupancy(self) -> Attribute:
        """The average heavy atom occupancy for coordinate records for the non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.average_occupancy')
    @property
    def completeness(self) -> Attribute:
        """The reported fraction of atomic coordinate records for the non-polymer entity instance."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.completeness')
    @property
    def intermolecular_clashes(self) -> Attribute:
        """The number of intermolecular MolProbity clashes cacluated for reported atomic coordinate records."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.intermolecular_clashes')
    @property
    def is_best_instance(self) -> Attribute:
        """This molecular instance is ranked as the best quality instance of this nonpolymer entity."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.is_best_instance')
    @property
    def is_subject_of_investigation(self) -> Attribute:
        """This molecular entity is identified as the subject of the current study."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.is_subject_of_investigation')
    @property
    def is_subject_of_investigation_provenance(self) -> Attribute:
        """The provenance for the selection of the molecular entity identified as the subject of the current study."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.is_subject_of_investigation_provenance')
    @property
    def mogul_angle_outliers(self) -> Attribute:
        """Number of bond angle outliers obtained from a CCDC Mogul survey of bond angles  in the CSD small    molecule crystal structure database. Outliers are defined as bond angles that have a Z-score    less than -2 or greater than 2."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.mogul_angle_outliers')
    @property
    def mogul_angles_RMSZ(self) -> Attribute:
        """The root-mean-square value of the Z-scores of bond angles for the non-polymer instance in degrees obtained from a CCDC Mogul survey of bond angles in the CSD small molecule crystal structure database."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.mogul_angles_RMSZ')
    @property
    def mogul_bond_outliers(self) -> Attribute:
        """Number of bond distance outliers obtained from a CCDC Mogul survey of bond lengths in the CSD small    molecule crystal structure database.  Outliers are defined as bond distances that have a Z-score    less than -2 or greater than 2."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.mogul_bond_outliers')
    @property
    def mogul_bonds_RMSZ(self) -> Attribute:
        """The root-mean-square value of the Z-scores of bond lengths for the nonpolymer instance in Angstroms obtained from a CCDC Mogul survey of bond lengths in the CSD small molecule crystal structure database."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.mogul_bonds_RMSZ')
    @property
    def natoms_eds(self) -> Attribute:
        """The number of atoms in the non-polymer instance returned by the EDS software."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.natoms_eds')
    @property
    def num_mogul_angles_RMSZ(self) -> Attribute:
        """The number of bond angles compared to 'standard geometry' made using the Mogul program."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.num_mogul_angles_RMSZ')
    @property
    def num_mogul_bonds_RMSZ(self) -> Attribute:
        """The number of bond lengths compared to 'standard geometry' made using the Mogul program."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.num_mogul_bonds_RMSZ')
    @property
    def ranking_model_fit(self) -> Attribute:
        """The ranking of the model fit score component."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.ranking_model_fit')
    @property
    def ranking_model_geometry(self) -> Attribute:
        """The ranking of the model geometry score component."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.ranking_model_geometry')
    @property
    def score_model_fit(self) -> Attribute:
        """The value of the model fit score component."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.score_model_fit')
    @property
    def score_model_geometry(self) -> Attribute:
        """The value of the model geometry score component."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.score_model_geometry')
    @property
    def stereo_outliers(self) -> Attribute:
        """Number of stereochemical/chirality errors."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.stereo_outliers')
    @property
    def type(self) -> Attribute:
        """Score type."""
        return Attribute('rcsb_nonpolymer_instance_validation_score.type')

class Attr_ConnectTarget_8205355186666445722:
    """"""
    @property
    def auth_asym_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.auth_asym_id')
    @property
    def auth_seq_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.auth_seq_id')
    @property
    def label_alt_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.label_alt_id')
    @property
    def label_asym_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.label_asym_id')
    @property
    def label_atom_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_atom_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.label_atom_id')
    @property
    def label_comp_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.label_comp_id')
    @property
    def label_seq_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.connect_target_label_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.label_seq_id')
    @property
    def symmetry(self) -> Attribute:
        """Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_nonpolymer_struct_conn.label* to generate the  target of the structure connection."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_target.symmetry')

class Attr_ConnectPartner_4074903831780207623:
    """"""
    @property
    def label_alt_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_partner.label_alt_id')
    @property
    def label_asym_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_partner.label_asym_id')
    @property
    def label_atom_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _chem_comp_atom.atom_id in the  CHEM_COMP_ATOM category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_partner.label_atom_id')
    @property
    def label_comp_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_partner.label_comp_id')
    @property
    def label_seq_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_partner.label_seq_id')
    @property
    def symmetry(self) -> Attribute:
        """Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_nonpolymer_struct_conn.connect_partner_label* to generate the  partner in the structure connection."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_partner.symmetry')

class Attr_RcsbNonpolymerStructConn_1709108760528740593:
    """"""
    @property
    def connect_type(self) -> Attribute:
        """The connection type."""
        return Attribute('rcsb_nonpolymer_struct_conn.connect_type')
    @property
    def description(self) -> Attribute:
        """A description of special details of the connection."""
        return Attribute('rcsb_nonpolymer_struct_conn.description')
    @property
    def dist_value(self) -> Attribute:
        """Distance value for this contact."""
        return Attribute('rcsb_nonpolymer_struct_conn.dist_value')
    @property
    def id(self) -> Attribute:
        """The value of _rcsb_nonpolymer_struct_conn.id is an identifier for connection.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('rcsb_nonpolymer_struct_conn.id')
    @property
    def ordinal_id(self) -> Attribute:
        """The value of _rcsb_nonpolymer_struct_conn.id must uniquely identify a record in  the rcsb_nonpolymer_struct_conn list."""
        return Attribute('rcsb_nonpolymer_struct_conn.ordinal_id')
    @property
    def role(self) -> Attribute:
        """The chemical or structural role of the interaction"""
        return Attribute('rcsb_nonpolymer_struct_conn.role')
    @property
    def value_order(self) -> Attribute:
        """The chemical bond order associated with the specified atoms in  this contact."""
        return Attribute('rcsb_nonpolymer_struct_conn.value_order')
    @property
    def connect_target(self) -> 'Attr_ConnectTarget_8205355186666445722':
        """"""
        return Attr_ConnectTarget_8205355186666445722()
    @property
    def connect_partner(self) -> 'Attr_ConnectPartner_4074903831780207623':
        """"""
        return Attr_ConnectPartner_4074903831780207623()

class Attr_RcsbTargetNeighbors_1731505614121248038:
    """"""
    @property
    def alt_id(self) -> Attribute:
        """Alternate conformer identifier for the non-polymer entity instance."""
        return Attribute('rcsb_target_neighbors.alt_id')
    @property
    def atom_id(self) -> Attribute:
        """The atom identifier for the non-polymer entity instance."""
        return Attribute('rcsb_target_neighbors.atom_id')
    @property
    def comp_id(self) -> Attribute:
        """Component identifier for the non-polymer entity instance."""
        return Attribute('rcsb_target_neighbors.comp_id')
    @property
    def distance(self) -> Attribute:
        """Distance value for this target interaction."""
        return Attribute('rcsb_target_neighbors.distance')
    @property
    def target_asym_id(self) -> Attribute:
        """The entity instance identifier for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_asym_id')
    @property
    def target_atom_id(self) -> Attribute:
        """The atom identifier for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_atom_id')
    @property
    def target_auth_seq_id(self) -> Attribute:
        """The author residue index for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_auth_seq_id')
    @property
    def target_comp_id(self) -> Attribute:
        """The chemical component identifier for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_comp_id')
    @property
    def target_entity_id(self) -> Attribute:
        """The entity identifier for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_entity_id')
    @property
    def target_is_bound(self) -> Attribute:
        """A flag to indicate the nature of the target interaction is covalent or metal-coordination."""
        return Attribute('rcsb_target_neighbors.target_is_bound')
    @property
    def target_model_id(self) -> Attribute:
        """Model identifier for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_model_id')
    @property
    def target_seq_id(self) -> Attribute:
        """The sequence position for the target of interaction."""
        return Attribute('rcsb_target_neighbors.target_seq_id')

class Attr_StructAsym_8770235843712827894:
    """"""
    @property
    def pdbx_PDB_id(self) -> Attribute:
        """This data item is a pointer to _atom_site.pdbx_PDB_strand_id the  ATOM_SITE category."""
        return Attribute('struct_asym.pdbx_PDB_id')
    @property
    def pdbx_alt_id(self) -> Attribute:
        """This data item is a pointer to _atom_site.ndb_alias_strand_id the  ATOM_SITE category."""
        return Attribute('struct_asym.pdbx_alt_id')
    @property
    def pdbx_order(self) -> Attribute:
        """This data item gives the order of the structural elements in the  ATOM_SITE category."""
        return Attribute('struct_asym.pdbx_order')
    @property
    def pdbx_type(self) -> Attribute:
        """This data item describes the general type of the structural elements  in the ATOM_SITE category."""
        return Attribute('struct_asym.pdbx_type')

class Attr_ReferenceSequenceIdentifiers_8267042051166864156:
    """"""
    @property
    def database_accession(self) -> Attribute:
        """Reference database accession code"""
        return Attribute('rcsb_uniprot_container_identifiers.reference_sequence_identifiers.database_accession')
    @property
    def database_isoform(self) -> Attribute:
        """Reference database identifier for the sequence isoform"""
        return Attribute('rcsb_uniprot_container_identifiers.reference_sequence_identifiers.database_isoform')
    @property
    def database_name(self) -> Attribute:
        """Reference database name"""
        return Attribute('rcsb_uniprot_container_identifiers.reference_sequence_identifiers.database_name')
    @property
    def provenance_source(self) -> Attribute:
        """Source of the reference database assignment"""
        return Attribute('rcsb_uniprot_container_identifiers.reference_sequence_identifiers.provenance_source')

class Attr_RcsbUniprotContainerIdentifiers_2055158671997989571:
    """"""
    @property
    def uniprot_id(self) -> Attribute:
        """Primary accession number of a given UniProtKB entry."""
        return Attribute('rcsb_uniprot_container_identifiers.uniprot_id')
    @property
    def reference_sequence_identifiers(self) -> 'Attr_ReferenceSequenceIdentifiers_8267042051166864156':
        """"""
        return Attr_ReferenceSequenceIdentifiers_8267042051166864156()

class Attr_RcsbUniprotKeyword_5702066830568654507:
    """Keywords constitute a controlled vocabulary that summarises the content of a UniProtKB entry."""
    @property
    def id(self) -> Attribute:
        """A unique keyword identifier."""
        return Attribute('rcsb_uniprot_keyword.id')
    @property
    def value(self) -> Attribute:
        """Human-readable keyword term."""
        return Attribute('rcsb_uniprot_keyword.value')

class Attr_Name_9188208751305316669:
    """"""
    @property
    def value(self) -> Attribute:
        """Name that allows to unambiguously identify a protein."""
        return Attribute('rcsb_uniprot_protein.name.value')
    @property
    def provenance_code(self) -> Attribute:
        """Historical record of the data attribute."""
        return Attribute('rcsb_uniprot_protein.name.provenance_code')

class Attr_Function_5076563990201906989:
    """"""
    @property
    def details(self) -> Attribute:
        """General function(s) of a protein."""
        return Attribute('rcsb_uniprot_protein.function.details')
    @property
    def provenance_code(self) -> Attribute:
        """Historical record of the data attribute."""
        return Attribute('rcsb_uniprot_protein.function.provenance_code')

class Attr_Name_4784258142180370537:
    """"""
    @property
    def type(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_protein.gene.name.type')
    @property
    def value(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_protein.gene.name.value')

class Attr_Gene_2851943022508815399:
    """"""
    @property
    def name(self) -> 'Attr_Name_4784258142180370537':
        """"""
        return Attr_Name_4784258142180370537()

class Attr_SourceOrganism_1012876817757968594:
    """Taxonomy information on the organism that is the source of the protein sequence."""
    @property
    def scientific_name(self) -> Attribute:
        """The scientific name of the organism in which a protein occurs."""
        return Attribute('rcsb_uniprot_protein.source_organism.scientific_name')
    @property
    def taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the organism in which a protein occurs."""
        return Attribute('rcsb_uniprot_protein.source_organism.taxonomy_id')
    @property
    def provenance_code(self) -> Attribute:
        """Historical record of the data attribute."""
        return Attribute('rcsb_uniprot_protein.source_organism.provenance_code')

class Attr_Ec_1917243136632730572:
    """"""
    @property
    def number(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_protein.ec.number')
    @property
    def provenance_code(self) -> Attribute:
        """Historical record of the data attribute."""
        return Attribute('rcsb_uniprot_protein.ec.provenance_code')

class Attr_RcsbUniprotProtein_1148492260866263344:
    """"""
    @property
    def sequence(self) -> Attribute:
        """Protein sequence data for canonical protein sequence."""
        return Attribute('rcsb_uniprot_protein.sequence')
    @property
    def name(self) -> 'Attr_Name_9188208751305316669':
        """"""
        return Attr_Name_9188208751305316669()
    @property
    def function(self) -> 'Attr_Function_5076563990201906989':
        """"""
        return Attr_Function_5076563990201906989()
    @property
    def gene(self) -> 'Attr_Gene_2851943022508815399':
        """"""
        return Attr_Gene_2851943022508815399()
    @property
    def source_organism(self) -> 'Attr_SourceOrganism_1012876817757968594':
        """Taxonomy information on the organism that is the source of the protein sequence."""
        return Attr_SourceOrganism_1012876817757968594()
    @property
    def ec(self) -> 'Attr_Ec_1917243136632730572':
        """"""
        return Attr_Ec_1917243136632730572()

class Attr_FeaturePositions_1319380549849587427:
    """"""
    @property
    def beg_comp_id(self) -> Attribute:
        """An identifier for the monomer(s) corresponding to the feature assignment."""
        return Attribute('rcsb_uniprot_feature.feature_positions.beg_comp_id')
    @property
    def beg_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature begins."""
        return Attribute('rcsb_uniprot_feature.feature_positions.beg_seq_id')
    @property
    def end_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature ends."""
        return Attribute('rcsb_uniprot_feature.feature_positions.end_seq_id')
    @property
    def value(self) -> Attribute:
        """The value for the feature over this monomer segment."""
        return Attribute('rcsb_uniprot_feature.feature_positions.value')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_feature.feature_positions.values')

class Attr_RcsbUniprotFeature_1881409233569800478:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_uniprot_feature.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_uniprot_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_uniprot_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_uniprot_feature.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_uniprot_feature.provenance_source')
    @property
    def reference_scheme(self) -> Attribute:
        """Code residue coordinate system for the assigned feature."""
        return Attribute('rcsb_uniprot_feature.reference_scheme')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_uniprot_feature.type')
    @property
    def feature_positions(self) -> 'Attr_FeaturePositions_1319380549849587427':
        """"""
        return Attr_FeaturePositions_1319380549849587427()

class Attr_AnnotationLineage_3962192906542633922:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_uniprot_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_uniprot_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_uniprot_annotation.annotation_lineage.name')

class Attr_AdditionalProperties_1390711903636955532:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name"""
        return Attribute('rcsb_uniprot_annotation.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_annotation.additional_properties.values')

class Attr_RcsbUniprotAnnotation_3803643403302486016:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_uniprot_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_uniprot_annotation.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_uniprot_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_uniprot_annotation.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_uniprot_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_uniprot_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_3962192906542633922':
        """"""
        return Attr_AnnotationLineage_3962192906542633922()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_1390711903636955532':
        """"""
        return Attr_AdditionalProperties_1390711903636955532()

class Attr_RcsbUniprotExternalReference_2403504378685336846:
    """"""
    @property
    def reference_id(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_external_reference.reference_id')
    @property
    def reference_name(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_external_reference.reference_name')
    @property
    def provenance_source(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_external_reference.provenance_source')

class Attr_Scores_3951673443276478389:
    """Alignment scores"""
    @property
    def target_coverage(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.scores.target_coverage')
    @property
    def query_coverage(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.scores.query_coverage')
    @property
    def target_length(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.scores.target_length')
    @property
    def query_length(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.scores.query_length')

class Attr_AlignedRegions_5046294652337776940:
    """Aligned sequence regions"""
    @property
    def target_begin(self) -> Attribute:
        """NCBI sequence start position"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.aligned_regions.target_begin')
    @property
    def query_begin(self) -> Attribute:
        """Entity seqeunce start position"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.aligned_regions.query_begin')
    @property
    def length(self) -> Attribute:
        """Aligned region length"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.aligned_regions.length')

class Attr_CoreEntityIdentifiers_7465926911781943972:
    """core_entity identifiers"""
    @property
    def entry_id(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.core_entity_identifiers.entry_id')
    @property
    def entity_id(self) -> Attribute:
        """"""
        return Attribute('rcsb_uniprot_alignments.core_entity_alignments.core_entity_identifiers.entity_id')

class Attr_CoreEntityAlignments_7692768742489313423:
    """List of alignments with core_entity canonical sequences"""
    @property
    def scores(self) -> 'Attr_Scores_3951673443276478389':
        """Alignment scores"""
        return Attr_Scores_3951673443276478389()
    @property
    def aligned_regions(self) -> 'Attr_AlignedRegions_5046294652337776940':
        """Aligned sequence regions"""
        return Attr_AlignedRegions_5046294652337776940()
    @property
    def core_entity_identifiers(self) -> 'Attr_CoreEntityIdentifiers_7465926911781943972':
        """core_entity identifiers"""
        return Attr_CoreEntityIdentifiers_7465926911781943972()

class Attr_RcsbUniprotAlignments_2406293443920110804:
    """UniProt pairwise sequence alignments."""
    @property
    def core_entity_alignments(self) -> 'Attr_CoreEntityAlignments_7692768742489313423':
        """List of alignments with core_entity canonical sequences"""
        return Attr_CoreEntityAlignments_7692768742489313423()

class Attr_RcsbBranchedEntityInstanceContainerIdentifiers_2861184413435366569:
    """"""
    @property
    def asym_id(self) -> Attribute:
        """Instance identifier for this container."""
        return Attribute('rcsb_branched_entity_instance_container_identifiers.asym_id')
    @property
    def auth_asym_id(self) -> Attribute:
        """Author instance identifier for this container."""
        return Attribute('rcsb_branched_entity_instance_container_identifiers.auth_asym_id')
    @property
    def entity_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_branched_entity_instance_container_identifiers.entity_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_branched_entity_instance_container_identifiers.entry_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers."""
        return Attribute('rcsb_branched_entity_instance_container_identifiers.rcsb_id')

class Attr_AnnotationLineage_7435108368706229753:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_branched_instance_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_branched_instance_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_branched_instance_annotation.annotation_lineage.name')

class Attr_RcsbBranchedInstanceAnnotation_672822815378712341:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_branched_instance_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_branched_instance_annotation.assignment_version')
    @property
    def comp_id(self) -> Attribute:
        """Chemical component identifier."""
        return Attribute('rcsb_branched_instance_annotation.comp_id')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_branched_instance_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_branched_instance_annotation.name')
    @property
    def ordinal(self) -> Attribute:
        """Ordinal identifier for this category"""
        return Attribute('rcsb_branched_instance_annotation.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_branched_instance_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_branched_instance_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_7435108368706229753':
        """"""
        return Attr_AnnotationLineage_7435108368706229753()

class Attr_FeaturePositions_2116051832006189682:
    """"""
    @property
    def beg_comp_id(self) -> Attribute:
        """An identifier for the monomer(s) corresponding to the feature assignment."""
        return Attribute('rcsb_branched_instance_feature.feature_positions.beg_comp_id')
    @property
    def beg_seq_id(self) -> Attribute:
        """An identifier for the leading monomer feature position."""
        return Attribute('rcsb_branched_instance_feature.feature_positions.beg_seq_id')
    @property
    def end_seq_id(self) -> Attribute:
        """An identifier for the terminal monomer feature position."""
        return Attribute('rcsb_branched_instance_feature.feature_positions.end_seq_id')
    @property
    def value(self) -> Attribute:
        """The value of the feature at the monomer position."""
        return Attribute('rcsb_branched_instance_feature.feature_positions.value')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_branched_instance_feature.feature_positions.values')

class Attr_FeatureValue_8910873802041013118:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """The chemical component identifier for the instance of the feature value."""
        return Attribute('rcsb_branched_instance_feature.feature_value.comp_id')
    @property
    def details(self) -> Attribute:
        """Specific details about the feature."""
        return Attribute('rcsb_branched_instance_feature.feature_value.details')
    @property
    def reference(self) -> Attribute:
        """The reference value of the feature."""
        return Attribute('rcsb_branched_instance_feature.feature_value.reference')
    @property
    def reported(self) -> Attribute:
        """The reported value of the feature."""
        return Attribute('rcsb_branched_instance_feature.feature_value.reported')
    @property
    def uncertainty_estimate(self) -> Attribute:
        """The estimated uncertainty of the reported feature value."""
        return Attribute('rcsb_branched_instance_feature.feature_value.uncertainty_estimate')
    @property
    def uncertainty_estimate_type(self) -> Attribute:
        """The type of estimated uncertainty for the reported feature value."""
        return Attribute('rcsb_branched_instance_feature.feature_value.uncertainty_estimate_type')

class Attr_AdditionalProperties_2620266861902529283:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_branched_instance_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_branched_instance_feature.additional_properties.values')

class Attr_RcsbBranchedInstanceFeature_6570529883936783032:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_branched_instance_feature.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_branched_instance_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_branched_instance_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_branched_instance_feature.name')
    @property
    def ordinal(self) -> Attribute:
        """Ordinal identifier for this category"""
        return Attribute('rcsb_branched_instance_feature.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_branched_instance_feature.provenance_source')
    @property
    def reference_scheme(self) -> Attribute:
        """Code residue coordinate system for the assigned feature."""
        return Attribute('rcsb_branched_instance_feature.reference_scheme')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_branched_instance_feature.type')
    @property
    def feature_positions(self) -> 'Attr_FeaturePositions_2116051832006189682':
        """"""
        return Attr_FeaturePositions_2116051832006189682()
    @property
    def feature_value(self) -> 'Attr_FeatureValue_8910873802041013118':
        """"""
        return Attr_FeatureValue_8910873802041013118()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_2620266861902529283':
        """"""
        return Attr_AdditionalProperties_2620266861902529283()

class Attr_RcsbBranchedInstanceFeatureSummary_6073811527940749640:
    """"""
    @property
    def count(self) -> Attribute:
        """The feature count."""
        return Attribute('rcsb_branched_instance_feature_summary.count')
    @property
    def coverage(self) -> Attribute:
        """The fractional feature coverage relative to the full branched entity."""
        return Attribute('rcsb_branched_instance_feature_summary.coverage')
    @property
    def maximum_length(self) -> Attribute:
        """The maximum feature length."""
        return Attribute('rcsb_branched_instance_feature_summary.maximum_length')
    @property
    def maximum_value(self) -> Attribute:
        """The maximum feature value."""
        return Attribute('rcsb_branched_instance_feature_summary.maximum_value')
    @property
    def minimum_length(self) -> Attribute:
        """The minimum feature length."""
        return Attribute('rcsb_branched_instance_feature_summary.minimum_length')
    @property
    def minimum_value(self) -> Attribute:
        """The minimum feature value."""
        return Attribute('rcsb_branched_instance_feature_summary.minimum_value')
    @property
    def type(self) -> Attribute:
        """Type or category of the feature."""
        return Attribute('rcsb_branched_instance_feature_summary.type')

class Attr_ConnectTarget_6692907946124029965:
    """"""
    @property
    def auth_asym_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.auth_asym_id')
    @property
    def auth_seq_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.auth_seq_id')
    @property
    def label_alt_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.label_alt_id')
    @property
    def label_asym_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.label_asym_id')
    @property
    def label_atom_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_atom_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.label_atom_id')
    @property
    def label_comp_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.label_comp_id')
    @property
    def label_seq_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.connect_target_label_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_target.label_seq_id')
    @property
    def symmetry(self) -> Attribute:
        """Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_branched_struct_conn.label* to generate the  target of the structure connection."""
        return Attribute('rcsb_branched_struct_conn.connect_target.symmetry')

class Attr_ConnectPartner_2543372445541924727:
    """"""
    @property
    def label_alt_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_partner.label_alt_id')
    @property
    def label_asym_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_partner.label_asym_id')
    @property
    def label_atom_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _chem_comp_atom.atom_id in the  CHEM_COMP_ATOM category."""
        return Attribute('rcsb_branched_struct_conn.connect_partner.label_atom_id')
    @property
    def label_comp_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_partner.label_comp_id')
    @property
    def label_seq_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_branched_struct_conn.connect_partner.label_seq_id')
    @property
    def symmetry(self) -> Attribute:
        """Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_branched_struct_conn.connect_partner_label* to generate the  partner in the structure connection."""
        return Attribute('rcsb_branched_struct_conn.connect_partner.symmetry')

class Attr_RcsbBranchedStructConn_6003569928516495413:
    """"""
    @property
    def connect_type(self) -> Attribute:
        """The connection type."""
        return Attribute('rcsb_branched_struct_conn.connect_type')
    @property
    def description(self) -> Attribute:
        """A description of special details of the connection."""
        return Attribute('rcsb_branched_struct_conn.description')
    @property
    def dist_value(self) -> Attribute:
        """Distance value for this contact."""
        return Attribute('rcsb_branched_struct_conn.dist_value')
    @property
    def id(self) -> Attribute:
        """The value of _rcsb_branched_struct_conn.id is an identifier for connection."""
        return Attribute('rcsb_branched_struct_conn.id')
    @property
    def ordinal_id(self) -> Attribute:
        """The value of _rcsb_branched_struct_conn.id must uniquely identify a record in  the rcsb_branched_struct_conn list."""
        return Attribute('rcsb_branched_struct_conn.ordinal_id')
    @property
    def role(self) -> Attribute:
        """The chemical or structural role of the interaction"""
        return Attribute('rcsb_branched_struct_conn.role')
    @property
    def value_order(self) -> Attribute:
        """The chemical bond order associated with the specified atoms in  this contact."""
        return Attribute('rcsb_branched_struct_conn.value_order')
    @property
    def connect_target(self) -> 'Attr_ConnectTarget_6692907946124029965':
        """"""
        return Attr_ConnectTarget_6692907946124029965()
    @property
    def connect_partner(self) -> 'Attr_ConnectPartner_2543372445541924727':
        """"""
        return Attr_ConnectPartner_2543372445541924727()

class Attr_RcsbLigandNeighbors_1880587839048653220:
    """"""
    @property
    def alt_id(self) -> Attribute:
        """Alternate conformer identifier for the target instance."""
        return Attribute('rcsb_ligand_neighbors.alt_id')
    @property
    def atom_id(self) -> Attribute:
        """The atom identifier for the target instance."""
        return Attribute('rcsb_ligand_neighbors.atom_id')
    @property
    def auth_seq_id(self) -> Attribute:
        """The author residue index for the target instance."""
        return Attribute('rcsb_ligand_neighbors.auth_seq_id')
    @property
    def comp_id(self) -> Attribute:
        """Component identifier for the target instance."""
        return Attribute('rcsb_ligand_neighbors.comp_id')
    @property
    def distance(self) -> Attribute:
        """Distance value for this ligand interaction."""
        return Attribute('rcsb_ligand_neighbors.distance')
    @property
    def ligand_alt_id(self) -> Attribute:
        """Alternate conformer identifier for the ligand interaction."""
        return Attribute('rcsb_ligand_neighbors.ligand_alt_id')
    @property
    def ligand_asym_id(self) -> Attribute:
        """The entity instance identifier for the ligand interaction."""
        return Attribute('rcsb_ligand_neighbors.ligand_asym_id')
    @property
    def ligand_atom_id(self) -> Attribute:
        """The atom identifier for the ligand interaction."""
        return Attribute('rcsb_ligand_neighbors.ligand_atom_id')
    @property
    def ligand_comp_id(self) -> Attribute:
        """The chemical component identifier for the ligand interaction."""
        return Attribute('rcsb_ligand_neighbors.ligand_comp_id')
    @property
    def ligand_entity_id(self) -> Attribute:
        """The entity identifier for the ligand of interaction."""
        return Attribute('rcsb_ligand_neighbors.ligand_entity_id')
    @property
    def ligand_is_bound(self) -> Attribute:
        """A flag to indicate the nature of the ligand interaction is covalent or metal-coordination."""
        return Attribute('rcsb_ligand_neighbors.ligand_is_bound')
    @property
    def ligand_model_id(self) -> Attribute:
        """Model identifier for the ligand interaction."""
        return Attribute('rcsb_ligand_neighbors.ligand_model_id')
    @property
    def seq_id(self) -> Attribute:
        """The sequence position for the target instance."""
        return Attribute('rcsb_ligand_neighbors.seq_id')

class Attr_PdbxEntityBranch_6585698773760777520:
    """"""
    @property
    def rcsb_branched_component_count(self) -> Attribute:
        """Number of constituent chemical components in the branched entity."""
        return Attribute('pdbx_entity_branch.rcsb_branched_component_count')
    @property
    def type(self) -> Attribute:
        """The type of this branched oligosaccharide."""
        return Attribute('pdbx_entity_branch.type')

class Attr_PdbxEntityBranchDescriptor_164054067697101551:
    """"""
    @property
    def descriptor(self) -> Attribute:
        """This data item contains the descriptor value for this  entity."""
        return Attribute('pdbx_entity_branch_descriptor.descriptor')
    @property
    def program(self) -> Attribute:
        """This data item contains the name of the program  or library used to compute the descriptor."""
        return Attribute('pdbx_entity_branch_descriptor.program')
    @property
    def program_version(self) -> Attribute:
        """This data item contains the version of the program  or library used to compute the descriptor."""
        return Attribute('pdbx_entity_branch_descriptor.program_version')
    @property
    def type(self) -> Attribute:
        """This data item contains the descriptor type."""
        return Attribute('pdbx_entity_branch_descriptor.type')

class Attr_RcsbBranchedEntity_7127345435010229726:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the branched entity."""
        return Attribute('rcsb_branched_entity.details')
    @property
    def formula_weight(self) -> Attribute:
        """Formula mass (KDa) of the branched entity."""
        return Attribute('rcsb_branched_entity.formula_weight')
    @property
    def pdbx_description(self) -> Attribute:
        """A description of the branched entity."""
        return Attribute('rcsb_branched_entity.pdbx_description')
    @property
    def pdbx_number_of_molecules(self) -> Attribute:
        """The number of molecules of the branched entity in the entry."""
        return Attribute('rcsb_branched_entity.pdbx_number_of_molecules')

class Attr_AnnotationLineage_2594584768469439962:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_branched_entity_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_branched_entity_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_branched_entity_annotation.annotation_lineage.name')

class Attr_RcsbBranchedEntityAnnotation_7897611392574466247:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_branched_entity_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_branched_entity_annotation.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_branched_entity_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_branched_entity_annotation.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_branched_entity_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_branched_entity_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_2594584768469439962':
        """"""
        return Attr_AnnotationLineage_2594584768469439962()

class Attr_ReferenceIdentifiers_2304801728374397635:
    """"""
    @property
    def provenance_source(self) -> Attribute:
        """Source of the reference resource assignment"""
        return Attribute('rcsb_branched_entity_container_identifiers.reference_identifiers.provenance_source')
    @property
    def resource_accession(self) -> Attribute:
        """Reference resource accession code"""
        return Attribute('rcsb_branched_entity_container_identifiers.reference_identifiers.resource_accession')
    @property
    def resource_name(self) -> Attribute:
        """Reference resource name"""
        return Attribute('rcsb_branched_entity_container_identifiers.reference_identifiers.resource_name')

class Attr_RcsbBranchedEntityContainerIdentifiers_2702156472399669336:
    """"""
    @property
    def asym_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_branched_entity_container_identifiers.asym_ids')
    @property
    def auth_asym_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_branched_entity_container_identifiers.auth_asym_ids')
    @property
    def chem_comp_monomers(self) -> Attribute:
        """"""
        return Attribute('rcsb_branched_entity_container_identifiers.chem_comp_monomers')
    @property
    def chem_ref_def_id(self) -> Attribute:
        """The chemical reference definition identifier for the entity in this container."""
        return Attribute('rcsb_branched_entity_container_identifiers.chem_ref_def_id')
    @property
    def entity_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_branched_entity_container_identifiers.entity_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_branched_entity_container_identifiers.entry_id')
    @property
    def prd_id(self) -> Attribute:
        """The BIRD identifier for the entity in this container."""
        return Attribute('rcsb_branched_entity_container_identifiers.prd_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers."""
        return Attribute('rcsb_branched_entity_container_identifiers.rcsb_id')
    @property
    def reference_identifiers(self) -> 'Attr_ReferenceIdentifiers_2304801728374397635':
        """"""
        return Attr_ReferenceIdentifiers_2304801728374397635()

class Attr_FeaturePositions_251460226936398238:
    """"""
    @property
    def beg_comp_id(self) -> Attribute:
        """An identifier for the leading monomer corresponding to the feature assignment."""
        return Attribute('rcsb_branched_entity_feature.feature_positions.beg_comp_id')
    @property
    def beg_seq_id(self) -> Attribute:
        """An identifier for the leading monomer position of the feature."""
        return Attribute('rcsb_branched_entity_feature.feature_positions.beg_seq_id')
    @property
    def end_seq_id(self) -> Attribute:
        """An identifier for the leading monomer position of the feature."""
        return Attribute('rcsb_branched_entity_feature.feature_positions.end_seq_id')
    @property
    def value(self) -> Attribute:
        """The value for the feature at this monomer."""
        return Attribute('rcsb_branched_entity_feature.feature_positions.value')

class Attr_AdditionalProperties_6281207833623426560:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_branched_entity_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_branched_entity_feature.additional_properties.values')

class Attr_RcsbBranchedEntityFeature_1505102972707174718:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_branched_entity_feature.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_branched_entity_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_branched_entity_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_branched_entity_feature.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_branched_entity_feature.provenance_source')
    @property
    def reference_scheme(self) -> Attribute:
        """Code residue coordinate system for the assigned feature."""
        return Attribute('rcsb_branched_entity_feature.reference_scheme')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_branched_entity_feature.type')
    @property
    def feature_positions(self) -> 'Attr_FeaturePositions_251460226936398238':
        """"""
        return Attr_FeaturePositions_251460226936398238()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_6281207833623426560':
        """"""
        return Attr_AdditionalProperties_6281207833623426560()

class Attr_RcsbBranchedEntityFeatureSummary_8620054670851748367:
    """"""
    @property
    def count(self) -> Attribute:
        """The feature count."""
        return Attribute('rcsb_branched_entity_feature_summary.count')
    @property
    def coverage(self) -> Attribute:
        """The fractional feature coverage relative to the full branched entity."""
        return Attribute('rcsb_branched_entity_feature_summary.coverage')
    @property
    def maximum_length(self) -> Attribute:
        """The maximum feature length."""
        return Attribute('rcsb_branched_entity_feature_summary.maximum_length')
    @property
    def maximum_value(self) -> Attribute:
        """The maximum feature value."""
        return Attribute('rcsb_branched_entity_feature_summary.maximum_value')
    @property
    def minimum_length(self) -> Attribute:
        """The minimum feature length."""
        return Attribute('rcsb_branched_entity_feature_summary.minimum_length')
    @property
    def minimum_value(self) -> Attribute:
        """The minimum feature value."""
        return Attribute('rcsb_branched_entity_feature_summary.minimum_value')
    @property
    def type(self) -> Attribute:
        """Type or category of the feature."""
        return Attribute('rcsb_branched_entity_feature_summary.type')

class Attr_RcsbBranchedEntityKeywords_7809048164391685214:
    """"""
    @property
    def text(self) -> Attribute:
        """Keywords describing this branched entity."""
        return Attribute('rcsb_branched_entity_keywords.text')

class Attr_RcsbBranchedEntityNameCom_6713474324205697671:
    """"""
    @property
    def name(self) -> Attribute:
        """A common name for the branched entity."""
        return Attribute('rcsb_branched_entity_name_com.name')

class Attr_RcsbBranchedEntityNameSys_2316662242913320166:
    """"""
    @property
    def name(self) -> Attribute:
        """The systematic name for the branched entity."""
        return Attribute('rcsb_branched_entity_name_sys.name')
    @property
    def system(self) -> Attribute:
        """The system used to generate the systematic name of the branched entity."""
        return Attribute('rcsb_branched_entity_name_sys.system')

class Attr_RcsbPolymerEntityInstanceContainerIdentifiers_4117279514301415360:
    """"""
    @property
    def asym_id(self) -> Attribute:
        """Instance identifier for this container."""
        return Attribute('rcsb_polymer_entity_instance_container_identifiers.asym_id')
    @property
    def auth_asym_id(self) -> Attribute:
        """Author instance identifier for this container."""
        return Attribute('rcsb_polymer_entity_instance_container_identifiers.auth_asym_id')
    @property
    def auth_to_entity_poly_seq_mapping(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_instance_container_identifiers.auth_to_entity_poly_seq_mapping')
    @property
    def entity_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_polymer_entity_instance_container_identifiers.entity_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_polymer_entity_instance_container_identifiers.entry_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers."""
        return Attribute('rcsb_polymer_entity_instance_container_identifiers.rcsb_id')

class Attr_AnnotationLineage_8973475768845617756:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_polymer_instance_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_polymer_instance_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_polymer_instance_annotation.annotation_lineage.name')

class Attr_RcsbPolymerInstanceAnnotation_2474965843387619093:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_polymer_instance_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_polymer_instance_annotation.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_polymer_instance_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_polymer_instance_annotation.name')
    @property
    def ordinal(self) -> Attribute:
        """Ordinal identifier for this category"""
        return Attribute('rcsb_polymer_instance_annotation.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_polymer_instance_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_polymer_instance_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_8973475768845617756':
        """"""
        return Attr_AnnotationLineage_8973475768845617756()

class Attr_FeaturePositions_279501591416285509:
    """"""
    @property
    def beg_comp_id(self) -> Attribute:
        """An identifier for the monomer(s) corresponding to the feature assignment."""
        return Attribute('rcsb_polymer_instance_feature.feature_positions.beg_comp_id')
    @property
    def beg_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature begins."""
        return Attribute('rcsb_polymer_instance_feature.feature_positions.beg_seq_id')
    @property
    def end_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature ends."""
        return Attribute('rcsb_polymer_instance_feature.feature_positions.end_seq_id')
    @property
    def value(self) -> Attribute:
        """The value of the feature over the monomer segment."""
        return Attribute('rcsb_polymer_instance_feature.feature_positions.value')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_instance_feature.feature_positions.values')

class Attr_AdditionalProperties_7096152205969120873:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_polymer_instance_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_instance_feature.additional_properties.values')

class Attr_RcsbPolymerInstanceFeature_4606921343215410585:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_polymer_instance_feature.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_polymer_instance_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_polymer_instance_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_polymer_instance_feature.name')
    @property
    def ordinal(self) -> Attribute:
        """Ordinal identifier for this category"""
        return Attribute('rcsb_polymer_instance_feature.ordinal')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_polymer_instance_feature.provenance_source')
    @property
    def reference_scheme(self) -> Attribute:
        """Code residue coordinate system for the assigned feature."""
        return Attribute('rcsb_polymer_instance_feature.reference_scheme')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_polymer_instance_feature.type')
    @property
    def feature_positions(self) -> 'Attr_FeaturePositions_279501591416285509':
        """"""
        return Attr_FeaturePositions_279501591416285509()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_7096152205969120873':
        """"""
        return Attr_AdditionalProperties_7096152205969120873()

class Attr_RcsbPolymerInstanceFeatureSummary_6516870355967066808:
    """"""
    @property
    def count(self) -> Attribute:
        """The feature count per polymer chain."""
        return Attribute('rcsb_polymer_instance_feature_summary.count')
    @property
    def coverage(self) -> Attribute:
        """The fractional feature coverage relative to the full entity sequence."""
        return Attribute('rcsb_polymer_instance_feature_summary.coverage')
    @property
    def maximum_length(self) -> Attribute:
        """The maximum feature length."""
        return Attribute('rcsb_polymer_instance_feature_summary.maximum_length')
    @property
    def maximum_value(self) -> Attribute:
        """The maximum feature value."""
        return Attribute('rcsb_polymer_instance_feature_summary.maximum_value')
    @property
    def minimum_length(self) -> Attribute:
        """The minimum feature length."""
        return Attribute('rcsb_polymer_instance_feature_summary.minimum_length')
    @property
    def minimum_value(self) -> Attribute:
        """The minimum feature value."""
        return Attribute('rcsb_polymer_instance_feature_summary.minimum_value')
    @property
    def type(self) -> Attribute:
        """Type or category of the feature."""
        return Attribute('rcsb_polymer_instance_feature_summary.type')

class Attr_RcsbPolymerInstanceInfo_2673440109957145241:
    """"""
    @property
    def modeled_residue_count(self) -> Attribute:
        """The number of modeled residues in the polymer instance."""
        return Attribute('rcsb_polymer_instance_info.modeled_residue_count')

class Attr_ConnectTarget_5271257635113228474:
    """"""
    @property
    def auth_asym_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.auth_asym_id')
    @property
    def auth_seq_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.auth_seq_id')
    @property
    def label_alt_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.label_alt_id')
    @property
    def label_asym_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.label_asym_id')
    @property
    def label_atom_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_atom_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.label_atom_id')
    @property
    def label_comp_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.label_comp_id')
    @property
    def label_seq_id(self) -> Attribute:
        """A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.connect_target_label_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.label_seq_id')
    @property
    def symmetry(self) -> Attribute:
        """Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_polymer_struct_conn.label* to generate the  target of the structure connection."""
        return Attribute('rcsb_polymer_struct_conn.connect_target.symmetry')

class Attr_ConnectPartner_1078810037029767524:
    """"""
    @property
    def label_alt_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_partner.label_alt_id')
    @property
    def label_asym_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_partner.label_asym_id')
    @property
    def label_atom_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _chem_comp_atom.atom_id in the  CHEM_COMP_ATOM category."""
        return Attribute('rcsb_polymer_struct_conn.connect_partner.label_atom_id')
    @property
    def label_comp_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_partner.label_comp_id')
    @property
    def label_seq_id(self) -> Attribute:
        """A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_seq_id in the  ATOM_SITE category."""
        return Attribute('rcsb_polymer_struct_conn.connect_partner.label_seq_id')
    @property
    def symmetry(self) -> Attribute:
        """Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_polymer_struct_conn.connect_partner_label* to generate the  partner in the structure connection."""
        return Attribute('rcsb_polymer_struct_conn.connect_partner.symmetry')

class Attr_RcsbPolymerStructConn_7021313551494511902:
    """"""
    @property
    def connect_type(self) -> Attribute:
        """The connection type."""
        return Attribute('rcsb_polymer_struct_conn.connect_type')
    @property
    def description(self) -> Attribute:
        """A description of special details of the connection."""
        return Attribute('rcsb_polymer_struct_conn.description')
    @property
    def dist_value(self) -> Attribute:
        """Distance value for this contact."""
        return Attribute('rcsb_polymer_struct_conn.dist_value')
    @property
    def id(self) -> Attribute:
        """The value of _rcsb_polymer_struct_conn.id is an identifier for connection.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('rcsb_polymer_struct_conn.id')
    @property
    def ordinal_id(self) -> Attribute:
        """The value of _rcsb_polymer_struct_conn.id must uniquely identify a record in  the rcsb_polymer_struct_conn list."""
        return Attribute('rcsb_polymer_struct_conn.ordinal_id')
    @property
    def role(self) -> Attribute:
        """The chemical or structural role of the interaction"""
        return Attribute('rcsb_polymer_struct_conn.role')
    @property
    def value_order(self) -> Attribute:
        """The chemical bond order associated with the specified atoms in  this contact."""
        return Attribute('rcsb_polymer_struct_conn.value_order')
    @property
    def connect_target(self) -> 'Attr_ConnectTarget_5271257635113228474':
        """"""
        return Attr_ConnectTarget_5271257635113228474()
    @property
    def connect_partner(self) -> 'Attr_ConnectPartner_1078810037029767524':
        """"""
        return Attr_ConnectPartner_1078810037029767524()

class Attr_AuditAuthor_62427880465664534:
    """"""
    @property
    def identifier_ORCID(self) -> Attribute:
        """The Open Researcher and Contributor ID (ORCID)."""
        return Attribute('audit_author.identifier_ORCID')
    @property
    def name(self) -> Attribute:
        """The name of an author of this data block. If there are multiple  authors, _audit_author.name is looped with _audit_author.address.  The family name(s), followed by a comma and including any  dynastic components, precedes the first name(s) or initial(s)."""
        return Attribute('audit_author.name')
    @property
    def pdbx_ordinal(self) -> Attribute:
        """This data item defines the order of the author's name in the  list of audit authors."""
        return Attribute('audit_author.pdbx_ordinal')

class Attr_Cell_8152123297833183303:
    """"""
    @property
    def Z_PDB(self) -> Attribute:
        """The number of the polymeric chains in a unit cell. In the case  of heteropolymers, Z is the number of occurrences of the most  populous chain.   This data item is provided for compatibility with the original  Protein Data Bank format, and only for that purpose."""
        return Attribute('cell.Z_PDB')
    @property
    def angle_alpha(self) -> Attribute:
        """Unit-cell angle alpha of the reported structure in degrees."""
        return Attribute('cell.angle_alpha')
    @property
    def angle_beta(self) -> Attribute:
        """Unit-cell angle beta of the reported structure in degrees."""
        return Attribute('cell.angle_beta')
    @property
    def angle_gamma(self) -> Attribute:
        """Unit-cell angle gamma of the reported structure in degrees."""
        return Attribute('cell.angle_gamma')
    @property
    def formula_units_Z(self) -> Attribute:
        """The number of the formula units in the unit cell as specified  by _chemical_formula.structural, _chemical_formula.moiety or  _chemical_formula.sum."""
        return Attribute('cell.formula_units_Z')
    @property
    def length_a(self) -> Attribute:
        """Unit-cell length a corresponding to the structure reported in angstroms."""
        return Attribute('cell.length_a')
    @property
    def length_b(self) -> Attribute:
        """Unit-cell length b corresponding to the structure reported in  angstroms."""
        return Attribute('cell.length_b')
    @property
    def length_c(self) -> Attribute:
        """Unit-cell length c corresponding to the structure reported in angstroms."""
        return Attribute('cell.length_c')
    @property
    def pdbx_unique_axis(self) -> Attribute:
        """To further identify unique axis if necessary.  E.g., P 21 with  an unique C axis will have 'C' in this field."""
        return Attribute('cell.pdbx_unique_axis')
    @property
    def volume(self) -> Attribute:
        """Cell volume V in angstroms cubed.   V = a b c (1 - cos^2^~alpha~ - cos^2^~beta~ - cos^2^~gamma~             + 2 cos~alpha~ cos~beta~ cos~gamma~)^1/2^   a     = _cell.length_a  b     = _cell.length_b  c     = _cell.length_c  alpha = _cell.angle_alpha  beta  = _cell.angle_beta  gamma = _cell.angle_gamma"""
        return Attribute('cell.volume')

class Attr_Citation_1260406672264572138:
    """"""
    @property
    def book_id_ISBN(self) -> Attribute:
        """The International Standard Book Number (ISBN) code assigned to  the book cited; relevant for books or book chapters."""
        return Attribute('citation.book_id_ISBN')
    @property
    def book_publisher(self) -> Attribute:
        """The name of the publisher of the citation; relevant  for books or book chapters."""
        return Attribute('citation.book_publisher')
    @property
    def book_publisher_city(self) -> Attribute:
        """The location of the publisher of the citation; relevant  for books or book chapters."""
        return Attribute('citation.book_publisher_city')
    @property
    def book_title(self) -> Attribute:
        """The title of the book in which the citation appeared; relevant  for books or book chapters."""
        return Attribute('citation.book_title')
    @property
    def coordinate_linkage(self) -> Attribute:
        """_citation.coordinate_linkage states whether this citation  is concerned with precisely the set of coordinates given in the  data block. If, for instance, the publication described the same  structure, but the coordinates had undergone further refinement  prior to the creation of the data block, the value of this data  item would be 'no'."""
        return Attribute('citation.coordinate_linkage')
    @property
    def country(self) -> Attribute:
        """The country/region of publication; relevant for books  and book chapters."""
        return Attribute('citation.country')
    @property
    def id(self) -> Attribute:
        """The value of _citation.id must uniquely identify a record in the  CITATION list.   The _citation.id 'primary' should be used to indicate the  citation that the author(s) consider to be the most pertinent to  the contents of the data block.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('citation.id')
    @property
    def journal_abbrev(self) -> Attribute:
        """Abbreviated name of the cited journal as given in the  Chemical Abstracts Service Source Index."""
        return Attribute('citation.journal_abbrev')
    @property
    def journal_full(self) -> Attribute:
        """Full name of the cited journal; relevant for journal articles."""
        return Attribute('citation.journal_full')
    @property
    def journal_id_ASTM(self) -> Attribute:
        """The American Society for Testing and Materials (ASTM) code  assigned to the journal cited (also referred to as the CODEN  designator of the Chemical Abstracts Service); relevant for  journal articles."""
        return Attribute('citation.journal_id_ASTM')
    @property
    def journal_id_CSD(self) -> Attribute:
        """The Cambridge Structural Database (CSD) code assigned to the  journal cited; relevant for journal articles. This is also the  system used at the Protein Data Bank (PDB)."""
        return Attribute('citation.journal_id_CSD')
    @property
    def journal_id_ISSN(self) -> Attribute:
        """The International Standard Serial Number (ISSN) code assigned to  the journal cited; relevant for journal articles."""
        return Attribute('citation.journal_id_ISSN')
    @property
    def journal_issue(self) -> Attribute:
        """Issue number of the journal cited; relevant for journal  articles."""
        return Attribute('citation.journal_issue')
    @property
    def journal_volume(self) -> Attribute:
        """Volume number of the journal cited; relevant for journal  articles."""
        return Attribute('citation.journal_volume')
    @property
    def language(self) -> Attribute:
        """Language in which the cited article is written."""
        return Attribute('citation.language')
    @property
    def page_first(self) -> Attribute:
        """The first page of the citation; relevant for journal  articles, books and book chapters."""
        return Attribute('citation.page_first')
    @property
    def page_last(self) -> Attribute:
        """The last page of the citation; relevant for journal  articles, books and book chapters."""
        return Attribute('citation.page_last')
    @property
    def pdbx_database_id_DOI(self) -> Attribute:
        """Document Object Identifier used by doi.org to uniquely  specify bibliographic entry."""
        return Attribute('citation.pdbx_database_id_DOI')
    @property
    def pdbx_database_id_PubMed(self) -> Attribute:
        """Ascession number used by PubMed to categorize a specific  bibliographic entry."""
        return Attribute('citation.pdbx_database_id_PubMed')
    @property
    def rcsb_authors(self) -> Attribute:
        """"""
        return Attribute('citation.rcsb_authors')
    @property
    def rcsb_is_primary(self) -> Attribute:
        """Flag to indicate a primary citation."""
        return Attribute('citation.rcsb_is_primary')
    @property
    def rcsb_journal_abbrev(self) -> Attribute:
        """Normalized journal abbreviation."""
        return Attribute('citation.rcsb_journal_abbrev')
    @property
    def title(self) -> Attribute:
        """The title of the citation; relevant for journal articles, books  and book chapters."""
        return Attribute('citation.title')
    @property
    def unpublished_flag(self) -> Attribute:
        """Flag to indicate that this citation will not be published."""
        return Attribute('citation.unpublished_flag')
    @property
    def year(self) -> Attribute:
        """The year of the citation; relevant for journal articles, books  and book chapters."""
        return Attribute('citation.year')

class Attr_Database2_4588843887365885359:
    """"""
    @property
    def database_code(self) -> Attribute:
        """The code assigned by the database identified in  _database_2.database_id."""
        return Attribute('database_2.database_code')
    @property
    def database_id(self) -> Attribute:
        """An abbreviation that identifies the database."""
        return Attribute('database_2.database_id')
    @property
    def pdbx_DOI(self) -> Attribute:
        """Document Object Identifier (DOI) for this entry registered with http://crossref.org."""
        return Attribute('database_2.pdbx_DOI')
    @property
    def pdbx_database_accession(self) -> Attribute:
        """Extended accession code issued for for _database_2.database_code assigned by the database identified in  _database_2.database_id."""
        return Attribute('database_2.pdbx_database_accession')

class Attr_Diffrn_5561519300761882462:
    """"""
    @property
    def ambient_pressure(self) -> Attribute:
        """The mean hydrostatic pressure in kilopascals at which the  intensities were measured."""
        return Attribute('diffrn.ambient_pressure')
    @property
    def ambient_temp(self) -> Attribute:
        """The mean temperature in kelvins at which the intensities were  measured."""
        return Attribute('diffrn.ambient_temp')
    @property
    def ambient_temp_details(self) -> Attribute:
        """A description of special aspects of temperature control during  data collection."""
        return Attribute('diffrn.ambient_temp_details')
    @property
    def crystal_id(self) -> Attribute:
        """This data item is a pointer to _exptl_crystal.id in the  EXPTL_CRYSTAL category."""
        return Attribute('diffrn.crystal_id')
    @property
    def crystal_support(self) -> Attribute:
        """The physical device used to support the crystal during data  collection."""
        return Attribute('diffrn.crystal_support')
    @property
    def details(self) -> Attribute:
        """Special details of the diffraction measurement process. Should  include information about source instability, crystal motion,  degradation and so on."""
        return Attribute('diffrn.details')
    @property
    def id(self) -> Attribute:
        """This data item uniquely identifies a set of diffraction  data."""
        return Attribute('diffrn.id')
    @property
    def pdbx_serial_crystal_experiment(self) -> Attribute:
        """Y/N if using serial crystallography experiment in which multiple crystals contribute to each diffraction frame in the experiment."""
        return Attribute('diffrn.pdbx_serial_crystal_experiment')

class Attr_DiffrnDetector_540682412782732369:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the radiation detector."""
        return Attribute('diffrn_detector.details')
    @property
    def detector(self) -> Attribute:
        """The general class of the radiation detector."""
        return Attribute('diffrn_detector.detector')
    @property
    def diffrn_id(self) -> Attribute:
        """This data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('diffrn_detector.diffrn_id')
    @property
    def pdbx_collection_date(self) -> Attribute:
        """The date of data collection."""
        return Attribute('diffrn_detector.pdbx_collection_date')
    @property
    def pdbx_frequency(self) -> Attribute:
        """The operating frequency of the detector (Hz) used in data collection."""
        return Attribute('diffrn_detector.pdbx_frequency')
    @property
    def type(self) -> Attribute:
        """The make, model or name of the detector device used."""
        return Attribute('diffrn_detector.type')

class Attr_DiffrnRadiation_188986262919187256:
    """"""
    @property
    def collimation(self) -> Attribute:
        """The collimation or focusing applied to the radiation."""
        return Attribute('diffrn_radiation.collimation')
    @property
    def diffrn_id(self) -> Attribute:
        """This data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('diffrn_radiation.diffrn_id')
    @property
    def monochromator(self) -> Attribute:
        """The method used to obtain monochromatic radiation. If a mono-  chromator crystal is used, the material and the indices of the  Bragg reflection are specified."""
        return Attribute('diffrn_radiation.monochromator')
    @property
    def pdbx_diffrn_protocol(self) -> Attribute:
        """SINGLE WAVELENGTH, LAUE, or MAD."""
        return Attribute('diffrn_radiation.pdbx_diffrn_protocol')
    @property
    def pdbx_monochromatic_or_laue_m_l(self) -> Attribute:
        """Monochromatic or Laue."""
        return Attribute('diffrn_radiation.pdbx_monochromatic_or_laue_m_l')
    @property
    def pdbx_scattering_type(self) -> Attribute:
        """The radiation scattering type for this diffraction data set."""
        return Attribute('diffrn_radiation.pdbx_scattering_type')
    @property
    def pdbx_wavelength(self) -> Attribute:
        """Wavelength of radiation."""
        return Attribute('diffrn_radiation.pdbx_wavelength')
    @property
    def pdbx_wavelength_list(self) -> Attribute:
        """Comma separated list of wavelengths or wavelength range."""
        return Attribute('diffrn_radiation.pdbx_wavelength_list')
    @property
    def type(self) -> Attribute:
        """The nature of the radiation. This is typically a description  of the X-ray wavelength in Siegbahn notation."""
        return Attribute('diffrn_radiation.type')
    @property
    def wavelength_id(self) -> Attribute:
        """This data item is a pointer to _diffrn_radiation_wavelength.id  in the DIFFRN_RADIATION_WAVELENGTH category."""
        return Attribute('diffrn_radiation.wavelength_id')

class Attr_DiffrnSource_8609644499962653127:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the radiation source used."""
        return Attribute('diffrn_source.details')
    @property
    def diffrn_id(self) -> Attribute:
        """This data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('diffrn_source.diffrn_id')
    @property
    def pdbx_synchrotron_beamline(self) -> Attribute:
        """Synchrotron beamline."""
        return Attribute('diffrn_source.pdbx_synchrotron_beamline')
    @property
    def pdbx_synchrotron_site(self) -> Attribute:
        """Synchrotron site."""
        return Attribute('diffrn_source.pdbx_synchrotron_site')
    @property
    def pdbx_wavelength(self) -> Attribute:
        """Wavelength of radiation."""
        return Attribute('diffrn_source.pdbx_wavelength')
    @property
    def pdbx_wavelength_list(self) -> Attribute:
        """Comma separated list of wavelengths or wavelength range."""
        return Attribute('diffrn_source.pdbx_wavelength_list')
    @property
    def source(self) -> Attribute:
        """The general class of the radiation source."""
        return Attribute('diffrn_source.source')
    @property
    def type(self) -> Attribute:
        """The make, model or name of the source of radiation."""
        return Attribute('diffrn_source.type')

class Attr_Em2dCrystalEntity_5442783675105080567:
    """"""
    @property
    def angle_gamma(self) -> Attribute:
        """Unit-cell angle gamma in degrees."""
        return Attribute('em_2d_crystal_entity.angle_gamma')
    @property
    def c_sampling_length(self) -> Attribute:
        """Length used to sample the reciprocal lattice lines in the c-direction."""
        return Attribute('em_2d_crystal_entity.c_sampling_length')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_2d_crystal_entity.id')
    @property
    def image_processing_id(self) -> Attribute:
        """pointer to _em_image_processing.id in the EM_IMAGE_PROCESSING category."""
        return Attribute('em_2d_crystal_entity.image_processing_id')
    @property
    def length_a(self) -> Attribute:
        """Unit-cell length a in angstroms."""
        return Attribute('em_2d_crystal_entity.length_a')
    @property
    def length_b(self) -> Attribute:
        """Unit-cell length b in angstroms."""
        return Attribute('em_2d_crystal_entity.length_b')
    @property
    def length_c(self) -> Attribute:
        """Thickness of 2D crystal"""
        return Attribute('em_2d_crystal_entity.length_c')
    @property
    def space_group_name_H_M(self) -> Attribute:
        """There are 17 plane groups classified as oblique, rectangular, square, and hexagonal.  To describe the symmetry of 2D crystals of biological molecules,  plane groups are expanded to equivalent noncentrosymmetric space groups.  The 2D crystal plane corresponds to the 'ab' plane of the space group.   Enumerated space group descriptions include the plane group number in parentheses,  the H-M plane group symbol, and the plane group class."""
        return Attribute('em_2d_crystal_entity.space_group_name_H_M')

class Attr_Em3dCrystalEntity_362674572910326460:
    """"""
    @property
    def angle_alpha(self) -> Attribute:
        """Unit-cell angle alpha in degrees."""
        return Attribute('em_3d_crystal_entity.angle_alpha')
    @property
    def angle_beta(self) -> Attribute:
        """Unit-cell angle beta in degrees."""
        return Attribute('em_3d_crystal_entity.angle_beta')
    @property
    def angle_gamma(self) -> Attribute:
        """Unit-cell angle gamma in degrees."""
        return Attribute('em_3d_crystal_entity.angle_gamma')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_3d_crystal_entity.id')
    @property
    def image_processing_id(self) -> Attribute:
        """pointer to _em_image_processing.id in the EM_IMAGE_PROCESSING category."""
        return Attribute('em_3d_crystal_entity.image_processing_id')
    @property
    def length_a(self) -> Attribute:
        """Unit-cell length a in angstroms."""
        return Attribute('em_3d_crystal_entity.length_a')
    @property
    def length_b(self) -> Attribute:
        """Unit-cell length b in angstroms."""
        return Attribute('em_3d_crystal_entity.length_b')
    @property
    def length_c(self) -> Attribute:
        """Unit-cell length c in angstroms."""
        return Attribute('em_3d_crystal_entity.length_c')
    @property
    def space_group_name(self) -> Attribute:
        """Space group name."""
        return Attribute('em_3d_crystal_entity.space_group_name')
    @property
    def space_group_num(self) -> Attribute:
        """Space group number."""
        return Attribute('em_3d_crystal_entity.space_group_num')

class Attr_Em3dFitting_183403454660579888:
    """"""
    @property
    def details(self) -> Attribute:
        """Any additional details regarding fitting of atomic coordinates into  the 3DEM volume, including data and considerations from other  methods used in computation of the model."""
        return Attribute('em_3d_fitting.details')
    @property
    def id(self) -> Attribute:
        """The value of _em_3d_fitting.id must uniquely identify  a fitting procedure of atomic coordinates  into 3dem reconstructed map volume."""
        return Attribute('em_3d_fitting.id')
    @property
    def method(self) -> Attribute:
        """The method used to fit atomic coordinates  into the 3dem reconstructed map."""
        return Attribute('em_3d_fitting.method')
    @property
    def overall_b_value(self) -> Attribute:
        """The overall B (temperature factor) value for the 3d-em volume."""
        return Attribute('em_3d_fitting.overall_b_value')
    @property
    def ref_protocol(self) -> Attribute:
        """The refinement protocol used."""
        return Attribute('em_3d_fitting.ref_protocol')
    @property
    def ref_space(self) -> Attribute:
        """A flag to indicate whether fitting was carried out in real  or reciprocal refinement space."""
        return Attribute('em_3d_fitting.ref_space')
    @property
    def target_criteria(self) -> Attribute:
        """The measure used to assess quality of fit of the atomic coordinates in the  3DEM map volume."""
        return Attribute('em_3d_fitting.target_criteria')

class Attr_Em3dFittingList_2436868757309379014:
    """"""
    @property
    def em_3d_fitting_id(self) -> Attribute:
        """The value of _em_3d_fitting_list.3d_fitting_id is a pointer  to  _em_3d_fitting.id in the 3d_fitting category"""
        return Attribute('em_3d_fitting_list.3d_fitting_id')
    @property
    def details(self) -> Attribute:
        """Details about the model used in fitting."""
        return Attribute('em_3d_fitting_list.details')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_3d_fitting_list.id')
    @property
    def pdb_chain_id(self) -> Attribute:
        """The ID of the biopolymer chain used for fitting, e.g., A.  Please note that only one chain can be specified per instance.  If all chains of a particular structure have been used for fitting, this field can be left blank."""
        return Attribute('em_3d_fitting_list.pdb_chain_id')
    @property
    def pdb_chain_residue_range(self) -> Attribute:
        """Residue range for the identified chain."""
        return Attribute('em_3d_fitting_list.pdb_chain_residue_range')
    @property
    def pdb_entry_id(self) -> Attribute:
        """The PDB code for the entry used in fitting."""
        return Attribute('em_3d_fitting_list.pdb_entry_id')

class Attr_Em3dReconstruction_6962286487449101352:
    """"""
    @property
    def actual_pixel_size(self) -> Attribute:
        """The actual pixel size of the projection set of images in Angstroms."""
        return Attribute('em_3d_reconstruction.actual_pixel_size')
    @property
    def algorithm(self) -> Attribute:
        """The reconstruction algorithm/technique used to generate the map."""
        return Attribute('em_3d_reconstruction.algorithm')
    @property
    def details(self) -> Attribute:
        """Any additional details used in the 3d reconstruction."""
        return Attribute('em_3d_reconstruction.details')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_3d_reconstruction.id')
    @property
    def image_processing_id(self) -> Attribute:
        """Foreign key to the EM_IMAGE_PROCESSING category"""
        return Attribute('em_3d_reconstruction.image_processing_id')
    @property
    def magnification_calibration(self) -> Attribute:
        """The magnification calibration method for the 3d reconstruction."""
        return Attribute('em_3d_reconstruction.magnification_calibration')
    @property
    def method(self) -> Attribute:
        """The algorithm method used for the 3d-reconstruction."""
        return Attribute('em_3d_reconstruction.method')
    @property
    def nominal_pixel_size(self) -> Attribute:
        """The nominal pixel size of the projection set of images in Angstroms."""
        return Attribute('em_3d_reconstruction.nominal_pixel_size')
    @property
    def num_class_averages(self) -> Attribute:
        """The number of classes used in the final 3d reconstruction"""
        return Attribute('em_3d_reconstruction.num_class_averages')
    @property
    def num_particles(self) -> Attribute:
        """The number of 2D projections or 3D subtomograms used in the 3d reconstruction"""
        return Attribute('em_3d_reconstruction.num_particles')
    @property
    def refinement_type(self) -> Attribute:
        """Indicates details on how the half-map used for resolution determination (usually by FSC) have been generated."""
        return Attribute('em_3d_reconstruction.refinement_type')
    @property
    def resolution(self) -> Attribute:
        """The final resolution (in angstroms) of the 3D reconstruction."""
        return Attribute('em_3d_reconstruction.resolution')
    @property
    def resolution_method(self) -> Attribute:
        """The  method used to determine the final resolution  of the 3d reconstruction.  The Fourier Shell Correlation criterion as a measure of  resolution is based on the concept of splitting the (2D)  data set into two halves; averaging each and comparing them  using the Fourier Ring Correlation (FRC) technique."""
        return Attribute('em_3d_reconstruction.resolution_method')
    @property
    def symmetry_type(self) -> Attribute:
        """The type of symmetry applied to the reconstruction"""
        return Attribute('em_3d_reconstruction.symmetry_type')

class Attr_EmCtfCorrection_5430460427553524849:
    """"""
    @property
    def details(self) -> Attribute:
        """Any additional details about CTF correction"""
        return Attribute('em_ctf_correction.details')
    @property
    def em_image_processing_id(self) -> Attribute:
        """Foreign key to the EM_IMAGE_PROCESSING category"""
        return Attribute('em_ctf_correction.em_image_processing_id')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_ctf_correction.id')
    @property
    def type(self) -> Attribute:
        """Type of CTF correction applied"""
        return Attribute('em_ctf_correction.type')

class Attr_EmDiffraction_2470912780379215592:
    """"""
    @property
    def camera_length(self) -> Attribute:
        """The camera length (in millimeters). The camera length is the  product of the objective focal length and the combined magnification  of the intermediate and projector lenses when the microscope is  operated in the diffraction mode."""
        return Attribute('em_diffraction.camera_length')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_diffraction.id')
    @property
    def imaging_id(self) -> Attribute:
        """Foreign key to the EM_IMAGING category"""
        return Attribute('em_diffraction.imaging_id')
    @property
    def tilt_angle_list(self) -> Attribute:
        """Comma-separated list of tilt angles (in degrees) used in the electron diffraction experiment."""
        return Attribute('em_diffraction.tilt_angle_list')

class Attr_EmDiffractionShell_4934540720457196892:
    """"""
    @property
    def em_diffraction_stats_id(self) -> Attribute:
        """Pointer to EM CRYSTALLOGRAPHY STATS"""
        return Attribute('em_diffraction_shell.em_diffraction_stats_id')
    @property
    def fourier_space_coverage(self) -> Attribute:
        """Completeness of the structure factor data within this resolution shell, in percent"""
        return Attribute('em_diffraction_shell.fourier_space_coverage')
    @property
    def high_resolution(self) -> Attribute:
        """High resolution limit for this shell (angstroms)"""
        return Attribute('em_diffraction_shell.high_resolution')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_diffraction_shell.id')
    @property
    def low_resolution(self) -> Attribute:
        """Low resolution limit for this shell (angstroms)"""
        return Attribute('em_diffraction_shell.low_resolution')
    @property
    def multiplicity(self) -> Attribute:
        """Multiplicity (average number of measurements) for the structure factors in this resolution shell"""
        return Attribute('em_diffraction_shell.multiplicity')
    @property
    def num_structure_factors(self) -> Attribute:
        """Number of measured structure factors in this resolution shell"""
        return Attribute('em_diffraction_shell.num_structure_factors')
    @property
    def phase_residual(self) -> Attribute:
        """Phase residual for this resolution shell, in degrees"""
        return Attribute('em_diffraction_shell.phase_residual')

class Attr_EmDiffractionStats_4117859647005514778:
    """"""
    @property
    def details(self) -> Attribute:
        """Any addition details about the structure factor measurements"""
        return Attribute('em_diffraction_stats.details')
    @property
    def fourier_space_coverage(self) -> Attribute:
        """Completeness of the structure factor data within the defined space group  at the reported resolution (percent)."""
        return Attribute('em_diffraction_stats.fourier_space_coverage')
    @property
    def high_resolution(self) -> Attribute:
        """High resolution limit of the structure factor data, in angstroms"""
        return Attribute('em_diffraction_stats.high_resolution')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_diffraction_stats.id')
    @property
    def image_processing_id(self) -> Attribute:
        """Pointer to _em_image_processing.id"""
        return Attribute('em_diffraction_stats.image_processing_id')
    @property
    def num_intensities_measured(self) -> Attribute:
        """Total number of diffraction intensities measured (before averaging)"""
        return Attribute('em_diffraction_stats.num_intensities_measured')
    @property
    def num_structure_factors(self) -> Attribute:
        """Number of structure factors obtained (merged amplitudes + phases)"""
        return Attribute('em_diffraction_stats.num_structure_factors')
    @property
    def overall_phase_error(self) -> Attribute:
        """Overall phase error in degrees"""
        return Attribute('em_diffraction_stats.overall_phase_error')
    @property
    def overall_phase_residual(self) -> Attribute:
        """Overall phase residual in degrees"""
        return Attribute('em_diffraction_stats.overall_phase_residual')
    @property
    def phase_error_rejection_criteria(self) -> Attribute:
        """Criteria used to reject phases"""
        return Attribute('em_diffraction_stats.phase_error_rejection_criteria')
    @property
    def r_merge(self) -> Attribute:
        """Rmerge value (percent)"""
        return Attribute('em_diffraction_stats.r_merge')
    @property
    def r_sym(self) -> Attribute:
        """Rsym value (percent)"""
        return Attribute('em_diffraction_stats.r_sym')

class Attr_EmEmbedding_779734661784868619:
    """"""
    @property
    def details(self) -> Attribute:
        """Staining procedure used in the specimen preparation."""
        return Attribute('em_embedding.details')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_embedding.id')
    @property
    def material(self) -> Attribute:
        """The embedding  material."""
        return Attribute('em_embedding.material')
    @property
    def specimen_id(self) -> Attribute:
        """Foreign key relationship to the EM SPECIMEN category"""
        return Attribute('em_embedding.specimen_id')

class Attr_EmEntityAssembly_8629257542291011594:
    """"""
    @property
    def details(self) -> Attribute:
        """Additional details about the sample or sample subcomponent."""
        return Attribute('em_entity_assembly.details')
    @property
    def entity_id_list(self) -> Attribute:
        """"""
        return Attribute('em_entity_assembly.entity_id_list')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_entity_assembly.id')
    @property
    def name(self) -> Attribute:
        """The name of the sample or sample subcomponent."""
        return Attribute('em_entity_assembly.name')
    @property
    def oligomeric_details(self) -> Attribute:
        """oligomeric details"""
        return Attribute('em_entity_assembly.oligomeric_details')
    @property
    def parent_id(self) -> Attribute:
        """The parent of this assembly.  This data item is an internal category pointer to _em_entity_assembly.id.  By convention, the full assembly (top of hierarchy) is assigned parent id 0 (zero)."""
        return Attribute('em_entity_assembly.parent_id')
    @property
    def source(self) -> Attribute:
        """The type of source (e.g., natural source) for the component (sample or sample subcomponent)"""
        return Attribute('em_entity_assembly.source')
    @property
    def synonym(self) -> Attribute:
        """Alternative name of the component."""
        return Attribute('em_entity_assembly.synonym')
    @property
    def type(self) -> Attribute:
        """The general type of the sample or sample subcomponent."""
        return Attribute('em_entity_assembly.type')

class Attr_EmExperiment_7693395228713719246:
    """"""
    @property
    def aggregation_state(self) -> Attribute:
        """The aggregation/assembly state of the imaged specimen."""
        return Attribute('em_experiment.aggregation_state')
    @property
    def entity_assembly_id(self) -> Attribute:
        """Foreign key to the EM_ENTITY_ASSEMBLY category"""
        return Attribute('em_experiment.entity_assembly_id')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_experiment.id')
    @property
    def reconstruction_method(self) -> Attribute:
        """The reconstruction method used in the EM experiment."""
        return Attribute('em_experiment.reconstruction_method')

class Attr_EmHelicalEntity_179661736991184042:
    """"""
    @property
    def angular_rotation_per_subunit(self) -> Attribute:
        """The angular rotation per helical subunit in degrees. Negative values indicate left-handed helices; positive values indicate right handed helices."""
        return Attribute('em_helical_entity.angular_rotation_per_subunit')
    @property
    def axial_rise_per_subunit(self) -> Attribute:
        """The axial rise per subunit in the helical assembly."""
        return Attribute('em_helical_entity.axial_rise_per_subunit')
    @property
    def axial_symmetry(self) -> Attribute:
        """Symmetry of the helical axis, either cyclic (Cn) or dihedral (Dn), where n>=1."""
        return Attribute('em_helical_entity.axial_symmetry')
    @property
    def details(self) -> Attribute:
        """Any other details regarding the helical assembly"""
        return Attribute('em_helical_entity.details')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_helical_entity.id')
    @property
    def image_processing_id(self) -> Attribute:
        """This data item is a pointer to _em_image_processing.id."""
        return Attribute('em_helical_entity.image_processing_id')

class Attr_EmImageRecording_7369174113551656390:
    """"""
    @property
    def average_exposure_time(self) -> Attribute:
        """The average exposure time for each image."""
        return Attribute('em_image_recording.average_exposure_time')
    @property
    def avg_electron_dose_per_image(self) -> Attribute:
        """The electron dose received by the specimen per image (electrons per square angstrom)."""
        return Attribute('em_image_recording.avg_electron_dose_per_image')
    @property
    def details(self) -> Attribute:
        """Any additional details about image recording."""
        return Attribute('em_image_recording.details')
    @property
    def detector_mode(self) -> Attribute:
        """The detector mode used during image recording."""
        return Attribute('em_image_recording.detector_mode')
    @property
    def film_or_detector_model(self) -> Attribute:
        """The detector type used for recording images.  Usually film , CCD camera or direct electron detector."""
        return Attribute('em_image_recording.film_or_detector_model')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_image_recording.id')
    @property
    def imaging_id(self) -> Attribute:
        """This data item the id of the microscopy settings used in the imaging."""
        return Attribute('em_image_recording.imaging_id')
    @property
    def num_diffraction_images(self) -> Attribute:
        """The number of diffraction images collected."""
        return Attribute('em_image_recording.num_diffraction_images')
    @property
    def num_grids_imaged(self) -> Attribute:
        """Number of grids in the microscopy session"""
        return Attribute('em_image_recording.num_grids_imaged')
    @property
    def num_real_images(self) -> Attribute:
        """The number of micrograph images collected."""
        return Attribute('em_image_recording.num_real_images')

class Attr_EmImaging_8443919935556524626:
    """"""
    @property
    def accelerating_voltage(self) -> Attribute:
        """A value of accelerating voltage (in kV) used for imaging."""
        return Attribute('em_imaging.accelerating_voltage')
    @property
    def alignment_procedure(self) -> Attribute:
        """The type of procedure used to align the microscope electron beam."""
        return Attribute('em_imaging.alignment_procedure')
    @property
    def astigmatism(self) -> Attribute:
        """astigmatism"""
        return Attribute('em_imaging.astigmatism')
    @property
    def c2_aperture_diameter(self) -> Attribute:
        """The open diameter of the c2 condenser lens,  in microns."""
        return Attribute('em_imaging.c2_aperture_diameter')
    @property
    def calibrated_defocus_max(self) -> Attribute:
        """The maximum calibrated defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
        return Attribute('em_imaging.calibrated_defocus_max')
    @property
    def calibrated_defocus_min(self) -> Attribute:
        """The minimum calibrated defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
        return Attribute('em_imaging.calibrated_defocus_min')
    @property
    def calibrated_magnification(self) -> Attribute:
        """The magnification value obtained for a known standard just  prior to, during or just after the imaging experiment."""
        return Attribute('em_imaging.calibrated_magnification')
    @property
    def cryogen(self) -> Attribute:
        """Cryogen type used to maintain the specimen stage temperature during imaging  in the microscope."""
        return Attribute('em_imaging.cryogen')
    @property
    def date(self) -> Attribute:
        """Date (YYYY-MM-DD) of imaging experiment or the date at which  a series of experiments began."""
        return Attribute('em_imaging.date')
    @property
    def details(self) -> Attribute:
        """Any additional imaging details."""
        return Attribute('em_imaging.details')
    @property
    def detector_distance(self) -> Attribute:
        """The camera length (in millimeters). The camera length is the  product of the objective focal length and the combined magnification  of the intermediate and projector lenses when the microscope is  operated in the diffraction mode."""
        return Attribute('em_imaging.detector_distance')
    @property
    def electron_beam_tilt_params(self) -> Attribute:
        """electron beam tilt params"""
        return Attribute('em_imaging.electron_beam_tilt_params')
    @property
    def electron_source(self) -> Attribute:
        """The source of electrons. The electron gun."""
        return Attribute('em_imaging.electron_source')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_imaging.id')
    @property
    def illumination_mode(self) -> Attribute:
        """The mode of illumination."""
        return Attribute('em_imaging.illumination_mode')
    @property
    def microscope_model(self) -> Attribute:
        """The name of the model of microscope."""
        return Attribute('em_imaging.microscope_model')
    @property
    def mode(self) -> Attribute:
        """The mode of imaging."""
        return Attribute('em_imaging.mode')
    @property
    def nominal_cs(self) -> Attribute:
        """The spherical aberration coefficient (Cs) in millimeters,  of the objective lens."""
        return Attribute('em_imaging.nominal_cs')
    @property
    def nominal_defocus_max(self) -> Attribute:
        """The maximum defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
        return Attribute('em_imaging.nominal_defocus_max')
    @property
    def nominal_defocus_min(self) -> Attribute:
        """The minimum defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
        return Attribute('em_imaging.nominal_defocus_min')
    @property
    def nominal_magnification(self) -> Attribute:
        """The magnification indicated by the microscope readout."""
        return Attribute('em_imaging.nominal_magnification')
    @property
    def recording_temperature_maximum(self) -> Attribute:
        """The specimen temperature maximum (kelvin) for the duration  of imaging."""
        return Attribute('em_imaging.recording_temperature_maximum')
    @property
    def recording_temperature_minimum(self) -> Attribute:
        """The specimen temperature minimum (kelvin) for the duration  of imaging."""
        return Attribute('em_imaging.recording_temperature_minimum')
    @property
    def residual_tilt(self) -> Attribute:
        """Residual tilt of the electron beam (in miliradians)"""
        return Attribute('em_imaging.residual_tilt')
    @property
    def specimen_holder_model(self) -> Attribute:
        """The name of the model of specimen holder used during imaging."""
        return Attribute('em_imaging.specimen_holder_model')
    @property
    def specimen_holder_type(self) -> Attribute:
        """The type of specimen holder used during imaging."""
        return Attribute('em_imaging.specimen_holder_type')
    @property
    def specimen_id(self) -> Attribute:
        """Foreign key to the EM_SPECIMEN category"""
        return Attribute('em_imaging.specimen_id')
    @property
    def temperature(self) -> Attribute:
        """The mean specimen stage temperature (in kelvin) during imaging  in the microscope."""
        return Attribute('em_imaging.temperature')
    @property
    def tilt_angle_max(self) -> Attribute:
        """The maximum angle at which the specimen was tilted to obtain  recorded images."""
        return Attribute('em_imaging.tilt_angle_max')
    @property
    def tilt_angle_min(self) -> Attribute:
        """The minimum angle at which the specimen was tilted to obtain  recorded images."""
        return Attribute('em_imaging.tilt_angle_min')

class Attr_EmParticleSelection_3934816513497008143:
    """"""
    @property
    def details(self) -> Attribute:
        """Additional detail such as description of filters used, if selection was manual or automated, and/or template details."""
        return Attribute('em_particle_selection.details')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_particle_selection.id')
    @property
    def image_processing_id(self) -> Attribute:
        """The value of _em_particle_selection.image_processing_id points to  the EM_IMAGE_PROCESSING category."""
        return Attribute('em_particle_selection.image_processing_id')
    @property
    def num_particles_selected(self) -> Attribute:
        """The number of particles selected from the projection set of images."""
        return Attribute('em_particle_selection.num_particles_selected')

class Attr_EmSingleParticleEntity_1456680838209852130:
    """"""
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_single_particle_entity.id')
    @property
    def image_processing_id(self) -> Attribute:
        """pointer to _em_image_processing.id."""
        return Attribute('em_single_particle_entity.image_processing_id')
    @property
    def point_symmetry(self) -> Attribute:
        """Point symmetry symbol, either Cn, Dn, T, O, or I"""
        return Attribute('em_single_particle_entity.point_symmetry')

class Attr_EmSoftware_1920208556683351508:
    """"""
    @property
    def category(self) -> Attribute:
        """The purpose of the software."""
        return Attribute('em_software.category')
    @property
    def details(self) -> Attribute:
        """Details about the software used."""
        return Attribute('em_software.details')
    @property
    def fitting_id(self) -> Attribute:
        """pointer to _em_3d_fitting.id in the EM_3D_FITTING category."""
        return Attribute('em_software.fitting_id')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_software.id')
    @property
    def image_processing_id(self) -> Attribute:
        """pointer to _em_image_processing.id in the EM_IMAGE_PROCESSING category."""
        return Attribute('em_software.image_processing_id')
    @property
    def imaging_id(self) -> Attribute:
        """pointer to _em_imaging.id in the EM_IMAGING category."""
        return Attribute('em_software.imaging_id')
    @property
    def name(self) -> Attribute:
        """The name of the software package used, e.g., RELION.  Depositors are strongly   encouraged to provide a value in this field."""
        return Attribute('em_software.name')
    @property
    def version(self) -> Attribute:
        """The version of the software."""
        return Attribute('em_software.version')

class Attr_EmSpecimen_373910393168309909:
    """"""
    @property
    def concentration(self) -> Attribute:
        """The concentration (in milligrams per milliliter, mg/ml)  of the complex in the sample."""
        return Attribute('em_specimen.concentration')
    @property
    def details(self) -> Attribute:
        """A description of any additional details of the specimen preparation."""
        return Attribute('em_specimen.details')
    @property
    def embedding_applied(self) -> Attribute:
        """'YES' indicates that the specimen has been embedded."""
        return Attribute('em_specimen.embedding_applied')
    @property
    def experiment_id(self) -> Attribute:
        """Pointer to _em_experiment.id."""
        return Attribute('em_specimen.experiment_id')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_specimen.id')
    @property
    def shadowing_applied(self) -> Attribute:
        """'YES' indicates that the specimen has been shadowed."""
        return Attribute('em_specimen.shadowing_applied')
    @property
    def staining_applied(self) -> Attribute:
        """'YES' indicates that the specimen has been stained."""
        return Attribute('em_specimen.staining_applied')
    @property
    def vitrification_applied(self) -> Attribute:
        """'YES' indicates that the specimen was vitrified by cryopreservation."""
        return Attribute('em_specimen.vitrification_applied')

class Attr_EmStaining_3944418554910099293:
    """"""
    @property
    def details(self) -> Attribute:
        """Staining procedure used in the specimen preparation."""
        return Attribute('em_staining.details')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_staining.id')
    @property
    def material(self) -> Attribute:
        """The staining  material."""
        return Attribute('em_staining.material')
    @property
    def specimen_id(self) -> Attribute:
        """Foreign key relationship to the EM SPECIMEN category"""
        return Attribute('em_staining.specimen_id')
    @property
    def type(self) -> Attribute:
        """type of staining"""
        return Attribute('em_staining.type')

class Attr_EmVitrification_7134423166492578777:
    """"""
    @property
    def chamber_temperature(self) -> Attribute:
        """The temperature (in kelvin) of the sample just prior to vitrification."""
        return Attribute('em_vitrification.chamber_temperature')
    @property
    def cryogen_name(self) -> Attribute:
        """This is the name of the cryogen."""
        return Attribute('em_vitrification.cryogen_name')
    @property
    def details(self) -> Attribute:
        """Any additional details relating to vitrification."""
        return Attribute('em_vitrification.details')
    @property
    def humidity(self) -> Attribute:
        """Relative humidity (%) of air surrounding the specimen just prior to vitrification."""
        return Attribute('em_vitrification.humidity')
    @property
    def id(self) -> Attribute:
        """PRIMARY KEY"""
        return Attribute('em_vitrification.id')
    @property
    def instrument(self) -> Attribute:
        """The type of instrument used in the vitrification process."""
        return Attribute('em_vitrification.instrument')
    @property
    def method(self) -> Attribute:
        """The procedure for vitrification."""
        return Attribute('em_vitrification.method')
    @property
    def specimen_id(self) -> Attribute:
        """This data item is a pointer to _em_specimen.id"""
        return Attribute('em_vitrification.specimen_id')
    @property
    def temp(self) -> Attribute:
        """The vitrification temperature (in kelvin), e.g.,   temperature of the plunge instrument cryogen bath."""
        return Attribute('em_vitrification.temp')
    @property
    def time_resolved_state(self) -> Attribute:
        """The length of time after an event effecting the sample that  vitrification was induced and a description of the event."""
        return Attribute('em_vitrification.time_resolved_state')

class Attr_Entry_7047640374000475139:
    """"""
    @property
    def id(self) -> Attribute:
        """The value of _entry.id identifies the data block.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('entry.id')
    @property
    def ma_collection_id(self) -> Attribute:
        """An identifier for the model collection associated with the entry."""
        return Attribute('entry.ma_collection_id')

class Attr_Exptl_6468111129516196243:
    """"""
    @property
    def crystals_number(self) -> Attribute:
        """The total number of crystals used in the  measurement of  intensities."""
        return Attribute('exptl.crystals_number')
    @property
    def details(self) -> Attribute:
        """Any special information about the experimental work prior to the  intensity measurement. See also _exptl_crystal.preparation."""
        return Attribute('exptl.details')
    @property
    def method(self) -> Attribute:
        """The method used in the experiment."""
        return Attribute('exptl.method')
    @property
    def method_details(self) -> Attribute:
        """A description of special aspects of the experimental method."""
        return Attribute('exptl.method_details')

class Attr_ExptlCrystal_8825550452672787166:
    """"""
    @property
    def colour(self) -> Attribute:
        """The colour of the crystal."""
        return Attribute('exptl_crystal.colour')
    @property
    def density_Matthews(self) -> Attribute:
        """The density of the crystal, expressed as the ratio of the  volume of the asymmetric unit to the molecular mass of a  monomer of the structure, in units of angstroms^3^ per dalton.   Ref: Matthews, B. W. (1968). J. Mol. Biol. 33, 491-497."""
        return Attribute('exptl_crystal.density_Matthews')
    @property
    def density_meas(self) -> Attribute:
        """Density values measured using standard chemical and physical  methods. The units are megagrams per cubic metre (grams per  cubic centimetre)."""
        return Attribute('exptl_crystal.density_meas')
    @property
    def density_percent_sol(self) -> Attribute:
        """Density value P calculated from the crystal cell and contents,  expressed as per cent solvent.   P = 1 - (1.23 N MMass) / V   N     = the number of molecules in the unit cell  MMass = the molecular mass of each molecule (gm/mole)  V     = the volume of the unit cell (A^3^)  1.23  = a conversion factor evaluated as:           (0.74 cm^3^/g) (10^24^ A^3^/cm^3^)          --------------------------------------               (6.02*10^23^) molecules/mole           where 0.74 is an assumed value for the partial specific          volume of the molecule"""
        return Attribute('exptl_crystal.density_percent_sol')
    @property
    def description(self) -> Attribute:
        """A description of the quality and habit of the crystal.  The crystal dimensions should not normally be reported here;  use instead the specific items in the EXPTL_CRYSTAL category  relating to size for the gross dimensions of the crystal and  data items in the EXPTL_CRYSTAL_FACE category to describe the  relationship between individual faces."""
        return Attribute('exptl_crystal.description')
    @property
    def id(self) -> Attribute:
        """The value of _exptl_crystal.id must uniquely identify a record in  the EXPTL_CRYSTAL list.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('exptl_crystal.id')
    @property
    def pdbx_mosaicity(self) -> Attribute:
        """Isotropic approximation of the distribution of mis-orientation angles specified in degrees of all the mosaic domain blocks in the crystal, represented as a standard deviation. Here, a mosaic block is a set of contiguous unit cells assumed to be perfectly aligned. Lower mosaicity indicates better ordered crystals. See for example:  Nave, C. (1998). Acta Cryst. D54, 848-853.  Note that many software packages estimate the mosaic rotation distribution differently and may combine several physical properties of the experiment into a single mosaic term. This term will help fit the modeled spots to the observed spots without necessarily being directly related to the physics of the crystal itself."""
        return Attribute('exptl_crystal.pdbx_mosaicity')
    @property
    def pdbx_mosaicity_esd(self) -> Attribute:
        """The uncertainty in the mosaicity estimate for the crystal."""
        return Attribute('exptl_crystal.pdbx_mosaicity_esd')
    @property
    def preparation(self) -> Attribute:
        """Details of crystal growth and preparation of the crystal (e.g.  mounting) prior to the intensity measurements."""
        return Attribute('exptl_crystal.preparation')

class Attr_ExptlCrystalGrow_409049865057722864:
    """"""
    @property
    def crystal_id(self) -> Attribute:
        """This data item is a pointer to _exptl_crystal.id in the  EXPTL_CRYSTAL category."""
        return Attribute('exptl_crystal_grow.crystal_id')
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the crystal growth."""
        return Attribute('exptl_crystal_grow.details')
    @property
    def method(self) -> Attribute:
        """The method used to grow the crystals."""
        return Attribute('exptl_crystal_grow.method')
    @property
    def pH(self) -> Attribute:
        """The pH at which the crystal was grown. If more than one pH was  employed during the crystallization process, the final pH should  be noted here and the protocol involving multiple pH values  should be described in _exptl_crystal_grow.details."""
        return Attribute('exptl_crystal_grow.pH')
    @property
    def pdbx_details(self) -> Attribute:
        """Text description of crystal growth procedure."""
        return Attribute('exptl_crystal_grow.pdbx_details')
    @property
    def pdbx_pH_range(self) -> Attribute:
        """The range of pH values at which the crystal was grown.   Used when  a point estimate of pH is not appropriate."""
        return Attribute('exptl_crystal_grow.pdbx_pH_range')
    @property
    def temp(self) -> Attribute:
        """The temperature in kelvins at which the crystal was grown.  If more than one temperature was employed during the  crystallization process, the final temperature should be noted  here and the protocol  involving multiple temperatures should be  described in _exptl_crystal_grow.details."""
        return Attribute('exptl_crystal_grow.temp')
    @property
    def temp_details(self) -> Attribute:
        """A description of special aspects of temperature control during  crystal growth."""
        return Attribute('exptl_crystal_grow.temp_details')

class Attr_IhmEntryCollectionMapping_5112330335347866000:
    """"""
    @property
    def collection_id(self) -> Attribute:
        """Identifier for the entry collection.   This data item is a pointer to _ihm_entry_collection.id in the   IHM_ENTRY_COLLECTION category."""
        return Attribute('ihm_entry_collection_mapping.collection_id')

class Attr_IhmExternalReferenceInfo_43481185161579931:
    """"""
    @property
    def associated_url(self) -> Attribute:
        """The Uniform Resource Locator (URL) corresponding to the external reference (DOI).   This URL should link to the corresponding downloadable file or archive and is provided   to enable automated software to download the referenced file or archive."""
        return Attribute('ihm_external_reference_info.associated_url')
    @property
    def reference(self) -> Attribute:
        """The external reference or the Digital Object Identifier (DOI).  This field is not relevant for local files."""
        return Attribute('ihm_external_reference_info.reference')
    @property
    def reference_provider(self) -> Attribute:
        """The name of the reference provider."""
        return Attribute('ihm_external_reference_info.reference_provider')

class Attr_MaData_2196974696908633366:
    """"""
    @property
    def content_type(self) -> Attribute:
        """The type of data held in the dataset."""
        return Attribute('ma_data.content_type')
    @property
    def content_type_other_details(self) -> Attribute:
        """Details for other content types."""
        return Attribute('ma_data.content_type_other_details')
    @property
    def id(self) -> Attribute:
        """A unique identifier for the data."""
        return Attribute('ma_data.id')
    @property
    def name(self) -> Attribute:
        """An author-given name for the content held in the dataset."""
        return Attribute('ma_data.name')

class Attr_PdbxSgProject_5312137082222539390:
    """"""
    @property
    def full_name_of_center(self) -> Attribute:
        """The value identifies the full name of center."""
        return Attribute('pdbx_SG_project.full_name_of_center')
    @property
    def id(self) -> Attribute:
        """A unique integer identifier for this center"""
        return Attribute('pdbx_SG_project.id')
    @property
    def initial_of_center(self) -> Attribute:
        """The value identifies the full name of center."""
        return Attribute('pdbx_SG_project.initial_of_center')
    @property
    def project_name(self) -> Attribute:
        """The value identifies the Structural Genomics project."""
        return Attribute('pdbx_SG_project.project_name')

class Attr_PdbxAuditRevisionCategory_94306754416665653:
    """"""
    @property
    def category(self) -> Attribute:
        """The category updated in the pdbx_audit_revision_category record."""
        return Attribute('pdbx_audit_revision_category.category')
    @property
    def data_content_type(self) -> Attribute:
        """The type of file that the pdbx_audit_revision_history record refers to."""
        return Attribute('pdbx_audit_revision_category.data_content_type')
    @property
    def ordinal(self) -> Attribute:
        """A unique identifier for the pdbx_audit_revision_category record."""
        return Attribute('pdbx_audit_revision_category.ordinal')
    @property
    def revision_ordinal(self) -> Attribute:
        """A pointer to  _pdbx_audit_revision_history.ordinal"""
        return Attribute('pdbx_audit_revision_category.revision_ordinal')

class Attr_PdbxAuditRevisionDetails_7978068151254483793:
    """"""
    @property
    def data_content_type(self) -> Attribute:
        """The type of file that the pdbx_audit_revision_history record refers to."""
        return Attribute('pdbx_audit_revision_details.data_content_type')
    @property
    def description(self) -> Attribute:
        """Additional details describing the revision."""
        return Attribute('pdbx_audit_revision_details.description')
    @property
    def details(self) -> Attribute:
        """Further details describing the revision."""
        return Attribute('pdbx_audit_revision_details.details')
    @property
    def ordinal(self) -> Attribute:
        """A unique identifier for the pdbx_audit_revision_details record."""
        return Attribute('pdbx_audit_revision_details.ordinal')
    @property
    def provider(self) -> Attribute:
        """The provider of the revision."""
        return Attribute('pdbx_audit_revision_details.provider')
    @property
    def revision_ordinal(self) -> Attribute:
        """A pointer to  _pdbx_audit_revision_history.ordinal"""
        return Attribute('pdbx_audit_revision_details.revision_ordinal')
    @property
    def type(self) -> Attribute:
        """A type classification of the revision"""
        return Attribute('pdbx_audit_revision_details.type')

class Attr_PdbxAuditRevisionGroup_3357869764139277325:
    """"""
    @property
    def data_content_type(self) -> Attribute:
        """The type of file that the pdbx_audit_revision_history record refers to."""
        return Attribute('pdbx_audit_revision_group.data_content_type')
    @property
    def group(self) -> Attribute:
        """The collection of categories updated with this revision."""
        return Attribute('pdbx_audit_revision_group.group')
    @property
    def ordinal(self) -> Attribute:
        """A unique identifier for the pdbx_audit_revision_group record."""
        return Attribute('pdbx_audit_revision_group.ordinal')
    @property
    def revision_ordinal(self) -> Attribute:
        """A pointer to  _pdbx_audit_revision_history.ordinal"""
        return Attribute('pdbx_audit_revision_group.revision_ordinal')

class Attr_PdbxAuditRevisionHistory_4584809085243058953:
    """"""
    @property
    def data_content_type(self) -> Attribute:
        """The type of file that the pdbx_audit_revision_history record refers to."""
        return Attribute('pdbx_audit_revision_history.data_content_type')
    @property
    def major_revision(self) -> Attribute:
        """The major version number of deposition release."""
        return Attribute('pdbx_audit_revision_history.major_revision')
    @property
    def minor_revision(self) -> Attribute:
        """The minor version number of deposition release."""
        return Attribute('pdbx_audit_revision_history.minor_revision')
    @property
    def ordinal(self) -> Attribute:
        """A unique identifier for the pdbx_audit_revision_history record."""
        return Attribute('pdbx_audit_revision_history.ordinal')
    @property
    def revision_date(self) -> Attribute:
        """The release date of the revision"""
        return Attribute('pdbx_audit_revision_history.revision_date')

class Attr_PdbxAuditRevisionItem_355903234718695599:
    """"""
    @property
    def data_content_type(self) -> Attribute:
        """The type of file that the pdbx_audit_revision_history record refers to."""
        return Attribute('pdbx_audit_revision_item.data_content_type')
    @property
    def item(self) -> Attribute:
        """A high level explanation the author has provided for submitting a revision."""
        return Attribute('pdbx_audit_revision_item.item')
    @property
    def ordinal(self) -> Attribute:
        """A unique identifier for the pdbx_audit_revision_item record."""
        return Attribute('pdbx_audit_revision_item.ordinal')
    @property
    def revision_ordinal(self) -> Attribute:
        """A pointer to  _pdbx_audit_revision_history.ordinal"""
        return Attribute('pdbx_audit_revision_item.revision_ordinal')

class Attr_PdbxAuditSupport_6234993279930336019:
    """"""
    @property
    def country(self) -> Attribute:
        """The country/region providing the funding support for the entry.  Funding information is optionally provided for entries after June 2016."""
        return Attribute('pdbx_audit_support.country')
    @property
    def funding_organization(self) -> Attribute:
        """The name of the organization providing funding support for the  entry. Funding information is optionally provided for entries  after June 2016."""
        return Attribute('pdbx_audit_support.funding_organization')
    @property
    def grant_number(self) -> Attribute:
        """The grant number associated with this source of support."""
        return Attribute('pdbx_audit_support.grant_number')
    @property
    def ordinal(self) -> Attribute:
        """A unique sequential integer identifier for each source of support for this entry."""
        return Attribute('pdbx_audit_support.ordinal')

class Attr_PdbxDatabasePdbObsSpr_2398372918850929347:
    """"""
    @property
    def date(self) -> Attribute:
        """The date of replacement."""
        return Attribute('pdbx_database_PDB_obs_spr.date')
    @property
    def details(self) -> Attribute:
        """Details related to the replaced or replacing entry."""
        return Attribute('pdbx_database_PDB_obs_spr.details')
    @property
    def id(self) -> Attribute:
        """Identifier for the type of obsolete entry to be added to this entry."""
        return Attribute('pdbx_database_PDB_obs_spr.id')
    @property
    def pdb_id(self) -> Attribute:
        """The new PDB identifier for the replaced entry."""
        return Attribute('pdbx_database_PDB_obs_spr.pdb_id')
    @property
    def replace_pdb_id(self) -> Attribute:
        """The PDB identifier for the replaced (OLD) entry/entries."""
        return Attribute('pdbx_database_PDB_obs_spr.replace_pdb_id')

class Attr_PdbxDatabaseRelated_7350539981266203513:
    """"""
    @property
    def content_type(self) -> Attribute:
        """The identifying content type of the related entry."""
        return Attribute('pdbx_database_related.content_type')
    @property
    def db_id(self) -> Attribute:
        """The identifying code in the related database."""
        return Attribute('pdbx_database_related.db_id')
    @property
    def db_name(self) -> Attribute:
        """The name of the database containing the related entry."""
        return Attribute('pdbx_database_related.db_name')
    @property
    def details(self) -> Attribute:
        """A description of the related entry."""
        return Attribute('pdbx_database_related.details')

class Attr_PdbxDatabaseStatus_2843649403162468643:
    """"""
    @property
    def SG_entry(self) -> Attribute:
        """This code indicates whether the entry belongs to  Structural Genomics Project."""
        return Attribute('pdbx_database_status.SG_entry')
    @property
    def deposit_site(self) -> Attribute:
        """The site where the file was deposited."""
        return Attribute('pdbx_database_status.deposit_site')
    @property
    def methods_development_category(self) -> Attribute:
        """The methods development category in which this  entry has been placed."""
        return Attribute('pdbx_database_status.methods_development_category')
    @property
    def pdb_format_compatible(self) -> Attribute:
        """A flag indicating that the entry is compatible with the PDB format.   A value of 'N' indicates that the no PDB format data file is  corresponding to this entry is available in the PDB archive."""
        return Attribute('pdbx_database_status.pdb_format_compatible')
    @property
    def process_site(self) -> Attribute:
        """The site where the file was deposited."""
        return Attribute('pdbx_database_status.process_site')
    @property
    def recvd_initial_deposition_date(self) -> Attribute:
        """The date of initial deposition.  (The first message for  deposition has been received.)"""
        return Attribute('pdbx_database_status.recvd_initial_deposition_date')
    @property
    def status_code(self) -> Attribute:
        """Code for status of file."""
        return Attribute('pdbx_database_status.status_code')
    @property
    def status_code_cs(self) -> Attribute:
        """Code for status of chemical shift data file."""
        return Attribute('pdbx_database_status.status_code_cs')
    @property
    def status_code_mr(self) -> Attribute:
        """Code for status of NMR constraints file."""
        return Attribute('pdbx_database_status.status_code_mr')
    @property
    def status_code_sf(self) -> Attribute:
        """Code for status of structure factor file."""
        return Attribute('pdbx_database_status.status_code_sf')

class Attr_PdbxDepositGroup_7970256297506492451:
    """"""
    @property
    def group_description(self) -> Attribute:
        """A description of the contents of entries in the collection."""
        return Attribute('pdbx_deposit_group.group_description')
    @property
    def group_id(self) -> Attribute:
        """A unique identifier for a group of entries deposited as a collection."""
        return Attribute('pdbx_deposit_group.group_id')
    @property
    def group_title(self) -> Attribute:
        """A title to describe the group of entries deposited in the collection."""
        return Attribute('pdbx_deposit_group.group_title')
    @property
    def group_type(self) -> Attribute:
        """Text to describe a grouping of entries in multiple collections"""
        return Attribute('pdbx_deposit_group.group_type')

class Attr_PdbxInitialRefinementModel_6955766111047015209:
    """"""
    @property
    def accession_code(self) -> Attribute:
        """This item identifies an accession code of the resource where the initial model  is used"""
        return Attribute('pdbx_initial_refinement_model.accession_code')
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the initial model"""
        return Attribute('pdbx_initial_refinement_model.details')
    @property
    def entity_id_list(self) -> Attribute:
        """"""
        return Attribute('pdbx_initial_refinement_model.entity_id_list')
    @property
    def id(self) -> Attribute:
        """A unique identifier for the starting model record."""
        return Attribute('pdbx_initial_refinement_model.id')
    @property
    def source_name(self) -> Attribute:
        """This item identifies the resource of initial model used for refinement"""
        return Attribute('pdbx_initial_refinement_model.source_name')
    @property
    def type(self) -> Attribute:
        """This item describes the type of the initial model was generated"""
        return Attribute('pdbx_initial_refinement_model.type')

class Attr_PdbxMoleculeFeatures_672286848675098587:
    """"""
    @property
    def class_(self) -> Attribute:
        """Broadly defines the function of the molecule."""
        return Attribute('pdbx_molecule_features.class')
    @property
    def details(self) -> Attribute:
        """Additional details describing the molecule."""
        return Attribute('pdbx_molecule_features.details')
    @property
    def name(self) -> Attribute:
        """A name of the molecule."""
        return Attribute('pdbx_molecule_features.name')
    @property
    def prd_id(self) -> Attribute:
        """The value of _pdbx_molecule_features.prd_id is the accession code for this  reference molecule."""
        return Attribute('pdbx_molecule_features.prd_id')
    @property
    def type(self) -> Attribute:
        """Defines the structural classification of the molecule."""
        return Attribute('pdbx_molecule_features.type')

class Attr_PdbxNmrDetails_8942441883318100394:
    """"""
    @property
    def text(self) -> Attribute:
        """Additional details describing the NMR experiment."""
        return Attribute('pdbx_nmr_details.text')

class Attr_PdbxNmrEnsemble_2203587242519146887:
    """"""
    @property
    def average_constraint_violations_per_residue(self) -> Attribute:
        """The average number of constraint violations on a per residue basis for  the ensemble."""
        return Attribute('pdbx_nmr_ensemble.average_constraint_violations_per_residue')
    @property
    def average_constraints_per_residue(self) -> Attribute:
        """The average number of constraints per residue for the ensemble"""
        return Attribute('pdbx_nmr_ensemble.average_constraints_per_residue')
    @property
    def average_distance_constraint_violation(self) -> Attribute:
        """The average distance restraint violation for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.average_distance_constraint_violation')
    @property
    def average_torsion_angle_constraint_violation(self) -> Attribute:
        """The average torsion angle constraint violation for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.average_torsion_angle_constraint_violation')
    @property
    def conformer_selection_criteria(self) -> Attribute:
        """By highlighting the appropriate choice(s), describe how the submitted conformer (models) were selected."""
        return Attribute('pdbx_nmr_ensemble.conformer_selection_criteria')
    @property
    def conformers_calculated_total_number(self) -> Attribute:
        """The total number of conformer (models) that were calculated in the final round."""
        return Attribute('pdbx_nmr_ensemble.conformers_calculated_total_number')
    @property
    def conformers_submitted_total_number(self) -> Attribute:
        """The number of conformer (models) that are submitted for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.conformers_submitted_total_number')
    @property
    def distance_constraint_violation_method(self) -> Attribute:
        """Describe the method used to calculate the distance constraint violation statistics,  i.e. are they calculated over all the distance constraints or calculated for  violations only?"""
        return Attribute('pdbx_nmr_ensemble.distance_constraint_violation_method')
    @property
    def maximum_distance_constraint_violation(self) -> Attribute:
        """The maximum distance constraint violation for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.maximum_distance_constraint_violation')
    @property
    def maximum_lower_distance_constraint_violation(self) -> Attribute:
        """The maximum lower distance constraint violation for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.maximum_lower_distance_constraint_violation')
    @property
    def maximum_torsion_angle_constraint_violation(self) -> Attribute:
        """The maximum torsion angle constraint violation for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.maximum_torsion_angle_constraint_violation')
    @property
    def maximum_upper_distance_constraint_violation(self) -> Attribute:
        """The maximum upper distance constraint violation for the ensemble."""
        return Attribute('pdbx_nmr_ensemble.maximum_upper_distance_constraint_violation')
    @property
    def representative_conformer(self) -> Attribute:
        """The number of the conformer identified as most representative."""
        return Attribute('pdbx_nmr_ensemble.representative_conformer')
    @property
    def torsion_angle_constraint_violation_method(self) -> Attribute:
        """This item describes the method used to calculate the torsion angle constraint violation statistics. i.e. are the entered values based on all torsion angle or calculated for violations only?"""
        return Attribute('pdbx_nmr_ensemble.torsion_angle_constraint_violation_method')

class Attr_PdbxNmrExptl_996468958718618529:
    """"""
    @property
    def conditions_id(self) -> Attribute:
        """The number to identify the set of sample conditions."""
        return Attribute('pdbx_nmr_exptl.conditions_id')
    @property
    def experiment_id(self) -> Attribute:
        """A numerical ID for each experiment."""
        return Attribute('pdbx_nmr_exptl.experiment_id')
    @property
    def sample_state(self) -> Attribute:
        """Physical state of the sample either anisotropic or isotropic."""
        return Attribute('pdbx_nmr_exptl.sample_state')
    @property
    def solution_id(self) -> Attribute:
        """The solution_id from the Experimental Sample to identify the sample  that these conditions refer to.   [Remember to save the entries here before returning to the   Experimental Sample form]"""
        return Attribute('pdbx_nmr_exptl.solution_id')
    @property
    def spectrometer_id(self) -> Attribute:
        """Pointer to '_pdbx_nmr_spectrometer.spectrometer_id'"""
        return Attribute('pdbx_nmr_exptl.spectrometer_id')
    @property
    def type(self) -> Attribute:
        """The type of NMR experiment."""
        return Attribute('pdbx_nmr_exptl.type')

class Attr_PdbxNmrExptlSampleConditions_3017575829123646322:
    """"""
    @property
    def conditions_id(self) -> Attribute:
        """The condition number as defined above."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.conditions_id')
    @property
    def details(self) -> Attribute:
        """General details describing conditions of both the sample and the environment during measurements."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.details')
    @property
    def ionic_strength(self) -> Attribute:
        """The ionic strength at which the NMR data were collected -in lieu of  this enter the concentration and identity of the salt in the sample."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.ionic_strength')
    @property
    def ionic_strength_err(self) -> Attribute:
        """Estimate of the standard error for the value for the sample ionic strength."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.ionic_strength_err')
    @property
    def ionic_strength_units(self) -> Attribute:
        """Units for the value of the sample condition ionic strength.."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.ionic_strength_units')
    @property
    def label(self) -> Attribute:
        """A descriptive label that uniquely identifies this set of sample conditions."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.label')
    @property
    def pH(self) -> Attribute:
        """The pH at which the NMR data were collected."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.pH')
    @property
    def pH_err(self) -> Attribute:
        """Estimate of the standard error for the value for the sample pH."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.pH_err')
    @property
    def pH_units(self) -> Attribute:
        """Units for the value of the sample condition pH."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.pH_units')
    @property
    def pressure(self) -> Attribute:
        """The pressure at which NMR data were collected."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.pressure')
    @property
    def pressure_err(self) -> Attribute:
        """Estimate of the standard error for the value for the sample pressure."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.pressure_err')
    @property
    def pressure_units(self) -> Attribute:
        """The units of pressure at which NMR data were collected."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.pressure_units')
    @property
    def temperature(self) -> Attribute:
        """The temperature (in kelvin) at which NMR data were  collected."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.temperature')
    @property
    def temperature_err(self) -> Attribute:
        """Estimate of the standard error for the value for the sample temperature."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.temperature_err')
    @property
    def temperature_units(self) -> Attribute:
        """Units for the value of the sample condition temperature."""
        return Attribute('pdbx_nmr_exptl_sample_conditions.temperature_units')

class Attr_PdbxNmrRefine_2514587179798376093:
    """"""
    @property
    def details(self) -> Attribute:
        """Additional details about the NMR refinement."""
        return Attribute('pdbx_nmr_refine.details')
    @property
    def method(self) -> Attribute:
        """The method used to determine the structure."""
        return Attribute('pdbx_nmr_refine.method')
    @property
    def software_ordinal(self) -> Attribute:
        """Pointer to _software.ordinal"""
        return Attribute('pdbx_nmr_refine.software_ordinal')

class Attr_PdbxNmrRepresentative_7165353340664204411:
    """"""
    @property
    def conformer_id(self) -> Attribute:
        """If a member of the ensemble has been selected as a representative  structure, identify it by its model number."""
        return Attribute('pdbx_nmr_representative.conformer_id')
    @property
    def selection_criteria(self) -> Attribute:
        """By highlighting the appropriate choice(s), describe the criteria used to select this structure as a representative structure, or if an average structure has been calculated describe how this was done."""
        return Attribute('pdbx_nmr_representative.selection_criteria')

class Attr_PdbxNmrSampleDetails_4164748925044019281:
    """"""
    @property
    def contents(self) -> Attribute:
        """A complete description of each NMR sample. Include the concentration and concentration units for each component (include buffers, etc.). For each component describe the isotopic composition, including the % labeling level, if known.  For example: 1. Uniform (random) labeling with 15N: U-15N 2. Uniform (random) labeling with 13C, 15N at known labeling    levels: U-95% 13C;U-98% 15N 3. Residue selective labeling: U-95% 15N-Thymine 4. Site specific labeling: 95% 13C-Ala18, 5. Natural abundance labeling in an otherwise uniformly labeled    biomolecule is designated by NA: U-13C; NA-K,H"""
        return Attribute('pdbx_nmr_sample_details.contents')
    @property
    def details(self) -> Attribute:
        """Brief description of the sample providing additional information not captured by other items in the category."""
        return Attribute('pdbx_nmr_sample_details.details')
    @property
    def label(self) -> Attribute:
        """A value that uniquely identifies this sample from the other samples listed in the entry."""
        return Attribute('pdbx_nmr_sample_details.label')
    @property
    def solution_id(self) -> Attribute:
        """The name (number) of the sample."""
        return Attribute('pdbx_nmr_sample_details.solution_id')
    @property
    def solvent_system(self) -> Attribute:
        """The solvent system used for this sample."""
        return Attribute('pdbx_nmr_sample_details.solvent_system')
    @property
    def type(self) -> Attribute:
        """A descriptive term for the sample that defines the general physical properties of the sample."""
        return Attribute('pdbx_nmr_sample_details.type')

class Attr_PdbxNmrSoftware_7903304074939432631:
    """"""
    @property
    def authors(self) -> Attribute:
        """The name of the authors of the software used in this  procedure."""
        return Attribute('pdbx_nmr_software.authors')
    @property
    def classification(self) -> Attribute:
        """The purpose of the software."""
        return Attribute('pdbx_nmr_software.classification')
    @property
    def name(self) -> Attribute:
        """The name of the software used for the task."""
        return Attribute('pdbx_nmr_software.name')
    @property
    def ordinal(self) -> Attribute:
        """An ordinal index for this category"""
        return Attribute('pdbx_nmr_software.ordinal')
    @property
    def version(self) -> Attribute:
        """The version of the software."""
        return Attribute('pdbx_nmr_software.version')

class Attr_PdbxNmrSpectrometer_518721406184626396:
    """"""
    @property
    def details(self) -> Attribute:
        """A text description of the NMR spectrometer."""
        return Attribute('pdbx_nmr_spectrometer.details')
    @property
    def field_strength(self) -> Attribute:
        """The field strength in MHz of the spectrometer"""
        return Attribute('pdbx_nmr_spectrometer.field_strength')
    @property
    def manufacturer(self) -> Attribute:
        """The name of the manufacturer of the spectrometer."""
        return Attribute('pdbx_nmr_spectrometer.manufacturer')
    @property
    def model(self) -> Attribute:
        """The model of the NMR spectrometer."""
        return Attribute('pdbx_nmr_spectrometer.model')
    @property
    def spectrometer_id(self) -> Attribute:
        """Assign a numerical ID to each instrument."""
        return Attribute('pdbx_nmr_spectrometer.spectrometer_id')
    @property
    def type(self) -> Attribute:
        """Select the instrument manufacturer(s) and the model(s) of the NMR(s) used for this work."""
        return Attribute('pdbx_nmr_spectrometer.type')

class Attr_PdbxReflnsTwin_6266513563282235397:
    """"""
    @property
    def crystal_id(self) -> Attribute:
        """The crystal identifier.  A reference to  _exptl_crystal.id in category EXPTL_CRYSTAL."""
        return Attribute('pdbx_reflns_twin.crystal_id')
    @property
    def diffrn_id(self) -> Attribute:
        """The diffraction data set identifier.  A reference to  _diffrn.id in category DIFFRN."""
        return Attribute('pdbx_reflns_twin.diffrn_id')
    @property
    def domain_id(self) -> Attribute:
        """An identifier for the twin domain."""
        return Attribute('pdbx_reflns_twin.domain_id')
    @property
    def fraction(self) -> Attribute:
        """The twin fraction or twin factor represents a quantitative parameter for the crystal twinning.  The value 0 represents no twinning, < 0.5 partial twinning,  = 0.5 for perfect twinning."""
        return Attribute('pdbx_reflns_twin.fraction')
    @property
    def operator(self) -> Attribute:
        """The possible merohedral or hemihedral twinning operators for different point groups are:  True point group  	Twin operation  	hkl related to 3                      	2 along a,b             h,-h-k,-l                        	2 along a*,b*           h+k,-k,-l                         2 along c               -h,-k,l 4                       2 along a,b,a*,b*       h,-k,-l 6                       2 along a,b,a*,b*       h,-h-k,-l 321                     2 along a*,b*,c         -h,-k,l 312                     2 along a,b,c           -h,-k,l 23                      4 along a,b,c            k,-h,l  References:  Yeates, T.O. (1997) Methods in Enzymology 276, 344-358. Detecting and  Overcoming Crystal Twinning.   and information from the following on-line sites:     CNS site http://cns.csb.yale.edu/v1.1/    CCP4 site http://www.ccp4.ac.uk/dist/html/detwin.html    SHELX site http://shelx.uni-ac.gwdg.de/~rherbst/twin.html"""
        return Attribute('pdbx_reflns_twin.operator')
    @property
    def type(self) -> Attribute:
        """There are two types of twinning: merohedral or hemihedral                                  non-merohedral or epitaxial  For merohedral twinning the diffraction patterns from the different domains are completely superimposable.   Hemihedral twinning is a special case of merohedral twinning. It only involves two distinct domains.  Pseudo-merohedral twinning is a subclass merohedral twinning in which lattice is coincidentally superimposable.  In the case of non-merohedral or epitaxial twinning  the reciprocal lattices do not superimpose exactly. In this case the  diffraction pattern consists of two (or more) interpenetrating lattices, which can in principle be separated."""
        return Attribute('pdbx_reflns_twin.type')

class Attr_PdbxRelatedExpDataSet_510615844747980254:
    """"""
    @property
    def data_reference(self) -> Attribute:
        """A DOI reference to the related data set."""
        return Attribute('pdbx_related_exp_data_set.data_reference')
    @property
    def data_set_type(self) -> Attribute:
        """The type of the experimenatal data set."""
        return Attribute('pdbx_related_exp_data_set.data_set_type')
    @property
    def details(self) -> Attribute:
        """Additional details describing the content of the related data set and its application to  the current investigation."""
        return Attribute('pdbx_related_exp_data_set.details')
    @property
    def metadata_reference(self) -> Attribute:
        """A DOI reference to the metadata decribing the related data set."""
        return Attribute('pdbx_related_exp_data_set.metadata_reference')

class Attr_PdbxSerialCrystallographyDataReduction_5645660585384434442:
    """"""
    @property
    def crystal_hits(self) -> Attribute:
        """For experiments in which samples are provided in a  continuous stream, the total number of frames collected  in which the crystal was hit."""
        return Attribute('pdbx_serial_crystallography_data_reduction.crystal_hits')
    @property
    def diffrn_id(self) -> Attribute:
        """The data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('pdbx_serial_crystallography_data_reduction.diffrn_id')
    @property
    def droplet_hits(self) -> Attribute:
        """For experiments in which samples are provided in a  continuous stream, the total number of frames collected  in which a droplet was hit."""
        return Attribute('pdbx_serial_crystallography_data_reduction.droplet_hits')
    @property
    def frame_hits(self) -> Attribute:
        """For experiments in which samples are provided in a  continuous stream, the total number of data frames collected  in which the sample was hit."""
        return Attribute('pdbx_serial_crystallography_data_reduction.frame_hits')
    @property
    def frames_failed_index(self) -> Attribute:
        """For experiments in which samples are provided in a  continuous stream, the total number of data frames collected  that contained a 'hit' but failed to index."""
        return Attribute('pdbx_serial_crystallography_data_reduction.frames_failed_index')
    @property
    def frames_indexed(self) -> Attribute:
        """For experiments in which samples are provided in a  continuous stream, the total number of data frames collected  that were indexed."""
        return Attribute('pdbx_serial_crystallography_data_reduction.frames_indexed')
    @property
    def frames_total(self) -> Attribute:
        """The total number of data frames collected for this  data set."""
        return Attribute('pdbx_serial_crystallography_data_reduction.frames_total')
    @property
    def lattices_indexed(self) -> Attribute:
        """For experiments in which samples are provided in a  continuous stream, the total number of lattices indexed."""
        return Attribute('pdbx_serial_crystallography_data_reduction.lattices_indexed')
    @property
    def lattices_merged(self) -> Attribute:
        """For experiments in which samples are provided in a             continuous stream, the total number of crystal lattices             that were merged in the final dataset.  Can be             less than frames_indexed depending on filtering during merging or 	    can be more than frames_indexed if there are multiple lattices. 	    per frame."""
        return Attribute('pdbx_serial_crystallography_data_reduction.lattices_merged')
    @property
    def xfel_pulse_events(self) -> Attribute:
        """For FEL experiments, the number of pulse events in the dataset."""
        return Attribute('pdbx_serial_crystallography_data_reduction.xfel_pulse_events')
    @property
    def xfel_run_numbers(self) -> Attribute:
        """For FEL experiments, in which data collection was performed 	       in batches, indicates which subset of the data collected                were used in producing this dataset."""
        return Attribute('pdbx_serial_crystallography_data_reduction.xfel_run_numbers')

class Attr_PdbxSerialCrystallographyMeasurement_7227600034672541797:
    """"""
    @property
    def collection_time_total(self) -> Attribute:
        """The total number of hours required to measure this data set."""
        return Attribute('pdbx_serial_crystallography_measurement.collection_time_total')
    @property
    def collimation(self) -> Attribute:
        """The collimation or type of focusing optics applied to the radiation."""
        return Attribute('pdbx_serial_crystallography_measurement.collimation')
    @property
    def diffrn_id(self) -> Attribute:
        """The data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('pdbx_serial_crystallography_measurement.diffrn_id')
    @property
    def focal_spot_size(self) -> Attribute:
        """The focal spot size of the beam  impinging on the sample (micrometres squared)."""
        return Attribute('pdbx_serial_crystallography_measurement.focal_spot_size')
    @property
    def photons_per_pulse(self) -> Attribute:
        """The photons per pulse measured in  (tera photons (10^(12)^)/pulse units)."""
        return Attribute('pdbx_serial_crystallography_measurement.photons_per_pulse')
    @property
    def pulse_duration(self) -> Attribute:
        """The average duration (femtoseconds) 	       of the pulse energy measured at the sample."""
        return Attribute('pdbx_serial_crystallography_measurement.pulse_duration')
    @property
    def pulse_energy(self) -> Attribute:
        """The energy/pulse of the X-ray pulse impacting the sample measured in microjoules."""
        return Attribute('pdbx_serial_crystallography_measurement.pulse_energy')
    @property
    def pulse_photon_energy(self) -> Attribute:
        """The photon energy of the X-ray pulse measured in KeV."""
        return Attribute('pdbx_serial_crystallography_measurement.pulse_photon_energy')
    @property
    def source_distance(self) -> Attribute:
        """The distance from source to the sample along the optical axis (metres)."""
        return Attribute('pdbx_serial_crystallography_measurement.source_distance')
    @property
    def source_size(self) -> Attribute:
        """The dimension of the source beam measured at the source (micrometres squared)."""
        return Attribute('pdbx_serial_crystallography_measurement.source_size')
    @property
    def xfel_pulse_repetition_rate(self) -> Attribute:
        """For FEL experiments, the pulse repetition rate measured in cycles per seconds."""
        return Attribute('pdbx_serial_crystallography_measurement.xfel_pulse_repetition_rate')

class Attr_PdbxSerialCrystallographySampleDelivery_1301595853714466834:
    """"""
    @property
    def description(self) -> Attribute:
        """The description of the mechanism by which the specimen in placed in the path  of the source."""
        return Attribute('pdbx_serial_crystallography_sample_delivery.description')
    @property
    def diffrn_id(self) -> Attribute:
        """The data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('pdbx_serial_crystallography_sample_delivery.diffrn_id')
    @property
    def method(self) -> Attribute:
        """The description of the mechanism by which the specimen in placed in the path  of the source."""
        return Attribute('pdbx_serial_crystallography_sample_delivery.method')

class Attr_PdbxSerialCrystallographySampleDeliveryFixedTarget_4202109415478603101:
    """"""
    @property
    def crystals_per_unit(self) -> Attribute:
        """The number of crystals per dropplet or pore in fixed target"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.crystals_per_unit')
    @property
    def description(self) -> Attribute:
        """For a fixed target sample, a description of sample preparation"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.description')
    @property
    def details(self) -> Attribute:
        """Any details pertinent to the fixed sample target"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.details')
    @property
    def diffrn_id(self) -> Attribute:
        """The data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.diffrn_id')
    @property
    def motion_control(self) -> Attribute:
        """Device used to control movement of the fixed sample"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.motion_control')
    @property
    def sample_dehydration_prevention(self) -> Attribute:
        """Method to prevent dehydration of sample"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.sample_dehydration_prevention')
    @property
    def sample_holding(self) -> Attribute:
        """For a fixed target sample, mechanism to hold sample in the beam"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.sample_holding')
    @property
    def sample_solvent(self) -> Attribute:
        """The sample solution content and concentration"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.sample_solvent')
    @property
    def sample_unit_size(self) -> Attribute:
        """Size of pore in grid supporting sample. Diameter or length in micrometres,  e.g. pore diameter"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.sample_unit_size')
    @property
    def support_base(self) -> Attribute:
        """Type of base holding the support"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.support_base')
    @property
    def velocity_horizontal(self) -> Attribute:
        """Velocity of sample horizontally relative to a perpendicular beam in millimetres/second"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.velocity_horizontal')
    @property
    def velocity_vertical(self) -> Attribute:
        """Velocity of sample vertically relative to a perpendicular beam in millimetres/second"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_fixed_target.velocity_vertical')

class Attr_PdbxSerialCrystallographySampleDeliveryInjection_1302945912861463402:
    """"""
    @property
    def carrier_solvent(self) -> Attribute:
        """For continuous sample flow experiments, the carrier buffer used  to move the sample into the beam. Should include protein  concentration."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.carrier_solvent')
    @property
    def crystal_concentration(self) -> Attribute:
        """For continuous sample flow experiments, the concentration of  crystals in the solution being injected.   The concentration is measured in million crystals/ml."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.crystal_concentration')
    @property
    def description(self) -> Attribute:
        """For continuous sample flow experiments, a description of the injector used  to move the sample into the beam."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.description')
    @property
    def diffrn_id(self) -> Attribute:
        """The data item is a pointer to _diffrn.id in the DIFFRN  category."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.diffrn_id')
    @property
    def filter_size(self) -> Attribute:
        """The size of filter in micrometres in filtering crystals"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.filter_size')
    @property
    def flow_rate(self) -> Attribute:
        """For continuous sample flow experiments, the flow rate of  solution being injected  measured in ul/min."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.flow_rate')
    @property
    def injector_diameter(self) -> Attribute:
        """For continuous sample flow experiments, the diameter of the  injector in micrometres."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.injector_diameter')
    @property
    def injector_nozzle(self) -> Attribute:
        """The type of nozzle to deliver and focus sample jet"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.injector_nozzle')
    @property
    def injector_pressure(self) -> Attribute:
        """For continuous sample flow experiments, the mean pressure  in kilopascals at which the sample is injected into the beam."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.injector_pressure')
    @property
    def injector_temperature(self) -> Attribute:
        """For continuous sample flow experiments, the temperature in  Kelvins of the speciman injected. This may be different from  the temperature of the sample."""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.injector_temperature')
    @property
    def jet_diameter(self) -> Attribute:
        """Diameter in micrometres of jet stream of sample delivery"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.jet_diameter')
    @property
    def power_by(self) -> Attribute:
        """Sample deliver driving force, e.g. Gas, Electronic Potential"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.power_by')
    @property
    def preparation(self) -> Attribute:
        """Details of crystal growth and preparation of the crystals"""
        return Attribute('pdbx_serial_crystallography_sample_delivery_injection.preparation')

class Attr_PdbxSolnScatter_5325256616457838874:
    """"""
    @property
    def buffer_name(self) -> Attribute:
        """The name of the buffer used for the sample in the solution scattering  experiment."""
        return Attribute('pdbx_soln_scatter.buffer_name')
    @property
    def concentration_range(self) -> Attribute:
        """The concentration range (mg/mL) of the complex in the  sample used in the solution scattering experiment to  determine the mean radius of structural elongation."""
        return Attribute('pdbx_soln_scatter.concentration_range')
    @property
    def data_analysis_software_list(self) -> Attribute:
        """A list of the software used in the data analysis"""
        return Attribute('pdbx_soln_scatter.data_analysis_software_list')
    @property
    def data_reduction_software_list(self) -> Attribute:
        """A list of the software used in the data reduction"""
        return Attribute('pdbx_soln_scatter.data_reduction_software_list')
    @property
    def detector_specific(self) -> Attribute:
        """The particular radiation detector. In general this will be a   manufacturer, description, model number or some combination of   these."""
        return Attribute('pdbx_soln_scatter.detector_specific')
    @property
    def detector_type(self) -> Attribute:
        """The general class of the radiation detector."""
        return Attribute('pdbx_soln_scatter.detector_type')
    @property
    def id(self) -> Attribute:
        """The value of _pdbx_soln_scatter.id must  uniquely identify the sample in the category PDBX_SOLN_SCATTER"""
        return Attribute('pdbx_soln_scatter.id')
    @property
    def max_mean_cross_sectional_radii_gyration(self) -> Attribute:
        """The maximum mean radius of structural elongation of the sample.  In a given solute-solvent contrast, the radius of gyration  R_G is a measure of structural elongation if the internal  inhomogeneity of scattering densities has no effect. Guiner  analysis at low Q give the R_G and the forward scattering at  zero angle I(0).      lnl(Q) = lnl(0) - R_G^2Q^2/3   where        Q = 4(pi)sin(theta/lamda)        2theta = scattering angle        lamda = wavelength   The above expression is valid in a QR_G range for extended  rod-like particles. The relative I(0)/c values ( where   c = sample concentration) for sample measurements in a  constant buffer for a single sample data session, gives the  relative masses of the protein(s) studied when referenced  against a standard.   see:      O.Glatter & O.Kratky, (1982). Editors of 'Small angle       X-ray Scattering, Academic Press, New York.      O.Kratky. (1963). X-ray small angle scattering with       substances of biological interest in diluted solutions.       Prog. Biophys. Chem., 13, 105-173.      G.D.Wignall & F.S.Bates, (1987). The small-angle approximation       of X-ray and neutron scatter from rigid rods of non-uniform       cross section and finite length. J.Appl. Crystallog., 18, 452-460.   If the structure is elongated, the mean radius of gyration  of the cross-sectional structure R_XS  and the mean cross sectional  intensity at zero angle [I(Q).Q]_Q->0 is obtained from     ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
        return Attribute('pdbx_soln_scatter.max_mean_cross_sectional_radii_gyration')
    @property
    def max_mean_cross_sectional_radii_gyration_esd(self) -> Attribute:
        """The estimated standard deviation for the minimum mean radius of structural elongation of the sample. In a given solute-solvent contrast, the radius of gyration R_G is a measure of structural elongation if the internal inhomogeneity of scattering densities has no effect. Guiner analysis at low Q give the R_G and the forward scattering at zero angle I(0).      lnl(Q) = lnl(0) - R_G^2Q^2/3  where       Q = 4(pi)sin(theta/lamda)       2theta = scattering angle       lamda = wavelength  The above expression is valid in a QR_G range for extended rod-like particles. The relative I(0)/c values ( where  c = sample concentration) for sample measurements in a constant buffer for a single sample data session, gives the relative masses of the protein(s) studied when referenced against a standard.  see:     O.Glatter & O.Kratky, (1982). Editors of 'Small angle      X-ray Scattering, Academic Press, New York.     O.Kratky. (1963). X-ray small angle scattering with      substances of biological interest in diluted solutions.      Prog. Biophys. Chem., 13, 105-173.     G.D.Wignall & F.S.Bates, (1987). The small-angle approximation      of X-ray and neutron scatter from rigid rods of non-uniform      cross section and finite length. J.Appl. Crystallog., 18, 452-460.  If the structure is elongated, the mean radius of gyration of the cross-sectional structure R_XS  and the mean cross sectional intensity at zero angle [I(Q).Q]_Q->0 is obtained from    ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
        return Attribute('pdbx_soln_scatter.max_mean_cross_sectional_radii_gyration_esd')
    @property
    def mean_guiner_radius(self) -> Attribute:
        """The mean radius of structural elongation of the sample.  In a given solute-solvent contrast, the radius of gyration  R_G is a measure of structural elongation if the internal  inhomogeneity of scattering densities has no effect. Guiner  analysis at low Q gives the R_G and the forward scattering at  zero angle I(0).       lnl(Q) = lnl(0) - R_G^2Q^2/3   where        Q = 4(pi)sin(theta/lamda)        2theta = scattering angle        lamda = wavelength   The above expression is valid in a QR_G range for extended  rod-like particles. The relative I(0)/c values ( where   c = sample concentration) for sample measurements in a  constant buffer for a single sample data session, gives the  relative masses of the protein(s) studied when referenced  against a standard.   see: O.Glatter & O.Kratky, (1982). Editors of 'Small angle       X-ray Scattering, Academic Press, New York.       O.Kratky. (1963). X-ray small angle scattering with       substances of biological interest in diluted solutions.       Prog. Biophys. Chem., 13, 105-173.        G.D.Wignall & F.S.Bates, (1987). The small-angle approximation       of X-ray and neutron scatter from rigid rods of non-uniform       cross section and finite length. J.Appl. Crystallog., 18, 452-460.   If the structure is elongated, the mean radius of gyration  of the cross-sectional structure R_XS  and the mean cross sectional  intensity at zero angle [I(Q).Q]_Q->0 is obtained from      ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
        return Attribute('pdbx_soln_scatter.mean_guiner_radius')
    @property
    def mean_guiner_radius_esd(self) -> Attribute:
        """The estimated standard deviation for the  mean radius of structural elongation of the sample.  In a given solute-solvent contrast, the radius of gyration  R_G is a measure of structural elongation if the internal  inhomogeneity of scattering densities has no effect. Guiner  analysis at low Q give the R_G and the forward scattering at  zero angle I(0).       lnl(Q) = lnl(0) - R_G^2Q^2/3   where        Q = 4(pi)sin(theta/lamda)        2theta = scattering angle        lamda = wavelength   The above expression is valid in a QR_G range for extended  rod-like particles. The relative I(0)/c values ( where   c = sample concentration) for sample measurements in a  constant buffer for a single sample data session, gives the  relative masses of the protein(s) studied when referenced  against a standard.   see:      O.Glatter & O.Kratky, (1982). Editors of 'Small angle       X-ray Scattering, Academic Press, New York.      O.Kratky. (1963). X-ray small angle scattering with       substances of biological interest in diluted solutions.       Prog. Biophys. Chem., 13, 105-173.      G.D.Wignall & F.S.Bates, (1987). The small-angle approximation       of X-ray and neutron scatter from rigid rods of non-uniform       cross section and finite length. J.Appl. Crystallog., 18, 452-460.   If the structure is elongated, the mean radius of gyration  of the cross-sectional structure R_XS  and the mean cross sectional  intensity at zero angle [I(Q).Q]_Q->0 is obtained from     ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
        return Attribute('pdbx_soln_scatter.mean_guiner_radius_esd')
    @property
    def min_mean_cross_sectional_radii_gyration(self) -> Attribute:
        """The minimum mean radius of structural elongation of the sample. In a given solute-solvent contrast, the radius of gyration R_G is a measure of structural elongation if the internal inhomogeneity of scattering densities has no effect. Guiner analysis at low Q give the R_G and the forward scattering at zero angle I(0).      lnl(Q) = lnl(0) - R_G^2Q^2/3  where       Q = 4(pi)sin(theta/lamda)       2theta = scattering angle       lamda = wavelength  The above expression is valid in a QR_G range for extended rod-like particles. The relative I(0)/c values ( where  c = sample concentration) for sample measurements in a constant buffer for a single sample data session, gives the relative masses of the protein(s) studied when referenced against a standard.  see:     O.Glatter & O.Kratky, (1982). Editors of 'Small angle      X-ray Scattering, Academic Press, New York.     O.Kratky. (1963). X-ray small angle scattering with      substances of biological interest in diluted solutions.      Prog. Biophys. Chem., 13, 105-173.     G.D.Wignall & F.S.Bates, (1987). The small-angle approximation      of X-ray and neutron scatter from rigid rods of non-uniform      cross section and finite length. J.Appl. Crystallog., 18, 452-460.  If the structure is elongated, the mean radius of gyration of the cross-sectional structure R_XS  and the mean cross sectional intensity at zero angle [I(Q).Q]_Q->0 is obtained from    ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
        return Attribute('pdbx_soln_scatter.min_mean_cross_sectional_radii_gyration')
    @property
    def min_mean_cross_sectional_radii_gyration_esd(self) -> Attribute:
        """The estimated standard deviation for the minimum mean radius of structural elongation of the sample. In a given solute-solvent contrast, the radius of gyration R_G is a measure of structural elongation if the internal inhomogeneity of scattering densities has no effect. Guiner analysis at low Q give the R_G and the forward scattering at zero angle I(0).     lnl(Q) = lnl(0) - R_G^2Q^2/3  where       Q = 4(pi)sin(theta/lamda)       2theta = scattering angle       lamda = wavelength  The above expression is valid in a QR_G range for extended rod-like particles. The relative I(0)/c values ( where  c = sample concentration) for sample measurements in a constant buffer for a single sample data session, gives the relative masses of the protein(s) studied when referenced against a standard.  see:     O.Glatter & O.Kratky, (1982). Editors of 'Small angle      X-ray Scattering, Academic Press, New York.     O.Kratky. (1963). X-ray small angle scattering with      substances of biological interest in diluted solutions.      Prog. Biophys. Chem., 13, 105-173.     G.D.Wignall & F.S.Bates, (1987). The small-angle approximation      of X-ray and neutron scatter from rigid rods of non-uniform      cross section and finite length. J.Appl. Crystallog., 18, 452-460.  If the structure is elongated, the mean radius of gyration of the cross-sectional structure R_XS  and the mean cross sectional intensity at zero angle [I(Q).Q]_Q->0 is obtained from     ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
        return Attribute('pdbx_soln_scatter.min_mean_cross_sectional_radii_gyration_esd')
    @property
    def num_time_frames(self) -> Attribute:
        """The number of time frame solution scattering images used."""
        return Attribute('pdbx_soln_scatter.num_time_frames')
    @property
    def protein_length(self) -> Attribute:
        """The length (or range) of the protein sample under study. If the solution structure is approximated as an elongated elliptical cyclinder the length L is determined from,    L = sqrt [12( (R_G)^2  -  (R_XS)^2 ) ]  The length should also be given by    L = pi I(0) / [ I(Q).Q]_Q->0"""
        return Attribute('pdbx_soln_scatter.protein_length')
    @property
    def sample_pH(self) -> Attribute:
        """The pH value of the buffered sample."""
        return Attribute('pdbx_soln_scatter.sample_pH')
    @property
    def source_beamline(self) -> Attribute:
        """The beamline name used for the experiment"""
        return Attribute('pdbx_soln_scatter.source_beamline')
    @property
    def source_beamline_instrument(self) -> Attribute:
        """The instrumentation used on the beamline"""
        return Attribute('pdbx_soln_scatter.source_beamline_instrument')
    @property
    def source_class(self) -> Attribute:
        """The general class of the radiation source."""
        return Attribute('pdbx_soln_scatter.source_class')
    @property
    def source_type(self) -> Attribute:
        """The make, model, name or beamline of the source of radiation."""
        return Attribute('pdbx_soln_scatter.source_type')
    @property
    def temperature(self) -> Attribute:
        """The temperature in kelvins at which the experiment  was conducted"""
        return Attribute('pdbx_soln_scatter.temperature')
    @property
    def type(self) -> Attribute:
        """The type of solution scattering experiment carried out"""
        return Attribute('pdbx_soln_scatter.type')

class Attr_PdbxSolnScatterModel_4225404216560231291:
    """"""
    @property
    def conformer_selection_criteria(self) -> Attribute:
        """A description of the conformer selection criteria  used."""
        return Attribute('pdbx_soln_scatter_model.conformer_selection_criteria')
    @property
    def details(self) -> Attribute:
        """A description of any additional details concerning the experiment."""
        return Attribute('pdbx_soln_scatter_model.details')
    @property
    def entry_fitting_list(self) -> Attribute:
        """A list of the entries used to fit the model  to the scattering data"""
        return Attribute('pdbx_soln_scatter_model.entry_fitting_list')
    @property
    def id(self) -> Attribute:
        """The value of _pdbx_soln_scatter_model.id must  uniquely identify the sample in the category PDBX_SOLN_SCATTER_MODEL"""
        return Attribute('pdbx_soln_scatter_model.id')
    @property
    def method(self) -> Attribute:
        """A description of the methods used in the modelling"""
        return Attribute('pdbx_soln_scatter_model.method')
    @property
    def num_conformers_calculated(self) -> Attribute:
        """The number of model conformers calculated."""
        return Attribute('pdbx_soln_scatter_model.num_conformers_calculated')
    @property
    def num_conformers_submitted(self) -> Attribute:
        """The number of model conformers submitted in the entry"""
        return Attribute('pdbx_soln_scatter_model.num_conformers_submitted')
    @property
    def representative_conformer(self) -> Attribute:
        """The index of the representative conformer among the submitted conformers for the entry"""
        return Attribute('pdbx_soln_scatter_model.representative_conformer')
    @property
    def scatter_id(self) -> Attribute:
        """This data item is a pointer to  _pdbx_soln_scatter.id in the  PDBX_SOLN_SCATTER category."""
        return Attribute('pdbx_soln_scatter_model.scatter_id')
    @property
    def software_author_list(self) -> Attribute:
        """A list of the software authors"""
        return Attribute('pdbx_soln_scatter_model.software_author_list')
    @property
    def software_list(self) -> Attribute:
        """A list of the software used in the modeeling"""
        return Attribute('pdbx_soln_scatter_model.software_list')

class Attr_PdbxVrptSummary_382225482295680055:
    """"""
    @property
    def RNA_suiteness(self) -> Attribute:
        """The MolProbity conformer-match quality parameter for RNA structures. Low values are worse. Specific to structures that contain RNA polymers."""
        return Attribute('pdbx_vrpt_summary.RNA_suiteness')
    @property
    def attempted_validation_steps(self) -> Attribute:
        """The steps that were attempted by the validation pipeline software.  A step typically involves running a 3rd party validation tool, for instance 'mogul' Each step will be enumerated in _pdbx_vrpt_software category."""
        return Attribute('pdbx_vrpt_summary.attempted_validation_steps')
    @property
    def ligands_for_buster_report(self) -> Attribute:
        """A flag indicating if there are ligands in the model used for detailed Buster analysis."""
        return Attribute('pdbx_vrpt_summary.ligands_for_buster_report')
    @property
    def report_creation_date(self) -> Attribute:
        """The date, time and time-zone that the validation report  was created.  The string will be formatted like yyyy-mm-dd:hh:mm in GMT time."""
        return Attribute('pdbx_vrpt_summary.report_creation_date')
    @property
    def restypes_notchecked_for_bond_angle_geometry(self) -> Attribute:
        """"""
        return Attribute('pdbx_vrpt_summary.restypes_notchecked_for_bond_angle_geometry')

class Attr_PdbxVrptSummaryDiffraction_3838680457496923333:
    """"""
    @property
    def B_factor_type(self) -> Attribute:
        """An indicator if isotropic B factors are partial or full values."""
        return Attribute('pdbx_vrpt_summary_diffraction.B_factor_type')
    @property
    def Babinet_b(self) -> Attribute:
        """REFMAC scaling parameter as reported in log output line starting 'bulk solvent: scale'. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
        return Attribute('pdbx_vrpt_summary_diffraction.Babinet_b')
    @property
    def Babinet_k(self) -> Attribute:
        """REFMAC scaling parameter as reported in log output line starting 'bulk solvent: scale'. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
        return Attribute('pdbx_vrpt_summary_diffraction.Babinet_k')
    @property
    def CCP4_version(self) -> Attribute:
        """The version of CCP4 suite used in the analysis."""
        return Attribute('pdbx_vrpt_summary_diffraction.CCP4_version')
    @property
    def DCC_R(self) -> Attribute:
        """The overall R-factor from a DCC recalculation of an electron density map. Currently value is rounded to 2 decimal places. X-ray entry specific, obtained from the DCC program."""
        return Attribute('pdbx_vrpt_summary_diffraction.DCC_R')
    @property
    def DCC_Rfree(self) -> Attribute:
        """Rfree as calculated by DCC."""
        return Attribute('pdbx_vrpt_summary_diffraction.DCC_Rfree')
    @property
    def EDS_R(self) -> Attribute:
        """The overall R factor from the EDS REFMAC calculation (no free set is used in this). Currently value is rounded to 2 decimal places. X-ray entry specific, obtained in the eds step from REFMAC calculation."""
        return Attribute('pdbx_vrpt_summary_diffraction.EDS_R')
    @property
    def EDS_R_warning(self) -> Attribute:
        """Warning message when EDS calculated R vs reported R is higher than a threshold"""
        return Attribute('pdbx_vrpt_summary_diffraction.EDS_R_warning')
    @property
    def EDS_res_high(self) -> Attribute:
        """The data high resolution diffraction limit, in Angstroms, found in the input structure factor file. X-ray entry specific, obtained in the EDS step."""
        return Attribute('pdbx_vrpt_summary_diffraction.EDS_res_high')
    @property
    def EDS_res_low(self) -> Attribute:
        """The data low resolution diffraction limit, in Angstroms, found in the input structure factor file. X-ray entry specific, obtained in the EDS step."""
        return Attribute('pdbx_vrpt_summary_diffraction.EDS_res_low')
    @property
    def Fo_Fc_correlation(self) -> Attribute:
        """Fo,Fc correlation: The difference between the observed structure factors (Fo) and the  calculated structure factors (Fc) measures the correlation between the model and the experimental data.  X-ray entry specific, obtained in the eds step from REFMAC calculation."""
        return Attribute('pdbx_vrpt_summary_diffraction.Fo_Fc_correlation')
    @property
    def I_over_sigma(self) -> Attribute:
        """Each reflection has an intensity (I) and an uncertainty in measurement  (sigma(I)), so I/sigma(I) is the signal-to-noise ratio. This ratio decreases at higher resolution. <I/sigma(I)> is the mean of individual I/sigma(I) values. Value for outer resolution shell is given in parentheses. In case structure factor amplitudes are deposited, Xtriage estimates the intensities first and then calculates this metric. When intensities are available in the deposited file, these are converted to amplitudes and then back to intensity estimate before calculating the metric.   X-ray entry specific, calculated by Phenix Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.I_over_sigma')
    @property
    def Padilla_Yeates_L2_mean(self) -> Attribute:
        """Padilla and Yeates twinning parameter <|L**2|>. Theoretical values is 0.333 in the untwinned case, and 0.2 in the perfectly twinned case. X-ray entry specific, obtained from the Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.Padilla_Yeates_L2_mean')
    @property
    def Padilla_Yeates_L_mean(self) -> Attribute:
        """Padilla and Yeates twinning parameter <|L|>. Theoretical values is 0.5 in the untwinned case, and 0.375 in the perfectly twinned case. X-ray entry specific, obtained from the Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.Padilla_Yeates_L_mean')
    @property
    def Q_score(self) -> Attribute:
        """The overall Q-score of the fit of coordinates to the electron map. The Q-score is defined in Pintilie, GH. et al., Nature Methods, 17, 328-334 (2020)"""
        return Attribute('pdbx_vrpt_summary_diffraction.Q_score')
    @property
    def Wilson_B_aniso(self) -> Attribute:
        """Result of absolute likelihood based Wilson scaling,  The anisotropic B value of the data is determined using a likelihood based approach.  The resulting B tensor is reported, the 3 diagonal values are given first, followed by the 3 off diagonal values. A large spread in (especially the diagonal) values indicates anisotropy.  X-ray entry specific, calculated by Phenix Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.Wilson_B_aniso')
    @property
    def Wilson_B_estimate(self) -> Attribute:
        """An estimate of the overall B-value of the structure, calculated from the diffraction data.  Units Angstroms squared. It serves as an indicator of the degree of order in the crystal and the value is usually  not hugely different from the average B-value calculated from the model. X-ray entry specific, calculated by Phenix Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.Wilson_B_estimate')
    @property
    def acentric_outliers(self) -> Attribute:
        """The number of acentric reflections that Xtriage identifies as outliers on the basis  of Wilson statistics. Note that if pseudo translational symmetry is present,  a large number of 'outliers' will be present. X-ray entry specific, calculated by Phenix Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.acentric_outliers')
    @property
    def bulk_solvent_b(self) -> Attribute:
        """REFMAC scaling parameter as reported in log output file. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
        return Attribute('pdbx_vrpt_summary_diffraction.bulk_solvent_b')
    @property
    def bulk_solvent_k(self) -> Attribute:
        """REFMAC reported scaling parameter. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
        return Attribute('pdbx_vrpt_summary_diffraction.bulk_solvent_k')
    @property
    def centric_outliers(self) -> Attribute:
        """The number of centric reflections that Xtriage identifies as outliers. X-ray entry specific, calculated by Phenix Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.centric_outliers')
    @property
    def data_anisotropy(self) -> Attribute:
        """The ratio (Bmax - Bmin) / Bmean where Bmax, Bmin and Bmean are computed from the B-values  associated with the principal axes of the anisotropic thermal ellipsoid.  This ratio is usually less than 0.5; for only 1% of PDB entries it is more than 1.0 (Read et al., 2011). X-ray entry specific, obtained from the Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.data_anisotropy')
    @property
    def data_completeness(self) -> Attribute:
        """The percent completeness of diffraction data."""
        return Attribute('pdbx_vrpt_summary_diffraction.data_completeness')
    @property
    def density_fitness_version(self) -> Attribute:
        """The version of density-fitness suite programs used in the analysis."""
        return Attribute('pdbx_vrpt_summary_diffraction.density_fitness_version')
    @property
    def exp_method(self) -> Attribute:
        """Experimental method for statistics"""
        return Attribute('pdbx_vrpt_summary_diffraction.exp_method')
    @property
    def num_miller_indices(self) -> Attribute:
        """The number of Miller Indices reported by the Xtriage program. This should be the same as the number of _refln in the input structure factor file. X-ray entry specific, calculated by Phenix Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.num_miller_indices')
    @property
    def number_reflns_R_free(self) -> Attribute:
        """The number of reflections in the free set as defined in the input structure factor file supplied to the validation pipeline.  X-ray entry specific, obtained from the DCC program."""
        return Attribute('pdbx_vrpt_summary_diffraction.number_reflns_R_free')
    @property
    def percent_RSRZ_outliers(self) -> Attribute:
        """The percent of RSRZ outliers."""
        return Attribute('pdbx_vrpt_summary_diffraction.percent_RSRZ_outliers')
    @property
    def percent_free_reflections(self) -> Attribute:
        """A percentage, Normally percent proportion of the total number. Between 0% and 100%."""
        return Attribute('pdbx_vrpt_summary_diffraction.percent_free_reflections')
    @property
    def servalcat_version(self) -> Attribute:
        """The version of Servalcat program used in the analysis."""
        return Attribute('pdbx_vrpt_summary_diffraction.servalcat_version')
    @property
    def trans_NCS_details(self) -> Attribute:
        """A sentence giving the result of Xtriage's analysis on translational NCS. X-ray entry specific, obtained from the Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.trans_NCS_details')
    @property
    def twin_fraction(self) -> Attribute:
        """Estimated twinning fraction for operators as identified by Xtriage. A semicolon separated list of operators with fractions is givens  X-ray entry specific, obtained from the Xtriage program."""
        return Attribute('pdbx_vrpt_summary_diffraction.twin_fraction')

class Attr_PdbxVrptSummaryEm_2090535797322644506:
    """"""
    @property
    def Q_score(self) -> Attribute:
        """The overall Q-score of the fit of coordinates to the electron map. The Q-score is defined in Pintilie, GH. et al., Nature Methods, 17, 328-334 (2020)"""
        return Attribute('pdbx_vrpt_summary_em.Q_score')
    @property
    def atom_inclusion_all_atoms(self) -> Attribute:
        """The proportion of all non hydrogen atoms within density."""
        return Attribute('pdbx_vrpt_summary_em.atom_inclusion_all_atoms')
    @property
    def atom_inclusion_backbone(self) -> Attribute:
        """The proportion of backbone atoms within density."""
        return Attribute('pdbx_vrpt_summary_em.atom_inclusion_backbone')
    @property
    def author_provided_fsc_resolution_by_cutoff_halfbit(self) -> Attribute:
        """The resolution from the intersection of the author provided fsc and the indicator curve halfbit."""
        return Attribute('pdbx_vrpt_summary_em.author_provided_fsc_resolution_by_cutoff_halfbit')
    @property
    def author_provided_fsc_resolution_by_cutoff_onebit(self) -> Attribute:
        """The resolution from the intersection of the author provided fsc and the indicator curve onebit."""
        return Attribute('pdbx_vrpt_summary_em.author_provided_fsc_resolution_by_cutoff_onebit')
    @property
    def author_provided_fsc_resolution_by_cutoff_pt_143(self) -> Attribute:
        """The resolution from the intersection of the author provided fsc and the indicator curve 0.143."""
        return Attribute('pdbx_vrpt_summary_em.author_provided_fsc_resolution_by_cutoff_pt_143')
    @property
    def author_provided_fsc_resolution_by_cutoff_pt_333(self) -> Attribute:
        """The resolution from the intersection of the author provided fsc and the indicator curve 0.333."""
        return Attribute('pdbx_vrpt_summary_em.author_provided_fsc_resolution_by_cutoff_pt_333')
    @property
    def author_provided_fsc_resolution_by_cutoff_pt_5(self) -> Attribute:
        """The resolution from the intersection of the author provided fsc and the indicator curve 0.5."""
        return Attribute('pdbx_vrpt_summary_em.author_provided_fsc_resolution_by_cutoff_pt_5')
    @property
    def author_provided_fsc_resolution_by_cutoff_threesigma(self) -> Attribute:
        """The resolution from the intersection of the author provided fsc and the indicator curve threesigma."""
        return Attribute('pdbx_vrpt_summary_em.author_provided_fsc_resolution_by_cutoff_threesigma')
    @property
    def calculated_fsc_resolution_by_cutoff_halfbit(self) -> Attribute:
        """The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve halfbit."""
        return Attribute('pdbx_vrpt_summary_em.calculated_fsc_resolution_by_cutoff_halfbit')
    @property
    def calculated_fsc_resolution_by_cutoff_onebit(self) -> Attribute:
        """The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve onebit."""
        return Attribute('pdbx_vrpt_summary_em.calculated_fsc_resolution_by_cutoff_onebit')
    @property
    def calculated_fsc_resolution_by_cutoff_pt_143(self) -> Attribute:
        """The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve 0.143."""
        return Attribute('pdbx_vrpt_summary_em.calculated_fsc_resolution_by_cutoff_pt_143')
    @property
    def calculated_fsc_resolution_by_cutoff_pt_333(self) -> Attribute:
        """The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve 0.333."""
        return Attribute('pdbx_vrpt_summary_em.calculated_fsc_resolution_by_cutoff_pt_333')
    @property
    def calculated_fsc_resolution_by_cutoff_pt_5(self) -> Attribute:
        """The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve 0.5."""
        return Attribute('pdbx_vrpt_summary_em.calculated_fsc_resolution_by_cutoff_pt_5')
    @property
    def calculated_fsc_resolution_by_cutoff_threesigma(self) -> Attribute:
        """The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve threesigma."""
        return Attribute('pdbx_vrpt_summary_em.calculated_fsc_resolution_by_cutoff_threesigma')
    @property
    def contour_level_primary_map(self) -> Attribute:
        """The recommended contour level for the primary map of this deposition."""
        return Attribute('pdbx_vrpt_summary_em.contour_level_primary_map')
    @property
    def exp_method(self) -> Attribute:
        """Experimental method for statistics"""
        return Attribute('pdbx_vrpt_summary_em.exp_method')

class Attr_PdbxVrptSummaryGeometry_3987198781088756668:
    """"""
    @property
    def angles_RMSZ(self) -> Attribute:
        """The overall root mean square of the Z-score for deviations of bond angles in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
        return Attribute('pdbx_vrpt_summary_geometry.angles_RMSZ')
    @property
    def bonds_RMSZ(self) -> Attribute:
        """The overall root mean square of the Z-score for deviations of bond lengths in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
        return Attribute('pdbx_vrpt_summary_geometry.bonds_RMSZ')
    @property
    def clashscore(self) -> Attribute:
        """This score is derived from the number of pairs of atoms in the PDB_model_num that are unusually close to each other.  It is calculated by the MolProbity pdbx_vrpt_software and expressed as the number or such clashes per thousand atoms. For structures determined by NMR the clashscore value here will only consider label_atom_id pairs in the  well-defined (core) residues from ensemble analysis."""
        return Attribute('pdbx_vrpt_summary_geometry.clashscore')
    @property
    def clashscore_full_length(self) -> Attribute:
        """Only given for structures determined by NMR. The MolProbity pdbx_vrpt_instance_clashes score for all label_atom_id pairs."""
        return Attribute('pdbx_vrpt_summary_geometry.clashscore_full_length')
    @property
    def num_H_reduce(self) -> Attribute:
        """This is the number of hydrogen atoms added and optimized by the MolProbity reduce pdbx_vrpt_software as part of the all-atom clashscore."""
        return Attribute('pdbx_vrpt_summary_geometry.num_H_reduce')
    @property
    def num_angles_RMSZ(self) -> Attribute:
        """The number of bond angles compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
        return Attribute('pdbx_vrpt_summary_geometry.num_angles_RMSZ')
    @property
    def num_bonds_RMSZ(self) -> Attribute:
        """The number of bond lengths compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
        return Attribute('pdbx_vrpt_summary_geometry.num_bonds_RMSZ')
    @property
    def percent_ramachandran_outliers(self) -> Attribute:
        """The percentage of residues with Ramachandran outliers."""
        return Attribute('pdbx_vrpt_summary_geometry.percent_ramachandran_outliers')
    @property
    def percent_ramachandran_outliers_full_length(self) -> Attribute:
        """Only given for structures determined by NMR. The MolProbity Ramachandran outlier score for all atoms in the structure rather than just the well-defined (core) residues."""
        return Attribute('pdbx_vrpt_summary_geometry.percent_ramachandran_outliers_full_length')
    @property
    def percent_rotamer_outliers(self) -> Attribute:
        """The MolProbity sidechain outlier score (a percentage). Protein sidechains mostly adopt certain (combinations of) preferred torsion angle values  (called rotamers or rotameric conformers), much like their backbone torsion angles  (as assessed in the Ramachandran analysis). MolProbity considers the sidechain conformation  of a residue to be an outlier if its set of torsion angles is not similar to any preferred  combination. The sidechain outlier score is calculated as the percentage of residues  with an unusual sidechain conformation with respect to the total number of residues for  which the assessment is available. Example: percent-rota-outliers='2.44'. Specific to structure that contain protein chains and have sidechains modelled. For NMR structures only the  well-defined (core) residues from ensemble analysis will be considered. The percentage of residues with rotamer outliers."""
        return Attribute('pdbx_vrpt_summary_geometry.percent_rotamer_outliers')
    @property
    def percent_rotamer_outliers_full_length(self) -> Attribute:
        """Only given for structures determined by NMR. The MolProbity sidechain outlier score for all atoms in the structure rather than just the well-defined (core) residues."""
        return Attribute('pdbx_vrpt_summary_geometry.percent_rotamer_outliers_full_length')

class Attr_PdbxVrptSummaryNmr_1781281589840552930:
    """"""
    @property
    def chemical_shift_completeness(self) -> Attribute:
        """Overall completeness of the chemical shift assignments for the well-defined  regions of the structure."""
        return Attribute('pdbx_vrpt_summary_nmr.chemical_shift_completeness')
    @property
    def chemical_shift_completeness_full_length(self) -> Attribute:
        """Overall completeness of the chemical shift assignments for the full  macromolecule or complex as suggested by the molecular description of an entry (whether some portion of it is modelled or not)."""
        return Attribute('pdbx_vrpt_summary_nmr.chemical_shift_completeness_full_length')
    @property
    def cyrange_error(self) -> Attribute:
        """Diagnostic message from the wrapper of Cyrange software which identifies the  well-defined cores (domains) of NMR protein structures."""
        return Attribute('pdbx_vrpt_summary_nmr.cyrange_error')
    @property
    def cyrange_number_of_domains(self) -> Attribute:
        """Total number of well-defined cores (domains) identified by Cyrange"""
        return Attribute('pdbx_vrpt_summary_nmr.cyrange_number_of_domains')
    @property
    def exp_method(self) -> Attribute:
        """Experimental method for statistics"""
        return Attribute('pdbx_vrpt_summary_nmr.exp_method')
    @property
    def medoid_model(self) -> Attribute:
        """For each Cyrange well-defined core ('cyrange_domain') the id of the PDB_model_num which is most  similar to other models as measured by pairwise RMSDs over the domain.  For the whole entry ('Entry'), the medoid PDB_model_num of the largest core is taken as an overall representative of the structure."""
        return Attribute('pdbx_vrpt_summary_nmr.medoid_model')
    @property
    def nmr_models_consistency_flag(self) -> Attribute:
        """A flag indicating if all models in the NMR ensemble contain the exact  same atoms ('True') or if the models differ in this respect ('False')."""
        return Attribute('pdbx_vrpt_summary_nmr.nmr_models_consistency_flag')
    @property
    def nmrclust_error(self) -> Attribute:
        """Diagnostic message from the wrapper of NMRClust software which clusters NMR models."""
        return Attribute('pdbx_vrpt_summary_nmr.nmrclust_error')
    @property
    def nmrclust_number_of_clusters(self) -> Attribute:
        """Total number of clusters in the NMR ensemble identified by NMRClust."""
        return Attribute('pdbx_vrpt_summary_nmr.nmrclust_number_of_clusters')
    @property
    def nmrclust_number_of_models(self) -> Attribute:
        """Number of models analysed by NMRClust - should in almost all cases be the same as the number of models in the NMR ensemble."""
        return Attribute('pdbx_vrpt_summary_nmr.nmrclust_number_of_models')
    @property
    def nmrclust_number_of_outliers(self) -> Attribute:
        """Number of models that do not belong to any cluster as deemed by NMRClust."""
        return Attribute('pdbx_vrpt_summary_nmr.nmrclust_number_of_outliers')
    @property
    def nmrclust_representative_model(self) -> Attribute:
        """Overall representative PDB_model_num of the NMR ensemble as identified by NMRClust."""
        return Attribute('pdbx_vrpt_summary_nmr.nmrclust_representative_model')

class Attr_RcsbAccessionInfo_5412680110888487367:
    """"""
    @property
    def deposit_date(self) -> Attribute:
        """The entry deposition date."""
        return Attribute('rcsb_accession_info.deposit_date')
    @property
    def has_released_experimental_data(self) -> Attribute:
        """A code indicating the current availibility of experimental data in the repository."""
        return Attribute('rcsb_accession_info.has_released_experimental_data')
    @property
    def initial_release_date(self) -> Attribute:
        """The entry initial release date."""
        return Attribute('rcsb_accession_info.initial_release_date')
    @property
    def major_revision(self) -> Attribute:
        """The latest entry major revision number."""
        return Attribute('rcsb_accession_info.major_revision')
    @property
    def minor_revision(self) -> Attribute:
        """The latest entry minor revision number."""
        return Attribute('rcsb_accession_info.minor_revision')
    @property
    def revision_date(self) -> Attribute:
        """The latest entry revision date."""
        return Attribute('rcsb_accession_info.revision_date')
    @property
    def status_code(self) -> Attribute:
        """The release status for the entry."""
        return Attribute('rcsb_accession_info.status_code')

class Attr_RcsbBindingAffinity_2637605452600619135:
    """"""
    @property
    def comp_id(self) -> Attribute:
        """Ligand identifier."""
        return Attribute('rcsb_binding_affinity.comp_id')
    @property
    def link(self) -> Attribute:
        """Link to external resource referencing the data."""
        return Attribute('rcsb_binding_affinity.link')
    @property
    def provenance_code(self) -> Attribute:
        """The resource name for the related binding affinity reference."""
        return Attribute('rcsb_binding_affinity.provenance_code')
    @property
    def reference_sequence_identity(self) -> Attribute:
        """Data point provided by BindingDB. Percent identity between PDB sequence and reference sequence."""
        return Attribute('rcsb_binding_affinity.reference_sequence_identity')
    @property
    def symbol(self) -> Attribute:
        """Binding affinity symbol indicating approximate or precise strength of the binding."""
        return Attribute('rcsb_binding_affinity.symbol')
    @property
    def type(self) -> Attribute:
        """Binding affinity measurement given in one of the following types:  The concentration constants: IC50: the concentration of ligand that reduces enzyme activity by 50%;  EC50: the concentration of compound that generates a half-maximal response;  The binding constant:  Kd: dissociation constant;  Ka: association constant;  Ki: enzyme inhibition constant;  The thermodynamic parameters:  delta G: Gibbs free energy of binding (for association reaction);  delta H: change in enthalpy associated with a chemical reaction;  delta S: change in entropy associated with a chemical reaction."""
        return Attribute('rcsb_binding_affinity.type')
    @property
    def unit(self) -> Attribute:
        """Binding affinity unit.  Dissociation constant Kd is normally in molar units (or millimolar , micromolar, nanomolar, etc).  Association constant Ka is normally expressed in inverse molar units (e.g. M-1)."""
        return Attribute('rcsb_binding_affinity.unit')
    @property
    def value(self) -> Attribute:
        """Binding affinity value between a ligand and its target molecule."""
        return Attribute('rcsb_binding_affinity.value')

class Attr_RcsbCompModelProvenance_3545842955570420179:
    """"""
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier corresponding to the computed structure model."""
        return Attribute('rcsb_comp_model_provenance.entry_id')
    @property
    def source_db(self) -> Attribute:
        """Source database for the computed structure model."""
        return Attribute('rcsb_comp_model_provenance.source_db')
    @property
    def source_filename(self) -> Attribute:
        """Source filename for the computed structure model."""
        return Attribute('rcsb_comp_model_provenance.source_filename')
    @property
    def source_pae_url(self) -> Attribute:
        """Source URL for computed structure model predicted aligned error (PAE) json file."""
        return Attribute('rcsb_comp_model_provenance.source_pae_url')
    @property
    def source_url(self) -> Attribute:
        """Source URL for computed structure model file."""
        return Attribute('rcsb_comp_model_provenance.source_url')

class Attr_RcsbEntryContainerIdentifiers_1853475238367472706:
    """"""
    @property
    def assembly_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.assembly_ids')
    @property
    def branched_entity_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.branched_entity_ids')
    @property
    def emdb_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.emdb_ids')
    @property
    def entity_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.entity_ids')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_entry_container_identifiers.entry_id')
    @property
    def model_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.model_ids')
    @property
    def non_polymer_entity_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.non_polymer_entity_ids')
    @property
    def polymer_entity_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.polymer_entity_ids')
    @property
    def pubmed_id(self) -> Attribute:
        """Unique integer value assigned to each PubMed record."""
        return Attribute('rcsb_entry_container_identifiers.pubmed_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entry container."""
        return Attribute('rcsb_entry_container_identifiers.rcsb_id')
    @property
    def related_emdb_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.related_emdb_ids')
    @property
    def water_entity_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_container_identifiers.water_entity_ids')

class Attr_RcsbEntryGroupMembership_6556163331500770084:
    """"""
    @property
    def aggregation_method(self) -> Attribute:
        """Method used to establish group membership"""
        return Attribute('rcsb_entry_group_membership.aggregation_method')
    @property
    def group_id(self) -> Attribute:
        """A unique identifier for a group of entries"""
        return Attribute('rcsb_entry_group_membership.group_id')

class Attr_DiffrnResolutionHigh_2760660138162112179:
    """"""
    @property
    def provenance_source(self) -> Attribute:
        """The provenence source for the high resolution limit of data collection."""
        return Attribute('rcsb_entry_info.diffrn_resolution_high.provenance_source')
    @property
    def value(self) -> Attribute:
        """The high resolution limit of data collection."""
        return Attribute('rcsb_entry_info.diffrn_resolution_high.value')

class Attr_RcsbEntryInfo_9153466176300520716:
    """"""
    @property
    def assembly_count(self) -> Attribute:
        """The number of assemblies defined for this entry including the deposited assembly."""
        return Attribute('rcsb_entry_info.assembly_count')
    @property
    def branched_entity_count(self) -> Attribute:
        """The number of distinct branched entities in the structure entry."""
        return Attribute('rcsb_entry_info.branched_entity_count')
    @property
    def branched_molecular_weight_maximum(self) -> Attribute:
        """The maximum molecular mass (KDa) of a branched entity in the deposited structure entry."""
        return Attribute('rcsb_entry_info.branched_molecular_weight_maximum')
    @property
    def branched_molecular_weight_minimum(self) -> Attribute:
        """The minimum molecular mass (KDa) of a branched entity in the deposited structure entry."""
        return Attribute('rcsb_entry_info.branched_molecular_weight_minimum')
    @property
    def cis_peptide_count(self) -> Attribute:
        """The number of cis-peptide linkages per deposited structure model."""
        return Attribute('rcsb_entry_info.cis_peptide_count')
    @property
    def deposited_atom_count(self) -> Attribute:
        """The number of heavy atom coordinates records per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_atom_count')
    @property
    def deposited_deuterated_water_count(self) -> Attribute:
        """The number of deuterated water molecules per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_deuterated_water_count')
    @property
    def deposited_hydrogen_atom_count(self) -> Attribute:
        """The number of hydrogen atom coordinates records per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_hydrogen_atom_count')
    @property
    def deposited_model_count(self) -> Attribute:
        """The number of model structures deposited."""
        return Attribute('rcsb_entry_info.deposited_model_count')
    @property
    def deposited_modeled_polymer_monomer_count(self) -> Attribute:
        """The number of modeled polymer monomers in the deposited coordinate data.  This is the total count of monomers with reported coordinate data for all polymer  entity instances in the deposited coordinate data."""
        return Attribute('rcsb_entry_info.deposited_modeled_polymer_monomer_count')
    @property
    def deposited_nonpolymer_entity_instance_count(self) -> Attribute:
        """The number of non-polymer instances in the deposited data set.  This is the total count of non-polymer entity instances reported  per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_nonpolymer_entity_instance_count')
    @property
    def deposited_polymer_entity_instance_count(self) -> Attribute:
        """The number of polymer instances in the deposited data set.  This is the total count of polymer entity instances reported  per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_polymer_entity_instance_count')
    @property
    def deposited_polymer_monomer_count(self) -> Attribute:
        """The number of polymer monomers in sample entity instances in the deposited data set.  This is the total count of monomers for all polymer entity instances reported  per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_polymer_monomer_count')
    @property
    def deposited_solvent_atom_count(self) -> Attribute:
        """The number of heavy solvent atom coordinates records per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_solvent_atom_count')
    @property
    def deposited_unmodeled_polymer_monomer_count(self) -> Attribute:
        """The number of unmodeled polymer monomers in the deposited coordinate data. This is  the total count of monomers with unreported coordinate data for all polymer  entity instances per deposited structure model."""
        return Attribute('rcsb_entry_info.deposited_unmodeled_polymer_monomer_count')
    @property
    def diffrn_radiation_wavelength_maximum(self) -> Attribute:
        """The maximum radiation wavelength in angstroms."""
        return Attribute('rcsb_entry_info.diffrn_radiation_wavelength_maximum')
    @property
    def diffrn_radiation_wavelength_minimum(self) -> Attribute:
        """The minimum radiation wavelength in angstroms."""
        return Attribute('rcsb_entry_info.diffrn_radiation_wavelength_minimum')
    @property
    def disulfide_bond_count(self) -> Attribute:
        """The number of disulfide bonds per deposited structure model."""
        return Attribute('rcsb_entry_info.disulfide_bond_count')
    @property
    def entity_count(self) -> Attribute:
        """The number of distinct polymer, non-polymer, branched molecular, and solvent entities per deposited structure model."""
        return Attribute('rcsb_entry_info.entity_count')
    @property
    def experimental_method(self) -> Attribute:
        """The category of experimental method(s) used to determine the structure entry."""
        return Attribute('rcsb_entry_info.experimental_method')
    @property
    def experimental_method_count(self) -> Attribute:
        """The number of experimental methods contributing data to the structure determination."""
        return Attribute('rcsb_entry_info.experimental_method_count')
    @property
    def ihm_multi_scale_flag(self) -> Attribute:
        """Multi-scale modeling flag for integrative structures."""
        return Attribute('rcsb_entry_info.ihm_multi_scale_flag')
    @property
    def ihm_multi_state_flag(self) -> Attribute:
        """Multi-state modeling flag for integrative structures."""
        return Attribute('rcsb_entry_info.ihm_multi_state_flag')
    @property
    def ihm_ordered_state_flag(self) -> Attribute:
        """Ordered-state modeling flag for integrative structures."""
        return Attribute('rcsb_entry_info.ihm_ordered_state_flag')
    @property
    def ihm_structure_description(self) -> Attribute:
        """Description of the integrative structure."""
        return Attribute('rcsb_entry_info.ihm_structure_description')
    @property
    def inter_mol_covalent_bond_count(self) -> Attribute:
        """The number of intermolecular covalent bonds."""
        return Attribute('rcsb_entry_info.inter_mol_covalent_bond_count')
    @property
    def inter_mol_metalic_bond_count(self) -> Attribute:
        """The number of intermolecular metalic bonds."""
        return Attribute('rcsb_entry_info.inter_mol_metalic_bond_count')
    @property
    def molecular_weight(self) -> Attribute:
        """The molecular mass (KDa) of polymer and non-polymer entities (exclusive of solvent) in the deposited structure entry."""
        return Attribute('rcsb_entry_info.molecular_weight')
    @property
    def na_polymer_entity_types(self) -> Attribute:
        """Nucleic acid polymer entity type categories describing the entry."""
        return Attribute('rcsb_entry_info.na_polymer_entity_types')
    @property
    def ndb_struct_conf_na_feature_combined(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_info.ndb_struct_conf_na_feature_combined')
    @property
    def nonpolymer_bound_components(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_info.nonpolymer_bound_components')
    @property
    def nonpolymer_entity_count(self) -> Attribute:
        """The number of distinct non-polymer entities in the structure entry exclusive of solvent."""
        return Attribute('rcsb_entry_info.nonpolymer_entity_count')
    @property
    def nonpolymer_molecular_weight_maximum(self) -> Attribute:
        """The maximum molecular mass (KDa) of a non-polymer entity in the deposited structure entry."""
        return Attribute('rcsb_entry_info.nonpolymer_molecular_weight_maximum')
    @property
    def nonpolymer_molecular_weight_minimum(self) -> Attribute:
        """The minimum molecular mass (KDa) of a non-polymer entity in the deposited structure entry."""
        return Attribute('rcsb_entry_info.nonpolymer_molecular_weight_minimum')
    @property
    def polymer_composition(self) -> Attribute:
        """Categories describing the polymer entity composition for the entry."""
        return Attribute('rcsb_entry_info.polymer_composition')
    @property
    def polymer_entity_count(self) -> Attribute:
        """The number of distinct polymer entities in the structure entry."""
        return Attribute('rcsb_entry_info.polymer_entity_count')
    @property
    def polymer_entity_count_DNA(self) -> Attribute:
        """The number of distinct DNA polymer entities."""
        return Attribute('rcsb_entry_info.polymer_entity_count_DNA')
    @property
    def polymer_entity_count_RNA(self) -> Attribute:
        """The number of distinct RNA polymer entities."""
        return Attribute('rcsb_entry_info.polymer_entity_count_RNA')
    @property
    def polymer_entity_count_nucleic_acid(self) -> Attribute:
        """The number of distinct nucleic acid polymer entities (DNA or RNA)."""
        return Attribute('rcsb_entry_info.polymer_entity_count_nucleic_acid')
    @property
    def polymer_entity_count_nucleic_acid_hybrid(self) -> Attribute:
        """The number of distinct hybrid nucleic acid polymer entities."""
        return Attribute('rcsb_entry_info.polymer_entity_count_nucleic_acid_hybrid')
    @property
    def polymer_entity_count_protein(self) -> Attribute:
        """The number of distinct protein polymer entities."""
        return Attribute('rcsb_entry_info.polymer_entity_count_protein')
    @property
    def polymer_entity_taxonomy_count(self) -> Attribute:
        """The number of distinct taxonomies represented among the polymer entities in the entry."""
        return Attribute('rcsb_entry_info.polymer_entity_taxonomy_count')
    @property
    def polymer_molecular_weight_maximum(self) -> Attribute:
        """The maximum molecular mass (KDa) of a polymer entity in the deposited structure entry."""
        return Attribute('rcsb_entry_info.polymer_molecular_weight_maximum')
    @property
    def polymer_molecular_weight_minimum(self) -> Attribute:
        """The minimum molecular mass (KDa) of a polymer entity in the deposited structure entry."""
        return Attribute('rcsb_entry_info.polymer_molecular_weight_minimum')
    @property
    def polymer_monomer_count_maximum(self) -> Attribute:
        """The maximum monomer count of a polymer entity per deposited structure model."""
        return Attribute('rcsb_entry_info.polymer_monomer_count_maximum')
    @property
    def polymer_monomer_count_minimum(self) -> Attribute:
        """The minimum monomer count of a polymer entity per deposited structure model."""
        return Attribute('rcsb_entry_info.polymer_monomer_count_minimum')
    @property
    def representative_model(self) -> Attribute:
        """The chosen representative model."""
        return Attribute('rcsb_entry_info.representative_model')
    @property
    def resolution_combined(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_info.resolution_combined')
    @property
    def selected_polymer_entity_types(self) -> Attribute:
        """Selected polymer entity type categories describing the entry."""
        return Attribute('rcsb_entry_info.selected_polymer_entity_types')
    @property
    def software_programs_combined(self) -> Attribute:
        """"""
        return Attribute('rcsb_entry_info.software_programs_combined')
    @property
    def solvent_entity_count(self) -> Attribute:
        """The number of distinct solvent entities per deposited structure model."""
        return Attribute('rcsb_entry_info.solvent_entity_count')
    @property
    def structure_determination_methodology(self) -> Attribute:
        """Indicates if the structure was determined using experimental or computational methods."""
        return Attribute('rcsb_entry_info.structure_determination_methodology')
    @property
    def structure_determination_methodology_priority(self) -> Attribute:
        """Indicates the priority of the value in _rcsb_entry_info.structure_determination_methodology.  The lower the number the higher the priority.  Priority values for 'experimental' structures is currently set to 10 and  the values for 'computational' structures is set to 100."""
        return Attribute('rcsb_entry_info.structure_determination_methodology_priority')
    @property
    def diffrn_resolution_high(self) -> 'Attr_DiffrnResolutionHigh_2760660138162112179':
        """"""
        return Attr_DiffrnResolutionHigh_2760660138162112179()

class Attr_RcsbExternalReferences_35346722406294313:
    """"""
    @property
    def id(self) -> Attribute:
        """ID (accession) from external resource linked to this entry."""
        return Attribute('rcsb_external_references.id')
    @property
    def link(self) -> Attribute:
        """Link to this entry in external resource"""
        return Attribute('rcsb_external_references.link')
    @property
    def type(self) -> Attribute:
        """Internal identifier for external resources"""
        return Attribute('rcsb_external_references.type')

class Attr_RcsbIhmDatasetList_7444655874522715573:
    """"""
    @property
    def count(self) -> Attribute:
        """Number of input datasets used in integrative modeling."""
        return Attribute('rcsb_ihm_dataset_list.count')
    @property
    def name(self) -> Attribute:
        """Name of input dataset used in integrative modeling."""
        return Attribute('rcsb_ihm_dataset_list.name')
    @property
    def type(self) -> Attribute:
        """Type of input dataset used in integrative modeling."""
        return Attribute('rcsb_ihm_dataset_list.type')

class Attr_RcsbIhmDatasetSourceDbReference_4072845881100142479:
    """"""
    @property
    def accession_code(self) -> Attribute:
        """Accession code for the input dataset."""
        return Attribute('rcsb_ihm_dataset_source_db_reference.accession_code')
    @property
    def db_name(self) -> Attribute:
        """Name of the source database for the input dataset."""
        return Attribute('rcsb_ihm_dataset_source_db_reference.db_name')

class Attr_MaQaMetricGlobal_8328474904211466956:
    """"""
    @property
    def description(self) -> Attribute:
        """Description of the global QA metric."""
        return Attribute('rcsb_ma_qa_metric_global.ma_qa_metric_global.description')
    @property
    def name(self) -> Attribute:
        """Name of the global QA metric."""
        return Attribute('rcsb_ma_qa_metric_global.ma_qa_metric_global.name')
    @property
    def type(self) -> Attribute:
        """The type of global QA metric."""
        return Attribute('rcsb_ma_qa_metric_global.ma_qa_metric_global.type')
    @property
    def type_other_details(self) -> Attribute:
        """Details for other type of global QA metric."""
        return Attribute('rcsb_ma_qa_metric_global.ma_qa_metric_global.type_other_details')
    @property
    def value(self) -> Attribute:
        """Value of the global QA metric."""
        return Attribute('rcsb_ma_qa_metric_global.ma_qa_metric_global.value')

class Attr_RcsbMaQaMetricGlobal_6198698729975125693:
    """"""
    @property
    def model_id(self) -> Attribute:
        """The model identifier."""
        return Attribute('rcsb_ma_qa_metric_global.model_id')
    @property
    def ma_qa_metric_global(self) -> 'Attr_MaQaMetricGlobal_8328474904211466956':
        """"""
        return Attr_MaQaMetricGlobal_8328474904211466956()

class Attr_RcsbPrimaryCitation_7888783886584885968:
    """"""
    @property
    def book_id_ISBN(self) -> Attribute:
        """The International Standard Book Number (ISBN) code assigned to  the book cited; relevant for books or book chapters."""
        return Attribute('rcsb_primary_citation.book_id_ISBN')
    @property
    def book_publisher(self) -> Attribute:
        """The name of the publisher of the citation; relevant  for books or book chapters."""
        return Attribute('rcsb_primary_citation.book_publisher')
    @property
    def book_publisher_city(self) -> Attribute:
        """The location of the publisher of the citation; relevant  for books or book chapters."""
        return Attribute('rcsb_primary_citation.book_publisher_city')
    @property
    def book_title(self) -> Attribute:
        """The title of the book in which the citation appeared; relevant  for books or book chapters."""
        return Attribute('rcsb_primary_citation.book_title')
    @property
    def coordinate_linkage(self) -> Attribute:
        """_rcsb_primary_citation.coordinate_linkage states whether this citation  is concerned with precisely the set of coordinates given in the  data block. If, for instance, the publication described the same  structure, but the coordinates had undergone further refinement  prior to the creation of the data block, the value of this data  item would be 'no'."""
        return Attribute('rcsb_primary_citation.coordinate_linkage')
    @property
    def country(self) -> Attribute:
        """The country/region of publication; relevant for books  and book chapters."""
        return Attribute('rcsb_primary_citation.country')
    @property
    def id(self) -> Attribute:
        """The value of _rcsb_primary_citation.id must uniquely identify a record in the  CITATION list.   The _rcsb_primary_citation.id 'primary' should be used to indicate the  citation that the author(s) consider to be the most pertinent to  the contents of the data block.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('rcsb_primary_citation.id')
    @property
    def journal_abbrev(self) -> Attribute:
        """Abbreviated name of the cited journal as given in the  Chemical Abstracts Service Source Index."""
        return Attribute('rcsb_primary_citation.journal_abbrev')
    @property
    def journal_id_ASTM(self) -> Attribute:
        """The American Society for Testing and Materials (ASTM) code  assigned to the journal cited (also referred to as the CODEN  designator of the Chemical Abstracts Service); relevant for  journal articles."""
        return Attribute('rcsb_primary_citation.journal_id_ASTM')
    @property
    def journal_id_CSD(self) -> Attribute:
        """The Cambridge Structural Database (CSD) code assigned to the  journal cited; relevant for journal articles. This is also the  system used at the Protein Data Bank (PDB)."""
        return Attribute('rcsb_primary_citation.journal_id_CSD')
    @property
    def journal_id_ISSN(self) -> Attribute:
        """The International Standard Serial Number (ISSN) code assigned to  the journal cited; relevant for journal articles."""
        return Attribute('rcsb_primary_citation.journal_id_ISSN')
    @property
    def journal_issue(self) -> Attribute:
        """Issue number of the journal cited; relevant for journal  articles."""
        return Attribute('rcsb_primary_citation.journal_issue')
    @property
    def journal_volume(self) -> Attribute:
        """Volume number of the journal cited; relevant for journal  articles."""
        return Attribute('rcsb_primary_citation.journal_volume')
    @property
    def language(self) -> Attribute:
        """Language in which the cited article is written."""
        return Attribute('rcsb_primary_citation.language')
    @property
    def page_first(self) -> Attribute:
        """The first page of the citation; relevant for journal  articles, books and book chapters."""
        return Attribute('rcsb_primary_citation.page_first')
    @property
    def page_last(self) -> Attribute:
        """The last page of the citation; relevant for journal  articles, books and book chapters."""
        return Attribute('rcsb_primary_citation.page_last')
    @property
    def pdbx_database_id_DOI(self) -> Attribute:
        """Document Object Identifier used by doi.org to uniquely  specify bibliographic entry."""
        return Attribute('rcsb_primary_citation.pdbx_database_id_DOI')
    @property
    def pdbx_database_id_PubMed(self) -> Attribute:
        """Ascession number used by PubMed to categorize a specific  bibliographic entry."""
        return Attribute('rcsb_primary_citation.pdbx_database_id_PubMed')
    @property
    def rcsb_ORCID_identifiers(self) -> Attribute:
        """"""
        return Attribute('rcsb_primary_citation.rcsb_ORCID_identifiers')
    @property
    def rcsb_authors(self) -> Attribute:
        """"""
        return Attribute('rcsb_primary_citation.rcsb_authors')
    @property
    def rcsb_journal_abbrev(self) -> Attribute:
        """Normalized journal abbreviation."""
        return Attribute('rcsb_primary_citation.rcsb_journal_abbrev')
    @property
    def title(self) -> Attribute:
        """The title of the citation; relevant for journal articles, books  and book chapters."""
        return Attribute('rcsb_primary_citation.title')
    @property
    def year(self) -> Attribute:
        """The year of the citation; relevant for journal articles, books  and book chapters."""
        return Attribute('rcsb_primary_citation.year')

class Attr_Refine_7912134435919030599:
    """"""
    @property
    def B_iso_max(self) -> Attribute:
        """The maximum isotropic displacement parameter (B value)  found in the coordinate set."""
        return Attribute('refine.B_iso_max')
    @property
    def B_iso_mean(self) -> Attribute:
        """The mean isotropic displacement parameter (B value)  for the coordinate set."""
        return Attribute('refine.B_iso_mean')
    @property
    def B_iso_min(self) -> Attribute:
        """The minimum isotropic displacement parameter (B value)  found in the coordinate set."""
        return Attribute('refine.B_iso_min')
    @property
    def aniso_B_1_1(self) -> Attribute:
        """The [1][1] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
        return Attribute('refine.aniso_B_1_1')
    @property
    def aniso_B_1_2(self) -> Attribute:
        """The [1][2] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
        return Attribute('refine.aniso_B_1_2')
    @property
    def aniso_B_1_3(self) -> Attribute:
        """The [1][3] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
        return Attribute('refine.aniso_B_1_3')
    @property
    def aniso_B_2_2(self) -> Attribute:
        """The [2][2] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
        return Attribute('refine.aniso_B_2_2')
    @property
    def aniso_B_2_3(self) -> Attribute:
        """The [2][3] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
        return Attribute('refine.aniso_B_2_3')
    @property
    def aniso_B_3_3(self) -> Attribute:
        """The [3][3] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
        return Attribute('refine.aniso_B_3_3')
    @property
    def correlation_coeff_Fo_to_Fc(self) -> Attribute:
        """The correlation coefficient between the observed and              calculated structure factors for reflections included in              the refinement.               The correlation coefficient is scale-independent and gives              an idea of the quality of the refined model.                            sum~i~(Fo~i~ Fc~i~ - <Fo><Fc>) R~corr~ = ------------------------------------------------------------           SQRT{sum~i~(Fo~i~)^2^-<Fo>^2^} SQRT{sum~i~(Fc~i~)^2^-<Fc>^2^}               Fo = observed structure factors              Fc = calculated structure factors              <>   denotes average value               summation is over reflections included in the refinement"""
        return Attribute('refine.correlation_coeff_Fo_to_Fc')
    @property
    def correlation_coeff_Fo_to_Fc_free(self) -> Attribute:
        """The correlation coefficient between the observed and              calculated structure factors for reflections not included              in the refinement (free reflections).                The correlation coefficient is scale-independent and gives               an idea of the quality of the refined model.                            sum~i~(Fo~i~ Fc~i~ - <Fo><Fc>) R~corr~ = ------------------------------------------------------------           SQRT{sum~i~(Fo~i~)^2^-<Fo>^2^} SQRT{sum~i~(Fc~i~)^2^-<Fc>^2^}                Fo  = observed structure factors               Fc  = calculated structure factors               <>    denotes average value                summation is over reflections not included               in the refinement (free reflections)"""
        return Attribute('refine.correlation_coeff_Fo_to_Fc_free')
    @property
    def details(self) -> Attribute:
        """Description of special aspects of the refinement process."""
        return Attribute('refine.details')
    @property
    def ls_R_factor_R_free(self) -> Attribute:
        """Residual factor R for reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
        return Attribute('refine.ls_R_factor_R_free')
    @property
    def ls_R_factor_R_free_error(self) -> Attribute:
        """The estimated error in _refine.ls_R_factor_R_free.  The method used to estimate the error is described in the  item _refine.ls_R_factor_R_free_error_details."""
        return Attribute('refine.ls_R_factor_R_free_error')
    @property
    def ls_R_factor_R_free_error_details(self) -> Attribute:
        """Special aspects of the method used to estimated the error in  _refine.ls_R_factor_R_free."""
        return Attribute('refine.ls_R_factor_R_free_error_details')
    @property
    def ls_R_factor_R_work(self) -> Attribute:
        """Residual factor R for reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the working  reflections (i.e. were included in the refinement)  when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.   _refine.ls_R_factor_obs should not be confused with  _refine.ls_R_factor_R_work; the former reports the results of a  refinement in which all observed reflections were used, the  latter a refinement in which a subset of the observed  reflections were excluded from refinement for the calculation  of a 'free' R factor. However, it would be meaningful to quote  both values if a 'free' R factor were calculated for most of  the refinement, but all of the observed reflections were used  in the final rounds of refinement; such a protocol should be  explained in _refine.details.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
        return Attribute('refine.ls_R_factor_R_work')
    @property
    def ls_R_factor_all(self) -> Attribute:
        """Residual factor R for all reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
        return Attribute('refine.ls_R_factor_all')
    @property
    def ls_R_factor_obs(self) -> Attribute:
        """Residual factor R for reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion.   _refine.ls_R_factor_obs should not be confused with  _refine.ls_R_factor_R_work; the former reports the results of a  refinement in which all observed reflections were used, the  latter a refinement in which a subset of the observed  reflections were excluded from refinement for the calculation  of a 'free' R factor. However, it would be meaningful to quote  both values if a 'free' R factor were calculated for most of  the refinement, but all of the observed reflections were used  in the final rounds of refinement; such a protocol should be  explained in _refine.details.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
        return Attribute('refine.ls_R_factor_obs')
    @property
    def ls_d_res_high(self) -> Attribute:
        """The smallest value for the interplanar spacings for the  reflection data used in the refinement in angstroms. This is  called the highest resolution."""
        return Attribute('refine.ls_d_res_high')
    @property
    def ls_d_res_low(self) -> Attribute:
        """The largest value for the interplanar spacings for  the reflection data used in the refinement in angstroms.  This is called the lowest resolution."""
        return Attribute('refine.ls_d_res_low')
    @property
    def ls_matrix_type(self) -> Attribute:
        """Type of matrix used to accumulate the least-squares derivatives."""
        return Attribute('refine.ls_matrix_type')
    @property
    def ls_number_parameters(self) -> Attribute:
        """The number of parameters refined in the least-squares process.  If possible, this number should include some contribution from  the restrained parameters. The restrained parameters are  distinct from the constrained parameters (where one or more  parameters are linearly dependent on the refined value of  another). Least-squares restraints often depend on geometry or  energy considerations and this makes their direct contribution  to this number, and to the goodness-of-fit calculation,  difficult to assess."""
        return Attribute('refine.ls_number_parameters')
    @property
    def ls_number_reflns_R_free(self) -> Attribute:
        """The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details."""
        return Attribute('refine.ls_number_reflns_R_free')
    @property
    def ls_number_reflns_R_work(self) -> Attribute:
        """The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, and that were used as the working  reflections (i.e. were included in the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details."""
        return Attribute('refine.ls_number_reflns_R_work')
    @property
    def ls_number_reflns_all(self) -> Attribute:
        """The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low."""
        return Attribute('refine.ls_number_reflns_all')
    @property
    def ls_number_reflns_obs(self) -> Attribute:
        """The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion."""
        return Attribute('refine.ls_number_reflns_obs')
    @property
    def ls_number_restraints(self) -> Attribute:
        """The number of restrained parameters. These are parameters which  are not directly dependent on another refined parameter.  Restrained parameters often involve geometry or energy  dependencies.  See also _atom_site.constraints and _atom_site.refinement_flags.  A general description of refinement constraints may appear in  _refine.details."""
        return Attribute('refine.ls_number_restraints')
    @property
    def ls_percent_reflns_R_free(self) -> Attribute:
        """The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor,  expressed as a percentage of the number of geometrically  observable reflections that satisfy the resolution limits."""
        return Attribute('refine.ls_percent_reflns_R_free')
    @property
    def ls_percent_reflns_obs(self) -> Attribute:
        """The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, expressed as a percentage of the  number of geometrically observable reflections that satisfy  the resolution limits."""
        return Attribute('refine.ls_percent_reflns_obs')
    @property
    def ls_redundancy_reflns_all(self) -> Attribute:
        """The ratio of the total number of observations of the  reflections that satisfy the resolution limits established by  _refine.ls_d_res_high and _refine.ls_d_res_low to the number  of crystallographically unique reflections that satisfy the  same limits."""
        return Attribute('refine.ls_redundancy_reflns_all')
    @property
    def ls_redundancy_reflns_obs(self) -> Attribute:
        """The ratio of the total number of observations of the  reflections that satisfy the resolution limits established by  _refine.ls_d_res_high and _refine.ls_d_res_low and the  observation limit established by _reflns.observed_criterion to  the number of crystallographically unique reflections that  satisfy the same limits."""
        return Attribute('refine.ls_redundancy_reflns_obs')
    @property
    def ls_wR_factor_R_free(self) -> Attribute:
        """Weighted residual factor wR for reflections that satisfy the  resolution limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.        ( sum|w |Y~obs~ - Y~calc~|^2^| )^1/2^  wR = ( ---------------------------- )       (        sum|w Y~obs~^2^|      )   Y~obs~  = the observed amplitude specified by            _refine.ls_structure_factor_coef  Y~calc~ = the calculated amplitude specified by            _refine.ls_structure_factor_coef  w       = the least-squares weight   sum is taken over the specified reflections"""
        return Attribute('refine.ls_wR_factor_R_free')
    @property
    def ls_wR_factor_R_work(self) -> Attribute:
        """Weighted residual factor wR for reflections that satisfy the  resolution limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the working  reflections (i.e. were included in the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.        ( sum|w |Y~obs~ - Y~calc~|^2^| )^1/2^  wR = ( ---------------------------- )       (        sum|w Y~obs~^2^|      )   Y~obs~  = the observed amplitude specified by            _refine.ls_structure_factor_coef  Y~calc~ = the calculated amplitude specified by            _refine.ls_structure_factor_coef  w       = the least-squares weight   sum is taken over the specified reflections"""
        return Attribute('refine.ls_wR_factor_R_work')
    @property
    def occupancy_max(self) -> Attribute:
        """The maximum value for occupancy found in the coordinate set."""
        return Attribute('refine.occupancy_max')
    @property
    def occupancy_min(self) -> Attribute:
        """The minimum value for occupancy found in the coordinate set."""
        return Attribute('refine.occupancy_min')
    @property
    def overall_FOM_free_R_set(self) -> Attribute:
        """Average figure of merit of phases of reflections not included  in the refinement.   This value is derived from the likelihood function.   FOM           = I~1~(X)/I~0~(X)   I~0~, I~1~     = zero- and first-order modified Bessel functions                  of the first kind  X              = sigma~A~ |E~o~| |E~c~|/SIGMA  E~o~, E~c~     = normalized observed and calculated structure                  factors  sigma~A~       = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                  estimated using maximum likelihood  Sigma~P~       = sum~{atoms in model}~ f^2^  Sigma~N~       = sum~{atoms in crystal}~ f^2^  f              = form factor of atoms  delta~x~       = expected error  SIGMA          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]  sigma~{E;exp}~ = uncertainties of normalized observed                  structure factors  epsilon       = multiplicity of the diffracting plane   Ref: Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).       Acta Cryst. D53, 240-255."""
        return Attribute('refine.overall_FOM_free_R_set')
    @property
    def overall_FOM_work_R_set(self) -> Attribute:
        """Average figure of merit of phases of reflections included in  the refinement.   This value is derived from the likelihood function.   FOM           = I~1~(X)/I~0~(X)   I~0~, I~1~     = zero- and first-order modified Bessel functions                  of the first kind  X              = sigma~A~ |E~o~| |E~c~|/SIGMA  E~o~, E~c~     = normalized observed and calculated structure                  factors  sigma~A~       = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                  estimated using maximum likelihood  Sigma~P~       = sum~{atoms in model}~ f^2^  Sigma~N~       = sum~{atoms in crystal}~ f^2^  f              = form factor of atoms  delta~x~       = expected error  SIGMA          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]  sigma~{E;exp}~ = uncertainties of normalized observed                  structure factors  epsilon       = multiplicity of the diffracting plane   Ref: Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).       Acta Cryst. D53, 240-255."""
        return Attribute('refine.overall_FOM_work_R_set')
    @property
    def overall_SU_B(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)            of the displacement parameters based on a maximum-likelihood            residual.             The overall standard uncertainty (sigma~B~)^2^ gives an idea            of the uncertainty in the B values of averagely defined            atoms (atoms with B values equal to the average B value).                                           N~a~ (sigma~B~)^2^ = 8 ----------------------------------------------                   sum~i~ {[1/Sigma - (E~o~)^2^ (1-m^2^)](SUM_AS)s^4^}             N~a~           = number of atoms            E~o~           = normalized structure factors            m              = figure of merit of phases of reflections                             included in the summation            s              = reciprocal-space vector             SUM_AS         = (sigma~A~)^2^/Sigma^2^            Sigma          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]            sigma~{E;exp}~  = experimental uncertainties of normalized                             structure factors            sigma~A~        = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                             estimated using maximum likelihood            Sigma~P~        = sum~{atoms in model}~ f^2^            Sigma~N~        = sum~{atoms in crystal}~ f^2^            f               = atom form factor            delta~x~        = expected error            epsilon         = multiplicity of diffracting plane             summation is over all reflections included in refinement             Ref: (sigma~A~ estimation) 'Refinement of macromolecular                 structures by the maximum-likelihood method',                 Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).                 Acta Cryst. D53, 240-255.                  (SU B estimation) Murshudov, G. N. & Dodson,                 E. J. (1997). Simplified error estimation a la                 Cruickshank in macromolecular crystallography.                 CCP4 Newsletter on Protein Crystallography, No. 33,                 January 1997, pp. 31-39.                 http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
        return Attribute('refine.overall_SU_B')
    @property
    def overall_SU_ML(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)            of the positional parameters based on a maximum likelihood            residual.             The overall standard uncertainty (sigma~X~)^2^ gives an            idea of the uncertainty in the position of averagely            defined atoms (atoms with B values equal to average B value)                   3                         N~a~ (sigma~X~)^2^  = ---------------------------------------------------------                  8 pi^2^ sum~i~ {[1/Sigma - (E~o~)^2^ (1-m^2^)](SUM_AS)s^2^}             N~a~           = number of atoms            E~o~           = normalized structure factors            m              = figure of merit of phases of reflections                             included in the summation            s              = reciprocal-space vector             SUM_AS         = (sigma~A~)^2^/Sigma^2^            Sigma          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]            sigma~{E;exp}~  = experimental uncertainties of normalized                             structure factors            sigma~A~        = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                             estimated using maximum likelihood            Sigma~P~        = sum~{atoms in model}~ f^2^            Sigma~N~        = sum~{atoms in crystal}~ f^2^            f               = atom form factor            delta~x~        = expected error            epsilon         = multiplicity of diffracting plane             summation is over all reflections included in refinement             Ref: (sigma_A estimation) 'Refinement of macromolecular                 structures by the maximum-likelihood method',                 Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).                 Acta Cryst. D53, 240-255.                  (SU ML estimation) Murshudov, G. N. & Dodson,                 E. J. (1997). Simplified error estimation a la                 Cruickshank in macromolecular crystallography.                 CCP4 Newsletter on Protein Crystallography, No. 33,                 January 1997, pp. 31-39.                 http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
        return Attribute('refine.overall_SU_ML')
    @property
    def overall_SU_R_Cruickshank_DPI(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R value, expressed in a formalism known as the dispersion  precision indicator (DPI).   The overall standard uncertainty (sigma~B~) gives an idea  of the uncertainty in the B values of averagely defined  atoms (atoms with B values equal to the average B value).                          N~a~  (sigma~B~)^2^ = 0.65 ---------- (R~value~)^2^ (D~min~)^2^ C^-2/3^                       (N~o~-N~p~)    N~a~     = number of atoms included in refinement  N~o~     = number of observations  N~p~     = number of parameters refined  R~value~ = conventional crystallographic R value  D~min~   = maximum resolution  C        = completeness of data   Ref: Cruickshank, D. W. J. (1999). Acta Cryst. D55, 583-601.        Murshudov, G. N. & Dodson,       E. J. (1997). Simplified error estimation a la       Cruickshank in macromolecular crystallography.       CCP4 Newsletter on Protein Crystallography, No. 33,       January 1997, pp. 31-39.       http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
        return Attribute('refine.overall_SU_R_Cruickshank_DPI')
    @property
    def overall_SU_R_free(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the free R value.   The overall standard uncertainty (sigma~B~) gives an idea  of the uncertainty in the B values of averagely defined  atoms (atoms with B values equal to the average B value).                          N~a~  (sigma~B~)^2^ = 0.65 ---------- (R~free~)^2^ (D~min~)^2^ C^-2/3^                       (N~o~-N~p~)    N~a~     = number of atoms included in refinement  N~o~     = number of observations  N~p~     = number of parameters refined  R~free~  = conventional free crystallographic R value calculated           using reflections not included in refinement  D~min~   = maximum resolution  C        = completeness of data   Ref: Cruickshank, D. W. J. (1999). Acta Cryst. D55, 583-601.        Murshudov, G. N. & Dodson,       E. J. (1997). Simplified error estimation a la       Cruickshank in macromolecular crystallography.       CCP4 Newsletter on Protein Crystallography, No. 33,       January 1997, pp. 31-39.       http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
        return Attribute('refine.overall_SU_R_free')
    @property
    def pdbx_R_Free_selection_details(self) -> Attribute:
        """Details of the manner in which the cross validation  reflections were selected."""
        return Attribute('refine.pdbx_R_Free_selection_details')
    @property
    def pdbx_TLS_residual_ADP_flag(self) -> Attribute:
        """A flag for TLS refinements identifying the type of atomic displacement parameters stored  in _atom_site.B_iso_or_equiv."""
        return Attribute('refine.pdbx_TLS_residual_ADP_flag')
    @property
    def pdbx_average_fsc_free(self) -> Attribute:
        """Average Fourier Shell Correlation (avgFSC) between model and  observed structure factors for reflections not included in refinement.   The average FSC is a measure of the agreement between observed  and calculated structure factors.                    sum(N~i~ FSC~free-i~)  avgFSC~free~   = ---------------------                   sum(N~i~)    N~i~          = the number of free reflections in the resolution shell i  FSC~free-i~   = FSC for free reflections in the i-th resolution shell calculated as:                  (sum(|F~o~| |F~c~| fom cos(phi~c~-phi~o~)))  FSC~free-i~  = -------------------------------------------                 (sum(|F~o~|^2^) (sum(|F~c~|^2^)))^1/2^   |F~o~|   = amplitude of observed structure factor  |F~c~|   = amplitude of calculated structure factor  phi~o~   = phase of observed structure factor  phi~c~   = phase of calculated structure factor  fom      = figure of merit of the experimental phases.   Summation of FSC~free-i~ is carried over all free reflections in the resolution shell.   Summation of avgFSC~free~ is carried over all resolution shells.    Ref:  Rosenthal P.B., Henderson R.        'Optimal determination of particle orientation, absolute hand,        and contrast loss in single-particle electron cryomicroscopy.        Journal of Molecular Biology. 2003;333(4):721-745, equation (A6)."""
        return Attribute('refine.pdbx_average_fsc_free')
    @property
    def pdbx_average_fsc_overall(self) -> Attribute:
        """Overall average Fourier Shell Correlation (avgFSC) between model and  observed structure factors for all reflections.   The average FSC is a measure of the agreement between observed  and calculated structure factors.              sum(N~i~ FSC~i~)  avgFSC   = ----------------             sum(N~i~)    N~i~     = the number of all reflections in the resolution shell i  FSC~i~   = FSC for all reflections in the i-th resolution shell calculated as:             (sum(|F~o~| |F~c~| fom cos(phi~c~-phi~o~)))  FSC~i~  = -------------------------------------------            (sum(|F~o~|^2^) (sum(|F~c~|^2^)))^1/2^   |F~o~|   = amplitude of observed structure factor  |F~c~|   = amplitude of calculated structure factor  phi~o~   = phase of observed structure factor  phi~c~   = phase of calculated structure factor  fom      = figure of merit of the experimental phases.   Summation of FSC~i~ is carried over all reflections in the resolution shell.   Summation of avgFSC is carried over all resolution shells.    Ref:  Rosenthal P.B., Henderson R.        'Optimal determination of particle orientation, absolute hand,        and contrast loss in single-particle electron cryomicroscopy.        Journal of Molecular Biology. 2003;333(4):721-745, equation (A6)."""
        return Attribute('refine.pdbx_average_fsc_overall')
    @property
    def pdbx_average_fsc_work(self) -> Attribute:
        """Average Fourier Shell Correlation (avgFSC) between model and  observed structure factors for reflections included in refinement.   The average FSC is a measure of the agreement between observed  and calculated structure factors.                    sum(N~i~ FSC~work-i~)  avgFSC~work~   = ---------------------                   sum(N~i~)    N~i~          = the number of working reflections in the resolution shell i  FSC~work-i~   = FSC for working reflections in the i-th resolution shell calculated as:                  (sum(|F~o~| |F~c~| fom cos(phi~c~-phi~o~)))  FSC~work-i~  = -------------------------------------------                 (sum(|F~o~|^2^) (sum(|F~c~|^2^)))^1/2^   |F~o~|   = amplitude of observed structure factor  |F~c~|   = amplitude of calculated structure factor  phi~o~   = phase of observed structure factor  phi~c~   = phase of calculated structure factor  fom      = figure of merit of the experimental phases.   Summation of FSC~work-i~ is carried over all working reflections in the resolution shell.   Summation of avgFSC~work~ is carried over all resolution shells.    Ref:  Rosenthal P.B., Henderson R.        'Optimal determination of particle orientation, absolute hand,        and contrast loss in single-particle electron cryomicroscopy.        Journal of Molecular Biology. 2003;333(4):721-745, equation (A6)."""
        return Attribute('refine.pdbx_average_fsc_work')
    @property
    def pdbx_data_cutoff_high_absF(self) -> Attribute:
        """Value of F at 'high end' of data cutoff."""
        return Attribute('refine.pdbx_data_cutoff_high_absF')
    @property
    def pdbx_data_cutoff_high_rms_absF(self) -> Attribute:
        """Value of RMS |F| used as high data cutoff."""
        return Attribute('refine.pdbx_data_cutoff_high_rms_absF')
    @property
    def pdbx_data_cutoff_low_absF(self) -> Attribute:
        """Value of F at 'low end' of data cutoff."""
        return Attribute('refine.pdbx_data_cutoff_low_absF')
    @property
    def pdbx_diffrn_id(self) -> Attribute:
        """"""
        return Attribute('refine.pdbx_diffrn_id')
    @property
    def pdbx_isotropic_thermal_model(self) -> Attribute:
        """Whether the structure was refined with indvidual isotropic, anisotropic or overall temperature factor."""
        return Attribute('refine.pdbx_isotropic_thermal_model')
    @property
    def pdbx_ls_cross_valid_method(self) -> Attribute:
        """Whether the cross validataion method was used through out or only at the end."""
        return Attribute('refine.pdbx_ls_cross_valid_method')
    @property
    def pdbx_ls_sigma_F(self) -> Attribute:
        """Data cutoff (SIGMA(F))"""
        return Attribute('refine.pdbx_ls_sigma_F')
    @property
    def pdbx_ls_sigma_Fsqd(self) -> Attribute:
        """Data cutoff (SIGMA(F^2))"""
        return Attribute('refine.pdbx_ls_sigma_Fsqd')
    @property
    def pdbx_ls_sigma_I(self) -> Attribute:
        """Data cutoff (SIGMA(I))"""
        return Attribute('refine.pdbx_ls_sigma_I')
    @property
    def pdbx_method_to_determine_struct(self) -> Attribute:
        """Method(s) used to determine the structure."""
        return Attribute('refine.pdbx_method_to_determine_struct')
    @property
    def pdbx_overall_ESU_R(self) -> Attribute:
        """Overall estimated standard uncertainties of positional  parameters based on R value."""
        return Attribute('refine.pdbx_overall_ESU_R')
    @property
    def pdbx_overall_ESU_R_Free(self) -> Attribute:
        """Overall estimated standard uncertainties of positional parameters based on R free value."""
        return Attribute('refine.pdbx_overall_ESU_R_Free')
    @property
    def pdbx_overall_SU_R_Blow_DPI(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R value, expressed in a formalism known as the dispersion  precision indicator (DPI).   Ref: Blow, D (2002) Acta Cryst. D58, 792-797"""
        return Attribute('refine.pdbx_overall_SU_R_Blow_DPI')
    @property
    def pdbx_overall_SU_R_free_Blow_DPI(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R-free value, expressed in a formalism known as the dispersion  precision indicator (DPI).   Ref: Blow, D (2002) Acta Cryst. D58, 792-797"""
        return Attribute('refine.pdbx_overall_SU_R_free_Blow_DPI')
    @property
    def pdbx_overall_SU_R_free_Cruickshank_DPI(self) -> Attribute:
        """The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R-free value, expressed in a formalism known as the dispersion  precision indicator (DPI).   Ref: Cruickshank, D. W. J. (1999). Acta Cryst. D55, 583-601."""
        return Attribute('refine.pdbx_overall_SU_R_free_Cruickshank_DPI')
    @property
    def pdbx_overall_phase_error(self) -> Attribute:
        """The overall phase error for all reflections after refinement using  the current refinement target."""
        return Attribute('refine.pdbx_overall_phase_error')
    @property
    def pdbx_refine_id(self) -> Attribute:
        """This data item uniquely identifies a refinement within an entry.  _refine.pdbx_refine_id can be used to distinguish the results of  joint refinements."""
        return Attribute('refine.pdbx_refine_id')
    @property
    def pdbx_solvent_ion_probe_radii(self) -> Attribute:
        """For bulk solvent mask calculation, the amount that the ionic radii of atoms, which can be ions, are increased used."""
        return Attribute('refine.pdbx_solvent_ion_probe_radii')
    @property
    def pdbx_solvent_shrinkage_radii(self) -> Attribute:
        """For bulk solvent mask calculation, amount mask is shrunk after taking away atoms with new radii and a constant value assigned to this new region."""
        return Attribute('refine.pdbx_solvent_shrinkage_radii')
    @property
    def pdbx_solvent_vdw_probe_radii(self) -> Attribute:
        """For bulk solvent mask calculation, the value by which the vdw radii of non-ion atoms (like carbon) are increased and used."""
        return Attribute('refine.pdbx_solvent_vdw_probe_radii')
    @property
    def pdbx_starting_model(self) -> Attribute:
        """Starting model for refinement.  Starting model for  molecular replacement should refer to a previous  structure or experiment."""
        return Attribute('refine.pdbx_starting_model')
    @property
    def pdbx_stereochem_target_val_spec_case(self) -> Attribute:
        """Special case of stereochemistry target values used in SHELXL refinement."""
        return Attribute('refine.pdbx_stereochem_target_val_spec_case')
    @property
    def pdbx_stereochemistry_target_values(self) -> Attribute:
        """Stereochemistry target values used in refinement."""
        return Attribute('refine.pdbx_stereochemistry_target_values')
    @property
    def solvent_model_details(self) -> Attribute:
        """Special aspects of the solvent model used during refinement."""
        return Attribute('refine.solvent_model_details')
    @property
    def solvent_model_param_bsol(self) -> Attribute:
        """The value of the BSOL solvent-model parameter describing  the average isotropic displacement parameter of disordered  solvent atoms.   This is one of the two parameters (the other is  _refine.solvent_model_param_ksol) in Tronrud's method of  modelling the contribution of bulk solvent to the  scattering. The standard scale factor is modified according  to the expression       k0 exp(-B0 * s^2^)[1-KSOL * exp(-BSOL * s^2^)]   where k0 and B0 are the scale factors for the protein.   Ref: Tronrud, D. E. (1997). Methods Enzymol. 277, 243-268."""
        return Attribute('refine.solvent_model_param_bsol')
    @property
    def solvent_model_param_ksol(self) -> Attribute:
        """The value of the KSOL solvent-model parameter describing  the ratio of the electron density in the bulk solvent to the  electron density in the molecular solute.   This is one of the two parameters (the other is  _refine.solvent_model_param_bsol) in Tronrud's method of  modelling the contribution of bulk solvent to the  scattering. The standard scale factor is modified according  to the expression       k0 exp(-B0 * s^2^)[1-KSOL * exp(-BSOL * s^2^)]   where k0 and B0 are the scale factors for the protein.   Ref: Tronrud, D. E. (1997). Methods Enzymol. 277, 243-268."""
        return Attribute('refine.solvent_model_param_ksol')

class Attr_RefineAnalyze_3766990047408157880:
    """"""
    @property
    def Luzzati_coordinate_error_free(self) -> Attribute:
        """The estimated coordinate error obtained from the plot of  the R value versus sin(theta)/lambda for the reflections  treated as a test set during refinement.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
        return Attribute('refine_analyze.Luzzati_coordinate_error_free')
    @property
    def Luzzati_coordinate_error_obs(self) -> Attribute:
        """The estimated coordinate error obtained from the plot of  the R value versus sin(theta)/lambda for reflections classified  as observed.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
        return Attribute('refine_analyze.Luzzati_coordinate_error_obs')
    @property
    def Luzzati_d_res_low_free(self) -> Attribute:
        """The value of the low-resolution cutoff used in constructing the  Luzzati plot for reflections treated as a test set during  refinement.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
        return Attribute('refine_analyze.Luzzati_d_res_low_free')
    @property
    def Luzzati_d_res_low_obs(self) -> Attribute:
        """The value of the low-resolution cutoff used in  constructing the Luzzati plot for reflections classified as  observed.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
        return Attribute('refine_analyze.Luzzati_d_res_low_obs')
    @property
    def Luzzati_sigma_a_free(self) -> Attribute:
        """The value of sigma~a~ used in constructing the Luzzati plot for  the reflections treated as a test set during refinement.  Details of the estimation of sigma~a~ can be specified  in _refine_analyze.Luzzati_sigma_a_free_details.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
        return Attribute('refine_analyze.Luzzati_sigma_a_free')
    @property
    def Luzzati_sigma_a_obs(self) -> Attribute:
        """The value of sigma~a~ used in constructing the Luzzati plot for  reflections classified as observed. Details of the  estimation of sigma~a~ can be specified in  _refine_analyze.Luzzati_sigma_a_obs_details.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
        return Attribute('refine_analyze.Luzzati_sigma_a_obs')
    @property
    def number_disordered_residues(self) -> Attribute:
        """The number of discretely disordered residues in the refined  model."""
        return Attribute('refine_analyze.number_disordered_residues')
    @property
    def occupancy_sum_hydrogen(self) -> Attribute:
        """The sum of the occupancies of the hydrogen atoms in the refined  model."""
        return Attribute('refine_analyze.occupancy_sum_hydrogen')
    @property
    def occupancy_sum_non_hydrogen(self) -> Attribute:
        """The sum of the occupancies of the non-hydrogen atoms in the   refined model."""
        return Attribute('refine_analyze.occupancy_sum_non_hydrogen')
    @property
    def pdbx_Luzzati_d_res_high_obs(self) -> Attribute:
        """record the high resolution for calculating Luzzati statistics."""
        return Attribute('refine_analyze.pdbx_Luzzati_d_res_high_obs')
    @property
    def pdbx_refine_id(self) -> Attribute:
        """This data item uniquely identifies a refinement within an entry.  _refine_analyze.pdbx_refine_id can be used to distinguish the results  of joint refinements."""
        return Attribute('refine_analyze.pdbx_refine_id')

class Attr_RefineHist_8709642682844207763:
    """"""
    @property
    def cycle_id(self) -> Attribute:
        """The value of _refine_hist.cycle_id must uniquely identify a  record in the REFINE_HIST list.   Note that this item need not be a number; it can be any unique  identifier."""
        return Attribute('refine_hist.cycle_id')
    @property
    def d_res_high(self) -> Attribute:
        """The lowest value for the interplanar spacings for the  reflection data for this cycle of refinement. This is called  the highest resolution."""
        return Attribute('refine_hist.d_res_high')
    @property
    def d_res_low(self) -> Attribute:
        """The highest value for the interplanar spacings for the  reflection data for this cycle of refinement. This is  called the lowest resolution."""
        return Attribute('refine_hist.d_res_low')
    @property
    def number_atoms_solvent(self) -> Attribute:
        """The number of solvent atoms that were included in the model at  this cycle of the refinement."""
        return Attribute('refine_hist.number_atoms_solvent')
    @property
    def number_atoms_total(self) -> Attribute:
        """The total number of atoms that were included in the model at  this cycle of the refinement."""
        return Attribute('refine_hist.number_atoms_total')
    @property
    def pdbx_B_iso_mean_ligand(self) -> Attribute:
        """Mean isotropic B-value for ligand molecules included in refinement."""
        return Attribute('refine_hist.pdbx_B_iso_mean_ligand')
    @property
    def pdbx_B_iso_mean_solvent(self) -> Attribute:
        """Mean isotropic B-value for solvent molecules included in refinement."""
        return Attribute('refine_hist.pdbx_B_iso_mean_solvent')
    @property
    def pdbx_number_atoms_ligand(self) -> Attribute:
        """Number of ligand atoms included in refinement"""
        return Attribute('refine_hist.pdbx_number_atoms_ligand')
    @property
    def pdbx_number_atoms_nucleic_acid(self) -> Attribute:
        """Number of nucleic atoms included in refinement"""
        return Attribute('refine_hist.pdbx_number_atoms_nucleic_acid')
    @property
    def pdbx_number_atoms_protein(self) -> Attribute:
        """Number of protein atoms included in refinement"""
        return Attribute('refine_hist.pdbx_number_atoms_protein')
    @property
    def pdbx_number_residues_total(self) -> Attribute:
        """Total number of polymer residues included in refinement."""
        return Attribute('refine_hist.pdbx_number_residues_total')
    @property
    def pdbx_refine_id(self) -> Attribute:
        """This data item uniquely identifies a refinement within an entry.  _refine_hist.pdbx_refine_id can be used to distinguish the results  of joint refinements."""
        return Attribute('refine_hist.pdbx_refine_id')

class Attr_RefineLsRestr_7134436328750966974:
    """"""
    @property
    def dev_ideal(self) -> Attribute:
        """For the given parameter type, the root-mean-square deviation  between the ideal values used as restraints in the least-squares  refinement and the values obtained by refinement. For instance,  bond distances may deviate by 0.018 /%A (r.m.s.) from ideal  values in the current model."""
        return Attribute('refine_ls_restr.dev_ideal')
    @property
    def dev_ideal_target(self) -> Attribute:
        """For the given parameter type, the target root-mean-square  deviation between the ideal values used as restraints in the  least-squares refinement and the values obtained by refinement."""
        return Attribute('refine_ls_restr.dev_ideal_target')
    @property
    def number(self) -> Attribute:
        """The number of parameters of this type subjected to restraint in  least-squares refinement."""
        return Attribute('refine_ls_restr.number')
    @property
    def pdbx_refine_id(self) -> Attribute:
        """This data item uniquely identifies a refinement within an entry.  _refine_ls_restr.pdbx_refine_id can be used to distinguish the results  of joint refinements."""
        return Attribute('refine_ls_restr.pdbx_refine_id')
    @property
    def pdbx_restraint_function(self) -> Attribute:
        """The functional form of the restraint function used in the least-squares  refinement."""
        return Attribute('refine_ls_restr.pdbx_restraint_function')
    @property
    def type(self) -> Attribute:
        """The type of the parameter being restrained.  Explicit sets of data values are provided for the programs  PROTIN/PROLSQ (beginning with p_) and RESTRAIN (beginning with  RESTRAIN_). As computer programs change, these data values  are given as examples, not as an enumeration list. Computer  programs that convert a data block to a refinement table will  expect the exact form of the data values given here to be used."""
        return Attribute('refine_ls_restr.type')
    @property
    def weight(self) -> Attribute:
        """The weighting value applied to this type of restraint in  the least-squares refinement."""
        return Attribute('refine_ls_restr.weight')

class Attr_Reflns_4430294562024073293:
    """"""
    @property
    def B_iso_Wilson_estimate(self) -> Attribute:
        """The value of the overall isotropic displacement parameter  estimated from the slope of the Wilson plot."""
        return Attribute('reflns.B_iso_Wilson_estimate')
    @property
    def R_free_details(self) -> Attribute:
        """A description of the method by which a subset of reflections was  selected for exclusion from refinement so as to be used in the  calculation of a 'free' R factor."""
        return Attribute('reflns.R_free_details')
    @property
    def Rmerge_F_all(self) -> Attribute:
        """Residual factor Rmerge for all reflections that satisfy the  resolution limits established by _reflns.d_resolution_high  and _reflns.d_resolution_low.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
        return Attribute('reflns.Rmerge_F_all')
    @property
    def Rmerge_F_obs(self) -> Attribute:
        """Residual factor Rmerge for reflections that satisfy the  resolution limits established by _reflns.d_resolution_high  and _reflns.d_resolution_low and the observation limit  established by _reflns.observed_criterion.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
        return Attribute('reflns.Rmerge_F_obs')
    @property
    def d_resolution_high(self) -> Attribute:
        """The smallest value in angstroms for the interplanar spacings  for the reflection data. This is called the highest resolution."""
        return Attribute('reflns.d_resolution_high')
    @property
    def d_resolution_low(self) -> Attribute:
        """The largest value in angstroms for the interplanar spacings  for the reflection data. This is called the lowest resolution."""
        return Attribute('reflns.d_resolution_low')
    @property
    def data_reduction_details(self) -> Attribute:
        """A description of special aspects of the data-reduction  procedures."""
        return Attribute('reflns.data_reduction_details')
    @property
    def data_reduction_method(self) -> Attribute:
        """The method used for data reduction.   Note that this is not the computer program used, which is  described in the SOFTWARE category, but the method  itself.   This data item should be used to describe significant  methodological options used within the data-reduction programs."""
        return Attribute('reflns.data_reduction_method')
    @property
    def details(self) -> Attribute:
        """A description of reflection data not covered by other data  names. This should include details of the Friedel pairs."""
        return Attribute('reflns.details')
    @property
    def limit_h_max(self) -> Attribute:
        """Maximum value of the Miller index h for the reflection data. This  need not have the same value as _diffrn_reflns.limit_h_max."""
        return Attribute('reflns.limit_h_max')
    @property
    def limit_h_min(self) -> Attribute:
        """Minimum value of the Miller index h for the reflection data. This  need not have the same value as _diffrn_reflns.limit_h_min."""
        return Attribute('reflns.limit_h_min')
    @property
    def limit_k_max(self) -> Attribute:
        """Maximum value of the Miller index k for the reflection data. This  need not have the same value as _diffrn_reflns.limit_k_max."""
        return Attribute('reflns.limit_k_max')
    @property
    def limit_k_min(self) -> Attribute:
        """Minimum value of the Miller index k for the reflection data. This  need not have the same value as _diffrn_reflns.limit_k_min."""
        return Attribute('reflns.limit_k_min')
    @property
    def limit_l_max(self) -> Attribute:
        """Maximum value of the Miller index l for the reflection data. This  need not have the same value as _diffrn_reflns.limit_l_max."""
        return Attribute('reflns.limit_l_max')
    @property
    def limit_l_min(self) -> Attribute:
        """Minimum value of the Miller index l for the reflection data. This  need not have the same value as _diffrn_reflns.limit_l_min."""
        return Attribute('reflns.limit_l_min')
    @property
    def number_all(self) -> Attribute:
        """The total number of reflections in the REFLN list (not the  DIFFRN_REFLN list). This number may contain Friedel-equivalent  reflections according to the nature of the structure and the  procedures used. The item _reflns.details describes the  reflection data."""
        return Attribute('reflns.number_all')
    @property
    def number_obs(self) -> Attribute:
        """The number of reflections in the REFLN list (not the DIFFRN_REFLN  list) classified as observed (see _reflns.observed_criterion).  This number may contain Friedel-equivalent reflections according  to the nature of the structure and the procedures used."""
        return Attribute('reflns.number_obs')
    @property
    def observed_criterion(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'. This  criterion is usually expressed in terms of a sigma(I) or  sigma(F) threshold."""
        return Attribute('reflns.observed_criterion')
    @property
    def observed_criterion_F_max(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'  expressed as an upper limit for the value of F."""
        return Attribute('reflns.observed_criterion_F_max')
    @property
    def observed_criterion_F_min(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'  expressed as a lower limit for the value of F."""
        return Attribute('reflns.observed_criterion_F_min')
    @property
    def observed_criterion_I_max(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'  expressed as an upper limit for the value of I."""
        return Attribute('reflns.observed_criterion_I_max')
    @property
    def observed_criterion_I_min(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'  expressed as a lower limit for the value of I."""
        return Attribute('reflns.observed_criterion_I_min')
    @property
    def observed_criterion_sigma_F(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'  expressed as a multiple of the value of sigma(F)."""
        return Attribute('reflns.observed_criterion_sigma_F')
    @property
    def observed_criterion_sigma_I(self) -> Attribute:
        """The criterion used to classify a reflection as 'observed'  expressed as a multiple of the value of sigma(I)."""
        return Attribute('reflns.observed_criterion_sigma_I')
    @property
    def pdbx_CC_half(self) -> Attribute:
        """The Pearson's correlation coefficient expressed as a decimal value               between the average intensities from randomly selected               half-datasets.  	      Ref: Karplus & Diederichs (2012), Science 336, 1030-33"""
        return Attribute('reflns.pdbx_CC_half')
    @property
    def pdbx_R_split(self) -> Attribute:
        """R split measures the agreement between the sets of intensities created by merging               odd- and even-numbered images  from the overall data.  	      Ref: T. A. White, R. A. Kirian, A. V. Martin, A. Aquila, K. Nass, A. Barty               and H. N. Chapman (2012), J. Appl. Cryst. 45, 335-341"""
        return Attribute('reflns.pdbx_R_split')
    @property
    def pdbx_Rmerge_I_obs(self) -> Attribute:
        """The R value for merging intensities satisfying the observed  criteria in this data set."""
        return Attribute('reflns.pdbx_Rmerge_I_obs')
    @property
    def pdbx_Rpim_I_all(self) -> Attribute:
        """The precision-indicating merging R factor value Rpim,  for merging all intensities in this data set.          sum~i~ [1/(N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |  Rpim = --------------------------------------------------                       sum~i~ ( sum~j~ I~j~ )   I~j~   = the intensity of the jth observation of reflection i  <I~i~> = the mean of the intensities of all observations           of reflection i  N~i~   = the redundancy (the number of times reflection i           has been measured).   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection.   Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.       Biol. 4, 269-275.       Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.       30, 203-205.       Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
        return Attribute('reflns.pdbx_Rpim_I_all')
    @property
    def pdbx_Rrim_I_all(self) -> Attribute:
        """The redundancy-independent merging R factor value Rrim,               also denoted Rmeas, for merging all intensities in this               data set.                       sum~i~ [N~i~/(N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |               Rrim = ----------------------------------------------------                                   sum~i~ ( sum~j~ I~j~ )                I~j~   = the intensity of the jth observation of reflection i               <I~i~> = the mean of the intensities of all observations of                        reflection i 	       N~i~   = the redundancy (the number of times reflection i                        has been measured).                sum~i~ is taken over all reflections               sum~j~ is taken over all observations of each reflection.                Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.                    Biol. 4, 269-275.                    Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.                    30, 203-205.                    Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
        return Attribute('reflns.pdbx_Rrim_I_all')
    @property
    def pdbx_Rsym_value(self) -> Attribute:
        """The R sym value as a decimal number."""
        return Attribute('reflns.pdbx_Rsym_value')
    @property
    def pdbx_chi_squared(self) -> Attribute:
        """Overall  Chi-squared statistic."""
        return Attribute('reflns.pdbx_chi_squared')
    @property
    def pdbx_diffrn_id(self) -> Attribute:
        """"""
        return Attribute('reflns.pdbx_diffrn_id')
    @property
    def pdbx_netI_over_av_sigmaI(self) -> Attribute:
        """The ratio of the average intensity to the average uncertainty,  <I>/<sigma(I)>."""
        return Attribute('reflns.pdbx_netI_over_av_sigmaI')
    @property
    def pdbx_netI_over_sigmaI(self) -> Attribute:
        """The mean of the ratio of the intensities to their  standard uncertainties, <I/sigma(I)>."""
        return Attribute('reflns.pdbx_netI_over_sigmaI')
    @property
    def pdbx_number_measured_all(self) -> Attribute:
        """Total number of measured reflections."""
        return Attribute('reflns.pdbx_number_measured_all')
    @property
    def pdbx_ordinal(self) -> Attribute:
        """An ordinal identifier for this set of reflection statistics."""
        return Attribute('reflns.pdbx_ordinal')
    @property
    def pdbx_redundancy(self) -> Attribute:
        """Overall redundancy for this data set."""
        return Attribute('reflns.pdbx_redundancy')
    @property
    def pdbx_scaling_rejects(self) -> Attribute:
        """Number of reflections rejected in scaling operations."""
        return Attribute('reflns.pdbx_scaling_rejects')
    @property
    def percent_possible_obs(self) -> Attribute:
        """The percentage of geometrically possible reflections represented  by reflections that satisfy the resolution limits established  by _reflns.d_resolution_high and _reflns.d_resolution_low and  the observation limit established by  _reflns.observed_criterion."""
        return Attribute('reflns.percent_possible_obs')
    @property
    def phase_calculation_details(self) -> Attribute:
        """The value of _reflns.phase_calculation_details describes a  special details about calculation of phases in _refln.phase_calc."""
        return Attribute('reflns.phase_calculation_details')

class Attr_ReflnsShell_7995187720501940459:
    """"""
    @property
    def Rmerge_F_all(self) -> Attribute:
        """Residual factor Rmerge for all reflections that satisfy the  resolution limits established by _reflns_shell.d_res_high and  _reflns_shell.d_res_low.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
        return Attribute('reflns_shell.Rmerge_F_all')
    @property
    def Rmerge_F_obs(self) -> Attribute:
        """Residual factor Rmerge for reflections that satisfy the  resolution limits established by _reflns_shell.d_res_high and  _reflns_shell.d_res_low and the observation criterion  established by _reflns.observed_criterion.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
        return Attribute('reflns_shell.Rmerge_F_obs')
    @property
    def Rmerge_I_all(self) -> Attribute:
        """The value of Rmerge(I) for all reflections in a given shell.               sum~i~(sum~j~|I~j~ - <I>|)  Rmerge(I) = --------------------------                  sum~i~(sum~j~<I>)   I~j~ = the intensity of the jth observation of reflection i  <I>  = the mean of the intensities of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
        return Attribute('reflns_shell.Rmerge_I_all')
    @property
    def Rmerge_I_obs(self) -> Attribute:
        """The value of Rmerge(I) for reflections classified as 'observed'  (see _reflns.observed_criterion) in a given shell.               sum~i~(sum~j~|I~j~ - <I>|)  Rmerge(I) = --------------------------                  sum~i~(sum~j~<I>)   I~j~ = the intensity of the jth observation of reflection i  <I>  = the mean of the intensities of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
        return Attribute('reflns_shell.Rmerge_I_obs')
    @property
    def d_res_high(self) -> Attribute:
        """The smallest value in angstroms for the interplanar spacings  for the reflections in this shell. This is called the highest  resolution."""
        return Attribute('reflns_shell.d_res_high')
    @property
    def d_res_low(self) -> Attribute:
        """The highest value in angstroms for the interplanar spacings  for the reflections in this shell. This is called the lowest  resolution."""
        return Attribute('reflns_shell.d_res_low')
    @property
    def meanI_over_sigI_all(self) -> Attribute:
        """The ratio of the mean of the intensities of all reflections  in this shell to the mean of the standard uncertainties of the  intensities of all reflections in this shell."""
        return Attribute('reflns_shell.meanI_over_sigI_all')
    @property
    def meanI_over_sigI_obs(self) -> Attribute:
        """The ratio of the mean of the intensities of the reflections  classified as 'observed' (see _reflns.observed_criterion) in  this shell to the mean of the standard uncertainties of the  intensities of the 'observed' reflections in this  shell."""
        return Attribute('reflns_shell.meanI_over_sigI_obs')
    @property
    def meanI_over_uI_all(self) -> Attribute:
        """The ratio of the mean of the intensities of all reflections  in this shell to the mean of the standard uncertainties of the  intensities of all reflections in this shell."""
        return Attribute('reflns_shell.meanI_over_uI_all')
    @property
    def number_measured_all(self) -> Attribute:
        """The total number of reflections measured for this  shell."""
        return Attribute('reflns_shell.number_measured_all')
    @property
    def number_measured_obs(self) -> Attribute:
        """The number of reflections classified as 'observed'  (see _reflns.observed_criterion) for this  shell."""
        return Attribute('reflns_shell.number_measured_obs')
    @property
    def number_possible(self) -> Attribute:
        """The number of unique reflections it is possible to measure in  this shell."""
        return Attribute('reflns_shell.number_possible')
    @property
    def number_unique_all(self) -> Attribute:
        """The total number of measured reflections which are symmetry-  unique after merging for this shell."""
        return Attribute('reflns_shell.number_unique_all')
    @property
    def number_unique_obs(self) -> Attribute:
        """The total number of measured reflections classified as 'observed'  (see _reflns.observed_criterion) which are symmetry-unique  after merging for this shell."""
        return Attribute('reflns_shell.number_unique_obs')
    @property
    def pdbx_CC_half(self) -> Attribute:
        """The Pearson's correlation coefficient expressed as a decimal value               between the average intensities from randomly selected               half-datasets within the resolution shell.  	      Ref: Karplus & Diederichs (2012), Science 336, 1030-33"""
        return Attribute('reflns_shell.pdbx_CC_half')
    @property
    def pdbx_R_split(self) -> Attribute:
        """R split measures the agreement between the sets of intensities created by merging               odd- and even-numbered images from the data within the resolution shell.  	      Ref: T. A. White, R. A. Kirian, A. V. Martin, A. Aquila, K. Nass, 	      A. Barty and H. N. Chapman (2012), J. Appl. Cryst. 45, 335-341"""
        return Attribute('reflns_shell.pdbx_R_split')
    @property
    def pdbx_Rpim_I_all(self) -> Attribute:
        """The precision-indicating merging R factor value Rpim,  for merging all intensities in a given shell.          sum~i~ [1/(N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |  Rpim = --------------------------------------------------                       sum~i~ ( sum~j~ I~j~ )   I~j~   = the intensity of the jth observation of reflection i  <I~i~> = the mean of the intensities of all observations of           reflection i  N~i~   = the redundancy (the number of times reflection i           has been measured).   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection.   Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.       Biol. 4, 269-275.       Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.       30, 203-205.       Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
        return Attribute('reflns_shell.pdbx_Rpim_I_all')
    @property
    def pdbx_Rrim_I_all(self) -> Attribute:
        """The redundancy-independent merging R factor value Rrim,               also denoted Rmeas, for merging all intensities in a               given shell.                       sum~i~ [N~i~ /( N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |               Rrim = --------------------------------------------------------                                    sum~i~ ( sum~j~ I~j~ )                I~j~   = the intensity of the jth observation of reflection i               <I~i~> = the mean of the intensities of all observations of                        reflection i 	      N~i~   = the redundancy (the number of times reflection i                        has been measured).                sum~i~ is taken over all reflections               sum~j~ is taken over all observations of each reflection.                Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.                    Biol. 4, 269-275.                    Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.                    30, 203-205.                    Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
        return Attribute('reflns_shell.pdbx_Rrim_I_all')
    @property
    def pdbx_Rsym_value(self) -> Attribute:
        """R sym value in percent."""
        return Attribute('reflns_shell.pdbx_Rsym_value')
    @property
    def pdbx_chi_squared(self) -> Attribute:
        """Chi-squared statistic for this resolution shell."""
        return Attribute('reflns_shell.pdbx_chi_squared')
    @property
    def pdbx_diffrn_id(self) -> Attribute:
        """"""
        return Attribute('reflns_shell.pdbx_diffrn_id')
    @property
    def pdbx_netI_over_sigmaI_all(self) -> Attribute:
        """The mean of the ratio of the intensities to their  standard uncertainties of all reflections in the  resolution shell.   _reflns_shell.pdbx_netI_over_sigmaI_all =  <I/sigma(I)>"""
        return Attribute('reflns_shell.pdbx_netI_over_sigmaI_all')
    @property
    def pdbx_netI_over_sigmaI_obs(self) -> Attribute:
        """The mean of the ratio of the intensities to their  standard uncertainties of observed reflections  (see _reflns.observed_criterion) in the resolution shell.   _reflns_shell.pdbx_netI_over_sigmaI_obs =  <I/sigma(I)>"""
        return Attribute('reflns_shell.pdbx_netI_over_sigmaI_obs')
    @property
    def pdbx_ordinal(self) -> Attribute:
        """An ordinal identifier for this resolution shell."""
        return Attribute('reflns_shell.pdbx_ordinal')
    @property
    def pdbx_redundancy(self) -> Attribute:
        """Redundancy for the current shell."""
        return Attribute('reflns_shell.pdbx_redundancy')
    @property
    def pdbx_rejects(self) -> Attribute:
        """The number of rejected reflections in the resolution  shell.  Reflections may be rejected from scaling  by setting the observation criterion,  _reflns.observed_criterion."""
        return Attribute('reflns_shell.pdbx_rejects')
    @property
    def percent_possible_all(self) -> Attribute:
        """The percentage of geometrically possible reflections represented  by all reflections measured for this shell."""
        return Attribute('reflns_shell.percent_possible_all')
    @property
    def percent_possible_obs(self) -> Attribute:
        """The percentage of geometrically possible reflections represented  by reflections classified as 'observed' (see  _reflns.observed_criterion) for this shell."""
        return Attribute('reflns_shell.percent_possible_obs')

class Attr_Software_2560259537581220155:
    """"""
    @property
    def citation_id(self) -> Attribute:
        """This data item is a pointer to _citation.id in the CITATION  category."""
        return Attribute('software.citation_id')
    @property
    def classification(self) -> Attribute:
        """The classification of the program according to its  major function."""
        return Attribute('software.classification')
    @property
    def contact_author(self) -> Attribute:
        """The recognized contact author of the software. This could be  the original author, someone who has modified the code or  someone who maintains the code.  It should be the person  most commonly associated with the code."""
        return Attribute('software.contact_author')
    @property
    def contact_author_email(self) -> Attribute:
        """The e-mail address of the person specified in  _software.contact_author."""
        return Attribute('software.contact_author_email')
    @property
    def date(self) -> Attribute:
        """The date the software was released."""
        return Attribute('software.date')
    @property
    def description(self) -> Attribute:
        """Description of the software."""
        return Attribute('software.description')
    @property
    def language(self) -> Attribute:
        """The major computing language in which the software is  coded."""
        return Attribute('software.language')
    @property
    def location(self) -> Attribute:
        """The URL for an Internet address at which  details of the software can be found."""
        return Attribute('software.location')
    @property
    def name(self) -> Attribute:
        """The name of the software."""
        return Attribute('software.name')
    @property
    def os(self) -> Attribute:
        """The name of the operating system under which the software  runs."""
        return Attribute('software.os')
    @property
    def pdbx_ordinal(self) -> Attribute:
        """An ordinal index for this category"""
        return Attribute('software.pdbx_ordinal')
    @property
    def type(self) -> Attribute:
        """The classification of the software according to the most  common types."""
        return Attribute('software.type')
    @property
    def version(self) -> Attribute:
        """The version of the software."""
        return Attribute('software.version')

class Attr_Struct_1438102844827982749:
    """"""
    @property
    def pdbx_CASP_flag(self) -> Attribute:
        """The item indicates whether the entry is a CASP target, a CASD-NMR target,  or similar target participating in methods development experiments."""
        return Attribute('struct.pdbx_CASP_flag')
    @property
    def pdbx_descriptor(self) -> Attribute:
        """An automatically generated descriptor for an NDB structure or  the unstructured content of the PDB COMPND record."""
        return Attribute('struct.pdbx_descriptor')
    @property
    def pdbx_model_details(self) -> Attribute:
        """Text description of the methodology which produced this  model structure."""
        return Attribute('struct.pdbx_model_details')
    @property
    def pdbx_model_type_details(self) -> Attribute:
        """A description of the type of structure model."""
        return Attribute('struct.pdbx_model_type_details')
    @property
    def title(self) -> Attribute:
        """A title for the data block. The author should attempt to convey  the essence of the structure archived in the CIF in the title,  and to distinguish this structural result from others."""
        return Attribute('struct.title')

class Attr_StructKeywords_3901773578464770903:
    """"""
    @property
    def pdbx_keywords(self) -> Attribute:
        """Terms characterizing the macromolecular structure."""
        return Attribute('struct_keywords.pdbx_keywords')
    @property
    def text(self) -> Attribute:
        """Keywords describing this structure."""
        return Attribute('struct_keywords.text')

class Attr_Symmetry_8107587269104871708:
    """"""
    @property
    def Int_Tables_number(self) -> Attribute:
        """Space-group number from International Tables for Crystallography  Vol. A (2002)."""
        return Attribute('symmetry.Int_Tables_number')
    @property
    def cell_setting(self) -> Attribute:
        """The cell settings for this space-group symmetry."""
        return Attribute('symmetry.cell_setting')
    @property
    def pdbx_full_space_group_name_H_M(self) -> Attribute:
        """Used for PDB space group:   Example: 'C 1 2 1'  (instead of C 2)           'P 1 2 1'  (instead of P 2)           'P 1 21 1' (instead of P 21)           'P 1 1 21' (instead of P 21 -unique C axis)           'H 3'      (instead of R 3   -hexagonal)           'H 3 2'    (instead of R 3 2 -hexagonal)"""
        return Attribute('symmetry.pdbx_full_space_group_name_H_M')
    @property
    def space_group_name_H_M(self) -> Attribute:
        """Hermann-Mauguin space-group symbol. Note that the  Hermann-Mauguin symbol does not necessarily contain complete  information about the symmetry and the space-group origin. If  used, always supply the FULL symbol from International Tables  for Crystallography Vol. A (2002) and indicate the origin and  the setting if it is not implicit. If there is any doubt that  the equivalent positions can be uniquely deduced from this  symbol, specify the  _symmetry_equiv.pos_as_xyz or  _symmetry.space_group_name_Hall  data items as well. Leave  spaces between symbols referring to  different axes."""
        return Attribute('symmetry.space_group_name_H_M')
    @property
    def space_group_name_Hall(self) -> Attribute:
        """Space-group symbol as described by Hall (1981). This symbol  gives the space-group setting explicitly. Leave spaces between  the separate components of the symbol.   Ref: Hall, S. R. (1981). Acta Cryst. A37, 517-525; erratum  (1981) A37, 921."""
        return Attribute('symmetry.space_group_name_Hall')

class Attr_RcsbPubmedContainerIdentifiers_4606950534434183105:
    """"""
    @property
    def pubmed_id(self) -> Attribute:
        """UID assigned to each PubMed record."""
        return Attribute('rcsb_pubmed_container_identifiers.pubmed_id')

class Attr_RcsbPubmedMeshDescriptorsLineage_239826911826696632:
    """Members of the MeSH classification lineage."""
    @property
    def id(self) -> Attribute:
        """Identifier for MeSH classification term."""
        return Attribute('rcsb_pubmed_mesh_descriptors_lineage.id')
    @property
    def name(self) -> Attribute:
        """MeSH classification term."""
        return Attribute('rcsb_pubmed_mesh_descriptors_lineage.name')
    @property
    def depth(self) -> Attribute:
        """Hierarchy depth."""
        return Attribute('rcsb_pubmed_mesh_descriptors_lineage.depth')

class Attr_EntityPoly_565075102590953250:
    """"""
    @property
    def nstd_linkage(self) -> Attribute:
        """A flag to indicate whether the polymer contains at least  one monomer-to-monomer link different from that implied by  _entity_poly.type."""
        return Attribute('entity_poly.nstd_linkage')
    @property
    def nstd_monomer(self) -> Attribute:
        """A flag to indicate whether the polymer contains at least  one monomer that is not considered standard."""
        return Attribute('entity_poly.nstd_monomer')
    @property
    def pdbx_seq_one_letter_code(self) -> Attribute:
        """Sequence of protein or nucleic acid polymer in standard one-letter                codes of amino acids or nucleotides. Non-standard amino                acids/nucleotides are represented by their Chemical                Component Dictionary (CCD) codes in                parenthesis. Deoxynucleotides are represented by the                specially-assigned 2-letter CCD codes in parenthesis,                with 'D' prefix added to their ribonucleotide                counterparts. For hybrid polymer, each residue is                represented by the code of its individual type. A                cyclic polymer is represented in linear sequence from                the chosen start to end.  A for Alanine or Adenosine-5'-monophosphate C for Cysteine or Cytidine-5'-monophosphate D for Aspartic acid E for Glutamic acid F for Phenylalanine G for Glycine or Guanosine-5'-monophosphate H for Histidine I for Isoleucine or Inosinic Acid L for Leucine K for Lysine M for Methionine N for Asparagine  or Unknown ribonucleotide O for Pyrrolysine P for Proline Q for Glutamine R for Arginine S for Serine T for Threonine U for Selenocysteine or Uridine-5'-monophosphate V for Valine W for Tryptophan Y for Tyrosine (DA) for 2'-deoxyadenosine-5'-monophosphate (DC) for 2'-deoxycytidine-5'-monophosphate (DG) for 2'-deoxyguanosine-5'-monophosphate (DT) for Thymidine-5'-monophosphate (MSE) for Selenomethionine (SEP) for Phosphoserine (TPO) for Phosphothreonine (PTR) for Phosphotyrosine (PCA) for Pyroglutamic acid (UNK) for Unknown amino acid (ACE) for Acetylation cap (NH2) for Amidation cap"""
        return Attribute('entity_poly.pdbx_seq_one_letter_code')
    @property
    def pdbx_seq_one_letter_code_can(self) -> Attribute:
        """Canonical sequence of protein or nucleic acid polymer in standard                one-letter codes of amino acids or nucleotides,                corresponding to the sequence in                _entity_poly.pdbx_seq_one_letter_code. Non-standard                amino acids/nucleotides are represented by the codes of                their parents if parent is specified in                _chem_comp.mon_nstd_parent_comp_id, or by letter 'X' if                parent is not specified. Deoxynucleotides are                represented by their canonical one-letter codes of A,                C, G, or T.                 For modifications with several parent amino acids, 	       all corresponding parent amino acid codes will be listed 	       (ex. chromophores)."""
        return Attribute('entity_poly.pdbx_seq_one_letter_code_can')
    @property
    def pdbx_sequence_evidence_code(self) -> Attribute:
        """Evidence for the assignment of the polymer sequence."""
        return Attribute('entity_poly.pdbx_sequence_evidence_code')
    @property
    def pdbx_strand_id(self) -> Attribute:
        """The PDB strand/chain id(s) corresponding to this polymer entity."""
        return Attribute('entity_poly.pdbx_strand_id')
    @property
    def pdbx_target_identifier(self) -> Attribute:
        """For Structural Genomics entries, the sequence's target identifier registered at the TargetTrack database."""
        return Attribute('entity_poly.pdbx_target_identifier')
    @property
    def rcsb_artifact_monomer_count(self) -> Attribute:
        """Number of regions in the sample sequence identified as expression tags, linkers, or  cloning artifacts."""
        return Attribute('entity_poly.rcsb_artifact_monomer_count')
    @property
    def rcsb_conflict_count(self) -> Attribute:
        """Number of monomer conflicts relative to the reference sequence."""
        return Attribute('entity_poly.rcsb_conflict_count')
    @property
    def rcsb_deletion_count(self) -> Attribute:
        """Number of monomer deletions relative to the reference sequence."""
        return Attribute('entity_poly.rcsb_deletion_count')
    @property
    def rcsb_entity_polymer_type(self) -> Attribute:
        """A coarse-grained polymer entity type."""
        return Attribute('entity_poly.rcsb_entity_polymer_type')
    @property
    def rcsb_insertion_count(self) -> Attribute:
        """Number of monomer insertions relative to the reference sequence."""
        return Attribute('entity_poly.rcsb_insertion_count')
    @property
    def rcsb_mutation_count(self) -> Attribute:
        """Number of engineered mutations engineered in the sample sequence."""
        return Attribute('entity_poly.rcsb_mutation_count')
    @property
    def rcsb_non_std_monomer_count(self) -> Attribute:
        """Number of non-standard monomers in the sample sequence."""
        return Attribute('entity_poly.rcsb_non_std_monomer_count')
    @property
    def rcsb_non_std_monomers(self) -> Attribute:
        """"""
        return Attribute('entity_poly.rcsb_non_std_monomers')
    @property
    def rcsb_prd_id(self) -> Attribute:
        """For polymer BIRD molecules the BIRD identifier for the entity."""
        return Attribute('entity_poly.rcsb_prd_id')
    @property
    def rcsb_sample_sequence_length(self) -> Attribute:
        """The monomer length of the sample sequence."""
        return Attribute('entity_poly.rcsb_sample_sequence_length')
    @property
    def type(self) -> Attribute:
        """The type of the polymer."""
        return Attribute('entity_poly.type')

class Attr_EntitySrcGen_4801190379354878659:
    """"""
    @property
    def expression_system_id(self) -> Attribute:
        """A unique identifier for the expression system. This  should be extracted from a local list of expression  systems."""
        return Attribute('entity_src_gen.expression_system_id')
    @property
    def gene_src_common_name(self) -> Attribute:
        """The common name of the natural organism from which the gene was  obtained."""
        return Attribute('entity_src_gen.gene_src_common_name')
    @property
    def gene_src_details(self) -> Attribute:
        """A description of special aspects of the natural organism from  which the gene was obtained."""
        return Attribute('entity_src_gen.gene_src_details')
    @property
    def gene_src_genus(self) -> Attribute:
        """The genus of the natural organism from which the gene was  obtained."""
        return Attribute('entity_src_gen.gene_src_genus')
    @property
    def gene_src_species(self) -> Attribute:
        """The species of the natural organism from which the gene was  obtained."""
        return Attribute('entity_src_gen.gene_src_species')
    @property
    def gene_src_strain(self) -> Attribute:
        """The strain of the natural organism from which the gene was  obtained, if relevant."""
        return Attribute('entity_src_gen.gene_src_strain')
    @property
    def gene_src_tissue(self) -> Attribute:
        """The tissue of the natural organism from which the gene was  obtained."""
        return Attribute('entity_src_gen.gene_src_tissue')
    @property
    def gene_src_tissue_fraction(self) -> Attribute:
        """The subcellular fraction of the tissue of the natural organism  from which the gene was obtained."""
        return Attribute('entity_src_gen.gene_src_tissue_fraction')
    @property
    def host_org_common_name(self) -> Attribute:
        """The common name of the organism that served as host for the  production of the entity.  Where full details of the protein  production are available it would be expected that this item  be derived from _entity_src_gen_express.host_org_common_name  or via _entity_src_gen_express.host_org_tax_id"""
        return Attribute('entity_src_gen.host_org_common_name')
    @property
    def host_org_details(self) -> Attribute:
        """A description of special aspects of the organism that served as  host for the production of the entity. Where full details of  the protein production are available it would be expected that  this item would derived from _entity_src_gen_express.host_org_details"""
        return Attribute('entity_src_gen.host_org_details')
    @property
    def host_org_genus(self) -> Attribute:
        """The genus of the organism that served as host for the production  of the entity."""
        return Attribute('entity_src_gen.host_org_genus')
    @property
    def host_org_species(self) -> Attribute:
        """The species of the organism that served as host for the  production of the entity."""
        return Attribute('entity_src_gen.host_org_species')
    @property
    def pdbx_alt_source_flag(self) -> Attribute:
        """This data item identifies cases in which an alternative source  modeled."""
        return Attribute('entity_src_gen.pdbx_alt_source_flag')
    @property
    def pdbx_beg_seq_num(self) -> Attribute:
        """The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('entity_src_gen.pdbx_beg_seq_num')
    @property
    def pdbx_description(self) -> Attribute:
        """Information on the source which is not given elsewhere."""
        return Attribute('entity_src_gen.pdbx_description')
    @property
    def pdbx_end_seq_num(self) -> Attribute:
        """The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('entity_src_gen.pdbx_end_seq_num')
    @property
    def pdbx_gene_src_atcc(self) -> Attribute:
        """American Type Culture Collection tissue culture number."""
        return Attribute('entity_src_gen.pdbx_gene_src_atcc')
    @property
    def pdbx_gene_src_cell(self) -> Attribute:
        """Cell type."""
        return Attribute('entity_src_gen.pdbx_gene_src_cell')
    @property
    def pdbx_gene_src_cell_line(self) -> Attribute:
        """The specific line of cells."""
        return Attribute('entity_src_gen.pdbx_gene_src_cell_line')
    @property
    def pdbx_gene_src_cellular_location(self) -> Attribute:
        """Identifies the location inside (or outside) the cell."""
        return Attribute('entity_src_gen.pdbx_gene_src_cellular_location')
    @property
    def pdbx_gene_src_fragment(self) -> Attribute:
        """A domain or fragment of the molecule."""
        return Attribute('entity_src_gen.pdbx_gene_src_fragment')
    @property
    def pdbx_gene_src_gene(self) -> Attribute:
        """Identifies the gene."""
        return Attribute('entity_src_gen.pdbx_gene_src_gene')
    @property
    def pdbx_gene_src_ncbi_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the gene source organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('entity_src_gen.pdbx_gene_src_ncbi_taxonomy_id')
    @property
    def pdbx_gene_src_organ(self) -> Attribute:
        """Organized group of tissues that carries on a specialized function."""
        return Attribute('entity_src_gen.pdbx_gene_src_organ')
    @property
    def pdbx_gene_src_organelle(self) -> Attribute:
        """Organized structure within cell."""
        return Attribute('entity_src_gen.pdbx_gene_src_organelle')
    @property
    def pdbx_gene_src_scientific_name(self) -> Attribute:
        """Scientific name of the organism."""
        return Attribute('entity_src_gen.pdbx_gene_src_scientific_name')
    @property
    def pdbx_gene_src_variant(self) -> Attribute:
        """Identifies the variant."""
        return Attribute('entity_src_gen.pdbx_gene_src_variant')
    @property
    def pdbx_host_org_atcc(self) -> Attribute:
        """Americal Tissue Culture Collection of the expression system. Where  full details of the protein production are available it would  be expected that this item  would be derived from  _entity_src_gen_express.host_org_culture_collection"""
        return Attribute('entity_src_gen.pdbx_host_org_atcc')
    @property
    def pdbx_host_org_cell(self) -> Attribute:
        """Cell type from which the gene is derived. Where  entity.target_id is provided this should be derived from  details of the target."""
        return Attribute('entity_src_gen.pdbx_host_org_cell')
    @property
    def pdbx_host_org_cell_line(self) -> Attribute:
        """A specific line of cells used as the expression system. Where  full details of the protein production are available it would  be expected that this item would be derived from  entity_src_gen_express.host_org_cell_line"""
        return Attribute('entity_src_gen.pdbx_host_org_cell_line')
    @property
    def pdbx_host_org_cellular_location(self) -> Attribute:
        """Identifies the location inside (or outside) the cell which  expressed the molecule."""
        return Attribute('entity_src_gen.pdbx_host_org_cellular_location')
    @property
    def pdbx_host_org_culture_collection(self) -> Attribute:
        """Culture collection of the expression system. Where  full details of the protein production are available it would  be expected that this item  would be derived somehwere, but  exactly where is not clear."""
        return Attribute('entity_src_gen.pdbx_host_org_culture_collection')
    @property
    def pdbx_host_org_gene(self) -> Attribute:
        """Specific gene which expressed the molecule."""
        return Attribute('entity_src_gen.pdbx_host_org_gene')
    @property
    def pdbx_host_org_ncbi_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the expression system organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('entity_src_gen.pdbx_host_org_ncbi_taxonomy_id')
    @property
    def pdbx_host_org_organ(self) -> Attribute:
        """Specific organ which expressed the molecule."""
        return Attribute('entity_src_gen.pdbx_host_org_organ')
    @property
    def pdbx_host_org_organelle(self) -> Attribute:
        """Specific organelle which expressed the molecule."""
        return Attribute('entity_src_gen.pdbx_host_org_organelle')
    @property
    def pdbx_host_org_scientific_name(self) -> Attribute:
        """The scientific name of the organism that served as host for the  production of the entity. Where full details of the protein  production are available it would be expected that this item  would be derived from _entity_src_gen_express.host_org_scientific_name  or via _entity_src_gen_express.host_org_tax_id"""
        return Attribute('entity_src_gen.pdbx_host_org_scientific_name')
    @property
    def pdbx_host_org_strain(self) -> Attribute:
        """The strain of the organism in which the entity was expressed."""
        return Attribute('entity_src_gen.pdbx_host_org_strain')
    @property
    def pdbx_host_org_tissue(self) -> Attribute:
        """The specific tissue which expressed the molecule. Where full details  of the protein production are available it would be expected that this  item would be derived from _entity_src_gen_express.host_org_tissue"""
        return Attribute('entity_src_gen.pdbx_host_org_tissue')
    @property
    def pdbx_host_org_tissue_fraction(self) -> Attribute:
        """The fraction of the tissue which expressed the molecule."""
        return Attribute('entity_src_gen.pdbx_host_org_tissue_fraction')
    @property
    def pdbx_host_org_variant(self) -> Attribute:
        """Variant of the organism used as the expression system. Where  full details of the protein production are available it would  be expected that this item be derived from  entity_src_gen_express.host_org_variant or via  _entity_src_gen_express.host_org_tax_id"""
        return Attribute('entity_src_gen.pdbx_host_org_variant')
    @property
    def pdbx_host_org_vector(self) -> Attribute:
        """Identifies the vector used. Where full details of the protein  production are available it would be expected that this item  would be derived from _entity_src_gen_clone.vector_name."""
        return Attribute('entity_src_gen.pdbx_host_org_vector')
    @property
    def pdbx_host_org_vector_type(self) -> Attribute:
        """Identifies the type of vector used (plasmid, virus, or cosmid).  Where full details of the protein production are available it  would be expected that this item would be derived from  _entity_src_gen_express.vector_type."""
        return Attribute('entity_src_gen.pdbx_host_org_vector_type')
    @property
    def pdbx_seq_type(self) -> Attribute:
        """This data item povides additional information about the sequence type."""
        return Attribute('entity_src_gen.pdbx_seq_type')
    @property
    def pdbx_src_id(self) -> Attribute:
        """This data item is an ordinal identifier for entity_src_gen data records."""
        return Attribute('entity_src_gen.pdbx_src_id')
    @property
    def plasmid_details(self) -> Attribute:
        """A description of special aspects of the plasmid that produced the  entity in the host organism. Where full details of the protein  production are available it would be expected that this item  would be derived from _pdbx_construct.details of the construct  pointed to from _entity_src_gen_express.plasmid_id."""
        return Attribute('entity_src_gen.plasmid_details')
    @property
    def plasmid_name(self) -> Attribute:
        """The name of the plasmid that produced the entity in the host  organism. Where full details of the protein production are available  it would be expected that this item would be derived from  _pdbx_construct.name of the construct pointed to from  _entity_src_gen_express.plasmid_id."""
        return Attribute('entity_src_gen.plasmid_name')

class Attr_EntitySrcNat_2888136308711114733:
    """"""
    @property
    def common_name(self) -> Attribute:
        """The common name of the organism from which the entity  was isolated."""
        return Attribute('entity_src_nat.common_name')
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the organism from which the  entity was isolated."""
        return Attribute('entity_src_nat.details')
    @property
    def genus(self) -> Attribute:
        """The genus of the organism from which the entity was isolated."""
        return Attribute('entity_src_nat.genus')
    @property
    def pdbx_alt_source_flag(self) -> Attribute:
        """This data item identifies cases in which an alternative source  modeled."""
        return Attribute('entity_src_nat.pdbx_alt_source_flag')
    @property
    def pdbx_atcc(self) -> Attribute:
        """Americal Tissue Culture Collection number."""
        return Attribute('entity_src_nat.pdbx_atcc')
    @property
    def pdbx_beg_seq_num(self) -> Attribute:
        """The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('entity_src_nat.pdbx_beg_seq_num')
    @property
    def pdbx_cell(self) -> Attribute:
        """A particular cell type."""
        return Attribute('entity_src_nat.pdbx_cell')
    @property
    def pdbx_cell_line(self) -> Attribute:
        """The specific line of cells."""
        return Attribute('entity_src_nat.pdbx_cell_line')
    @property
    def pdbx_cellular_location(self) -> Attribute:
        """Identifies the location inside (or outside) the cell."""
        return Attribute('entity_src_nat.pdbx_cellular_location')
    @property
    def pdbx_end_seq_num(self) -> Attribute:
        """The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('entity_src_nat.pdbx_end_seq_num')
    @property
    def pdbx_fragment(self) -> Attribute:
        """A domain or fragment of the molecule."""
        return Attribute('entity_src_nat.pdbx_fragment')
    @property
    def pdbx_ncbi_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the source organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('entity_src_nat.pdbx_ncbi_taxonomy_id')
    @property
    def pdbx_organ(self) -> Attribute:
        """Organized group of tissues that carries on a specialized function."""
        return Attribute('entity_src_nat.pdbx_organ')
    @property
    def pdbx_organelle(self) -> Attribute:
        """Organized structure within cell."""
        return Attribute('entity_src_nat.pdbx_organelle')
    @property
    def pdbx_organism_scientific(self) -> Attribute:
        """Scientific name of the organism of the natural source."""
        return Attribute('entity_src_nat.pdbx_organism_scientific')
    @property
    def pdbx_plasmid_details(self) -> Attribute:
        """Details about the plasmid."""
        return Attribute('entity_src_nat.pdbx_plasmid_details')
    @property
    def pdbx_plasmid_name(self) -> Attribute:
        """The plasmid containing the gene."""
        return Attribute('entity_src_nat.pdbx_plasmid_name')
    @property
    def pdbx_secretion(self) -> Attribute:
        """Identifies the secretion from which the molecule was isolated."""
        return Attribute('entity_src_nat.pdbx_secretion')
    @property
    def pdbx_src_id(self) -> Attribute:
        """This data item is an ordinal identifier for entity_src_nat data records."""
        return Attribute('entity_src_nat.pdbx_src_id')
    @property
    def pdbx_variant(self) -> Attribute:
        """Identifies the variant."""
        return Attribute('entity_src_nat.pdbx_variant')
    @property
    def species(self) -> Attribute:
        """The species of the organism from which the entity was isolated."""
        return Attribute('entity_src_nat.species')
    @property
    def strain(self) -> Attribute:
        """The strain of the organism from which the entity was isolated."""
        return Attribute('entity_src_nat.strain')
    @property
    def tissue(self) -> Attribute:
        """The tissue of the organism from which the entity was isolated."""
        return Attribute('entity_src_nat.tissue')
    @property
    def tissue_fraction(self) -> Attribute:
        """The subcellular fraction of the tissue of the organism from  which the entity was isolated."""
        return Attribute('entity_src_nat.tissue_fraction')

class Attr_PdbxEntitySrcSyn_8594067501614494274:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the source for the  synthetic entity."""
        return Attribute('pdbx_entity_src_syn.details')
    @property
    def ncbi_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier of the organism from which the sequence of  the synthetic entity was derived.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('pdbx_entity_src_syn.ncbi_taxonomy_id')
    @property
    def organism_common_name(self) -> Attribute:
        """The common name of the organism from which the sequence of  the synthetic entity was derived."""
        return Attribute('pdbx_entity_src_syn.organism_common_name')
    @property
    def organism_scientific(self) -> Attribute:
        """The scientific name of the organism from which the sequence of  the synthetic entity was derived."""
        return Attribute('pdbx_entity_src_syn.organism_scientific')
    @property
    def pdbx_alt_source_flag(self) -> Attribute:
        """This data item identifies cases in which an alternative source  modeled."""
        return Attribute('pdbx_entity_src_syn.pdbx_alt_source_flag')
    @property
    def pdbx_beg_seq_num(self) -> Attribute:
        """The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('pdbx_entity_src_syn.pdbx_beg_seq_num')
    @property
    def pdbx_end_seq_num(self) -> Attribute:
        """The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('pdbx_entity_src_syn.pdbx_end_seq_num')
    @property
    def pdbx_src_id(self) -> Attribute:
        """This data item is an ordinal identifier for pdbx_entity_src_syn data records."""
        return Attribute('pdbx_entity_src_syn.pdbx_src_id')

class Attr_RcsbClusterFlexibility_9137763694137947026:
    """"""
    @property
    def avg_rmsd(self) -> Attribute:
        """Average RMSD refer to average pairwise RMSD (Root Mean Square Deviation of C-alpha atoms) between structures in the cluster (95% sequence identity) where a given entity belongs."""
        return Attribute('rcsb_cluster_flexibility.avg_rmsd')
    @property
    def label(self) -> Attribute:
        """Structural flexibility in the cluster (95% sequence identity) where a given entity belongs."""
        return Attribute('rcsb_cluster_flexibility.label')
    @property
    def link(self) -> Attribute:
        """Link to the associated PDBFlex database entry."""
        return Attribute('rcsb_cluster_flexibility.link')
    @property
    def max_rmsd(self) -> Attribute:
        """Maximal RMSD refer to maximal pairwise RMSD (Root Mean Square Deviation of C-alpha atoms) between structures in the cluster (95% sequence identity) where a given entity belongs."""
        return Attribute('rcsb_cluster_flexibility.max_rmsd')
    @property
    def provenance_code(self) -> Attribute:
        """Provenance code indicating the origin of the flexibility data."""
        return Attribute('rcsb_cluster_flexibility.provenance_code')

class Attr_RcsbClusterMembership_3657139151815645104:
    """"""
    @property
    def cluster_id(self) -> Attribute:
        """Identifier for a cluster at the specified level of sequence identity within the cluster data set."""
        return Attribute('rcsb_cluster_membership.cluster_id')
    @property
    def identity(self) -> Attribute:
        """Sequence identity expressed as an integer percent value."""
        return Attribute('rcsb_cluster_membership.identity')

class Attr_TaxonomyLineage_1200498375346659611:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the NCBI Taxonomy lineage as parent taxonomy lineage depth (1-N)"""
        return Attribute('rcsb_entity_host_organism.taxonomy_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the NCBI Taxonomy lineage as parent taxonomy idcodes."""
        return Attribute('rcsb_entity_host_organism.taxonomy_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the NCBI Taxonomy lineage as parent taxonomy names."""
        return Attribute('rcsb_entity_host_organism.taxonomy_lineage.name')

class Attr_RcsbEntityHostOrganism_2339318299077688287:
    """"""
    @property
    def beg_seq_num(self) -> Attribute:
        """The beginning polymer sequence position for the polymer section corresponding  to this host organism.   A reference to the sequence position in the entity_poly category."""
        return Attribute('rcsb_entity_host_organism.beg_seq_num')
    @property
    def common_name(self) -> Attribute:
        """The common name of the host organism"""
        return Attribute('rcsb_entity_host_organism.common_name')
    @property
    def end_seq_num(self) -> Attribute:
        """The ending polymer sequence position for the polymer section corresponding  to this host organism.   A reference to the sequence position in the entity_poly category."""
        return Attribute('rcsb_entity_host_organism.end_seq_num')
    @property
    def ncbi_common_names(self) -> Attribute:
        """"""
        return Attribute('rcsb_entity_host_organism.ncbi_common_names')
    @property
    def ncbi_parent_scientific_name(self) -> Attribute:
        """The parent scientific name in the NCBI taxonomy hierarchy (depth=1) associated with this taxonomy code.  References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
        return Attribute('rcsb_entity_host_organism.ncbi_parent_scientific_name')
    @property
    def ncbi_scientific_name(self) -> Attribute:
        """The scientific name associated with this taxonomy code aggregated by the NCBI Taxonomy Database.    This name corresponds to the taxonomy identifier assigned by the PDB depositor.   References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
        return Attribute('rcsb_entity_host_organism.ncbi_scientific_name')
    @property
    def ncbi_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the host organism.    Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('rcsb_entity_host_organism.ncbi_taxonomy_id')
    @property
    def pdbx_src_id(self) -> Attribute:
        """An identifier for an entity segment."""
        return Attribute('rcsb_entity_host_organism.pdbx_src_id')
    @property
    def provenance_source(self) -> Attribute:
        """A code indicating the provenance of the host organism."""
        return Attribute('rcsb_entity_host_organism.provenance_source')
    @property
    def scientific_name(self) -> Attribute:
        """The scientific name of the host organism"""
        return Attribute('rcsb_entity_host_organism.scientific_name')
    @property
    def taxonomy_lineage(self) -> 'Attr_TaxonomyLineage_1200498375346659611':
        """"""
        return Attr_TaxonomyLineage_1200498375346659611()

class Attr_TaxonomyLineage_5566530543188446842:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the NCBI Taxonomy lineage as parent taxonomy lineage depth (1-N)"""
        return Attribute('rcsb_entity_source_organism.taxonomy_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the NCBI Taxonomy lineage as parent taxonomy idcodes."""
        return Attribute('rcsb_entity_source_organism.taxonomy_lineage.id')
    @property
    def name(self) -> Attribute:
        """Memebers of the NCBI Taxonomy lineage as parent taxonomy names."""
        return Attribute('rcsb_entity_source_organism.taxonomy_lineage.name')

class Attr_RcsbGeneName_7116322769208094974:
    """"""
    @property
    def provenance_source(self) -> Attribute:
        """A code indicating the provenance of the source organism details for the entity"""
        return Attribute('rcsb_entity_source_organism.rcsb_gene_name.provenance_source')
    @property
    def value(self) -> Attribute:
        """Gene name."""
        return Attribute('rcsb_entity_source_organism.rcsb_gene_name.value')

class Attr_RcsbEntitySourceOrganism_7670836516038773145:
    """"""
    @property
    def beg_seq_num(self) -> Attribute:
        """The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('rcsb_entity_source_organism.beg_seq_num')
    @property
    def common_name(self) -> Attribute:
        """The common name for the source organism assigned by the PDB depositor."""
        return Attribute('rcsb_entity_source_organism.common_name')
    @property
    def end_seq_num(self) -> Attribute:
        """The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
        return Attribute('rcsb_entity_source_organism.end_seq_num')
    @property
    def ncbi_common_names(self) -> Attribute:
        """"""
        return Attribute('rcsb_entity_source_organism.ncbi_common_names')
    @property
    def ncbi_parent_scientific_name(self) -> Attribute:
        """A parent scientific name in the NCBI taxonomy hierarchy of the source organism assigned by the PDB depositor.   For cellular organism this corresponds to a superkingdom (e.g., Archaea, Bacteria, Eukaryota).  For viruses this   corresponds to a clade (e.g.  Adnaviria, Bicaudaviridae, Clavaviridae). For other and unclassified entries this   corresponds to the first level of any taxonomic rank below the root level.  References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
        return Attribute('rcsb_entity_source_organism.ncbi_parent_scientific_name')
    @property
    def ncbi_scientific_name(self) -> Attribute:
        """The scientific name associated with this taxonomy code aggregated by the NCBI Taxonomy Database.    This name corresponds to the taxonomy identifier assigned by the PDB depositor.   References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
        return Attribute('rcsb_entity_source_organism.ncbi_scientific_name')
    @property
    def ncbi_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the gene source organism assigned by the PDB depositor.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('rcsb_entity_source_organism.ncbi_taxonomy_id')
    @property
    def pdbx_src_id(self) -> Attribute:
        """An identifier for the entity segment."""
        return Attribute('rcsb_entity_source_organism.pdbx_src_id')
    @property
    def provenance_source(self) -> Attribute:
        """Reference to the provenance of the source organism details for the entity.   Primary data indicates information obtained from the same source as the structural model.  UniProt and NCBI are provided as alternate sources of provenance for organism details."""
        return Attribute('rcsb_entity_source_organism.provenance_source')
    @property
    def scientific_name(self) -> Attribute:
        """The scientific name of the source organism assigned by the PDB depositor."""
        return Attribute('rcsb_entity_source_organism.scientific_name')
    @property
    def source_type(self) -> Attribute:
        """The source type for the entity"""
        return Attribute('rcsb_entity_source_organism.source_type')
    @property
    def taxonomy_lineage(self) -> 'Attr_TaxonomyLineage_5566530543188446842':
        """"""
        return Attr_TaxonomyLineage_5566530543188446842()
    @property
    def rcsb_gene_name(self) -> 'Attr_RcsbGeneName_7116322769208094974':
        """"""
        return Attr_RcsbGeneName_7116322769208094974()

class Attr_RcsbGenomicLineage_7387597817044800956:
    """"""
    @property
    def depth(self) -> Attribute:
        """Classification hierarchy depth."""
        return Attribute('rcsb_genomic_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Automatically assigned ID that uniquely identifies taxonomy, chromosome or gene in the Genome Location Browser."""
        return Attribute('rcsb_genomic_lineage.id')
    @property
    def name(self) -> Attribute:
        """A human-readable term name."""
        return Attribute('rcsb_genomic_lineage.name')

class Attr_RcsbMembraneLineage_5001566126692314102:
    """"""
    @property
    def depth(self) -> Attribute:
        """Hierarchy depth."""
        return Attribute('rcsb_membrane_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Automatically assigned ID for membrane classification term in the Membrane Protein Browser."""
        return Attribute('rcsb_membrane_lineage.id')
    @property
    def name(self) -> Attribute:
        """Membrane protein classification term."""
        return Attribute('rcsb_membrane_lineage.name')

class Attr_RcsbEcLineage_7080158274932634398:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the enzyme classification lineage as parent classification hierarchy depth (1-N)."""
        return Attribute('rcsb_polymer_entity.rcsb_ec_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the enzyme classification lineage as parent classification codes."""
        return Attribute('rcsb_polymer_entity.rcsb_ec_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the enzyme classification lineage as parent classification names."""
        return Attribute('rcsb_polymer_entity.rcsb_ec_lineage.name')

class Attr_RcsbMacromolecularNamesCombined_8251203771099939423:
    """"""
    @property
    def name(self) -> Attribute:
        """Combined list of macromolecular names."""
        return Attribute('rcsb_polymer_entity.rcsb_macromolecular_names_combined.name')
    @property
    def provenance_code(self) -> Attribute:
        """Combined list of macromolecular names associated provenance code.   ECO (https://github.com/evidenceontology/evidenceontology)"""
        return Attribute('rcsb_polymer_entity.rcsb_macromolecular_names_combined.provenance_code')
    @property
    def provenance_source(self) -> Attribute:
        """Combined list of macromolecular names associated name source."""
        return Attribute('rcsb_polymer_entity.rcsb_macromolecular_names_combined.provenance_source')

class Attr_RcsbEnzymeClassCombined_4276663759983825184:
    """"""
    @property
    def depth(self) -> Attribute:
        """The enzyme classification hierarchy depth (1-N)."""
        return Attribute('rcsb_polymer_entity.rcsb_enzyme_class_combined.depth')
    @property
    def ec(self) -> Attribute:
        """Combined list of enzyme class assignments."""
        return Attribute('rcsb_polymer_entity.rcsb_enzyme_class_combined.ec')
    @property
    def provenance_source(self) -> Attribute:
        """Combined list of enzyme class associated provenance sources."""
        return Attribute('rcsb_polymer_entity.rcsb_enzyme_class_combined.provenance_source')

class Attr_RcsbPolymerNameCombined_5781927271096085651:
    """"""
    @property
    def names(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity.rcsb_polymer_name_combined.names')
    @property
    def provenance_source(self) -> Attribute:
        """Provenance source for the combined protein names."""
        return Attribute('rcsb_polymer_entity.rcsb_polymer_name_combined.provenance_source')

class Attr_RcsbPolymerEntity_5921975448015471234:
    """"""
    @property
    def details(self) -> Attribute:
        """A description of special aspects of the entity."""
        return Attribute('rcsb_polymer_entity.details')
    @property
    def formula_weight(self) -> Attribute:
        """Formula mass (KDa) of the entity."""
        return Attribute('rcsb_polymer_entity.formula_weight')
    @property
    def pdbx_description(self) -> Attribute:
        """A description of the polymer entity."""
        return Attribute('rcsb_polymer_entity.pdbx_description')
    @property
    def pdbx_ec(self) -> Attribute:
        """Enzyme Commission (EC) number(s)"""
        return Attribute('rcsb_polymer_entity.pdbx_ec')
    @property
    def pdbx_fragment(self) -> Attribute:
        """Polymer entity fragment description(s)."""
        return Attribute('rcsb_polymer_entity.pdbx_fragment')
    @property
    def pdbx_mutation(self) -> Attribute:
        """Details about any polymer entity mutation(s)."""
        return Attribute('rcsb_polymer_entity.pdbx_mutation')
    @property
    def pdbx_number_of_molecules(self) -> Attribute:
        """The number of molecules of the entity in the entry."""
        return Attribute('rcsb_polymer_entity.pdbx_number_of_molecules')
    @property
    def rcsb_multiple_source_flag(self) -> Attribute:
        """A code indicating the entity has multiple biological sources."""
        return Attribute('rcsb_polymer_entity.rcsb_multiple_source_flag')
    @property
    def rcsb_source_part_count(self) -> Attribute:
        """The number of biological sources for the polymer entity. Multiple source contributions  may come from the same organism (taxonomy)."""
        return Attribute('rcsb_polymer_entity.rcsb_source_part_count')
    @property
    def rcsb_source_taxonomy_count(self) -> Attribute:
        """The number of distinct source taxonomies for the polymer entity. Commonly used to identify chimeric polymers."""
        return Attribute('rcsb_polymer_entity.rcsb_source_taxonomy_count')
    @property
    def src_method(self) -> Attribute:
        """The method by which the sample for the polymer entity was produced.  Entities isolated directly from natural sources (tissues, soil  samples etc.) are expected to have further information in the  ENTITY_SRC_NAT category. Entities isolated from genetically  manipulated sources are expected to have further information in  the ENTITY_SRC_GEN category."""
        return Attribute('rcsb_polymer_entity.src_method')
    @property
    def rcsb_ec_lineage(self) -> 'Attr_RcsbEcLineage_7080158274932634398':
        """"""
        return Attr_RcsbEcLineage_7080158274932634398()
    @property
    def rcsb_macromolecular_names_combined(self) -> 'Attr_RcsbMacromolecularNamesCombined_8251203771099939423':
        """"""
        return Attr_RcsbMacromolecularNamesCombined_8251203771099939423()
    @property
    def rcsb_enzyme_class_combined(self) -> 'Attr_RcsbEnzymeClassCombined_4276663759983825184':
        """"""
        return Attr_RcsbEnzymeClassCombined_4276663759983825184()
    @property
    def rcsb_polymer_name_combined(self) -> 'Attr_RcsbPolymerNameCombined_5781927271096085651':
        """"""
        return Attr_RcsbPolymerNameCombined_5781927271096085651()

class Attr_AlignedRegions_9047259739742124248:
    """"""
    @property
    def entity_beg_seq_id(self) -> Attribute:
        """An identifier for the monomer in the entity sequence at which this segment of the alignment begins."""
        return Attribute('rcsb_polymer_entity_align.aligned_regions.entity_beg_seq_id')
    @property
    def length(self) -> Attribute:
        """The length of this segment of the alignment."""
        return Attribute('rcsb_polymer_entity_align.aligned_regions.length')
    @property
    def ref_beg_seq_id(self) -> Attribute:
        """An identifier for the monomer in the reference sequence at which this segment of the alignment begins."""
        return Attribute('rcsb_polymer_entity_align.aligned_regions.ref_beg_seq_id')

class Attr_RcsbPolymerEntityAlign_1484248402375036549:
    """"""
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the reference sequence."""
        return Attribute('rcsb_polymer_entity_align.provenance_source')
    @property
    def reference_database_accession(self) -> Attribute:
        """Reference sequence accession code."""
        return Attribute('rcsb_polymer_entity_align.reference_database_accession')
    @property
    def reference_database_isoform(self) -> Attribute:
        """Reference sequence isoform identifier."""
        return Attribute('rcsb_polymer_entity_align.reference_database_isoform')
    @property
    def reference_database_name(self) -> Attribute:
        """Reference sequence database name."""
        return Attribute('rcsb_polymer_entity_align.reference_database_name')
    @property
    def aligned_regions(self) -> 'Attr_AlignedRegions_9047259739742124248':
        """"""
        return Attr_AlignedRegions_9047259739742124248()

class Attr_AnnotationLineage_4560075783257099349:
    """"""
    @property
    def depth(self) -> Attribute:
        """Members of the annotation lineage as parent lineage depth (1-N)"""
        return Attribute('rcsb_polymer_entity_annotation.annotation_lineage.depth')
    @property
    def id(self) -> Attribute:
        """Members of the annotation lineage as parent class identifiers."""
        return Attribute('rcsb_polymer_entity_annotation.annotation_lineage.id')
    @property
    def name(self) -> Attribute:
        """Members of the annotation lineage as parent class names."""
        return Attribute('rcsb_polymer_entity_annotation.annotation_lineage.name')

class Attr_AdditionalProperties_873143115076248267:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_polymer_entity_annotation.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_annotation.additional_properties.values')

class Attr_RcsbPolymerEntityAnnotation_5571272436143411659:
    """"""
    @property
    def annotation_id(self) -> Attribute:
        """An identifier for the annotation."""
        return Attribute('rcsb_polymer_entity_annotation.annotation_id')
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the annotation assignment."""
        return Attribute('rcsb_polymer_entity_annotation.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the annotation."""
        return Attribute('rcsb_polymer_entity_annotation.description')
    @property
    def name(self) -> Attribute:
        """A name for the annotation."""
        return Attribute('rcsb_polymer_entity_annotation.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the annotation."""
        return Attribute('rcsb_polymer_entity_annotation.provenance_source')
    @property
    def type(self) -> Attribute:
        """A type or category of the annotation."""
        return Attribute('rcsb_polymer_entity_annotation.type')
    @property
    def annotation_lineage(self) -> 'Attr_AnnotationLineage_4560075783257099349':
        """"""
        return Attr_AnnotationLineage_4560075783257099349()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_873143115076248267':
        """"""
        return Attr_AdditionalProperties_873143115076248267()

class Attr_ReferenceSequenceIdentifiers_2909229000461187798:
    """"""
    @property
    def database_accession(self) -> Attribute:
        """Reference database accession code"""
        return Attribute('rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession')
    @property
    def database_isoform(self) -> Attribute:
        """Reference database identifier for the sequence isoform"""
        return Attribute('rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_isoform')
    @property
    def database_name(self) -> Attribute:
        """Reference database name"""
        return Attribute('rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_name')
    @property
    def entity_sequence_coverage(self) -> Attribute:
        """Indicates what fraction of this polymer entity sequence is covered by the reference sequence."""
        return Attribute('rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.entity_sequence_coverage')
    @property
    def provenance_source(self) -> Attribute:
        """Source of the reference database assignment"""
        return Attribute('rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.provenance_source')
    @property
    def reference_sequence_coverage(self) -> Attribute:
        """Indicates what fraction of the reference sequence is covered by this polymer entity sequence."""
        return Attribute('rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.reference_sequence_coverage')

class Attr_RcsbPolymerEntityContainerIdentifiers_8865481299329375829:
    """"""
    @property
    def asym_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_container_identifiers.asym_ids')
    @property
    def auth_asym_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_container_identifiers.auth_asym_ids')
    @property
    def chem_comp_monomers(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_container_identifiers.chem_comp_monomers')
    @property
    def chem_comp_nstd_monomers(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_container_identifiers.chem_comp_nstd_monomers')
    @property
    def chem_ref_def_id(self) -> Attribute:
        """The chemical reference definition identifier for the entity in this container."""
        return Attribute('rcsb_polymer_entity_container_identifiers.chem_ref_def_id')
    @property
    def entity_id(self) -> Attribute:
        """Entity identifier for the container."""
        return Attribute('rcsb_polymer_entity_container_identifiers.entity_id')
    @property
    def entry_id(self) -> Attribute:
        """Entry identifier for the container."""
        return Attribute('rcsb_polymer_entity_container_identifiers.entry_id')
    @property
    def prd_id(self) -> Attribute:
        """The BIRD identifier for the entity in this container."""
        return Attribute('rcsb_polymer_entity_container_identifiers.prd_id')
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers."""
        return Attribute('rcsb_polymer_entity_container_identifiers.rcsb_id')
    @property
    def uniprot_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_container_identifiers.uniprot_ids')
    @property
    def reference_sequence_identifiers(self) -> 'Attr_ReferenceSequenceIdentifiers_2909229000461187798':
        """"""
        return Attr_ReferenceSequenceIdentifiers_2909229000461187798()

class Attr_FeaturePositions_8052355259091987412:
    """"""
    @property
    def beg_comp_id(self) -> Attribute:
        """An identifier for the leading monomer corresponding to the feature assignment."""
        return Attribute('rcsb_polymer_entity_feature.feature_positions.beg_comp_id')
    @property
    def beg_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature begins."""
        return Attribute('rcsb_polymer_entity_feature.feature_positions.beg_seq_id')
    @property
    def end_seq_id(self) -> Attribute:
        """An identifier for the monomer at which this segment of the feature ends."""
        return Attribute('rcsb_polymer_entity_feature.feature_positions.end_seq_id')
    @property
    def value(self) -> Attribute:
        """The value for the feature over this monomer segment."""
        return Attribute('rcsb_polymer_entity_feature.feature_positions.value')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_feature.feature_positions.values')

class Attr_AdditionalProperties_1666076376924594772:
    """"""
    @property
    def name(self) -> Attribute:
        """The additional property name."""
        return Attribute('rcsb_polymer_entity_feature.additional_properties.name')
    @property
    def values(self) -> Attribute:
        """"""
        return Attribute('rcsb_polymer_entity_feature.additional_properties.values')

class Attr_RcsbPolymerEntityFeature_7686936654585147572:
    """"""
    @property
    def assignment_version(self) -> Attribute:
        """Identifies the version of the feature assignment."""
        return Attribute('rcsb_polymer_entity_feature.assignment_version')
    @property
    def description(self) -> Attribute:
        """A description for the feature."""
        return Attribute('rcsb_polymer_entity_feature.description')
    @property
    def feature_id(self) -> Attribute:
        """An identifier for the feature."""
        return Attribute('rcsb_polymer_entity_feature.feature_id')
    @property
    def name(self) -> Attribute:
        """A name for the feature."""
        return Attribute('rcsb_polymer_entity_feature.name')
    @property
    def provenance_source(self) -> Attribute:
        """Code identifying the individual, organization or program that  assigned the feature."""
        return Attribute('rcsb_polymer_entity_feature.provenance_source')
    @property
    def reference_scheme(self) -> Attribute:
        """Code residue coordinate system for the assigned feature."""
        return Attribute('rcsb_polymer_entity_feature.reference_scheme')
    @property
    def type(self) -> Attribute:
        """A type or category of the feature."""
        return Attribute('rcsb_polymer_entity_feature.type')
    @property
    def feature_positions(self) -> 'Attr_FeaturePositions_8052355259091987412':
        """"""
        return Attr_FeaturePositions_8052355259091987412()
    @property
    def additional_properties(self) -> 'Attr_AdditionalProperties_1666076376924594772':
        """"""
        return Attr_AdditionalProperties_1666076376924594772()

class Attr_RcsbPolymerEntityFeatureSummary_356259014689795612:
    """"""
    @property
    def count(self) -> Attribute:
        """The feature count."""
        return Attribute('rcsb_polymer_entity_feature_summary.count')
    @property
    def coverage(self) -> Attribute:
        """The fractional feature coverage relative to the full entity sequence.  For instance, the fraction of features such as mutations, artifacts or modified monomers  relative to the length of the entity sequence."""
        return Attribute('rcsb_polymer_entity_feature_summary.coverage')
    @property
    def maximum_length(self) -> Attribute:
        """The maximum feature length."""
        return Attribute('rcsb_polymer_entity_feature_summary.maximum_length')
    @property
    def maximum_value(self) -> Attribute:
        """The maximum feature value."""
        return Attribute('rcsb_polymer_entity_feature_summary.maximum_value')
    @property
    def minimum_length(self) -> Attribute:
        """The minimum feature length."""
        return Attribute('rcsb_polymer_entity_feature_summary.minimum_length')
    @property
    def minimum_value(self) -> Attribute:
        """The minimum feature value."""
        return Attribute('rcsb_polymer_entity_feature_summary.minimum_value')
    @property
    def type(self) -> Attribute:
        """Type or category of the feature."""
        return Attribute('rcsb_polymer_entity_feature_summary.type')

class Attr_AlignedRegions_8874527163401477443:
    """"""
    @property
    def entity_beg_seq_id(self) -> Attribute:
        """An identifier for the monomer in the entity sequence at which this segment of the alignment begins."""
        return Attribute('rcsb_polymer_entity_group_membership.aligned_regions.entity_beg_seq_id')
    @property
    def length(self) -> Attribute:
        """The length of this segment of the alignment."""
        return Attribute('rcsb_polymer_entity_group_membership.aligned_regions.length')
    @property
    def ref_beg_seq_id(self) -> Attribute:
        """An identifier for the monomer in the reference sequence at which this segment of the alignment begins."""
        return Attribute('rcsb_polymer_entity_group_membership.aligned_regions.ref_beg_seq_id')

class Attr_RcsbPolymerEntityGroupMembership_3724512927620508481:
    """"""
    @property
    def aggregation_method(self) -> Attribute:
        """Method used to establish group membership"""
        return Attribute('rcsb_polymer_entity_group_membership.aggregation_method')
    @property
    def group_id(self) -> Attribute:
        """A unique identifier for a group of entities"""
        return Attribute('rcsb_polymer_entity_group_membership.group_id')
    @property
    def similarity_cutoff(self) -> Attribute:
        """Degree of similarity expressed as a floating-point number"""
        return Attribute('rcsb_polymer_entity_group_membership.similarity_cutoff')
    @property
    def aligned_regions(self) -> 'Attr_AlignedRegions_8874527163401477443':
        """"""
        return Attr_AlignedRegions_8874527163401477443()

class Attr_RcsbPolymerEntityKeywords_111563731748706027:
    """"""
    @property
    def text(self) -> Attribute:
        """Keywords describing this polymer entity."""
        return Attribute('rcsb_polymer_entity_keywords.text')

class Attr_RcsbPolymerEntityNameCom_3999100602014898303:
    """"""
    @property
    def name(self) -> Attribute:
        """A common name for the polymer entity."""
        return Attribute('rcsb_polymer_entity_name_com.name')

class Attr_RcsbPolymerEntityNameSys_7214700575849167110:
    """"""
    @property
    def name(self) -> Attribute:
        """The systematic name for the polymer entity."""
        return Attribute('rcsb_polymer_entity_name_sys.name')
    @property
    def system(self) -> Attribute:
        """The system used to generate the systematic name of the polymer entity."""
        return Attribute('rcsb_polymer_entity_name_sys.system')

class Attr_AlignedTarget_6675245833699317221:
    """"""
    @property
    def entity_beg_seq_id(self) -> Attribute:
        """The position of the monomer in the entity sequence at which the alignment begins."""
        return Attribute('rcsb_related_target_references.aligned_target.entity_beg_seq_id')
    @property
    def length(self) -> Attribute:
        """The length of the alignment."""
        return Attribute('rcsb_related_target_references.aligned_target.length')
    @property
    def target_beg_seq_id(self) -> Attribute:
        """The position of the monomer in the target sequence at which the alignment begins."""
        return Attribute('rcsb_related_target_references.aligned_target.target_beg_seq_id')

class Attr_RcsbRelatedTargetReferences_4514573363264039448:
    """"""
    @property
    def related_resource_name(self) -> Attribute:
        """The related target data resource name."""
        return Attribute('rcsb_related_target_references.related_resource_name')
    @property
    def related_resource_version(self) -> Attribute:
        """The version of the target data resource."""
        return Attribute('rcsb_related_target_references.related_resource_version')
    @property
    def related_target_id(self) -> Attribute:
        """An identifier for the target sequence in the related data resource."""
        return Attribute('rcsb_related_target_references.related_target_id')
    @property
    def target_taxonomy_id(self) -> Attribute:
        """NCBI Taxonomy identifier for the target organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
        return Attribute('rcsb_related_target_references.target_taxonomy_id')
    @property
    def aligned_target(self) -> 'Attr_AlignedTarget_6675245833699317221':
        """"""
        return Attr_AlignedTarget_6675245833699317221()

class Attr_RcsbTargetCofactors_1473429961113133440:
    """"""
    @property
    def binding_assay_value(self) -> Attribute:
        """The value measured or determined by the assay."""
        return Attribute('rcsb_target_cofactors.binding_assay_value')
    @property
    def binding_assay_value_type(self) -> Attribute:
        """The type of measurement or value determined by the assay."""
        return Attribute('rcsb_target_cofactors.binding_assay_value_type')
    @property
    def cofactor_InChIKey(self) -> Attribute:
        """Standard IUPAC International Chemical Identifier (InChI) descriptor key  for the cofactor.   InChI, the IUPAC International Chemical Identifier,  by Stephen R Heller, Alan McNaught, Igor Pletnev, Stephen Stein and Dmitrii Tchekhovskoi,  Journal of Cheminformatics, 2015, 7:23"""
        return Attribute('rcsb_target_cofactors.cofactor_InChIKey')
    @property
    def cofactor_SMILES(self) -> Attribute:
        """Simplified molecular-input line-entry system (SMILES) descriptor for the cofactor.     Weininger D (February 1988). 'SMILES, a chemical language and information system. 1.    Introduction to methodology and encoding rules'. Journal of Chemical Information and Modeling. 28 (1): 31-6.     Weininger D, Weininger A, Weininger JL (May 1989).    'SMILES. 2. Algorithm for generation of unique SMILES notation',    Journal of Chemical Information and Modeling. 29 (2): 97-101."""
        return Attribute('rcsb_target_cofactors.cofactor_SMILES')
    @property
    def cofactor_chem_comp_id(self) -> Attribute:
        """The chemical component definition identifier for the cofactor."""
        return Attribute('rcsb_target_cofactors.cofactor_chem_comp_id')
    @property
    def cofactor_description(self) -> Attribute:
        """The cofactor description."""
        return Attribute('rcsb_target_cofactors.cofactor_description')
    @property
    def cofactor_name(self) -> Attribute:
        """The cofactor name."""
        return Attribute('rcsb_target_cofactors.cofactor_name')
    @property
    def cofactor_prd_id(self) -> Attribute:
        """The BIRD definition identifier for the cofactor."""
        return Attribute('rcsb_target_cofactors.cofactor_prd_id')
    @property
    def cofactor_resource_id(self) -> Attribute:
        """Identifier for the cofactor assigned by the resource."""
        return Attribute('rcsb_target_cofactors.cofactor_resource_id')
    @property
    def mechanism_of_action(self) -> Attribute:
        """Mechanism of action describes the biochemical interaction through which the  cofactor produces a pharmacological effect."""
        return Attribute('rcsb_target_cofactors.mechanism_of_action')
    @property
    def neighbor_flag(self) -> Attribute:
        """A flag to indicate the cofactor is a structural neighbor of this  entity."""
        return Attribute('rcsb_target_cofactors.neighbor_flag')
    @property
    def patent_nos(self) -> Attribute:
        """"""
        return Attribute('rcsb_target_cofactors.patent_nos')
    @property
    def pubmed_ids(self) -> Attribute:
        """"""
        return Attribute('rcsb_target_cofactors.pubmed_ids')
    @property
    def resource_name(self) -> Attribute:
        """Resource providing target and cofactor data."""
        return Attribute('rcsb_target_cofactors.resource_name')
    @property
    def resource_version(self) -> Attribute:
        """Version of the information distributed by the data resource."""
        return Attribute('rcsb_target_cofactors.resource_version')
    @property
    def target_resource_id(self) -> Attribute:
        """Identifier for the target assigned by the resource."""
        return Attribute('rcsb_target_cofactors.target_resource_id')

class Attr_DrugbankContainerIdentifiers_2912637152102270126:
    """"""
    @property
    def drugbank_id(self) -> Attribute:
        """The DrugBank accession code"""
        return Attribute('drugbank_container_identifiers.drugbank_id')

class Attr_DrugProducts_8024560382107348415:
    """"""
    @property
    def approved(self) -> Attribute:
        """Indicates whether this drug has been approved by the regulating government."""
        return Attribute('drugbank_info.drug_products.approved')
    @property
    def country(self) -> Attribute:
        """The country where this commercially available drug has been approved."""
        return Attribute('drugbank_info.drug_products.country')
    @property
    def ended_marketing_on(self) -> Attribute:
        """The ending date for market approval."""
        return Attribute('drugbank_info.drug_products.ended_marketing_on')
    @property
    def name(self) -> Attribute:
        """The proprietary name(s) provided by the manufacturer for any commercially available products containing this drug."""
        return Attribute('drugbank_info.drug_products.name')
    @property
    def source(self) -> Attribute:
        """Source of this product information. For example, a value of DPD indicates this information was retrieved from the Canadian Drug Product Database."""
        return Attribute('drugbank_info.drug_products.source')
    @property
    def started_marketing_on(self) -> Attribute:
        """The starting date for market approval."""
        return Attribute('drugbank_info.drug_products.started_marketing_on')

class Attr_DrugbankInfo_8732299424569036807:
    """"""
    @property
    def affected_organisms(self) -> Attribute:
        """"""
        return Attribute('drugbank_info.affected_organisms')
    @property
    def atc_codes(self) -> Attribute:
        """"""
        return Attribute('drugbank_info.atc_codes')
    @property
    def brand_names(self) -> Attribute:
        """"""
        return Attribute('drugbank_info.brand_names')
    @property
    def cas_number(self) -> Attribute:
        """The DrugBank assigned Chemical Abstracts Service identifier."""
        return Attribute('drugbank_info.cas_number')
    @property
    def description(self) -> Attribute:
        """The DrugBank drug description."""
        return Attribute('drugbank_info.description')
    @property
    def drug_categories(self) -> Attribute:
        """"""
        return Attribute('drugbank_info.drug_categories')
    @property
    def drug_groups(self) -> Attribute:
        """"""
        return Attribute('drugbank_info.drug_groups')
    @property
    def drugbank_id(self) -> Attribute:
        """The DrugBank accession code"""
        return Attribute('drugbank_info.drugbank_id')
    @property
    def indication(self) -> Attribute:
        """The DrugBank drug indication."""
        return Attribute('drugbank_info.indication')
    @property
    def mechanism_of_action(self) -> Attribute:
        """The DrugBank drug mechanism of actions."""
        return Attribute('drugbank_info.mechanism_of_action')
    @property
    def name(self) -> Attribute:
        """The DrugBank drug name."""
        return Attribute('drugbank_info.name')
    @property
    def pharmacology(self) -> Attribute:
        """The DrugBank drug pharmacology."""
        return Attribute('drugbank_info.pharmacology')
    @property
    def synonyms(self) -> Attribute:
        """"""
        return Attribute('drugbank_info.synonyms')
    @property
    def drug_products(self) -> 'Attr_DrugProducts_8024560382107348415':
        """"""
        return Attr_DrugProducts_8024560382107348415()

class Attr_DrugbankTarget_2055091295599847616:
    """"""
    @property
    def interaction_type(self) -> Attribute:
        """The type of target interaction."""
        return Attribute('drugbank_target.interaction_type')
    @property
    def name(self) -> Attribute:
        """The target name."""
        return Attribute('drugbank_target.name')
    @property
    def ordinal(self) -> Attribute:
        """The value of _drugbank_target.ordinal distinguishes  related examples for each chemical component."""
        return Attribute('drugbank_target.ordinal')
    @property
    def organism_common_name(self) -> Attribute:
        """The organism common name."""
        return Attribute('drugbank_target.organism_common_name')
    @property
    def reference_database_accession_code(self) -> Attribute:
        """The reference identifier code for the target interaction reference."""
        return Attribute('drugbank_target.reference_database_accession_code')
    @property
    def reference_database_name(self) -> Attribute:
        """The reference database name for the target interaction."""
        return Attribute('drugbank_target.reference_database_name')
    @property
    def seq_one_letter_code(self) -> Attribute:
        """Target sequence expressed as string of one-letter amino acid codes."""
        return Attribute('drugbank_target.seq_one_letter_code')
    @property
    def target_actions(self) -> Attribute:
        """"""
        return Attribute('drugbank_target.target_actions')

class AttributesRoot_0:
    """"""
    @property
    def pdbx_entity_nonpoly(self) -> 'Attr_PdbxEntityNonpoly_8778912838621600994':
        """"""
        return Attr_PdbxEntityNonpoly_8778912838621600994()
    @property
    def rcsb_latest_revision(self) -> 'Attr_RcsbLatestRevision_909480110613895552':
        """"""
        return Attr_RcsbLatestRevision_909480110613895552()
    @property
    def rcsb_nonpolymer_entity(self) -> 'Attr_RcsbNonpolymerEntity_2498174034378417098':
        """"""
        return Attr_RcsbNonpolymerEntity_2498174034378417098()
    @property
    def rcsb_nonpolymer_entity_annotation(self) -> 'Attr_RcsbNonpolymerEntityAnnotation_8352551812836966247':
        """"""
        return Attr_RcsbNonpolymerEntityAnnotation_8352551812836966247()
    @property
    def rcsb_nonpolymer_entity_container_identifiers(self) -> 'Attr_RcsbNonpolymerEntityContainerIdentifiers_7723152394641565112':
        """"""
        return Attr_RcsbNonpolymerEntityContainerIdentifiers_7723152394641565112()
    @property
    def rcsb_nonpolymer_entity_feature(self) -> 'Attr_RcsbNonpolymerEntityFeature_5417306140368469249':
        """"""
        return Attr_RcsbNonpolymerEntityFeature_5417306140368469249()
    @property
    def rcsb_nonpolymer_entity_feature_summary(self) -> 'Attr_RcsbNonpolymerEntityFeatureSummary_6813952545237991837':
        """"""
        return Attr_RcsbNonpolymerEntityFeatureSummary_6813952545237991837()
    @property
    def rcsb_nonpolymer_entity_keywords(self) -> 'Attr_RcsbNonpolymerEntityKeywords_373904751617707870':
        """"""
        return Attr_RcsbNonpolymerEntityKeywords_373904751617707870()
    @property
    def rcsb_nonpolymer_entity_name_com(self) -> 'Attr_RcsbNonpolymerEntityNameCom_2614432273012680843':
        """"""
        return Attr_RcsbNonpolymerEntityNameCom_2614432273012680843()
    @property
    def rcsb_id(self) -> Attribute:
        """A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers."""
        return Attribute('rcsb_id')
    @property
    def chem_comp(self) -> 'Attr_ChemComp_3514688068582236663':
        """"""
        return Attr_ChemComp_3514688068582236663()
    @property
    def pdbx_chem_comp_audit(self) -> 'Attr_PdbxChemCompAudit_4705584761086028783':
        """"""
        return Attr_PdbxChemCompAudit_4705584761086028783()
    @property
    def pdbx_chem_comp_descriptor(self) -> 'Attr_PdbxChemCompDescriptor_944258368257366730':
        """"""
        return Attr_PdbxChemCompDescriptor_944258368257366730()
    @property
    def pdbx_chem_comp_feature(self) -> 'Attr_PdbxChemCompFeature_5992594350396210640':
        """"""
        return Attr_PdbxChemCompFeature_5992594350396210640()
    @property
    def pdbx_chem_comp_identifier(self) -> 'Attr_PdbxChemCompIdentifier_5913762028284950543':
        """"""
        return Attr_PdbxChemCompIdentifier_5913762028284950543()
    @property
    def pdbx_family_prd_audit(self) -> 'Attr_PdbxFamilyPrdAudit_5629410239400904712':
        """"""
        return Attr_PdbxFamilyPrdAudit_5629410239400904712()
    @property
    def pdbx_prd_audit(self) -> 'Attr_PdbxPrdAudit_467923765230688021':
        """"""
        return Attr_PdbxPrdAudit_467923765230688021()
    @property
    def pdbx_reference_entity_list(self) -> 'Attr_PdbxReferenceEntityList_4320910281296680440':
        """"""
        return Attr_PdbxReferenceEntityList_4320910281296680440()
    @property
    def pdbx_reference_entity_poly(self) -> 'Attr_PdbxReferenceEntityPoly_5699906335811438204':
        """"""
        return Attr_PdbxReferenceEntityPoly_5699906335811438204()
    @property
    def pdbx_reference_entity_poly_link(self) -> 'Attr_PdbxReferenceEntityPolyLink_1611015207283996980':
        """"""
        return Attr_PdbxReferenceEntityPolyLink_1611015207283996980()
    @property
    def pdbx_reference_entity_poly_seq(self) -> 'Attr_PdbxReferenceEntityPolySeq_423560373521741291':
        """"""
        return Attr_PdbxReferenceEntityPolySeq_423560373521741291()
    @property
    def pdbx_reference_entity_sequence(self) -> 'Attr_PdbxReferenceEntitySequence_4279113401125687683':
        """"""
        return Attr_PdbxReferenceEntitySequence_4279113401125687683()
    @property
    def pdbx_reference_entity_src_nat(self) -> 'Attr_PdbxReferenceEntitySrcNat_2273266908519462102':
        """"""
        return Attr_PdbxReferenceEntitySrcNat_2273266908519462102()
    @property
    def pdbx_reference_molecule(self) -> 'Attr_PdbxReferenceMolecule_5913335729239546704':
        """"""
        return Attr_PdbxReferenceMolecule_5913335729239546704()
    @property
    def pdbx_reference_molecule_annotation(self) -> 'Attr_PdbxReferenceMoleculeAnnotation_3720401434528444555':
        """"""
        return Attr_PdbxReferenceMoleculeAnnotation_3720401434528444555()
    @property
    def pdbx_reference_molecule_details(self) -> 'Attr_PdbxReferenceMoleculeDetails_5854178980865644353':
        """"""
        return Attr_PdbxReferenceMoleculeDetails_5854178980865644353()
    @property
    def pdbx_reference_molecule_family(self) -> 'Attr_PdbxReferenceMoleculeFamily_8096817097636067251':
        """"""
        return Attr_PdbxReferenceMoleculeFamily_8096817097636067251()
    @property
    def pdbx_reference_molecule_features(self) -> 'Attr_PdbxReferenceMoleculeFeatures_5006906081052064742':
        """"""
        return Attr_PdbxReferenceMoleculeFeatures_5006906081052064742()
    @property
    def pdbx_reference_molecule_list(self) -> 'Attr_PdbxReferenceMoleculeList_9123781017092751690':
        """"""
        return Attr_PdbxReferenceMoleculeList_9123781017092751690()
    @property
    def pdbx_reference_molecule_related_structures(self) -> 'Attr_PdbxReferenceMoleculeRelatedStructures_4419261954773238425':
        """"""
        return Attr_PdbxReferenceMoleculeRelatedStructures_4419261954773238425()
    @property
    def pdbx_reference_molecule_synonyms(self) -> 'Attr_PdbxReferenceMoleculeSynonyms_7929125595815704912':
        """"""
        return Attr_PdbxReferenceMoleculeSynonyms_7929125595815704912()
    @property
    def rcsb_bird_citation(self) -> 'Attr_RcsbBirdCitation_4986285152268166071':
        """"""
        return Attr_RcsbBirdCitation_4986285152268166071()
    @property
    def rcsb_chem_comp_annotation(self) -> 'Attr_RcsbChemCompAnnotation_5910187435239757597':
        """"""
        return Attr_RcsbChemCompAnnotation_5910187435239757597()
    @property
    def rcsb_chem_comp_container_identifiers(self) -> 'Attr_RcsbChemCompContainerIdentifiers_3544777131158993539':
        """"""
        return Attr_RcsbChemCompContainerIdentifiers_3544777131158993539()
    @property
    def rcsb_chem_comp_descriptor(self) -> 'Attr_RcsbChemCompDescriptor_2875693885776408658':
        """"""
        return Attr_RcsbChemCompDescriptor_2875693885776408658()
    @property
    def rcsb_chem_comp_info(self) -> 'Attr_RcsbChemCompInfo_7676662344779069623':
        """"""
        return Attr_RcsbChemCompInfo_7676662344779069623()
    @property
    def rcsb_chem_comp_related(self) -> 'Attr_RcsbChemCompRelated_3136262384131889076':
        """"""
        return Attr_RcsbChemCompRelated_3136262384131889076()
    @property
    def rcsb_chem_comp_synonyms(self) -> 'Attr_RcsbChemCompSynonyms_3609015270641752462':
        """"""
        return Attr_RcsbChemCompSynonyms_3609015270641752462()
    @property
    def rcsb_chem_comp_target(self) -> 'Attr_RcsbChemCompTarget_8644528845840450023':
        """"""
        return Attr_RcsbChemCompTarget_8644528845840450023()
    @property
    def rcsb_schema_container_identifiers(self) -> 'Attr_RcsbSchemaContainerIdentifiers_2309482841021532999':
        """"""
        return Attr_RcsbSchemaContainerIdentifiers_2309482841021532999()
    @property
    def pdbx_struct_assembly(self) -> 'Attr_PdbxStructAssembly_23494749422806577':
        """"""
        return Attr_PdbxStructAssembly_23494749422806577()
    @property
    def pdbx_struct_assembly_auth_evidence(self) -> 'Attr_PdbxStructAssemblyAuthEvidence_9042404590181311099':
        """"""
        return Attr_PdbxStructAssemblyAuthEvidence_9042404590181311099()
    @property
    def pdbx_struct_assembly_gen(self) -> 'Attr_PdbxStructAssemblyGen_6492419249568703958':
        """"""
        return Attr_PdbxStructAssemblyGen_6492419249568703958()
    @property
    def pdbx_struct_assembly_prop(self) -> 'Attr_PdbxStructAssemblyProp_1730850938995923140':
        """"""
        return Attr_PdbxStructAssemblyProp_1730850938995923140()
    @property
    def pdbx_struct_oper_list(self) -> 'Attr_PdbxStructOperList_3741840671125252682':
        """"""
        return Attr_PdbxStructOperList_3741840671125252682()
    @property
    def rcsb_assembly_annotation(self) -> 'Attr_RcsbAssemblyAnnotation_6537260788827864652':
        """"""
        return Attr_RcsbAssemblyAnnotation_6537260788827864652()
    @property
    def rcsb_assembly_container_identifiers(self) -> 'Attr_RcsbAssemblyContainerIdentifiers_1245167145276486690':
        """"""
        return Attr_RcsbAssemblyContainerIdentifiers_1245167145276486690()
    @property
    def rcsb_assembly_feature(self) -> 'Attr_RcsbAssemblyFeature_5968959041198250090':
        """"""
        return Attr_RcsbAssemblyFeature_5968959041198250090()
    @property
    def rcsb_assembly_info(self) -> 'Attr_RcsbAssemblyInfo_5934210934139594148':
        """"""
        return Attr_RcsbAssemblyInfo_5934210934139594148()
    @property
    def rcsb_struct_symmetry(self) -> 'Attr_RcsbStructSymmetry_2000709393001487832':
        """"""
        return Attr_RcsbStructSymmetry_2000709393001487832()
    @property
    def rcsb_struct_symmetry_lineage(self) -> 'Attr_RcsbStructSymmetryLineage_9092103971171207111':
        """"""
        return Attr_RcsbStructSymmetryLineage_9092103971171207111()
    @property
    def rcsb_struct_symmetry_provenance_code(self) -> Attribute:
        """The title and version of software package used for symmetry calculations."""
        return Attribute('rcsb_struct_symmetry_provenance_code')
    @property
    def rcsb_repository_holdings_current(self) -> 'Attr_RcsbRepositoryHoldingsCurrent_1988663083059252371':
        """"""
        return Attr_RcsbRepositoryHoldingsCurrent_1988663083059252371()
    @property
    def rcsb_repository_holdings_current_entry_container_identifiers(self) -> 'Attr_RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers_168164911212486505':
        """"""
        return Attr_RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers_168164911212486505()
    @property
    def pdbx_struct_special_symmetry(self) -> 'Attr_PdbxStructSpecialSymmetry_6715667423544602245':
        """"""
        return Attr_PdbxStructSpecialSymmetry_6715667423544602245()
    @property
    def pdbx_vrpt_summary_entity_fit_to_map(self) -> 'Attr_PdbxVrptSummaryEntityFitToMap_7730038269615328452':
        """"""
        return Attr_PdbxVrptSummaryEntityFitToMap_7730038269615328452()
    @property
    def pdbx_vrpt_summary_entity_geometry(self) -> 'Attr_PdbxVrptSummaryEntityGeometry_3714083458255245184':
        """"""
        return Attr_PdbxVrptSummaryEntityGeometry_3714083458255245184()
    @property
    def rcsb_nonpolymer_entity_instance_container_identifiers(self) -> 'Attr_RcsbNonpolymerEntityInstanceContainerIdentifiers_5240252078881992651':
        """"""
        return Attr_RcsbNonpolymerEntityInstanceContainerIdentifiers_5240252078881992651()
    @property
    def rcsb_nonpolymer_instance_annotation(self) -> 'Attr_RcsbNonpolymerInstanceAnnotation_3768354779221868650':
        """"""
        return Attr_RcsbNonpolymerInstanceAnnotation_3768354779221868650()
    @property
    def rcsb_nonpolymer_instance_feature(self) -> 'Attr_RcsbNonpolymerInstanceFeature_3192278488326817956':
        """"""
        return Attr_RcsbNonpolymerInstanceFeature_3192278488326817956()
    @property
    def rcsb_nonpolymer_instance_feature_summary(self) -> 'Attr_RcsbNonpolymerInstanceFeatureSummary_2371206104525972356':
        """"""
        return Attr_RcsbNonpolymerInstanceFeatureSummary_2371206104525972356()
    @property
    def rcsb_nonpolymer_instance_validation_score(self) -> 'Attr_RcsbNonpolymerInstanceValidationScore_2590341230540896038':
        """"""
        return Attr_RcsbNonpolymerInstanceValidationScore_2590341230540896038()
    @property
    def rcsb_nonpolymer_struct_conn(self) -> 'Attr_RcsbNonpolymerStructConn_1709108760528740593':
        """"""
        return Attr_RcsbNonpolymerStructConn_1709108760528740593()
    @property
    def rcsb_target_neighbors(self) -> 'Attr_RcsbTargetNeighbors_1731505614121248038':
        """"""
        return Attr_RcsbTargetNeighbors_1731505614121248038()
    @property
    def struct_asym(self) -> 'Attr_StructAsym_8770235843712827894':
        """"""
        return Attr_StructAsym_8770235843712827894()
    @property
    def rcsb_uniprot_container_identifiers(self) -> 'Attr_RcsbUniprotContainerIdentifiers_2055158671997989571':
        """"""
        return Attr_RcsbUniprotContainerIdentifiers_2055158671997989571()
    @property
    def rcsb_uniprot_accession(self) -> Attribute:
        """List of UniProtKB accession numbers where original accession numbers are retained as ‘secondary’ accession numbers."""
        return Attribute('rcsb_uniprot_accession')
    @property
    def rcsb_uniprot_entry_name(self) -> Attribute:
        """A list of unique identifiers (former IDs), often containing biologically relevant information."""
        return Attribute('rcsb_uniprot_entry_name')
    @property
    def rcsb_uniprot_keyword(self) -> 'Attr_RcsbUniprotKeyword_5702066830568654507':
        """Keywords constitute a controlled vocabulary that summarises the content of a UniProtKB entry."""
        return Attr_RcsbUniprotKeyword_5702066830568654507()
    @property
    def rcsb_uniprot_protein(self) -> 'Attr_RcsbUniprotProtein_1148492260866263344':
        """"""
        return Attr_RcsbUniprotProtein_1148492260866263344()
    @property
    def rcsb_uniprot_feature(self) -> 'Attr_RcsbUniprotFeature_1881409233569800478':
        """"""
        return Attr_RcsbUniprotFeature_1881409233569800478()
    @property
    def rcsb_uniprot_annotation(self) -> 'Attr_RcsbUniprotAnnotation_3803643403302486016':
        """"""
        return Attr_RcsbUniprotAnnotation_3803643403302486016()
    @property
    def rcsb_uniprot_external_reference(self) -> 'Attr_RcsbUniprotExternalReference_2403504378685336846':
        """"""
        return Attr_RcsbUniprotExternalReference_2403504378685336846()
    @property
    def rcsb_uniprot_alignments(self) -> 'Attr_RcsbUniprotAlignments_2406293443920110804':
        """UniProt pairwise sequence alignments."""
        return Attr_RcsbUniprotAlignments_2406293443920110804()
    @property
    def rcsb_branched_entity_instance_container_identifiers(self) -> 'Attr_RcsbBranchedEntityInstanceContainerIdentifiers_2861184413435366569':
        """"""
        return Attr_RcsbBranchedEntityInstanceContainerIdentifiers_2861184413435366569()
    @property
    def rcsb_branched_instance_annotation(self) -> 'Attr_RcsbBranchedInstanceAnnotation_672822815378712341':
        """"""
        return Attr_RcsbBranchedInstanceAnnotation_672822815378712341()
    @property
    def rcsb_branched_instance_feature(self) -> 'Attr_RcsbBranchedInstanceFeature_6570529883936783032':
        """"""
        return Attr_RcsbBranchedInstanceFeature_6570529883936783032()
    @property
    def rcsb_branched_instance_feature_summary(self) -> 'Attr_RcsbBranchedInstanceFeatureSummary_6073811527940749640':
        """"""
        return Attr_RcsbBranchedInstanceFeatureSummary_6073811527940749640()
    @property
    def rcsb_branched_struct_conn(self) -> 'Attr_RcsbBranchedStructConn_6003569928516495413':
        """"""
        return Attr_RcsbBranchedStructConn_6003569928516495413()
    @property
    def rcsb_ligand_neighbors(self) -> 'Attr_RcsbLigandNeighbors_1880587839048653220':
        """"""
        return Attr_RcsbLigandNeighbors_1880587839048653220()
    @property
    def pdbx_entity_branch(self) -> 'Attr_PdbxEntityBranch_6585698773760777520':
        """"""
        return Attr_PdbxEntityBranch_6585698773760777520()
    @property
    def pdbx_entity_branch_descriptor(self) -> 'Attr_PdbxEntityBranchDescriptor_164054067697101551':
        """"""
        return Attr_PdbxEntityBranchDescriptor_164054067697101551()
    @property
    def rcsb_branched_entity(self) -> 'Attr_RcsbBranchedEntity_7127345435010229726':
        """"""
        return Attr_RcsbBranchedEntity_7127345435010229726()
    @property
    def rcsb_branched_entity_annotation(self) -> 'Attr_RcsbBranchedEntityAnnotation_7897611392574466247':
        """"""
        return Attr_RcsbBranchedEntityAnnotation_7897611392574466247()
    @property
    def rcsb_branched_entity_container_identifiers(self) -> 'Attr_RcsbBranchedEntityContainerIdentifiers_2702156472399669336':
        """"""
        return Attr_RcsbBranchedEntityContainerIdentifiers_2702156472399669336()
    @property
    def rcsb_branched_entity_feature(self) -> 'Attr_RcsbBranchedEntityFeature_1505102972707174718':
        """"""
        return Attr_RcsbBranchedEntityFeature_1505102972707174718()
    @property
    def rcsb_branched_entity_feature_summary(self) -> 'Attr_RcsbBranchedEntityFeatureSummary_8620054670851748367':
        """"""
        return Attr_RcsbBranchedEntityFeatureSummary_8620054670851748367()
    @property
    def rcsb_branched_entity_keywords(self) -> 'Attr_RcsbBranchedEntityKeywords_7809048164391685214':
        """"""
        return Attr_RcsbBranchedEntityKeywords_7809048164391685214()
    @property
    def rcsb_branched_entity_name_com(self) -> 'Attr_RcsbBranchedEntityNameCom_6713474324205697671':
        """"""
        return Attr_RcsbBranchedEntityNameCom_6713474324205697671()
    @property
    def rcsb_branched_entity_name_sys(self) -> 'Attr_RcsbBranchedEntityNameSys_2316662242913320166':
        """"""
        return Attr_RcsbBranchedEntityNameSys_2316662242913320166()
    @property
    def rcsb_polymer_entity_instance_container_identifiers(self) -> 'Attr_RcsbPolymerEntityInstanceContainerIdentifiers_4117279514301415360':
        """"""
        return Attr_RcsbPolymerEntityInstanceContainerIdentifiers_4117279514301415360()
    @property
    def rcsb_polymer_instance_annotation(self) -> 'Attr_RcsbPolymerInstanceAnnotation_2474965843387619093':
        """"""
        return Attr_RcsbPolymerInstanceAnnotation_2474965843387619093()
    @property
    def rcsb_polymer_instance_feature(self) -> 'Attr_RcsbPolymerInstanceFeature_4606921343215410585':
        """"""
        return Attr_RcsbPolymerInstanceFeature_4606921343215410585()
    @property
    def rcsb_polymer_instance_feature_summary(self) -> 'Attr_RcsbPolymerInstanceFeatureSummary_6516870355967066808':
        """"""
        return Attr_RcsbPolymerInstanceFeatureSummary_6516870355967066808()
    @property
    def rcsb_polymer_instance_info(self) -> 'Attr_RcsbPolymerInstanceInfo_2673440109957145241':
        """"""
        return Attr_RcsbPolymerInstanceInfo_2673440109957145241()
    @property
    def rcsb_polymer_struct_conn(self) -> 'Attr_RcsbPolymerStructConn_7021313551494511902':
        """"""
        return Attr_RcsbPolymerStructConn_7021313551494511902()
    @property
    def audit_author(self) -> 'Attr_AuditAuthor_62427880465664534':
        """"""
        return Attr_AuditAuthor_62427880465664534()
    @property
    def cell(self) -> 'Attr_Cell_8152123297833183303':
        """"""
        return Attr_Cell_8152123297833183303()
    @property
    def citation(self) -> 'Attr_Citation_1260406672264572138':
        """"""
        return Attr_Citation_1260406672264572138()
    @property
    def database_2(self) -> 'Attr_Database2_4588843887365885359':
        """"""
        return Attr_Database2_4588843887365885359()
    @property
    def diffrn(self) -> 'Attr_Diffrn_5561519300761882462':
        """"""
        return Attr_Diffrn_5561519300761882462()
    @property
    def diffrn_detector(self) -> 'Attr_DiffrnDetector_540682412782732369':
        """"""
        return Attr_DiffrnDetector_540682412782732369()
    @property
    def diffrn_radiation(self) -> 'Attr_DiffrnRadiation_188986262919187256':
        """"""
        return Attr_DiffrnRadiation_188986262919187256()
    @property
    def diffrn_source(self) -> 'Attr_DiffrnSource_8609644499962653127':
        """"""
        return Attr_DiffrnSource_8609644499962653127()
    @property
    def em_2d_crystal_entity(self) -> 'Attr_Em2dCrystalEntity_5442783675105080567':
        """"""
        return Attr_Em2dCrystalEntity_5442783675105080567()
    @property
    def em_3d_crystal_entity(self) -> 'Attr_Em3dCrystalEntity_362674572910326460':
        """"""
        return Attr_Em3dCrystalEntity_362674572910326460()
    @property
    def em_3d_fitting(self) -> 'Attr_Em3dFitting_183403454660579888':
        """"""
        return Attr_Em3dFitting_183403454660579888()
    @property
    def em_3d_fitting_list(self) -> 'Attr_Em3dFittingList_2436868757309379014':
        """"""
        return Attr_Em3dFittingList_2436868757309379014()
    @property
    def em_3d_reconstruction(self) -> 'Attr_Em3dReconstruction_6962286487449101352':
        """"""
        return Attr_Em3dReconstruction_6962286487449101352()
    @property
    def em_ctf_correction(self) -> 'Attr_EmCtfCorrection_5430460427553524849':
        """"""
        return Attr_EmCtfCorrection_5430460427553524849()
    @property
    def em_diffraction(self) -> 'Attr_EmDiffraction_2470912780379215592':
        """"""
        return Attr_EmDiffraction_2470912780379215592()
    @property
    def em_diffraction_shell(self) -> 'Attr_EmDiffractionShell_4934540720457196892':
        """"""
        return Attr_EmDiffractionShell_4934540720457196892()
    @property
    def em_diffraction_stats(self) -> 'Attr_EmDiffractionStats_4117859647005514778':
        """"""
        return Attr_EmDiffractionStats_4117859647005514778()
    @property
    def em_embedding(self) -> 'Attr_EmEmbedding_779734661784868619':
        """"""
        return Attr_EmEmbedding_779734661784868619()
    @property
    def em_entity_assembly(self) -> 'Attr_EmEntityAssembly_8629257542291011594':
        """"""
        return Attr_EmEntityAssembly_8629257542291011594()
    @property
    def em_experiment(self) -> 'Attr_EmExperiment_7693395228713719246':
        """"""
        return Attr_EmExperiment_7693395228713719246()
    @property
    def em_helical_entity(self) -> 'Attr_EmHelicalEntity_179661736991184042':
        """"""
        return Attr_EmHelicalEntity_179661736991184042()
    @property
    def em_image_recording(self) -> 'Attr_EmImageRecording_7369174113551656390':
        """"""
        return Attr_EmImageRecording_7369174113551656390()
    @property
    def em_imaging(self) -> 'Attr_EmImaging_8443919935556524626':
        """"""
        return Attr_EmImaging_8443919935556524626()
    @property
    def em_particle_selection(self) -> 'Attr_EmParticleSelection_3934816513497008143':
        """"""
        return Attr_EmParticleSelection_3934816513497008143()
    @property
    def em_single_particle_entity(self) -> 'Attr_EmSingleParticleEntity_1456680838209852130':
        """"""
        return Attr_EmSingleParticleEntity_1456680838209852130()
    @property
    def em_software(self) -> 'Attr_EmSoftware_1920208556683351508':
        """"""
        return Attr_EmSoftware_1920208556683351508()
    @property
    def em_specimen(self) -> 'Attr_EmSpecimen_373910393168309909':
        """"""
        return Attr_EmSpecimen_373910393168309909()
    @property
    def em_staining(self) -> 'Attr_EmStaining_3944418554910099293':
        """"""
        return Attr_EmStaining_3944418554910099293()
    @property
    def em_vitrification(self) -> 'Attr_EmVitrification_7134423166492578777':
        """"""
        return Attr_EmVitrification_7134423166492578777()
    @property
    def entry(self) -> 'Attr_Entry_7047640374000475139':
        """"""
        return Attr_Entry_7047640374000475139()
    @property
    def exptl(self) -> 'Attr_Exptl_6468111129516196243':
        """"""
        return Attr_Exptl_6468111129516196243()
    @property
    def exptl_crystal(self) -> 'Attr_ExptlCrystal_8825550452672787166':
        """"""
        return Attr_ExptlCrystal_8825550452672787166()
    @property
    def exptl_crystal_grow(self) -> 'Attr_ExptlCrystalGrow_409049865057722864':
        """"""
        return Attr_ExptlCrystalGrow_409049865057722864()
    @property
    def ihm_entry_collection_mapping(self) -> 'Attr_IhmEntryCollectionMapping_5112330335347866000':
        """"""
        return Attr_IhmEntryCollectionMapping_5112330335347866000()
    @property
    def ihm_external_reference_info(self) -> 'Attr_IhmExternalReferenceInfo_43481185161579931':
        """"""
        return Attr_IhmExternalReferenceInfo_43481185161579931()
    @property
    def ma_data(self) -> 'Attr_MaData_2196974696908633366':
        """"""
        return Attr_MaData_2196974696908633366()
    @property
    def pdbx_SG_project(self) -> 'Attr_PdbxSgProject_5312137082222539390':
        """"""
        return Attr_PdbxSgProject_5312137082222539390()
    @property
    def pdbx_audit_revision_category(self) -> 'Attr_PdbxAuditRevisionCategory_94306754416665653':
        """"""
        return Attr_PdbxAuditRevisionCategory_94306754416665653()
    @property
    def pdbx_audit_revision_details(self) -> 'Attr_PdbxAuditRevisionDetails_7978068151254483793':
        """"""
        return Attr_PdbxAuditRevisionDetails_7978068151254483793()
    @property
    def pdbx_audit_revision_group(self) -> 'Attr_PdbxAuditRevisionGroup_3357869764139277325':
        """"""
        return Attr_PdbxAuditRevisionGroup_3357869764139277325()
    @property
    def pdbx_audit_revision_history(self) -> 'Attr_PdbxAuditRevisionHistory_4584809085243058953':
        """"""
        return Attr_PdbxAuditRevisionHistory_4584809085243058953()
    @property
    def pdbx_audit_revision_item(self) -> 'Attr_PdbxAuditRevisionItem_355903234718695599':
        """"""
        return Attr_PdbxAuditRevisionItem_355903234718695599()
    @property
    def pdbx_audit_support(self) -> 'Attr_PdbxAuditSupport_6234993279930336019':
        """"""
        return Attr_PdbxAuditSupport_6234993279930336019()
    @property
    def pdbx_database_PDB_obs_spr(self) -> 'Attr_PdbxDatabasePdbObsSpr_2398372918850929347':
        """"""
        return Attr_PdbxDatabasePdbObsSpr_2398372918850929347()
    @property
    def pdbx_database_related(self) -> 'Attr_PdbxDatabaseRelated_7350539981266203513':
        """"""
        return Attr_PdbxDatabaseRelated_7350539981266203513()
    @property
    def pdbx_database_status(self) -> 'Attr_PdbxDatabaseStatus_2843649403162468643':
        """"""
        return Attr_PdbxDatabaseStatus_2843649403162468643()
    @property
    def pdbx_deposit_group(self) -> 'Attr_PdbxDepositGroup_7970256297506492451':
        """"""
        return Attr_PdbxDepositGroup_7970256297506492451()
    @property
    def pdbx_initial_refinement_model(self) -> 'Attr_PdbxInitialRefinementModel_6955766111047015209':
        """"""
        return Attr_PdbxInitialRefinementModel_6955766111047015209()
    @property
    def pdbx_molecule_features(self) -> 'Attr_PdbxMoleculeFeatures_672286848675098587':
        """"""
        return Attr_PdbxMoleculeFeatures_672286848675098587()
    @property
    def pdbx_nmr_details(self) -> 'Attr_PdbxNmrDetails_8942441883318100394':
        """"""
        return Attr_PdbxNmrDetails_8942441883318100394()
    @property
    def pdbx_nmr_ensemble(self) -> 'Attr_PdbxNmrEnsemble_2203587242519146887':
        """"""
        return Attr_PdbxNmrEnsemble_2203587242519146887()
    @property
    def pdbx_nmr_exptl(self) -> 'Attr_PdbxNmrExptl_996468958718618529':
        """"""
        return Attr_PdbxNmrExptl_996468958718618529()
    @property
    def pdbx_nmr_exptl_sample_conditions(self) -> 'Attr_PdbxNmrExptlSampleConditions_3017575829123646322':
        """"""
        return Attr_PdbxNmrExptlSampleConditions_3017575829123646322()
    @property
    def pdbx_nmr_refine(self) -> 'Attr_PdbxNmrRefine_2514587179798376093':
        """"""
        return Attr_PdbxNmrRefine_2514587179798376093()
    @property
    def pdbx_nmr_representative(self) -> 'Attr_PdbxNmrRepresentative_7165353340664204411':
        """"""
        return Attr_PdbxNmrRepresentative_7165353340664204411()
    @property
    def pdbx_nmr_sample_details(self) -> 'Attr_PdbxNmrSampleDetails_4164748925044019281':
        """"""
        return Attr_PdbxNmrSampleDetails_4164748925044019281()
    @property
    def pdbx_nmr_software(self) -> 'Attr_PdbxNmrSoftware_7903304074939432631':
        """"""
        return Attr_PdbxNmrSoftware_7903304074939432631()
    @property
    def pdbx_nmr_spectrometer(self) -> 'Attr_PdbxNmrSpectrometer_518721406184626396':
        """"""
        return Attr_PdbxNmrSpectrometer_518721406184626396()
    @property
    def pdbx_reflns_twin(self) -> 'Attr_PdbxReflnsTwin_6266513563282235397':
        """"""
        return Attr_PdbxReflnsTwin_6266513563282235397()
    @property
    def pdbx_related_exp_data_set(self) -> 'Attr_PdbxRelatedExpDataSet_510615844747980254':
        """"""
        return Attr_PdbxRelatedExpDataSet_510615844747980254()
    @property
    def pdbx_serial_crystallography_data_reduction(self) -> 'Attr_PdbxSerialCrystallographyDataReduction_5645660585384434442':
        """"""
        return Attr_PdbxSerialCrystallographyDataReduction_5645660585384434442()
    @property
    def pdbx_serial_crystallography_measurement(self) -> 'Attr_PdbxSerialCrystallographyMeasurement_7227600034672541797':
        """"""
        return Attr_PdbxSerialCrystallographyMeasurement_7227600034672541797()
    @property
    def pdbx_serial_crystallography_sample_delivery(self) -> 'Attr_PdbxSerialCrystallographySampleDelivery_1301595853714466834':
        """"""
        return Attr_PdbxSerialCrystallographySampleDelivery_1301595853714466834()
    @property
    def pdbx_serial_crystallography_sample_delivery_fixed_target(self) -> 'Attr_PdbxSerialCrystallographySampleDeliveryFixedTarget_4202109415478603101':
        """"""
        return Attr_PdbxSerialCrystallographySampleDeliveryFixedTarget_4202109415478603101()
    @property
    def pdbx_serial_crystallography_sample_delivery_injection(self) -> 'Attr_PdbxSerialCrystallographySampleDeliveryInjection_1302945912861463402':
        """"""
        return Attr_PdbxSerialCrystallographySampleDeliveryInjection_1302945912861463402()
    @property
    def pdbx_soln_scatter(self) -> 'Attr_PdbxSolnScatter_5325256616457838874':
        """"""
        return Attr_PdbxSolnScatter_5325256616457838874()
    @property
    def pdbx_soln_scatter_model(self) -> 'Attr_PdbxSolnScatterModel_4225404216560231291':
        """"""
        return Attr_PdbxSolnScatterModel_4225404216560231291()
    @property
    def pdbx_vrpt_summary(self) -> 'Attr_PdbxVrptSummary_382225482295680055':
        """"""
        return Attr_PdbxVrptSummary_382225482295680055()
    @property
    def pdbx_vrpt_summary_diffraction(self) -> 'Attr_PdbxVrptSummaryDiffraction_3838680457496923333':
        """"""
        return Attr_PdbxVrptSummaryDiffraction_3838680457496923333()
    @property
    def pdbx_vrpt_summary_em(self) -> 'Attr_PdbxVrptSummaryEm_2090535797322644506':
        """"""
        return Attr_PdbxVrptSummaryEm_2090535797322644506()
    @property
    def pdbx_vrpt_summary_geometry(self) -> 'Attr_PdbxVrptSummaryGeometry_3987198781088756668':
        """"""
        return Attr_PdbxVrptSummaryGeometry_3987198781088756668()
    @property
    def pdbx_vrpt_summary_nmr(self) -> 'Attr_PdbxVrptSummaryNmr_1781281589840552930':
        """"""
        return Attr_PdbxVrptSummaryNmr_1781281589840552930()
    @property
    def rcsb_accession_info(self) -> 'Attr_RcsbAccessionInfo_5412680110888487367':
        """"""
        return Attr_RcsbAccessionInfo_5412680110888487367()
    @property
    def rcsb_binding_affinity(self) -> 'Attr_RcsbBindingAffinity_2637605452600619135':
        """"""
        return Attr_RcsbBindingAffinity_2637605452600619135()
    @property
    def rcsb_comp_model_provenance(self) -> 'Attr_RcsbCompModelProvenance_3545842955570420179':
        """"""
        return Attr_RcsbCompModelProvenance_3545842955570420179()
    @property
    def rcsb_entry_container_identifiers(self) -> 'Attr_RcsbEntryContainerIdentifiers_1853475238367472706':
        """"""
        return Attr_RcsbEntryContainerIdentifiers_1853475238367472706()
    @property
    def rcsb_entry_group_membership(self) -> 'Attr_RcsbEntryGroupMembership_6556163331500770084':
        """"""
        return Attr_RcsbEntryGroupMembership_6556163331500770084()
    @property
    def rcsb_entry_info(self) -> 'Attr_RcsbEntryInfo_9153466176300520716':
        """"""
        return Attr_RcsbEntryInfo_9153466176300520716()
    @property
    def rcsb_external_references(self) -> 'Attr_RcsbExternalReferences_35346722406294313':
        """"""
        return Attr_RcsbExternalReferences_35346722406294313()
    @property
    def rcsb_ihm_dataset_list(self) -> 'Attr_RcsbIhmDatasetList_7444655874522715573':
        """"""
        return Attr_RcsbIhmDatasetList_7444655874522715573()
    @property
    def rcsb_ihm_dataset_source_db_reference(self) -> 'Attr_RcsbIhmDatasetSourceDbReference_4072845881100142479':
        """"""
        return Attr_RcsbIhmDatasetSourceDbReference_4072845881100142479()
    @property
    def rcsb_ma_qa_metric_global(self) -> 'Attr_RcsbMaQaMetricGlobal_6198698729975125693':
        """"""
        return Attr_RcsbMaQaMetricGlobal_6198698729975125693()
    @property
    def rcsb_primary_citation(self) -> 'Attr_RcsbPrimaryCitation_7888783886584885968':
        """"""
        return Attr_RcsbPrimaryCitation_7888783886584885968()
    @property
    def refine(self) -> 'Attr_Refine_7912134435919030599':
        """"""
        return Attr_Refine_7912134435919030599()
    @property
    def refine_analyze(self) -> 'Attr_RefineAnalyze_3766990047408157880':
        """"""
        return Attr_RefineAnalyze_3766990047408157880()
    @property
    def refine_hist(self) -> 'Attr_RefineHist_8709642682844207763':
        """"""
        return Attr_RefineHist_8709642682844207763()
    @property
    def refine_ls_restr(self) -> 'Attr_RefineLsRestr_7134436328750966974':
        """"""
        return Attr_RefineLsRestr_7134436328750966974()
    @property
    def reflns(self) -> 'Attr_Reflns_4430294562024073293':
        """"""
        return Attr_Reflns_4430294562024073293()
    @property
    def reflns_shell(self) -> 'Attr_ReflnsShell_7995187720501940459':
        """"""
        return Attr_ReflnsShell_7995187720501940459()
    @property
    def software(self) -> 'Attr_Software_2560259537581220155':
        """"""
        return Attr_Software_2560259537581220155()
    @property
    def struct(self) -> 'Attr_Struct_1438102844827982749':
        """"""
        return Attr_Struct_1438102844827982749()
    @property
    def struct_keywords(self) -> 'Attr_StructKeywords_3901773578464770903':
        """"""
        return Attr_StructKeywords_3901773578464770903()
    @property
    def symmetry(self) -> 'Attr_Symmetry_8107587269104871708':
        """"""
        return Attr_Symmetry_8107587269104871708()
    @property
    def rcsb_pubmed_container_identifiers(self) -> 'Attr_RcsbPubmedContainerIdentifiers_4606950534434183105':
        """"""
        return Attr_RcsbPubmedContainerIdentifiers_4606950534434183105()
    @property
    def rcsb_pubmed_central_id(self) -> Attribute:
        """Unique integer value assigned to each PubMed Central record."""
        return Attribute('rcsb_pubmed_central_id')
    @property
    def rcsb_pubmed_doi(self) -> Attribute:
        """Persistent identifier used to provide a link to an article location on the Internet."""
        return Attribute('rcsb_pubmed_doi')
    @property
    def rcsb_pubmed_abstract_text(self) -> Attribute:
        """A concise, accurate and factual mini-version of the paper contents."""
        return Attribute('rcsb_pubmed_abstract_text')
    @property
    def rcsb_pubmed_affiliation_info(self) -> Attribute:
        """The institution(s) that the author is affiliated with. Multiple affiliations per author are allowed."""
        return Attribute('rcsb_pubmed_affiliation_info')
    @property
    def rcsb_pubmed_mesh_descriptors(self) -> Attribute:
        """NLM controlled vocabulary, Medical Subject Headings (MeSH), is used to characterize the content of the articles represented by MEDLINE citations."""
        return Attribute('rcsb_pubmed_mesh_descriptors')
    @property
    def rcsb_pubmed_mesh_descriptors_lineage(self) -> 'Attr_RcsbPubmedMeshDescriptorsLineage_239826911826696632':
        """Members of the MeSH classification lineage."""
        return Attr_RcsbPubmedMeshDescriptorsLineage_239826911826696632()
    @property
    def entity_poly(self) -> 'Attr_EntityPoly_565075102590953250':
        """"""
        return Attr_EntityPoly_565075102590953250()
    @property
    def entity_src_gen(self) -> 'Attr_EntitySrcGen_4801190379354878659':
        """"""
        return Attr_EntitySrcGen_4801190379354878659()
    @property
    def entity_src_nat(self) -> 'Attr_EntitySrcNat_2888136308711114733':
        """"""
        return Attr_EntitySrcNat_2888136308711114733()
    @property
    def pdbx_entity_src_syn(self) -> 'Attr_PdbxEntitySrcSyn_8594067501614494274':
        """"""
        return Attr_PdbxEntitySrcSyn_8594067501614494274()
    @property
    def rcsb_cluster_flexibility(self) -> 'Attr_RcsbClusterFlexibility_9137763694137947026':
        """"""
        return Attr_RcsbClusterFlexibility_9137763694137947026()
    @property
    def rcsb_cluster_membership(self) -> 'Attr_RcsbClusterMembership_3657139151815645104':
        """"""
        return Attr_RcsbClusterMembership_3657139151815645104()
    @property
    def rcsb_entity_host_organism(self) -> 'Attr_RcsbEntityHostOrganism_2339318299077688287':
        """"""
        return Attr_RcsbEntityHostOrganism_2339318299077688287()
    @property
    def rcsb_entity_source_organism(self) -> 'Attr_RcsbEntitySourceOrganism_7670836516038773145':
        """"""
        return Attr_RcsbEntitySourceOrganism_7670836516038773145()
    @property
    def rcsb_genomic_lineage(self) -> 'Attr_RcsbGenomicLineage_7387597817044800956':
        """"""
        return Attr_RcsbGenomicLineage_7387597817044800956()
    @property
    def rcsb_membrane_lineage(self) -> 'Attr_RcsbMembraneLineage_5001566126692314102':
        """"""
        return Attr_RcsbMembraneLineage_5001566126692314102()
    @property
    def rcsb_polymer_entity(self) -> 'Attr_RcsbPolymerEntity_5921975448015471234':
        """"""
        return Attr_RcsbPolymerEntity_5921975448015471234()
    @property
    def rcsb_polymer_entity_align(self) -> 'Attr_RcsbPolymerEntityAlign_1484248402375036549':
        """"""
        return Attr_RcsbPolymerEntityAlign_1484248402375036549()
    @property
    def rcsb_polymer_entity_annotation(self) -> 'Attr_RcsbPolymerEntityAnnotation_5571272436143411659':
        """"""
        return Attr_RcsbPolymerEntityAnnotation_5571272436143411659()
    @property
    def rcsb_polymer_entity_container_identifiers(self) -> 'Attr_RcsbPolymerEntityContainerIdentifiers_8865481299329375829':
        """"""
        return Attr_RcsbPolymerEntityContainerIdentifiers_8865481299329375829()
    @property
    def rcsb_polymer_entity_feature(self) -> 'Attr_RcsbPolymerEntityFeature_7686936654585147572':
        """"""
        return Attr_RcsbPolymerEntityFeature_7686936654585147572()
    @property
    def rcsb_polymer_entity_feature_summary(self) -> 'Attr_RcsbPolymerEntityFeatureSummary_356259014689795612':
        """"""
        return Attr_RcsbPolymerEntityFeatureSummary_356259014689795612()
    @property
    def rcsb_polymer_entity_group_membership(self) -> 'Attr_RcsbPolymerEntityGroupMembership_3724512927620508481':
        """"""
        return Attr_RcsbPolymerEntityGroupMembership_3724512927620508481()
    @property
    def rcsb_polymer_entity_keywords(self) -> 'Attr_RcsbPolymerEntityKeywords_111563731748706027':
        """"""
        return Attr_RcsbPolymerEntityKeywords_111563731748706027()
    @property
    def rcsb_polymer_entity_name_com(self) -> 'Attr_RcsbPolymerEntityNameCom_3999100602014898303':
        """"""
        return Attr_RcsbPolymerEntityNameCom_3999100602014898303()
    @property
    def rcsb_polymer_entity_name_sys(self) -> 'Attr_RcsbPolymerEntityNameSys_7214700575849167110':
        """"""
        return Attr_RcsbPolymerEntityNameSys_7214700575849167110()
    @property
    def rcsb_related_target_references(self) -> 'Attr_RcsbRelatedTargetReferences_4514573363264039448':
        """"""
        return Attr_RcsbRelatedTargetReferences_4514573363264039448()
    @property
    def rcsb_target_cofactors(self) -> 'Attr_RcsbTargetCofactors_1473429961113133440':
        """"""
        return Attr_RcsbTargetCofactors_1473429961113133440()
    @property
    def rcsb_membrane_lineage_provenance_code(self) -> Attribute:
        """Mpstruc keyword denotes original annotation, Homology keyword denotes annotation inferred by homology."""
        return Attribute('rcsb_membrane_lineage_provenance_code')
    @property
    def drugbank_container_identifiers(self) -> 'Attr_DrugbankContainerIdentifiers_2912637152102270126':
        """"""
        return Attr_DrugbankContainerIdentifiers_2912637152102270126()
    @property
    def drugbank_info(self) -> 'Attr_DrugbankInfo_8732299424569036807':
        """"""
        return Attr_DrugbankInfo_8732299424569036807()
    @property
    def drugbank_target(self) -> 'Attr_DrugbankTarget_2055091295599847616':
        """"""
        return Attr_DrugbankTarget_2055091295599847616()

attrs = AttributesRoot_0()
