import textwrap
import requests
from typing import Any, Optional, List, Union

RCSB_ARGUMENT_TYPES = {
    "polymer_entity_instance": {"asym_id": "String!", "entry_id": "String!"},
    "chem_comps": {"comp_ids": "[String]!"},
    "nonpolymer_entity_groups": {"group_ids": "[String]!"},
    "polymer_entity_groups": {"group_ids": "[String]!"},
    "interface": {"assembly_id": "String!", "interface_id": "String!", "entry_id": "String!"},
    "nonpolymer_entities": {"entity_ids": "[String!]!"},
    "polymer_entities": {"entity_ids": "[String!]!"},
    "polymer_entity": {"entity_id": "String!", "entry_id": "String!"},
    "entry_group": {"group_id": "String!"},
    "pubmed": {"pubmed_id": "Int!"},
    "assembly": {"assembly_id": "String!", "entry_id": "String!"},
    "branched_entity_instances": {"instance_ids": "[String]!"},
    "group_provenance": {"group_provenance_id": "String!"},
    "polymer_entity_instances": {"instance_ids": "[String]!"},
    "interfaces": {"interface_ids": "[String!]!"},
    "nonpolymer_entity_group": {"group_id": "String!"},
    "assemblies": {"assembly_ids": "[String]!"},
    "branched_entity": {"entity_id": "String!", "entry_id": "String!"},
    "polymer_entity_group": {"group_id": "String!"},
    "branched_entity_instance": {"asym_id": "String!", "entry_id": "String!"},
    "nonpolymer_entity_instance": {"asym_id": "String!", "entry_id": "String!"},
    "chem_comp": {"comp_id": "String!"},
    "entry": {"entry_id": "String!"},
    "entries": {"entry_ids": "[String!]!"},
    "entry_groups": {"group_ids": "[String]!"},
    "branched_entities": {"entity_ids": "[String!]!"},
    "uniprot": {"uniprot_id": "String!"},
    "nonpolymer_entity_instances": {"instance_ids": "[String]!"},
    "nonpolymer_entity": {"entity_id": "String!", "entry_id": "String!"}
}

# --- Query Logic ---

class QueryNode:
    def __init__(self, name=None, parent=None, arguments=None):
        self._name = name
        self._parent = parent
        self._children = []
        self._arguments = arguments or {}

    def _enter(self, name, node_class, **kwargs):
        # Deduplication: Return existing node if already requested
        for child in self._children:
            if child._name == name and isinstance(child, node_class):
                child._arguments.update(kwargs)
                return child
        
        # Create new typed node
        new_node = node_class(name=name, parent=self, arguments=kwargs)
        self._children.append(new_node)
        return new_node

    @property
    def end(self):
        """Navigates back to the parent node."""
        return self._parent if self._parent else self

    def render(self, query_name="structure"):
        root = self
        while root._parent:
            root = root._parent

        variable_map = {}
        
        for child in root._children:
            # Skip if it's just a string/scalar leaf
            if not hasattr(child, "_name"): 
                continue

            known_args = RCSB_ARGUMENT_TYPES.get(child._name, {})

            for arg_name, arg_value in child._arguments.items():
                if isinstance(arg_value, str) and arg_value.startswith("$"):
                    clean_var_name = arg_value[1:] # remove $
                    gql_type = known_args.get(arg_name, "String!")
                    variable_map[clean_var_name] = gql_type

        var_header = ""
        if variable_map:
            # Sort for consistent output
            defs = [f"${name}: {type_def}" for name, type_def in sorted(variable_map.items())]
            var_header = f"({', '.join(defs)})"

        fields = root._render_node(indent=2)
        return f"query {query_name}{var_header} {{\n{fields}\n}}"

    def _render_node(self, indent=0):
        pad = " " * indent
        if self._name is None: # Root
            parts = [c._render_node(indent) for c in self._children]
            return "\n".join(filter(None, parts))

        # Format Arguments
        name_part = self._name
        if self._arguments:
            args = []
            for k, v in self._arguments.items():
                if isinstance(v, str) and v.startswith("$"):
                    args.append(f'{k}: {v}')
                elif isinstance(v, str):
                    args.append(f'{k}: "{v}"')
                else:
                    args.append(f"{k}: {v}")

            name_part = f"{self._name}({', '.join(args)})"

        if not self._children:
            # Leaf node (Scalar)
            return f"{pad}{name_part}"
        
        # Object node
        inner = [c._render_node(indent + 2) for c in self._children]
        # Filter empty blocks (Ghost nodes)
        inner = list(filter(None, inner))
        if not inner:
            return "" 
            
        return f"{pad}{name_part} {{\n" + "\n".join(inner) + f"\n{pad}}}"

    @staticmethod
    def execute(rendered_query: str, **variables):
        """Executes a rendered GraphQL query against the RCSB Data API."""
        response = requests.post(
            "https://data.rcsb.org/graphql",
            json={
            	"query": rendered_query,
            	"variables": variables or {}
            },
        )
        response.raise_for_status()
    
        return response.json().get("data", {})

    def submit(self, **variables):
        """Renders and executes the stored query.
        Use `QueryNode.execute` if running multiple submissions."""
        return self.execute(self.render(), **variables)

# --- Generated Schema Classes ---

class AuditAuthor(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def identifier_ORCID(self) -> 'AuditAuthor':
		"""The Open Researcher and Contributor ID (ORCID).  Examples: 0000-0002-6681-547X """
		self._enter('identifier_ORCID', Query)
		return self
	@property
	def name(self) -> 'AuditAuthor':
		"""The name of an author of this data block. If there are multiple  authors, _audit_author.name is looped with _audit_author.address.  The family name(s), followed by a comma and including any  dynastic components, precedes the first name(s) or initial(s).  Examples: Jones, T.J., Bleary, Percival R., O'Neil, F.K., Van den Bossche, G., Yang, D.-L., Simonov, Yu.A """
		self._enter('name', Query)
		return self
	@property
	def pdbx_ordinal(self) -> 'AuditAuthor':
		"""This data item defines the order of the author's name in the  list of audit authors."""
		self._enter('pdbx_ordinal', Query)
		return self

class Cell(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def Z_PDB(self) -> 'Cell':
		"""The number of the polymeric chains in a unit cell. In the case  of heteropolymers, Z is the number of occurrences of the most  populous chain.   This data item is provided for compatibility with the original  Protein Data Bank format, and only for that purpose."""
		self._enter('Z_PDB', Query)
		return self
	@property
	def angle_alpha(self) -> 'Cell':
		"""Unit-cell angle alpha of the reported structure in degrees."""
		self._enter('angle_alpha', Query)
		return self
	@property
	def angle_beta(self) -> 'Cell':
		"""Unit-cell angle beta of the reported structure in degrees."""
		self._enter('angle_beta', Query)
		return self
	@property
	def angle_gamma(self) -> 'Cell':
		"""Unit-cell angle gamma of the reported structure in degrees."""
		self._enter('angle_gamma', Query)
		return self
	@property
	def formula_units_Z(self) -> 'Cell':
		"""The number of the formula units in the unit cell as specified  by _chemical_formula.structural, _chemical_formula.moiety or  _chemical_formula.sum."""
		self._enter('formula_units_Z', Query)
		return self
	@property
	def length_a(self) -> 'Cell':
		"""Unit-cell length a corresponding to the structure reported in angstroms."""
		self._enter('length_a', Query)
		return self
	@property
	def length_b(self) -> 'Cell':
		"""Unit-cell length b corresponding to the structure reported in  angstroms."""
		self._enter('length_b', Query)
		return self
	@property
	def length_c(self) -> 'Cell':
		"""Unit-cell length c corresponding to the structure reported in angstroms."""
		self._enter('length_c', Query)
		return self
	@property
	def pdbx_unique_axis(self) -> 'Cell':
		"""To further identify unique axis if necessary.  E.g., P 21 with  an unique C axis will have 'C' in this field."""
		self._enter('pdbx_unique_axis', Query)
		return self
	@property
	def volume(self) -> 'Cell':
		"""Cell volume V in angstroms cubed.   V = a b c (1 - cos^2^~alpha~ - cos^2^~beta~ - cos^2^~gamma~             + 2 cos~alpha~ cos~beta~ cos~gamma~)^1/2^   a     = _cell.length_a  b     = _cell.length_b  c     = _cell.length_c  alpha = _cell.angle_alpha  beta  = _cell.angle_beta  gamma = _cell.angle_gamma"""
		self._enter('volume', Query)
		return self

class ChemComp(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def formula(self) -> 'ChemComp':
		"""The formula for the chemical component. Formulae are written  according to the following rules:   (1) Only recognized element symbols may be used.   (2) Each element symbol is followed by a 'count' number. A count     of '1' may be omitted.   (3) A space or parenthesis must separate each cluster of     (element symbol + count), but in general parentheses are     not used.   (4) The order of elements depends on whether carbon is     present or not. If carbon is present, the order should be:     C, then H, then the other elements in alphabetical order     of their symbol. If carbon is not present, the elements     are listed purely in alphabetic order of their symbol. This     is the 'Hill' system used by Chemical Abstracts.  Examples: C18 H19 N7 O8 S """
		self._enter('formula', Query)
		return self
	@property
	def formula_weight(self) -> 'ChemComp':
		"""Formula mass of the chemical component.  Examples: null, null """
		self._enter('formula_weight', Query)
		return self
	@property
	def id(self) -> 'ChemComp':
		"""The value of _chem_comp.id must uniquely identify each item in  the CHEM_COMP list.   For protein polymer entities, this is the three-letter code for  the amino acid.   For nucleic acid polymer entities, this is the one-letter code  for the base.  Examples: ALA, VAL, DG, C """
		self._enter('id', Query)
		return self
	@property
	def mon_nstd_parent_comp_id(self) -> 'ChemComp':
		"""The identifier for the parent component of the nonstandard  component. May be be a comma separated list if this component  is derived from multiple components.   Items in this indirectly point to _chem_comp.id in  the CHEM_COMP category."""
		self._enter('mon_nstd_parent_comp_id', Query)
		return self
	@property
	def name(self) -> 'ChemComp':
		"""The full name of the component.  Examples: alanine, valine, adenine, cytosine """
		self._enter('name', Query)
		return self
	@property
	def one_letter_code(self) -> 'ChemComp':
		"""For standard polymer components, the one-letter code for  the component.   For non-standard polymer components, the  one-letter code for parent component if this exists;  otherwise, the one-letter code should be given as 'X'.   Components that derived from multiple parents components  are described by a sequence of one-letter-codes.  Examples: A, B, R, N, D, C, Q, E, Z, G, H, I, L, K, M, F, P, S, T, W, Y, V, U, O, X """
		self._enter('one_letter_code', Query)
		return self
	@property
	def pdbx_ambiguous_flag(self) -> 'ChemComp':
		"""A preliminary classification used by PDB to indicate  that the chemistry of this component while described  as clearly as possible is still ambiguous.  Software  tools may not be able to process this component  definition."""
		self._enter('pdbx_ambiguous_flag', Query)
		return self
	@property
	def pdbx_formal_charge(self) -> 'ChemComp':
		"""The net integer charge assigned to this component. This is the  formal charge assignment normally found in chemical diagrams."""
		self._enter('pdbx_formal_charge', Query)
		return self
	@property
	def pdbx_initial_date(self) -> 'ChemComp':
		"""Date component was added to database."""
		self._enter('pdbx_initial_date', Query)
		return self
	@property
	def pdbx_modified_date(self) -> 'ChemComp':
		"""Date component was last modified."""
		self._enter('pdbx_modified_date', Query)
		return self
	@property
	def pdbx_processing_site(self) -> 'ChemComp':
		"""This data item identifies the deposition site that processed  this chemical component defintion.  Allowable values: EBI, PDBC, PDBE, PDBJ, RCSB """
		self._enter('pdbx_processing_site', Query)
		return self
	@property
	def pdbx_release_status(self) -> 'ChemComp':
		"""This data item holds the current release status for the component.  Allowable values: DEL, HOLD, HPUB, OBS, REF_ONLY, REL """
		self._enter('pdbx_release_status', Query)
		return self
	@property
	def pdbx_replaced_by(self) -> 'ChemComp':
		"""Identifies the _chem_comp.id of the component that  has replaced this component.  Examples: q11, tvx """
		self._enter('pdbx_replaced_by', Query)
		return self
	@property
	def pdbx_replaces(self) -> 'ChemComp':
		"""Identifies the _chem_comp.id's of the components  which have been replaced by this component.  Multiple id codes should be separated by commas.  Examples: q11, tvx,atv """
		self._enter('pdbx_replaces', Query)
		return self
	@property
	def pdbx_subcomponent_list(self) -> 'ChemComp':
		"""The list of subcomponents contained in this component.  Examples: TSM DPH HIS CHF EMR """
		self._enter('pdbx_subcomponent_list', Query)
		return self
	@property
	def three_letter_code(self) -> 'ChemComp':
		"""For standard polymer components, the common three-letter code for  the component.   Non-standard polymer components and non-polymer  components are also assigned three-letter-codes.   For ambiguous polymer components three-letter code should  be given as 'UNK'.  Ambiguous ions are assigned the code 'UNX'.  Ambiguous non-polymer components are assigned the code 'UNL'.  Examples: ALA, ARG, ASN, ASP, ASX, CYS, GLN, GLU, GLY, GLX, HIS, ILE, LEU, LYS, MET, PHE, PRO, SER, THR, TRP, TYR, VAL, 1MA, 5MC, OMC, 1MG, 2MG, M2G, 7MG, 0MG, H2U, 5MU, PSU, ACE, FOR, HOH, UNK """
		self._enter('three_letter_code', Query)
		return self
	@property
	def type(self) -> 'ChemComp':
		"""For standard polymer components, the type of the monomer.  Note that monomers that will form polymers are of three types:  linking monomers, monomers with some type of N-terminal (or 5')  cap and monomers with some type of C-terminal (or 3') cap.  Allowable values: D-beta-peptide, C-gamma linking, D-gamma-peptide, C-delta linking, D-peptide COOH carboxy terminus, D-peptide NH3 amino terminus, D-peptide linking, D-saccharide, D-saccharide, alpha linking, D-saccharide, beta linking, DNA OH 3 prime terminus, DNA OH 5 prime terminus, DNA linking, L-DNA linking, L-RNA linking, L-beta-peptide, C-gamma linking, L-gamma-peptide, C-delta linking, L-peptide COOH carboxy terminus, L-peptide NH3 amino terminus, L-peptide linking, L-saccharide, L-saccharide, alpha linking, L-saccharide, beta linking, RNA OH 3 prime terminus, RNA OH 5 prime terminus, RNA linking, non-polymer, other, peptide linking, peptide-like, saccharide """
		self._enter('type', Query)
		return self

class Citation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def book_id_ISBN(self) -> 'Citation':
		"""The International Standard Book Number (ISBN) code assigned to  the book cited; relevant for books or book chapters."""
		self._enter('book_id_ISBN', Query)
		return self
	@property
	def book_publisher(self) -> 'Citation':
		"""The name of the publisher of the citation; relevant  for books or book chapters.  Examples: John Wiley and Sons """
		self._enter('book_publisher', Query)
		return self
	@property
	def book_publisher_city(self) -> 'Citation':
		"""The location of the publisher of the citation; relevant  for books or book chapters.  Examples: London """
		self._enter('book_publisher_city', Query)
		return self
	@property
	def book_title(self) -> 'Citation':
		"""The title of the book in which the citation appeared; relevant  for books or book chapters."""
		self._enter('book_title', Query)
		return self
	@property
	def coordinate_linkage(self) -> 'Citation':
		"""_citation.coordinate_linkage states whether this citation  is concerned with precisely the set of coordinates given in the  data block. If, for instance, the publication described the same  structure, but the coordinates had undergone further refinement  prior to the creation of the data block, the value of this data  item would be 'no'.  Allowable values: n, no, y, yes """
		self._enter('coordinate_linkage', Query)
		return self
	@property
	def country(self) -> 'Citation':
		"""The country/region of publication; relevant for books  and book chapters."""
		self._enter('country', Query)
		return self
	@property
	def id(self) -> 'Citation':
		"""The value of _citation.id must uniquely identify a record in the  CITATION list.   The _citation.id 'primary' should be used to indicate the  citation that the author(s) consider to be the most pertinent to  the contents of the data block.   Note that this item need not be a number; it can be any unique  identifier.  Examples: primary, 1, 2 """
		self._enter('id', Query)
		return self
	@property
	def journal_abbrev(self) -> 'Citation':
		"""Abbreviated name of the cited journal as given in the  Chemical Abstracts Service Source Index.  Examples: J.Mol.Biol., J. Mol. Biol. """
		self._enter('journal_abbrev', Query)
		return self
	@property
	def journal_full(self) -> 'Citation':
		"""Full name of the cited journal; relevant for journal articles.  Examples: Journal of Molecular Biology """
		self._enter('journal_full', Query)
		return self
	@property
	def journal_id_ASTM(self) -> 'Citation':
		"""The American Society for Testing and Materials (ASTM) code  assigned to the journal cited (also referred to as the CODEN  designator of the Chemical Abstracts Service); relevant for  journal articles."""
		self._enter('journal_id_ASTM', Query)
		return self
	@property
	def journal_id_CSD(self) -> 'Citation':
		"""The Cambridge Structural Database (CSD) code assigned to the  journal cited; relevant for journal articles. This is also the  system used at the Protein Data Bank (PDB).  Examples: 0070 """
		self._enter('journal_id_CSD', Query)
		return self
	@property
	def journal_id_ISSN(self) -> 'Citation':
		"""The International Standard Serial Number (ISSN) code assigned to  the journal cited; relevant for journal articles."""
		self._enter('journal_id_ISSN', Query)
		return self
	@property
	def journal_issue(self) -> 'Citation':
		"""Issue number of the journal cited; relevant for journal  articles.  Examples: 2 """
		self._enter('journal_issue', Query)
		return self
	@property
	def journal_volume(self) -> 'Citation':
		"""Volume number of the journal cited; relevant for journal  articles.  Examples: 174 """
		self._enter('journal_volume', Query)
		return self
	@property
	def language(self) -> 'Citation':
		"""Language in which the cited article is written.  Examples: German """
		self._enter('language', Query)
		return self
	@property
	def page_first(self) -> 'Citation':
		"""The first page of the citation; relevant for journal  articles, books and book chapters."""
		self._enter('page_first', Query)
		return self
	@property
	def page_last(self) -> 'Citation':
		"""The last page of the citation; relevant for journal  articles, books and book chapters."""
		self._enter('page_last', Query)
		return self
	@property
	def pdbx_database_id_DOI(self) -> 'Citation':
		"""Document Object Identifier used by doi.org to uniquely  specify bibliographic entry.  Examples: 10.2345/S1384107697000225 """
		self._enter('pdbx_database_id_DOI', Query)
		return self
	@property
	def pdbx_database_id_PubMed(self) -> 'Citation':
		"""Ascession number used by PubMed to categorize a specific  bibliographic entry."""
		self._enter('pdbx_database_id_PubMed', Query)
		return self
	@property
	def rcsb_authors(self) -> 'Citation':
		"""Names of the authors of the citation; relevant for journal  articles, books and book chapters.  Names are separated by vertical bars.   The family name(s), followed by a comma and including any  dynastic components, precedes the first name(s) or initial(s)."""
		self._enter('rcsb_authors', Query)
		return self
	@property
	def rcsb_is_primary(self) -> 'Citation':
		"""Flag to indicate a primary citation.  Allowable values: N, Y """
		self._enter('rcsb_is_primary', Query)
		return self
	@property
	def rcsb_journal_abbrev(self) -> 'Citation':
		"""Normalized journal abbreviation.  Examples: Nat Struct Mol Biol """
		self._enter('rcsb_journal_abbrev', Query)
		return self
	@property
	def title(self) -> 'Citation':
		"""The title of the citation; relevant for journal articles, books  and book chapters.  Examples: Structure of diferric duck ovotransferrin                                   at 2.35 Angstroms resolution. """
		self._enter('title', Query)
		return self
	@property
	def unpublished_flag(self) -> 'Citation':
		"""Flag to indicate that this citation will not be published.  Allowable values: N, Y """
		self._enter('unpublished_flag', Query)
		return self
	@property
	def year(self) -> 'Citation':
		"""The year of the citation; relevant for journal articles, books  and book chapters."""
		self._enter('year', Query)
		return self

class ClustersMembers(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbStructSymmetryClusters':
		"""Return to parent (RcsbStructSymmetryClusters)"""
		return self._parent if self._parent else self
	@property
	def asym_id(self) -> 'ClustersMembers':
		"""Internal chain ID used in mmCIF files to uniquely identify structural elements in the asymmetric unit."""
		self._enter('asym_id', Query)
		return self
	@property
	def pdbx_struct_oper_list_ids(self) -> 'ClustersMembers':
		"""Optional list of operator ids (pdbx_struct_oper_list.id) as appears in pdbx_struct_assembly_gen.oper_expression."""
		self._enter('pdbx_struct_oper_list_ids', Query)
		return self

class CoreAssembly(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def branched_entity_instances(self) -> 'CoreBranchedEntityInstance':
		"""Get a list of branched entity instances (sugars) that constitute this assembly."""
		return self._enter('branched_entity_instances', CoreBranchedEntityInstance)
	@property
	def entry(self) -> 'CoreEntry':
		"""Get entry that includes this assembly."""
		return self._enter('entry', CoreEntry)
	@property
	def interfaces(self) -> 'CoreInterface':
		"""Get all pairwise polymer interfaces for this assembly."""
		return self._enter('interfaces', CoreInterface)
	@property
	def nonpolymer_entity_instances(self) -> 'CoreNonpolymerEntityInstance':
		"""Get a list of non-polymer entity instances (ligands) that constitute this assembly."""
		return self._enter('nonpolymer_entity_instances', CoreNonpolymerEntityInstance)
	@property
	def pdbx_struct_assembly(self) -> 'PdbxStructAssembly':
		""""""
		return self._enter('pdbx_struct_assembly', PdbxStructAssembly)
	@property
	def pdbx_struct_assembly_auth_evidence(self) -> 'PdbxStructAssemblyAuthEvidence':
		""""""
		return self._enter('pdbx_struct_assembly_auth_evidence', PdbxStructAssemblyAuthEvidence)
	@property
	def pdbx_struct_assembly_gen(self) -> 'PdbxStructAssemblyGen':
		""""""
		return self._enter('pdbx_struct_assembly_gen', PdbxStructAssemblyGen)
	@property
	def pdbx_struct_assembly_prop(self) -> 'PdbxStructAssemblyProp':
		""""""
		return self._enter('pdbx_struct_assembly_prop', PdbxStructAssemblyProp)
	@property
	def pdbx_struct_oper_list(self) -> 'PdbxStructOperList':
		""""""
		return self._enter('pdbx_struct_oper_list', PdbxStructOperList)
	@property
	def polymer_entity_instances(self) -> 'CorePolymerEntityInstance':
		"""Get a list of polymer entity instances (chains) that constitute this assembly."""
		return self._enter('polymer_entity_instances', CorePolymerEntityInstance)
	@property
	def rcsb_assembly_annotation(self) -> 'RcsbAssemblyAnnotation':
		""""""
		return self._enter('rcsb_assembly_annotation', RcsbAssemblyAnnotation)
	@property
	def rcsb_assembly_container_identifiers(self) -> 'RcsbAssemblyContainerIdentifiers':
		""""""
		return self._enter('rcsb_assembly_container_identifiers', RcsbAssemblyContainerIdentifiers)
	@property
	def rcsb_assembly_feature(self) -> 'RcsbAssemblyFeature':
		""""""
		return self._enter('rcsb_assembly_feature', RcsbAssemblyFeature)
	@property
	def rcsb_assembly_info(self) -> 'RcsbAssemblyInfo':
		""""""
		return self._enter('rcsb_assembly_info', RcsbAssemblyInfo)
	@property
	def rcsb_id(self) -> 'CoreAssembly':
		"""A unique identifier for each object in this assembly container formed by  a dash separated concatenation of entry and assembly identifiers.  Examples: 1KIP-1 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)
	@property
	def rcsb_struct_symmetry(self) -> 'RcsbStructSymmetry':
		""""""
		return self._enter('rcsb_struct_symmetry', RcsbStructSymmetry)
	@property
	def rcsb_struct_symmetry_lineage(self) -> 'RcsbStructSymmetryLineage':
		""""""
		return self._enter('rcsb_struct_symmetry_lineage', RcsbStructSymmetryLineage)
	@property
	def rcsb_struct_symmetry_provenance_code(self) -> 'CoreAssembly':
		"""The title and version of software package used for symmetry calculations."""
		self._enter('rcsb_struct_symmetry_provenance_code', Query)
		return self

class CoreBranchedEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def branched_entity_instances(self) -> 'CoreBranchedEntityInstance':
		"""Get all unique branched instances (chains) for this molecular entity."""
		return self._enter('branched_entity_instances', CoreBranchedEntityInstance)
	@property
	def chem_comp_monomers(self) -> 'CoreChemComp':
		"""Get all unique monomers described in this branched entity."""
		return self._enter('chem_comp_monomers', CoreChemComp)
	@property
	def entry(self) -> 'CoreEntry':
		"""Get entry that contains this branched entity."""
		return self._enter('entry', CoreEntry)
	@property
	def pdbx_entity_branch(self) -> 'PdbxEntityBranch':
		""""""
		return self._enter('pdbx_entity_branch', PdbxEntityBranch)
	@property
	def pdbx_entity_branch_descriptor(self) -> 'PdbxEntityBranchDescriptor':
		""""""
		return self._enter('pdbx_entity_branch_descriptor', PdbxEntityBranchDescriptor)
	@property
	def prd(self) -> 'CoreChemComp':
		"""Get a BIRD chemical components described in this branched entity."""
		return self._enter('prd', CoreChemComp)
	@property
	def rcsb_branched_entity(self) -> 'RcsbBranchedEntity':
		""""""
		return self._enter('rcsb_branched_entity', RcsbBranchedEntity)
	@property
	def rcsb_branched_entity_annotation(self) -> 'RcsbBranchedEntityAnnotation':
		""""""
		return self._enter('rcsb_branched_entity_annotation', RcsbBranchedEntityAnnotation)
	@property
	def rcsb_branched_entity_container_identifiers(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		""""""
		return self._enter('rcsb_branched_entity_container_identifiers', RcsbBranchedEntityContainerIdentifiers)
	@property
	def rcsb_branched_entity_feature(self) -> 'RcsbBranchedEntityFeature':
		""""""
		return self._enter('rcsb_branched_entity_feature', RcsbBranchedEntityFeature)
	@property
	def rcsb_branched_entity_feature_summary(self) -> 'RcsbBranchedEntityFeatureSummary':
		""""""
		return self._enter('rcsb_branched_entity_feature_summary', RcsbBranchedEntityFeatureSummary)
	@property
	def rcsb_branched_entity_keywords(self) -> 'RcsbBranchedEntityKeywords':
		""""""
		return self._enter('rcsb_branched_entity_keywords', RcsbBranchedEntityKeywords)
	@property
	def rcsb_branched_entity_name_com(self) -> 'RcsbBranchedEntityNameCom':
		""""""
		return self._enter('rcsb_branched_entity_name_com', RcsbBranchedEntityNameCom)
	@property
	def rcsb_branched_entity_name_sys(self) -> 'RcsbBranchedEntityNameSys':
		""""""
		return self._enter('rcsb_branched_entity_name_sys', RcsbBranchedEntityNameSys)
	@property
	def rcsb_id(self) -> 'CoreBranchedEntity':
		"""A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers.  Examples: 2HYV_2 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)

class CoreBranchedEntityInstance(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def branched_entity(self) -> 'CoreBranchedEntity':
		"""Get branched entity for this branched entity instance."""
		return self._enter('branched_entity', CoreBranchedEntity)
	@property
	def pdbx_struct_special_symmetry(self) -> 'PdbxStructSpecialSymmetry':
		""""""
		return self._enter('pdbx_struct_special_symmetry', PdbxStructSpecialSymmetry)
	@property
	def rcsb_branched_entity_instance_container_identifiers(self) -> 'RcsbBranchedEntityInstanceContainerIdentifiers':
		""""""
		return self._enter('rcsb_branched_entity_instance_container_identifiers', RcsbBranchedEntityInstanceContainerIdentifiers)
	@property
	def rcsb_branched_instance_annotation(self) -> 'RcsbBranchedInstanceAnnotation':
		""""""
		return self._enter('rcsb_branched_instance_annotation', RcsbBranchedInstanceAnnotation)
	@property
	def rcsb_branched_instance_feature(self) -> 'RcsbBranchedInstanceFeature':
		""""""
		return self._enter('rcsb_branched_instance_feature', RcsbBranchedInstanceFeature)
	@property
	def rcsb_branched_instance_feature_summary(self) -> 'RcsbBranchedInstanceFeatureSummary':
		""""""
		return self._enter('rcsb_branched_instance_feature_summary', RcsbBranchedInstanceFeatureSummary)
	@property
	def rcsb_branched_struct_conn(self) -> 'RcsbBranchedStructConn':
		""""""
		return self._enter('rcsb_branched_struct_conn', RcsbBranchedStructConn)
	@property
	def rcsb_id(self) -> 'CoreBranchedEntityInstance':
		"""A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers.  Examples: 1KIP.A """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)
	@property
	def rcsb_ligand_neighbors(self) -> 'RcsbLigandNeighbors':
		""""""
		return self._enter('rcsb_ligand_neighbors', RcsbLigandNeighbors)
	@property
	def struct_asym(self) -> 'StructAsym':
		""""""
		return self._enter('struct_asym', StructAsym)

class CoreChemComp(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def chem_comp(self) -> 'ChemComp':
		""""""
		return self._enter('chem_comp', ChemComp)
	@property
	def drugbank(self) -> 'CoreDrugbank':
		"""Get DrubBank entry associated with this chemical component."""
		return self._enter('drugbank', CoreDrugbank)
	@property
	def pdbx_chem_comp_audit(self) -> 'PdbxChemCompAudit':
		""""""
		return self._enter('pdbx_chem_comp_audit', PdbxChemCompAudit)
	@property
	def pdbx_chem_comp_descriptor(self) -> 'PdbxChemCompDescriptor':
		""""""
		return self._enter('pdbx_chem_comp_descriptor', PdbxChemCompDescriptor)
	@property
	def pdbx_chem_comp_feature(self) -> 'PdbxChemCompFeature':
		""""""
		return self._enter('pdbx_chem_comp_feature', PdbxChemCompFeature)
	@property
	def pdbx_chem_comp_identifier(self) -> 'PdbxChemCompIdentifier':
		""""""
		return self._enter('pdbx_chem_comp_identifier', PdbxChemCompIdentifier)
	@property
	def pdbx_family_prd_audit(self) -> 'PdbxFamilyPrdAudit':
		""""""
		return self._enter('pdbx_family_prd_audit', PdbxFamilyPrdAudit)
	@property
	def pdbx_prd_audit(self) -> 'PdbxPrdAudit':
		""""""
		return self._enter('pdbx_prd_audit', PdbxPrdAudit)
	@property
	def pdbx_reference_entity_list(self) -> 'PdbxReferenceEntityList':
		""""""
		return self._enter('pdbx_reference_entity_list', PdbxReferenceEntityList)
	@property
	def pdbx_reference_entity_poly(self) -> 'PdbxReferenceEntityPoly':
		""""""
		return self._enter('pdbx_reference_entity_poly', PdbxReferenceEntityPoly)
	@property
	def pdbx_reference_entity_poly_link(self) -> 'PdbxReferenceEntityPolyLink':
		""""""
		return self._enter('pdbx_reference_entity_poly_link', PdbxReferenceEntityPolyLink)
	@property
	def pdbx_reference_entity_poly_seq(self) -> 'PdbxReferenceEntityPolySeq':
		""""""
		return self._enter('pdbx_reference_entity_poly_seq', PdbxReferenceEntityPolySeq)
	@property
	def pdbx_reference_entity_sequence(self) -> 'PdbxReferenceEntitySequence':
		""""""
		return self._enter('pdbx_reference_entity_sequence', PdbxReferenceEntitySequence)
	@property
	def pdbx_reference_entity_src_nat(self) -> 'PdbxReferenceEntitySrcNat':
		""""""
		return self._enter('pdbx_reference_entity_src_nat', PdbxReferenceEntitySrcNat)
	@property
	def pdbx_reference_molecule(self) -> 'PdbxReferenceMolecule':
		""""""
		return self._enter('pdbx_reference_molecule', PdbxReferenceMolecule)
	@property
	def pdbx_reference_molecule_annotation(self) -> 'PdbxReferenceMoleculeAnnotation':
		""""""
		return self._enter('pdbx_reference_molecule_annotation', PdbxReferenceMoleculeAnnotation)
	@property
	def pdbx_reference_molecule_details(self) -> 'PdbxReferenceMoleculeDetails':
		""""""
		return self._enter('pdbx_reference_molecule_details', PdbxReferenceMoleculeDetails)
	@property
	def pdbx_reference_molecule_family(self) -> 'PdbxReferenceMoleculeFamily':
		""""""
		return self._enter('pdbx_reference_molecule_family', PdbxReferenceMoleculeFamily)
	@property
	def pdbx_reference_molecule_features(self) -> 'PdbxReferenceMoleculeFeatures':
		""""""
		return self._enter('pdbx_reference_molecule_features', PdbxReferenceMoleculeFeatures)
	@property
	def pdbx_reference_molecule_list(self) -> 'PdbxReferenceMoleculeList':
		""""""
		return self._enter('pdbx_reference_molecule_list', PdbxReferenceMoleculeList)
	@property
	def pdbx_reference_molecule_related_structures(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		""""""
		return self._enter('pdbx_reference_molecule_related_structures', PdbxReferenceMoleculeRelatedStructures)
	@property
	def pdbx_reference_molecule_synonyms(self) -> 'PdbxReferenceMoleculeSynonyms':
		""""""
		return self._enter('pdbx_reference_molecule_synonyms', PdbxReferenceMoleculeSynonyms)
	@property
	def rcsb_bird_citation(self) -> 'RcsbBirdCitation':
		""""""
		return self._enter('rcsb_bird_citation', RcsbBirdCitation)
	@property
	def rcsb_chem_comp_annotation(self) -> 'RcsbChemCompAnnotation':
		""""""
		return self._enter('rcsb_chem_comp_annotation', RcsbChemCompAnnotation)
	@property
	def rcsb_chem_comp_container_identifiers(self) -> 'RcsbChemCompContainerIdentifiers':
		""""""
		return self._enter('rcsb_chem_comp_container_identifiers', RcsbChemCompContainerIdentifiers)
	@property
	def rcsb_chem_comp_descriptor(self) -> 'RcsbChemCompDescriptor':
		""""""
		return self._enter('rcsb_chem_comp_descriptor', RcsbChemCompDescriptor)
	@property
	def rcsb_chem_comp_info(self) -> 'RcsbChemCompInfo':
		""""""
		return self._enter('rcsb_chem_comp_info', RcsbChemCompInfo)
	@property
	def rcsb_chem_comp_related(self) -> 'RcsbChemCompRelated':
		""""""
		return self._enter('rcsb_chem_comp_related', RcsbChemCompRelated)
	@property
	def rcsb_chem_comp_synonyms(self) -> 'RcsbChemCompSynonyms':
		""""""
		return self._enter('rcsb_chem_comp_synonyms', RcsbChemCompSynonyms)
	@property
	def rcsb_chem_comp_target(self) -> 'RcsbChemCompTarget':
		""""""
		return self._enter('rcsb_chem_comp_target', RcsbChemCompTarget)
	@property
	def rcsb_id(self) -> 'CoreChemComp':
		"""A unique identifier for the chemical definition in this container.  Examples: ATP, PRD_000010 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_schema_container_identifiers(self) -> 'RcsbSchemaContainerIdentifiers':
		""""""
		return self._enter('rcsb_schema_container_identifiers', RcsbSchemaContainerIdentifiers)

class CoreDrugbank(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def drugbank_container_identifiers(self) -> 'DrugbankContainerIdentifiers':
		""""""
		return self._enter('drugbank_container_identifiers', DrugbankContainerIdentifiers)
	@property
	def drugbank_info(self) -> 'DrugbankInfo':
		""""""
		return self._enter('drugbank_info', DrugbankInfo)
	@property
	def drugbank_target(self) -> 'DrugbankTarget':
		""""""
		return self._enter('drugbank_target', DrugbankTarget)

class CoreEntityAlignmentsAlignedRegions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotAlignmentsCoreEntityAlignments':
		"""Return to parent (RcsbUniprotAlignmentsCoreEntityAlignments)"""
		return self._parent if self._parent else self
	@property
	def length(self) -> 'CoreEntityAlignmentsAlignedRegions':
		"""Aligned region length"""
		self._enter('length', Query)
		return self
	@property
	def query_begin(self) -> 'CoreEntityAlignmentsAlignedRegions':
		"""Entity seqeunce start position"""
		self._enter('query_begin', Query)
		return self
	@property
	def target_begin(self) -> 'CoreEntityAlignmentsAlignedRegions':
		"""NCBI sequence start position"""
		self._enter('target_begin', Query)
		return self

class CoreEntityAlignmentsCoreEntityIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotAlignmentsCoreEntityAlignments':
		"""Return to parent (RcsbUniprotAlignmentsCoreEntityAlignments)"""
		return self._parent if self._parent else self
	@property
	def entity_id(self) -> 'CoreEntityAlignmentsCoreEntityIdentifiers':
		""""""
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'CoreEntityAlignmentsCoreEntityIdentifiers':
		""""""
		self._enter('entry_id', Query)
		return self

class CoreEntityAlignmentsScores(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotAlignmentsCoreEntityAlignments':
		"""Return to parent (RcsbUniprotAlignmentsCoreEntityAlignments)"""
		return self._parent if self._parent else self
	@property
	def query_coverage(self) -> 'CoreEntityAlignmentsScores':
		""""""
		self._enter('query_coverage', Query)
		return self
	@property
	def query_length(self) -> 'CoreEntityAlignmentsScores':
		""""""
		self._enter('query_length', Query)
		return self
	@property
	def target_coverage(self) -> 'CoreEntityAlignmentsScores':
		""""""
		self._enter('target_coverage', Query)
		return self
	@property
	def target_length(self) -> 'CoreEntityAlignmentsScores':
		""""""
		self._enter('target_length', Query)
		return self

class CoreEntry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def assemblies(self) -> 'CoreAssembly':
		"""Get all assemblies for this entry."""
		return self._enter('assemblies', CoreAssembly)
	@property
	def audit_author(self) -> 'AuditAuthor':
		""""""
		return self._enter('audit_author', AuditAuthor)
	@property
	def branched_entities(self) -> 'CoreBranchedEntity':
		"""Get all branched entities for this entry."""
		return self._enter('branched_entities', CoreBranchedEntity)
	@property
	def cell(self) -> 'Cell':
		""""""
		return self._enter('cell', Cell)
	@property
	def citation(self) -> 'Citation':
		""""""
		return self._enter('citation', Citation)
	@property
	def database_2(self) -> 'Database2':
		""""""
		return self._enter('database_2', Database2)
	@property
	def diffrn(self) -> 'Diffrn':
		""""""
		return self._enter('diffrn', Diffrn)
	@property
	def diffrn_detector(self) -> 'DiffrnDetector':
		""""""
		return self._enter('diffrn_detector', DiffrnDetector)
	@property
	def diffrn_radiation(self) -> 'DiffrnRadiation':
		""""""
		return self._enter('diffrn_radiation', DiffrnRadiation)
	@property
	def diffrn_source(self) -> 'DiffrnSource':
		""""""
		return self._enter('diffrn_source', DiffrnSource)
	@property
	def em_2d_crystal_entity(self) -> 'Em2dCrystalEntity':
		""""""
		return self._enter('em_2d_crystal_entity', Em2dCrystalEntity)
	@property
	def em_3d_crystal_entity(self) -> 'Em3dCrystalEntity':
		""""""
		return self._enter('em_3d_crystal_entity', Em3dCrystalEntity)
	@property
	def em_3d_fitting(self) -> 'Em3dFitting':
		""""""
		return self._enter('em_3d_fitting', Em3dFitting)
	@property
	def em_3d_fitting_list(self) -> 'Em3dFittingList':
		""""""
		return self._enter('em_3d_fitting_list', Em3dFittingList)
	@property
	def em_3d_reconstruction(self) -> 'Em3dReconstruction':
		""""""
		return self._enter('em_3d_reconstruction', Em3dReconstruction)
	@property
	def em_ctf_correction(self) -> 'EmCtfCorrection':
		""""""
		return self._enter('em_ctf_correction', EmCtfCorrection)
	@property
	def em_diffraction(self) -> 'EmDiffraction':
		""""""
		return self._enter('em_diffraction', EmDiffraction)
	@property
	def em_diffraction_shell(self) -> 'EmDiffractionShell':
		""""""
		return self._enter('em_diffraction_shell', EmDiffractionShell)
	@property
	def em_diffraction_stats(self) -> 'EmDiffractionStats':
		""""""
		return self._enter('em_diffraction_stats', EmDiffractionStats)
	@property
	def em_embedding(self) -> 'EmEmbedding':
		""""""
		return self._enter('em_embedding', EmEmbedding)
	@property
	def em_entity_assembly(self) -> 'EmEntityAssembly':
		""""""
		return self._enter('em_entity_assembly', EmEntityAssembly)
	@property
	def em_experiment(self) -> 'EmExperiment':
		""""""
		return self._enter('em_experiment', EmExperiment)
	@property
	def em_helical_entity(self) -> 'EmHelicalEntity':
		""""""
		return self._enter('em_helical_entity', EmHelicalEntity)
	@property
	def em_image_recording(self) -> 'EmImageRecording':
		""""""
		return self._enter('em_image_recording', EmImageRecording)
	@property
	def em_imaging(self) -> 'EmImaging':
		""""""
		return self._enter('em_imaging', EmImaging)
	@property
	def em_particle_selection(self) -> 'EmParticleSelection':
		""""""
		return self._enter('em_particle_selection', EmParticleSelection)
	@property
	def em_single_particle_entity(self) -> 'EmSingleParticleEntity':
		""""""
		return self._enter('em_single_particle_entity', EmSingleParticleEntity)
	@property
	def em_software(self) -> 'EmSoftware':
		""""""
		return self._enter('em_software', EmSoftware)
	@property
	def em_specimen(self) -> 'EmSpecimen':
		""""""
		return self._enter('em_specimen', EmSpecimen)
	@property
	def em_staining(self) -> 'EmStaining':
		""""""
		return self._enter('em_staining', EmStaining)
	@property
	def em_vitrification(self) -> 'EmVitrification':
		""""""
		return self._enter('em_vitrification', EmVitrification)
	@property
	def entry(self) -> 'Entry':
		""""""
		return self._enter('entry', Entry)
	@property
	def entry_groups(self) -> 'GroupEntry':
		"""Get all groups for this entry."""
		return self._enter('entry_groups', GroupEntry)
	@property
	def exptl(self) -> 'Exptl':
		""""""
		return self._enter('exptl', Exptl)
	@property
	def exptl_crystal(self) -> 'ExptlCrystal':
		""""""
		return self._enter('exptl_crystal', ExptlCrystal)
	@property
	def exptl_crystal_grow(self) -> 'ExptlCrystalGrow':
		""""""
		return self._enter('exptl_crystal_grow', ExptlCrystalGrow)
	@property
	def ihm_entry_collection_mapping(self) -> 'IhmEntryCollectionMapping':
		""""""
		return self._enter('ihm_entry_collection_mapping', IhmEntryCollectionMapping)
	@property
	def ihm_external_reference_info(self) -> 'IhmExternalReferenceInfo':
		""""""
		return self._enter('ihm_external_reference_info', IhmExternalReferenceInfo)
	@property
	def ma_data(self) -> 'MaData':
		""""""
		return self._enter('ma_data', MaData)
	@property
	def nonpolymer_entities(self) -> 'CoreNonpolymerEntity':
		"""Get all non-polymer (non-solvent) entities for this entry."""
		return self._enter('nonpolymer_entities', CoreNonpolymerEntity)
	@property
	def pdbx_SG_project(self) -> 'PdbxSGProject':
		""""""
		return self._enter('pdbx_SG_project', PdbxSGProject)
	@property
	def pdbx_audit_revision_category(self) -> 'PdbxAuditRevisionCategory':
		""""""
		return self._enter('pdbx_audit_revision_category', PdbxAuditRevisionCategory)
	@property
	def pdbx_audit_revision_details(self) -> 'PdbxAuditRevisionDetails':
		""""""
		return self._enter('pdbx_audit_revision_details', PdbxAuditRevisionDetails)
	@property
	def pdbx_audit_revision_group(self) -> 'PdbxAuditRevisionGroup':
		""""""
		return self._enter('pdbx_audit_revision_group', PdbxAuditRevisionGroup)
	@property
	def pdbx_audit_revision_history(self) -> 'PdbxAuditRevisionHistory':
		""""""
		return self._enter('pdbx_audit_revision_history', PdbxAuditRevisionHistory)
	@property
	def pdbx_audit_revision_item(self) -> 'PdbxAuditRevisionItem':
		""""""
		return self._enter('pdbx_audit_revision_item', PdbxAuditRevisionItem)
	@property
	def pdbx_audit_support(self) -> 'PdbxAuditSupport':
		""""""
		return self._enter('pdbx_audit_support', PdbxAuditSupport)
	@property
	def pdbx_database_PDB_obs_spr(self) -> 'PdbxDatabasePDBObsSpr':
		""""""
		return self._enter('pdbx_database_PDB_obs_spr', PdbxDatabasePDBObsSpr)
	@property
	def pdbx_database_related(self) -> 'PdbxDatabaseRelated':
		""""""
		return self._enter('pdbx_database_related', PdbxDatabaseRelated)
	@property
	def pdbx_database_status(self) -> 'PdbxDatabaseStatus':
		""""""
		return self._enter('pdbx_database_status', PdbxDatabaseStatus)
	@property
	def pdbx_deposit_group(self) -> 'PdbxDepositGroup':
		""""""
		return self._enter('pdbx_deposit_group', PdbxDepositGroup)
	@property
	def pdbx_initial_refinement_model(self) -> 'PdbxInitialRefinementModel':
		""""""
		return self._enter('pdbx_initial_refinement_model', PdbxInitialRefinementModel)
	@property
	def pdbx_molecule_features(self) -> 'PdbxMoleculeFeatures':
		""""""
		return self._enter('pdbx_molecule_features', PdbxMoleculeFeatures)
	@property
	def pdbx_nmr_details(self) -> 'PdbxNmrDetails':
		""""""
		return self._enter('pdbx_nmr_details', PdbxNmrDetails)
	@property
	def pdbx_nmr_ensemble(self) -> 'PdbxNmrEnsemble':
		""""""
		return self._enter('pdbx_nmr_ensemble', PdbxNmrEnsemble)
	@property
	def pdbx_nmr_exptl(self) -> 'PdbxNmrExptl':
		""""""
		return self._enter('pdbx_nmr_exptl', PdbxNmrExptl)
	@property
	def pdbx_nmr_exptl_sample_conditions(self) -> 'PdbxNmrExptlSampleConditions':
		""""""
		return self._enter('pdbx_nmr_exptl_sample_conditions', PdbxNmrExptlSampleConditions)
	@property
	def pdbx_nmr_refine(self) -> 'PdbxNmrRefine':
		""""""
		return self._enter('pdbx_nmr_refine', PdbxNmrRefine)
	@property
	def pdbx_nmr_representative(self) -> 'PdbxNmrRepresentative':
		""""""
		return self._enter('pdbx_nmr_representative', PdbxNmrRepresentative)
	@property
	def pdbx_nmr_sample_details(self) -> 'PdbxNmrSampleDetails':
		""""""
		return self._enter('pdbx_nmr_sample_details', PdbxNmrSampleDetails)
	@property
	def pdbx_nmr_software(self) -> 'PdbxNmrSoftware':
		""""""
		return self._enter('pdbx_nmr_software', PdbxNmrSoftware)
	@property
	def pdbx_nmr_spectrometer(self) -> 'PdbxNmrSpectrometer':
		""""""
		return self._enter('pdbx_nmr_spectrometer', PdbxNmrSpectrometer)
	@property
	def pdbx_reflns_twin(self) -> 'PdbxReflnsTwin':
		""""""
		return self._enter('pdbx_reflns_twin', PdbxReflnsTwin)
	@property
	def pdbx_related_exp_data_set(self) -> 'PdbxRelatedExpDataSet':
		""""""
		return self._enter('pdbx_related_exp_data_set', PdbxRelatedExpDataSet)
	@property
	def pdbx_serial_crystallography_data_reduction(self) -> 'PdbxSerialCrystallographyDataReduction':
		""""""
		return self._enter('pdbx_serial_crystallography_data_reduction', PdbxSerialCrystallographyDataReduction)
	@property
	def pdbx_serial_crystallography_measurement(self) -> 'PdbxSerialCrystallographyMeasurement':
		""""""
		return self._enter('pdbx_serial_crystallography_measurement', PdbxSerialCrystallographyMeasurement)
	@property
	def pdbx_serial_crystallography_sample_delivery(self) -> 'PdbxSerialCrystallographySampleDelivery':
		""""""
		return self._enter('pdbx_serial_crystallography_sample_delivery', PdbxSerialCrystallographySampleDelivery)
	@property
	def pdbx_serial_crystallography_sample_delivery_fixed_target(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		""""""
		return self._enter('pdbx_serial_crystallography_sample_delivery_fixed_target', PdbxSerialCrystallographySampleDeliveryFixedTarget)
	@property
	def pdbx_serial_crystallography_sample_delivery_injection(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		""""""
		return self._enter('pdbx_serial_crystallography_sample_delivery_injection', PdbxSerialCrystallographySampleDeliveryInjection)
	@property
	def pdbx_soln_scatter(self) -> 'PdbxSolnScatter':
		""""""
		return self._enter('pdbx_soln_scatter', PdbxSolnScatter)
	@property
	def pdbx_soln_scatter_model(self) -> 'PdbxSolnScatterModel':
		""""""
		return self._enter('pdbx_soln_scatter_model', PdbxSolnScatterModel)
	@property
	def pdbx_vrpt_summary(self) -> 'PdbxVrptSummary':
		""""""
		return self._enter('pdbx_vrpt_summary', PdbxVrptSummary)
	@property
	def pdbx_vrpt_summary_diffraction(self) -> 'PdbxVrptSummaryDiffraction':
		""""""
		return self._enter('pdbx_vrpt_summary_diffraction', PdbxVrptSummaryDiffraction)
	@property
	def pdbx_vrpt_summary_em(self) -> 'PdbxVrptSummaryEm':
		""""""
		return self._enter('pdbx_vrpt_summary_em', PdbxVrptSummaryEm)
	@property
	def pdbx_vrpt_summary_geometry(self) -> 'PdbxVrptSummaryGeometry':
		""""""
		return self._enter('pdbx_vrpt_summary_geometry', PdbxVrptSummaryGeometry)
	@property
	def pdbx_vrpt_summary_nmr(self) -> 'PdbxVrptSummaryNmr':
		""""""
		return self._enter('pdbx_vrpt_summary_nmr', PdbxVrptSummaryNmr)
	@property
	def polymer_entities(self) -> 'CorePolymerEntity':
		"""Get all polymer entities for this entry."""
		return self._enter('polymer_entities', CorePolymerEntity)
	@property
	def pubmed(self) -> 'CorePubmed':
		"""Get literature information from PubMed database."""
		return self._enter('pubmed', CorePubmed)
	@property
	def rcsb_accession_info(self) -> 'RcsbAccessionInfo':
		""""""
		return self._enter('rcsb_accession_info', RcsbAccessionInfo)
	@property
	def rcsb_associated_holdings(self) -> 'CurrentEntry':
		"""The list of content types associated with this entry."""
		return self._enter('rcsb_associated_holdings', CurrentEntry)
	@property
	def rcsb_binding_affinity(self) -> 'RcsbBindingAffinity':
		""""""
		return self._enter('rcsb_binding_affinity', RcsbBindingAffinity)
	@property
	def rcsb_comp_model_provenance(self) -> 'RcsbCompModelProvenance':
		""""""
		return self._enter('rcsb_comp_model_provenance', RcsbCompModelProvenance)
	@property
	def rcsb_entry_container_identifiers(self) -> 'RcsbEntryContainerIdentifiers':
		""""""
		return self._enter('rcsb_entry_container_identifiers', RcsbEntryContainerIdentifiers)
	@property
	def rcsb_entry_group_membership(self) -> 'RcsbEntryGroupMembership':
		""""""
		return self._enter('rcsb_entry_group_membership', RcsbEntryGroupMembership)
	@property
	def rcsb_entry_info(self) -> 'RcsbEntryInfo':
		""""""
		return self._enter('rcsb_entry_info', RcsbEntryInfo)
	@property
	def rcsb_external_references(self) -> 'RcsbExternalReferences':
		""""""
		return self._enter('rcsb_external_references', RcsbExternalReferences)
	@property
	def rcsb_id(self) -> 'CoreEntry':
		"""A unique identifier for each object in this entry container.  Examples: 1KIP """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_ihm_dataset_list(self) -> 'RcsbIhmDatasetList':
		""""""
		return self._enter('rcsb_ihm_dataset_list', RcsbIhmDatasetList)
	@property
	def rcsb_ihm_dataset_source_db_reference(self) -> 'RcsbIhmDatasetSourceDbReference':
		""""""
		return self._enter('rcsb_ihm_dataset_source_db_reference', RcsbIhmDatasetSourceDbReference)
	@property
	def rcsb_ma_qa_metric_global(self) -> 'RcsbMaQaMetricGlobal':
		""""""
		return self._enter('rcsb_ma_qa_metric_global', RcsbMaQaMetricGlobal)
	@property
	def rcsb_primary_citation(self) -> 'RcsbPrimaryCitation':
		""""""
		return self._enter('rcsb_primary_citation', RcsbPrimaryCitation)
	@property
	def refine(self) -> 'Refine':
		""""""
		return self._enter('refine', Refine)
	@property
	def refine_analyze(self) -> 'RefineAnalyze':
		""""""
		return self._enter('refine_analyze', RefineAnalyze)
	@property
	def refine_hist(self) -> 'RefineHist':
		""""""
		return self._enter('refine_hist', RefineHist)
	@property
	def refine_ls_restr(self) -> 'RefineLsRestr':
		""""""
		return self._enter('refine_ls_restr', RefineLsRestr)
	@property
	def reflns(self) -> 'Reflns':
		""""""
		return self._enter('reflns', Reflns)
	@property
	def reflns_shell(self) -> 'ReflnsShell':
		""""""
		return self._enter('reflns_shell', ReflnsShell)
	@property
	def software(self) -> 'Software':
		""""""
		return self._enter('software', Software)
	@property
	def struct(self) -> 'Struct':
		""""""
		return self._enter('struct', Struct)
	@property
	def struct_keywords(self) -> 'StructKeywords':
		""""""
		return self._enter('struct_keywords', StructKeywords)
	@property
	def symmetry(self) -> 'Symmetry':
		""""""
		return self._enter('symmetry', Symmetry)

class CoreInterface(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def rcsb_id(self) -> 'CoreInterface':
		""""""
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_interface_container_identifiers(self) -> 'RcsbInterfaceContainerIdentifiers':
		""""""
		return self._enter('rcsb_interface_container_identifiers', RcsbInterfaceContainerIdentifiers)
	@property
	def rcsb_interface_info(self) -> 'RcsbInterfaceInfo':
		""""""
		return self._enter('rcsb_interface_info', RcsbInterfaceInfo)
	@property
	def rcsb_interface_operator(self) -> 'CoreInterface':
		"""List of operations for each interface partner."""
		self._enter('rcsb_interface_operator', Query)
		return self
	@property
	def rcsb_interface_partner(self) -> 'RcsbInterfacePartner':
		""""""
		return self._enter('rcsb_interface_partner', RcsbInterfacePartner)
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)

class CoreNonpolymerEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def entry(self) -> 'CoreEntry':
		"""Get entry that contains this non-polymer entity."""
		return self._enter('entry', CoreEntry)
	@property
	def nonpolymer_comp(self) -> 'CoreChemComp':
		"""Get a non-polymer chemical components described in this molecular entity."""
		return self._enter('nonpolymer_comp', CoreChemComp)
	@property
	def nonpolymer_entity_instances(self) -> 'CoreNonpolymerEntityInstance':
		"""Get all unique non-polymer instances (chains) for this non-polymer entity."""
		return self._enter('nonpolymer_entity_instances', CoreNonpolymerEntityInstance)
	@property
	def pdbx_entity_nonpoly(self) -> 'PdbxEntityNonpoly':
		""""""
		return self._enter('pdbx_entity_nonpoly', PdbxEntityNonpoly)
	@property
	def prd(self) -> 'CoreChemComp':
		"""Get a BIRD chemical components described in this molecular entity."""
		return self._enter('prd', CoreChemComp)
	@property
	def rcsb_id(self) -> 'CoreNonpolymerEntity':
		"""A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers.  Examples: 6EL3_1 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)
	@property
	def rcsb_nonpolymer_entity(self) -> 'RcsbNonpolymerEntity':
		""""""
		return self._enter('rcsb_nonpolymer_entity', RcsbNonpolymerEntity)
	@property
	def rcsb_nonpolymer_entity_annotation(self) -> 'RcsbNonpolymerEntityAnnotation':
		""""""
		return self._enter('rcsb_nonpolymer_entity_annotation', RcsbNonpolymerEntityAnnotation)
	@property
	def rcsb_nonpolymer_entity_container_identifiers(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		""""""
		return self._enter('rcsb_nonpolymer_entity_container_identifiers', RcsbNonpolymerEntityContainerIdentifiers)
	@property
	def rcsb_nonpolymer_entity_feature(self) -> 'RcsbNonpolymerEntityFeature':
		""""""
		return self._enter('rcsb_nonpolymer_entity_feature', RcsbNonpolymerEntityFeature)
	@property
	def rcsb_nonpolymer_entity_feature_summary(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		""""""
		return self._enter('rcsb_nonpolymer_entity_feature_summary', RcsbNonpolymerEntityFeatureSummary)
	@property
	def rcsb_nonpolymer_entity_keywords(self) -> 'RcsbNonpolymerEntityKeywords':
		""""""
		return self._enter('rcsb_nonpolymer_entity_keywords', RcsbNonpolymerEntityKeywords)
	@property
	def rcsb_nonpolymer_entity_name_com(self) -> 'RcsbNonpolymerEntityNameCom':
		""""""
		return self._enter('rcsb_nonpolymer_entity_name_com', RcsbNonpolymerEntityNameCom)

class CoreNonpolymerEntityInstance(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def nonpolymer_entity(self) -> 'CoreNonpolymerEntity':
		"""Get non-polymer entity for this non-polymer entity instance."""
		return self._enter('nonpolymer_entity', CoreNonpolymerEntity)
	@property
	def pdbx_struct_special_symmetry(self) -> 'PdbxStructSpecialSymmetry':
		""""""
		return self._enter('pdbx_struct_special_symmetry', PdbxStructSpecialSymmetry)
	@property
	def pdbx_vrpt_summary_entity_fit_to_map(self) -> 'PdbxVrptSummaryEntityFitToMap':
		""""""
		return self._enter('pdbx_vrpt_summary_entity_fit_to_map', PdbxVrptSummaryEntityFitToMap)
	@property
	def pdbx_vrpt_summary_entity_geometry(self) -> 'PdbxVrptSummaryEntityGeometry':
		""""""
		return self._enter('pdbx_vrpt_summary_entity_geometry', PdbxVrptSummaryEntityGeometry)
	@property
	def rcsb_id(self) -> 'CoreNonpolymerEntityInstance':
		"""A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers.  Examples: 1KIP.A """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)
	@property
	def rcsb_nonpolymer_entity_instance_container_identifiers(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		""""""
		return self._enter('rcsb_nonpolymer_entity_instance_container_identifiers', RcsbNonpolymerEntityInstanceContainerIdentifiers)
	@property
	def rcsb_nonpolymer_instance_annotation(self) -> 'RcsbNonpolymerInstanceAnnotation':
		""""""
		return self._enter('rcsb_nonpolymer_instance_annotation', RcsbNonpolymerInstanceAnnotation)
	@property
	def rcsb_nonpolymer_instance_feature(self) -> 'RcsbNonpolymerInstanceFeature':
		""""""
		return self._enter('rcsb_nonpolymer_instance_feature', RcsbNonpolymerInstanceFeature)
	@property
	def rcsb_nonpolymer_instance_feature_summary(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		""""""
		return self._enter('rcsb_nonpolymer_instance_feature_summary', RcsbNonpolymerInstanceFeatureSummary)
	@property
	def rcsb_nonpolymer_instance_validation_score(self) -> 'RcsbNonpolymerInstanceValidationScore':
		""""""
		return self._enter('rcsb_nonpolymer_instance_validation_score', RcsbNonpolymerInstanceValidationScore)
	@property
	def rcsb_nonpolymer_struct_conn(self) -> 'RcsbNonpolymerStructConn':
		""""""
		return self._enter('rcsb_nonpolymer_struct_conn', RcsbNonpolymerStructConn)
	@property
	def rcsb_target_neighbors(self) -> 'RcsbTargetNeighbors':
		""""""
		return self._enter('rcsb_target_neighbors', RcsbTargetNeighbors)
	@property
	def struct_asym(self) -> 'StructAsym':
		""""""
		return self._enter('struct_asym', StructAsym)

class CorePfam(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def rcsb_id(self) -> 'CorePfam':
		"""Accession number of Pfam entry."""
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_pfam_accession(self) -> 'CorePfam':
		"""The unique accession code of protein families and domains in the Pfam database.  Examples: PF00621, PF00637, PF00656 """
		self._enter('rcsb_pfam_accession', Query)
		return self
	@property
	def rcsb_pfam_clan_id(self) -> 'CorePfam':
		"""Details of the Pfam clan to which the entity belongs."""
		self._enter('rcsb_pfam_clan_id', Query)
		return self
	@property
	def rcsb_pfam_comment(self) -> 'CorePfam':
		"""Textual description of the family."""
		self._enter('rcsb_pfam_comment', Query)
		return self
	@property
	def rcsb_pfam_container_identifiers(self) -> 'RcsbPfamContainerIdentifiers':
		""""""
		return self._enter('rcsb_pfam_container_identifiers', RcsbPfamContainerIdentifiers)
	@property
	def rcsb_pfam_description(self) -> 'CorePfam':
		"""A human-readable name of protein families and domains.  Examples: Lectin like domain, Cell division control protein 24, OB domain 2, Protein of unknown function (DUF722) """
		self._enter('rcsb_pfam_description', Query)
		return self
	@property
	def rcsb_pfam_identifier(self) -> 'CorePfam':
		"""The unique identifier of protein families and domains in the Pfam database.  Examples: RhoGEF, Clathrin, Peptidase_C14 """
		self._enter('rcsb_pfam_identifier', Query)
		return self
	@property
	def rcsb_pfam_provenance_code(self) -> 'CorePfam':
		"""Pfam-A is the manually curated portion of the Pfam database.  Allowable values: Pfam-A """
		self._enter('rcsb_pfam_provenance_code', Query)
		return self
	@property
	def rcsb_pfam_seed_source(self) -> 'CorePfam':
		"""Pfam entries are classified into six different categories, depending on the length and nature of the sequence regions included in the entry: family, domain, repeats, motifs, coiled-coil, and disordered.  Allowable values: Family, Domain, Repeat, Motif, Disordered, Coiled-coil """
		self._enter('rcsb_pfam_seed_source', Query)
		return self

class CorePolymerEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def chem_comp_monomers(self) -> 'CoreChemComp':
		"""Get all unique monomers described in this molecular entity."""
		return self._enter('chem_comp_monomers', CoreChemComp)
	@property
	def chem_comp_nstd_monomers(self) -> 'CoreChemComp':
		"""Get all unique non-standard monomers described in this molecular entity."""
		return self._enter('chem_comp_nstd_monomers', CoreChemComp)
	@property
	def entity_poly(self) -> 'EntityPoly':
		""""""
		return self._enter('entity_poly', EntityPoly)
	@property
	def entity_src_gen(self) -> 'EntitySrcGen':
		""""""
		return self._enter('entity_src_gen', EntitySrcGen)
	@property
	def entity_src_nat(self) -> 'EntitySrcNat':
		""""""
		return self._enter('entity_src_nat', EntitySrcNat)
	@property
	def entry(self) -> 'CoreEntry':
		"""Get entry that contains this molecular entity."""
		return self._enter('entry', CoreEntry)
	@property
	def pdbx_entity_src_syn(self) -> 'PdbxEntitySrcSyn':
		""""""
		return self._enter('pdbx_entity_src_syn', PdbxEntitySrcSyn)
	@property
	def pfams(self) -> 'CorePfam':
		"""Get all unique Pfam annotations associated with this molecular entity."""
		return self._enter('pfams', CorePfam)
	@property
	def polymer_entity_groups(self) -> 'GroupPolymerEntity':
		"""Get all groups for this entity."""
		return self._enter('polymer_entity_groups', GroupPolymerEntity)
	@property
	def polymer_entity_instances(self) -> 'CorePolymerEntityInstance':
		"""Get all unique polymer instances (chains) for this molecular entity."""
		return self._enter('polymer_entity_instances', CorePolymerEntityInstance)
	@property
	def prd(self) -> 'CoreChemComp':
		"""Get a BIRD chemical components described in this molecular entity."""
		return self._enter('prd', CoreChemComp)
	@property
	def rcsb_cluster_flexibility(self) -> 'RcsbClusterFlexibility':
		""""""
		return self._enter('rcsb_cluster_flexibility', RcsbClusterFlexibility)
	@property
	def rcsb_cluster_membership(self) -> 'RcsbClusterMembership':
		""""""
		return self._enter('rcsb_cluster_membership', RcsbClusterMembership)
	@property
	def rcsb_entity_host_organism(self) -> 'RcsbEntityHostOrganism':
		""""""
		return self._enter('rcsb_entity_host_organism', RcsbEntityHostOrganism)
	@property
	def rcsb_entity_source_organism(self) -> 'RcsbEntitySourceOrganism':
		""""""
		return self._enter('rcsb_entity_source_organism', RcsbEntitySourceOrganism)
	@property
	def rcsb_genomic_lineage(self) -> 'RcsbGenomicLineage':
		""""""
		return self._enter('rcsb_genomic_lineage', RcsbGenomicLineage)
	@property
	def rcsb_id(self) -> 'CorePolymerEntity':
		"""A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers.  Examples: 6EL3_1 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)
	@property
	def rcsb_membrane_lineage(self) -> 'RcsbMembraneLineage':
		""""""
		return self._enter('rcsb_membrane_lineage', RcsbMembraneLineage)
	@property
	def rcsb_membrane_lineage_provenance_code(self) -> 'CorePolymerEntity':
		"""Mpstruc keyword denotes original annotation, Homology keyword denotes annotation inferred by homology.  Allowable values: Homology, Mpstruc """
		self._enter('rcsb_membrane_lineage_provenance_code', Query)
		return self
	@property
	def rcsb_polymer_entity(self) -> 'RcsbPolymerEntity':
		""""""
		return self._enter('rcsb_polymer_entity', RcsbPolymerEntity)
	@property
	def rcsb_polymer_entity_align(self) -> 'RcsbPolymerEntityAlign':
		""""""
		return self._enter('rcsb_polymer_entity_align', RcsbPolymerEntityAlign)
	@property
	def rcsb_polymer_entity_annotation(self) -> 'RcsbPolymerEntityAnnotation':
		""""""
		return self._enter('rcsb_polymer_entity_annotation', RcsbPolymerEntityAnnotation)
	@property
	def rcsb_polymer_entity_container_identifiers(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		""""""
		return self._enter('rcsb_polymer_entity_container_identifiers', RcsbPolymerEntityContainerIdentifiers)
	@property
	def rcsb_polymer_entity_feature(self) -> 'RcsbPolymerEntityFeature':
		""""""
		return self._enter('rcsb_polymer_entity_feature', RcsbPolymerEntityFeature)
	@property
	def rcsb_polymer_entity_feature_summary(self) -> 'RcsbPolymerEntityFeatureSummary':
		""""""
		return self._enter('rcsb_polymer_entity_feature_summary', RcsbPolymerEntityFeatureSummary)
	@property
	def rcsb_polymer_entity_group_membership(self) -> 'RcsbPolymerEntityGroupMembership':
		""""""
		return self._enter('rcsb_polymer_entity_group_membership', RcsbPolymerEntityGroupMembership)
	@property
	def rcsb_polymer_entity_keywords(self) -> 'RcsbPolymerEntityKeywords':
		""""""
		return self._enter('rcsb_polymer_entity_keywords', RcsbPolymerEntityKeywords)
	@property
	def rcsb_polymer_entity_name_com(self) -> 'RcsbPolymerEntityNameCom':
		""""""
		return self._enter('rcsb_polymer_entity_name_com', RcsbPolymerEntityNameCom)
	@property
	def rcsb_polymer_entity_name_sys(self) -> 'RcsbPolymerEntityNameSys':
		""""""
		return self._enter('rcsb_polymer_entity_name_sys', RcsbPolymerEntityNameSys)
	@property
	def rcsb_related_target_references(self) -> 'RcsbRelatedTargetReferences':
		""""""
		return self._enter('rcsb_related_target_references', RcsbRelatedTargetReferences)
	@property
	def rcsb_target_cofactors(self) -> 'RcsbTargetCofactors':
		""""""
		return self._enter('rcsb_target_cofactors', RcsbTargetCofactors)
	@property
	def uniprots(self) -> 'CoreUniprot':
		"""Get all unique UniProt KB annotations associated with this molecular entity."""
		return self._enter('uniprots', CoreUniprot)

class CorePolymerEntityInstance(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def pdbx_struct_special_symmetry(self) -> 'PdbxStructSpecialSymmetry':
		""""""
		return self._enter('pdbx_struct_special_symmetry', PdbxStructSpecialSymmetry)
	@property
	def pdbx_vrpt_summary_entity_fit_to_map(self) -> 'PdbxVrptSummaryEntityFitToMap':
		""""""
		return self._enter('pdbx_vrpt_summary_entity_fit_to_map', PdbxVrptSummaryEntityFitToMap)
	@property
	def pdbx_vrpt_summary_entity_geometry(self) -> 'PdbxVrptSummaryEntityGeometry':
		""""""
		return self._enter('pdbx_vrpt_summary_entity_geometry', PdbxVrptSummaryEntityGeometry)
	@property
	def polymer_entity(self) -> 'CorePolymerEntity':
		"""Get polymer entity for this polymer entity instance."""
		return self._enter('polymer_entity', CorePolymerEntity)
	@property
	def rcsb_id(self) -> 'CorePolymerEntityInstance':
		"""A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers.  Examples: 1KIP.A """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_latest_revision(self) -> 'RcsbLatestRevision':
		""""""
		return self._enter('rcsb_latest_revision', RcsbLatestRevision)
	@property
	def rcsb_ligand_neighbors(self) -> 'RcsbLigandNeighbors':
		""""""
		return self._enter('rcsb_ligand_neighbors', RcsbLigandNeighbors)
	@property
	def rcsb_polymer_entity_instance_container_identifiers(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		""""""
		return self._enter('rcsb_polymer_entity_instance_container_identifiers', RcsbPolymerEntityInstanceContainerIdentifiers)
	@property
	def rcsb_polymer_instance_annotation(self) -> 'RcsbPolymerInstanceAnnotation':
		""""""
		return self._enter('rcsb_polymer_instance_annotation', RcsbPolymerInstanceAnnotation)
	@property
	def rcsb_polymer_instance_feature(self) -> 'RcsbPolymerInstanceFeature':
		""""""
		return self._enter('rcsb_polymer_instance_feature', RcsbPolymerInstanceFeature)
	@property
	def rcsb_polymer_instance_feature_summary(self) -> 'RcsbPolymerInstanceFeatureSummary':
		""""""
		return self._enter('rcsb_polymer_instance_feature_summary', RcsbPolymerInstanceFeatureSummary)
	@property
	def rcsb_polymer_instance_info(self) -> 'RcsbPolymerInstanceInfo':
		""""""
		return self._enter('rcsb_polymer_instance_info', RcsbPolymerInstanceInfo)
	@property
	def rcsb_polymer_struct_conn(self) -> 'RcsbPolymerStructConn':
		""""""
		return self._enter('rcsb_polymer_struct_conn', RcsbPolymerStructConn)
	@property
	def struct_asym(self) -> 'StructAsym':
		""""""
		return self._enter('struct_asym', StructAsym)

class CorePubmed(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def rcsb_id(self) -> 'CorePubmed':
		"""Unique integer value assigned to each PubMed record."""
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_pubmed_abstract_text(self) -> 'CorePubmed':
		"""A concise, accurate and factual mini-version of the paper contents."""
		self._enter('rcsb_pubmed_abstract_text', Query)
		return self
	@property
	def rcsb_pubmed_affiliation_info(self) -> 'CorePubmed':
		"""The institution(s) that the author is affiliated with. Multiple affiliations per author are allowed."""
		self._enter('rcsb_pubmed_affiliation_info', Query)
		return self
	@property
	def rcsb_pubmed_central_id(self) -> 'CorePubmed':
		"""Unique integer value assigned to each PubMed Central record."""
		self._enter('rcsb_pubmed_central_id', Query)
		return self
	@property
	def rcsb_pubmed_container_identifiers(self) -> 'RcsbPubmedContainerIdentifiers':
		""""""
		return self._enter('rcsb_pubmed_container_identifiers', RcsbPubmedContainerIdentifiers)
	@property
	def rcsb_pubmed_doi(self) -> 'CorePubmed':
		"""Persistent identifier used to provide a link to an article location on the Internet."""
		self._enter('rcsb_pubmed_doi', Query)
		return self
	@property
	def rcsb_pubmed_mesh_descriptors(self) -> 'CorePubmed':
		"""NLM controlled vocabulary, Medical Subject Headings (MeSH), is used to characterize the content of the articles represented by MEDLINE citations."""
		self._enter('rcsb_pubmed_mesh_descriptors', Query)
		return self
	@property
	def rcsb_pubmed_mesh_descriptors_lineage(self) -> 'RcsbPubmedMeshDescriptorsLineage':
		"""Members of the MeSH classification lineage."""
		return self._enter('rcsb_pubmed_mesh_descriptors_lineage', RcsbPubmedMeshDescriptorsLineage)

class CoreUniprot(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def rcsb_id(self) -> 'CoreUniprot':
		"""Primary accession number of a given UniProtKB entry."""
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_uniprot_accession(self) -> 'CoreUniprot':
		"""List of UniProtKB accession numbers where original accession numbers are retained as ‘secondary’ accession numbers."""
		self._enter('rcsb_uniprot_accession', Query)
		return self
	@property
	def rcsb_uniprot_alignments(self) -> 'RcsbUniprotAlignments':
		"""UniProt pairwise sequence alignments."""
		return self._enter('rcsb_uniprot_alignments', RcsbUniprotAlignments)
	@property
	def rcsb_uniprot_annotation(self) -> 'RcsbUniprotAnnotation':
		""""""
		return self._enter('rcsb_uniprot_annotation', RcsbUniprotAnnotation)
	@property
	def rcsb_uniprot_container_identifiers(self) -> 'RcsbUniprotContainerIdentifiers':
		""""""
		return self._enter('rcsb_uniprot_container_identifiers', RcsbUniprotContainerIdentifiers)
	@property
	def rcsb_uniprot_entry_name(self) -> 'CoreUniprot':
		"""A list of unique identifiers (former IDs), often containing biologically relevant information."""
		self._enter('rcsb_uniprot_entry_name', Query)
		return self
	@property
	def rcsb_uniprot_external_reference(self) -> 'RcsbUniprotExternalReference':
		""""""
		return self._enter('rcsb_uniprot_external_reference', RcsbUniprotExternalReference)
	@property
	def rcsb_uniprot_feature(self) -> 'RcsbUniprotFeature':
		""""""
		return self._enter('rcsb_uniprot_feature', RcsbUniprotFeature)
	@property
	def rcsb_uniprot_keyword(self) -> 'RcsbUniprotKeyword':
		"""Keywords constitute a controlled vocabulary that summarises the content of a UniProtKB entry."""
		return self._enter('rcsb_uniprot_keyword', RcsbUniprotKeyword)
	@property
	def rcsb_uniprot_protein(self) -> 'RcsbUniprotProtein':
		""""""
		return self._enter('rcsb_uniprot_protein', RcsbUniprotProtein)

class CurrentEntry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def rcsb_id(self) -> 'CurrentEntry':
		"""The RCSB entry identifier.  Examples: 1KIP """
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_repository_holdings_current(self) -> 'RcsbRepositoryHoldingsCurrent':
		""""""
		return self._enter('rcsb_repository_holdings_current', RcsbRepositoryHoldingsCurrent)
	@property
	def rcsb_repository_holdings_current_entry_container_identifiers(self) -> 'RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers':
		""""""
		return self._enter('rcsb_repository_holdings_current_entry_container_identifiers', RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers)

class Database2(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def database_code(self) -> 'Database2':
		"""The code assigned by the database identified in  _database_2.database_id.  Examples: 4HHB, 3LTQ """
		self._enter('database_code', Query)
		return self
	@property
	def database_id(self) -> 'Database2':
		"""An abbreviation that identifies the database.  Allowable values: AlphaFoldDB, BMRB, EBI, EMDB, MODBASE, ModelArchive, NDB, PDB, PDB-Dev, PDBE, PDB_ACC, RCSB, SWISS-MODEL_REPOSITORY, WWPDB """
		self._enter('database_id', Query)
		return self
	@property
	def pdbx_DOI(self) -> 'Database2':
		"""Document Object Identifier (DOI) for this entry registered with http://crossref.org.  Examples: 10.2210/pdb6lu7/pdb """
		self._enter('pdbx_DOI', Query)
		return self
	@property
	def pdbx_database_accession(self) -> 'Database2':
		"""Extended accession code issued for for _database_2.database_code assigned by the database identified in  _database_2.database_id.  Examples: pdb_00006lu7 """
		self._enter('pdbx_database_accession', Query)
		return self

class Diffrn(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def ambient_pressure(self) -> 'Diffrn':
		"""The mean hydrostatic pressure in kilopascals at which the  intensities were measured."""
		self._enter('ambient_pressure', Query)
		return self
	@property
	def ambient_temp(self) -> 'Diffrn':
		"""The mean temperature in kelvins at which the intensities were  measured."""
		self._enter('ambient_temp', Query)
		return self
	@property
	def ambient_temp_details(self) -> 'Diffrn':
		"""A description of special aspects of temperature control during  data collection."""
		self._enter('ambient_temp_details', Query)
		return self
	@property
	def crystal_id(self) -> 'Diffrn':
		"""This data item is a pointer to _exptl_crystal.id in the  EXPTL_CRYSTAL category."""
		self._enter('crystal_id', Query)
		return self
	@property
	def crystal_support(self) -> 'Diffrn':
		"""The physical device used to support the crystal during data  collection.  Examples: glass capillary, quartz capillary, fiber, metal loop """
		self._enter('crystal_support', Query)
		return self
	@property
	def details(self) -> 'Diffrn':
		"""Special details of the diffraction measurement process. Should  include information about source instability, crystal motion,  degradation and so on."""
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'Diffrn':
		"""This data item uniquely identifies a set of diffraction  data."""
		self._enter('id', Query)
		return self
	@property
	def pdbx_serial_crystal_experiment(self) -> 'Diffrn':
		"""Y/N if using serial crystallography experiment in which multiple crystals contribute to each diffraction frame in the experiment.  Allowable values: N, Y """
		self._enter('pdbx_serial_crystal_experiment', Query)
		return self

class DiffrnDetector(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'DiffrnDetector':
		"""A description of special aspects of the radiation detector."""
		self._enter('details', Query)
		return self
	@property
	def detector(self) -> 'DiffrnDetector':
		"""The general class of the radiation detector.  Examples: photographic film, scintillation counter, CCD plate, BF~3~ counter """
		self._enter('detector', Query)
		return self
	@property
	def diffrn_id(self) -> 'DiffrnDetector':
		"""This data item is a pointer to _diffrn.id in the DIFFRN  category."""
		self._enter('diffrn_id', Query)
		return self
	@property
	def pdbx_collection_date(self) -> 'DiffrnDetector':
		"""The date of data collection.  Examples: 1996-12-25 """
		self._enter('pdbx_collection_date', Query)
		return self
	@property
	def pdbx_frequency(self) -> 'DiffrnDetector':
		"""The operating frequency of the detector (Hz) used in data collection."""
		self._enter('pdbx_frequency', Query)
		return self
	@property
	def type(self) -> 'DiffrnDetector':
		"""The make, model or name of the detector device used.  Examples: DECTRIS PILATUS 12M, RAYONIX MX-325 """
		self._enter('type', Query)
		return self

class DiffrnRadiation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def collimation(self) -> 'DiffrnRadiation':
		"""The collimation or focusing applied to the radiation.  Examples: 0.3 mm double-pinhole, 0.5 mm, focusing mirrors """
		self._enter('collimation', Query)
		return self
	@property
	def diffrn_id(self) -> 'DiffrnRadiation':
		"""This data item is a pointer to _diffrn.id in the DIFFRN  category."""
		self._enter('diffrn_id', Query)
		return self
	@property
	def monochromator(self) -> 'DiffrnRadiation':
		"""The method used to obtain monochromatic radiation. If a mono-  chromator crystal is used, the material and the indices of the  Bragg reflection are specified.  Examples: Zr filter, Ge 220, none, equatorial mounted graphite """
		self._enter('monochromator', Query)
		return self
	@property
	def pdbx_diffrn_protocol(self) -> 'DiffrnRadiation':
		"""SINGLE WAVELENGTH, LAUE, or MAD.  Examples: SINGLE WAVELENGTH, MONOCHROMATIC, LAUE, MAD, OTHER """
		self._enter('pdbx_diffrn_protocol', Query)
		return self
	@property
	def pdbx_monochromatic_or_laue_m_l(self) -> 'DiffrnRadiation':
		"""Monochromatic or Laue.  Allowable values: L, M """
		self._enter('pdbx_monochromatic_or_laue_m_l', Query)
		return self
	@property
	def pdbx_scattering_type(self) -> 'DiffrnRadiation':
		"""The radiation scattering type for this diffraction data set.  Allowable values: electron, neutron, x-ray """
		self._enter('pdbx_scattering_type', Query)
		return self
	@property
	def pdbx_wavelength(self) -> 'DiffrnRadiation':
		"""Wavelength of radiation."""
		self._enter('pdbx_wavelength', Query)
		return self
	@property
	def pdbx_wavelength_list(self) -> 'DiffrnRadiation':
		"""Comma separated list of wavelengths or wavelength range."""
		self._enter('pdbx_wavelength_list', Query)
		return self
	@property
	def type(self) -> 'DiffrnRadiation':
		"""The nature of the radiation. This is typically a description  of the X-ray wavelength in Siegbahn notation.  Examples: CuK\a, Cu K\a~1~, Cu K-L~2,3~, white-beam """
		self._enter('type', Query)
		return self
	@property
	def wavelength_id(self) -> 'DiffrnRadiation':
		"""This data item is a pointer to _diffrn_radiation_wavelength.id  in the DIFFRN_RADIATION_WAVELENGTH category."""
		self._enter('wavelength_id', Query)
		return self

class DiffrnSource(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'DiffrnSource':
		"""A description of special aspects of the radiation source used."""
		self._enter('details', Query)
		return self
	@property
	def diffrn_id(self) -> 'DiffrnSource':
		"""This data item is a pointer to _diffrn.id in the DIFFRN  category."""
		self._enter('diffrn_id', Query)
		return self
	@property
	def pdbx_synchrotron_beamline(self) -> 'DiffrnSource':
		"""Synchrotron beamline.  Examples: 17-ID-1, 19-ID """
		self._enter('pdbx_synchrotron_beamline', Query)
		return self
	@property
	def pdbx_synchrotron_site(self) -> 'DiffrnSource':
		"""Synchrotron site.  Examples: APS, NSLS-II """
		self._enter('pdbx_synchrotron_site', Query)
		return self
	@property
	def pdbx_wavelength(self) -> 'DiffrnSource':
		"""Wavelength of radiation."""
		self._enter('pdbx_wavelength', Query)
		return self
	@property
	def pdbx_wavelength_list(self) -> 'DiffrnSource':
		"""Comma separated list of wavelengths or wavelength range.  Examples: 0.987 or 0.987, 0.988, 1.0 or 0.99-1.5 """
		self._enter('pdbx_wavelength_list', Query)
		return self
	@property
	def source(self) -> 'DiffrnSource':
		"""The general class of the radiation source.  Examples: sealed X-ray tube, nuclear reactor, spallation source, electron microscope, rotating-anode X-ray tube, synchrotron """
		self._enter('source', Query)
		return self
	@property
	def type(self) -> 'DiffrnSource':
		"""The make, model or name of the source of radiation.  Examples: NSLS beamline X8C, Rigaku RU200 """
		self._enter('type', Query)
		return self

class DrugbankContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreDrugbank':
		"""Return to parent (CoreDrugbank)"""
		return self._parent if self._parent else self
	@property
	def drugbank_id(self) -> 'DrugbankContainerIdentifiers':
		"""The DrugBank accession code"""
		self._enter('drugbank_id', Query)
		return self

class DrugbankInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreDrugbank':
		"""Return to parent (CoreDrugbank)"""
		return self._parent if self._parent else self
	@property
	def affected_organisms(self) -> 'DrugbankInfo':
		"""The DrugBank drug affected organisms."""
		self._enter('affected_organisms', Query)
		return self
	@property
	def atc_codes(self) -> 'DrugbankInfo':
		"""The Anatomical Therapeutic Chemical Classification System (ATC) codes."""
		self._enter('atc_codes', Query)
		return self
	@property
	def brand_names(self) -> 'DrugbankInfo':
		"""DrugBank drug brand names."""
		self._enter('brand_names', Query)
		return self
	@property
	def cas_number(self) -> 'DrugbankInfo':
		"""The DrugBank assigned Chemical Abstracts Service identifier.  Examples: 56-65-5 """
		self._enter('cas_number', Query)
		return self
	@property
	def description(self) -> 'DrugbankInfo':
		"""The DrugBank drug description."""
		self._enter('description', Query)
		return self
	@property
	def drug_categories(self) -> 'DrugbankInfo':
		"""The DrugBank drug categories."""
		self._enter('drug_categories', Query)
		return self
	@property
	def drug_groups(self) -> 'DrugbankInfo':
		"""The DrugBank drug groups determine their drug development status.  Allowable values: approved, experimental, illicit, investigational, nutraceutical, vet_approved, withdrawn """
		self._enter('drug_groups', Query)
		return self
	@property
	def drug_products(self) -> 'DrugbankInfoDrugProducts':
		""""""
		return self._enter('drug_products', DrugbankInfoDrugProducts)
	@property
	def drugbank_id(self) -> 'DrugbankInfo':
		"""The DrugBank accession code"""
		self._enter('drugbank_id', Query)
		return self
	@property
	def indication(self) -> 'DrugbankInfo':
		"""The DrugBank drug indication.  Examples: For nutritional supplementation, also for treating dietary shortage or imbalance """
		self._enter('indication', Query)
		return self
	@property
	def mechanism_of_action(self) -> 'DrugbankInfo':
		"""The DrugBank drug mechanism of actions.  Examples: ATP is able to store and transport chemical energy within cells. """
		self._enter('mechanism_of_action', Query)
		return self
	@property
	def name(self) -> 'DrugbankInfo':
		"""The DrugBank drug name."""
		self._enter('name', Query)
		return self
	@property
	def pharmacology(self) -> 'DrugbankInfo':
		"""The DrugBank drug pharmacology.  Examples: Adenosine triphosphate (ATP) is the nucleotide known in biochemistry as the 'molecular currency' of intracellular energy transfer; that is, ATP is able to store and transport chemical energy within cells. ATP also plays an important role in the synthesis of nucleic acids. The total quantity of ATP in the human body is about 0.1 mole. The energy used by human cells requires the hydrolysis of 200 to 300 moles of ATP daily. This means that each ATP molecule is recycled 2000 to 3000 times during a single day. ATP cannot be stored, hence its consumption must closely follow its synthesis. """
		self._enter('pharmacology', Query)
		return self
	@property
	def synonyms(self) -> 'DrugbankInfo':
		"""DrugBank drug name synonyms."""
		self._enter('synonyms', Query)
		return self

class DrugbankInfoDrugProducts(QueryNode):
	""""""
	@property
	def end(self) -> 'DrugbankInfo':
		"""Return to parent (DrugbankInfo)"""
		return self._parent if self._parent else self
	@property
	def approved(self) -> 'DrugbankInfoDrugProducts':
		"""Indicates whether this drug has been approved by the regulating government.  Allowable values: N, Y """
		self._enter('approved', Query)
		return self
	@property
	def country(self) -> 'DrugbankInfoDrugProducts':
		"""The country where this commercially available drug has been approved.  Allowable values: Canada, EU, US """
		self._enter('country', Query)
		return self
	@property
	def ended_marketing_on(self) -> 'DrugbankInfoDrugProducts':
		"""The ending date for market approval.  Examples: 2003-07-30 """
		self._enter('ended_marketing_on', Query)
		return self
	@property
	def name(self) -> 'DrugbankInfoDrugProducts':
		"""The proprietary name(s) provided by the manufacturer for any commercially available products containing this drug.  Examples: Hivid Tab 0.375mg """
		self._enter('name', Query)
		return self
	@property
	def source(self) -> 'DrugbankInfoDrugProducts':
		"""Source of this product information. For example, a value of DPD indicates this information was retrieved from the Canadian Drug Product Database.  Allowable values: DPD, EMA, FDA NDC """
		self._enter('source', Query)
		return self
	@property
	def started_marketing_on(self) -> 'DrugbankInfoDrugProducts':
		"""The starting date for market approval.  Examples: 1992-12-31 """
		self._enter('started_marketing_on', Query)
		return self

class DrugbankTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreDrugbank':
		"""Return to parent (CoreDrugbank)"""
		return self._parent if self._parent else self
	@property
	def interaction_type(self) -> 'DrugbankTarget':
		"""The type of target interaction."""
		self._enter('interaction_type', Query)
		return self
	@property
	def name(self) -> 'DrugbankTarget':
		"""The target name."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'DrugbankTarget':
		"""The value of _drugbank_target.ordinal distinguishes  related examples for each chemical component."""
		self._enter('ordinal', Query)
		return self
	@property
	def organism_common_name(self) -> 'DrugbankTarget':
		"""The organism common name."""
		self._enter('organism_common_name', Query)
		return self
	@property
	def reference_database_accession_code(self) -> 'DrugbankTarget':
		"""The reference identifier code for the target interaction reference.  Examples: Q9HD40 """
		self._enter('reference_database_accession_code', Query)
		return self
	@property
	def reference_database_name(self) -> 'DrugbankTarget':
		"""The reference database name for the target interaction.  Allowable values: UniProt """
		self._enter('reference_database_name', Query)
		return self
	@property
	def seq_one_letter_code(self) -> 'DrugbankTarget':
		"""Target sequence expressed as string of one-letter amino acid codes.  Examples: MAKQRSG... """
		self._enter('seq_one_letter_code', Query)
		return self
	@property
	def target_actions(self) -> 'DrugbankTarget':
		"""The actions of the target interaction."""
		self._enter('target_actions', Query)
		return self

class Em2dCrystalEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def angle_gamma(self) -> 'Em2dCrystalEntity':
		"""Unit-cell angle gamma in degrees."""
		self._enter('angle_gamma', Query)
		return self
	@property
	def c_sampling_length(self) -> 'Em2dCrystalEntity':
		"""Length used to sample the reciprocal lattice lines in the c-direction."""
		self._enter('c_sampling_length', Query)
		return self
	@property
	def id(self) -> 'Em2dCrystalEntity':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'Em2dCrystalEntity':
		"""pointer to _em_image_processing.id in the EM_IMAGE_PROCESSING category."""
		self._enter('image_processing_id', Query)
		return self
	@property
	def length_a(self) -> 'Em2dCrystalEntity':
		"""Unit-cell length a in angstroms.  Examples: null """
		self._enter('length_a', Query)
		return self
	@property
	def length_b(self) -> 'Em2dCrystalEntity':
		"""Unit-cell length b in angstroms.  Examples: null """
		self._enter('length_b', Query)
		return self
	@property
	def length_c(self) -> 'Em2dCrystalEntity':
		"""Thickness of 2D crystal  Examples: null """
		self._enter('length_c', Query)
		return self
	@property
	def space_group_name_H_M(self) -> 'Em2dCrystalEntity':
		"""There are 17 plane groups classified as oblique, rectangular, square, and hexagonal.  To describe the symmetry of 2D crystals of biological molecules,  plane groups are expanded to equivalent noncentrosymmetric space groups.  The 2D crystal plane corresponds to the 'ab' plane of the space group.   Enumerated space group descriptions include the plane group number in parentheses,  the H-M plane group symbol, and the plane group class.  Allowable values: C 1 2, C 2 2 2, P 1, P 1 2, P 1 21, P 2, P 2 2 2, P 2 2 21, P 2 21 21, P 3, P 3 1 2, P 3 2 1, P 4, P 4 2 2, P 4 21 2, P 6, P 6 2 2 """
		self._enter('space_group_name_H_M', Query)
		return self

class Em3dCrystalEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def angle_alpha(self) -> 'Em3dCrystalEntity':
		"""Unit-cell angle alpha in degrees.  Examples: null """
		self._enter('angle_alpha', Query)
		return self
	@property
	def angle_beta(self) -> 'Em3dCrystalEntity':
		"""Unit-cell angle beta in degrees.  Examples: null """
		self._enter('angle_beta', Query)
		return self
	@property
	def angle_gamma(self) -> 'Em3dCrystalEntity':
		"""Unit-cell angle gamma in degrees.  Examples: null """
		self._enter('angle_gamma', Query)
		return self
	@property
	def id(self) -> 'Em3dCrystalEntity':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'Em3dCrystalEntity':
		"""pointer to _em_image_processing.id in the EM_IMAGE_PROCESSING category."""
		self._enter('image_processing_id', Query)
		return self
	@property
	def length_a(self) -> 'Em3dCrystalEntity':
		"""Unit-cell length a in angstroms.  Examples: null """
		self._enter('length_a', Query)
		return self
	@property
	def length_b(self) -> 'Em3dCrystalEntity':
		"""Unit-cell length b in angstroms.  Examples: null """
		self._enter('length_b', Query)
		return self
	@property
	def length_c(self) -> 'Em3dCrystalEntity':
		"""Unit-cell length c in angstroms.  Examples: null """
		self._enter('length_c', Query)
		return self
	@property
	def space_group_name(self) -> 'Em3dCrystalEntity':
		"""Space group name.  Examples: P 1, P 21 21 2, I 4, H 3 """
		self._enter('space_group_name', Query)
		return self
	@property
	def space_group_num(self) -> 'Em3dCrystalEntity':
		"""Space group number."""
		self._enter('space_group_num', Query)
		return self

class Em3dFitting(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'Em3dFitting':
		"""Any additional details regarding fitting of atomic coordinates into  the 3DEM volume, including data and considerations from other  methods used in computation of the model.  Examples: Initial local fitting was done using Chimera and then NMFF was used for flexible fitting. """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'Em3dFitting':
		"""The value of _em_3d_fitting.id must uniquely identify  a fitting procedure of atomic coordinates  into 3dem reconstructed map volume."""
		self._enter('id', Query)
		return self
	@property
	def method(self) -> 'Em3dFitting':
		"""The method used to fit atomic coordinates  into the 3dem reconstructed map."""
		self._enter('method', Query)
		return self
	@property
	def overall_b_value(self) -> 'Em3dFitting':
		"""The overall B (temperature factor) value for the 3d-em volume."""
		self._enter('overall_b_value', Query)
		return self
	@property
	def ref_protocol(self) -> 'Em3dFitting':
		"""The refinement protocol used.  Allowable values: AB INITIO MODEL, BACKBONE TRACE, FLEXIBLE FIT, OTHER, RIGID BODY FIT """
		self._enter('ref_protocol', Query)
		return self
	@property
	def ref_space(self) -> 'Em3dFitting':
		"""A flag to indicate whether fitting was carried out in real  or reciprocal refinement space.  Allowable values: REAL, RECIPROCAL """
		self._enter('ref_space', Query)
		return self
	@property
	def target_criteria(self) -> 'Em3dFitting':
		"""The measure used to assess quality of fit of the atomic coordinates in the  3DEM map volume.  Examples: Cross-correlation coefficient """
		self._enter('target_criteria', Query)
		return self

class Em3dFittingList(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def _3d_fitting_id(self) -> 'Em3dFittingList':
		"""The value of _em_3d_fitting_list.3d_fitting_id is a pointer  to  _em_3d_fitting.id in the 3d_fitting category"""
		self._enter('_3d_fitting_id', Query)
		return self
	@property
	def details(self) -> 'Em3dFittingList':
		"""Details about the model used in fitting.  Examples: The initial model consisted of the complete biological assembly for PDB entry 2GTL. """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'Em3dFittingList':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def pdb_chain_id(self) -> 'Em3dFittingList':
		"""The ID of the biopolymer chain used for fitting, e.g., A.  Please note that only one chain can be specified per instance.  If all chains of a particular structure have been used for fitting, this field can be left blank.  Examples: The ID of the biopolymer chain used for fitting, e.g., A. Please note that only one chain can be specified per instance. If all chains of a particular structure have been used for fitting, this field can be left blank. """
		self._enter('pdb_chain_id', Query)
		return self
	@property
	def pdb_chain_residue_range(self) -> 'Em3dFittingList':
		"""Residue range for the identified chain."""
		self._enter('pdb_chain_residue_range', Query)
		return self
	@property
	def pdb_entry_id(self) -> 'Em3dFittingList':
		"""The PDB code for the entry used in fitting.  Examples: 1EHZ """
		self._enter('pdb_entry_id', Query)
		return self

class Em3dReconstruction(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def actual_pixel_size(self) -> 'Em3dReconstruction':
		"""The actual pixel size of the projection set of images in Angstroms.  Examples: null, null """
		self._enter('actual_pixel_size', Query)
		return self
	@property
	def algorithm(self) -> 'Em3dReconstruction':
		"""The reconstruction algorithm/technique used to generate the map."""
		self._enter('algorithm', Query)
		return self
	@property
	def details(self) -> 'Em3dReconstruction':
		"""Any additional details used in the 3d reconstruction.  Examples: a modified version of SPIDER program was used for the reconstruction """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'Em3dReconstruction':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'Em3dReconstruction':
		"""Foreign key to the EM_IMAGE_PROCESSING category"""
		self._enter('image_processing_id', Query)
		return self
	@property
	def magnification_calibration(self) -> 'Em3dReconstruction':
		"""The magnification calibration method for the 3d reconstruction.  Examples: TMV images """
		self._enter('magnification_calibration', Query)
		return self
	@property
	def method(self) -> 'Em3dReconstruction':
		"""The algorithm method used for the 3d-reconstruction.  Examples: cross-common lines, polar Fourier transform (PFT) """
		self._enter('method', Query)
		return self
	@property
	def nominal_pixel_size(self) -> 'Em3dReconstruction':
		"""The nominal pixel size of the projection set of images in Angstroms.  Examples: null, null """
		self._enter('nominal_pixel_size', Query)
		return self
	@property
	def num_class_averages(self) -> 'Em3dReconstruction':
		"""The number of classes used in the final 3d reconstruction"""
		self._enter('num_class_averages', Query)
		return self
	@property
	def num_particles(self) -> 'Em3dReconstruction':
		"""The number of 2D projections or 3D subtomograms used in the 3d reconstruction"""
		self._enter('num_particles', Query)
		return self
	@property
	def refinement_type(self) -> 'Em3dReconstruction':
		"""Indicates details on how the half-map used for resolution determination (usually by FSC) have been generated.  Allowable values: HALF-MAPS REFINED AGAINST SAME DATA, HALF-MAPS REFINED INDEPENDENTLY, HALF-MAPS REFINED INDEPENDENTLY WITH FREQUENCY RANGE OMITTED, HALF-MAPS REFINED WITH FREQUENCY RANGE OMITTED, OTHER """
		self._enter('refinement_type', Query)
		return self
	@property
	def resolution(self) -> 'Em3dReconstruction':
		"""The final resolution (in angstroms) of the 3D reconstruction.  Examples: null, null """
		self._enter('resolution', Query)
		return self
	@property
	def resolution_method(self) -> 'Em3dReconstruction':
		"""The  method used to determine the final resolution  of the 3d reconstruction.  The Fourier Shell Correlation criterion as a measure of  resolution is based on the concept of splitting the (2D)  data set into two halves; averaging each and comparing them  using the Fourier Ring Correlation (FRC) technique.  Examples: FSC at 0.5 cut-off """
		self._enter('resolution_method', Query)
		return self
	@property
	def symmetry_type(self) -> 'Em3dReconstruction':
		"""The type of symmetry applied to the reconstruction  Allowable values: 2D CRYSTAL, 3D CRYSTAL, HELICAL, POINT """
		self._enter('symmetry_type', Query)
		return self

class EmCtfCorrection(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'EmCtfCorrection':
		"""Any additional details about CTF correction  Examples: CTF amplitude correction was performed following 3D reconstruction """
		self._enter('details', Query)
		return self
	@property
	def em_image_processing_id(self) -> 'EmCtfCorrection':
		"""Foreign key to the EM_IMAGE_PROCESSING category"""
		self._enter('em_image_processing_id', Query)
		return self
	@property
	def id(self) -> 'EmCtfCorrection':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def type(self) -> 'EmCtfCorrection':
		"""Type of CTF correction applied"""
		self._enter('type', Query)
		return self

class EmDiffraction(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def camera_length(self) -> 'EmDiffraction':
		"""The camera length (in millimeters). The camera length is the  product of the objective focal length and the combined magnification  of the intermediate and projector lenses when the microscope is  operated in the diffraction mode."""
		self._enter('camera_length', Query)
		return self
	@property
	def id(self) -> 'EmDiffraction':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def imaging_id(self) -> 'EmDiffraction':
		"""Foreign key to the EM_IMAGING category"""
		self._enter('imaging_id', Query)
		return self
	@property
	def tilt_angle_list(self) -> 'EmDiffraction':
		"""Comma-separated list of tilt angles (in degrees) used in the electron diffraction experiment.  Examples: 20,40,50,55 """
		self._enter('tilt_angle_list', Query)
		return self

class EmDiffractionShell(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def em_diffraction_stats_id(self) -> 'EmDiffractionShell':
		"""Pointer to EM CRYSTALLOGRAPHY STATS"""
		self._enter('em_diffraction_stats_id', Query)
		return self
	@property
	def fourier_space_coverage(self) -> 'EmDiffractionShell':
		"""Completeness of the structure factor data within this resolution shell, in percent  Examples: null """
		self._enter('fourier_space_coverage', Query)
		return self
	@property
	def high_resolution(self) -> 'EmDiffractionShell':
		"""High resolution limit for this shell (angstroms)  Examples: null """
		self._enter('high_resolution', Query)
		return self
	@property
	def id(self) -> 'EmDiffractionShell':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def low_resolution(self) -> 'EmDiffractionShell':
		"""Low resolution limit for this shell (angstroms)  Examples: null """
		self._enter('low_resolution', Query)
		return self
	@property
	def multiplicity(self) -> 'EmDiffractionShell':
		"""Multiplicity (average number of measurements) for the structure factors in this resolution shell  Examples: null """
		self._enter('multiplicity', Query)
		return self
	@property
	def num_structure_factors(self) -> 'EmDiffractionShell':
		"""Number of measured structure factors in this resolution shell"""
		self._enter('num_structure_factors', Query)
		return self
	@property
	def phase_residual(self) -> 'EmDiffractionShell':
		"""Phase residual for this resolution shell, in degrees  Examples: null """
		self._enter('phase_residual', Query)
		return self

class EmDiffractionStats(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'EmDiffractionStats':
		"""Any addition details about the structure factor measurements  Examples: Phases were obtained from micrograph images of the 2D crystals """
		self._enter('details', Query)
		return self
	@property
	def fourier_space_coverage(self) -> 'EmDiffractionStats':
		"""Completeness of the structure factor data within the defined space group  at the reported resolution (percent).  Examples: null """
		self._enter('fourier_space_coverage', Query)
		return self
	@property
	def high_resolution(self) -> 'EmDiffractionStats':
		"""High resolution limit of the structure factor data, in angstroms  Examples: null """
		self._enter('high_resolution', Query)
		return self
	@property
	def id(self) -> 'EmDiffractionStats':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'EmDiffractionStats':
		"""Pointer to _em_image_processing.id"""
		self._enter('image_processing_id', Query)
		return self
	@property
	def num_intensities_measured(self) -> 'EmDiffractionStats':
		"""Total number of diffraction intensities measured (before averaging)"""
		self._enter('num_intensities_measured', Query)
		return self
	@property
	def num_structure_factors(self) -> 'EmDiffractionStats':
		"""Number of structure factors obtained (merged amplitudes + phases)"""
		self._enter('num_structure_factors', Query)
		return self
	@property
	def overall_phase_error(self) -> 'EmDiffractionStats':
		"""Overall phase error in degrees  Examples: null """
		self._enter('overall_phase_error', Query)
		return self
	@property
	def overall_phase_residual(self) -> 'EmDiffractionStats':
		"""Overall phase residual in degrees  Examples: null """
		self._enter('overall_phase_residual', Query)
		return self
	@property
	def phase_error_rejection_criteria(self) -> 'EmDiffractionStats':
		"""Criteria used to reject phases  Examples: Structure factors with phase errors higher than 20 degrees were omitted from refinement """
		self._enter('phase_error_rejection_criteria', Query)
		return self
	@property
	def r_merge(self) -> 'EmDiffractionStats':
		"""Rmerge value (percent)  Examples: null """
		self._enter('r_merge', Query)
		return self
	@property
	def r_sym(self) -> 'EmDiffractionStats':
		"""Rsym value (percent)  Examples: null """
		self._enter('r_sym', Query)
		return self

class EmEmbedding(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'EmEmbedding':
		"""Staining procedure used in the specimen preparation.  Examples: The crystal suspension was injected into the lens of a drop of buffer containing   1 % tannin sitting on a carbon film supported by a molybdenum grid.  An equal volume   of 1% glucose was then added and the solution thoroughly but gently mixed.  The grid   was then blotted, air dried, and frozen in LN2. """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'EmEmbedding':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def material(self) -> 'EmEmbedding':
		"""The embedding  material.  Examples: tannin and glucose """
		self._enter('material', Query)
		return self
	@property
	def specimen_id(self) -> 'EmEmbedding':
		"""Foreign key relationship to the EM SPECIMEN category"""
		self._enter('specimen_id', Query)
		return self

class EmEntityAssembly(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'EmEntityAssembly':
		"""Additional details about the sample or sample subcomponent.  Examples: Fab fragment generated by proteolytic cleavage of LA2 IgG antibody. """
		self._enter('details', Query)
		return self
	@property
	def entity_id_list(self) -> 'EmEntityAssembly':
		"""macromolecules associated with this component, if defined  as comma separated list of entity ids (integers)."""
		self._enter('entity_id_list', Query)
		return self
	@property
	def id(self) -> 'EmEntityAssembly':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'EmEntityAssembly':
		"""The name of the sample or sample subcomponent.  Examples: Ternary complex of alpha-tubulin with tubulin folding cofactors TBCE and TBCB, 80S Ribosome bound to emetine, messenger RNA, initiation factor 2, GroEL, antibody Fab fragment """
		self._enter('name', Query)
		return self
	@property
	def oligomeric_details(self) -> 'EmEntityAssembly':
		"""oligomeric details"""
		self._enter('oligomeric_details', Query)
		return self
	@property
	def parent_id(self) -> 'EmEntityAssembly':
		"""The parent of this assembly.  This data item is an internal category pointer to _em_entity_assembly.id.  By convention, the full assembly (top of hierarchy) is assigned parent id 0 (zero)."""
		self._enter('parent_id', Query)
		return self
	@property
	def source(self) -> 'EmEntityAssembly':
		"""The type of source (e.g., natural source) for the component (sample or sample subcomponent)  Allowable values: MULTIPLE SOURCES, NATURAL, RECOMBINANT, SYNTHETIC """
		self._enter('source', Query)
		return self
	@property
	def synonym(self) -> 'EmEntityAssembly':
		"""Alternative name of the component.  Examples: FADV-1 """
		self._enter('synonym', Query)
		return self
	@property
	def type(self) -> 'EmEntityAssembly':
		"""The general type of the sample or sample subcomponent."""
		self._enter('type', Query)
		return self

class EmExperiment(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def aggregation_state(self) -> 'EmExperiment':
		"""The aggregation/assembly state of the imaged specimen.  Allowable values: 2D ARRAY, 3D ARRAY, CELL, FILAMENT, HELICAL ARRAY, PARTICLE, TISSUE """
		self._enter('aggregation_state', Query)
		return self
	@property
	def entity_assembly_id(self) -> 'EmExperiment':
		"""Foreign key to the EM_ENTITY_ASSEMBLY category"""
		self._enter('entity_assembly_id', Query)
		return self
	@property
	def id(self) -> 'EmExperiment':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def reconstruction_method(self) -> 'EmExperiment':
		"""The reconstruction method used in the EM experiment.  Allowable values: CRYSTALLOGRAPHY, HELICAL, SINGLE PARTICLE, SUBTOMOGRAM AVERAGING, TOMOGRAPHY """
		self._enter('reconstruction_method', Query)
		return self

class EmHelicalEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def angular_rotation_per_subunit(self) -> 'EmHelicalEntity':
		"""The angular rotation per helical subunit in degrees. Negative values indicate left-handed helices; positive values indicate right handed helices.  Examples: null """
		self._enter('angular_rotation_per_subunit', Query)
		return self
	@property
	def axial_rise_per_subunit(self) -> 'EmHelicalEntity':
		"""The axial rise per subunit in the helical assembly.  Examples: null """
		self._enter('axial_rise_per_subunit', Query)
		return self
	@property
	def axial_symmetry(self) -> 'EmHelicalEntity':
		"""Symmetry of the helical axis, either cyclic (Cn) or dihedral (Dn), where n>=1.  Examples: C1, D2, C7 """
		self._enter('axial_symmetry', Query)
		return self
	@property
	def details(self) -> 'EmHelicalEntity':
		"""Any other details regarding the helical assembly  Examples: Dihedral symmetry """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'EmHelicalEntity':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'EmHelicalEntity':
		"""This data item is a pointer to _em_image_processing.id."""
		self._enter('image_processing_id', Query)
		return self

class EmImageRecording(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def average_exposure_time(self) -> 'EmImageRecording':
		"""The average exposure time for each image.  Examples: null """
		self._enter('average_exposure_time', Query)
		return self
	@property
	def avg_electron_dose_per_image(self) -> 'EmImageRecording':
		"""The electron dose received by the specimen per image (electrons per square angstrom).  Examples: null """
		self._enter('avg_electron_dose_per_image', Query)
		return self
	@property
	def details(self) -> 'EmImageRecording':
		"""Any additional details about image recording.  Examples: Images were collected in movie-mode at 17 frames per second """
		self._enter('details', Query)
		return self
	@property
	def detector_mode(self) -> 'EmImageRecording':
		"""The detector mode used during image recording.  Allowable values: COUNTING, INTEGRATING, OTHER, SUPER-RESOLUTION """
		self._enter('detector_mode', Query)
		return self
	@property
	def film_or_detector_model(self) -> 'EmImageRecording':
		"""The detector type used for recording images.  Usually film , CCD camera or direct electron detector."""
		self._enter('film_or_detector_model', Query)
		return self
	@property
	def id(self) -> 'EmImageRecording':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def imaging_id(self) -> 'EmImageRecording':
		"""This data item the id of the microscopy settings used in the imaging."""
		self._enter('imaging_id', Query)
		return self
	@property
	def num_diffraction_images(self) -> 'EmImageRecording':
		"""The number of diffraction images collected."""
		self._enter('num_diffraction_images', Query)
		return self
	@property
	def num_grids_imaged(self) -> 'EmImageRecording':
		"""Number of grids in the microscopy session"""
		self._enter('num_grids_imaged', Query)
		return self
	@property
	def num_real_images(self) -> 'EmImageRecording':
		"""The number of micrograph images collected."""
		self._enter('num_real_images', Query)
		return self

class EmImaging(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def accelerating_voltage(self) -> 'EmImaging':
		"""A value of accelerating voltage (in kV) used for imaging."""
		self._enter('accelerating_voltage', Query)
		return self
	@property
	def alignment_procedure(self) -> 'EmImaging':
		"""The type of procedure used to align the microscope electron beam.  Allowable values: BASIC, COMA FREE, NONE, OTHER, ZEMLIN TABLEAU """
		self._enter('alignment_procedure', Query)
		return self
	@property
	def astigmatism(self) -> 'EmImaging':
		"""astigmatism"""
		self._enter('astigmatism', Query)
		return self
	@property
	def c2_aperture_diameter(self) -> 'EmImaging':
		"""The open diameter of the c2 condenser lens,  in microns."""
		self._enter('c2_aperture_diameter', Query)
		return self
	@property
	def calibrated_defocus_max(self) -> 'EmImaging':
		"""The maximum calibrated defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
		self._enter('calibrated_defocus_max', Query)
		return self
	@property
	def calibrated_defocus_min(self) -> 'EmImaging':
		"""The minimum calibrated defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
		self._enter('calibrated_defocus_min', Query)
		return self
	@property
	def calibrated_magnification(self) -> 'EmImaging':
		"""The magnification value obtained for a known standard just  prior to, during or just after the imaging experiment."""
		self._enter('calibrated_magnification', Query)
		return self
	@property
	def cryogen(self) -> 'EmImaging':
		"""Cryogen type used to maintain the specimen stage temperature during imaging  in the microscope.  Allowable values: HELIUM, NITROGEN """
		self._enter('cryogen', Query)
		return self
	@property
	def date(self) -> 'EmImaging':
		"""Date (YYYY-MM-DD) of imaging experiment or the date at which  a series of experiments began.  Examples: 2001-05-08 """
		self._enter('date', Query)
		return self
	@property
	def details(self) -> 'EmImaging':
		"""Any additional imaging details.  Examples: Preliminary grid screening was performed manually. """
		self._enter('details', Query)
		return self
	@property
	def detector_distance(self) -> 'EmImaging':
		"""The camera length (in millimeters). The camera length is the  product of the objective focal length and the combined magnification  of the intermediate and projector lenses when the microscope is  operated in the diffraction mode."""
		self._enter('detector_distance', Query)
		return self
	@property
	def electron_beam_tilt_params(self) -> 'EmImaging':
		"""electron beam tilt params"""
		self._enter('electron_beam_tilt_params', Query)
		return self
	@property
	def electron_source(self) -> 'EmImaging':
		"""The source of electrons. The electron gun."""
		self._enter('electron_source', Query)
		return self
	@property
	def id(self) -> 'EmImaging':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def illumination_mode(self) -> 'EmImaging':
		"""The mode of illumination.  Allowable values: FLOOD BEAM, OTHER, SPOT SCAN """
		self._enter('illumination_mode', Query)
		return self
	@property
	def microscope_model(self) -> 'EmImaging':
		"""The name of the model of microscope.  Allowable values: FEI MORGAGNI, FEI POLARA 300, FEI TALOS ARCTICA, FEI TECNAI 10, FEI TECNAI 12, FEI TECNAI 20, FEI TECNAI ARCTICA, FEI TECNAI F20, FEI TECNAI F30, FEI TECNAI SPHERA, FEI TECNAI SPIRIT, FEI TITAN, FEI TITAN KRIOS, FEI/PHILIPS CM10, FEI/PHILIPS CM12, FEI/PHILIPS CM120T, FEI/PHILIPS CM200FEG, FEI/PHILIPS CM200FEG/SOPHIE, FEI/PHILIPS CM200FEG/ST, FEI/PHILIPS CM200FEG/UT, FEI/PHILIPS CM200T, FEI/PHILIPS CM300FEG/HE, FEI/PHILIPS CM300FEG/ST, FEI/PHILIPS CM300FEG/T, FEI/PHILIPS EM400, FEI/PHILIPS EM420, HITACHI EF2000, HITACHI EF3000, HITACHI H-9500SD, HITACHI H3000 UHVEM, HITACHI H7600, HITACHI HF2000, HITACHI HF3000, JEOL 1000EES, JEOL 100B, JEOL 100CX, JEOL 1010, JEOL 1200, JEOL 1200EX, JEOL 1200EXII, JEOL 1230, JEOL 1400, JEOL 1400/HR + YPS FEG, JEOL 2000EX, JEOL 2000EXII, JEOL 2010, JEOL 2010F, JEOL 2010HC, JEOL 2010HT, JEOL 2010UHR, JEOL 2011, JEOL 2100, JEOL 2100F, JEOL 2200FS, JEOL 2200FSC, JEOL 3000SFF, JEOL 3100FEF, JEOL 3100FFC, JEOL 3200FS, JEOL 3200FSC, JEOL 4000, JEOL 4000EX, JEOL CRYO ARM 200, JEOL CRYO ARM 300, JEOL KYOTO-3000SFF, SIEMENS SULEIKA, TFS GLACIOS, TFS KRIOS, TFS TALOS, TFS TALOS F200C, TFS TALOS L120C, TFS TITAN THEMIS, TFS TUNDRA, ZEISS LEO912, ZEISS LIBRA120PLUS """
		self._enter('microscope_model', Query)
		return self
	@property
	def mode(self) -> 'EmImaging':
		"""The mode of imaging.  Allowable values: 4D-STEM, BRIGHT FIELD, DARK FIELD, DIFFRACTION, OTHER """
		self._enter('mode', Query)
		return self
	@property
	def nominal_cs(self) -> 'EmImaging':
		"""The spherical aberration coefficient (Cs) in millimeters,  of the objective lens.  Examples: null """
		self._enter('nominal_cs', Query)
		return self
	@property
	def nominal_defocus_max(self) -> 'EmImaging':
		"""The maximum defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
		self._enter('nominal_defocus_max', Query)
		return self
	@property
	def nominal_defocus_min(self) -> 'EmImaging':
		"""The minimum defocus value of the objective lens (in nanometers) used  to obtain the recorded images. Negative values refer to overfocus."""
		self._enter('nominal_defocus_min', Query)
		return self
	@property
	def nominal_magnification(self) -> 'EmImaging':
		"""The magnification indicated by the microscope readout."""
		self._enter('nominal_magnification', Query)
		return self
	@property
	def recording_temperature_maximum(self) -> 'EmImaging':
		"""The specimen temperature maximum (kelvin) for the duration  of imaging."""
		self._enter('recording_temperature_maximum', Query)
		return self
	@property
	def recording_temperature_minimum(self) -> 'EmImaging':
		"""The specimen temperature minimum (kelvin) for the duration  of imaging."""
		self._enter('recording_temperature_minimum', Query)
		return self
	@property
	def residual_tilt(self) -> 'EmImaging':
		"""Residual tilt of the electron beam (in miliradians)"""
		self._enter('residual_tilt', Query)
		return self
	@property
	def specimen_holder_model(self) -> 'EmImaging':
		"""The name of the model of specimen holder used during imaging.  Allowable values: FEI TITAN KRIOS AUTOGRID HOLDER, FISCHIONE 2550, FISCHIONE INSTRUMENTS DUAL AXIS TOMOGRAPHY HOLDER, GATAN 626 SINGLE TILT LIQUID NITROGEN CRYO TRANSFER HOLDER, GATAN 910 MULTI-SPECIMEN SINGLE TILT CRYO TRANSFER HOLDER, GATAN 914 HIGH TILT LIQUID NITROGEN CRYO TRANSFER TOMOGRAPHY HOLDER, GATAN 915 DOUBLE TILT LIQUID NITROGEN CRYO TRANSFER HOLDER, GATAN CHDT 3504 DOUBLE TILT HIGH RESOLUTION NITROGEN COOLING HOLDER, GATAN CT3500 SINGLE TILT LIQUID NITROGEN CRYO TRANSFER HOLDER, GATAN CT3500TR SINGLE TILT ROTATION LIQUID NITROGEN CRYO TRANSFER HOLDER, GATAN ELSA 698 SINGLE TILT LIQUID NITROGEN CRYO TRANSFER HOLDER, GATAN HC 3500 SINGLE TILT HEATING/NITROGEN COOLING HOLDER, GATAN HCHDT 3010 DOUBLE TILT HIGH RESOLUTION HELIUM COOLING HOLDER, GATAN HCHST 3008 SINGLE TILT HIGH RESOLUTION HELIUM COOLING HOLDER, GATAN HELIUM, GATAN LIQUID NITROGEN, GATAN UHRST 3500 SINGLE TILT ULTRA HIGH RESOLUTION NITROGEN COOLING HOLDER, GATAN ULTDT ULTRA LOW TEMPERATURE DOUBLE TILT HELIUM COOLING HOLDER, GATAN ULTST ULTRA LOW TEMPERATURE SINGLE TILT HELIUM COOLING HOLDER, HOME BUILD, JEOL, JEOL 3200FSC CRYOHOLDER, JEOL CRYOSPECPORTER, OTHER, PHILIPS ROTATION HOLDER, SIDE ENTRY, EUCENTRIC """
		self._enter('specimen_holder_model', Query)
		return self
	@property
	def specimen_holder_type(self) -> 'EmImaging':
		"""The type of specimen holder used during imaging.  Examples: cryo """
		self._enter('specimen_holder_type', Query)
		return self
	@property
	def specimen_id(self) -> 'EmImaging':
		"""Foreign key to the EM_SPECIMEN category"""
		self._enter('specimen_id', Query)
		return self
	@property
	def temperature(self) -> 'EmImaging':
		"""The mean specimen stage temperature (in kelvin) during imaging  in the microscope."""
		self._enter('temperature', Query)
		return self
	@property
	def tilt_angle_max(self) -> 'EmImaging':
		"""The maximum angle at which the specimen was tilted to obtain  recorded images."""
		self._enter('tilt_angle_max', Query)
		return self
	@property
	def tilt_angle_min(self) -> 'EmImaging':
		"""The minimum angle at which the specimen was tilted to obtain  recorded images."""
		self._enter('tilt_angle_min', Query)
		return self

class EmParticleSelection(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'EmParticleSelection':
		"""Additional detail such as description of filters used, if selection was manual or automated, and/or template details.  Examples: negative monitor contrast facilitated particle picking """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'EmParticleSelection':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'EmParticleSelection':
		"""The value of _em_particle_selection.image_processing_id points to  the EM_IMAGE_PROCESSING category."""
		self._enter('image_processing_id', Query)
		return self
	@property
	def num_particles_selected(self) -> 'EmParticleSelection':
		"""The number of particles selected from the projection set of images."""
		self._enter('num_particles_selected', Query)
		return self

class EmSingleParticleEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def id(self) -> 'EmSingleParticleEntity':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'EmSingleParticleEntity':
		"""pointer to _em_image_processing.id."""
		self._enter('image_processing_id', Query)
		return self
	@property
	def point_symmetry(self) -> 'EmSingleParticleEntity':
		"""Point symmetry symbol, either Cn, Dn, T, O, or I  Examples: C1, C5, C4 """
		self._enter('point_symmetry', Query)
		return self

class EmSoftware(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def category(self) -> 'EmSoftware':
		"""The purpose of the software.  Allowable values: CLASSIFICATION, CRYSTALLOGRAPHY MERGING, CTF CORRECTION, DIFFRACTION INDEXING, EWALD SPHERE CORRECTION, FINAL EULER ASSIGNMENT, IMAGE ACQUISITION, INITIAL EULER ASSIGNMENT, LATTICE DISTORTION CORRECTION, LAYERLINE INDEXING, MASKING, MODEL FITTING, MODEL REFINEMENT, MOLECULAR REPLACEMENT, OTHER, PARTICLE SELECTION, RECONSTRUCTION, SERIES ALIGNMENT, SYMMETRY DETERMINATION, VOLUME SELECTION """
		self._enter('category', Query)
		return self
	@property
	def details(self) -> 'EmSoftware':
		"""Details about the software used.  Examples: EMAN2 e2boxer.py was used to automatically select particle images. """
		self._enter('details', Query)
		return self
	@property
	def fitting_id(self) -> 'EmSoftware':
		"""pointer to _em_3d_fitting.id in the EM_3D_FITTING category."""
		self._enter('fitting_id', Query)
		return self
	@property
	def id(self) -> 'EmSoftware':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def image_processing_id(self) -> 'EmSoftware':
		"""pointer to _em_image_processing.id in the EM_IMAGE_PROCESSING category."""
		self._enter('image_processing_id', Query)
		return self
	@property
	def imaging_id(self) -> 'EmSoftware':
		"""pointer to _em_imaging.id in the EM_IMAGING category."""
		self._enter('imaging_id', Query)
		return self
	@property
	def name(self) -> 'EmSoftware':
		"""The name of the software package used, e.g., RELION.  Depositors are strongly   encouraged to provide a value in this field.  Examples: EMAN, Imagic, Spider, Bsoft, UCSF-Chimera """
		self._enter('name', Query)
		return self
	@property
	def version(self) -> 'EmSoftware':
		"""The version of the software.  Examples: 9.03, 2.1 """
		self._enter('version', Query)
		return self

class EmSpecimen(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def concentration(self) -> 'EmSpecimen':
		"""The concentration (in milligrams per milliliter, mg/ml)  of the complex in the sample.  Examples: null """
		self._enter('concentration', Query)
		return self
	@property
	def details(self) -> 'EmSpecimen':
		"""A description of any additional details of the specimen preparation.  Examples: This sample was monodisperse., Au was deposited at a 30 degree angle to 15 nm thickness., Colloidal gold particles were deposited by dipping into dilute solution., The specimen was frozen at high pressure using the bal-tec hpm 010 instrument., The embedded sample was sectioned at 100 K to 50 nm final thickness. """
		self._enter('details', Query)
		return self
	@property
	def embedding_applied(self) -> 'EmSpecimen':
		"""'YES' indicates that the specimen has been embedded.  Allowable values: NO, YES """
		self._enter('embedding_applied', Query)
		return self
	@property
	def experiment_id(self) -> 'EmSpecimen':
		"""Pointer to _em_experiment.id."""
		self._enter('experiment_id', Query)
		return self
	@property
	def id(self) -> 'EmSpecimen':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def shadowing_applied(self) -> 'EmSpecimen':
		"""'YES' indicates that the specimen has been shadowed.  Allowable values: NO, YES """
		self._enter('shadowing_applied', Query)
		return self
	@property
	def staining_applied(self) -> 'EmSpecimen':
		"""'YES' indicates that the specimen has been stained.  Allowable values: NO, YES """
		self._enter('staining_applied', Query)
		return self
	@property
	def vitrification_applied(self) -> 'EmSpecimen':
		"""'YES' indicates that the specimen was vitrified by cryopreservation.  Allowable values: NO, YES """
		self._enter('vitrification_applied', Query)
		return self

class EmStaining(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'EmStaining':
		"""Staining procedure used in the specimen preparation.  Examples: Negatively stained EM specimens were prepared using a carbon-sandwich technique   and uranyl-formate stain. """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'EmStaining':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def material(self) -> 'EmStaining':
		"""The staining  material.  Examples: Uranyl Acetate """
		self._enter('material', Query)
		return self
	@property
	def specimen_id(self) -> 'EmStaining':
		"""Foreign key relationship to the EM SPECIMEN category"""
		self._enter('specimen_id', Query)
		return self
	@property
	def type(self) -> 'EmStaining':
		"""type of staining  Allowable values: NEGATIVE, NONE, POSITIVE """
		self._enter('type', Query)
		return self

class EmVitrification(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def chamber_temperature(self) -> 'EmVitrification':
		"""The temperature (in kelvin) of the sample just prior to vitrification."""
		self._enter('chamber_temperature', Query)
		return self
	@property
	def cryogen_name(self) -> 'EmVitrification':
		"""This is the name of the cryogen.  Allowable values: ETHANE, ETHANE-PROPANE, FREON 12, FREON 22, HELIUM, METHANE, NITROGEN, OTHER, PROPANE """
		self._enter('cryogen_name', Query)
		return self
	@property
	def details(self) -> 'EmVitrification':
		"""Any additional details relating to vitrification.  Examples: Vitrification carried out in argon atmosphere. """
		self._enter('details', Query)
		return self
	@property
	def humidity(self) -> 'EmVitrification':
		"""Relative humidity (%) of air surrounding the specimen just prior to vitrification."""
		self._enter('humidity', Query)
		return self
	@property
	def id(self) -> 'EmVitrification':
		"""PRIMARY KEY"""
		self._enter('id', Query)
		return self
	@property
	def instrument(self) -> 'EmVitrification':
		"""The type of instrument used in the vitrification process.  Allowable values: CRYOSOL VITROJET, EMS-002 RAPID IMMERSION FREEZER, FEI VITROBOT MARK I, FEI VITROBOT MARK II, FEI VITROBOT MARK III, FEI VITROBOT MARK IV, GATAN CRYOPLUNGE 3, HOMEMADE PLUNGER, LEICA EM CPC, LEICA EM GP, LEICA KF80, LEICA PLUNGER, REICHERT-JUNG PLUNGER, SPOTITON, SPT LABTECH CHAMELEON, ZEISS PLUNGE FREEZER CRYOBOX """
		self._enter('instrument', Query)
		return self
	@property
	def method(self) -> 'EmVitrification':
		"""The procedure for vitrification.  Examples: plunge freezing """
		self._enter('method', Query)
		return self
	@property
	def specimen_id(self) -> 'EmVitrification':
		"""This data item is a pointer to _em_specimen.id"""
		self._enter('specimen_id', Query)
		return self
	@property
	def temp(self) -> 'EmVitrification':
		"""The vitrification temperature (in kelvin), e.g.,   temperature of the plunge instrument cryogen bath."""
		self._enter('temp', Query)
		return self
	@property
	def time_resolved_state(self) -> 'EmVitrification':
		"""The length of time after an event effecting the sample that  vitrification was induced and a description of the event.  Examples: plunge 30 msec after spraying with effector """
		self._enter('time_resolved_state', Query)
		return self

class EntityPoly(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def nstd_linkage(self) -> 'EntityPoly':
		"""A flag to indicate whether the polymer contains at least  one monomer-to-monomer link different from that implied by  _entity_poly.type.  Allowable values: n, no, y, yes """
		self._enter('nstd_linkage', Query)
		return self
	@property
	def nstd_monomer(self) -> 'EntityPoly':
		"""A flag to indicate whether the polymer contains at least  one monomer that is not considered standard.  Allowable values: n, no, y, yes """
		self._enter('nstd_monomer', Query)
		return self
	@property
	def pdbx_seq_one_letter_code(self) -> 'EntityPoly':
		"""Sequence of protein or nucleic acid polymer in standard one-letter                codes of amino acids or nucleotides. Non-standard amino                acids/nucleotides are represented by their Chemical                Component Dictionary (CCD) codes in                parenthesis. Deoxynucleotides are represented by the                specially-assigned 2-letter CCD codes in parenthesis,                with 'D' prefix added to their ribonucleotide                counterparts. For hybrid polymer, each residue is                represented by the code of its individual type. A                cyclic polymer is represented in linear sequence from                the chosen start to end.  A for Alanine or Adenosine-5'-monophosphate C for Cysteine or Cytidine-5'-monophosphate D for Aspartic acid E for Glutamic acid F for Phenylalanine G for Glycine or Guanosine-5'-monophosphate H for Histidine I for Isoleucine or Inosinic Acid L for Leucine K for Lysine M for Methionine N for Asparagine  or Unknown ribonucleotide O for Pyrrolysine P for Proline Q for Glutamine R for Arginine S for Serine T for Threonine U for Selenocysteine or Uridine-5'-monophosphate V for Valine W for Tryptophan Y for Tyrosine (DA) for 2'-deoxyadenosine-5'-monophosphate (DC) for 2'-deoxycytidine-5'-monophosphate (DG) for 2'-deoxyguanosine-5'-monophosphate (DT) for Thymidine-5'-monophosphate (MSE) for Selenomethionine (SEP) for Phosphoserine (TPO) for Phosphothreonine (PTR) for Phosphotyrosine (PCA) for Pyroglutamic acid (UNK) for Unknown amino acid (ACE) for Acetylation cap (NH2) for Amidation cap  Examples: HHHH(MSE)AKQRSG or AUCGGAAU, (MSE)SHHWGYGKHNGPEHWHKDFPIAKGERQSPVDIDTHTAKYDPSLKPLSVSYDQATSLRILNNGAAFNVEFD """
		self._enter('pdbx_seq_one_letter_code', Query)
		return self
	@property
	def pdbx_seq_one_letter_code_can(self) -> 'EntityPoly':
		"""Canonical sequence of protein or nucleic acid polymer in standard                one-letter codes of amino acids or nucleotides,                corresponding to the sequence in                _entity_poly.pdbx_seq_one_letter_code. Non-standard                amino acids/nucleotides are represented by the codes of                their parents if parent is specified in                _chem_comp.mon_nstd_parent_comp_id, or by letter 'X' if                parent is not specified. Deoxynucleotides are                represented by their canonical one-letter codes of A,                C, G, or T.                 For modifications with several parent amino acids, 	       all corresponding parent amino acid codes will be listed 	       (ex. chromophores).  Examples: MSHHWGYGKHNGPEHWHKDFPIAKGERQSPVDIDTHTAKYDPSLKPLSVSYDQATSLRILNNGAAFNVEFD """
		self._enter('pdbx_seq_one_letter_code_can', Query)
		return self
	@property
	def pdbx_sequence_evidence_code(self) -> 'EntityPoly':
		"""Evidence for the assignment of the polymer sequence.  Allowable values: depositor provided, derived from coordinates """
		self._enter('pdbx_sequence_evidence_code', Query)
		return self
	@property
	def pdbx_strand_id(self) -> 'EntityPoly':
		"""The PDB strand/chain id(s) corresponding to this polymer entity.  Examples: A,B, A, B, A,B,C """
		self._enter('pdbx_strand_id', Query)
		return self
	@property
	def pdbx_target_identifier(self) -> 'EntityPoly':
		"""For Structural Genomics entries, the sequence's target identifier registered at the TargetTrack database.  Examples: JCSG-11211, 356560 """
		self._enter('pdbx_target_identifier', Query)
		return self
	@property
	def rcsb_artifact_monomer_count(self) -> 'EntityPoly':
		"""Number of regions in the sample sequence identified as expression tags, linkers, or  cloning artifacts."""
		self._enter('rcsb_artifact_monomer_count', Query)
		return self
	@property
	def rcsb_conflict_count(self) -> 'EntityPoly':
		"""Number of monomer conflicts relative to the reference sequence."""
		self._enter('rcsb_conflict_count', Query)
		return self
	@property
	def rcsb_deletion_count(self) -> 'EntityPoly':
		"""Number of monomer deletions relative to the reference sequence."""
		self._enter('rcsb_deletion_count', Query)
		return self
	@property
	def rcsb_entity_polymer_type(self) -> 'EntityPoly':
		"""A coarse-grained polymer entity type.  Allowable values: DNA, NA-hybrid, Other, Protein, RNA """
		self._enter('rcsb_entity_polymer_type', Query)
		return self
	@property
	def rcsb_insertion_count(self) -> 'EntityPoly':
		"""Number of monomer insertions relative to the reference sequence."""
		self._enter('rcsb_insertion_count', Query)
		return self
	@property
	def rcsb_mutation_count(self) -> 'EntityPoly':
		"""Number of engineered mutations engineered in the sample sequence."""
		self._enter('rcsb_mutation_count', Query)
		return self
	@property
	def rcsb_non_std_monomer_count(self) -> 'EntityPoly':
		"""Number of non-standard monomers in the sample sequence."""
		self._enter('rcsb_non_std_monomer_count', Query)
		return self
	@property
	def rcsb_non_std_monomers(self) -> 'EntityPoly':
		"""Unique list of non-standard monomer chemical component identifiers in the sample sequence."""
		self._enter('rcsb_non_std_monomers', Query)
		return self
	@property
	def rcsb_prd_id(self) -> 'EntityPoly':
		"""For polymer BIRD molecules the BIRD identifier for the entity."""
		self._enter('rcsb_prd_id', Query)
		return self
	@property
	def rcsb_sample_sequence_length(self) -> 'EntityPoly':
		"""The monomer length of the sample sequence."""
		self._enter('rcsb_sample_sequence_length', Query)
		return self
	@property
	def type(self) -> 'EntityPoly':
		"""The type of the polymer.  Allowable values: cyclic-pseudo-peptide, other, peptide nucleic acid, polydeoxyribonucleotide, polydeoxyribonucleotide/polyribonucleotide hybrid, polypeptide(D), polypeptide(L), polyribonucleotide """
		self._enter('type', Query)
		return self

class EntitySrcGen(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def expression_system_id(self) -> 'EntitySrcGen':
		"""A unique identifier for the expression system. This  should be extracted from a local list of expression  systems."""
		self._enter('expression_system_id', Query)
		return self
	@property
	def gene_src_common_name(self) -> 'EntitySrcGen':
		"""The common name of the natural organism from which the gene was  obtained.  Examples: man, yeast, bacteria """
		self._enter('gene_src_common_name', Query)
		return self
	@property
	def gene_src_details(self) -> 'EntitySrcGen':
		"""A description of special aspects of the natural organism from  which the gene was obtained."""
		self._enter('gene_src_details', Query)
		return self
	@property
	def gene_src_genus(self) -> 'EntitySrcGen':
		"""The genus of the natural organism from which the gene was  obtained.  Examples: Homo, Saccharomyces, Escherichia """
		self._enter('gene_src_genus', Query)
		return self
	@property
	def gene_src_species(self) -> 'EntitySrcGen':
		"""The species of the natural organism from which the gene was  obtained.  Examples: sapiens, cerevisiae, coli """
		self._enter('gene_src_species', Query)
		return self
	@property
	def gene_src_strain(self) -> 'EntitySrcGen':
		"""The strain of the natural organism from which the gene was  obtained, if relevant.  Examples: DH5a, BMH 71-18 """
		self._enter('gene_src_strain', Query)
		return self
	@property
	def gene_src_tissue(self) -> 'EntitySrcGen':
		"""The tissue of the natural organism from which the gene was  obtained.  Examples: heart, liver, eye lens """
		self._enter('gene_src_tissue', Query)
		return self
	@property
	def gene_src_tissue_fraction(self) -> 'EntitySrcGen':
		"""The subcellular fraction of the tissue of the natural organism  from which the gene was obtained.  Examples: mitochondria, nucleus, membrane """
		self._enter('gene_src_tissue_fraction', Query)
		return self
	@property
	def host_org_common_name(self) -> 'EntitySrcGen':
		"""The common name of the organism that served as host for the  production of the entity.  Where full details of the protein  production are available it would be expected that this item  be derived from _entity_src_gen_express.host_org_common_name  or via _entity_src_gen_express.host_org_tax_id  Examples: yeast, bacteria """
		self._enter('host_org_common_name', Query)
		return self
	@property
	def host_org_details(self) -> 'EntitySrcGen':
		"""A description of special aspects of the organism that served as  host for the production of the entity. Where full details of  the protein production are available it would be expected that  this item would derived from _entity_src_gen_express.host_org_details"""
		self._enter('host_org_details', Query)
		return self
	@property
	def host_org_genus(self) -> 'EntitySrcGen':
		"""The genus of the organism that served as host for the production  of the entity.  Examples: Saccharomyces, Escherichia """
		self._enter('host_org_genus', Query)
		return self
	@property
	def host_org_species(self) -> 'EntitySrcGen':
		"""The species of the organism that served as host for the  production of the entity.  Examples: cerevisiae, coli """
		self._enter('host_org_species', Query)
		return self
	@property
	def pdbx_alt_source_flag(self) -> 'EntitySrcGen':
		"""This data item identifies cases in which an alternative source  modeled.  Allowable values: model, sample """
		self._enter('pdbx_alt_source_flag', Query)
		return self
	@property
	def pdbx_beg_seq_num(self) -> 'EntitySrcGen':
		"""The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('pdbx_beg_seq_num', Query)
		return self
	@property
	def pdbx_description(self) -> 'EntitySrcGen':
		"""Information on the source which is not given elsewhere."""
		self._enter('pdbx_description', Query)
		return self
	@property
	def pdbx_end_seq_num(self) -> 'EntitySrcGen':
		"""The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('pdbx_end_seq_num', Query)
		return self
	@property
	def pdbx_gene_src_atcc(self) -> 'EntitySrcGen':
		"""American Type Culture Collection tissue culture number.  Examples: 6051 """
		self._enter('pdbx_gene_src_atcc', Query)
		return self
	@property
	def pdbx_gene_src_cell(self) -> 'EntitySrcGen':
		"""Cell type.  Examples: ENDOTHELIAL """
		self._enter('pdbx_gene_src_cell', Query)
		return self
	@property
	def pdbx_gene_src_cell_line(self) -> 'EntitySrcGen':
		"""The specific line of cells.  Examples: HELA CELLS """
		self._enter('pdbx_gene_src_cell_line', Query)
		return self
	@property
	def pdbx_gene_src_cellular_location(self) -> 'EntitySrcGen':
		"""Identifies the location inside (or outside) the cell.  Examples: CYTOPLASM, NUCLEUS """
		self._enter('pdbx_gene_src_cellular_location', Query)
		return self
	@property
	def pdbx_gene_src_fragment(self) -> 'EntitySrcGen':
		"""A domain or fragment of the molecule.  Examples: CYTOPLASM, NUCLEUS """
		self._enter('pdbx_gene_src_fragment', Query)
		return self
	@property
	def pdbx_gene_src_gene(self) -> 'EntitySrcGen':
		"""Identifies the gene."""
		self._enter('pdbx_gene_src_gene', Query)
		return self
	@property
	def pdbx_gene_src_ncbi_taxonomy_id(self) -> 'EntitySrcGen':
		"""NCBI Taxonomy identifier for the gene source organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('pdbx_gene_src_ncbi_taxonomy_id', Query)
		return self
	@property
	def pdbx_gene_src_organ(self) -> 'EntitySrcGen':
		"""Organized group of tissues that carries on a specialized function.  Examples: KIDNEY, LIVER, PANCREAS """
		self._enter('pdbx_gene_src_organ', Query)
		return self
	@property
	def pdbx_gene_src_organelle(self) -> 'EntitySrcGen':
		"""Organized structure within cell.  Examples: MITOCHONDRIA """
		self._enter('pdbx_gene_src_organelle', Query)
		return self
	@property
	def pdbx_gene_src_scientific_name(self) -> 'EntitySrcGen':
		"""Scientific name of the organism.  Examples: Homo sapiens, Saccharomyces Cerevisiae """
		self._enter('pdbx_gene_src_scientific_name', Query)
		return self
	@property
	def pdbx_gene_src_variant(self) -> 'EntitySrcGen':
		"""Identifies the variant.  Examples: DELTAH1DELTATRP """
		self._enter('pdbx_gene_src_variant', Query)
		return self
	@property
	def pdbx_host_org_atcc(self) -> 'EntitySrcGen':
		"""Americal Tissue Culture Collection of the expression system. Where  full details of the protein production are available it would  be expected that this item  would be derived from  _entity_src_gen_express.host_org_culture_collection"""
		self._enter('pdbx_host_org_atcc', Query)
		return self
	@property
	def pdbx_host_org_cell(self) -> 'EntitySrcGen':
		"""Cell type from which the gene is derived. Where  entity.target_id is provided this should be derived from  details of the target.  Examples: ENDOTHELIAL """
		self._enter('pdbx_host_org_cell', Query)
		return self
	@property
	def pdbx_host_org_cell_line(self) -> 'EntitySrcGen':
		"""A specific line of cells used as the expression system. Where  full details of the protein production are available it would  be expected that this item would be derived from  entity_src_gen_express.host_org_cell_line  Examples: HELA """
		self._enter('pdbx_host_org_cell_line', Query)
		return self
	@property
	def pdbx_host_org_cellular_location(self) -> 'EntitySrcGen':
		"""Identifies the location inside (or outside) the cell which  expressed the molecule.  Examples: CYTOPLASM, NUCLEUS """
		self._enter('pdbx_host_org_cellular_location', Query)
		return self
	@property
	def pdbx_host_org_culture_collection(self) -> 'EntitySrcGen':
		"""Culture collection of the expression system. Where  full details of the protein production are available it would  be expected that this item  would be derived somehwere, but  exactly where is not clear."""
		self._enter('pdbx_host_org_culture_collection', Query)
		return self
	@property
	def pdbx_host_org_gene(self) -> 'EntitySrcGen':
		"""Specific gene which expressed the molecule.  Examples: HIV-1 POL, GLNS7, U1A (2-98, Y31H, Q36R) """
		self._enter('pdbx_host_org_gene', Query)
		return self
	@property
	def pdbx_host_org_ncbi_taxonomy_id(self) -> 'EntitySrcGen':
		"""NCBI Taxonomy identifier for the expression system organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('pdbx_host_org_ncbi_taxonomy_id', Query)
		return self
	@property
	def pdbx_host_org_organ(self) -> 'EntitySrcGen':
		"""Specific organ which expressed the molecule.  Examples: KIDNEY """
		self._enter('pdbx_host_org_organ', Query)
		return self
	@property
	def pdbx_host_org_organelle(self) -> 'EntitySrcGen':
		"""Specific organelle which expressed the molecule.  Examples: MITOCHONDRIA """
		self._enter('pdbx_host_org_organelle', Query)
		return self
	@property
	def pdbx_host_org_scientific_name(self) -> 'EntitySrcGen':
		"""The scientific name of the organism that served as host for the  production of the entity. Where full details of the protein  production are available it would be expected that this item  would be derived from _entity_src_gen_express.host_org_scientific_name  or via _entity_src_gen_express.host_org_tax_id  Examples: ESCHERICHIA COLI, SACCHAROMYCES CEREVISIAE """
		self._enter('pdbx_host_org_scientific_name', Query)
		return self
	@property
	def pdbx_host_org_strain(self) -> 'EntitySrcGen':
		"""The strain of the organism in which the entity was expressed.  Examples: AR120 """
		self._enter('pdbx_host_org_strain', Query)
		return self
	@property
	def pdbx_host_org_tissue(self) -> 'EntitySrcGen':
		"""The specific tissue which expressed the molecule. Where full details  of the protein production are available it would be expected that this  item would be derived from _entity_src_gen_express.host_org_tissue  Examples: heart, liver, eye lens """
		self._enter('pdbx_host_org_tissue', Query)
		return self
	@property
	def pdbx_host_org_tissue_fraction(self) -> 'EntitySrcGen':
		"""The fraction of the tissue which expressed the molecule.  Examples: mitochondria, nucleus, membrane """
		self._enter('pdbx_host_org_tissue_fraction', Query)
		return self
	@property
	def pdbx_host_org_variant(self) -> 'EntitySrcGen':
		"""Variant of the organism used as the expression system. Where  full details of the protein production are available it would  be expected that this item be derived from  entity_src_gen_express.host_org_variant or via  _entity_src_gen_express.host_org_tax_id  Examples: TRP-LAC, LAMBDA DE3 """
		self._enter('pdbx_host_org_variant', Query)
		return self
	@property
	def pdbx_host_org_vector(self) -> 'EntitySrcGen':
		"""Identifies the vector used. Where full details of the protein  production are available it would be expected that this item  would be derived from _entity_src_gen_clone.vector_name.  Examples: PBIT36, PET15B, PUC18 """
		self._enter('pdbx_host_org_vector', Query)
		return self
	@property
	def pdbx_host_org_vector_type(self) -> 'EntitySrcGen':
		"""Identifies the type of vector used (plasmid, virus, or cosmid).  Where full details of the protein production are available it  would be expected that this item would be derived from  _entity_src_gen_express.vector_type.  Examples: COSMID, PLASMID """
		self._enter('pdbx_host_org_vector_type', Query)
		return self
	@property
	def pdbx_seq_type(self) -> 'EntitySrcGen':
		"""This data item povides additional information about the sequence type.  Allowable values: Biological sequence, C-terminal tag, Linker, N-terminal tag """
		self._enter('pdbx_seq_type', Query)
		return self
	@property
	def pdbx_src_id(self) -> 'EntitySrcGen':
		"""This data item is an ordinal identifier for entity_src_gen data records."""
		self._enter('pdbx_src_id', Query)
		return self
	@property
	def plasmid_details(self) -> 'EntitySrcGen':
		"""A description of special aspects of the plasmid that produced the  entity in the host organism. Where full details of the protein  production are available it would be expected that this item  would be derived from _pdbx_construct.details of the construct  pointed to from _entity_src_gen_express.plasmid_id."""
		self._enter('plasmid_details', Query)
		return self
	@property
	def plasmid_name(self) -> 'EntitySrcGen':
		"""The name of the plasmid that produced the entity in the host  organism. Where full details of the protein production are available  it would be expected that this item would be derived from  _pdbx_construct.name of the construct pointed to from  _entity_src_gen_express.plasmid_id.  Examples: pET3C, pT123sab """
		self._enter('plasmid_name', Query)
		return self

class EntitySrcNat(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def common_name(self) -> 'EntitySrcNat':
		"""The common name of the organism from which the entity  was isolated.  Examples: man, yeast, bacteria """
		self._enter('common_name', Query)
		return self
	@property
	def details(self) -> 'EntitySrcNat':
		"""A description of special aspects of the organism from which the  entity was isolated."""
		self._enter('details', Query)
		return self
	@property
	def genus(self) -> 'EntitySrcNat':
		"""The genus of the organism from which the entity was isolated.  Examples: Homo, Saccharomyces, Escherichia """
		self._enter('genus', Query)
		return self
	@property
	def pdbx_alt_source_flag(self) -> 'EntitySrcNat':
		"""This data item identifies cases in which an alternative source  modeled.  Allowable values: model, sample """
		self._enter('pdbx_alt_source_flag', Query)
		return self
	@property
	def pdbx_atcc(self) -> 'EntitySrcNat':
		"""Americal Tissue Culture Collection number.  Examples: 6051 """
		self._enter('pdbx_atcc', Query)
		return self
	@property
	def pdbx_beg_seq_num(self) -> 'EntitySrcNat':
		"""The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('pdbx_beg_seq_num', Query)
		return self
	@property
	def pdbx_cell(self) -> 'EntitySrcNat':
		"""A particular cell type.  Examples: BHK-21 """
		self._enter('pdbx_cell', Query)
		return self
	@property
	def pdbx_cell_line(self) -> 'EntitySrcNat':
		"""The specific line of cells.  Examples: HELA """
		self._enter('pdbx_cell_line', Query)
		return self
	@property
	def pdbx_cellular_location(self) -> 'EntitySrcNat':
		"""Identifies the location inside (or outside) the cell."""
		self._enter('pdbx_cellular_location', Query)
		return self
	@property
	def pdbx_end_seq_num(self) -> 'EntitySrcNat':
		"""The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('pdbx_end_seq_num', Query)
		return self
	@property
	def pdbx_fragment(self) -> 'EntitySrcNat':
		"""A domain or fragment of the molecule."""
		self._enter('pdbx_fragment', Query)
		return self
	@property
	def pdbx_ncbi_taxonomy_id(self) -> 'EntitySrcNat':
		"""NCBI Taxonomy identifier for the source organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('pdbx_ncbi_taxonomy_id', Query)
		return self
	@property
	def pdbx_organ(self) -> 'EntitySrcNat':
		"""Organized group of tissues that carries on a specialized function.  Examples: KIDNEY """
		self._enter('pdbx_organ', Query)
		return self
	@property
	def pdbx_organelle(self) -> 'EntitySrcNat':
		"""Organized structure within cell.  Examples: MITOCHONDRIA """
		self._enter('pdbx_organelle', Query)
		return self
	@property
	def pdbx_organism_scientific(self) -> 'EntitySrcNat':
		"""Scientific name of the organism of the natural source.  Examples: Bos taurus, BOS TAURUS, SUS SCROFA, ASPERGILLUS ORYZAE """
		self._enter('pdbx_organism_scientific', Query)
		return self
	@property
	def pdbx_plasmid_details(self) -> 'EntitySrcNat':
		"""Details about the plasmid.  Examples: PLC28 DERIVATIVE """
		self._enter('pdbx_plasmid_details', Query)
		return self
	@property
	def pdbx_plasmid_name(self) -> 'EntitySrcNat':
		"""The plasmid containing the gene.  Examples: pB322 """
		self._enter('pdbx_plasmid_name', Query)
		return self
	@property
	def pdbx_secretion(self) -> 'EntitySrcNat':
		"""Identifies the secretion from which the molecule was isolated.  Examples: saliva, urine, venom """
		self._enter('pdbx_secretion', Query)
		return self
	@property
	def pdbx_src_id(self) -> 'EntitySrcNat':
		"""This data item is an ordinal identifier for entity_src_nat data records."""
		self._enter('pdbx_src_id', Query)
		return self
	@property
	def pdbx_variant(self) -> 'EntitySrcNat':
		"""Identifies the variant."""
		self._enter('pdbx_variant', Query)
		return self
	@property
	def species(self) -> 'EntitySrcNat':
		"""The species of the organism from which the entity was isolated.  Examples: sapiens, cerevisiae, coli """
		self._enter('species', Query)
		return self
	@property
	def strain(self) -> 'EntitySrcNat':
		"""The strain of the organism from which the entity was isolated.  Examples: DH5a, BMH 71-18 """
		self._enter('strain', Query)
		return self
	@property
	def tissue(self) -> 'EntitySrcNat':
		"""The tissue of the organism from which the entity was isolated.  Examples: heart, liver, eye lens """
		self._enter('tissue', Query)
		return self
	@property
	def tissue_fraction(self) -> 'EntitySrcNat':
		"""The subcellular fraction of the tissue of the organism from  which the entity was isolated.  Examples: mitochondria, nucleus, membrane """
		self._enter('tissue_fraction', Query)
		return self

class Entry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def id(self) -> 'Entry':
		"""The value of _entry.id identifies the data block.   Note that this item need not be a number; it can be any unique  identifier."""
		self._enter('id', Query)
		return self
	@property
	def ma_collection_id(self) -> 'Entry':
		"""An identifier for the model collection associated with the entry."""
		self._enter('ma_collection_id', Query)
		return self

class Exptl(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def crystals_number(self) -> 'Exptl':
		"""The total number of crystals used in the  measurement of  intensities."""
		self._enter('crystals_number', Query)
		return self
	@property
	def details(self) -> 'Exptl':
		"""Any special information about the experimental work prior to the  intensity measurement. See also _exptl_crystal.preparation."""
		self._enter('details', Query)
		return self
	@property
	def method(self) -> 'Exptl':
		"""The method used in the experiment.  Allowable values: ELECTRON CRYSTALLOGRAPHY, ELECTRON MICROSCOPY, EPR, FIBER DIFFRACTION, FLUORESCENCE TRANSFER, INFRARED SPECTROSCOPY, NEUTRON DIFFRACTION, POWDER DIFFRACTION, SOLID-STATE NMR, SOLUTION NMR, SOLUTION SCATTERING, THEORETICAL MODEL, X-RAY DIFFRACTION """
		self._enter('method', Query)
		return self
	@property
	def method_details(self) -> 'Exptl':
		"""A description of special aspects of the experimental method.  Examples: 29 structures, minimized average structure """
		self._enter('method_details', Query)
		return self

class ExptlCrystal(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def colour(self) -> 'ExptlCrystal':
		"""The colour of the crystal.  Examples: dark green """
		self._enter('colour', Query)
		return self
	@property
	def density_Matthews(self) -> 'ExptlCrystal':
		"""The density of the crystal, expressed as the ratio of the  volume of the asymmetric unit to the molecular mass of a  monomer of the structure, in units of angstroms^3^ per dalton.   Ref: Matthews, B. W. (1968). J. Mol. Biol. 33, 491-497.  Examples: null """
		self._enter('density_Matthews', Query)
		return self
	@property
	def density_meas(self) -> 'ExptlCrystal':
		"""Density values measured using standard chemical and physical  methods. The units are megagrams per cubic metre (grams per  cubic centimetre)."""
		self._enter('density_meas', Query)
		return self
	@property
	def density_percent_sol(self) -> 'ExptlCrystal':
		"""Density value P calculated from the crystal cell and contents,  expressed as per cent solvent.   P = 1 - (1.23 N MMass) / V   N     = the number of molecules in the unit cell  MMass = the molecular mass of each molecule (gm/mole)  V     = the volume of the unit cell (A^3^)  1.23  = a conversion factor evaluated as:           (0.74 cm^3^/g) (10^24^ A^3^/cm^3^)          --------------------------------------               (6.02*10^23^) molecules/mole           where 0.74 is an assumed value for the partial specific          volume of the molecule"""
		self._enter('density_percent_sol', Query)
		return self
	@property
	def description(self) -> 'ExptlCrystal':
		"""A description of the quality and habit of the crystal.  The crystal dimensions should not normally be reported here;  use instead the specific items in the EXPTL_CRYSTAL category  relating to size for the gross dimensions of the crystal and  data items in the EXPTL_CRYSTAL_FACE category to describe the  relationship between individual faces."""
		self._enter('description', Query)
		return self
	@property
	def id(self) -> 'ExptlCrystal':
		"""The value of _exptl_crystal.id must uniquely identify a record in  the EXPTL_CRYSTAL list.   Note that this item need not be a number; it can be any unique  identifier."""
		self._enter('id', Query)
		return self
	@property
	def pdbx_mosaicity(self) -> 'ExptlCrystal':
		"""Isotropic approximation of the distribution of mis-orientation angles specified in degrees of all the mosaic domain blocks in the crystal, represented as a standard deviation. Here, a mosaic block is a set of contiguous unit cells assumed to be perfectly aligned. Lower mosaicity indicates better ordered crystals. See for example:  Nave, C. (1998). Acta Cryst. D54, 848-853.  Note that many software packages estimate the mosaic rotation distribution differently and may combine several physical properties of the experiment into a single mosaic term. This term will help fit the modeled spots to the observed spots without necessarily being directly related to the physics of the crystal itself."""
		self._enter('pdbx_mosaicity', Query)
		return self
	@property
	def pdbx_mosaicity_esd(self) -> 'ExptlCrystal':
		"""The uncertainty in the mosaicity estimate for the crystal."""
		self._enter('pdbx_mosaicity_esd', Query)
		return self
	@property
	def preparation(self) -> 'ExptlCrystal':
		"""Details of crystal growth and preparation of the crystal (e.g.  mounting) prior to the intensity measurements.  Examples: mounted in an argon-filled quartz capillary """
		self._enter('preparation', Query)
		return self

class ExptlCrystalGrow(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def crystal_id(self) -> 'ExptlCrystalGrow':
		"""This data item is a pointer to _exptl_crystal.id in the  EXPTL_CRYSTAL category."""
		self._enter('crystal_id', Query)
		return self
	@property
	def details(self) -> 'ExptlCrystalGrow':
		"""A description of special aspects of the crystal growth.  Examples: Solution 2 was prepared as a well solution and                                   mixed. A droplet containing 2 \ml of solution                                   1 was delivered onto a cover slip; 2 \ml of                                   solution 2 was added to the droplet without                                   mixing., Crystal plates were originally stored at room                                   temperature for 1 week but no nucleation                                   occurred. They were then transferred to 4                                   degrees C, at which temperature well formed                                   single crystals grew in 2 days., The dependence on pH for successful crystal                                   growth is very sharp. At pH 7.4 only showers                                   of tiny crystals grew, at pH 7.5 well formed                                   single crystals grew, at pH 7.6 no                                   crystallization occurred at all. """
		self._enter('details', Query)
		return self
	@property
	def method(self) -> 'ExptlCrystalGrow':
		"""The method used to grow the crystals.  Examples: MICROBATCH, VAPOR DIFFUSION, HANGING DROP """
		self._enter('method', Query)
		return self
	@property
	def pH(self) -> 'ExptlCrystalGrow':
		"""The pH at which the crystal was grown. If more than one pH was  employed during the crystallization process, the final pH should  be noted here and the protocol involving multiple pH values  should be described in _exptl_crystal_grow.details.  Examples: null, null, null """
		self._enter('pH', Query)
		return self
	@property
	def pdbx_details(self) -> 'ExptlCrystalGrow':
		"""Text description of crystal growth procedure.  Examples: PEG 4000, potassium phosphate, magnesium chloride, cacodylate """
		self._enter('pdbx_details', Query)
		return self
	@property
	def pdbx_pH_range(self) -> 'ExptlCrystalGrow':
		"""The range of pH values at which the crystal was grown.   Used when  a point estimate of pH is not appropriate.  Examples: 5.6 - 6.4 """
		self._enter('pdbx_pH_range', Query)
		return self
	@property
	def temp(self) -> 'ExptlCrystalGrow':
		"""The temperature in kelvins at which the crystal was grown.  If more than one temperature was employed during the  crystallization process, the final temperature should be noted  here and the protocol  involving multiple temperatures should be  described in _exptl_crystal_grow.details."""
		self._enter('temp', Query)
		return self
	@property
	def temp_details(self) -> 'ExptlCrystalGrow':
		"""A description of special aspects of temperature control during  crystal growth."""
		self._enter('temp_details', Query)
		return self

class GeneName(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotProteinGene':
		"""Return to parent (RcsbUniprotProteinGene)"""
		return self._parent if self._parent else self
	@property
	def type(self) -> 'GeneName':
		"""Allowable values: PRIMARY, SYNONYM, ORDERED_LOCUS, ORF."""
		self._enter('type', Query)
		return self
	@property
	def value(self) -> 'GeneName':
		""""""
		self._enter('value', Query)
		return self

class GroupEntry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def group_provenance(self) -> 'GroupProvenance':
		"""Get provenance associated with this group."""
		return self._enter('group_provenance', GroupProvenance)
	@property
	def rcsb_group_accession_info(self) -> 'RcsbGroupAccessionInfo':
		""""""
		return self._enter('rcsb_group_accession_info', RcsbGroupAccessionInfo)
	@property
	def rcsb_group_container_identifiers(self) -> 'RcsbGroupContainerIdentifiers':
		""""""
		return self._enter('rcsb_group_container_identifiers', RcsbGroupContainerIdentifiers)
	@property
	def rcsb_group_info(self) -> 'RcsbGroupInfo':
		""""""
		return self._enter('rcsb_group_info', RcsbGroupInfo)
	@property
	def rcsb_group_related(self) -> 'RcsbGroupRelated':
		""""""
		return self._enter('rcsb_group_related', RcsbGroupRelated)
	@property
	def rcsb_group_statistics(self) -> 'RcsbGroupStatistics':
		""""""
		return self._enter('rcsb_group_statistics', RcsbGroupStatistics)
	@property
	def rcsb_id(self) -> 'GroupEntry':
		"""A unique textual identifier for a group"""
		self._enter('rcsb_id', Query)
		return self

class GroupMembersAlignmentScores(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment':
		"""Return to parent (RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment)"""
		return self._parent if self._parent else self
	@property
	def query_coverage(self) -> 'GroupMembersAlignmentScores':
		""""""
		self._enter('query_coverage', Query)
		return self
	@property
	def query_length(self) -> 'GroupMembersAlignmentScores':
		""""""
		self._enter('query_length', Query)
		return self
	@property
	def target_coverage(self) -> 'GroupMembersAlignmentScores':
		""""""
		self._enter('target_coverage', Query)
		return self
	@property
	def target_length(self) -> 'GroupMembersAlignmentScores':
		""""""
		self._enter('target_length', Query)
		return self

class GroupNonPolymerEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'Query':
		"""Return to parent (Query)"""
		return self._parent if self._parent else self
	@property
	def rcsb_group_accession_info(self) -> 'RcsbGroupAccessionInfo':
		""""""
		return self._enter('rcsb_group_accession_info', RcsbGroupAccessionInfo)
	@property
	def rcsb_group_container_identifiers(self) -> 'RcsbGroupContainerIdentifiers':
		""""""
		return self._enter('rcsb_group_container_identifiers', RcsbGroupContainerIdentifiers)
	@property
	def rcsb_group_info(self) -> 'RcsbGroupInfo':
		""""""
		return self._enter('rcsb_group_info', RcsbGroupInfo)
	@property
	def rcsb_group_related(self) -> 'RcsbGroupRelated':
		""""""
		return self._enter('rcsb_group_related', RcsbGroupRelated)
	@property
	def rcsb_group_statistics(self) -> 'RcsbGroupStatistics':
		""""""
		return self._enter('rcsb_group_statistics', RcsbGroupStatistics)
	@property
	def rcsb_id(self) -> 'GroupNonPolymerEntity':
		"""A unique textual identifier for a group"""
		self._enter('rcsb_id', Query)
		return self

class GroupPolymerEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def group_provenance(self) -> 'GroupProvenance':
		"""Get provenance associated with this group."""
		return self._enter('group_provenance', GroupProvenance)
	@property
	def rcsb_group_accession_info(self) -> 'RcsbGroupAccessionInfo':
		""""""
		return self._enter('rcsb_group_accession_info', RcsbGroupAccessionInfo)
	@property
	def rcsb_group_container_identifiers(self) -> 'RcsbGroupContainerIdentifiers':
		""""""
		return self._enter('rcsb_group_container_identifiers', RcsbGroupContainerIdentifiers)
	@property
	def rcsb_group_info(self) -> 'RcsbGroupInfo':
		""""""
		return self._enter('rcsb_group_info', RcsbGroupInfo)
	@property
	def rcsb_group_related(self) -> 'RcsbGroupRelated':
		""""""
		return self._enter('rcsb_group_related', RcsbGroupRelated)
	@property
	def rcsb_group_statistics(self) -> 'RcsbGroupStatistics':
		""""""
		return self._enter('rcsb_group_statistics', RcsbGroupStatistics)
	@property
	def rcsb_id(self) -> 'GroupPolymerEntity':
		"""A unique textual identifier for a group"""
		self._enter('rcsb_id', Query)
		return self
	@property
	def rcsb_polymer_entity_group_members_rankings(self) -> 'RcsbPolymerEntityGroupMembersRankings':
		""""""
		return self._enter('rcsb_polymer_entity_group_members_rankings', RcsbPolymerEntityGroupMembersRankings)
	@property
	def rcsb_polymer_entity_group_sequence_alignment(self) -> 'RcsbPolymerEntityGroupSequenceAlignment':
		""""""
		return self._enter('rcsb_polymer_entity_group_sequence_alignment', RcsbPolymerEntityGroupSequenceAlignment)

class GroupProvenance(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupEntry':
		"""Return to parent (GroupEntry)"""
		return self._parent if self._parent else self
	@property
	def rcsb_group_aggregation_method(self) -> 'RcsbGroupAggregationMethod':
		""""""
		return self._enter('rcsb_group_aggregation_method', RcsbGroupAggregationMethod)
	@property
	def rcsb_group_provenance_container_identifiers(self) -> 'RcsbGroupProvenanceContainerIdentifiers':
		""""""
		return self._enter('rcsb_group_provenance_container_identifiers', RcsbGroupProvenanceContainerIdentifiers)
	@property
	def rcsb_id(self) -> 'GroupProvenance':
		"""A unique textual identifier for a group provenance"""
		self._enter('rcsb_id', Query)
		return self

class IhmEntryCollectionMapping(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def collection_id(self) -> 'IhmEntryCollectionMapping':
		"""Identifier for the entry collection.   This data item is a pointer to _ihm_entry_collection.id in the   IHM_ENTRY_COLLECTION category."""
		self._enter('collection_id', Query)
		return self

class IhmExternalReferenceInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def associated_url(self) -> 'IhmExternalReferenceInfo':
		"""The Uniform Resource Locator (URL) corresponding to the external reference (DOI).   This URL should link to the corresponding downloadable file or archive and is provided   to enable automated software to download the referenced file or archive."""
		self._enter('associated_url', Query)
		return self
	@property
	def reference(self) -> 'IhmExternalReferenceInfo':
		"""The external reference or the Digital Object Identifier (DOI).  This field is not relevant for local files.  Examples: 10.5281/zenodo.46266 """
		self._enter('reference', Query)
		return self
	@property
	def reference_provider(self) -> 'IhmExternalReferenceInfo':
		"""The name of the reference provider.  Examples: Zenodo, Figshare, Crossref """
		self._enter('reference_provider', Query)
		return self

class InterfacePartnerFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""Return to parent (RcsbInterfacePartnerInterfacePartnerFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'InterfacePartnerFeatureAdditionalProperties':
		"""The additional property name.  Allowable values: TO_BE_DEFINED """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'InterfacePartnerFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class InterfacePartnerFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""Return to parent (RcsbInterfacePartnerInterfacePartnerFeature)"""
		return self._parent if self._parent else self
	@property
	def beg_seq_id(self) -> 'InterfacePartnerFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature begins."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'InterfacePartnerFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature ends."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def values(self) -> 'InterfacePartnerFeatureFeaturePositions':
		"""The value(s) of the feature over the monomer segment."""
		self._enter('values', Query)
		return self

class MaData(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def content_type(self) -> 'MaData':
		"""The type of data held in the dataset.  Allowable values: coevolution MSA, input structure, model coordinates, other, polymeric template library, reference database, spatial restraints, target, target-template alignment, template structure """
		self._enter('content_type', Query)
		return self
	@property
	def content_type_other_details(self) -> 'MaData':
		"""Details for other content types."""
		self._enter('content_type_other_details', Query)
		return self
	@property
	def id(self) -> 'MaData':
		"""A unique identifier for the data."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'MaData':
		"""An author-given name for the content held in the dataset.  Examples: NMR NOE Distances, Target Template Alignment, Coevolution Data """
		self._enter('name', Query)
		return self

class MethodDetails(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbGroupAggregationMethodMethod':
		"""Return to parent (RcsbGroupAggregationMethodMethod)"""
		return self._parent if self._parent else self
	@property
	def description(self) -> 'MethodDetails':
		"""A description of special aspects of the clustering process"""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'MethodDetails':
		"""Defines the name of the description associated with the clustering process"""
		self._enter('name', Query)
		return self
	@property
	def type(self) -> 'MethodDetails':
		"""Defines the type of the description associated with the clustering process"""
		self._enter('type', Query)
		return self
	@property
	def value(self) -> 'MethodDetails':
		"""Defines the value associated with the clustering process"""
		self._enter('value', Query)
		return self

class PdbxAuditRevisionCategory(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def category(self) -> 'PdbxAuditRevisionCategory':
		"""The category updated in the pdbx_audit_revision_category record.  Examples: audit_author, citation """
		self._enter('category', Query)
		return self
	@property
	def data_content_type(self) -> 'PdbxAuditRevisionCategory':
		"""The type of file that the pdbx_audit_revision_history record refers to.  Allowable values: Additional map, Chemical component, EM metadata, FSC, Half map, Image, Mask, NMR restraints, NMR shifts, Primary map, Structure factors, Structure model """
		self._enter('data_content_type', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxAuditRevisionCategory':
		"""A unique identifier for the pdbx_audit_revision_category record."""
		self._enter('ordinal', Query)
		return self
	@property
	def revision_ordinal(self) -> 'PdbxAuditRevisionCategory':
		"""A pointer to  _pdbx_audit_revision_history.ordinal"""
		self._enter('revision_ordinal', Query)
		return self

class PdbxAuditRevisionDetails(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def data_content_type(self) -> 'PdbxAuditRevisionDetails':
		"""The type of file that the pdbx_audit_revision_history record refers to.  Allowable values: Additional map, Chemical component, EM metadata, FSC, Half map, Image, Mask, NMR restraints, NMR shifts, Primary map, Structure factors, Structure model """
		self._enter('data_content_type', Query)
		return self
	@property
	def description(self) -> 'PdbxAuditRevisionDetails':
		"""Additional details describing the revision."""
		self._enter('description', Query)
		return self
	@property
	def details(self) -> 'PdbxAuditRevisionDetails':
		"""Further details describing the revision."""
		self._enter('details', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxAuditRevisionDetails':
		"""A unique identifier for the pdbx_audit_revision_details record."""
		self._enter('ordinal', Query)
		return self
	@property
	def provider(self) -> 'PdbxAuditRevisionDetails':
		"""The provider of the revision.  Allowable values: author, repository """
		self._enter('provider', Query)
		return self
	@property
	def revision_ordinal(self) -> 'PdbxAuditRevisionDetails':
		"""A pointer to  _pdbx_audit_revision_history.ordinal"""
		self._enter('revision_ordinal', Query)
		return self
	@property
	def type(self) -> 'PdbxAuditRevisionDetails':
		"""A type classification of the revision  Allowable values: Coordinate replacement, Data added, Data removed, Data updated, Initial release, Obsolete, Remediation """
		self._enter('type', Query)
		return self

class PdbxAuditRevisionGroup(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def data_content_type(self) -> 'PdbxAuditRevisionGroup':
		"""The type of file that the pdbx_audit_revision_history record refers to.  Allowable values: Additional map, Chemical component, EM metadata, FSC, Half map, Image, Mask, NMR restraints, NMR shifts, Primary map, Structure factors, Structure model """
		self._enter('data_content_type', Query)
		return self
	@property
	def group(self) -> 'PdbxAuditRevisionGroup':
		"""The collection of categories updated with this revision.  Allowable values: Advisory, Atomic model, Author supporting evidence, Data collection, Data processing, Database references, Derived calculations, Experimental data, Experimental preparation, Experimental summary, Non-polymer description, Other, Polymer sequence, Refinement description, Source and taxonomy, Structure summary, Version format compliance """
		self._enter('group', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxAuditRevisionGroup':
		"""A unique identifier for the pdbx_audit_revision_group record."""
		self._enter('ordinal', Query)
		return self
	@property
	def revision_ordinal(self) -> 'PdbxAuditRevisionGroup':
		"""A pointer to  _pdbx_audit_revision_history.ordinal"""
		self._enter('revision_ordinal', Query)
		return self

class PdbxAuditRevisionHistory(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def data_content_type(self) -> 'PdbxAuditRevisionHistory':
		"""The type of file that the pdbx_audit_revision_history record refers to.  Allowable values: Additional map, Chemical component, EM metadata, FSC, Half map, Image, Mask, NMR restraints, NMR shifts, Primary map, Structure factors, Structure model """
		self._enter('data_content_type', Query)
		return self
	@property
	def major_revision(self) -> 'PdbxAuditRevisionHistory':
		"""The major version number of deposition release."""
		self._enter('major_revision', Query)
		return self
	@property
	def minor_revision(self) -> 'PdbxAuditRevisionHistory':
		"""The minor version number of deposition release."""
		self._enter('minor_revision', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxAuditRevisionHistory':
		"""A unique identifier for the pdbx_audit_revision_history record."""
		self._enter('ordinal', Query)
		return self
	@property
	def revision_date(self) -> 'PdbxAuditRevisionHistory':
		"""The release date of the revision  Examples: 2017-03-08 """
		self._enter('revision_date', Query)
		return self

class PdbxAuditRevisionItem(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def data_content_type(self) -> 'PdbxAuditRevisionItem':
		"""The type of file that the pdbx_audit_revision_history record refers to.  Allowable values: Additional map, Chemical component, EM metadata, FSC, Half map, Image, Mask, NMR restraints, NMR shifts, Primary map, Structure factors, Structure model """
		self._enter('data_content_type', Query)
		return self
	@property
	def item(self) -> 'PdbxAuditRevisionItem':
		"""A high level explanation the author has provided for submitting a revision.  Examples: _atom_site.type_symbol """
		self._enter('item', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxAuditRevisionItem':
		"""A unique identifier for the pdbx_audit_revision_item record."""
		self._enter('ordinal', Query)
		return self
	@property
	def revision_ordinal(self) -> 'PdbxAuditRevisionItem':
		"""A pointer to  _pdbx_audit_revision_history.ordinal"""
		self._enter('revision_ordinal', Query)
		return self

class PdbxAuditSupport(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def country(self) -> 'PdbxAuditSupport':
		"""The country/region providing the funding support for the entry.  Funding information is optionally provided for entries after June 2016."""
		self._enter('country', Query)
		return self
	@property
	def funding_organization(self) -> 'PdbxAuditSupport':
		"""The name of the organization providing funding support for the  entry. Funding information is optionally provided for entries  after June 2016.  Examples: National Institutes of Health, Wellcome Trust, National Institutes of Health/National Institute of General Medical Sciences """
		self._enter('funding_organization', Query)
		return self
	@property
	def grant_number(self) -> 'PdbxAuditSupport':
		"""The grant number associated with this source of support."""
		self._enter('grant_number', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxAuditSupport':
		"""A unique sequential integer identifier for each source of support for this entry."""
		self._enter('ordinal', Query)
		return self

class PdbxChemCompAudit(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def action_type(self) -> 'PdbxChemCompAudit':
		"""The action associated with this audit record.  Allowable values: Create component, Initial release, Modify PCM, Modify aromatic_flag, Modify atom id, Modify backbone, Modify charge, Modify component atom id, Modify component comp_id, Modify coordinates, Modify descriptor, Modify formal charge, Modify formula, Modify identifier, Modify internal type, Modify leaving atom flag, Modify linking type, Modify model coordinates code, Modify name, Modify one letter code, Modify parent residue, Modify processing site, Modify subcomponent list, Modify synonyms, Modify value order, Obsolete component, Other modification """
		self._enter('action_type', Query)
		return self
	@property
	def comp_id(self) -> 'PdbxChemCompAudit':
		"""This data item is a pointer to _chem_comp.id in the CHEM_COMP  category."""
		self._enter('comp_id', Query)
		return self
	@property
	def date(self) -> 'PdbxChemCompAudit':
		"""The date associated with this audit record."""
		self._enter('date', Query)
		return self
	@property
	def details(self) -> 'PdbxChemCompAudit':
		"""Additional details decribing this change.  Examples: Added C14 as a leaving atom. """
		self._enter('details', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxChemCompAudit':
		"""This data item is an ordinal index for the  PDBX_CHEM_COMP_AUDIT category."""
		self._enter('ordinal', Query)
		return self

class PdbxChemCompDescriptor(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'PdbxChemCompDescriptor':
		"""This data item is a pointer to _chem_comp.id in the CHEM_COMP  category."""
		self._enter('comp_id', Query)
		return self
	@property
	def descriptor(self) -> 'PdbxChemCompDescriptor':
		"""This data item contains the descriptor value for this  component."""
		self._enter('descriptor', Query)
		return self
	@property
	def program(self) -> 'PdbxChemCompDescriptor':
		"""This data item contains the name of the program  or library used to compute the descriptor.  Examples: OPENEYE, CACTVS, DAYLIGHT, OTHER """
		self._enter('program', Query)
		return self
	@property
	def program_version(self) -> 'PdbxChemCompDescriptor':
		"""This data item contains the version of the program  or library used to compute the descriptor."""
		self._enter('program_version', Query)
		return self
	@property
	def type(self) -> 'PdbxChemCompDescriptor':
		"""This data item contains the descriptor type.  Allowable values: InChI, InChIKey, InChI_CHARGE, InChI_FIXEDH, InChI_ISOTOPE, InChI_MAIN, InChI_MAIN_CONNECT, InChI_MAIN_FORMULA, InChI_MAIN_HATOM, InChI_RECONNECT, InChI_STEREO, SMILES, SMILES_CANNONICAL, SMILES_CANONICAL """
		self._enter('type', Query)
		return self

class PdbxChemCompFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'PdbxChemCompFeature':
		"""The component identifier for this feature.  Examples: ABC, ATP """
		self._enter('comp_id', Query)
		return self
	@property
	def source(self) -> 'PdbxChemCompFeature':
		"""The information source for the component feature.  Examples: PDB, CHEBI, DRUGBANK, PUBCHEM """
		self._enter('source', Query)
		return self
	@property
	def type(self) -> 'PdbxChemCompFeature':
		"""The component feature type.  Allowable values: CARBOHYDRATE ANOMER, CARBOHYDRATE ISOMER, CARBOHYDRATE PRIMARY CARBONYL GROUP, CARBOHYDRATE RING """
		self._enter('type', Query)
		return self
	@property
	def value(self) -> 'PdbxChemCompFeature':
		"""The component feature value."""
		self._enter('value', Query)
		return self

class PdbxChemCompIdentifier(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'PdbxChemCompIdentifier':
		"""This data item is a pointer to _chem_comp.id in the CHEM_COMP  category."""
		self._enter('comp_id', Query)
		return self
	@property
	def identifier(self) -> 'PdbxChemCompIdentifier':
		"""This data item contains the identifier value for this  component."""
		self._enter('identifier', Query)
		return self
	@property
	def program(self) -> 'PdbxChemCompIdentifier':
		"""This data item contains the name of the program  or library used to compute the identifier.  Examples: OPENEYE, DAYLIGHT, ACD, AUTONOM, PUBCHEM_CID, PUBCHEM_SID, OTHER, NONE """
		self._enter('program', Query)
		return self
	@property
	def program_version(self) -> 'PdbxChemCompIdentifier':
		"""This data item contains the version of the program  or library used to compute the identifier."""
		self._enter('program_version', Query)
		return self
	@property
	def type(self) -> 'PdbxChemCompIdentifier':
		"""This data item contains the identifier type.  Allowable values: CAS REGISTRY NUMBER, COMMON NAME, CONDENSED IUPAC CARB SYMBOL, CONDENSED IUPAC CARBOHYDRATE SYMBOL, IUPAC CARB SYMBOL, IUPAC CARBOHYDRATE SYMBOL, MDL Identifier, PUBCHEM Identifier, SNFG CARB SYMBOL, SNFG CARBOHYDRATE SYMBOL, SYNONYM, SYSTEMATIC NAME """
		self._enter('type', Query)
		return self

class PdbxDatabasePDBObsSpr(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def date(self) -> 'PdbxDatabasePDBObsSpr':
		"""The date of replacement.  Examples: 1997-03-30 """
		self._enter('date', Query)
		return self
	@property
	def details(self) -> 'PdbxDatabasePDBObsSpr':
		"""Details related to the replaced or replacing entry."""
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'PdbxDatabasePDBObsSpr':
		"""Identifier for the type of obsolete entry to be added to this entry.  Allowable values: OBSLTE, SPRSDE """
		self._enter('id', Query)
		return self
	@property
	def pdb_id(self) -> 'PdbxDatabasePDBObsSpr':
		"""The new PDB identifier for the replaced entry.  Examples: 2ABC """
		self._enter('pdb_id', Query)
		return self
	@property
	def replace_pdb_id(self) -> 'PdbxDatabasePDBObsSpr':
		"""The PDB identifier for the replaced (OLD) entry/entries.  Examples: 3ABC """
		self._enter('replace_pdb_id', Query)
		return self

class PdbxDatabaseRelated(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def content_type(self) -> 'PdbxDatabaseRelated':
		"""The identifying content type of the related entry.  Allowable values: associated EM volume, associated NMR restraints, associated SAS data, associated structure factors, complete structure, consensus EM volume, derivative structure, ensemble, focused EM volume, minimized average structure, native structure, other, other EM volume, protein target sequence and/or protocol data, re-refinement, representative structure, split, unspecified """
		self._enter('content_type', Query)
		return self
	@property
	def db_id(self) -> 'PdbxDatabaseRelated':
		"""The identifying code in the related database.  Examples: 1ABC, BDL001 """
		self._enter('db_id', Query)
		return self
	@property
	def db_name(self) -> 'PdbxDatabaseRelated':
		"""The name of the database containing the related entry.  Allowable values: BIOISIS, BMCD, BMRB, EMDB, NDB, PDB, PDB-Dev, SASBDB, TargetDB, TargetTrack """
		self._enter('db_name', Query)
		return self
	@property
	def details(self) -> 'PdbxDatabaseRelated':
		"""A description of the related entry.  Examples: 1ABC contains the same protein complexed with Netropsin. """
		self._enter('details', Query)
		return self

class PdbxDatabaseStatus(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def SG_entry(self) -> 'PdbxDatabaseStatus':
		"""This code indicates whether the entry belongs to  Structural Genomics Project.  Allowable values: N, Y """
		self._enter('SG_entry', Query)
		return self
	@property
	def deposit_site(self) -> 'PdbxDatabaseStatus':
		"""The site where the file was deposited.  Allowable values: BMRB, BNL, NDB, PDBC, PDBE, PDBJ, RCSB """
		self._enter('deposit_site', Query)
		return self
	@property
	def methods_development_category(self) -> 'PdbxDatabaseStatus':
		"""The methods development category in which this  entry has been placed.  Allowable values: CAPRI, CASD-NMR, CASP, D3R, FoldIt, GPCR Dock, RNA-Puzzles """
		self._enter('methods_development_category', Query)
		return self
	@property
	def pdb_format_compatible(self) -> 'PdbxDatabaseStatus':
		"""A flag indicating that the entry is compatible with the PDB format.   A value of 'N' indicates that the no PDB format data file is  corresponding to this entry is available in the PDB archive.  Allowable values: N, Y """
		self._enter('pdb_format_compatible', Query)
		return self
	@property
	def process_site(self) -> 'PdbxDatabaseStatus':
		"""The site where the file was deposited.  Allowable values: BNL, NDB, PDBC, PDBE, PDBJ, RCSB """
		self._enter('process_site', Query)
		return self
	@property
	def recvd_initial_deposition_date(self) -> 'PdbxDatabaseStatus':
		"""The date of initial deposition.  (The first message for  deposition has been received.)  Examples: 1983-02-21 """
		self._enter('recvd_initial_deposition_date', Query)
		return self
	@property
	def status_code(self) -> 'PdbxDatabaseStatus':
		"""Code for status of file.  Allowable values: AUCO, AUTH, BIB, DEL, HOLD, HPUB, OBS, POLC, PROC, REFI, REL, REPL, REV, RMVD, TRSF, UPD, WAIT, WDRN """
		self._enter('status_code', Query)
		return self
	@property
	def status_code_cs(self) -> 'PdbxDatabaseStatus':
		"""Code for status of chemical shift data file.  Allowable values: AUCO, AUTH, HOLD, HPUB, OBS, POLC, PROC, REL, REPL, RMVD, WAIT, WDRN """
		self._enter('status_code_cs', Query)
		return self
	@property
	def status_code_mr(self) -> 'PdbxDatabaseStatus':
		"""Code for status of NMR constraints file.  Allowable values: AUCO, AUTH, HOLD, HPUB, OBS, POLC, PROC, REL, REPL, RMVD, WAIT, WDRN """
		self._enter('status_code_mr', Query)
		return self
	@property
	def status_code_sf(self) -> 'PdbxDatabaseStatus':
		"""Code for status of structure factor file.  Allowable values: AUTH, HOLD, HPUB, OBS, POLC, PROC, REL, REPL, RMVD, WAIT, WDRN """
		self._enter('status_code_sf', Query)
		return self

class PdbxDepositGroup(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def group_description(self) -> 'PdbxDepositGroup':
		"""A description of the contents of entries in the collection."""
		self._enter('group_description', Query)
		return self
	@property
	def group_id(self) -> 'PdbxDepositGroup':
		"""A unique identifier for a group of entries deposited as a collection.  Examples: G_1002119, G_1002043 """
		self._enter('group_id', Query)
		return self
	@property
	def group_title(self) -> 'PdbxDepositGroup':
		"""A title to describe the group of entries deposited in the collection."""
		self._enter('group_title', Query)
		return self
	@property
	def group_type(self) -> 'PdbxDepositGroup':
		"""Text to describe a grouping of entries in multiple collections  Allowable values: changed state, ground state, undefined """
		self._enter('group_type', Query)
		return self

class PdbxEntityBranch(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def rcsb_branched_component_count(self) -> 'PdbxEntityBranch':
		"""Number of constituent chemical components in the branched entity."""
		self._enter('rcsb_branched_component_count', Query)
		return self
	@property
	def type(self) -> 'PdbxEntityBranch':
		"""The type of this branched oligosaccharide.  Allowable values: oligosaccharide """
		self._enter('type', Query)
		return self

class PdbxEntityBranchDescriptor(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def descriptor(self) -> 'PdbxEntityBranchDescriptor':
		"""This data item contains the descriptor value for this  entity."""
		self._enter('descriptor', Query)
		return self
	@property
	def program(self) -> 'PdbxEntityBranchDescriptor':
		"""This data item contains the name of the program  or library used to compute the descriptor.  Examples: PDB-CARE, OTHER, GEMS """
		self._enter('program', Query)
		return self
	@property
	def program_version(self) -> 'PdbxEntityBranchDescriptor':
		"""This data item contains the version of the program  or library used to compute the descriptor."""
		self._enter('program_version', Query)
		return self
	@property
	def type(self) -> 'PdbxEntityBranchDescriptor':
		"""This data item contains the descriptor type.  Allowable values: Glycam Condensed Core Sequence, Glycam Condensed Sequence, LINUCS, WURCS """
		self._enter('type', Query)
		return self

class PdbxEntityNonpoly(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'PdbxEntityNonpoly':
		"""This data item is a pointer to _chem_comp.id in the CHEM_COMP category."""
		self._enter('comp_id', Query)
		return self
	@property
	def entity_id(self) -> 'PdbxEntityNonpoly':
		"""This data item is a pointer to _entity.id in the ENTITY category."""
		self._enter('entity_id', Query)
		return self
	@property
	def name(self) -> 'PdbxEntityNonpoly':
		"""A name for the non-polymer entity"""
		self._enter('name', Query)
		return self
	@property
	def rcsb_prd_id(self) -> 'PdbxEntityNonpoly':
		"""For non-polymer BIRD molecules the BIRD identifier for the entity."""
		self._enter('rcsb_prd_id', Query)
		return self

class PdbxEntitySrcSyn(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'PdbxEntitySrcSyn':
		"""A description of special aspects of the source for the  synthetic entity.  Examples: This sequence occurs naturally in humans. """
		self._enter('details', Query)
		return self
	@property
	def ncbi_taxonomy_id(self) -> 'PdbxEntitySrcSyn':
		"""NCBI Taxonomy identifier of the organism from which the sequence of  the synthetic entity was derived.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('ncbi_taxonomy_id', Query)
		return self
	@property
	def organism_common_name(self) -> 'PdbxEntitySrcSyn':
		"""The common name of the organism from which the sequence of  the synthetic entity was derived.  Examples: house mouse """
		self._enter('organism_common_name', Query)
		return self
	@property
	def organism_scientific(self) -> 'PdbxEntitySrcSyn':
		"""The scientific name of the organism from which the sequence of  the synthetic entity was derived.  Examples: synthetic construct, Mus musculus """
		self._enter('organism_scientific', Query)
		return self
	@property
	def pdbx_alt_source_flag(self) -> 'PdbxEntitySrcSyn':
		"""This data item identifies cases in which an alternative source  modeled.  Allowable values: model, sample """
		self._enter('pdbx_alt_source_flag', Query)
		return self
	@property
	def pdbx_beg_seq_num(self) -> 'PdbxEntitySrcSyn':
		"""The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('pdbx_beg_seq_num', Query)
		return self
	@property
	def pdbx_end_seq_num(self) -> 'PdbxEntitySrcSyn':
		"""The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('pdbx_end_seq_num', Query)
		return self
	@property
	def pdbx_src_id(self) -> 'PdbxEntitySrcSyn':
		"""This data item is an ordinal identifier for pdbx_entity_src_syn data records."""
		self._enter('pdbx_src_id', Query)
		return self

class PdbxFamilyPrdAudit(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def action_type(self) -> 'PdbxFamilyPrdAudit':
		"""The action associated with this audit record.  Allowable values: Add PRD, Create family, Initial release, Modify annotation, Modify citation, Modify family classification, Modify family name, Modify feature, Modify molecule details, Modify related structures, Modify sequence, Modify synonyms, Obsolete family, Obsolete familyt, Other modification, Remove PRD """
		self._enter('action_type', Query)
		return self
	@property
	def annotator(self) -> 'PdbxFamilyPrdAudit':
		"""The initials of the annotator creating of modifying the family.  Examples: JO, SJ, KB """
		self._enter('annotator', Query)
		return self
	@property
	def date(self) -> 'PdbxFamilyPrdAudit':
		"""The date associated with this audit record."""
		self._enter('date', Query)
		return self
	@property
	def details(self) -> 'PdbxFamilyPrdAudit':
		"""Additional details decribing this change.  Examples: Revise molecule sequence. """
		self._enter('details', Query)
		return self
	@property
	def family_prd_id(self) -> 'PdbxFamilyPrdAudit':
		"""This data item is a pointer to _pdbx_reference_molecule_family.family_prd_id in the 	       pdbx_reference_molecule category."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def processing_site(self) -> 'PdbxFamilyPrdAudit':
		"""An identifier for the wwPDB site creating or modifying the family.  Examples: RCSB, PDBE, PDBJ, BMRB, PDBC """
		self._enter('processing_site', Query)
		return self

class PdbxInitialRefinementModel(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def accession_code(self) -> 'PdbxInitialRefinementModel':
		"""This item identifies an accession code of the resource where the initial model  is used"""
		self._enter('accession_code', Query)
		return self
	@property
	def details(self) -> 'PdbxInitialRefinementModel':
		"""A description of special aspects of the initial model"""
		self._enter('details', Query)
		return self
	@property
	def entity_id_list(self) -> 'PdbxInitialRefinementModel':
		"""A comma separated list of entities reflecting the initial model used for refinement"""
		self._enter('entity_id_list', Query)
		return self
	@property
	def id(self) -> 'PdbxInitialRefinementModel':
		"""A unique identifier for the starting model record."""
		self._enter('id', Query)
		return self
	@property
	def source_name(self) -> 'PdbxInitialRefinementModel':
		"""This item identifies the resource of initial model used for refinement  Allowable values: AlphaFold, ITasser, InsightII, ModelArchive, Modeller, Other, PDB, PDB-Dev, PHYRE, Robetta, RoseTTAFold, SwissModel """
		self._enter('source_name', Query)
		return self
	@property
	def type(self) -> 'PdbxInitialRefinementModel':
		"""This item describes the type of the initial model was generated  Allowable values: experimental model, in silico model, integrative model, other """
		self._enter('type', Query)
		return self

class PdbxMoleculeFeatures(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def class_(self) -> 'PdbxMoleculeFeatures':
		"""Broadly defines the function of the molecule.  Allowable values: Antagonist, Anthelmintic, Antibiotic, Antibiotic, Anthelmintic, Antibiotic, Antimicrobial, Antibiotic, Antineoplastic, Anticancer, Anticoagulant, Anticoagulant, Antithrombotic, Antifungal, Antigen, Antiinflammatory, Antimicrobial, Antimicrobial, Antiparasitic, Antibiotic, Antimicrobial, Antiretroviral, Antimicrobial, Antitumor, Antineoplastic, Antiparasitic, Antiretroviral, Antithrombotic, Antitumor, Antiviral, CASPASE inhibitor, Chaperone binding, Drug delivery, Enzyme inhibitor, Glycan component, Growth factor, Immunosuppressant, Inducer, Inhibitor, Lantibiotic, Metabolism, Metal transport, Nutrient, Oxidation-reduction, Protein binding, Receptor, Substrate analog, Synthetic opioid, Thrombin inhibitor, Thrombin inhibitor, Trypsin inhibitor, Toxin, Transition state mimetic, Transport activator, Trypsin inhibitor, Unknown, Water retention """
		self._enter('class_', Query)
		return self
	@property
	def details(self) -> 'PdbxMoleculeFeatures':
		"""Additional details describing the molecule."""
		self._enter('details', Query)
		return self
	@property
	def name(self) -> 'PdbxMoleculeFeatures':
		"""A name of the molecule.  Examples: thiostrepton """
		self._enter('name', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxMoleculeFeatures':
		"""The value of _pdbx_molecule_features.prd_id is the accession code for this  reference molecule."""
		self._enter('prd_id', Query)
		return self
	@property
	def type(self) -> 'PdbxMoleculeFeatures':
		"""Defines the structural classification of the molecule.  Allowable values: Amino acid, Aminoglycoside, Ansamycin, Anthracycline, Anthraquinone, Chalkophore, Chalkophore, Polypeptide, Chromophore, Cyclic depsipeptide, Cyclic lipopeptide, Cyclic peptide, Glycopeptide, Heterocyclic, Imino sugar, Keto acid, Lipoglycopeptide, Lipopeptide, Macrolide, Non-polymer, Nucleoside, Oligopeptide, Oligosaccharide, Peptaibol, Peptide-like, Polycyclic, Polypeptide, Polysaccharide, Quinolone, Siderophore, Thiolactone, Thiopeptide, Unknown """
		self._enter('type', Query)
		return self

class PdbxNmrDetails(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def text(self) -> 'PdbxNmrDetails':
		"""Additional details describing the NMR experiment.  Examples: This structure was determined using standard 2D homonuclear techniques., The structure was determined using triple-resonance NMR spectroscopy. """
		self._enter('text', Query)
		return self

class PdbxNmrEnsemble(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def average_constraint_violations_per_residue(self) -> 'PdbxNmrEnsemble':
		"""The average number of constraint violations on a per residue basis for  the ensemble.  Examples: null """
		self._enter('average_constraint_violations_per_residue', Query)
		return self
	@property
	def average_constraints_per_residue(self) -> 'PdbxNmrEnsemble':
		"""The average number of constraints per residue for the ensemble  Examples: null """
		self._enter('average_constraints_per_residue', Query)
		return self
	@property
	def average_distance_constraint_violation(self) -> 'PdbxNmrEnsemble':
		"""The average distance restraint violation for the ensemble.  Examples: null """
		self._enter('average_distance_constraint_violation', Query)
		return self
	@property
	def average_torsion_angle_constraint_violation(self) -> 'PdbxNmrEnsemble':
		"""The average torsion angle constraint violation for the ensemble.  Examples: null """
		self._enter('average_torsion_angle_constraint_violation', Query)
		return self
	@property
	def conformer_selection_criteria(self) -> 'PdbxNmrEnsemble':
		"""By highlighting the appropriate choice(s), describe how the submitted conformer (models) were selected.  Examples: structures with the lowest energy, structures with the least restraint violations, structures with acceptable covalent geometry, structures with favorable non-bond energy, target function, back calculated data agree with experimental NOESY spectrum, all calculated structures submitted, The submitted conformer models are the 25 structures with the lowest     energy., The submitted conformer models are those with the fewest number of     constraint violations. """
		self._enter('conformer_selection_criteria', Query)
		return self
	@property
	def conformers_calculated_total_number(self) -> 'PdbxNmrEnsemble':
		"""The total number of conformer (models) that were calculated in the final round."""
		self._enter('conformers_calculated_total_number', Query)
		return self
	@property
	def conformers_submitted_total_number(self) -> 'PdbxNmrEnsemble':
		"""The number of conformer (models) that are submitted for the ensemble."""
		self._enter('conformers_submitted_total_number', Query)
		return self
	@property
	def distance_constraint_violation_method(self) -> 'PdbxNmrEnsemble':
		"""Describe the method used to calculate the distance constraint violation statistics,  i.e. are they calculated over all the distance constraints or calculated for  violations only?  Examples: Statistics were calculated over all of the distance constraints., Statistics were calculated for violations only """
		self._enter('distance_constraint_violation_method', Query)
		return self
	@property
	def maximum_distance_constraint_violation(self) -> 'PdbxNmrEnsemble':
		"""The maximum distance constraint violation for the ensemble.  Examples: null """
		self._enter('maximum_distance_constraint_violation', Query)
		return self
	@property
	def maximum_lower_distance_constraint_violation(self) -> 'PdbxNmrEnsemble':
		"""The maximum lower distance constraint violation for the ensemble.  Examples: null """
		self._enter('maximum_lower_distance_constraint_violation', Query)
		return self
	@property
	def maximum_torsion_angle_constraint_violation(self) -> 'PdbxNmrEnsemble':
		"""The maximum torsion angle constraint violation for the ensemble."""
		self._enter('maximum_torsion_angle_constraint_violation', Query)
		return self
	@property
	def maximum_upper_distance_constraint_violation(self) -> 'PdbxNmrEnsemble':
		"""The maximum upper distance constraint violation for the ensemble.  Examples: null """
		self._enter('maximum_upper_distance_constraint_violation', Query)
		return self
	@property
	def representative_conformer(self) -> 'PdbxNmrEnsemble':
		"""The number of the conformer identified as most representative."""
		self._enter('representative_conformer', Query)
		return self
	@property
	def torsion_angle_constraint_violation_method(self) -> 'PdbxNmrEnsemble':
		"""This item describes the method used to calculate the torsion angle constraint violation statistics. i.e. are the entered values based on all torsion angle or calculated for violations only?  Examples: Statistics were calculated over all the torsion angle constraints., Statistics were calculated for torsion angle constraints violations only. """
		self._enter('torsion_angle_constraint_violation_method', Query)
		return self

class PdbxNmrExptl(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def conditions_id(self) -> 'PdbxNmrExptl':
		"""The number to identify the set of sample conditions.  Examples: 1, 2, 3 """
		self._enter('conditions_id', Query)
		return self
	@property
	def experiment_id(self) -> 'PdbxNmrExptl':
		"""A numerical ID for each experiment.  Examples: 1, 2, 3 """
		self._enter('experiment_id', Query)
		return self
	@property
	def sample_state(self) -> 'PdbxNmrExptl':
		"""Physical state of the sample either anisotropic or isotropic.  Allowable values: anisotropic, isotropic """
		self._enter('sample_state', Query)
		return self
	@property
	def solution_id(self) -> 'PdbxNmrExptl':
		"""The solution_id from the Experimental Sample to identify the sample  that these conditions refer to.   [Remember to save the entries here before returning to the   Experimental Sample form]  Examples: 1, 2, 3 """
		self._enter('solution_id', Query)
		return self
	@property
	def spectrometer_id(self) -> 'PdbxNmrExptl':
		"""Pointer to '_pdbx_nmr_spectrometer.spectrometer_id'"""
		self._enter('spectrometer_id', Query)
		return self
	@property
	def type(self) -> 'PdbxNmrExptl':
		"""The type of NMR experiment.  Examples: 2D NOESY, 3D_15N-separated_NOESY, 3D_13C-separated_NOESY, 4D_13C-separated_NOESY, 4D_13C/15N-separated_NOESY, 3D_15N-separated_ROESY, 3D_13C-separated_ROESY, HNCA-J, HNHA, DQF-COSY, P-COSY, PE-COSY, E-COSY """
		self._enter('type', Query)
		return self

class PdbxNmrExptlSampleConditions(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def conditions_id(self) -> 'PdbxNmrExptlSampleConditions':
		"""The condition number as defined above.  Examples: 1, 2, 3 """
		self._enter('conditions_id', Query)
		return self
	@property
	def details(self) -> 'PdbxNmrExptlSampleConditions':
		"""General details describing conditions of both the sample and the environment during measurements.  Examples: The high salinity of the sample may have contributed to overheating of the sample during experiments with long saturation periods like the TOCSY experiments. """
		self._enter('details', Query)
		return self
	@property
	def ionic_strength(self) -> 'PdbxNmrExptlSampleConditions':
		"""The ionic strength at which the NMR data were collected -in lieu of  this enter the concentration and identity of the salt in the sample."""
		self._enter('ionic_strength', Query)
		return self
	@property
	def ionic_strength_err(self) -> 'PdbxNmrExptlSampleConditions':
		"""Estimate of the standard error for the value for the sample ionic strength.  Examples: null """
		self._enter('ionic_strength_err', Query)
		return self
	@property
	def ionic_strength_units(self) -> 'PdbxNmrExptlSampleConditions':
		"""Units for the value of the sample condition ionic strength..  Allowable values: M, Not defined, mM """
		self._enter('ionic_strength_units', Query)
		return self
	@property
	def label(self) -> 'PdbxNmrExptlSampleConditions':
		"""A descriptive label that uniquely identifies this set of sample conditions.  Examples: conditions_1 """
		self._enter('label', Query)
		return self
	@property
	def pH(self) -> 'PdbxNmrExptlSampleConditions':
		"""The pH at which the NMR data were collected.  Examples: null, null """
		self._enter('pH', Query)
		return self
	@property
	def pH_err(self) -> 'PdbxNmrExptlSampleConditions':
		"""Estimate of the standard error for the value for the sample pH.  Examples: null """
		self._enter('pH_err', Query)
		return self
	@property
	def pH_units(self) -> 'PdbxNmrExptlSampleConditions':
		"""Units for the value of the sample condition pH.  Allowable values: Not defined, pD, pH, pH* """
		self._enter('pH_units', Query)
		return self
	@property
	def pressure(self) -> 'PdbxNmrExptlSampleConditions':
		"""The pressure at which NMR data were collected.  Examples: 1, ambient, 1atm """
		self._enter('pressure', Query)
		return self
	@property
	def pressure_err(self) -> 'PdbxNmrExptlSampleConditions':
		"""Estimate of the standard error for the value for the sample pressure.  Examples: null """
		self._enter('pressure_err', Query)
		return self
	@property
	def pressure_units(self) -> 'PdbxNmrExptlSampleConditions':
		"""The units of pressure at which NMR data were collected.  Examples: Pa, atm, Torr """
		self._enter('pressure_units', Query)
		return self
	@property
	def temperature(self) -> 'PdbxNmrExptlSampleConditions':
		"""The temperature (in kelvin) at which NMR data were  collected."""
		self._enter('temperature', Query)
		return self
	@property
	def temperature_err(self) -> 'PdbxNmrExptlSampleConditions':
		"""Estimate of the standard error for the value for the sample temperature.  Examples: null """
		self._enter('temperature_err', Query)
		return self
	@property
	def temperature_units(self) -> 'PdbxNmrExptlSampleConditions':
		"""Units for the value of the sample condition temperature.  Allowable values: C, K, Not defined """
		self._enter('temperature_units', Query)
		return self

class PdbxNmrRefine(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'PdbxNmrRefine':
		"""Additional details about the NMR refinement.  Examples: Additional comments about the NMR refinement can be placed here, e.g. the structures are based on a total of 3344 restraints, 3167 are NOE-derived distance constraints, 68 dihedral angle restraints,109 distance restraints from hydrogen bonds. """
		self._enter('details', Query)
		return self
	@property
	def method(self) -> 'PdbxNmrRefine':
		"""The method used to determine the structure.  Examples: simulated annealing, distance geometry   simulated annealing   molecular dynamics   matrix relaxation   torsion angle dynamics """
		self._enter('method', Query)
		return self
	@property
	def software_ordinal(self) -> 'PdbxNmrRefine':
		"""Pointer to _software.ordinal"""
		self._enter('software_ordinal', Query)
		return self

class PdbxNmrRepresentative(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def conformer_id(self) -> 'PdbxNmrRepresentative':
		"""If a member of the ensemble has been selected as a representative  structure, identify it by its model number.  Examples: 15 """
		self._enter('conformer_id', Query)
		return self
	@property
	def selection_criteria(self) -> 'PdbxNmrRepresentative':
		"""By highlighting the appropriate choice(s), describe the criteria used to select this structure as a representative structure, or if an average structure has been calculated describe how this was done.  Examples: The structure closest to the average. The structure with the lowest energy was selected. The structure with the fewest number of violations was selected. A minimized average structure was calculated. """
		self._enter('selection_criteria', Query)
		return self

class PdbxNmrSampleDetails(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def contents(self) -> 'PdbxNmrSampleDetails':
		"""A complete description of each NMR sample. Include the concentration and concentration units for each component (include buffers, etc.). For each component describe the isotopic composition, including the % labeling level, if known.  For example: 1. Uniform (random) labeling with 15N: U-15N 2. Uniform (random) labeling with 13C, 15N at known labeling    levels: U-95% 13C;U-98% 15N 3. Residue selective labeling: U-95% 15N-Thymine 4. Site specific labeling: 95% 13C-Ala18, 5. Natural abundance labeling in an otherwise uniformly labeled    biomolecule is designated by NA: U-13C; NA-K,H  Examples: 2mM Ribonuclease  U-15N,13C; 50mM phosphate buffer NA; 90% H2O, 10% D2O """
		self._enter('contents', Query)
		return self
	@property
	def details(self) -> 'PdbxNmrSampleDetails':
		"""Brief description of the sample providing additional information not captured by other items in the category.  Examples: The added glycerol was used to raise the viscosity of the solution to 1.05 poisson. """
		self._enter('details', Query)
		return self
	@property
	def label(self) -> 'PdbxNmrSampleDetails':
		"""A value that uniquely identifies this sample from the other samples listed in the entry.  Examples: 15N_sample """
		self._enter('label', Query)
		return self
	@property
	def solution_id(self) -> 'PdbxNmrSampleDetails':
		"""The name (number) of the sample.  Examples: 1, 2, 3 """
		self._enter('solution_id', Query)
		return self
	@property
	def solvent_system(self) -> 'PdbxNmrSampleDetails':
		"""The solvent system used for this sample.  Examples: 90% H2O, 10% D2O """
		self._enter('solvent_system', Query)
		return self
	@property
	def type(self) -> 'PdbxNmrSampleDetails':
		"""A descriptive term for the sample that defines the general physical properties of the sample.  Allowable values: bicelle, emulsion, fiber, fibrous protein, filamentous virus, gel solid, gel solution, liposome, lyophilized powder, membrane, micelle, oriented membrane film, polycrystalline powder, reverse micelle, single crystal, solid, solution """
		self._enter('type', Query)
		return self

class PdbxNmrSoftware(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def authors(self) -> 'PdbxNmrSoftware':
		"""The name of the authors of the software used in this  procedure.  Examples: Brunger, Guentert """
		self._enter('authors', Query)
		return self
	@property
	def classification(self) -> 'PdbxNmrSoftware':
		"""The purpose of the software.  Examples: collection, processing, data analysis, structure solution, refinement, iterative matrix relaxation """
		self._enter('classification', Query)
		return self
	@property
	def name(self) -> 'PdbxNmrSoftware':
		"""The name of the software used for the task.  Examples: ANSIG, AURELIA, AZARA, CHARMM, CoMAND, CORMA, DIANA, DYANA, DSPACE, DISGEO, DGII, DISMAN, DINOSAUR, DISCOVER, FELIX, FT_NMR, GROMOS, IRMA, MARDIGRAS, NMRPipe, SA, UXNMR, VNMR, X-PLOR, XWINNMR """
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxNmrSoftware':
		"""An ordinal index for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def version(self) -> 'PdbxNmrSoftware':
		"""The version of the software.  Examples: 940501.3, 2.1 """
		self._enter('version', Query)
		return self

class PdbxNmrSpectrometer(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'PdbxNmrSpectrometer':
		"""A text description of the NMR spectrometer."""
		self._enter('details', Query)
		return self
	@property
	def field_strength(self) -> 'PdbxNmrSpectrometer':
		"""The field strength in MHz of the spectrometer"""
		self._enter('field_strength', Query)
		return self
	@property
	def manufacturer(self) -> 'PdbxNmrSpectrometer':
		"""The name of the manufacturer of the spectrometer.  Examples: Varian, Bruker, JEOL, GE """
		self._enter('manufacturer', Query)
		return self
	@property
	def model(self) -> 'PdbxNmrSpectrometer':
		"""The model of the NMR spectrometer.  Examples: AVANCE, AVANCE II, AVANCE III, AVANCE III HD, WH, WM, AC+, Alpha, AM, AMX, AMX II, DMX, DRX, DSX, MSL, OMEGA, OMEGA PSG, GX, GSX, A, AL, EC, EX, LA, ECP, Infinityplus, Mercury, VNMRS, VXR, UNITY, UNITY INOVA, UNITYPLUS, INOVA, home-built """
		self._enter('model', Query)
		return self
	@property
	def spectrometer_id(self) -> 'PdbxNmrSpectrometer':
		"""Assign a numerical ID to each instrument.  Examples: 1, 2, 3 """
		self._enter('spectrometer_id', Query)
		return self
	@property
	def type(self) -> 'PdbxNmrSpectrometer':
		"""Select the instrument manufacturer(s) and the model(s) of the NMR(s) used for this work.  Examples: Bruker WH, Bruker WM, Bruker AM, Bruker AMX, Bruker DMX, Bruker DRX, Bruker MSL, Bruker AVANCE, GE Omega, GE Omega PSG, JEOL GX, JEOL GSX, JEOL A, JEOL AL, JEOL EC, JEOL EX, JEOL LA, JEOL ECP, Varian VXRS, Varian UNITY, Varian UNITYplus, Varian INOVA, other """
		self._enter('type', Query)
		return self

class PdbxPrdAudit(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def action_type(self) -> 'PdbxPrdAudit':
		"""The action associated with this audit record.  Allowable values: Create molecule, Initial release, Modify audit, Modify class, Modify linkage, Modify molecule name, Modify representation, Modify sequence, Modify taxonomy organism, Modify type, Obsolete molecule, Other modification """
		self._enter('action_type', Query)
		return self
	@property
	def annotator(self) -> 'PdbxPrdAudit':
		"""The initials of the annotator creating of modifying the molecule.  Examples: JO, SJ, KB """
		self._enter('annotator', Query)
		return self
	@property
	def date(self) -> 'PdbxPrdAudit':
		"""The date associated with this audit record."""
		self._enter('date', Query)
		return self
	@property
	def details(self) -> 'PdbxPrdAudit':
		"""Additional details decribing this change.  Examples: Revise molecule sequence. """
		self._enter('details', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxPrdAudit':
		"""This data item is a pointer to _pdbx_reference_molecule.prd_id in the 	       pdbx_reference_molecule category."""
		self._enter('prd_id', Query)
		return self
	@property
	def processing_site(self) -> 'PdbxPrdAudit':
		"""An identifier for the wwPDB site creating or modifying the molecule.  Allowable values: BMRB, PDBC, PDBE, PDBJ, RCSB """
		self._enter('processing_site', Query)
		return self

class PdbxReferenceEntityList(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def component_id(self) -> 'PdbxReferenceEntityList':
		"""The component number of this entity within the molecule."""
		self._enter('component_id', Query)
		return self
	@property
	def details(self) -> 'PdbxReferenceEntityList':
		"""Additional details about this entity."""
		self._enter('details', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceEntityList':
		"""The value of _pdbx_reference_entity_list.prd_id is a reference  _pdbx_reference_molecule.prd_id in the PDBX_REFERENCE_MOLECULE category."""
		self._enter('prd_id', Query)
		return self
	@property
	def ref_entity_id(self) -> 'PdbxReferenceEntityList':
		"""The value of _pdbx_reference_entity_list.ref_entity_id is a unique identifier  the a constituent entity within this reference molecule."""
		self._enter('ref_entity_id', Query)
		return self
	@property
	def type(self) -> 'PdbxReferenceEntityList':
		"""Defines the polymer characteristic of the entity.  Allowable values: branched, non-polymer, polymer, polymer-like """
		self._enter('type', Query)
		return self

class PdbxReferenceEntityPoly(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def db_code(self) -> 'PdbxReferenceEntityPoly':
		"""The database code for this source information"""
		self._enter('db_code', Query)
		return self
	@property
	def db_name(self) -> 'PdbxReferenceEntityPoly':
		"""The database name for this source information"""
		self._enter('db_name', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceEntityPoly':
		"""The value of _pdbx_reference_entity_poly.prd_id is a reference 	       _pdbx_reference_entity_list.prd_id in the  PDBX_REFERENCE_ENTITY_LIST category."""
		self._enter('prd_id', Query)
		return self
	@property
	def ref_entity_id(self) -> 'PdbxReferenceEntityPoly':
		"""The value of _pdbx_reference_entity_poly.ref_entity_id is a reference  to _pdbx_reference_entity_list.ref_entity_id in PDBX_REFERENCE_ENTITY_LIST category."""
		self._enter('ref_entity_id', Query)
		return self
	@property
	def type(self) -> 'PdbxReferenceEntityPoly':
		"""The type of the polymer.  Allowable values: nucleic-acid-like, oligosaccharide, peptide-like, polysaccharide-like """
		self._enter('type', Query)
		return self

class PdbxReferenceEntityPolyLink(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def atom_id_1(self) -> 'PdbxReferenceEntityPolyLink':
		"""The atom identifier/name in the first of the two components making  the linkage."""
		self._enter('atom_id_1', Query)
		return self
	@property
	def atom_id_2(self) -> 'PdbxReferenceEntityPolyLink':
		"""The atom identifier/name in the second of the two components making  the linkage."""
		self._enter('atom_id_2', Query)
		return self
	@property
	def comp_id_1(self) -> 'PdbxReferenceEntityPolyLink':
		"""The component identifier in the first of the two components making the  linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.mon_id  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
		self._enter('comp_id_1', Query)
		return self
	@property
	def comp_id_2(self) -> 'PdbxReferenceEntityPolyLink':
		"""The component identifier in the second of the two components making the  linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.mon_id  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
		self._enter('comp_id_2', Query)
		return self
	@property
	def component_id(self) -> 'PdbxReferenceEntityPolyLink':
		"""The entity component identifier entity containing the linkage."""
		self._enter('component_id', Query)
		return self
	@property
	def entity_seq_num_1(self) -> 'PdbxReferenceEntityPolyLink':
		"""For a polymer entity, the sequence number in the first of  the two components making the linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.num  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
		self._enter('entity_seq_num_1', Query)
		return self
	@property
	def entity_seq_num_2(self) -> 'PdbxReferenceEntityPolyLink':
		"""For a polymer entity, the sequence number in the second of  the two components making the linkage.   This data item is a pointer to _pdbx_reference_entity_poly_seq.num  in the PDBX_REFERENCE_ENTITY_POLY_SEQ category."""
		self._enter('entity_seq_num_2', Query)
		return self
	@property
	def link_id(self) -> 'PdbxReferenceEntityPolyLink':
		"""The value of _pdbx_reference_entity_poly_link.link_id uniquely identifies  a linkage within a polymer entity."""
		self._enter('link_id', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceEntityPolyLink':
		"""The value of _pdbx_reference_entity_poly_link.prd_id is a reference  _pdbx_reference_entity_list.prd_id in the PDBX_REFERENCE_ENTITY_POLY category."""
		self._enter('prd_id', Query)
		return self
	@property
	def ref_entity_id(self) -> 'PdbxReferenceEntityPolyLink':
		"""The reference entity id of the polymer entity containing the linkage.   This data item is a pointer to _pdbx_reference_entity_poly.ref_entity_id  in the PDBX_REFERENCE_ENTITY_POLY category."""
		self._enter('ref_entity_id', Query)
		return self
	@property
	def value_order(self) -> 'PdbxReferenceEntityPolyLink':
		"""The bond order target for the non-standard linkage.  Allowable values: arom, delo, doub, pi, poly, quad, sing, trip """
		self._enter('value_order', Query)
		return self

class PdbxReferenceEntityPolySeq(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def hetero(self) -> 'PdbxReferenceEntityPolySeq':
		"""A flag to indicate that sequence heterogeneity at this monomer position.  Allowable values: N, Y """
		self._enter('hetero', Query)
		return self
	@property
	def mon_id(self) -> 'PdbxReferenceEntityPolySeq':
		"""This data item is the chemical component identifier of monomer."""
		self._enter('mon_id', Query)
		return self
	@property
	def num(self) -> 'PdbxReferenceEntityPolySeq':
		"""The value of _pdbx_reference_entity_poly_seq.num must uniquely and sequentially  identify a record in the PDBX_REFERENCE_ENTITY_POLY_SEQ list.   This value is conforms to author numbering conventions and does not map directly  to the numbering conventions used for _entity_poly_seq.num."""
		self._enter('num', Query)
		return self
	@property
	def observed(self) -> 'PdbxReferenceEntityPolySeq':
		"""A flag to indicate that this monomer is observed in the instance example.  Allowable values: N, Y """
		self._enter('observed', Query)
		return self
	@property
	def parent_mon_id(self) -> 'PdbxReferenceEntityPolySeq':
		"""This data item is the chemical component identifier for the parent component corresponding to this monomer."""
		self._enter('parent_mon_id', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceEntityPolySeq':
		"""The value of _pdbx_reference_entity_poly_seq.prd_id is a reference 	       _pdbx_reference_entity_poly.prd_id in the  PDBX_REFERENCE_ENTITY_POLY category."""
		self._enter('prd_id', Query)
		return self
	@property
	def ref_entity_id(self) -> 'PdbxReferenceEntityPolySeq':
		"""The value of _pdbx_reference_entity_poly_seq.ref_entity_id is a reference  to _pdbx_reference_entity_poly.ref_entity_id in PDBX_REFERENCE_ENTITY_POLY category."""
		self._enter('ref_entity_id', Query)
		return self

class PdbxReferenceEntitySequence(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def NRP_flag(self) -> 'PdbxReferenceEntitySequence':
		"""A flag to indicate a non-ribosomal entity.  Allowable values: N, Y """
		self._enter('NRP_flag', Query)
		return self
	@property
	def one_letter_codes(self) -> 'PdbxReferenceEntitySequence':
		"""The one-letter-code sequence for this entity.  Non-standard monomers are represented as 'X'."""
		self._enter('one_letter_codes', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceEntitySequence':
		"""The value of _pdbx_reference_entity_sequence.prd_id is a reference 	       _pdbx_reference_entity_list.prd_id in the  PDBX_REFERENCE_ENTITY_LIST category."""
		self._enter('prd_id', Query)
		return self
	@property
	def ref_entity_id(self) -> 'PdbxReferenceEntitySequence':
		"""The value of _pdbx_reference_entity_sequence.ref_entity_id is a reference  to _pdbx_reference_entity_list.ref_entity_id in PDBX_REFERENCE_ENTITY_LIST category."""
		self._enter('ref_entity_id', Query)
		return self
	@property
	def type(self) -> 'PdbxReferenceEntitySequence':
		"""The monomer type for the sequence.  Allowable values: peptide-like, saccharide """
		self._enter('type', Query)
		return self

class PdbxReferenceEntitySrcNat(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def atcc(self) -> 'PdbxReferenceEntitySrcNat':
		"""The Americal Tissue Culture Collection code for organism from which the entity was isolated."""
		self._enter('atcc', Query)
		return self
	@property
	def db_code(self) -> 'PdbxReferenceEntitySrcNat':
		"""The database code for this source information"""
		self._enter('db_code', Query)
		return self
	@property
	def db_name(self) -> 'PdbxReferenceEntitySrcNat':
		"""The database name for this source information"""
		self._enter('db_name', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxReferenceEntitySrcNat':
		"""The value of _pdbx_reference_entity_src_nat.ordinal distinguishes 	       source details for this entity."""
		self._enter('ordinal', Query)
		return self
	@property
	def organism_scientific(self) -> 'PdbxReferenceEntitySrcNat':
		"""The scientific name of the organism from which the entity was isolated.  Examples: Mus musculus """
		self._enter('organism_scientific', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceEntitySrcNat':
		"""The value of _pdbx_reference_entity_src_nat.prd_id is a reference 	       _pdbx_reference_entity_list.prd_id in the  PDBX_REFERENCE_ENTITY_LIST category."""
		self._enter('prd_id', Query)
		return self
	@property
	def ref_entity_id(self) -> 'PdbxReferenceEntitySrcNat':
		"""The value of _pdbx_reference_entity_src_nat.ref_entity_id is a reference  to _pdbx_reference_entity_list.ref_entity_id in PDBX_REFERENCE_ENTITY_LIST category."""
		self._enter('ref_entity_id', Query)
		return self
	@property
	def source(self) -> 'PdbxReferenceEntitySrcNat':
		"""The data source for this information."""
		self._enter('source', Query)
		return self
	@property
	def source_id(self) -> 'PdbxReferenceEntitySrcNat':
		"""A identifier within the data source for this information."""
		self._enter('source_id', Query)
		return self
	@property
	def taxid(self) -> 'PdbxReferenceEntitySrcNat':
		"""The NCBI TaxId of the organism from which the entity was isolated."""
		self._enter('taxid', Query)
		return self

class PdbxReferenceMolecule(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def chem_comp_id(self) -> 'PdbxReferenceMolecule':
		"""For entities represented as single molecules, the identifier  corresponding to the chemical definition for the molecule.  Examples: 0Z3, CD9 """
		self._enter('chem_comp_id', Query)
		return self
	@property
	def class_(self) -> 'PdbxReferenceMolecule':
		"""Broadly defines the function of the entity.  Allowable values: Antagonist, Anthelmintic, Antibiotic, Antibiotic, Anthelmintic, Antibiotic, Antimicrobial, Antibiotic, Antineoplastic, Anticancer, Anticoagulant, Anticoagulant, Antithrombotic, Antifungal, Antigen, Antiinflammatory, Antimicrobial, Antimicrobial, Antiparasitic, Antibiotic, Antimicrobial, Antiretroviral, Antimicrobial, Antitumor, Antineoplastic, Antiparasitic, Antiretroviral, Antithrombotic, Antitumor, Antiviral, CASPASE inhibitor, Chaperone binding, Drug delivery, Enzyme inhibitor, Glycan component, Growth factor, Immunosuppressant, Inducer, Inhibitor, Lantibiotic, Metabolism, Metal transport, Nutrient, Oxidation-reduction, Protein binding, Receptor, Substrate analog, Synthetic opioid, Thrombin inhibitor, Thrombin inhibitor, Trypsin inhibitor, Toxin, Transition state mimetic, Transport activator, Trypsin inhibitor, Unknown, Water retention """
		self._enter('class_', Query)
		return self
	@property
	def class_evidence_code(self) -> 'PdbxReferenceMolecule':
		"""Evidence for the assignment of _pdbx_reference_molecule.class"""
		self._enter('class_evidence_code', Query)
		return self
	@property
	def compound_details(self) -> 'PdbxReferenceMolecule':
		"""Special details about this molecule."""
		self._enter('compound_details', Query)
		return self
	@property
	def description(self) -> 'PdbxReferenceMolecule':
		"""Description of this molecule."""
		self._enter('description', Query)
		return self
	@property
	def formula(self) -> 'PdbxReferenceMolecule':
		"""The formula for the reference entity. Formulae are written  according to the rules:   1. Only recognised element symbols may be used.   2. Each element symbol is followed by a 'count' number. A count     of '1' may be omitted.   3. A space or parenthesis must separate each element symbol and     its count, but in general parentheses are not used.   4. The order of elements depends on whether or not carbon is     present. If carbon is present, the order should be: C, then     H, then the other elements in alphabetical order of their     symbol. If carbon is not present, the elements are listed     purely in alphabetic order of their symbol. This is the     'Hill' system used by Chemical Abstracts.  Examples: C18 H19 N7 O8 S """
		self._enter('formula', Query)
		return self
	@property
	def formula_weight(self) -> 'PdbxReferenceMolecule':
		"""Formula mass in daltons of the entity."""
		self._enter('formula_weight', Query)
		return self
	@property
	def name(self) -> 'PdbxReferenceMolecule':
		"""A name of the entity.  Examples: thiostrepton """
		self._enter('name', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceMolecule':
		"""The value of _pdbx_reference_molecule.prd_id is the unique identifier  for the reference molecule in this family.   By convention this ID uniquely identifies the reference molecule in  in the PDB reference dictionary.   The ID has the template form PRD_dddddd (e.g. PRD_000001)  Examples: PRD_000001, PRD_0000010 """
		self._enter('prd_id', Query)
		return self
	@property
	def release_status(self) -> 'PdbxReferenceMolecule':
		"""Defines the current PDB release status for this molecule definition.  Allowable values: HOLD, OBS, REL, WAIT """
		self._enter('release_status', Query)
		return self
	@property
	def replaced_by(self) -> 'PdbxReferenceMolecule':
		"""Assigns the identifier of the reference molecule that has replaced this molecule."""
		self._enter('replaced_by', Query)
		return self
	@property
	def replaces(self) -> 'PdbxReferenceMolecule':
		"""Assigns the identifier for the reference molecule which have been replaced  by this reference molecule.  Multiple molecule identifier codes should be separated by commas."""
		self._enter('replaces', Query)
		return self
	@property
	def represent_as(self) -> 'PdbxReferenceMolecule':
		"""Defines how this entity is represented in PDB data files.  Allowable values: branched, polymer, single molecule """
		self._enter('represent_as', Query)
		return self
	@property
	def representative_PDB_id_code(self) -> 'PdbxReferenceMolecule':
		"""The PDB accession code for the entry containing a representative example of this molecule."""
		self._enter('representative_PDB_id_code', Query)
		return self
	@property
	def type(self) -> 'PdbxReferenceMolecule':
		"""Defines the structural classification of the entity.  Allowable values: Amino acid, Aminoglycoside, Ansamycin, Anthracycline, Anthraquinone, Chalkophore, Chalkophore, Polypeptide, Chromophore, Cyclic depsipeptide, Cyclic lipopeptide, Cyclic peptide, Glycopeptide, Heterocyclic, Imino sugar, Keto acid, Lipoglycopeptide, Lipopeptide, Macrolide, Non-polymer, Nucleoside, Oligopeptide, Oligosaccharide, Peptaibol, Peptide-like, Polycyclic, Polypeptide, Polysaccharide, Quinolone, Siderophore, Thiolactone, Thiopeptide, Unknown """
		self._enter('type', Query)
		return self
	@property
	def type_evidence_code(self) -> 'PdbxReferenceMolecule':
		"""Evidence for the assignment of _pdbx_reference_molecule.type"""
		self._enter('type_evidence_code', Query)
		return self

class PdbxReferenceMoleculeAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeAnnotation':
		"""The value of _pdbx_reference_molecule_annotation.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxReferenceMoleculeAnnotation':
		"""This data item distinguishes anotations for this entity."""
		self._enter('ordinal', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceMoleculeAnnotation':
		"""This data item is a pointer to _pdbx_reference_molecule.prd_id in the  PDB_REFERENCE_MOLECULE category."""
		self._enter('prd_id', Query)
		return self
	@property
	def source(self) -> 'PdbxReferenceMoleculeAnnotation':
		"""The source of the annoation for this entity.  Examples: depositor provided, from UniProt Entry P200311 """
		self._enter('source', Query)
		return self
	@property
	def text(self) -> 'PdbxReferenceMoleculeAnnotation':
		"""Text describing the annotation for this entity.  Examples: antigen binding, glucose transporter activity """
		self._enter('text', Query)
		return self
	@property
	def type(self) -> 'PdbxReferenceMoleculeAnnotation':
		"""Type of annotation for this entity.  Examples: Function, Use, Pharmacology, Mechanism_of_Action, Biological_Activity, Inhibitor_Class, Therapeutic_Category, Research_Use, Other_annotation """
		self._enter('type', Query)
		return self

class PdbxReferenceMoleculeDetails(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeDetails':
		"""The value of _pdbx_reference_molecule_details.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id' in category PDBX_REFERENCE_MOLECULE_FAMILY."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxReferenceMoleculeDetails':
		"""The value of _pdbx_reference_molecule_details.ordinal is an ordinal that  distinguishes each descriptive text for this entity."""
		self._enter('ordinal', Query)
		return self
	@property
	def source(self) -> 'PdbxReferenceMoleculeDetails':
		"""A data source of this information (e.g. PubMed, Merck Index)"""
		self._enter('source', Query)
		return self
	@property
	def source_id(self) -> 'PdbxReferenceMoleculeDetails':
		"""A identifier within the data source for this information."""
		self._enter('source_id', Query)
		return self
	@property
	def text(self) -> 'PdbxReferenceMoleculeDetails':
		"""The text of the description of special aspects of the entity."""
		self._enter('text', Query)
		return self

class PdbxReferenceMoleculeFamily(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeFamily':
		"""The value of _pdbx_reference_entity.family_prd_id must uniquely identify a record in the  PDBX_REFERENCE_MOLECULE_FAMILY list.   By convention this ID uniquely identifies the reference family in  in the PDB reference dictionary.   The ID has the template form FAM_dddddd (e.g. FAM_000001)"""
		self._enter('family_prd_id', Query)
		return self
	@property
	def name(self) -> 'PdbxReferenceMoleculeFamily':
		"""The entity family name.  Examples: actinomycin, adriamycin """
		self._enter('name', Query)
		return self
	@property
	def release_status(self) -> 'PdbxReferenceMoleculeFamily':
		"""Assigns the current PDB release status for this family.  Allowable values: HOLD, OBS, REL, WAIT """
		self._enter('release_status', Query)
		return self
	@property
	def replaced_by(self) -> 'PdbxReferenceMoleculeFamily':
		"""Assigns the identifier of the family that has replaced this component."""
		self._enter('replaced_by', Query)
		return self
	@property
	def replaces(self) -> 'PdbxReferenceMoleculeFamily':
		"""Assigns the identifier for the family which have been replaced by this family.  Multiple family identifier codes should be separated by commas."""
		self._enter('replaces', Query)
		return self

class PdbxReferenceMoleculeFeatures(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The value of _pdbx_reference_molecule_features.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The value of _pdbx_reference_molecule_features.ordinal distinguishes 	       each feature for this entity."""
		self._enter('ordinal', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The value of _pdbx_reference_molecule_features.prd_id is a reference 	       _pdbx_reference_molecule.prd_id in the  PDBX_REFERENCE_MOLECULE category."""
		self._enter('prd_id', Query)
		return self
	@property
	def source(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The information source for the component feature.  Examples: PDB, CHEBI, DRUGBANK, PUBCHEM """
		self._enter('source', Query)
		return self
	@property
	def source_ordinal(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The value of _pdbx_reference_molecule_features.source_ordinal provides 	       the priority order of features from a particular source or database."""
		self._enter('source_ordinal', Query)
		return self
	@property
	def type(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The entity feature type.  Examples: FUNCTION, ENZYME INHIBITED, STRUCTURE IMAGE URL """
		self._enter('type', Query)
		return self
	@property
	def value(self) -> 'PdbxReferenceMoleculeFeatures':
		"""The entity feature value."""
		self._enter('value', Query)
		return self

class PdbxReferenceMoleculeList(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeList':
		"""The value of _pdbx_reference_molecule_list.family_prd_id is a reference to  _pdbx_reference_molecule_family.family_prd_id' in category PDBX_REFERENCE_MOLECULE_FAMILY."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceMoleculeList':
		"""The value of _pdbx_reference_molecule_list.prd_id is the unique identifier  for the reference molecule in this family.   By convention this ID uniquely identifies the reference molecule in  in the PDB reference dictionary.   The ID has the template form PRD_dddddd (e.g. PRD_000001)"""
		self._enter('prd_id', Query)
		return self

class PdbxReferenceMoleculeRelatedStructures(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def citation_id(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""A link to related reference information in the citation category."""
		self._enter('citation_id', Query)
		return self
	@property
	def db_accession(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The database accession code for the related structure reference.  Examples: 143108 """
		self._enter('db_accession', Query)
		return self
	@property
	def db_code(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The database identifier code for the related structure reference.  Examples: QEFHUE """
		self._enter('db_code', Query)
		return self
	@property
	def db_name(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The database name for the related structure reference.  Examples: CCDC """
		self._enter('db_name', Query)
		return self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The value of _pdbx_reference_molecule_related_structures.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def formula(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The formula for the reference entity. Formulae are written  according to the rules:   1. Only recognised element symbols may be used.   2. Each element symbol is followed by a 'count' number. A count     of '1' may be omitted.   3. A space or parenthesis must separate each element symbol and     its count, but in general parentheses are not used.   4. The order of elements depends on whether or not carbon is     present. If carbon is present, the order should be: C, then     H, then the other elements in alphabetical order of their     symbol. If carbon is not present, the elements are listed     purely in alphabetic order of their symbol. This is the     'Hill' system used by Chemical Abstracts.  Examples: C18 H19 N7 O8 S """
		self._enter('formula', Query)
		return self
	@property
	def name(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The chemical name for the structure entry in the related database  Examples: actinomycn """
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxReferenceMoleculeRelatedStructures':
		"""The value of _pdbx_reference_molecule_related_structures.ordinal distinguishes  related structural data for each entity."""
		self._enter('ordinal', Query)
		return self

class PdbxReferenceMoleculeSynonyms(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def family_prd_id(self) -> 'PdbxReferenceMoleculeSynonyms':
		"""The value of _pdbx_reference_molecule_synonyms.family_prd_id is a reference to  _pdbx_reference_molecule_list.family_prd_id in category PDBX_REFERENCE_MOLECULE_FAMILY_LIST."""
		self._enter('family_prd_id', Query)
		return self
	@property
	def name(self) -> 'PdbxReferenceMoleculeSynonyms':
		"""A synonym name for the entity.  Examples: thiostrepton """
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxReferenceMoleculeSynonyms':
		"""The value of _pdbx_reference_molecule_synonyms.ordinal is an ordinal 	       to distinguish synonyms for this entity."""
		self._enter('ordinal', Query)
		return self
	@property
	def prd_id(self) -> 'PdbxReferenceMoleculeSynonyms':
		"""The value of _pdbx_reference_molecule_synonyms.prd_id is a reference 	       _pdbx_reference_molecule.prd_id in the  PDBX_REFERENCE_MOLECULE category."""
		self._enter('prd_id', Query)
		return self
	@property
	def source(self) -> 'PdbxReferenceMoleculeSynonyms':
		"""The source of this synonym name for the entity.  Examples: CAS """
		self._enter('source', Query)
		return self

class PdbxReflnsTwin(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def crystal_id(self) -> 'PdbxReflnsTwin':
		"""The crystal identifier.  A reference to  _exptl_crystal.id in category EXPTL_CRYSTAL."""
		self._enter('crystal_id', Query)
		return self
	@property
	def diffrn_id(self) -> 'PdbxReflnsTwin':
		"""The diffraction data set identifier.  A reference to  _diffrn.id in category DIFFRN."""
		self._enter('diffrn_id', Query)
		return self
	@property
	def domain_id(self) -> 'PdbxReflnsTwin':
		"""An identifier for the twin domain."""
		self._enter('domain_id', Query)
		return self
	@property
	def fraction(self) -> 'PdbxReflnsTwin':
		"""The twin fraction or twin factor represents a quantitative parameter for the crystal twinning.  The value 0 represents no twinning, < 0.5 partial twinning,  = 0.5 for perfect twinning."""
		self._enter('fraction', Query)
		return self
	@property
	def operator(self) -> 'PdbxReflnsTwin':
		"""The possible merohedral or hemihedral twinning operators for different point groups are:  True point group  	Twin operation  	hkl related to 3                      	2 along a,b             h,-h-k,-l                        	2 along a*,b*           h+k,-k,-l                         2 along c               -h,-k,l 4                       2 along a,b,a*,b*       h,-k,-l 6                       2 along a,b,a*,b*       h,-h-k,-l 321                     2 along a*,b*,c         -h,-k,l 312                     2 along a,b,c           -h,-k,l 23                      4 along a,b,c            k,-h,l  References:  Yeates, T.O. (1997) Methods in Enzymology 276, 344-358. Detecting and  Overcoming Crystal Twinning.   and information from the following on-line sites:     CNS site http://cns.csb.yale.edu/v1.1/    CCP4 site http://www.ccp4.ac.uk/dist/html/detwin.html    SHELX site http://shelx.uni-ac.gwdg.de/~rherbst/twin.html  Examples: h,-h-k,-l, h+k,-k,-l, -h,-k,l, h,-k,-l, h,-h-k,-l, -h,-k,l, k,-h,l """
		self._enter('operator', Query)
		return self
	@property
	def type(self) -> 'PdbxReflnsTwin':
		"""There are two types of twinning: merohedral or hemihedral                                  non-merohedral or epitaxial  For merohedral twinning the diffraction patterns from the different domains are completely superimposable.   Hemihedral twinning is a special case of merohedral twinning. It only involves two distinct domains.  Pseudo-merohedral twinning is a subclass merohedral twinning in which lattice is coincidentally superimposable.  In the case of non-merohedral or epitaxial twinning  the reciprocal lattices do not superimpose exactly. In this case the  diffraction pattern consists of two (or more) interpenetrating lattices, which can in principle be separated.  Allowable values: epitaxial, hemihedral, merohedral, non-merohedral, pseudo-merohedral, tetartohedral """
		self._enter('type', Query)
		return self

class PdbxRelatedExpDataSet(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def data_reference(self) -> 'PdbxRelatedExpDataSet':
		"""A DOI reference to the related data set.  Examples: 10.000/10002/image_data/cif """
		self._enter('data_reference', Query)
		return self
	@property
	def data_set_type(self) -> 'PdbxRelatedExpDataSet':
		"""The type of the experimenatal data set.  Examples: diffraction image data, NMR free induction decay data """
		self._enter('data_set_type', Query)
		return self
	@property
	def details(self) -> 'PdbxRelatedExpDataSet':
		"""Additional details describing the content of the related data set and its application to  the current investigation."""
		self._enter('details', Query)
		return self
	@property
	def metadata_reference(self) -> 'PdbxRelatedExpDataSet':
		"""A DOI reference to the metadata decribing the related data set.  Examples: 10.000/10002/image_data/txt """
		self._enter('metadata_reference', Query)
		return self

class PdbxSGProject(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def full_name_of_center(self) -> 'PdbxSGProject':
		"""The value identifies the full name of center.  Allowable values: Accelerated Technologies Center for Gene to 3D Structure, Assembly, Dynamics and Evolution of Cell-Cell and Cell-Matrix Adhesions, Atoms-to-Animals: The Immune Function Network, Bacterial targets at IGS-CNRS, France, Berkeley Structural Genomics Center, Center for Eukaryotic Structural Genomics, Center for High-Throughput Structural Biology, Center for Membrane Proteins of Infectious Diseases, Center for Structural Biology of Infectious Diseases, Center for Structural Genomics of Infectious Diseases, Center for Structures of Membrane Proteins, Center for the X-ray Structure Determination of Human Transporters, Chaperone-Enabled Studies of Epigenetic Regulation Enzymes, Enzyme Discovery for Natural Product Biosynthesis, GPCR Network, Integrated Center for Structure and Function Innovation, Israel Structural Proteomics Center, Joint Center for Structural Genomics, Marseilles Structural Genomics Program @ AFMB, Medical Structural Genomics of Pathogenic Protozoa, Membrane Protein Structural Biology Consortium, Membrane Protein Structures by Solution NMR, Midwest Center for Macromolecular Research, Midwest Center for Structural Genomics, Mitochondrial Protein Partnership, Montreal-Kingston Bacterial Structural Genomics Initiative, Mycobacterium Tuberculosis Structural Proteomics Project, New York Consortium on Membrane Protein Structure, New York SGX Research Center for Structural Genomics, New York Structural GenomiX Research Consortium, New York Structural Genomics Research Consortium, Northeast Structural Genomics Consortium, Nucleocytoplasmic Transport: a Target for Cellular Control, Ontario Centre for Structural Proteomics, Oxford Protein Production Facility, Paris-Sud Yeast Structural Genomics, Partnership for Nuclear Receptor Signaling Code Biology, Partnership for Stem Cell Biology, Partnership for T-Cell Biology, Program for the Characterization of Secreted Effector Proteins, Protein Structure Factory, RIKEN Structural Genomics/Proteomics Initiative, Scottish Structural Proteomics Facility, Seattle Structural Genomics Center for Infectious Disease, South Africa Structural Targets Annotation Database, Southeast Collaboratory for Structural Genomics, Structural Genomics Consortium, Structural Genomics Consortium for Research on Gene Expression, Structural Genomics of Pathogenic Protozoa Consortium, Structural Proteomics in Europe, Structural Proteomics in Europe 2, Structure 2 Function Project, Structure, Dynamics and Activation Mechanisms of Chemokine Receptors, Structure-Function Analysis of Polymorphic CDI Toxin-Immunity Protein Complexes, Structure-Function Studies of Tight Junction Membrane Proteins, Structures of Mtb Proteins Conferring Susceptibility to Known Mtb Inhibitors, TB Structural Genomics Consortium, Transcontinental EM Initiative for Membrane Protein Structure, Transmembrane Protein Center """
		self._enter('full_name_of_center', Query)
		return self
	@property
	def id(self) -> 'PdbxSGProject':
		"""A unique integer identifier for this center  Allowable values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 """
		self._enter('id', Query)
		return self
	@property
	def initial_of_center(self) -> 'PdbxSGProject':
		"""The value identifies the full name of center.  Allowable values: ATCG3D, BIGS, BSGC, BSGI, CEBS, CELLMAT, CESG, CHSAM, CHTSB, CSBID, CSGID, CSMP, GPCR, IFN, ISFI, ISPC, JCSG, MCMR, MCSG, MPID, MPP, MPSBC, MPSbyNMR, MSGP, MSGPP, MTBI, NESG, NHRs, NPCXstals, NYCOMPS, NYSGRC, NYSGXRC, NatPro, OCSP, OPPF, PCSEP, PSF, RSGI, S2F, SASTAD, SECSG, SGC, SGCGES, SGPP, SPINE, SPINE-2, SSGCID, SSPF, STEMCELL, TBSGC, TCELL, TEMIMPS, TJMP, TMPC, TransportPDB, UC4CDI, XMTB, YSG """
		self._enter('initial_of_center', Query)
		return self
	@property
	def project_name(self) -> 'PdbxSGProject':
		"""The value identifies the Structural Genomics project.  Allowable values: Enzyme Function Initiative, NIAID, National Institute of Allergy and Infectious Diseases, NPPSFA, National Project on Protein Structural and Functional Analyses, PSI, Protein Structure Initiative, PSI:Biology """
		self._enter('project_name', Query)
		return self

class PdbxSerialCrystallographyDataReduction(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def crystal_hits(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a  continuous stream, the total number of frames collected  in which the crystal was hit."""
		self._enter('crystal_hits', Query)
		return self
	@property
	def diffrn_id(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""The data item is a pointer to _diffrn.id in the DIFFRN  category.  Examples: 1 """
		self._enter('diffrn_id', Query)
		return self
	@property
	def droplet_hits(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a  continuous stream, the total number of frames collected  in which a droplet was hit."""
		self._enter('droplet_hits', Query)
		return self
	@property
	def frame_hits(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a  continuous stream, the total number of data frames collected  in which the sample was hit."""
		self._enter('frame_hits', Query)
		return self
	@property
	def frames_failed_index(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a  continuous stream, the total number of data frames collected  that contained a 'hit' but failed to index."""
		self._enter('frames_failed_index', Query)
		return self
	@property
	def frames_indexed(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a  continuous stream, the total number of data frames collected  that were indexed."""
		self._enter('frames_indexed', Query)
		return self
	@property
	def frames_total(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""The total number of data frames collected for this  data set."""
		self._enter('frames_total', Query)
		return self
	@property
	def lattices_indexed(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a  continuous stream, the total number of lattices indexed."""
		self._enter('lattices_indexed', Query)
		return self
	@property
	def lattices_merged(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For experiments in which samples are provided in a             continuous stream, the total number of crystal lattices             that were merged in the final dataset.  Can be             less than frames_indexed depending on filtering during merging or 	    can be more than frames_indexed if there are multiple lattices. 	    per frame."""
		self._enter('lattices_merged', Query)
		return self
	@property
	def xfel_pulse_events(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For FEL experiments, the number of pulse events in the dataset."""
		self._enter('xfel_pulse_events', Query)
		return self
	@property
	def xfel_run_numbers(self) -> 'PdbxSerialCrystallographyDataReduction':
		"""For FEL experiments, in which data collection was performed 	       in batches, indicates which subset of the data collected                were used in producing this dataset."""
		self._enter('xfel_run_numbers', Query)
		return self

class PdbxSerialCrystallographyMeasurement(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def collection_time_total(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The total number of hours required to measure this data set.  Examples: null """
		self._enter('collection_time_total', Query)
		return self
	@property
	def collimation(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The collimation or type of focusing optics applied to the radiation.  Examples: Kirkpatrick-Baez mirrors, Beryllium compound refractive lenses, Fresnel zone plates """
		self._enter('collimation', Query)
		return self
	@property
	def diffrn_id(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The data item is a pointer to _diffrn.id in the DIFFRN  category.  Examples: 1 """
		self._enter('diffrn_id', Query)
		return self
	@property
	def focal_spot_size(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The focal spot size of the beam  impinging on the sample (micrometres squared)."""
		self._enter('focal_spot_size', Query)
		return self
	@property
	def photons_per_pulse(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The photons per pulse measured in  (tera photons (10^(12)^)/pulse units)."""
		self._enter('photons_per_pulse', Query)
		return self
	@property
	def pulse_duration(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The average duration (femtoseconds) 	       of the pulse energy measured at the sample."""
		self._enter('pulse_duration', Query)
		return self
	@property
	def pulse_energy(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The energy/pulse of the X-ray pulse impacting the sample measured in microjoules."""
		self._enter('pulse_energy', Query)
		return self
	@property
	def pulse_photon_energy(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The photon energy of the X-ray pulse measured in KeV."""
		self._enter('pulse_photon_energy', Query)
		return self
	@property
	def source_distance(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The distance from source to the sample along the optical axis (metres)."""
		self._enter('source_distance', Query)
		return self
	@property
	def source_size(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""The dimension of the source beam measured at the source (micrometres squared)."""
		self._enter('source_size', Query)
		return self
	@property
	def xfel_pulse_repetition_rate(self) -> 'PdbxSerialCrystallographyMeasurement':
		"""For FEL experiments, the pulse repetition rate measured in cycles per seconds."""
		self._enter('xfel_pulse_repetition_rate', Query)
		return self

class PdbxSerialCrystallographySampleDelivery(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def description(self) -> 'PdbxSerialCrystallographySampleDelivery':
		"""The description of the mechanism by which the specimen in placed in the path  of the source.  Examples: fixed target, electrospin, MESH, CoMESH, gas dynamic virtual nozzle, LCP injector, addressable microarray """
		self._enter('description', Query)
		return self
	@property
	def diffrn_id(self) -> 'PdbxSerialCrystallographySampleDelivery':
		"""The data item is a pointer to _diffrn.id in the DIFFRN  category.  Examples: 1 """
		self._enter('diffrn_id', Query)
		return self
	@property
	def method(self) -> 'PdbxSerialCrystallographySampleDelivery':
		"""The description of the mechanism by which the specimen in placed in the path  of the source.  Allowable values: fixed target, injection """
		self._enter('method', Query)
		return self

class PdbxSerialCrystallographySampleDeliveryFixedTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def crystals_per_unit(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""The number of crystals per dropplet or pore in fixed target"""
		self._enter('crystals_per_unit', Query)
		return self
	@property
	def description(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""For a fixed target sample, a description of sample preparation"""
		self._enter('description', Query)
		return self
	@property
	def details(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Any details pertinent to the fixed sample target"""
		self._enter('details', Query)
		return self
	@property
	def diffrn_id(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""The data item is a pointer to _diffrn.id in the DIFFRN  category.  Examples: 1 """
		self._enter('diffrn_id', Query)
		return self
	@property
	def motion_control(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Device used to control movement of the fixed sample  Examples: DMC-4080 """
		self._enter('motion_control', Query)
		return self
	@property
	def sample_dehydration_prevention(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Method to prevent dehydration of sample  Examples: seal, humidifed gas, flash freezing """
		self._enter('sample_dehydration_prevention', Query)
		return self
	@property
	def sample_holding(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""For a fixed target sample, mechanism to hold sample in the beam  Examples: mesh, loop, grid """
		self._enter('sample_holding', Query)
		return self
	@property
	def sample_solvent(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""The sample solution content and concentration"""
		self._enter('sample_solvent', Query)
		return self
	@property
	def sample_unit_size(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Size of pore in grid supporting sample. Diameter or length in micrometres,  e.g. pore diameter"""
		self._enter('sample_unit_size', Query)
		return self
	@property
	def support_base(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Type of base holding the support  Examples: goniometer """
		self._enter('support_base', Query)
		return self
	@property
	def velocity_horizontal(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Velocity of sample horizontally relative to a perpendicular beam in millimetres/second"""
		self._enter('velocity_horizontal', Query)
		return self
	@property
	def velocity_vertical(self) -> 'PdbxSerialCrystallographySampleDeliveryFixedTarget':
		"""Velocity of sample vertically relative to a perpendicular beam in millimetres/second"""
		self._enter('velocity_vertical', Query)
		return self

class PdbxSerialCrystallographySampleDeliveryInjection(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def carrier_solvent(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, the carrier buffer used  to move the sample into the beam. Should include protein  concentration.  Examples: LCP, grease, liquid """
		self._enter('carrier_solvent', Query)
		return self
	@property
	def crystal_concentration(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, the concentration of  crystals in the solution being injected.   The concentration is measured in million crystals/ml."""
		self._enter('crystal_concentration', Query)
		return self
	@property
	def description(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, a description of the injector used  to move the sample into the beam.  Examples: microextrusion injector """
		self._enter('description', Query)
		return self
	@property
	def diffrn_id(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""The data item is a pointer to _diffrn.id in the DIFFRN  category.  Examples: 1 """
		self._enter('diffrn_id', Query)
		return self
	@property
	def filter_size(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""The size of filter in micrometres in filtering crystals"""
		self._enter('filter_size', Query)
		return self
	@property
	def flow_rate(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, the flow rate of  solution being injected  measured in ul/min."""
		self._enter('flow_rate', Query)
		return self
	@property
	def injector_diameter(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, the diameter of the  injector in micrometres."""
		self._enter('injector_diameter', Query)
		return self
	@property
	def injector_nozzle(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""The type of nozzle to deliver and focus sample jet  Examples: gas, GDVN """
		self._enter('injector_nozzle', Query)
		return self
	@property
	def injector_pressure(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, the mean pressure  in kilopascals at which the sample is injected into the beam."""
		self._enter('injector_pressure', Query)
		return self
	@property
	def injector_temperature(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""For continuous sample flow experiments, the temperature in  Kelvins of the speciman injected. This may be different from  the temperature of the sample."""
		self._enter('injector_temperature', Query)
		return self
	@property
	def jet_diameter(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""Diameter in micrometres of jet stream of sample delivery"""
		self._enter('jet_diameter', Query)
		return self
	@property
	def power_by(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""Sample deliver driving force, e.g. Gas, Electronic Potential  Examples: syringe, gas, electronic potential """
		self._enter('power_by', Query)
		return self
	@property
	def preparation(self) -> 'PdbxSerialCrystallographySampleDeliveryInjection':
		"""Details of crystal growth and preparation of the crystals  Examples: Crystals transfered to carrier solvent at room temperature """
		self._enter('preparation', Query)
		return self

class PdbxSolnScatter(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def buffer_name(self) -> 'PdbxSolnScatter':
		"""The name of the buffer used for the sample in the solution scattering  experiment.  Examples: acetic acid """
		self._enter('buffer_name', Query)
		return self
	@property
	def concentration_range(self) -> 'PdbxSolnScatter':
		"""The concentration range (mg/mL) of the complex in the  sample used in the solution scattering experiment to  determine the mean radius of structural elongation.  Examples: 0.7 - 14 """
		self._enter('concentration_range', Query)
		return self
	@property
	def data_analysis_software_list(self) -> 'PdbxSolnScatter':
		"""A list of the software used in the data analysis  Examples: SCTPL5 GNOM """
		self._enter('data_analysis_software_list', Query)
		return self
	@property
	def data_reduction_software_list(self) -> 'PdbxSolnScatter':
		"""A list of the software used in the data reduction  Examples: OTOKO """
		self._enter('data_reduction_software_list', Query)
		return self
	@property
	def detector_specific(self) -> 'PdbxSolnScatter':
		"""The particular radiation detector. In general this will be a   manufacturer, description, model number or some combination of   these."""
		self._enter('detector_specific', Query)
		return self
	@property
	def detector_type(self) -> 'PdbxSolnScatter':
		"""The general class of the radiation detector."""
		self._enter('detector_type', Query)
		return self
	@property
	def id(self) -> 'PdbxSolnScatter':
		"""The value of _pdbx_soln_scatter.id must  uniquely identify the sample in the category PDBX_SOLN_SCATTER"""
		self._enter('id', Query)
		return self
	@property
	def max_mean_cross_sectional_radii_gyration(self) -> 'PdbxSolnScatter':
		"""The maximum mean radius of structural elongation of the sample.  In a given solute-solvent contrast, the radius of gyration  R_G is a measure of structural elongation if the internal  inhomogeneity of scattering densities has no effect. Guiner  analysis at low Q give the R_G and the forward scattering at  zero angle I(0).      lnl(Q) = lnl(0) - R_G^2Q^2/3   where        Q = 4(pi)sin(theta/lamda)        2theta = scattering angle        lamda = wavelength   The above expression is valid in a QR_G range for extended  rod-like particles. The relative I(0)/c values ( where   c = sample concentration) for sample measurements in a  constant buffer for a single sample data session, gives the  relative masses of the protein(s) studied when referenced  against a standard.   see:      O.Glatter & O.Kratky, (1982). Editors of 'Small angle       X-ray Scattering, Academic Press, New York.      O.Kratky. (1963). X-ray small angle scattering with       substances of biological interest in diluted solutions.       Prog. Biophys. Chem., 13, 105-173.      G.D.Wignall & F.S.Bates, (1987). The small-angle approximation       of X-ray and neutron scatter from rigid rods of non-uniform       cross section and finite length. J.Appl. Crystallog., 18, 452-460.   If the structure is elongated, the mean radius of gyration  of the cross-sectional structure R_XS  and the mean cross sectional  intensity at zero angle [I(Q).Q]_Q->0 is obtained from     ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
		self._enter('max_mean_cross_sectional_radii_gyration', Query)
		return self
	@property
	def max_mean_cross_sectional_radii_gyration_esd(self) -> 'PdbxSolnScatter':
		"""The estimated standard deviation for the minimum mean radius of structural elongation of the sample. In a given solute-solvent contrast, the radius of gyration R_G is a measure of structural elongation if the internal inhomogeneity of scattering densities has no effect. Guiner analysis at low Q give the R_G and the forward scattering at zero angle I(0).      lnl(Q) = lnl(0) - R_G^2Q^2/3  where       Q = 4(pi)sin(theta/lamda)       2theta = scattering angle       lamda = wavelength  The above expression is valid in a QR_G range for extended rod-like particles. The relative I(0)/c values ( where  c = sample concentration) for sample measurements in a constant buffer for a single sample data session, gives the relative masses of the protein(s) studied when referenced against a standard.  see:     O.Glatter & O.Kratky, (1982). Editors of 'Small angle      X-ray Scattering, Academic Press, New York.     O.Kratky. (1963). X-ray small angle scattering with      substances of biological interest in diluted solutions.      Prog. Biophys. Chem., 13, 105-173.     G.D.Wignall & F.S.Bates, (1987). The small-angle approximation      of X-ray and neutron scatter from rigid rods of non-uniform      cross section and finite length. J.Appl. Crystallog., 18, 452-460.  If the structure is elongated, the mean radius of gyration of the cross-sectional structure R_XS  and the mean cross sectional intensity at zero angle [I(Q).Q]_Q->0 is obtained from    ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
		self._enter('max_mean_cross_sectional_radii_gyration_esd', Query)
		return self
	@property
	def mean_guiner_radius(self) -> 'PdbxSolnScatter':
		"""The mean radius of structural elongation of the sample.  In a given solute-solvent contrast, the radius of gyration  R_G is a measure of structural elongation if the internal  inhomogeneity of scattering densities has no effect. Guiner  analysis at low Q gives the R_G and the forward scattering at  zero angle I(0).       lnl(Q) = lnl(0) - R_G^2Q^2/3   where        Q = 4(pi)sin(theta/lamda)        2theta = scattering angle        lamda = wavelength   The above expression is valid in a QR_G range for extended  rod-like particles. The relative I(0)/c values ( where   c = sample concentration) for sample measurements in a  constant buffer for a single sample data session, gives the  relative masses of the protein(s) studied when referenced  against a standard.   see: O.Glatter & O.Kratky, (1982). Editors of 'Small angle       X-ray Scattering, Academic Press, New York.       O.Kratky. (1963). X-ray small angle scattering with       substances of biological interest in diluted solutions.       Prog. Biophys. Chem., 13, 105-173.        G.D.Wignall & F.S.Bates, (1987). The small-angle approximation       of X-ray and neutron scatter from rigid rods of non-uniform       cross section and finite length. J.Appl. Crystallog., 18, 452-460.   If the structure is elongated, the mean radius of gyration  of the cross-sectional structure R_XS  and the mean cross sectional  intensity at zero angle [I(Q).Q]_Q->0 is obtained from      ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
		self._enter('mean_guiner_radius', Query)
		return self
	@property
	def mean_guiner_radius_esd(self) -> 'PdbxSolnScatter':
		"""The estimated standard deviation for the  mean radius of structural elongation of the sample.  In a given solute-solvent contrast, the radius of gyration  R_G is a measure of structural elongation if the internal  inhomogeneity of scattering densities has no effect. Guiner  analysis at low Q give the R_G and the forward scattering at  zero angle I(0).       lnl(Q) = lnl(0) - R_G^2Q^2/3   where        Q = 4(pi)sin(theta/lamda)        2theta = scattering angle        lamda = wavelength   The above expression is valid in a QR_G range for extended  rod-like particles. The relative I(0)/c values ( where   c = sample concentration) for sample measurements in a  constant buffer for a single sample data session, gives the  relative masses of the protein(s) studied when referenced  against a standard.   see:      O.Glatter & O.Kratky, (1982). Editors of 'Small angle       X-ray Scattering, Academic Press, New York.      O.Kratky. (1963). X-ray small angle scattering with       substances of biological interest in diluted solutions.       Prog. Biophys. Chem., 13, 105-173.      G.D.Wignall & F.S.Bates, (1987). The small-angle approximation       of X-ray and neutron scatter from rigid rods of non-uniform       cross section and finite length. J.Appl. Crystallog., 18, 452-460.   If the structure is elongated, the mean radius of gyration  of the cross-sectional structure R_XS  and the mean cross sectional  intensity at zero angle [I(Q).Q]_Q->0 is obtained from     ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
		self._enter('mean_guiner_radius_esd', Query)
		return self
	@property
	def min_mean_cross_sectional_radii_gyration(self) -> 'PdbxSolnScatter':
		"""The minimum mean radius of structural elongation of the sample. In a given solute-solvent contrast, the radius of gyration R_G is a measure of structural elongation if the internal inhomogeneity of scattering densities has no effect. Guiner analysis at low Q give the R_G and the forward scattering at zero angle I(0).      lnl(Q) = lnl(0) - R_G^2Q^2/3  where       Q = 4(pi)sin(theta/lamda)       2theta = scattering angle       lamda = wavelength  The above expression is valid in a QR_G range for extended rod-like particles. The relative I(0)/c values ( where  c = sample concentration) for sample measurements in a constant buffer for a single sample data session, gives the relative masses of the protein(s) studied when referenced against a standard.  see:     O.Glatter & O.Kratky, (1982). Editors of 'Small angle      X-ray Scattering, Academic Press, New York.     O.Kratky. (1963). X-ray small angle scattering with      substances of biological interest in diluted solutions.      Prog. Biophys. Chem., 13, 105-173.     G.D.Wignall & F.S.Bates, (1987). The small-angle approximation      of X-ray and neutron scatter from rigid rods of non-uniform      cross section and finite length. J.Appl. Crystallog., 18, 452-460.  If the structure is elongated, the mean radius of gyration of the cross-sectional structure R_XS  and the mean cross sectional intensity at zero angle [I(Q).Q]_Q->0 is obtained from    ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
		self._enter('min_mean_cross_sectional_radii_gyration', Query)
		return self
	@property
	def min_mean_cross_sectional_radii_gyration_esd(self) -> 'PdbxSolnScatter':
		"""The estimated standard deviation for the minimum mean radius of structural elongation of the sample. In a given solute-solvent contrast, the radius of gyration R_G is a measure of structural elongation if the internal inhomogeneity of scattering densities has no effect. Guiner analysis at low Q give the R_G and the forward scattering at zero angle I(0).     lnl(Q) = lnl(0) - R_G^2Q^2/3  where       Q = 4(pi)sin(theta/lamda)       2theta = scattering angle       lamda = wavelength  The above expression is valid in a QR_G range for extended rod-like particles. The relative I(0)/c values ( where  c = sample concentration) for sample measurements in a constant buffer for a single sample data session, gives the relative masses of the protein(s) studied when referenced against a standard.  see:     O.Glatter & O.Kratky, (1982). Editors of 'Small angle      X-ray Scattering, Academic Press, New York.     O.Kratky. (1963). X-ray small angle scattering with      substances of biological interest in diluted solutions.      Prog. Biophys. Chem., 13, 105-173.     G.D.Wignall & F.S.Bates, (1987). The small-angle approximation      of X-ray and neutron scatter from rigid rods of non-uniform      cross section and finite length. J.Appl. Crystallog., 18, 452-460.  If the structure is elongated, the mean radius of gyration of the cross-sectional structure R_XS  and the mean cross sectional intensity at zero angle [I(Q).Q]_Q->0 is obtained from     ln[I(Q).Q] = ln[l(Q).(Q)]_Q->0 - ((R_XS)^2Q^2)/2"""
		self._enter('min_mean_cross_sectional_radii_gyration_esd', Query)
		return self
	@property
	def num_time_frames(self) -> 'PdbxSolnScatter':
		"""The number of time frame solution scattering images used."""
		self._enter('num_time_frames', Query)
		return self
	@property
	def protein_length(self) -> 'PdbxSolnScatter':
		"""The length (or range) of the protein sample under study. If the solution structure is approximated as an elongated elliptical cyclinder the length L is determined from,    L = sqrt [12( (R_G)^2  -  (R_XS)^2 ) ]  The length should also be given by    L = pi I(0) / [ I(Q).Q]_Q->0"""
		self._enter('protein_length', Query)
		return self
	@property
	def sample_pH(self) -> 'PdbxSolnScatter':
		"""The pH value of the buffered sample."""
		self._enter('sample_pH', Query)
		return self
	@property
	def source_beamline(self) -> 'PdbxSolnScatter':
		"""The beamline name used for the experiment"""
		self._enter('source_beamline', Query)
		return self
	@property
	def source_beamline_instrument(self) -> 'PdbxSolnScatter':
		"""The instrumentation used on the beamline"""
		self._enter('source_beamline_instrument', Query)
		return self
	@property
	def source_class(self) -> 'PdbxSolnScatter':
		"""The general class of the radiation source.  Examples: neutron source, synchrotron """
		self._enter('source_class', Query)
		return self
	@property
	def source_type(self) -> 'PdbxSolnScatter':
		"""The make, model, name or beamline of the source of radiation."""
		self._enter('source_type', Query)
		return self
	@property
	def temperature(self) -> 'PdbxSolnScatter':
		"""The temperature in kelvins at which the experiment  was conducted"""
		self._enter('temperature', Query)
		return self
	@property
	def type(self) -> 'PdbxSolnScatter':
		"""The type of solution scattering experiment carried out  Allowable values: modelling, neutron, x-ray """
		self._enter('type', Query)
		return self

class PdbxSolnScatterModel(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def conformer_selection_criteria(self) -> 'PdbxSolnScatterModel':
		"""A description of the conformer selection criteria  used.  Examples: The modelled scattering curves were assessed by calculation of the    RG, RSX-1 and RXS-2 values in the same Q ranges    used in the experimental Guinier fits. models were    then ranked using a goodness-of-fit R-factor    defined by analogy with protein crystallography    and based on the experimental curves in the Q range    extending to 1.4 nm-1. """
		self._enter('conformer_selection_criteria', Query)
		return self
	@property
	def details(self) -> 'PdbxSolnScatterModel':
		"""A description of any additional details concerning the experiment.  Examples: Homology models were built for     the 17 SCR domains and energy minimisations were     performed to improve the connectivity in the fh model.     triantennary complex-type carbohydrate structures     (MAN3GLCNAC6GAL3FUC3NEUNAC1) were added to each of the     N-linked glycosylation sites. a library of linker peptide     conformations was used in domain modelling constrained     by the solution scattering fits. modelling with the     scattering data was also carried out by rotational     search methods. the x-ray and neutron scattering curve     I(Q) was calculated assuming a uniform scattering density     for the spheres using the debye equation as adapted to     spheres. x-ray curves were calculated from the hydrated     sphere models without corrections for wavelength spread or     beam divergence, while these corrections were applied for     the neutron curves but now using unhydrated models. """
		self._enter('details', Query)
		return self
	@property
	def entry_fitting_list(self) -> 'PdbxSolnScatterModel':
		"""A list of the entries used to fit the model  to the scattering data  Examples: PDB CODE 1HFI, 1HCC, 1HFH, 1VCC """
		self._enter('entry_fitting_list', Query)
		return self
	@property
	def id(self) -> 'PdbxSolnScatterModel':
		"""The value of _pdbx_soln_scatter_model.id must  uniquely identify the sample in the category PDBX_SOLN_SCATTER_MODEL"""
		self._enter('id', Query)
		return self
	@property
	def method(self) -> 'PdbxSolnScatterModel':
		"""A description of the methods used in the modelling  Examples: Constrained scattering fitting of homology models """
		self._enter('method', Query)
		return self
	@property
	def num_conformers_calculated(self) -> 'PdbxSolnScatterModel':
		"""The number of model conformers calculated."""
		self._enter('num_conformers_calculated', Query)
		return self
	@property
	def num_conformers_submitted(self) -> 'PdbxSolnScatterModel':
		"""The number of model conformers submitted in the entry"""
		self._enter('num_conformers_submitted', Query)
		return self
	@property
	def representative_conformer(self) -> 'PdbxSolnScatterModel':
		"""The index of the representative conformer among the submitted conformers for the entry"""
		self._enter('representative_conformer', Query)
		return self
	@property
	def scatter_id(self) -> 'PdbxSolnScatterModel':
		"""This data item is a pointer to  _pdbx_soln_scatter.id in the  PDBX_SOLN_SCATTER category."""
		self._enter('scatter_id', Query)
		return self
	@property
	def software_author_list(self) -> 'PdbxSolnScatterModel':
		"""A list of the software authors  Examples: MSI """
		self._enter('software_author_list', Query)
		return self
	@property
	def software_list(self) -> 'PdbxSolnScatterModel':
		"""A list of the software used in the modeeling  Examples: INSIGHT II, HOMOLOGY, DISCOVERY, BIOPOLYMER, DELPHI """
		self._enter('software_list', Query)
		return self

class PdbxStructAssembly(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'PdbxStructAssembly':
		"""A description of special aspects of the macromolecular assembly.                 In the PDB, 'representative helical assembly', 'complete point assembly', 	       'complete icosahedral assembly', 'software_defined_assembly', 'author_defined_assembly', 	       and 'author_and_software_defined_assembly' are considered 'biologically relevant assemblies.  Examples: The icosahedral virus particle. """
		self._enter('details', Query)
		return self
	@property
	def id(self) -> 'PdbxStructAssembly':
		"""The value of _pdbx_struct_assembly.id must uniquely identify a record in  the PDBX_STRUCT_ASSEMBLY list."""
		self._enter('id', Query)
		return self
	@property
	def method_details(self) -> 'PdbxStructAssembly':
		"""Provides details of the method used to determine or  compute the assembly."""
		self._enter('method_details', Query)
		return self
	@property
	def oligomeric_count(self) -> 'PdbxStructAssembly':
		"""The number of polymer molecules in the assembly."""
		self._enter('oligomeric_count', Query)
		return self
	@property
	def oligomeric_details(self) -> 'PdbxStructAssembly':
		"""Provides the details of the oligomeric state of the assembly.  Examples: monomer, octameric, tetradecameric, eicosameric, 21-meric, 60-meric, 180-meric, helical """
		self._enter('oligomeric_details', Query)
		return self
	@property
	def rcsb_candidate_assembly(self) -> 'PdbxStructAssembly':
		"""Candidate macromolecular assembly.   Excludes the following cases classified in pdbx_struct_asembly.details:   'crystal asymmetric unit', 'crystal asymmetric unit, crystal frame', 'helical asymmetric unit',  'helical asymmetric unit, std helical frame','icosahedral 23 hexamer', 'icosahedral asymmetric unit',  'icosahedral asymmetric unit, std point frame','icosahedral pentamer', 'pentasymmetron capsid unit',  'point asymmetric unit', 'point asymmetric unit, std point frame','trisymmetron capsid unit',   and 'deposited_coordinates'.  Allowable values: N, Y """
		self._enter('rcsb_candidate_assembly', Query)
		return self
	@property
	def rcsb_details(self) -> 'PdbxStructAssembly':
		"""A filtered description of the macromolecular assembly.  Allowable values: author_and_software_defined_assembly, author_defined_assembly, software_defined_assembly """
		self._enter('rcsb_details', Query)
		return self

class PdbxStructAssemblyAuthEvidence(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def assembly_id(self) -> 'PdbxStructAssemblyAuthEvidence':
		"""This item references an assembly in pdbx_struct_assembly"""
		self._enter('assembly_id', Query)
		return self
	@property
	def details(self) -> 'PdbxStructAssemblyAuthEvidence':
		"""Provides any additional information regarding the evidence of this assembly  Examples: Homology to bacteriorhodopsin, Helical filament was observed by negative staining and Cryo-EM """
		self._enter('details', Query)
		return self
	@property
	def experimental_support(self) -> 'PdbxStructAssemblyAuthEvidence':
		"""Provides the experimental method to determine the state of this assembly  Allowable values: NMR Distance Restraints, NMR relaxation study, SAXS, assay for oligomerization, cross-linking, electron microscopy, equilibrium centrifugation, fluorescence resonance energy transfer, gel filtration, homology, immunoprecipitation, isothermal titration calorimetry, light scattering, mass spectrometry, microscopy, native gel electrophoresis, none, scanning transmission electron microscopy, surface plasmon resonance """
		self._enter('experimental_support', Query)
		return self
	@property
	def id(self) -> 'PdbxStructAssemblyAuthEvidence':
		"""Identifies a unique record in pdbx_struct_assembly_auth_evidence."""
		self._enter('id', Query)
		return self

class PdbxStructAssemblyGen(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def assembly_id(self) -> 'PdbxStructAssemblyGen':
		"""This data item is a pointer to _pdbx_struct_assembly.id in the  PDBX_STRUCT_ASSEMBLY category."""
		self._enter('assembly_id', Query)
		return self
	@property
	def asym_id_list(self) -> 'PdbxStructAssemblyGen':
		"""This data item is a pointer to _struct_asym.id in  the STRUCT_ASYM category.   This item may be expressed as a comma separated list of identifiers."""
		self._enter('asym_id_list', Query)
		return self
	@property
	def oper_expression(self) -> 'PdbxStructAssemblyGen':
		"""Identifies the operation of collection of operations  from category PDBX_STRUCT_OPER_LIST.   Operation expressions may have the forms:    (1)        the single operation 1   (1,2,5)    the operations 1, 2, 5   (1-4)      the operations 1,2,3 and 4   (1,2)(3,4) the combinations of operations              3 and 4 followed by 1 and 2 (i.e.              the cartesian product of parenthetical              groups applied from right to left)  Examples: (1), (1,2,5), (1-60), (1-60)(61) """
		self._enter('oper_expression', Query)
		return self
	@property
	def ordinal(self) -> 'PdbxStructAssemblyGen':
		"""This data item is an ordinal index for the  PDBX_STRUCT_ASSEMBLY category."""
		self._enter('ordinal', Query)
		return self

class PdbxStructAssemblyProp(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def assembly_id(self) -> 'PdbxStructAssemblyProp':
		"""The identifier for the assembly used in category PDBX_STRUCT_ASSEMBLY."""
		self._enter('assembly_id', Query)
		return self
	@property
	def biol_id(self) -> 'PdbxStructAssemblyProp':
		"""The identifier for the assembly used in category PDBX_STRUCT_ASSEMBLY."""
		self._enter('biol_id', Query)
		return self
	@property
	def type(self) -> 'PdbxStructAssemblyProp':
		"""The property type for the assembly.  Allowable values: ABSA (A^2), MORE, SSA (A^2) """
		self._enter('type', Query)
		return self
	@property
	def value(self) -> 'PdbxStructAssemblyProp':
		"""The value of the assembly property."""
		self._enter('value', Query)
		return self

class PdbxStructOperList(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def id(self) -> 'PdbxStructOperList':
		"""This identifier code must uniquely identify a  record in the PDBX_STRUCT_OPER_LIST list."""
		self._enter('id', Query)
		return self
	@property
	def matrix_1_1(self) -> 'PdbxStructOperList':
		"""The [1][1] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_1_1', Query)
		return self
	@property
	def matrix_1_2(self) -> 'PdbxStructOperList':
		"""The [1][2] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_1_2', Query)
		return self
	@property
	def matrix_1_3(self) -> 'PdbxStructOperList':
		"""The [1][3] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_1_3', Query)
		return self
	@property
	def matrix_2_1(self) -> 'PdbxStructOperList':
		"""The [2][1] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_2_1', Query)
		return self
	@property
	def matrix_2_2(self) -> 'PdbxStructOperList':
		"""The [2][2] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_2_2', Query)
		return self
	@property
	def matrix_2_3(self) -> 'PdbxStructOperList':
		"""The [2][3] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_2_3', Query)
		return self
	@property
	def matrix_3_1(self) -> 'PdbxStructOperList':
		"""The [3][1] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_3_1', Query)
		return self
	@property
	def matrix_3_2(self) -> 'PdbxStructOperList':
		"""The [3][2] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_3_2', Query)
		return self
	@property
	def matrix_3_3(self) -> 'PdbxStructOperList':
		"""The [3][3] element of the 3x3 matrix component of the  transformation operation."""
		self._enter('matrix_3_3', Query)
		return self
	@property
	def name(self) -> 'PdbxStructOperList':
		"""A descriptive name for the transformation operation.  Examples: 1_555, two-fold rotation """
		self._enter('name', Query)
		return self
	@property
	def symmetry_operation(self) -> 'PdbxStructOperList':
		"""The symmetry operation corresponding to the transformation operation.  Examples: x,y,z, x+1/2,y,-z """
		self._enter('symmetry_operation', Query)
		return self
	@property
	def type(self) -> 'PdbxStructOperList':
		"""A code to indicate the type of operator.  Allowable values: 2D crystal symmetry operation, 3D crystal symmetry operation, build 2D crystal asymmetric unit, build 3D crystal asymmetric unit, build helical asymmetric unit, build point asymmetric unit, crystal symmetry operation, helical symmetry operation, identity operation, point symmetry operation, transform to 2D crystal frame, transform to 3D crystal frame, transform to crystal frame, transform to helical frame, transform to point frame """
		self._enter('type', Query)
		return self
	@property
	def vector_1(self) -> 'PdbxStructOperList':
		"""The [1] element of the three-element vector component of the  transformation operation."""
		self._enter('vector_1', Query)
		return self
	@property
	def vector_2(self) -> 'PdbxStructOperList':
		"""The [2] element of the three-element vector component of the  transformation operation."""
		self._enter('vector_2', Query)
		return self
	@property
	def vector_3(self) -> 'PdbxStructOperList':
		"""The [3] element of the three-element vector component of the  transformation operation."""
		self._enter('vector_3', Query)
		return self

class PdbxStructSpecialSymmetry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def PDB_model_num(self) -> 'PdbxStructSpecialSymmetry':
		"""Part of the identifier for the molecular component.  This data item is a pointer to _atom_site.pdbx_PDB_model_num in the ATOM_SITE category."""
		self._enter('PDB_model_num', Query)
		return self
	@property
	def auth_seq_id(self) -> 'PdbxStructSpecialSymmetry':
		"""Part of the identifier for the molecular component.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
		self._enter('auth_seq_id', Query)
		return self
	@property
	def id(self) -> 'PdbxStructSpecialSymmetry':
		"""The value of _pdbx_struct_special_symmetry.id must uniquely identify  each item in the PDBX_STRUCT_SPECIAL_SYMMETRY list.   This is an integer serial number."""
		self._enter('id', Query)
		return self
	@property
	def label_asym_id(self) -> 'PdbxStructSpecialSymmetry':
		"""Part of the identifier for the molecular component.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'PdbxStructSpecialSymmetry':
		"""Part of the identifier for the molecular component.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self

class PdbxVrptSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def RNA_suiteness(self) -> 'PdbxVrptSummary':
		"""The MolProbity conformer-match quality parameter for RNA structures. Low values are worse. Specific to structures that contain RNA polymers.  Examples: null """
		self._enter('RNA_suiteness', Query)
		return self
	@property
	def attempted_validation_steps(self) -> 'PdbxVrptSummary':
		"""The steps that were attempted by the validation pipeline software.  A step typically involves running a 3rd party validation tool, for instance 'mogul' Each step will be enumerated in _pdbx_vrpt_software category."""
		self._enter('attempted_validation_steps', Query)
		return self
	@property
	def ligands_for_buster_report(self) -> 'PdbxVrptSummary':
		"""A flag indicating if there are ligands in the model used for detailed Buster analysis.  Allowable values: N, Y """
		self._enter('ligands_for_buster_report', Query)
		return self
	@property
	def report_creation_date(self) -> 'PdbxVrptSummary':
		"""The date, time and time-zone that the validation report  was created.  The string will be formatted like yyyy-mm-dd:hh:mm in GMT time."""
		self._enter('report_creation_date', Query)
		return self
	@property
	def restypes_notchecked_for_bond_angle_geometry(self) -> 'PdbxVrptSummary':
		"""This is a comma separated list of the residue types whose bond lengths and bond angles have  not been checked against 'standard geometry' using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)"""
		self._enter('restypes_notchecked_for_bond_angle_geometry', Query)
		return self

class PdbxVrptSummaryDiffraction(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def B_factor_type(self) -> 'PdbxVrptSummaryDiffraction':
		"""An indicator if isotropic B factors are partial or full values.  Allowable values: FULL, PARTIAL """
		self._enter('B_factor_type', Query)
		return self
	@property
	def Babinet_b(self) -> 'PdbxVrptSummaryDiffraction':
		"""REFMAC scaling parameter as reported in log output line starting 'bulk solvent: scale'. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
		self._enter('Babinet_b', Query)
		return self
	@property
	def Babinet_k(self) -> 'PdbxVrptSummaryDiffraction':
		"""REFMAC scaling parameter as reported in log output line starting 'bulk solvent: scale'. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
		self._enter('Babinet_k', Query)
		return self
	@property
	def CCP4_version(self) -> 'PdbxVrptSummaryDiffraction':
		"""The version of CCP4 suite used in the analysis."""
		self._enter('CCP4_version', Query)
		return self
	@property
	def DCC_R(self) -> 'PdbxVrptSummaryDiffraction':
		"""The overall R-factor from a DCC recalculation of an electron density map. Currently value is rounded to 2 decimal places. X-ray entry specific, obtained from the DCC program."""
		self._enter('DCC_R', Query)
		return self
	@property
	def DCC_Rfree(self) -> 'PdbxVrptSummaryDiffraction':
		"""Rfree as calculated by DCC."""
		self._enter('DCC_Rfree', Query)
		return self
	@property
	def EDS_R(self) -> 'PdbxVrptSummaryDiffraction':
		"""The overall R factor from the EDS REFMAC calculation (no free set is used in this). Currently value is rounded to 2 decimal places. X-ray entry specific, obtained in the eds step from REFMAC calculation."""
		self._enter('EDS_R', Query)
		return self
	@property
	def EDS_R_warning(self) -> 'PdbxVrptSummaryDiffraction':
		"""Warning message when EDS calculated R vs reported R is higher than a threshold"""
		self._enter('EDS_R_warning', Query)
		return self
	@property
	def EDS_res_high(self) -> 'PdbxVrptSummaryDiffraction':
		"""The data high resolution diffraction limit, in Angstroms, found in the input structure factor file. X-ray entry specific, obtained in the EDS step."""
		self._enter('EDS_res_high', Query)
		return self
	@property
	def EDS_res_low(self) -> 'PdbxVrptSummaryDiffraction':
		"""The data low resolution diffraction limit, in Angstroms, found in the input structure factor file. X-ray entry specific, obtained in the EDS step."""
		self._enter('EDS_res_low', Query)
		return self
	@property
	def Fo_Fc_correlation(self) -> 'PdbxVrptSummaryDiffraction':
		"""Fo,Fc correlation: The difference between the observed structure factors (Fo) and the  calculated structure factors (Fc) measures the correlation between the model and the experimental data.  X-ray entry specific, obtained in the eds step from REFMAC calculation."""
		self._enter('Fo_Fc_correlation', Query)
		return self
	@property
	def I_over_sigma(self) -> 'PdbxVrptSummaryDiffraction':
		"""Each reflection has an intensity (I) and an uncertainty in measurement  (sigma(I)), so I/sigma(I) is the signal-to-noise ratio. This ratio decreases at higher resolution. <I/sigma(I)> is the mean of individual I/sigma(I) values. Value for outer resolution shell is given in parentheses. In case structure factor amplitudes are deposited, Xtriage estimates the intensities first and then calculates this metric. When intensities are available in the deposited file, these are converted to amplitudes and then back to intensity estimate before calculating the metric.   X-ray entry specific, calculated by Phenix Xtriage program."""
		self._enter('I_over_sigma', Query)
		return self
	@property
	def Padilla_Yeates_L2_mean(self) -> 'PdbxVrptSummaryDiffraction':
		"""Padilla and Yeates twinning parameter <|L**2|>. Theoretical values is 0.333 in the untwinned case, and 0.2 in the perfectly twinned case. X-ray entry specific, obtained from the Xtriage program."""
		self._enter('Padilla_Yeates_L2_mean', Query)
		return self
	@property
	def Padilla_Yeates_L_mean(self) -> 'PdbxVrptSummaryDiffraction':
		"""Padilla and Yeates twinning parameter <|L|>. Theoretical values is 0.5 in the untwinned case, and 0.375 in the perfectly twinned case. X-ray entry specific, obtained from the Xtriage program."""
		self._enter('Padilla_Yeates_L_mean', Query)
		return self
	@property
	def Q_score(self) -> 'PdbxVrptSummaryDiffraction':
		"""The overall Q-score of the fit of coordinates to the electron map. The Q-score is defined in Pintilie, GH. et al., Nature Methods, 17, 328-334 (2020)"""
		self._enter('Q_score', Query)
		return self
	@property
	def Wilson_B_aniso(self) -> 'PdbxVrptSummaryDiffraction':
		"""Result of absolute likelihood based Wilson scaling,  The anisotropic B value of the data is determined using a likelihood based approach.  The resulting B tensor is reported, the 3 diagonal values are given first, followed by the 3 off diagonal values. A large spread in (especially the diagonal) values indicates anisotropy.  X-ray entry specific, calculated by Phenix Xtriage program."""
		self._enter('Wilson_B_aniso', Query)
		return self
	@property
	def Wilson_B_estimate(self) -> 'PdbxVrptSummaryDiffraction':
		"""An estimate of the overall B-value of the structure, calculated from the diffraction data.  Units Angstroms squared. It serves as an indicator of the degree of order in the crystal and the value is usually  not hugely different from the average B-value calculated from the model. X-ray entry specific, calculated by Phenix Xtriage program."""
		self._enter('Wilson_B_estimate', Query)
		return self
	@property
	def acentric_outliers(self) -> 'PdbxVrptSummaryDiffraction':
		"""The number of acentric reflections that Xtriage identifies as outliers on the basis  of Wilson statistics. Note that if pseudo translational symmetry is present,  a large number of 'outliers' will be present. X-ray entry specific, calculated by Phenix Xtriage program."""
		self._enter('acentric_outliers', Query)
		return self
	@property
	def bulk_solvent_b(self) -> 'PdbxVrptSummaryDiffraction':
		"""REFMAC scaling parameter as reported in log output file. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
		self._enter('bulk_solvent_b', Query)
		return self
	@property
	def bulk_solvent_k(self) -> 'PdbxVrptSummaryDiffraction':
		"""REFMAC reported scaling parameter. X-ray entry specific, obtained in the EDS step from REFMAC calculation."""
		self._enter('bulk_solvent_k', Query)
		return self
	@property
	def centric_outliers(self) -> 'PdbxVrptSummaryDiffraction':
		"""The number of centric reflections that Xtriage identifies as outliers. X-ray entry specific, calculated by Phenix Xtriage program."""
		self._enter('centric_outliers', Query)
		return self
	@property
	def data_anisotropy(self) -> 'PdbxVrptSummaryDiffraction':
		"""The ratio (Bmax - Bmin) / Bmean where Bmax, Bmin and Bmean are computed from the B-values  associated with the principal axes of the anisotropic thermal ellipsoid.  This ratio is usually less than 0.5; for only 1% of PDB entries it is more than 1.0 (Read et al., 2011). X-ray entry specific, obtained from the Xtriage program."""
		self._enter('data_anisotropy', Query)
		return self
	@property
	def data_completeness(self) -> 'PdbxVrptSummaryDiffraction':
		"""The percent completeness of diffraction data."""
		self._enter('data_completeness', Query)
		return self
	@property
	def density_fitness_version(self) -> 'PdbxVrptSummaryDiffraction':
		"""The version of density-fitness suite programs used in the analysis."""
		self._enter('density_fitness_version', Query)
		return self
	@property
	def exp_method(self) -> 'PdbxVrptSummaryDiffraction':
		"""Experimental method for statistics"""
		self._enter('exp_method', Query)
		return self
	@property
	def num_miller_indices(self) -> 'PdbxVrptSummaryDiffraction':
		"""The number of Miller Indices reported by the Xtriage program. This should be the same as the number of _refln in the input structure factor file. X-ray entry specific, calculated by Phenix Xtriage program."""
		self._enter('num_miller_indices', Query)
		return self
	@property
	def number_reflns_R_free(self) -> 'PdbxVrptSummaryDiffraction':
		"""The number of reflections in the free set as defined in the input structure factor file supplied to the validation pipeline.  X-ray entry specific, obtained from the DCC program."""
		self._enter('number_reflns_R_free', Query)
		return self
	@property
	def percent_RSRZ_outliers(self) -> 'PdbxVrptSummaryDiffraction':
		"""The percent of RSRZ outliers."""
		self._enter('percent_RSRZ_outliers', Query)
		return self
	@property
	def percent_free_reflections(self) -> 'PdbxVrptSummaryDiffraction':
		"""A percentage, Normally percent proportion of the total number. Between 0% and 100%."""
		self._enter('percent_free_reflections', Query)
		return self
	@property
	def servalcat_version(self) -> 'PdbxVrptSummaryDiffraction':
		"""The version of Servalcat program used in the analysis."""
		self._enter('servalcat_version', Query)
		return self
	@property
	def trans_NCS_details(self) -> 'PdbxVrptSummaryDiffraction':
		"""A sentence giving the result of Xtriage's analysis on translational NCS. X-ray entry specific, obtained from the Xtriage program.  Examples: The largest off-origin peak in the Patterson function is 8.82% of the height of the origin peak. No significant pseudotranslation is detected. """
		self._enter('trans_NCS_details', Query)
		return self
	@property
	def twin_fraction(self) -> 'PdbxVrptSummaryDiffraction':
		"""Estimated twinning fraction for operators as identified by Xtriage. A semicolon separated list of operators with fractions is givens  X-ray entry specific, obtained from the Xtriage program.  Examples: h,h-k,h-l:0.477;-h,-h+k,-l:0.020;-h,-k,-h+l:0.017 """
		self._enter('twin_fraction', Query)
		return self

class PdbxVrptSummaryEm(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def Q_score(self) -> 'PdbxVrptSummaryEm':
		"""The overall Q-score of the fit of coordinates to the electron map. The Q-score is defined in Pintilie, GH. et al., Nature Methods, 17, 328-334 (2020)"""
		self._enter('Q_score', Query)
		return self
	@property
	def atom_inclusion_all_atoms(self) -> 'PdbxVrptSummaryEm':
		"""The proportion of all non hydrogen atoms within density."""
		self._enter('atom_inclusion_all_atoms', Query)
		return self
	@property
	def atom_inclusion_backbone(self) -> 'PdbxVrptSummaryEm':
		"""The proportion of backbone atoms within density."""
		self._enter('atom_inclusion_backbone', Query)
		return self
	@property
	def author_provided_fsc_resolution_by_cutoff_halfbit(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the author provided fsc and the indicator curve halfbit."""
		self._enter('author_provided_fsc_resolution_by_cutoff_halfbit', Query)
		return self
	@property
	def author_provided_fsc_resolution_by_cutoff_onebit(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the author provided fsc and the indicator curve onebit."""
		self._enter('author_provided_fsc_resolution_by_cutoff_onebit', Query)
		return self
	@property
	def author_provided_fsc_resolution_by_cutoff_pt_143(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the author provided fsc and the indicator curve 0.143."""
		self._enter('author_provided_fsc_resolution_by_cutoff_pt_143', Query)
		return self
	@property
	def author_provided_fsc_resolution_by_cutoff_pt_333(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the author provided fsc and the indicator curve 0.333."""
		self._enter('author_provided_fsc_resolution_by_cutoff_pt_333', Query)
		return self
	@property
	def author_provided_fsc_resolution_by_cutoff_pt_5(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the author provided fsc and the indicator curve 0.5."""
		self._enter('author_provided_fsc_resolution_by_cutoff_pt_5', Query)
		return self
	@property
	def author_provided_fsc_resolution_by_cutoff_threesigma(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the author provided fsc and the indicator curve threesigma."""
		self._enter('author_provided_fsc_resolution_by_cutoff_threesigma', Query)
		return self
	@property
	def calculated_fsc_resolution_by_cutoff_halfbit(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve halfbit."""
		self._enter('calculated_fsc_resolution_by_cutoff_halfbit', Query)
		return self
	@property
	def calculated_fsc_resolution_by_cutoff_onebit(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve onebit."""
		self._enter('calculated_fsc_resolution_by_cutoff_onebit', Query)
		return self
	@property
	def calculated_fsc_resolution_by_cutoff_pt_143(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve 0.143."""
		self._enter('calculated_fsc_resolution_by_cutoff_pt_143', Query)
		return self
	@property
	def calculated_fsc_resolution_by_cutoff_pt_333(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve 0.333."""
		self._enter('calculated_fsc_resolution_by_cutoff_pt_333', Query)
		return self
	@property
	def calculated_fsc_resolution_by_cutoff_pt_5(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve 0.5."""
		self._enter('calculated_fsc_resolution_by_cutoff_pt_5', Query)
		return self
	@property
	def calculated_fsc_resolution_by_cutoff_threesigma(self) -> 'PdbxVrptSummaryEm':
		"""The resolution from the intersection of the fsc curve generated by from the provided halfmaps and the indicator curve threesigma."""
		self._enter('calculated_fsc_resolution_by_cutoff_threesigma', Query)
		return self
	@property
	def contour_level_primary_map(self) -> 'PdbxVrptSummaryEm':
		"""The recommended contour level for the primary map of this deposition."""
		self._enter('contour_level_primary_map', Query)
		return self
	@property
	def exp_method(self) -> 'PdbxVrptSummaryEm':
		"""Experimental method for statistics"""
		self._enter('exp_method', Query)
		return self

class PdbxVrptSummaryEntityFitToMap(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def PDB_model_num(self) -> 'PdbxVrptSummaryEntityFitToMap':
		"""The unique model number from _atom_site.pdbx_PDB_model_num."""
		self._enter('PDB_model_num', Query)
		return self
	@property
	def Q_score(self) -> 'PdbxVrptSummaryEntityFitToMap':
		"""The calculated average Q-score."""
		self._enter('Q_score', Query)
		return self
	@property
	def average_residue_inclusion(self) -> 'PdbxVrptSummaryEntityFitToMap':
		"""The average of the residue inclusions for all residues in this instance"""
		self._enter('average_residue_inclusion', Query)
		return self

class PdbxVrptSummaryEntityGeometry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def PDB_model_num(self) -> 'PdbxVrptSummaryEntityGeometry':
		"""The unique model number from _atom_site.pdbx_PDB_model_num."""
		self._enter('PDB_model_num', Query)
		return self
	@property
	def angles_RMSZ(self) -> 'PdbxVrptSummaryEntityGeometry':
		"""The overall root mean square of the Z-score for deviations of bond angles in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
		self._enter('angles_RMSZ', Query)
		return self
	@property
	def average_residue_inclusion(self) -> 'PdbxVrptSummaryEntityGeometry':
		"""The average of the residue inclusions for all residues in this instance"""
		self._enter('average_residue_inclusion', Query)
		return self
	@property
	def bonds_RMSZ(self) -> 'PdbxVrptSummaryEntityGeometry':
		"""The overall root mean square of the Z-score for deviations of bond lengths in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
		self._enter('bonds_RMSZ', Query)
		return self
	@property
	def num_angles_RMSZ(self) -> 'PdbxVrptSummaryEntityGeometry':
		"""The number of bond angles compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
		self._enter('num_angles_RMSZ', Query)
		return self
	@property
	def num_bonds_RMSZ(self) -> 'PdbxVrptSummaryEntityGeometry':
		"""The number of bond lengths compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996)."""
		self._enter('num_bonds_RMSZ', Query)
		return self

class PdbxVrptSummaryGeometry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def angles_RMSZ(self) -> 'PdbxVrptSummaryGeometry':
		"""The overall root mean square of the Z-score for deviations of bond angles in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
		self._enter('angles_RMSZ', Query)
		return self
	@property
	def bonds_RMSZ(self) -> 'PdbxVrptSummaryGeometry':
		"""The overall root mean square of the Z-score for deviations of bond lengths in comparison to  'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
		self._enter('bonds_RMSZ', Query)
		return self
	@property
	def clashscore(self) -> 'PdbxVrptSummaryGeometry':
		"""This score is derived from the number of pairs of atoms in the PDB_model_num that are unusually close to each other.  It is calculated by the MolProbity pdbx_vrpt_software and expressed as the number or such clashes per thousand atoms. For structures determined by NMR the clashscore value here will only consider label_atom_id pairs in the  well-defined (core) residues from ensemble analysis."""
		self._enter('clashscore', Query)
		return self
	@property
	def clashscore_full_length(self) -> 'PdbxVrptSummaryGeometry':
		"""Only given for structures determined by NMR. The MolProbity pdbx_vrpt_instance_clashes score for all label_atom_id pairs."""
		self._enter('clashscore_full_length', Query)
		return self
	@property
	def num_H_reduce(self) -> 'PdbxVrptSummaryGeometry':
		"""This is the number of hydrogen atoms added and optimized by the MolProbity reduce pdbx_vrpt_software as part of the all-atom clashscore."""
		self._enter('num_H_reduce', Query)
		return self
	@property
	def num_angles_RMSZ(self) -> 'PdbxVrptSummaryGeometry':
		"""The number of bond angles compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
		self._enter('num_angles_RMSZ', Query)
		return self
	@property
	def num_bonds_RMSZ(self) -> 'PdbxVrptSummaryGeometry':
		"""The number of bond lengths compared to 'standard geometry' made using the MolProbity dangle program. Standard geometry parameters are taken from Engh and Huber (2001) and Parkinson et al. (1996). This value is for all chains in the structure."""
		self._enter('num_bonds_RMSZ', Query)
		return self
	@property
	def percent_ramachandran_outliers(self) -> 'PdbxVrptSummaryGeometry':
		"""The percentage of residues with Ramachandran outliers."""
		self._enter('percent_ramachandran_outliers', Query)
		return self
	@property
	def percent_ramachandran_outliers_full_length(self) -> 'PdbxVrptSummaryGeometry':
		"""Only given for structures determined by NMR. The MolProbity Ramachandran outlier score for all atoms in the structure rather than just the well-defined (core) residues."""
		self._enter('percent_ramachandran_outliers_full_length', Query)
		return self
	@property
	def percent_rotamer_outliers(self) -> 'PdbxVrptSummaryGeometry':
		"""The MolProbity sidechain outlier score (a percentage). Protein sidechains mostly adopt certain (combinations of) preferred torsion angle values  (called rotamers or rotameric conformers), much like their backbone torsion angles  (as assessed in the Ramachandran analysis). MolProbity considers the sidechain conformation  of a residue to be an outlier if its set of torsion angles is not similar to any preferred  combination. The sidechain outlier score is calculated as the percentage of residues  with an unusual sidechain conformation with respect to the total number of residues for  which the assessment is available. Example: percent-rota-outliers='2.44'. Specific to structure that contain protein chains and have sidechains modelled. For NMR structures only the  well-defined (core) residues from ensemble analysis will be considered. The percentage of residues with rotamer outliers."""
		self._enter('percent_rotamer_outliers', Query)
		return self
	@property
	def percent_rotamer_outliers_full_length(self) -> 'PdbxVrptSummaryGeometry':
		"""Only given for structures determined by NMR. The MolProbity sidechain outlier score for all atoms in the structure rather than just the well-defined (core) residues."""
		self._enter('percent_rotamer_outliers_full_length', Query)
		return self

class PdbxVrptSummaryNmr(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def chemical_shift_completeness(self) -> 'PdbxVrptSummaryNmr':
		"""Overall completeness of the chemical shift assignments for the well-defined  regions of the structure."""
		self._enter('chemical_shift_completeness', Query)
		return self
	@property
	def chemical_shift_completeness_full_length(self) -> 'PdbxVrptSummaryNmr':
		"""Overall completeness of the chemical shift assignments for the full  macromolecule or complex as suggested by the molecular description of an entry (whether some portion of it is modelled or not)."""
		self._enter('chemical_shift_completeness_full_length', Query)
		return self
	@property
	def cyrange_error(self) -> 'PdbxVrptSummaryNmr':
		"""Diagnostic message from the wrapper of Cyrange software which identifies the  well-defined cores (domains) of NMR protein structures."""
		self._enter('cyrange_error', Query)
		return self
	@property
	def cyrange_number_of_domains(self) -> 'PdbxVrptSummaryNmr':
		"""Total number of well-defined cores (domains) identified by Cyrange"""
		self._enter('cyrange_number_of_domains', Query)
		return self
	@property
	def exp_method(self) -> 'PdbxVrptSummaryNmr':
		"""Experimental method for statistics"""
		self._enter('exp_method', Query)
		return self
	@property
	def medoid_model(self) -> 'PdbxVrptSummaryNmr':
		"""For each Cyrange well-defined core ('cyrange_domain') the id of the PDB_model_num which is most  similar to other models as measured by pairwise RMSDs over the domain.  For the whole entry ('Entry'), the medoid PDB_model_num of the largest core is taken as an overall representative of the structure."""
		self._enter('medoid_model', Query)
		return self
	@property
	def nmr_models_consistency_flag(self) -> 'PdbxVrptSummaryNmr':
		"""A flag indicating if all models in the NMR ensemble contain the exact  same atoms ('True') or if the models differ in this respect ('False')."""
		self._enter('nmr_models_consistency_flag', Query)
		return self
	@property
	def nmrclust_error(self) -> 'PdbxVrptSummaryNmr':
		"""Diagnostic message from the wrapper of NMRClust software which clusters NMR models."""
		self._enter('nmrclust_error', Query)
		return self
	@property
	def nmrclust_number_of_clusters(self) -> 'PdbxVrptSummaryNmr':
		"""Total number of clusters in the NMR ensemble identified by NMRClust."""
		self._enter('nmrclust_number_of_clusters', Query)
		return self
	@property
	def nmrclust_number_of_models(self) -> 'PdbxVrptSummaryNmr':
		"""Number of models analysed by NMRClust - should in almost all cases be the same as the number of models in the NMR ensemble."""
		self._enter('nmrclust_number_of_models', Query)
		return self
	@property
	def nmrclust_number_of_outliers(self) -> 'PdbxVrptSummaryNmr':
		"""Number of models that do not belong to any cluster as deemed by NMRClust."""
		self._enter('nmrclust_number_of_outliers', Query)
		return self
	@property
	def nmrclust_representative_model(self) -> 'PdbxVrptSummaryNmr':
		"""Overall representative PDB_model_num of the NMR ensemble as identified by NMRClust."""
		self._enter('nmrclust_representative_model', Query)
		return self

class Query(QueryNode):
	"""Query root"""
	@property
	def end(self) -> 'QueryNode':
		"""Return to parent (QueryNode)"""
		return self._parent if self._parent else self
	def polymer_entity_instance(self, **kwargs) -> 'CorePolymerEntityInstance':
		"""Get a polymer entity instance (chain), given the ENTRY ID and ENTITY INSTANCE ID. Here ENTITY INSTANCE ID identifies structural element in the asymmetric unit, e.g. 'A', 'B', etc."""
		return self._enter('polymer_entity_instance', CorePolymerEntityInstance, **kwargs)
	def chem_comps(self, **kwargs) -> 'CoreChemComp':
		"""Get a list of chemical components given the list of CHEMICAL COMPONENT ID, e.g. 'CFF', 'HEM', 'FE'.For nucleic acid polymer entities, use the one-letter code for the base."""
		return self._enter('chem_comps', CoreChemComp, **kwargs)
	def nonpolymer_entity_groups(self, **kwargs) -> 'GroupNonPolymerEntity':
		"""Given a list of group IDs get a list of group objects formed by aggregating non-polymer entities that share a degree of similarity"""
		return self._enter('nonpolymer_entity_groups', GroupNonPolymerEntity, **kwargs)
	def polymer_entity_groups(self, **kwargs) -> 'GroupPolymerEntity':
		"""Given a list of group IDs get a list of group objects formed by aggregating polymer entities that share a degree of similarity"""
		return self._enter('polymer_entity_groups', GroupPolymerEntity, **kwargs)
	def interface(self, **kwargs) -> 'CoreInterface':
		"""Get a pairwise polymeric interface given the ENTRY ID, ASSEMBLY ID and INTERFACE ID."""
		return self._enter('interface', CoreInterface, **kwargs)
	def nonpolymer_entities(self, **kwargs) -> 'CoreNonpolymerEntity':
		"""Get a list of non-polymer entities given a list of ENTITY IDs. Here ENTITY ID is a compound identifier that includes entry_id and entity_id separated by '_', e.g. 1XXX_1. Note that the ENTRY ID part must be upper case."""
		return self._enter('nonpolymer_entities', CoreNonpolymerEntity, **kwargs)
	def polymer_entities(self, **kwargs) -> 'CorePolymerEntity':
		"""Get a list of polymer entities given a list of ENTITY IDs. Here ENTITY ID is a compound identifier that includes entry_id and entity_id separated by '_', e.g. 1XXX_1. Note that the ENTRY ID part must be upper case."""
		return self._enter('polymer_entities', CorePolymerEntity, **kwargs)
	def polymer_entity(self, **kwargs) -> 'CorePolymerEntity':
		"""Get a polymer entity, given the ENTRY ID and ENTITY ID. Here ENTITY ID is a '1', '2', '3', etc."""
		return self._enter('polymer_entity', CorePolymerEntity, **kwargs)
	def entry_group(self, **kwargs) -> 'GroupEntry':
		"""Given a group ID get a group object formed by aggregating individual structures that share a degree of similarity"""
		return self._enter('entry_group', GroupEntry, **kwargs)
	def pubmed(self, **kwargs) -> 'CorePubmed':
		"""Get literature information from PubMed database given the PubMed identifier."""
		return self._enter('pubmed', CorePubmed, **kwargs)
	def assembly(self, **kwargs) -> 'CoreAssembly':
		"""Get an assembly given the ENTRY ID and ASSEMBLY ID. Here ASSEMBLY ID is '1', '2', '3', etc. or 'deposited' for deposited coordinates."""
		return self._enter('assembly', CoreAssembly, **kwargs)
	def branched_entity_instances(self, **kwargs) -> 'CoreBranchedEntityInstance':
		"""Get a list of branched entity instances (chains), given the list of ENTITY INSTANCE IDs. Here ENTITY INSTANCE ID identifies structural element in the asymmetric unit, e.g. 'A', 'B', etc."""
		return self._enter('branched_entity_instances', CoreBranchedEntityInstance, **kwargs)
	def group_provenance(self, **kwargs) -> 'GroupProvenance':
		"""Given a group provenance ID get an object that describes aggregation method used to create groups"""
		return self._enter('group_provenance', GroupProvenance, **kwargs)
	def polymer_entity_instances(self, **kwargs) -> 'CorePolymerEntityInstance':
		"""Get a list of polymer entity instances (chains), given the list of ENTITY INSTANCE IDs. Here ENTITY INSTANCE ID identifies structural element in the asymmetric unit, e.g. 'A', 'B', etc."""
		return self._enter('polymer_entity_instances', CorePolymerEntityInstance, **kwargs)
	def interfaces(self, **kwargs) -> 'CoreInterface':
		"""Get a list of pairwise polymeric interfaces given a list of INTERFACE IDs. Here INTERFACE ID is a compound identifier that includes entry_id, assembly_id and interface_id e.g. 1XXX-1.1. Note that the ENTRY ID part must be upper case."""
		return self._enter('interfaces', CoreInterface, **kwargs)
	def nonpolymer_entity_group(self, **kwargs) -> 'GroupNonPolymerEntity':
		"""Given a group ID get a group object formed by aggregating non-polymer entities that share a degree of similarity"""
		return self._enter('nonpolymer_entity_group', GroupNonPolymerEntity, **kwargs)
	def assemblies(self, **kwargs) -> 'CoreAssembly':
		"""Get a list of assemblies given the list of ASSEMBLY IDs. Here an ASSEMBLY ID is a compound identifier that includes entry_id and assembly_id separated by '-', e.g. 1XXX-1."""
		return self._enter('assemblies', CoreAssembly, **kwargs)
	def branched_entity(self, **kwargs) -> 'CoreBranchedEntity':
		"""Get a branched entity, given the ENTRY ID and ENTITY ID. Here ENTITY ID is a '1', '2', '3', etc."""
		return self._enter('branched_entity', CoreBranchedEntity, **kwargs)
	def polymer_entity_group(self, **kwargs) -> 'GroupPolymerEntity':
		"""Given a group ID get a group object formed by aggregating polymer entities that share a degree of similarity"""
		return self._enter('polymer_entity_group', GroupPolymerEntity, **kwargs)
	def branched_entity_instance(self, **kwargs) -> 'CoreBranchedEntityInstance':
		"""Get a branched entity instance (chain), given the ENTRY ID and ENTITY INSTANCE ID. Here ENTITY INSTANCE ID identifies structural element in the asymmetric unit, e.g. 'A', 'B', etc."""
		return self._enter('branched_entity_instance', CoreBranchedEntityInstance, **kwargs)
	def nonpolymer_entity_instance(self, **kwargs) -> 'CoreNonpolymerEntityInstance':
		"""Get a non-polymer entity instance (chain), given the ENTRY ID and ENTITY INSTANCE ID. Here ENTITY INSTANCE ID identifies structural element in the asymmetric unit, e.g. 'A', 'B', etc."""
		return self._enter('nonpolymer_entity_instance', CoreNonpolymerEntityInstance, **kwargs)
	def chem_comp(self, **kwargs) -> 'CoreChemComp':
		"""Get a chemical component given the CHEMICAL COMPONENT ID, e.g. 'CFF', 'HEM', 'FE'.For nucleic acid polymer entities, use the one-letter code for the base."""
		return self._enter('chem_comp', CoreChemComp, **kwargs)
	def entry(self, **kwargs) -> 'CoreEntry':
		"""Get entry given the id."""
		return self._enter('entry', CoreEntry, **kwargs)
	def entries(self, **kwargs) -> 'CoreEntry':
		"""Get a list of entries given a list of IDs."""
		return self._enter('entries', CoreEntry, **kwargs)
	def entry_groups(self, **kwargs) -> 'GroupEntry':
		"""Given a list of group IDs get a list of group objects formed by aggregating structures that share a degree of similarity"""
		return self._enter('entry_groups', GroupEntry, **kwargs)
	def branched_entities(self, **kwargs) -> 'CoreBranchedEntity':
		"""Get a list of branched entities given a list of ENTITY IDs. Here ENTITY ID is a compound identifier that includes entry_id and entity_id separated by '_', e.g. 1XXX_1. Note that the ENTRY ID part must be upper case."""
		return self._enter('branched_entities', CoreBranchedEntity, **kwargs)
	def uniprot(self, **kwargs) -> 'CoreUniprot':
		"""Get UniProt KB entry given the UniProt primary accession."""
		return self._enter('uniprot', CoreUniprot, **kwargs)
	def nonpolymer_entity_instances(self, **kwargs) -> 'CoreNonpolymerEntityInstance':
		"""Get a list of non-polymer entity instances (chains), given the list of ENTITY INSTANCE IDs. Here ENTITY INSTANCE ID identifies structural element in the asymmetric unit, e.g. 'A', 'B', etc."""
		return self._enter('nonpolymer_entity_instances', CoreNonpolymerEntityInstance, **kwargs)
	def nonpolymer_entity(self, **kwargs) -> 'CoreNonpolymerEntity':
		"""Get a non-polymer entity, given the ENTRY ID and ENTITY ID. Here ENTITY ID is a '1', '2', '3', etc."""
		return self._enter('nonpolymer_entity', CoreNonpolymerEntity, **kwargs)

class RcsbAccessionInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def deposit_date(self) -> 'RcsbAccessionInfo':
		"""The entry deposition date.  Examples: 2020-07-11, 2013-10-01 """
		self._enter('deposit_date', Query)
		return self
	@property
	def has_released_experimental_data(self) -> 'RcsbAccessionInfo':
		"""A code indicating the current availibility of experimental data in the repository.  Allowable values: N, Y """
		self._enter('has_released_experimental_data', Query)
		return self
	@property
	def initial_release_date(self) -> 'RcsbAccessionInfo':
		"""The entry initial release date.  Examples: 2020-01-10, 2018-01-23 """
		self._enter('initial_release_date', Query)
		return self
	@property
	def major_revision(self) -> 'RcsbAccessionInfo':
		"""The latest entry major revision number."""
		self._enter('major_revision', Query)
		return self
	@property
	def minor_revision(self) -> 'RcsbAccessionInfo':
		"""The latest entry minor revision number."""
		self._enter('minor_revision', Query)
		return self
	@property
	def revision_date(self) -> 'RcsbAccessionInfo':
		"""The latest entry revision date.  Examples: 2020-02-11, 2018-10-23 """
		self._enter('revision_date', Query)
		return self
	@property
	def status_code(self) -> 'RcsbAccessionInfo':
		"""The release status for the entry.  Allowable values: AUCO, AUTH, HOLD, HPUB, POLC, PROC, REFI, REL, REPL, WAIT, WDRN """
		self._enter('status_code', Query)
		return self

class RcsbAssemblyAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbAssemblyAnnotationAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbAssemblyAnnotationAdditionalProperties)
	@property
	def annotation_id(self) -> 'RcsbAssemblyAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def assignment_version(self) -> 'RcsbAssemblyAnnotation':
		"""Identifies the version of the annotation assignment."""
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbAssemblyAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbAssemblyAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbAssemblyAnnotation':
		"""Code identifying the individual, organization or program that assigned the annotation.  Examples: MCSA """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbAssemblyAnnotation':
		"""A type or category of the annotation.  Allowable values: MCSA """
		self._enter('type', Query)
		return self

class RcsbAssemblyAnnotationAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbAssemblyAnnotation':
		"""Return to parent (RcsbAssemblyAnnotation)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbAssemblyAnnotationAdditionalProperties':
		"""The additional property name.  Allowable values: MCSA_MOTIF_COMPATIBILITY """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbAssemblyAnnotationAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbAssemblyContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def assembly_id(self) -> 'RcsbAssemblyContainerIdentifiers':
		"""Assembly identifier for the container.  Examples: 1, 5 """
		self._enter('assembly_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbAssemblyContainerIdentifiers':
		"""Entry identifier for the container."""
		self._enter('entry_id', Query)
		return self
	@property
	def interface_ids(self) -> 'RcsbAssemblyContainerIdentifiers':
		"""List of binary interface Ids within the assembly (it points to interface id collection)."""
		self._enter('interface_ids', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbAssemblyContainerIdentifiers':
		"""A unique identifier for each object in this assembly container formed by  a dash separated concatenation of entry and assembly identifiers.  Examples: 1KIP-1 """
		self._enter('rcsb_id', Query)
		return self

class RcsbAssemblyFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbAssemblyFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbAssemblyFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbAssemblyFeature':
		"""Identifies the version of the feature assignment."""
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbAssemblyFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbAssemblyFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'RcsbAssemblyFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', RcsbAssemblyFeatureFeaturePositions)
	@property
	def name(self) -> 'RcsbAssemblyFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbAssemblyFeature':
		"""Code identifying the individual, organization or program that assigned the feature.  Examples: MCSA """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbAssemblyFeature':
		"""A type or category of the feature.  Allowable values: MCSA """
		self._enter('type', Query)
		return self

class RcsbAssemblyFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbAssemblyFeature':
		"""Return to parent (RcsbAssemblyFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbAssemblyFeatureAdditionalProperties':
		"""The additional property name.  Allowable values: MCSA_MOTIF_COMPATIBILITY """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbAssemblyFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbAssemblyFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbAssemblyFeature':
		"""Return to parent (RcsbAssemblyFeature)"""
		return self._parent if self._parent else self
	@property
	def asym_id(self) -> 'RcsbAssemblyFeatureFeaturePositions':
		"""An identifier of polymer chain (label_asym_id) corresponding to the feature assignment.  Examples: A, B """
		self._enter('asym_id', Query)
		return self
	@property
	def beg_seq_id(self) -> 'RcsbAssemblyFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature begins."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'RcsbAssemblyFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature ends."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def struct_oper_list(self) -> 'RcsbAssemblyFeatureFeaturePositions':
		"""Identifies the list of operations from the category pdbx_struct_oper_list. One item in array per operator applied. The order follows how operators are applied."""
		self._enter('struct_oper_list', Query)
		return self
	@property
	def values(self) -> 'RcsbAssemblyFeatureFeaturePositions':
		"""The value(s) of the feature over the monomer segment."""
		self._enter('values', Query)
		return self

class RcsbAssemblyInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def assembly_id(self) -> 'RcsbAssemblyInfo':
		"""Entity identifier for the container."""
		self._enter('assembly_id', Query)
		return self
	@property
	def atom_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly non-hydrogen atomic coordinate count."""
		self._enter('atom_count', Query)
		return self
	@property
	def branched_atom_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly non-hydrogen branched entity atomic coordinate count."""
		self._enter('branched_atom_count', Query)
		return self
	@property
	def branched_entity_count(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct branched entities in the generated assembly."""
		self._enter('branched_entity_count', Query)
		return self
	@property
	def branched_entity_instance_count(self) -> 'RcsbAssemblyInfo':
		"""The number of branched instances in the generated assembly data set.  This is the total count of branched entity instances generated in the assembly coordinate data."""
		self._enter('branched_entity_instance_count', Query)
		return self
	@property
	def deuterated_water_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly deuterated water molecule count."""
		self._enter('deuterated_water_count', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbAssemblyInfo':
		"""The PDB entry accession code.  Examples: 1KIP """
		self._enter('entry_id', Query)
		return self
	@property
	def hydrogen_atom_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly hydrogen atomic coordinate count."""
		self._enter('hydrogen_atom_count', Query)
		return self
	@property
	def modeled_polymer_monomer_count(self) -> 'RcsbAssemblyInfo':
		"""The number of modeled polymer monomers in the assembly coordinate data.  This is the total count of monomers with reported coordinate data for all polymer  entity instances in the generated assembly coordinate data."""
		self._enter('modeled_polymer_monomer_count', Query)
		return self
	@property
	def na_polymer_entity_types(self) -> 'RcsbAssemblyInfo':
		"""Nucleic acid polymer entity type categories describing the generated assembly.  Allowable values: DNA (only), DNA/RNA (only), NA-hybrid (only), Other, RNA (only) """
		self._enter('na_polymer_entity_types', Query)
		return self
	@property
	def nonpolymer_atom_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly non-hydrogen non-polymer entity atomic coordinate count."""
		self._enter('nonpolymer_atom_count', Query)
		return self
	@property
	def nonpolymer_entity_count(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct non-polymer entities in the generated assembly exclusive of solvent."""
		self._enter('nonpolymer_entity_count', Query)
		return self
	@property
	def nonpolymer_entity_instance_count(self) -> 'RcsbAssemblyInfo':
		"""The number of non-polymer instances in the generated assembly data set exclusive of solvent.  This is the total count of non-polymer entity instances generated in the assembly coordinate data."""
		self._enter('nonpolymer_entity_instance_count', Query)
		return self
	@property
	def num_heterologous_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of heterologous (both binding sites are different) interface entities"""
		self._enter('num_heterologous_interface_entities', Query)
		return self
	@property
	def num_heteromeric_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of heteromeric (both partners are different polymeric entities) interface entities"""
		self._enter('num_heteromeric_interface_entities', Query)
		return self
	@property
	def num_homomeric_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of homomeric (both partners are the same polymeric entity) interface entities"""
		self._enter('num_homomeric_interface_entities', Query)
		return self
	@property
	def num_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of polymer-polymer interface entities, grouping equivalent interfaces at the entity level (i.e. same entity_ids on either side, with similar but not identical binding sites)"""
		self._enter('num_interface_entities', Query)
		return self
	@property
	def num_interfaces(self) -> 'RcsbAssemblyInfo':
		"""Number of geometrically equivalent (i.e. same asym_ids on either side) polymer-polymer interfaces in the assembly"""
		self._enter('num_interfaces', Query)
		return self
	@property
	def num_isologous_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of isologous (both binding sites are same, i.e. interface is symmetric) interface entities"""
		self._enter('num_isologous_interface_entities', Query)
		return self
	@property
	def num_na_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of nucleic acid-nucleic acid interface entities"""
		self._enter('num_na_interface_entities', Query)
		return self
	@property
	def num_prot_na_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of protein-nucleic acid interface entities"""
		self._enter('num_prot_na_interface_entities', Query)
		return self
	@property
	def num_protein_interface_entities(self) -> 'RcsbAssemblyInfo':
		"""Number of protein-protein interface entities"""
		self._enter('num_protein_interface_entities', Query)
		return self
	@property
	def polymer_atom_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly non-hydrogen polymer entity atomic coordinate count."""
		self._enter('polymer_atom_count', Query)
		return self
	@property
	def polymer_composition(self) -> 'RcsbAssemblyInfo':
		"""Categories describing the polymer entity composition for the generated assembly.  Allowable values: DNA, DNA/RNA, NA-hybrid, NA/oligosaccharide, RNA, heteromeric protein, homomeric protein, oligosaccharide, other, other type composition, other type pair, protein/NA, protein/NA/oligosaccharide, protein/oligosaccharide """
		self._enter('polymer_composition', Query)
		return self
	@property
	def polymer_entity_count(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct polymer entities in the generated assembly."""
		self._enter('polymer_entity_count', Query)
		return self
	@property
	def polymer_entity_count_DNA(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct DNA polymer entities in the generated assembly."""
		self._enter('polymer_entity_count_DNA', Query)
		return self
	@property
	def polymer_entity_count_RNA(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct RNA polymer entities in the generated assembly."""
		self._enter('polymer_entity_count_RNA', Query)
		return self
	@property
	def polymer_entity_count_nucleic_acid(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct nucleic acid polymer entities (DNA or RNA) in the generated assembly."""
		self._enter('polymer_entity_count_nucleic_acid', Query)
		return self
	@property
	def polymer_entity_count_nucleic_acid_hybrid(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct hybrid nucleic acid polymer entities in the generated assembly."""
		self._enter('polymer_entity_count_nucleic_acid_hybrid', Query)
		return self
	@property
	def polymer_entity_count_protein(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct protein polymer entities in the generated assembly."""
		self._enter('polymer_entity_count_protein', Query)
		return self
	@property
	def polymer_entity_instance_count(self) -> 'RcsbAssemblyInfo':
		"""The number of polymer instances in the generated assembly data set.  This is the total count of polymer entity instances generated in the assembly coordinate data."""
		self._enter('polymer_entity_instance_count', Query)
		return self
	@property
	def polymer_entity_instance_count_DNA(self) -> 'RcsbAssemblyInfo':
		"""The number of DNA polymer instances in the generated assembly data set.  This is the total count of DNA polymer entity instances generated in the assembly coordinate data."""
		self._enter('polymer_entity_instance_count_DNA', Query)
		return self
	@property
	def polymer_entity_instance_count_RNA(self) -> 'RcsbAssemblyInfo':
		"""The number of RNA polymer instances in the generated assembly data set.  This is the total count of RNA polymer entity instances generated in the assembly coordinate data."""
		self._enter('polymer_entity_instance_count_RNA', Query)
		return self
	@property
	def polymer_entity_instance_count_nucleic_acid(self) -> 'RcsbAssemblyInfo':
		"""The number of nucleic acid polymer instances in the generated assembly data set.  This is the total count of nucleic acid polymer entity instances generated in the assembly coordinate data."""
		self._enter('polymer_entity_instance_count_nucleic_acid', Query)
		return self
	@property
	def polymer_entity_instance_count_nucleic_acid_hybrid(self) -> 'RcsbAssemblyInfo':
		"""The number of hybrid nucleic acide polymer instances in the generated assembly data set.  This is the total count of hybrid nucleic acid polymer entity instances generated in the assembly coordinate data."""
		self._enter('polymer_entity_instance_count_nucleic_acid_hybrid', Query)
		return self
	@property
	def polymer_entity_instance_count_protein(self) -> 'RcsbAssemblyInfo':
		"""The number of protein polymer instances in the generated assembly data set.  This is the total count of protein polymer entity instances generated in the assembly coordinate data."""
		self._enter('polymer_entity_instance_count_protein', Query)
		return self
	@property
	def polymer_monomer_count(self) -> 'RcsbAssemblyInfo':
		"""The number of polymer monomers in sample entity instances comprising the assembly data set.  This is the total count of monomers for all polymer entity instances  in the generated assembly coordinate data."""
		self._enter('polymer_monomer_count', Query)
		return self
	@property
	def selected_polymer_entity_types(self) -> 'RcsbAssemblyInfo':
		"""Selected polymer entity type categories describing the generated assembly.  Allowable values: Nucleic acid (only), Other, Protein (only), Protein/NA """
		self._enter('selected_polymer_entity_types', Query)
		return self
	@property
	def solvent_atom_count(self) -> 'RcsbAssemblyInfo':
		"""The assembly non-hydrogen solvent atomic coordinate count."""
		self._enter('solvent_atom_count', Query)
		return self
	@property
	def solvent_entity_count(self) -> 'RcsbAssemblyInfo':
		"""The number of distinct solvent entities in the generated assembly."""
		self._enter('solvent_entity_count', Query)
		return self
	@property
	def solvent_entity_instance_count(self) -> 'RcsbAssemblyInfo':
		"""The number of solvent instances in the generated assembly data set.  This is the total count of solvent entity instances generated in the assembly coordinate data."""
		self._enter('solvent_entity_instance_count', Query)
		return self
	@property
	def total_assembly_buried_surface_area(self) -> 'RcsbAssemblyInfo':
		"""Total buried surface area calculated as the sum of buried surface areas over all interfaces"""
		self._enter('total_assembly_buried_surface_area', Query)
		return self
	@property
	def total_number_interface_residues(self) -> 'RcsbAssemblyInfo':
		"""Total number of interfacing residues in the assembly, calculated as the sum of interfacing residues over all interfaces"""
		self._enter('total_number_interface_residues', Query)
		return self
	@property
	def unmodeled_polymer_monomer_count(self) -> 'RcsbAssemblyInfo':
		"""The number of unmodeled polymer monomers in the assembly coordinate data. This is  the total count of monomers with unreported coordinate data for all polymer  entity instances in the generated assembly coordinate data."""
		self._enter('unmodeled_polymer_monomer_count', Query)
		return self

class RcsbBindingAffinity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbBindingAffinity':
		"""Ligand identifier.  Examples: 0WE, SPE, CL """
		self._enter('comp_id', Query)
		return self
	@property
	def link(self) -> 'RcsbBindingAffinity':
		"""Link to external resource referencing the data."""
		self._enter('link', Query)
		return self
	@property
	def provenance_code(self) -> 'RcsbBindingAffinity':
		"""The resource name for the related binding affinity reference.  Allowable values: Binding MOAD, BindingDB, PDBBind """
		self._enter('provenance_code', Query)
		return self
	@property
	def reference_sequence_identity(self) -> 'RcsbBindingAffinity':
		"""Data point provided by BindingDB. Percent identity between PDB sequence and reference sequence."""
		self._enter('reference_sequence_identity', Query)
		return self
	@property
	def symbol(self) -> 'RcsbBindingAffinity':
		"""Binding affinity symbol indicating approximate or precise strength of the binding.  Examples: ~, =, >, <, >=, <= """
		self._enter('symbol', Query)
		return self
	@property
	def type(self) -> 'RcsbBindingAffinity':
		"""Binding affinity measurement given in one of the following types:  The concentration constants: IC50: the concentration of ligand that reduces enzyme activity by 50%;  EC50: the concentration of compound that generates a half-maximal response;  The binding constant:  Kd: dissociation constant;  Ka: association constant;  Ki: enzyme inhibition constant;  The thermodynamic parameters:  delta G: Gibbs free energy of binding (for association reaction);  delta H: change in enthalpy associated with a chemical reaction;  delta S: change in entropy associated with a chemical reaction.  Allowable values: &Delta;G, &Delta;H, -T&Delta;S, EC50, IC50, Ka, Kd, Ki """
		self._enter('type', Query)
		return self
	@property
	def unit(self) -> 'RcsbBindingAffinity':
		"""Binding affinity unit.  Dissociation constant Kd is normally in molar units (or millimolar , micromolar, nanomolar, etc).  Association constant Ka is normally expressed in inverse molar units (e.g. M-1).  Examples: nM, kJ/mol """
		self._enter('unit', Query)
		return self
	@property
	def value(self) -> 'RcsbBindingAffinity':
		"""Binding affinity value between a ligand and its target molecule."""
		self._enter('value', Query)
		return self

class RcsbBirdCitation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def id(self) -> 'RcsbBirdCitation':
		"""The value of _rcsb_bird_citation.id must uniquely identify a record in the  rcsb_bird_citation list.  Examples: 1, 2 """
		self._enter('id', Query)
		return self
	@property
	def journal_abbrev(self) -> 'RcsbBirdCitation':
		"""Abbreviated name of the cited journal as given in the  Chemical Abstracts Service Source Index.  Examples: J.Mol.Biol., J. Mol. Biol. """
		self._enter('journal_abbrev', Query)
		return self
	@property
	def journal_volume(self) -> 'RcsbBirdCitation':
		"""Volume number of the journal cited; relevant for journal  articles.  Examples: 174 """
		self._enter('journal_volume', Query)
		return self
	@property
	def page_first(self) -> 'RcsbBirdCitation':
		"""The first page of the rcsb_bird_citation; relevant for journal  articles, books and book chapters."""
		self._enter('page_first', Query)
		return self
	@property
	def page_last(self) -> 'RcsbBirdCitation':
		"""The last page of the rcsb_bird_citation; relevant for journal  articles, books and book chapters."""
		self._enter('page_last', Query)
		return self
	@property
	def pdbx_database_id_DOI(self) -> 'RcsbBirdCitation':
		"""Document Object Identifier used by doi.org to uniquely  specify bibliographic entry.  Examples: 10.2345/S1384107697000225 """
		self._enter('pdbx_database_id_DOI', Query)
		return self
	@property
	def pdbx_database_id_PubMed(self) -> 'RcsbBirdCitation':
		"""Ascession number used by PubMed to categorize a specific  bibliographic entry."""
		self._enter('pdbx_database_id_PubMed', Query)
		return self
	@property
	def rcsb_authors(self) -> 'RcsbBirdCitation':
		"""Names of the authors of the citation; relevant for journal  articles, books and book chapters.  Names are separated by vertical bars.   The family name(s), followed by a comma and including any  dynastic components, precedes the first name(s) or initial(s)."""
		self._enter('rcsb_authors', Query)
		return self
	@property
	def title(self) -> 'RcsbBirdCitation':
		"""The title of the rcsb_bird_citation; relevant for journal articles, books  and book chapters.  Examples: Structure of diferric duck ovotransferrin                                   at 2.35 Angstroms resolution. """
		self._enter('title', Query)
		return self
	@property
	def year(self) -> 'RcsbBirdCitation':
		"""The year of the rcsb_bird_citation; relevant for journal articles, books  and book chapters."""
		self._enter('year', Query)
		return self

class RcsbBranchedEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'RcsbBranchedEntity':
		"""A description of special aspects of the branched entity."""
		self._enter('details', Query)
		return self
	@property
	def formula_weight(self) -> 'RcsbBranchedEntity':
		"""Formula mass (KDa) of the branched entity.  Examples: null, null """
		self._enter('formula_weight', Query)
		return self
	@property
	def pdbx_description(self) -> 'RcsbBranchedEntity':
		"""A description of the branched entity.  Examples: alpha-D-glucopyranose-(1-6)-beta-D-glucopyranose, beta-D-xylopyranose-(1-4)-beta-D-xylopyranose """
		self._enter('pdbx_description', Query)
		return self
	@property
	def pdbx_number_of_molecules(self) -> 'RcsbBranchedEntity':
		"""The number of molecules of the branched entity in the entry."""
		self._enter('pdbx_number_of_molecules', Query)
		return self

class RcsbBranchedEntityAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def annotation_id(self) -> 'RcsbBranchedEntityAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbBranchedEntityAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbBranchedEntityAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbBranchedEntityAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbBranchedEntityAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbBranchedEntityAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbBranchedEntityAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbBranchedEntityAnnotation':
		"""A type or category of the annotation."""
		self._enter('type', Query)
		return self

class RcsbBranchedEntityAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedEntityAnnotation':
		"""Return to parent (RcsbBranchedEntityAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbBranchedEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbBranchedEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbBranchedEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbBranchedEntityContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def asym_ids(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""Instance identifiers corresponding to copies of the entity in this container."""
		self._enter('asym_ids', Query)
		return self
	@property
	def auth_asym_ids(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""Author instance identifiers corresponding to copies of the entity in this container."""
		self._enter('auth_asym_ids', Query)
		return self
	@property
	def chem_comp_monomers(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""Unique list of monomer chemical component identifiers in the entity in this container."""
		self._enter('chem_comp_monomers', Query)
		return self
	@property
	def chem_ref_def_id(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""The chemical reference definition identifier for the entity in this container.  Examples: PRD_000010 """
		self._enter('chem_ref_def_id', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""Entity identifier for the container.  Examples: 1, 2 """
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""Entry identifier for the container.  Examples: 1B5F, 2HYV """
		self._enter('entry_id', Query)
		return self
	@property
	def prd_id(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""The BIRD identifier for the entity in this container.  Examples: PRD_000010 """
		self._enter('prd_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers.  Examples: 2HYV_2 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def reference_identifiers(self) -> 'RcsbBranchedEntityContainerIdentifiersReferenceIdentifiers':
		""""""
		return self._enter('reference_identifiers', RcsbBranchedEntityContainerIdentifiersReferenceIdentifiers)

class RcsbBranchedEntityContainerIdentifiersReferenceIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedEntityContainerIdentifiers':
		"""Return to parent (RcsbBranchedEntityContainerIdentifiers)"""
		return self._parent if self._parent else self
	@property
	def provenance_source(self) -> 'RcsbBranchedEntityContainerIdentifiersReferenceIdentifiers':
		"""Source of the reference resource assignment  Allowable values: PDB, RCSB """
		self._enter('provenance_source', Query)
		return self
	@property
	def resource_accession(self) -> 'RcsbBranchedEntityContainerIdentifiersReferenceIdentifiers':
		"""Reference resource accession code  Examples: G07411ON, G42666HT """
		self._enter('resource_accession', Query)
		return self
	@property
	def resource_name(self) -> 'RcsbBranchedEntityContainerIdentifiersReferenceIdentifiers':
		"""Reference resource name  Allowable values: GlyCosmos, GlyGen, GlyTouCan """
		self._enter('resource_name', Query)
		return self

class RcsbBranchedEntityFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbBranchedEntityFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbBranchedEntityFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbBranchedEntityFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbBranchedEntityFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbBranchedEntityFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'RcsbBranchedEntityFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', RcsbBranchedEntityFeatureFeaturePositions)
	@property
	def name(self) -> 'RcsbBranchedEntityFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbBranchedEntityFeature':
		"""Code identifying the individual, organization or program that  assigned the feature.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_scheme(self) -> 'RcsbBranchedEntityFeature':
		"""Code residue coordinate system for the assigned feature.  Allowable values: PDB entity """
		self._enter('reference_scheme', Query)
		return self
	@property
	def type(self) -> 'RcsbBranchedEntityFeature':
		"""A type or category of the feature.  Allowable values: mutation """
		self._enter('type', Query)
		return self

class RcsbBranchedEntityFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedEntityFeature':
		"""Return to parent (RcsbBranchedEntityFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbBranchedEntityFeatureAdditionalProperties':
		"""The additional property name."""
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbBranchedEntityFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbBranchedEntityFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedEntityFeature':
		"""Return to parent (RcsbBranchedEntityFeature)"""
		return self._parent if self._parent else self
	@property
	def beg_comp_id(self) -> 'RcsbBranchedEntityFeatureFeaturePositions':
		"""An identifier for the leading monomer corresponding to the feature assignment.  Examples: NAG, MAN """
		self._enter('beg_comp_id', Query)
		return self
	@property
	def beg_seq_id(self) -> 'RcsbBranchedEntityFeatureFeaturePositions':
		"""An identifier for the leading monomer position of the feature."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'RcsbBranchedEntityFeatureFeaturePositions':
		"""An identifier for the leading monomer position of the feature."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def value(self) -> 'RcsbBranchedEntityFeatureFeaturePositions':
		"""The value for the feature at this monomer.  Examples: null, null """
		self._enter('value', Query)
		return self

class RcsbBranchedEntityFeatureSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def count(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""The feature count."""
		self._enter('count', Query)
		return self
	@property
	def coverage(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""The fractional feature coverage relative to the full branched entity.  Examples: null, null """
		self._enter('coverage', Query)
		return self
	@property
	def maximum_length(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""The maximum feature length."""
		self._enter('maximum_length', Query)
		return self
	@property
	def maximum_value(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""The maximum feature value.  Examples: null, null """
		self._enter('maximum_value', Query)
		return self
	@property
	def minimum_length(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""The minimum feature length."""
		self._enter('minimum_length', Query)
		return self
	@property
	def minimum_value(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""The minimum feature value.  Examples: null, null """
		self._enter('minimum_value', Query)
		return self
	@property
	def type(self) -> 'RcsbBranchedEntityFeatureSummary':
		"""Type or category of the feature.  Allowable values: mutation """
		self._enter('type', Query)
		return self

class RcsbBranchedEntityInstanceContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def asym_id(self) -> 'RcsbBranchedEntityInstanceContainerIdentifiers':
		"""Instance identifier for this container."""
		self._enter('asym_id', Query)
		return self
	@property
	def auth_asym_id(self) -> 'RcsbBranchedEntityInstanceContainerIdentifiers':
		"""Author instance identifier for this container."""
		self._enter('auth_asym_id', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbBranchedEntityInstanceContainerIdentifiers':
		"""Entity identifier for the container."""
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbBranchedEntityInstanceContainerIdentifiers':
		"""Entry identifier for the container."""
		self._enter('entry_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbBranchedEntityInstanceContainerIdentifiers':
		"""A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers.  Examples: 1KIP.A """
		self._enter('rcsb_id', Query)
		return self

class RcsbBranchedEntityKeywords(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def text(self) -> 'RcsbBranchedEntityKeywords':
		"""Keywords describing this branched entity."""
		self._enter('text', Query)
		return self

class RcsbBranchedEntityNameCom(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbBranchedEntityNameCom':
		"""A common name for the branched entity.  Examples: HIV protease monomer, hemoglobin alpha chain """
		self._enter('name', Query)
		return self

class RcsbBranchedEntityNameSys(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntity':
		"""Return to parent (CoreBranchedEntity)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbBranchedEntityNameSys':
		"""The systematic name for the branched entity."""
		self._enter('name', Query)
		return self
	@property
	def system(self) -> 'RcsbBranchedEntityNameSys':
		"""The system used to generate the systematic name of the branched entity."""
		self._enter('system', Query)
		return self

class RcsbBranchedInstanceAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def annotation_id(self) -> 'RcsbBranchedInstanceAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbBranchedInstanceAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbBranchedInstanceAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbBranchedInstanceAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbBranchedInstanceAnnotation':
		"""Chemical component identifier.  Examples: ATP """
		self._enter('comp_id', Query)
		return self
	@property
	def description(self) -> 'RcsbBranchedInstanceAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbBranchedInstanceAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbBranchedInstanceAnnotation':
		"""Ordinal identifier for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbBranchedInstanceAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbBranchedInstanceAnnotation':
		"""A type or category of the annotation.  Allowable values: CATH, SCOP """
		self._enter('type', Query)
		return self

class RcsbBranchedInstanceAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedInstanceAnnotation':
		"""Return to parent (RcsbBranchedInstanceAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbBranchedInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbBranchedInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbBranchedInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbBranchedInstanceFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbBranchedInstanceFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbBranchedInstanceFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbBranchedInstanceFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbBranchedInstanceFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbBranchedInstanceFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'RcsbBranchedInstanceFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', RcsbBranchedInstanceFeatureFeaturePositions)
	@property
	def feature_value(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		""""""
		return self._enter('feature_value', RcsbBranchedInstanceFeatureFeatureValue)
	@property
	def name(self) -> 'RcsbBranchedInstanceFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbBranchedInstanceFeature':
		"""Ordinal identifier for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbBranchedInstanceFeature':
		"""Code identifying the individual, organization or program that  assigned the feature.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_scheme(self) -> 'RcsbBranchedInstanceFeature':
		"""Code residue coordinate system for the assigned feature.  Allowable values: PDB entity, PDB entry """
		self._enter('reference_scheme', Query)
		return self
	@property
	def type(self) -> 'RcsbBranchedInstanceFeature':
		"""A type or category of the feature.  Allowable values: BINDING_SITE, CATH, ECOD, MOGUL_ANGLE_OUTLIER, MOGUL_BOND_OUTLIER, RSCC_OUTLIER, RSRZ_OUTLIER, SCOP, STEREO_OUTLIER, UNOBSERVED_ATOM_XYZ, UNOBSERVED_RESIDUE_XYZ, ZERO_OCCUPANCY_ATOM_XYZ, ZERO_OCCUPANCY_RESIDUE_XYZ """
		self._enter('type', Query)
		return self

class RcsbBranchedInstanceFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedInstanceFeature':
		"""Return to parent (RcsbBranchedInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbBranchedInstanceFeatureAdditionalProperties':
		"""The additional property name.  Examples: bond_distance, bond_angle """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbBranchedInstanceFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbBranchedInstanceFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedInstanceFeature':
		"""Return to parent (RcsbBranchedInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def beg_comp_id(self) -> 'RcsbBranchedInstanceFeatureFeaturePositions':
		"""An identifier for the monomer(s) corresponding to the feature assignment.  Examples: NAG, MAN """
		self._enter('beg_comp_id', Query)
		return self
	@property
	def beg_seq_id(self) -> 'RcsbBranchedInstanceFeatureFeaturePositions':
		"""An identifier for the leading monomer feature position."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'RcsbBranchedInstanceFeatureFeaturePositions':
		"""An identifier for the terminal monomer feature position."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def value(self) -> 'RcsbBranchedInstanceFeatureFeaturePositions':
		"""The value of the feature at the monomer position.  Examples: null, null """
		self._enter('value', Query)
		return self
	@property
	def values(self) -> 'RcsbBranchedInstanceFeatureFeaturePositions':
		"""The value(s) of the feature at the monomer position."""
		self._enter('values', Query)
		return self

class RcsbBranchedInstanceFeatureFeatureValue(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedInstanceFeature':
		"""Return to parent (RcsbBranchedInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		"""The chemical component identifier for the instance of the feature value.  Examples: ATP,, STN """
		self._enter('comp_id', Query)
		return self
	@property
	def details(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		"""Specific details about the feature.  Examples: C1,C2, C1,C2,C3 """
		self._enter('details', Query)
		return self
	@property
	def reference(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		"""The reference value of the feature.  Examples: null, null """
		self._enter('reference', Query)
		return self
	@property
	def reported(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		"""The reported value of the feature.  Examples: null, null """
		self._enter('reported', Query)
		return self
	@property
	def uncertainty_estimate(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		"""The estimated uncertainty of the reported feature value.  Examples: null, null """
		self._enter('uncertainty_estimate', Query)
		return self
	@property
	def uncertainty_estimate_type(self) -> 'RcsbBranchedInstanceFeatureFeatureValue':
		"""The type of estimated uncertainty for the reported feature value.  Allowable values: Z-Score """
		self._enter('uncertainty_estimate_type', Query)
		return self

class RcsbBranchedInstanceFeatureSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def count(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""The feature count."""
		self._enter('count', Query)
		return self
	@property
	def coverage(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""The fractional feature coverage relative to the full branched entity.  Examples: null, null """
		self._enter('coverage', Query)
		return self
	@property
	def maximum_length(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""The maximum feature length."""
		self._enter('maximum_length', Query)
		return self
	@property
	def maximum_value(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""The maximum feature value.  Examples: null, null """
		self._enter('maximum_value', Query)
		return self
	@property
	def minimum_length(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""The minimum feature length."""
		self._enter('minimum_length', Query)
		return self
	@property
	def minimum_value(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""The minimum feature value.  Examples: null, null """
		self._enter('minimum_value', Query)
		return self
	@property
	def type(self) -> 'RcsbBranchedInstanceFeatureSummary':
		"""Type or category of the feature.  Allowable values: BINDING_SITE, CATH, MOGUL_ANGLE_OUTLIER, MOGUL_BOND_OUTLIER, RSCC_OUTLIER, RSRZ_OUTLIER, SCOP, STEREO_OUTLIER, UNOBSERVED_ATOM_XYZ, UNOBSERVED_RESIDUE_XYZ, ZERO_OCCUPANCY_ATOM_XYZ, ZERO_OCCUPANCY_RESIDUE_XYZ """
		self._enter('type', Query)
		return self

class RcsbBranchedStructConn(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def connect_partner(self) -> 'RcsbBranchedStructConnConnectPartner':
		""""""
		return self._enter('connect_partner', RcsbBranchedStructConnConnectPartner)
	@property
	def connect_target(self) -> 'RcsbBranchedStructConnConnectTarget':
		""""""
		return self._enter('connect_target', RcsbBranchedStructConnConnectTarget)
	@property
	def connect_type(self) -> 'RcsbBranchedStructConn':
		"""The connection type.  Allowable values: covalent bond, hydrogen bond, ionic interaction, metal coordination, mismatched base pairs """
		self._enter('connect_type', Query)
		return self
	@property
	def description(self) -> 'RcsbBranchedStructConn':
		"""A description of special details of the connection.  Examples: Watson-Crick base pair """
		self._enter('description', Query)
		return self
	@property
	def dist_value(self) -> 'RcsbBranchedStructConn':
		"""Distance value for this contact."""
		self._enter('dist_value', Query)
		return self
	@property
	def id(self) -> 'RcsbBranchedStructConn':
		"""The value of _rcsb_branched_struct_conn.id is an identifier for connection."""
		self._enter('id', Query)
		return self
	@property
	def ordinal_id(self) -> 'RcsbBranchedStructConn':
		"""The value of _rcsb_branched_struct_conn.id must uniquely identify a record in  the rcsb_branched_struct_conn list."""
		self._enter('ordinal_id', Query)
		return self
	@property
	def role(self) -> 'RcsbBranchedStructConn':
		"""The chemical or structural role of the interaction  Allowable values: C-Mannosylation, N-Glycosylation, O-Glycosylation """
		self._enter('role', Query)
		return self
	@property
	def value_order(self) -> 'RcsbBranchedStructConn':
		"""The chemical bond order associated with the specified atoms in  this contact.  Allowable values: doub, quad, sing, trip """
		self._enter('value_order', Query)
		return self

class RcsbBranchedStructConnConnectPartner(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedStructConn':
		"""Return to parent (RcsbBranchedStructConn)"""
		return self._parent if self._parent else self
	@property
	def label_alt_id(self) -> 'RcsbBranchedStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
		self._enter('label_alt_id', Query)
		return self
	@property
	def label_asym_id(self) -> 'RcsbBranchedStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_atom_id(self) -> 'RcsbBranchedStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _chem_comp_atom.atom_id in the  CHEM_COMP_ATOM category."""
		self._enter('label_atom_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'RcsbBranchedStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self
	@property
	def label_seq_id(self) -> 'RcsbBranchedStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_seq_id in the  ATOM_SITE category."""
		self._enter('label_seq_id', Query)
		return self
	@property
	def symmetry(self) -> 'RcsbBranchedStructConnConnectPartner':
		"""Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_branched_struct_conn.connect_partner_label* to generate the  partner in the structure connection.  Examples: 1_555, 7_645 """
		self._enter('symmetry', Query)
		return self

class RcsbBranchedStructConnConnectTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbBranchedStructConn':
		"""Return to parent (RcsbBranchedStructConn)"""
		return self._parent if self._parent else self
	@property
	def auth_asym_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_asym_id in the  ATOM_SITE category."""
		self._enter('auth_asym_id', Query)
		return self
	@property
	def auth_seq_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
		self._enter('auth_seq_id', Query)
		return self
	@property
	def label_alt_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
		self._enter('label_alt_id', Query)
		return self
	@property
	def label_asym_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_atom_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_atom_id in the  ATOM_SITE category."""
		self._enter('label_atom_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self
	@property
	def label_seq_id(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.connect_target_label_seq_id in the  ATOM_SITE category."""
		self._enter('label_seq_id', Query)
		return self
	@property
	def symmetry(self) -> 'RcsbBranchedStructConnConnectTarget':
		"""Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_branched_struct_conn.label* to generate the  target of the structure connection.  Examples: 1_555, 7_645 """
		self._enter('symmetry', Query)
		return self

class RcsbChemCompAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def annotation_id(self) -> 'RcsbChemCompAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbChemCompAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbChemCompAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbChemCompAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbChemCompAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbChemCompAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbChemCompAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: RESID, UniProt, PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbChemCompAnnotation':
		"""A type or category of the annotation.  Allowable values: ATC, Carbohydrate Anomer, Carbohydrate Isomer, Carbohydrate Primary Carbonyl Group, Carbohydrate Ring, Generating Enzyme, Modification Type, PSI-MOD """
		self._enter('type', Query)
		return self

class RcsbChemCompAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbChemCompAnnotation':
		"""Return to parent (RcsbChemCompAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbChemCompAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbChemCompAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbChemCompAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbChemCompContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def atc_codes(self) -> 'RcsbChemCompContainerIdentifiers':
		"""The Anatomical Therapeutic Chemical (ATC) Classification System identifiers corresponding  to the chemical component."""
		self._enter('atc_codes', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbChemCompContainerIdentifiers':
		"""The chemical component identifier.  Examples: ATP, STI """
		self._enter('comp_id', Query)
		return self
	@property
	def drugbank_id(self) -> 'RcsbChemCompContainerIdentifiers':
		"""The DrugBank identifier corresponding to the chemical component.  Examples: DB00781, DB15263 """
		self._enter('drugbank_id', Query)
		return self
	@property
	def prd_id(self) -> 'RcsbChemCompContainerIdentifiers':
		"""The BIRD definition identifier.  Examples: PRD_000010 """
		self._enter('prd_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbChemCompContainerIdentifiers':
		"""A unique identifier for the chemical definition in this container.  Examples: ATP, PRD_000010 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def subcomponent_ids(self) -> 'RcsbChemCompContainerIdentifiers':
		"""The list of subcomponents contained in this component."""
		self._enter('subcomponent_ids', Query)
		return self

class RcsbChemCompDescriptor(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def InChI(self) -> 'RcsbChemCompDescriptor':
		"""Standard IUPAC International Chemical Identifier (InChI) descriptor for the chemical component.     InChI, the IUPAC International Chemical Identifier,    by Stephen R Heller, Alan McNaught, Igor Pletnev, Stephen Stein and Dmitrii Tchekhovskoi,    Journal of Cheminformatics, 2015, 7:23;  Examples: InChI=1S/C3H6FO6P/c4-1-2(3(5)6)10-11(7,8)9/h2H,1H2,(H,5,6)(H2,7,8,9)/t2-/m0/s1 """
		self._enter('InChI', Query)
		return self
	@property
	def InChIKey(self) -> 'RcsbChemCompDescriptor':
		"""Standard IUPAC International Chemical Identifier (InChI) descriptor key  for the chemical component   InChI, the IUPAC International Chemical Identifier,  by Stephen R Heller, Alan McNaught, Igor Pletnev, Stephen Stein and Dmitrii Tchekhovskoi,  Journal of Cheminformatics, 2015, 7:23  Examples: BNOCDEBUFVJMQI-REOHCLBHSA-N """
		self._enter('InChIKey', Query)
		return self
	@property
	def SMILES(self) -> 'RcsbChemCompDescriptor':
		"""Simplified molecular-input line-entry system (SMILES) descriptor for the chemical component.     Weininger D (February 1988). 'SMILES, a chemical language and information system. 1.    Introduction to methodology and encoding rules'. Journal of Chemical Information and Modeling. 28 (1): 31-6.     Weininger D, Weininger A, Weininger JL (May 1989).    'SMILES. 2. Algorithm for generation of unique SMILES notation',    Journal of Chemical Information and Modeling. 29 (2): 97-101.  Examples: OC(=O)[CH](CF)O[P](O)(O)=O """
		self._enter('SMILES', Query)
		return self
	@property
	def SMILES_stereo(self) -> 'RcsbChemCompDescriptor':
		"""Simplified molecular-input line-entry system (SMILES) descriptor for the chemical  component including stereochemical features.   Weininger D (February 1988). 'SMILES, a chemical language and information system. 1.  Introduction to methodology and encoding rules'.  Journal of Chemical Information and Modeling. 28 (1): 31-6.   Weininger D, Weininger A, Weininger JL (May 1989).  'SMILES. 2. Algorithm for generation of unique SMILES notation'.  Journal of Chemical Information and Modeling. 29 (2): 97-101.  Examples: OC(=O)[C@H](CF)O[P](O)(O)=O """
		self._enter('SMILES_stereo', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbChemCompDescriptor':
		"""The chemical component identifier."""
		self._enter('comp_id', Query)
		return self

class RcsbChemCompInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def atom_count(self) -> 'RcsbChemCompInfo':
		"""Chemical component total atom count"""
		self._enter('atom_count', Query)
		return self
	@property
	def atom_count_chiral(self) -> 'RcsbChemCompInfo':
		"""Chemical component chiral atom count"""
		self._enter('atom_count_chiral', Query)
		return self
	@property
	def atom_count_heavy(self) -> 'RcsbChemCompInfo':
		"""Chemical component heavy atom count"""
		self._enter('atom_count_heavy', Query)
		return self
	@property
	def bond_count(self) -> 'RcsbChemCompInfo':
		"""Chemical component total bond count"""
		self._enter('bond_count', Query)
		return self
	@property
	def bond_count_aromatic(self) -> 'RcsbChemCompInfo':
		"""Chemical component aromatic bond count"""
		self._enter('bond_count_aromatic', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbChemCompInfo':
		"""The chemical component identifier."""
		self._enter('comp_id', Query)
		return self
	@property
	def initial_deposition_date(self) -> 'RcsbChemCompInfo':
		"""The date the chemical definition was first deposited in the PDB repository.  Examples: 2016-09-11 """
		self._enter('initial_deposition_date', Query)
		return self
	@property
	def initial_release_date(self) -> 'RcsbChemCompInfo':
		"""The initial date the chemical definition was released in the PDB repository.  Examples: 2016-09-11 """
		self._enter('initial_release_date', Query)
		return self
	@property
	def release_status(self) -> 'RcsbChemCompInfo':
		"""The release status of the chemical definition.  Allowable values: DEL, HOLD, HPUB, OBS, REF_ONLY, REL """
		self._enter('release_status', Query)
		return self
	@property
	def revision_date(self) -> 'RcsbChemCompInfo':
		"""The date of last revision of the chemical definition.  Examples: 2016-10-12 """
		self._enter('revision_date', Query)
		return self

class RcsbChemCompRelated(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbChemCompRelated':
		"""The value of _rcsb_chem_comp_related.comp_id is a reference to  a chemical component definition."""
		self._enter('comp_id', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbChemCompRelated':
		"""The value of _rcsb_chem_comp_related.ordinal distinguishes  related examples for each chemical component."""
		self._enter('ordinal', Query)
		return self
	@property
	def related_mapping_method(self) -> 'RcsbChemCompRelated':
		"""The method used to establish the resource correspondence.  Allowable values: assigned by DrugBank resource, assigned by PDB, assigned by PubChem resource, matching ChEMBL ID in Pharos, matching InChIKey in DrugBank, matching InChIKey in PubChem, matching InChIKey-prefix in DrugBank, matching by RESID resource """
		self._enter('related_mapping_method', Query)
		return self
	@property
	def resource_accession_code(self) -> 'RcsbChemCompRelated':
		"""The resource identifier code for the related chemical reference.  Examples: 124832 """
		self._enter('resource_accession_code', Query)
		return self
	@property
	def resource_name(self) -> 'RcsbChemCompRelated':
		"""The resource name for the related chemical reference.  Allowable values: CAS, CCDC/CSD, COD, ChEBI, ChEMBL, DrugBank, Pharos, PubChem, RESID """
		self._enter('resource_name', Query)
		return self

class RcsbChemCompSynonyms(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbChemCompSynonyms':
		"""The chemical component to which this synonym applies."""
		self._enter('comp_id', Query)
		return self
	@property
	def name(self) -> 'RcsbChemCompSynonyms':
		"""The synonym of this particular chemical component.  Examples: Ursonic acid, Talotrexin, 4-oxodecanedioic acid """
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbChemCompSynonyms':
		"""This data item is an ordinal index for the  RCSB_CHEM_COMP_SYNONYMS category."""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbChemCompSynonyms':
		"""The provenance of this synonym.  Allowable values: ACDLabs, Author, ChEBI, ChEMBL, DrugBank, GMML, Lexichem, OpenEye OEToolkits, OpenEye/Lexichem, PDB Reference Data, PDB Reference Data (Preferred), PDB-CARE, PubChem, RESID """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbChemCompSynonyms':
		"""This data item contains the synonym type.  Allowable values: Brand Name, Common Name, Condensed IUPAC Carbohydrate Symbol, IUPAC Carbohydrate Symbol, Preferred Common Name, Preferred Name, Preferred Synonym, SNFG Carbohydrate Symbol, Synonym, Systematic Name """
		self._enter('type', Query)
		return self

class RcsbChemCompTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbChemCompTarget':
		"""The value of _rcsb_chem_comp_target.comp_id is a reference to  a chemical component definition."""
		self._enter('comp_id', Query)
		return self
	@property
	def interaction_type(self) -> 'RcsbChemCompTarget':
		"""The type of target interaction."""
		self._enter('interaction_type', Query)
		return self
	@property
	def name(self) -> 'RcsbChemCompTarget':
		"""The chemical component target name."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbChemCompTarget':
		"""The value of _rcsb_chem_comp_target.ordinal distinguishes  related examples for each chemical component."""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbChemCompTarget':
		"""A code indicating the provenance of the target interaction assignment  Allowable values: DrugBank, PDB Primary Data """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_database_accession_code(self) -> 'RcsbChemCompTarget':
		"""The reference identifier code for the target interaction reference.  Examples: Q9HD40 """
		self._enter('reference_database_accession_code', Query)
		return self
	@property
	def reference_database_name(self) -> 'RcsbChemCompTarget':
		"""The reference database name for the target interaction.  Allowable values: UniProt """
		self._enter('reference_database_name', Query)
		return self
	@property
	def target_actions(self) -> 'RcsbChemCompTarget':
		"""The mechanism of action of the chemical component - target interaction."""
		self._enter('target_actions', Query)
		return self

class RcsbClusterFlexibility(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def avg_rmsd(self) -> 'RcsbClusterFlexibility':
		"""Average RMSD refer to average pairwise RMSD (Root Mean Square Deviation of C-alpha atoms) between structures in the cluster (95% sequence identity) where a given entity belongs."""
		self._enter('avg_rmsd', Query)
		return self
	@property
	def label(self) -> 'RcsbClusterFlexibility':
		"""Structural flexibility in the cluster (95% sequence identity) where a given entity belongs."""
		self._enter('label', Query)
		return self
	@property
	def link(self) -> 'RcsbClusterFlexibility':
		"""Link to the associated PDBFlex database entry."""
		self._enter('link', Query)
		return self
	@property
	def max_rmsd(self) -> 'RcsbClusterFlexibility':
		"""Maximal RMSD refer to maximal pairwise RMSD (Root Mean Square Deviation of C-alpha atoms) between structures in the cluster (95% sequence identity) where a given entity belongs."""
		self._enter('max_rmsd', Query)
		return self
	@property
	def provenance_code(self) -> 'RcsbClusterFlexibility':
		"""Provenance code indicating the origin of the flexibility data.  Allowable values: PDBFlex """
		self._enter('provenance_code', Query)
		return self

class RcsbClusterMembership(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def cluster_id(self) -> 'RcsbClusterMembership':
		"""Identifier for a cluster at the specified level of sequence identity within the cluster data set."""
		self._enter('cluster_id', Query)
		return self
	@property
	def identity(self) -> 'RcsbClusterMembership':
		"""Sequence identity expressed as an integer percent value."""
		self._enter('identity', Query)
		return self

class RcsbCompModelProvenance(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def entry_id(self) -> 'RcsbCompModelProvenance':
		"""Entry identifier corresponding to the computed structure model.  Examples: AF-P60325-F1, ma-bak-cepc-0019 """
		self._enter('entry_id', Query)
		return self
	@property
	def source_db(self) -> 'RcsbCompModelProvenance':
		"""Source database for the computed structure model.  Allowable values: AlphaFoldDB, ModelArchive """
		self._enter('source_db', Query)
		return self
	@property
	def source_filename(self) -> 'RcsbCompModelProvenance':
		"""Source filename for the computed structure model."""
		self._enter('source_filename', Query)
		return self
	@property
	def source_pae_url(self) -> 'RcsbCompModelProvenance':
		"""Source URL for computed structure model predicted aligned error (PAE) json file."""
		self._enter('source_pae_url', Query)
		return self
	@property
	def source_url(self) -> 'RcsbCompModelProvenance':
		"""Source URL for computed structure model file."""
		self._enter('source_url', Query)
		return self

class RcsbEntityHostOrganism(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def beg_seq_num(self) -> 'RcsbEntityHostOrganism':
		"""The beginning polymer sequence position for the polymer section corresponding  to this host organism.   A reference to the sequence position in the entity_poly category."""
		self._enter('beg_seq_num', Query)
		return self
	@property
	def common_name(self) -> 'RcsbEntityHostOrganism':
		"""The common name of the host organism"""
		self._enter('common_name', Query)
		return self
	@property
	def end_seq_num(self) -> 'RcsbEntityHostOrganism':
		"""The ending polymer sequence position for the polymer section corresponding  to this host organism.   A reference to the sequence position in the entity_poly category."""
		self._enter('end_seq_num', Query)
		return self
	@property
	def ncbi_common_names(self) -> 'RcsbEntityHostOrganism':
		"""Common names associated with this taxonomy code obtained from NCBI Taxonomy Database.    These names correspond to the taxonomy identifier assigned by the PDB depositor.  References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
		self._enter('ncbi_common_names', Query)
		return self
	@property
	def ncbi_parent_scientific_name(self) -> 'RcsbEntityHostOrganism':
		"""The parent scientific name in the NCBI taxonomy hierarchy (depth=1) associated with this taxonomy code.  References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
		self._enter('ncbi_parent_scientific_name', Query)
		return self
	@property
	def ncbi_scientific_name(self) -> 'RcsbEntityHostOrganism':
		"""The scientific name associated with this taxonomy code aggregated by the NCBI Taxonomy Database.    This name corresponds to the taxonomy identifier assigned by the PDB depositor.   References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
		self._enter('ncbi_scientific_name', Query)
		return self
	@property
	def ncbi_taxonomy_id(self) -> 'RcsbEntityHostOrganism':
		"""NCBI Taxonomy identifier for the host organism.    Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('ncbi_taxonomy_id', Query)
		return self
	@property
	def pdbx_src_id(self) -> 'RcsbEntityHostOrganism':
		"""An identifier for an entity segment."""
		self._enter('pdbx_src_id', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbEntityHostOrganism':
		"""A code indicating the provenance of the host organism.  Allowable values: PDB Primary Data, Primary Data """
		self._enter('provenance_source', Query)
		return self
	@property
	def scientific_name(self) -> 'RcsbEntityHostOrganism':
		"""The scientific name of the host organism"""
		self._enter('scientific_name', Query)
		return self
	@property
	def taxonomy_lineage(self) -> 'RcsbEntityHostOrganismTaxonomyLineage':
		""""""
		return self._enter('taxonomy_lineage', RcsbEntityHostOrganismTaxonomyLineage)

class RcsbEntityHostOrganismTaxonomyLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbEntityHostOrganism':
		"""Return to parent (RcsbEntityHostOrganism)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbEntityHostOrganismTaxonomyLineage':
		"""Members of the NCBI Taxonomy lineage as parent taxonomy lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbEntityHostOrganismTaxonomyLineage':
		"""Members of the NCBI Taxonomy lineage as parent taxonomy idcodes.  Examples: 469008, 10469 """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbEntityHostOrganismTaxonomyLineage':
		"""Members of the NCBI Taxonomy lineage as parent taxonomy names.  Examples: Escherichia coli BL21(DE3), Baculovirus """
		self._enter('name', Query)
		return self

class RcsbEntitySourceOrganism(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def beg_seq_num(self) -> 'RcsbEntitySourceOrganism':
		"""The beginning polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('beg_seq_num', Query)
		return self
	@property
	def common_name(self) -> 'RcsbEntitySourceOrganism':
		"""The common name for the source organism assigned by the PDB depositor."""
		self._enter('common_name', Query)
		return self
	@property
	def end_seq_num(self) -> 'RcsbEntitySourceOrganism':
		"""The ending polymer sequence position for the polymer section corresponding  to this source.   A reference to the sequence position in the entity_poly category."""
		self._enter('end_seq_num', Query)
		return self
	@property
	def ncbi_common_names(self) -> 'RcsbEntitySourceOrganism':
		"""Common names associated with this taxonomy code aggregated by the NCBI Taxonomy Database.    These name correspond to the taxonomy identifier assigned by the PDB depositor.  References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
		self._enter('ncbi_common_names', Query)
		return self
	@property
	def ncbi_parent_scientific_name(self) -> 'RcsbEntitySourceOrganism':
		"""A parent scientific name in the NCBI taxonomy hierarchy of the source organism assigned by the PDB depositor.   For cellular organism this corresponds to a superkingdom (e.g., Archaea, Bacteria, Eukaryota).  For viruses this   corresponds to a clade (e.g.  Adnaviria, Bicaudaviridae, Clavaviridae). For other and unclassified entries this   corresponds to the first level of any taxonomic rank below the root level.  References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21.  Examples: Archaea, Bacteria, Eukaryota, Adnaviria, Bicaudaviridae, Clavaviridae, Duplodnaviria """
		self._enter('ncbi_parent_scientific_name', Query)
		return self
	@property
	def ncbi_scientific_name(self) -> 'RcsbEntitySourceOrganism':
		"""The scientific name associated with this taxonomy code aggregated by the NCBI Taxonomy Database.    This name corresponds to the taxonomy identifier assigned by the PDB depositor.   References:  Sayers EW, Barrett T, Benson DA, Bryant SH, Canese K, Chetvernin V, Church DM, DiCuccio M, Edgar R, Federhen S, Feolo M, Geer LY, Helmberg W, Kapustin Y, Landsman D, Lipman DJ, Madden TL, Maglott DR, Miller V, Mizrachi I, Ostell J, Pruitt KD, Schuler GD, Sequeira E, Sherry ST, Shumway M, Sirotkin K, Souvorov A, Starchenko G, Tatusova TA, Wagner L, Yaschenko E, Ye J (2009). Database resources of the National Center for Biotechnology Information. Nucleic Acids Res. 2009 Jan;37(Database issue):D5-15. Epub 2008 Oct 21.  Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Sayers EW (2009). GenBank. Nucleic Acids Res. 2009 Jan;37(Database issue):D26-31. Epub 2008 Oct 21."""
		self._enter('ncbi_scientific_name', Query)
		return self
	@property
	def ncbi_taxonomy_id(self) -> 'RcsbEntitySourceOrganism':
		"""NCBI Taxonomy identifier for the gene source organism assigned by the PDB depositor.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('ncbi_taxonomy_id', Query)
		return self
	@property
	def pdbx_src_id(self) -> 'RcsbEntitySourceOrganism':
		"""An identifier for the entity segment."""
		self._enter('pdbx_src_id', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbEntitySourceOrganism':
		"""Reference to the provenance of the source organism details for the entity.   Primary data indicates information obtained from the same source as the structural model.  UniProt and NCBI are provided as alternate sources of provenance for organism details.  Allowable values: NCBI, PDB Primary Data, Primary Data, UniProt """
		self._enter('provenance_source', Query)
		return self
	@property
	def rcsb_gene_name(self) -> 'RcsbEntitySourceOrganismRcsbGeneName':
		""""""
		return self._enter('rcsb_gene_name', RcsbEntitySourceOrganismRcsbGeneName)
	@property
	def scientific_name(self) -> 'RcsbEntitySourceOrganism':
		"""The scientific name of the source organism assigned by the PDB depositor."""
		self._enter('scientific_name', Query)
		return self
	@property
	def source_type(self) -> 'RcsbEntitySourceOrganism':
		"""The source type for the entity  Allowable values: genetically engineered, natural, synthetic """
		self._enter('source_type', Query)
		return self
	@property
	def taxonomy_lineage(self) -> 'RcsbEntitySourceOrganismTaxonomyLineage':
		""""""
		return self._enter('taxonomy_lineage', RcsbEntitySourceOrganismTaxonomyLineage)

class RcsbEntitySourceOrganismRcsbGeneName(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbEntitySourceOrganism':
		"""Return to parent (RcsbEntitySourceOrganism)"""
		return self._parent if self._parent else self
	@property
	def provenance_source(self) -> 'RcsbEntitySourceOrganismRcsbGeneName':
		"""A code indicating the provenance of the source organism details for the entity  Allowable values: NCBI, PDB Primary Data, Primary Data, UniProt """
		self._enter('provenance_source', Query)
		return self
	@property
	def value(self) -> 'RcsbEntitySourceOrganismRcsbGeneName':
		"""Gene name.  Examples: lacA, hemH """
		self._enter('value', Query)
		return self

class RcsbEntitySourceOrganismTaxonomyLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbEntitySourceOrganism':
		"""Return to parent (RcsbEntitySourceOrganism)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbEntitySourceOrganismTaxonomyLineage':
		"""Members of the NCBI Taxonomy lineage as parent taxonomy lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbEntitySourceOrganismTaxonomyLineage':
		"""Members of the NCBI Taxonomy lineage as parent taxonomy idcodes.  Examples: 9606, 10090 """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbEntitySourceOrganismTaxonomyLineage':
		"""Memebers of the NCBI Taxonomy lineage as parent taxonomy names.  Examples: Homo sapiens, Mus musculus """
		self._enter('name', Query)
		return self

class RcsbEntryContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def assembly_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of identifiers for assemblies generated from the entry."""
		self._enter('assembly_ids', Query)
		return self
	@property
	def branched_entity_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of identifiers for the branched entity constituents for the entry."""
		self._enter('branched_entity_ids', Query)
		return self
	@property
	def emdb_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of EMDB identifiers for the 3D electron microscopy density maps  used in the production of the structure model."""
		self._enter('emdb_ids', Query)
		return self
	@property
	def entity_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of identifiers or the entity constituents for the entry."""
		self._enter('entity_ids', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbEntryContainerIdentifiers':
		"""Entry identifier for the container.  Examples: 4HHB, AF_AFP60325F1, MA_MABAKCEPC0019 """
		self._enter('entry_id', Query)
		return self
	@property
	def model_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of PDB model identifiers for the entry."""
		self._enter('model_ids', Query)
		return self
	@property
	def non_polymer_entity_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of identifiers for the non-polymer entity constituents for the entry."""
		self._enter('non_polymer_entity_ids', Query)
		return self
	@property
	def polymer_entity_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of identifiers for the polymer entity constituents for the entry."""
		self._enter('polymer_entity_ids', Query)
		return self
	@property
	def pubmed_id(self) -> 'RcsbEntryContainerIdentifiers':
		"""Unique integer value assigned to each PubMed record."""
		self._enter('pubmed_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbEntryContainerIdentifiers':
		"""A unique identifier for each object in this entry container.  Examples: 1KIP """
		self._enter('rcsb_id', Query)
		return self
	@property
	def related_emdb_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of EMDB identifiers for the 3D electron microscopy density maps  related to the structure model."""
		self._enter('related_emdb_ids', Query)
		return self
	@property
	def water_entity_ids(self) -> 'RcsbEntryContainerIdentifiers':
		"""List of identifiers for the solvent/water entity constituents for the entry."""
		self._enter('water_entity_ids', Query)
		return self

class RcsbEntryGroupMembership(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def aggregation_method(self) -> 'RcsbEntryGroupMembership':
		"""Method used to establish group membership  Allowable values: matching_deposit_group_id """
		self._enter('aggregation_method', Query)
		return self
	@property
	def group_id(self) -> 'RcsbEntryGroupMembership':
		"""A unique identifier for a group of entries  Examples: G_1001001 """
		self._enter('group_id', Query)
		return self

class RcsbEntryInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def assembly_count(self) -> 'RcsbEntryInfo':
		"""The number of assemblies defined for this entry including the deposited assembly."""
		self._enter('assembly_count', Query)
		return self
	@property
	def branched_entity_count(self) -> 'RcsbEntryInfo':
		"""The number of distinct branched entities in the structure entry."""
		self._enter('branched_entity_count', Query)
		return self
	@property
	def branched_molecular_weight_maximum(self) -> 'RcsbEntryInfo':
		"""The maximum molecular mass (KDa) of a branched entity in the deposited structure entry.  Examples: null, null """
		self._enter('branched_molecular_weight_maximum', Query)
		return self
	@property
	def branched_molecular_weight_minimum(self) -> 'RcsbEntryInfo':
		"""The minimum molecular mass (KDa) of a branched entity in the deposited structure entry.  Examples: null, null """
		self._enter('branched_molecular_weight_minimum', Query)
		return self
	@property
	def cis_peptide_count(self) -> 'RcsbEntryInfo':
		"""The number of cis-peptide linkages per deposited structure model."""
		self._enter('cis_peptide_count', Query)
		return self
	@property
	def deposited_atom_count(self) -> 'RcsbEntryInfo':
		"""The number of heavy atom coordinates records per deposited structure model."""
		self._enter('deposited_atom_count', Query)
		return self
	@property
	def deposited_deuterated_water_count(self) -> 'RcsbEntryInfo':
		"""The number of deuterated water molecules per deposited structure model."""
		self._enter('deposited_deuterated_water_count', Query)
		return self
	@property
	def deposited_hydrogen_atom_count(self) -> 'RcsbEntryInfo':
		"""The number of hydrogen atom coordinates records per deposited structure model."""
		self._enter('deposited_hydrogen_atom_count', Query)
		return self
	@property
	def deposited_model_count(self) -> 'RcsbEntryInfo':
		"""The number of model structures deposited."""
		self._enter('deposited_model_count', Query)
		return self
	@property
	def deposited_modeled_polymer_monomer_count(self) -> 'RcsbEntryInfo':
		"""The number of modeled polymer monomers in the deposited coordinate data.  This is the total count of monomers with reported coordinate data for all polymer  entity instances in the deposited coordinate data."""
		self._enter('deposited_modeled_polymer_monomer_count', Query)
		return self
	@property
	def deposited_nonpolymer_entity_instance_count(self) -> 'RcsbEntryInfo':
		"""The number of non-polymer instances in the deposited data set.  This is the total count of non-polymer entity instances reported  per deposited structure model."""
		self._enter('deposited_nonpolymer_entity_instance_count', Query)
		return self
	@property
	def deposited_polymer_entity_instance_count(self) -> 'RcsbEntryInfo':
		"""The number of polymer instances in the deposited data set.  This is the total count of polymer entity instances reported  per deposited structure model."""
		self._enter('deposited_polymer_entity_instance_count', Query)
		return self
	@property
	def deposited_polymer_monomer_count(self) -> 'RcsbEntryInfo':
		"""The number of polymer monomers in sample entity instances in the deposited data set.  This is the total count of monomers for all polymer entity instances reported  per deposited structure model."""
		self._enter('deposited_polymer_monomer_count', Query)
		return self
	@property
	def deposited_solvent_atom_count(self) -> 'RcsbEntryInfo':
		"""The number of heavy solvent atom coordinates records per deposited structure model."""
		self._enter('deposited_solvent_atom_count', Query)
		return self
	@property
	def deposited_unmodeled_polymer_monomer_count(self) -> 'RcsbEntryInfo':
		"""The number of unmodeled polymer monomers in the deposited coordinate data. This is  the total count of monomers with unreported coordinate data for all polymer  entity instances per deposited structure model."""
		self._enter('deposited_unmodeled_polymer_monomer_count', Query)
		return self
	@property
	def diffrn_radiation_wavelength_maximum(self) -> 'RcsbEntryInfo':
		"""The maximum radiation wavelength in angstroms."""
		self._enter('diffrn_radiation_wavelength_maximum', Query)
		return self
	@property
	def diffrn_radiation_wavelength_minimum(self) -> 'RcsbEntryInfo':
		"""The minimum radiation wavelength in angstroms."""
		self._enter('diffrn_radiation_wavelength_minimum', Query)
		return self
	@property
	def diffrn_resolution_high(self) -> 'RcsbEntryInfoDiffrnResolutionHigh':
		""""""
		return self._enter('diffrn_resolution_high', RcsbEntryInfoDiffrnResolutionHigh)
	@property
	def disulfide_bond_count(self) -> 'RcsbEntryInfo':
		"""The number of disulfide bonds per deposited structure model."""
		self._enter('disulfide_bond_count', Query)
		return self
	@property
	def entity_count(self) -> 'RcsbEntryInfo':
		"""The number of distinct polymer, non-polymer, branched molecular, and solvent entities per deposited structure model."""
		self._enter('entity_count', Query)
		return self
	@property
	def experimental_method(self) -> 'RcsbEntryInfo':
		"""The category of experimental method(s) used to determine the structure entry.  Allowable values: EM, Integrative, Multiple methods, NMR, Neutron, Other, X-ray """
		self._enter('experimental_method', Query)
		return self
	@property
	def experimental_method_count(self) -> 'RcsbEntryInfo':
		"""The number of experimental methods contributing data to the structure determination."""
		self._enter('experimental_method_count', Query)
		return self
	@property
	def ihm_multi_scale_flag(self) -> 'RcsbEntryInfo':
		"""Multi-scale modeling flag for integrative structures.  Allowable values: N, Y """
		self._enter('ihm_multi_scale_flag', Query)
		return self
	@property
	def ihm_multi_state_flag(self) -> 'RcsbEntryInfo':
		"""Multi-state modeling flag for integrative structures.  Allowable values: N, Y """
		self._enter('ihm_multi_state_flag', Query)
		return self
	@property
	def ihm_ordered_state_flag(self) -> 'RcsbEntryInfo':
		"""Ordered-state modeling flag for integrative structures.  Allowable values: N, Y """
		self._enter('ihm_ordered_state_flag', Query)
		return self
	@property
	def ihm_structure_description(self) -> 'RcsbEntryInfo':
		"""Description of the integrative structure."""
		self._enter('ihm_structure_description', Query)
		return self
	@property
	def inter_mol_covalent_bond_count(self) -> 'RcsbEntryInfo':
		"""The number of intermolecular covalent bonds."""
		self._enter('inter_mol_covalent_bond_count', Query)
		return self
	@property
	def inter_mol_metalic_bond_count(self) -> 'RcsbEntryInfo':
		"""The number of intermolecular metalic bonds."""
		self._enter('inter_mol_metalic_bond_count', Query)
		return self
	@property
	def molecular_weight(self) -> 'RcsbEntryInfo':
		"""The molecular mass (KDa) of polymer and non-polymer entities (exclusive of solvent) in the deposited structure entry.  Examples: null, null """
		self._enter('molecular_weight', Query)
		return self
	@property
	def na_polymer_entity_types(self) -> 'RcsbEntryInfo':
		"""Nucleic acid polymer entity type categories describing the entry.  Allowable values: DNA (only), DNA/RNA (only), NA-hybrid (only), Other, RNA (only) """
		self._enter('na_polymer_entity_types', Query)
		return self
	@property
	def ndb_struct_conf_na_feature_combined(self) -> 'RcsbEntryInfo':
		"""This data item identifies secondary structure  features of nucleic acids in the entry.  Allowable values: a-form double helix, b-form double helix, bulge loop, double helix, four-way junction, hairpin loop, internal loop, mismatched base pair, other right-handed double helix, parallel strands, quadruple helix, tetraloop, three-way junction, triple helix, two-way junction, z-form double helix """
		self._enter('ndb_struct_conf_na_feature_combined', Query)
		return self
	@property
	def nonpolymer_bound_components(self) -> 'RcsbEntryInfo':
		"""Bound nonpolymer components in this entry."""
		self._enter('nonpolymer_bound_components', Query)
		return self
	@property
	def nonpolymer_entity_count(self) -> 'RcsbEntryInfo':
		"""The number of distinct non-polymer entities in the structure entry exclusive of solvent."""
		self._enter('nonpolymer_entity_count', Query)
		return self
	@property
	def nonpolymer_molecular_weight_maximum(self) -> 'RcsbEntryInfo':
		"""The maximum molecular mass (KDa) of a non-polymer entity in the deposited structure entry.  Examples: null, null """
		self._enter('nonpolymer_molecular_weight_maximum', Query)
		return self
	@property
	def nonpolymer_molecular_weight_minimum(self) -> 'RcsbEntryInfo':
		"""The minimum molecular mass (KDa) of a non-polymer entity in the deposited structure entry.  Examples: null, null """
		self._enter('nonpolymer_molecular_weight_minimum', Query)
		return self
	@property
	def polymer_composition(self) -> 'RcsbEntryInfo':
		"""Categories describing the polymer entity composition for the entry.  Allowable values: DNA, DNA/RNA, NA-hybrid, NA/oligosaccharide, RNA, heteromeric protein, homomeric protein, oligosaccharide, other, other type composition, other type pair, protein/NA, protein/NA/oligosaccharide, protein/oligosaccharide """
		self._enter('polymer_composition', Query)
		return self
	@property
	def polymer_entity_count(self) -> 'RcsbEntryInfo':
		"""The number of distinct polymer entities in the structure entry."""
		self._enter('polymer_entity_count', Query)
		return self
	@property
	def polymer_entity_count_DNA(self) -> 'RcsbEntryInfo':
		"""The number of distinct DNA polymer entities."""
		self._enter('polymer_entity_count_DNA', Query)
		return self
	@property
	def polymer_entity_count_RNA(self) -> 'RcsbEntryInfo':
		"""The number of distinct RNA polymer entities."""
		self._enter('polymer_entity_count_RNA', Query)
		return self
	@property
	def polymer_entity_count_nucleic_acid(self) -> 'RcsbEntryInfo':
		"""The number of distinct nucleic acid polymer entities (DNA or RNA)."""
		self._enter('polymer_entity_count_nucleic_acid', Query)
		return self
	@property
	def polymer_entity_count_nucleic_acid_hybrid(self) -> 'RcsbEntryInfo':
		"""The number of distinct hybrid nucleic acid polymer entities."""
		self._enter('polymer_entity_count_nucleic_acid_hybrid', Query)
		return self
	@property
	def polymer_entity_count_protein(self) -> 'RcsbEntryInfo':
		"""The number of distinct protein polymer entities."""
		self._enter('polymer_entity_count_protein', Query)
		return self
	@property
	def polymer_entity_taxonomy_count(self) -> 'RcsbEntryInfo':
		"""The number of distinct taxonomies represented among the polymer entities in the entry."""
		self._enter('polymer_entity_taxonomy_count', Query)
		return self
	@property
	def polymer_molecular_weight_maximum(self) -> 'RcsbEntryInfo':
		"""The maximum molecular mass (KDa) of a polymer entity in the deposited structure entry.  Examples: null, null """
		self._enter('polymer_molecular_weight_maximum', Query)
		return self
	@property
	def polymer_molecular_weight_minimum(self) -> 'RcsbEntryInfo':
		"""The minimum molecular mass (KDa) of a polymer entity in the deposited structure entry.  Examples: null, null """
		self._enter('polymer_molecular_weight_minimum', Query)
		return self
	@property
	def polymer_monomer_count_maximum(self) -> 'RcsbEntryInfo':
		"""The maximum monomer count of a polymer entity per deposited structure model."""
		self._enter('polymer_monomer_count_maximum', Query)
		return self
	@property
	def polymer_monomer_count_minimum(self) -> 'RcsbEntryInfo':
		"""The minimum monomer count of a polymer entity per deposited structure model."""
		self._enter('polymer_monomer_count_minimum', Query)
		return self
	@property
	def representative_model(self) -> 'RcsbEntryInfo':
		"""The chosen representative model."""
		self._enter('representative_model', Query)
		return self
	@property
	def resolution_combined(self) -> 'RcsbEntryInfo':
		"""Combined estimates of experimental resolution contributing to the refined structural model.  Resolution reported in 'refine.ls_d_res_high' is used for X-RAY DIFFRACTION, FIBER DIFFRACTION,   POWDER DIFFRACTION, ELECTRON CRYSTALLOGRAPHY, and NEUTRON DIFFRACTION as identified in  'refine.pdbx_refine_id'.   Resolution reported in 'em_3d_reconstruction.resolution' is used for ELECTRON MICROSCOPY.   The best value corresponding to 'em_3d_reconstruction.resolution_method' == 'FSC 0.143 CUT-OFF'   is used, if available. If not, the best 'em_3d_reconstruction.resolution' value is used.   For structures that are not obtained from diffraction-based methods, the resolution values in   'refine.ls_d_res_high' are ignored.  Multiple values are reported only if multiple methods are used in the structure determination."""
		self._enter('resolution_combined', Query)
		return self
	@property
	def selected_polymer_entity_types(self) -> 'RcsbEntryInfo':
		"""Selected polymer entity type categories describing the entry.  Allowable values: Nucleic acid (only), Oligosaccharide (only), Other, Protein (only), Protein/NA, Protein/Oligosaccharide """
		self._enter('selected_polymer_entity_types', Query)
		return self
	@property
	def software_programs_combined(self) -> 'RcsbEntryInfo':
		"""Combined list of software programs names reported in connection with the production of this entry."""
		self._enter('software_programs_combined', Query)
		return self
	@property
	def solvent_entity_count(self) -> 'RcsbEntryInfo':
		"""The number of distinct solvent entities per deposited structure model."""
		self._enter('solvent_entity_count', Query)
		return self
	@property
	def structure_determination_methodology(self) -> 'RcsbEntryInfo':
		"""Indicates if the structure was determined using experimental or computational methods.  Allowable values: computational, experimental, integrative """
		self._enter('structure_determination_methodology', Query)
		return self
	@property
	def structure_determination_methodology_priority(self) -> 'RcsbEntryInfo':
		"""Indicates the priority of the value in _rcsb_entry_info.structure_determination_methodology.  The lower the number the higher the priority.  Priority values for 'experimental' structures is currently set to 10 and  the values for 'computational' structures is set to 100."""
		self._enter('structure_determination_methodology_priority', Query)
		return self

class RcsbEntryInfoDiffrnResolutionHigh(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbEntryInfo':
		"""Return to parent (RcsbEntryInfo)"""
		return self._parent if self._parent else self
	@property
	def provenance_source(self) -> 'RcsbEntryInfoDiffrnResolutionHigh':
		"""The provenence source for the high resolution limit of data collection.  Allowable values: Depositor assigned, From refinement resolution cutoff, From the high resolution shell """
		self._enter('provenance_source', Query)
		return self
	@property
	def value(self) -> 'RcsbEntryInfoDiffrnResolutionHigh':
		"""The high resolution limit of data collection."""
		self._enter('value', Query)
		return self

class RcsbExternalReferences(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def id(self) -> 'RcsbExternalReferences':
		"""ID (accession) from external resource linked to this entry.  Examples: 1BMR """
		self._enter('id', Query)
		return self
	@property
	def link(self) -> 'RcsbExternalReferences':
		"""Link to this entry in external resource"""
		self._enter('link', Query)
		return self
	@property
	def type(self) -> 'RcsbExternalReferences':
		"""Internal identifier for external resources  Allowable values: BMRB, EM DATA RESOURCE, NAKB, NDB, OLDERADO, PROTEIN DIFFRACTION, SB GRID """
		self._enter('type', Query)
		return self

class RcsbGenomicLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbGenomicLineage':
		"""Classification hierarchy depth."""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbGenomicLineage':
		"""Automatically assigned ID that uniquely identifies taxonomy, chromosome or gene in the Genome Location Browser.  Examples: 9606, 568815441, 414325 """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbGenomicLineage':
		"""A human-readable term name.  Examples: Homo sapiens, 8, defensin beta 103A """
		self._enter('name', Query)
		return self

class RcsbGroupAccessionInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupEntry':
		"""Return to parent (GroupEntry)"""
		return self._parent if self._parent else self
	@property
	def version(self) -> 'RcsbGroupAccessionInfo':
		"""Identifies the version of the groups solution"""
		self._enter('version', Query)
		return self

class RcsbGroupAggregationMethod(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupProvenance':
		"""Return to parent (GroupProvenance)"""
		return self._parent if self._parent else self
	@property
	def method(self) -> 'RcsbGroupAggregationMethodMethod':
		"""The details on a method used to calculate cluster solutions"""
		return self._enter('method', RcsbGroupAggregationMethodMethod)
	@property
	def similarity_criteria(self) -> 'RcsbGroupAggregationMethodSimilarityCriteria':
		""""""
		return self._enter('similarity_criteria', RcsbGroupAggregationMethodSimilarityCriteria)
	@property
	def type(self) -> 'RcsbGroupAggregationMethod':
		"""Specifies the type of similarity criteria used to aggregate members into higher levels in the hierarchy  Allowable values: sequence_identity, matching_uniprot_accession, matching_deposit_group_id, matching_chemical_component_id """
		self._enter('type', Query)
		return self

class RcsbGroupAggregationMethodMethod(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbGroupAggregationMethod':
		"""Return to parent (RcsbGroupAggregationMethod)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'MethodDetails':
		"""Additional details describing the clustering process"""
		return self._enter('details', MethodDetails)
	@property
	def name(self) -> 'RcsbGroupAggregationMethodMethod':
		"""The name of the software or the method used to calculate cluster solutions  Allowable values: mmseqs2, matching_reference_identity """
		self._enter('name', Query)
		return self
	@property
	def version(self) -> 'RcsbGroupAggregationMethodMethod':
		"""The version of the software.  Examples: v1.0, 3.1-2, unknown """
		self._enter('version', Query)
		return self

class RcsbGroupAggregationMethodSimilarityCriteria(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbGroupAggregationMethod':
		"""Return to parent (RcsbGroupAggregationMethod)"""
		return self._parent if self._parent else self
	@property
	def similarity_function(self) -> 'RcsbGroupAggregationMethodSimilarityCriteria':
		"""A function or similarity measure that quantifies the similarity between two members  Allowable values: rmsd, sequence_identity """
		self._enter('similarity_function', Query)
		return self

class RcsbGroupContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupEntry':
		"""Return to parent (GroupEntry)"""
		return self._parent if self._parent else self
	@property
	def group_id(self) -> 'RcsbGroupContainerIdentifiers':
		"""A unique textual identifier for a group"""
		self._enter('group_id', Query)
		return self
	@property
	def group_member_ids(self) -> 'RcsbGroupContainerIdentifiers':
		"""Member identifiers representing a group"""
		self._enter('group_member_ids', Query)
		return self
	@property
	def group_provenance_id(self) -> 'RcsbGroupContainerIdentifiers':
		"""A unique group provenance identifier  Allowable values: provenance_sequence_identity, provenance_matching_uniprot_accession, provenance_matching_deposit_group_id, provenance_matching_chemical_component_id """
		self._enter('group_provenance_id', Query)
		return self
	@property
	def parent_member_ids(self) -> 'RcsbGroupContainerIdentifiers':
		"""Member identifiers representing a higher level in the groping hierarchy that has parent-child relationship"""
		self._enter('parent_member_ids', Query)
		return self

class RcsbGroupInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupEntry':
		"""Return to parent (GroupEntry)"""
		return self._parent if self._parent else self
	@property
	def group_description(self) -> 'RcsbGroupInfo':
		""""""
		self._enter('group_description', Query)
		return self
	@property
	def group_members_count(self) -> 'RcsbGroupInfo':
		""""""
		self._enter('group_members_count', Query)
		return self
	@property
	def group_members_granularity(self) -> 'RcsbGroupInfo':
		"""Granularity of group members identifiers  Allowable values: assembly, entry, polymer_entity, non_polymer_entity, polymer_entity_instance """
		self._enter('group_members_granularity', Query)
		return self
	@property
	def group_name(self) -> 'RcsbGroupInfo':
		""""""
		self._enter('group_name', Query)
		return self

class RcsbGroupProvenanceContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupProvenance':
		"""Return to parent (GroupProvenance)"""
		return self._parent if self._parent else self
	@property
	def group_provenance_id(self) -> 'RcsbGroupProvenanceContainerIdentifiers':
		"""A unique group provenance identifier  Allowable values: provenance_sequence_identity, provenance_matching_uniprot_accession, provenance_matching_deposit_group_id, provenance_matching_chemical_component_id """
		self._enter('group_provenance_id', Query)
		return self

class RcsbGroupRelated(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupEntry':
		"""Return to parent (GroupEntry)"""
		return self._parent if self._parent else self
	@property
	def resource_accession_code(self) -> 'RcsbGroupRelated':
		"""A unique code assigned to a reference related the group  Examples: P69905 """
		self._enter('resource_accession_code', Query)
		return self
	@property
	def resource_name(self) -> 'RcsbGroupRelated':
		"""Defines the type of the resource describing related references  Examples: UniProt """
		self._enter('resource_name', Query)
		return self

class RcsbGroupStatistics(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupEntry':
		"""Return to parent (GroupEntry)"""
		return self._parent if self._parent else self
	@property
	def similarity_cutoff(self) -> 'RcsbGroupStatistics':
		"""The desired lower limit for the similarity between two members that belong to the same group"""
		self._enter('similarity_cutoff', Query)
		return self
	@property
	def similarity_score_max(self) -> 'RcsbGroupStatistics':
		"""Similarity score between two most similar group members"""
		self._enter('similarity_score_max', Query)
		return self
	@property
	def similarity_score_min(self) -> 'RcsbGroupStatistics':
		"""Similarity score between two least similar group members"""
		self._enter('similarity_score_min', Query)
		return self

class RcsbIhmDatasetList(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def count(self) -> 'RcsbIhmDatasetList':
		"""Number of input datasets used in integrative modeling."""
		self._enter('count', Query)
		return self
	@property
	def name(self) -> 'RcsbIhmDatasetList':
		"""Name of input dataset used in integrative modeling.  Allowable values: 2DEM class average, 3DEM volume, CX-MS data, Comparative model, Crosslinking-MS data, DNA footprinting data, De Novo model, EM raw micrographs, EPR data, Ensemble FRET data, Experimental model, H/D exchange data, Hydroxyl radical footprinting data, Integrative model, Mass Spectrometry data, Mutagenesis data, NMR data, Other, Predicted contacts, Quantitative measurements of genetic interactions, SAS data, Single molecule FRET data, X-ray diffraction data, Yeast two-hybrid screening data """
		self._enter('name', Query)
		return self
	@property
	def type(self) -> 'RcsbIhmDatasetList':
		"""Type of input dataset used in integrative modeling.  Allowable values: Computed restraints, Experimental data, Other, Starting model """
		self._enter('type', Query)
		return self

class RcsbIhmDatasetSourceDbReference(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def accession_code(self) -> 'RcsbIhmDatasetSourceDbReference':
		"""Accession code for the input dataset.  Examples: 5FM1, EMD-2799, SASDA82, PXD003381, MA-CO2KC """
		self._enter('accession_code', Query)
		return self
	@property
	def db_name(self) -> 'RcsbIhmDatasetSourceDbReference':
		"""Name of the source database for the input dataset.  Allowable values: AlphaFoldDB, BMRB, BMRbig, BioGRID, EMDB, EMPIAR, MASSIVE, ModelArchive, Other, PDB, PDB-Dev, PRIDE, ProXL, ProteomeXchange, SASBDB, iProX, jPOSTrepo """
		self._enter('db_name', Query)
		return self

class RcsbInterfaceContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreInterface':
		"""Return to parent (CoreInterface)"""
		return self._parent if self._parent else self
	@property
	def assembly_id(self) -> 'RcsbInterfaceContainerIdentifiers':
		"""This item references an assembly in pdbx_struct_assembly"""
		self._enter('assembly_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbInterfaceContainerIdentifiers':
		"""Entry identifier for the container."""
		self._enter('entry_id', Query)
		return self
	@property
	def interface_entity_id(self) -> 'RcsbInterfaceContainerIdentifiers':
		"""Identifier for NCS-equivalent interfaces within the assembly (same entity_ids on both sides)  Examples: 1, 2 """
		self._enter('interface_entity_id', Query)
		return self
	@property
	def interface_id(self) -> 'RcsbInterfaceContainerIdentifiers':
		"""Identifier for the geometrically equivalent (same asym_ids on either side) interfaces within the assembly  Examples: 1, 2 """
		self._enter('interface_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbInterfaceContainerIdentifiers':
		"""Unique identifier for the document  Examples: 2UZI-1.A.B?1 """
		self._enter('rcsb_id', Query)
		return self

class RcsbInterfaceInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreInterface':
		"""Return to parent (CoreInterface)"""
		return self._parent if self._parent else self
	@property
	def interface_area(self) -> 'RcsbInterfaceInfo':
		"""Total interface buried surface area"""
		self._enter('interface_area', Query)
		return self
	@property
	def interface_character(self) -> 'RcsbInterfaceInfo':
		"""Allowable values: homo, hetero."""
		self._enter('interface_character', Query)
		return self
	@property
	def num_core_interface_residues(self) -> 'RcsbInterfaceInfo':
		"""Number of core interface residues, defined as those that bury >90% accessible surface area with respect to the unbound state"""
		self._enter('num_core_interface_residues', Query)
		return self
	@property
	def num_interface_residues(self) -> 'RcsbInterfaceInfo':
		"""Number of interface residues, defined as those with burial fraction > 0"""
		self._enter('num_interface_residues', Query)
		return self
	@property
	def polymer_composition(self) -> 'RcsbInterfaceInfo':
		"""Allowable values: Nucleic acid (only), Protein (only), Protein/NA."""
		self._enter('polymer_composition', Query)
		return self
	@property
	def self_jaccard_contact_score(self) -> 'RcsbInterfaceInfo':
		"""The Jaccard score (intersection over union) of interface contacts in homomeric interfaces, comparing contact sets left-right vs right-left. High values indicate isologous (symmetric) interfaces, with value=1 if perfectly symmetric (e.g. crystallographic symmetry)"""
		self._enter('self_jaccard_contact_score', Query)
		return self

class RcsbInterfacePartner(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreInterface':
		"""Return to parent (CoreInterface)"""
		return self._parent if self._parent else self
	@property
	def interface_partner_feature(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		""""""
		return self._enter('interface_partner_feature', RcsbInterfacePartnerInterfacePartnerFeature)
	@property
	def interface_partner_identifier(self) -> 'RcsbInterfacePartnerInterfacePartnerIdentifier':
		""""""
		return self._enter('interface_partner_identifier', RcsbInterfacePartnerInterfacePartnerIdentifier)

class RcsbInterfacePartnerInterfacePartnerFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbInterfacePartner':
		"""Return to parent (RcsbInterfacePartner)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'InterfacePartnerFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', InterfacePartnerFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'InterfacePartnerFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', InterfacePartnerFeatureFeaturePositions)
	@property
	def name(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""Code identifying the individual, organization or program that assigned the feature.  Examples: NACCESS """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbInterfacePartnerInterfacePartnerFeature':
		"""A type or category of the feature.  Allowable values: ASA_UNBOUND, ASA_BOUND """
		self._enter('type', Query)
		return self

class RcsbInterfacePartnerInterfacePartnerIdentifier(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbInterfacePartner':
		"""Return to parent (RcsbInterfacePartner)"""
		return self._parent if self._parent else self
	@property
	def asym_id(self) -> 'RcsbInterfacePartnerInterfacePartnerIdentifier':
		"""Instance identifier for this container."""
		self._enter('asym_id', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbInterfacePartnerInterfacePartnerIdentifier':
		"""Polymer entity identifier for the container."""
		self._enter('entity_id', Query)
		return self

class RcsbLatestRevision(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def major_revision(self) -> 'RcsbLatestRevision':
		"""The major version number of the latest revision."""
		self._enter('major_revision', Query)
		return self
	@property
	def minor_revision(self) -> 'RcsbLatestRevision':
		"""The minor version number of the latest revision."""
		self._enter('minor_revision', Query)
		return self
	@property
	def revision_date(self) -> 'RcsbLatestRevision':
		"""The release date of the latest revision item.  Examples: 2020-02-11, 2018-10-23 """
		self._enter('revision_date', Query)
		return self

class RcsbLigandNeighbors(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def alt_id(self) -> 'RcsbLigandNeighbors':
		"""Alternate conformer identifier for the target instance."""
		self._enter('alt_id', Query)
		return self
	@property
	def atom_id(self) -> 'RcsbLigandNeighbors':
		"""The atom identifier for the target instance.  Examples: O1, N1, C1 """
		self._enter('atom_id', Query)
		return self
	@property
	def auth_seq_id(self) -> 'RcsbLigandNeighbors':
		"""The author residue index for the target instance."""
		self._enter('auth_seq_id', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbLigandNeighbors':
		"""Component identifier for the target instance."""
		self._enter('comp_id', Query)
		return self
	@property
	def distance(self) -> 'RcsbLigandNeighbors':
		"""Distance value for this ligand interaction."""
		self._enter('distance', Query)
		return self
	@property
	def ligand_alt_id(self) -> 'RcsbLigandNeighbors':
		"""Alternate conformer identifier for the ligand interaction."""
		self._enter('ligand_alt_id', Query)
		return self
	@property
	def ligand_asym_id(self) -> 'RcsbLigandNeighbors':
		"""The entity instance identifier for the ligand interaction.  Examples: A, B """
		self._enter('ligand_asym_id', Query)
		return self
	@property
	def ligand_atom_id(self) -> 'RcsbLigandNeighbors':
		"""The atom identifier for the ligand interaction.  Examples: OG, OE1, CD1 """
		self._enter('ligand_atom_id', Query)
		return self
	@property
	def ligand_comp_id(self) -> 'RcsbLigandNeighbors':
		"""The chemical component identifier for the ligand interaction.  Examples: ASN, TRP, SER """
		self._enter('ligand_comp_id', Query)
		return self
	@property
	def ligand_entity_id(self) -> 'RcsbLigandNeighbors':
		"""The entity identifier for the ligand of interaction.  Examples: 1, 2 """
		self._enter('ligand_entity_id', Query)
		return self
	@property
	def ligand_is_bound(self) -> 'RcsbLigandNeighbors':
		"""A flag to indicate the nature of the ligand interaction is covalent or metal-coordination.  Allowable values: N, Y """
		self._enter('ligand_is_bound', Query)
		return self
	@property
	def ligand_model_id(self) -> 'RcsbLigandNeighbors':
		"""Model identifier for the ligand interaction."""
		self._enter('ligand_model_id', Query)
		return self
	@property
	def seq_id(self) -> 'RcsbLigandNeighbors':
		"""The sequence position for the target instance."""
		self._enter('seq_id', Query)
		return self

class RcsbMaQaMetricGlobal(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def ma_qa_metric_global(self) -> 'RcsbMaQaMetricGlobalMaQaMetricGlobal':
		""""""
		return self._enter('ma_qa_metric_global', RcsbMaQaMetricGlobalMaQaMetricGlobal)
	@property
	def model_id(self) -> 'RcsbMaQaMetricGlobal':
		"""The model identifier."""
		self._enter('model_id', Query)
		return self

class RcsbMaQaMetricGlobalMaQaMetricGlobal(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbMaQaMetricGlobal':
		"""Return to parent (RcsbMaQaMetricGlobal)"""
		return self._parent if self._parent else self
	@property
	def description(self) -> 'RcsbMaQaMetricGlobalMaQaMetricGlobal':
		"""Description of the global QA metric.  Examples: confidence score predicting accuracy according to the CA-only Local Distance Difference Test (lDDT-CA) in [0,100] """
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbMaQaMetricGlobalMaQaMetricGlobal':
		"""Name of the global QA metric.  Examples: pLDDT """
		self._enter('name', Query)
		return self
	@property
	def type(self) -> 'RcsbMaQaMetricGlobalMaQaMetricGlobal':
		"""The type of global QA metric.  Allowable values: PAE, contact probability, distance, energy, ipTM, normalized score, other, pLDDT, pLDDT all-atom, pLDDT all-atom in [0,1], pLDDT in [0,1], pTM, zscore """
		self._enter('type', Query)
		return self
	@property
	def type_other_details(self) -> 'RcsbMaQaMetricGlobalMaQaMetricGlobal':
		"""Details for other type of global QA metric."""
		self._enter('type_other_details', Query)
		return self
	@property
	def value(self) -> 'RcsbMaQaMetricGlobalMaQaMetricGlobal':
		"""Value of the global QA metric.  Examples: null """
		self._enter('value', Query)
		return self

class RcsbMembraneLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbMembraneLineage':
		"""Hierarchy depth."""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbMembraneLineage':
		"""Automatically assigned ID for membrane classification term in the Membrane Protein Browser.  Examples: MONOTOPIC MEMBRANE PROTEINS.Oxidases.Monoamine Oxidase A """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbMembraneLineage':
		"""Membrane protein classification term."""
		self._enter('name', Query)
		return self

class RcsbNonpolymerEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'RcsbNonpolymerEntity':
		"""A description of special aspects of the entity."""
		self._enter('details', Query)
		return self
	@property
	def formula_weight(self) -> 'RcsbNonpolymerEntity':
		"""Formula mass (KDa) of the entity."""
		self._enter('formula_weight', Query)
		return self
	@property
	def pdbx_description(self) -> 'RcsbNonpolymerEntity':
		"""A description of the nonpolymer entity."""
		self._enter('pdbx_description', Query)
		return self
	@property
	def pdbx_number_of_molecules(self) -> 'RcsbNonpolymerEntity':
		"""The number of molecules of the nonpolymer entity in the entry."""
		self._enter('pdbx_number_of_molecules', Query)
		return self

class RcsbNonpolymerEntityAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def annotation_id(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbNonpolymerEntityAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbNonpolymerEntityAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""Non-polymer(ligand) chemical component identifier for the entity.  Examples: GTP, STN """
		self._enter('comp_id', Query)
		return self
	@property
	def description(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""A type or category of the annotation.  Allowable values: SUBJECT_OF_INVESTIGATION """
		self._enter('type', Query)
		return self

class RcsbNonpolymerEntityAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerEntityAnnotation':
		"""Return to parent (RcsbNonpolymerEntityAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbNonpolymerEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbNonpolymerEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbNonpolymerEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbNonpolymerEntityContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def asym_ids(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Instance identifiers corresponding to copies of the entity in this container."""
		self._enter('asym_ids', Query)
		return self
	@property
	def auth_asym_ids(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Author instance identifiers corresponding to copies of the entity in this container."""
		self._enter('auth_asym_ids', Query)
		return self
	@property
	def chem_ref_def_id(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""The chemical reference definition identifier for the entity in this container.  Examples: PRD_000010 """
		self._enter('chem_ref_def_id', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Entity identifier for the container.  Examples: 1, 2 """
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Entry identifier for the container.  Examples: 4HHB, 1KIP """
		self._enter('entry_id', Query)
		return self
	@property
	def nonpolymer_comp_id(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Non-polymer(ligand) chemical component identifier for the entity in this container.  Examples: GTP, STN """
		self._enter('nonpolymer_comp_id', Query)
		return self
	@property
	def prd_id(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""The BIRD identifier for the entity in this container.  Examples: PRD_000010 """
		self._enter('prd_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers.  Examples: 6EL3_1 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def reference_chemical_identifiers_provenance_source(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Source of the reference database assignment  Allowable values: PDB, RCSB """
		self._enter('reference_chemical_identifiers_provenance_source', Query)
		return self
	@property
	def reference_chemical_identifiers_resource_accession(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Reference resource accession code"""
		self._enter('reference_chemical_identifiers_resource_accession', Query)
		return self
	@property
	def reference_chemical_identifiers_resource_name(self) -> 'RcsbNonpolymerEntityContainerIdentifiers':
		"""Reference resource name  Allowable values: ChEBI, ChEMBL, DrugBank, PubChem """
		self._enter('reference_chemical_identifiers_resource_name', Query)
		return self

class RcsbNonpolymerEntityFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbNonpolymerEntityFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbNonpolymerEntityFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbNonpolymerEntityFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbNonpolymerEntityFeature':
		"""Non-polymer(ligand) chemical component identifier for the entity.  Examples: GTP, STN """
		self._enter('comp_id', Query)
		return self
	@property
	def description(self) -> 'RcsbNonpolymerEntityFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbNonpolymerEntityFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def name(self) -> 'RcsbNonpolymerEntityFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbNonpolymerEntityFeature':
		"""Code identifying the individual, organization or program that  assigned the feature.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerEntityFeature':
		"""A type or category of the feature.  Allowable values: SUBJECT_OF_INVESTIGATION """
		self._enter('type', Query)
		return self
	@property
	def value(self) -> 'RcsbNonpolymerEntityFeature':
		"""The feature value."""
		self._enter('value', Query)
		return self

class RcsbNonpolymerEntityFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerEntityFeature':
		"""Return to parent (RcsbNonpolymerEntityFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbNonpolymerEntityFeatureAdditionalProperties':
		"""The additional property name."""
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbNonpolymerEntityFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbNonpolymerEntityFeatureSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""Non-polymer(ligand) chemical component identifier for the entity.  Examples: GTP, STN """
		self._enter('comp_id', Query)
		return self
	@property
	def count(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""The feature count."""
		self._enter('count', Query)
		return self
	@property
	def maximum_length(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""The maximum feature length."""
		self._enter('maximum_length', Query)
		return self
	@property
	def maximum_value(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""The maximum feature value.  Examples: null, null """
		self._enter('maximum_value', Query)
		return self
	@property
	def minimum_length(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""The minimum feature length."""
		self._enter('minimum_length', Query)
		return self
	@property
	def minimum_value(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""The minimum feature value.  Examples: null, null """
		self._enter('minimum_value', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerEntityFeatureSummary':
		"""Type or category of the feature.  Allowable values: SUBJECT_OF_INVESTIGATION """
		self._enter('type', Query)
		return self

class RcsbNonpolymerEntityInstanceContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def asym_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""Instance identifier for this container."""
		self._enter('asym_id', Query)
		return self
	@property
	def auth_asym_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""Author instance identifier for this container."""
		self._enter('auth_asym_id', Query)
		return self
	@property
	def auth_seq_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""Residue number for non-polymer entity instance."""
		self._enter('auth_seq_id', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""Component identifier for non-polymer entity instance."""
		self._enter('comp_id', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""Entity identifier for the container."""
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""Entry identifier for the container."""
		self._enter('entry_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbNonpolymerEntityInstanceContainerIdentifiers':
		"""A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers.  Examples: 1KIP.A """
		self._enter('rcsb_id', Query)
		return self

class RcsbNonpolymerEntityKeywords(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def text(self) -> 'RcsbNonpolymerEntityKeywords':
		"""Keywords describing this non-polymer entity."""
		self._enter('text', Query)
		return self

class RcsbNonpolymerEntityNameCom(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntity':
		"""Return to parent (CoreNonpolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbNonpolymerEntityNameCom':
		"""A common name for the nonpolymer entity."""
		self._enter('name', Query)
		return self

class RcsbNonpolymerInstanceAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def annotation_id(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbNonpolymerInstanceAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbNonpolymerInstanceAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""Non-polymer (ligand) chemical component identifier.  Examples: ATP """
		self._enter('comp_id', Query)
		return self
	@property
	def description(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""Ordinal identifier for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""A type or category of the annotation.  Allowable values: HAS_COVALENT_LINKAGE, HAS_METAL_COORDINATION_LINKAGE, HAS_NO_COVALENT_LINKAGE, IS_RSCC_OUTLIER, IS_RSRZ_OUTLIER """
		self._enter('type', Query)
		return self

class RcsbNonpolymerInstanceAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerInstanceAnnotation':
		"""Return to parent (RcsbNonpolymerInstanceAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbNonpolymerInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbNonpolymerInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbNonpolymerInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbNonpolymerInstanceFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbNonpolymerInstanceFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbNonpolymerInstanceFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbNonpolymerInstanceFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbNonpolymerInstanceFeature':
		"""Component identifier for non-polymer entity instance."""
		self._enter('comp_id', Query)
		return self
	@property
	def description(self) -> 'RcsbNonpolymerInstanceFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbNonpolymerInstanceFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_value(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		""""""
		return self._enter('feature_value', RcsbNonpolymerInstanceFeatureFeatureValue)
	@property
	def name(self) -> 'RcsbNonpolymerInstanceFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbNonpolymerInstanceFeature':
		"""Ordinal identifier for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbNonpolymerInstanceFeature':
		"""Code identifying the individual, organization or program that  assigned the feature.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerInstanceFeature':
		"""A type or category of the feature.  Allowable values: HAS_COVALENT_LINKAGE, HAS_METAL_COORDINATION_LINKAGE, MODELED_ATOMS, MOGUL_ANGLE_OUTLIER, MOGUL_ANGLE_OUTLIERS, MOGUL_BOND_OUTLIER, MOGUL_BOND_OUTLIERS, MOGUL_RING_OUTLIERS, MOGUL_TORSION_OUTLIERS, RSCC_OUTLIER, RSRZ_OUTLIER, STEREO_OUTLIER, STEREO_OUTLIERS """
		self._enter('type', Query)
		return self

class RcsbNonpolymerInstanceFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerInstanceFeature':
		"""Return to parent (RcsbNonpolymerInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbNonpolymerInstanceFeatureAdditionalProperties':
		"""The additional property name.  Examples: bond_distance, bond_angle """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbNonpolymerInstanceFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbNonpolymerInstanceFeatureFeatureValue(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerInstanceFeature':
		"""Return to parent (RcsbNonpolymerInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		"""The chemical component identifier for the instance of the feature value.  Examples: ATP,, STN """
		self._enter('comp_id', Query)
		return self
	@property
	def details(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		"""Specific details about the feature.  Examples: C1,C2, C1,C2,C3 """
		self._enter('details', Query)
		return self
	@property
	def reference(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		"""The reference value of the feature.  Examples: null, null """
		self._enter('reference', Query)
		return self
	@property
	def reported(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		"""The reported value of the feature.  Examples: null, null """
		self._enter('reported', Query)
		return self
	@property
	def uncertainty_estimate(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		"""The estimated uncertainty of the reported feature value.  Examples: null, null """
		self._enter('uncertainty_estimate', Query)
		return self
	@property
	def uncertainty_estimate_type(self) -> 'RcsbNonpolymerInstanceFeatureFeatureValue':
		"""The type of estimated uncertainty for the reported feature value.  Allowable values: Z-Score """
		self._enter('uncertainty_estimate_type', Query)
		return self

class RcsbNonpolymerInstanceFeatureSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def comp_id(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""Component identifier for non-polymer entity instance."""
		self._enter('comp_id', Query)
		return self
	@property
	def count(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""The feature count."""
		self._enter('count', Query)
		return self
	@property
	def coverage(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""The fractional feature coverage relative to the full entity sequence.  Examples: null, null """
		self._enter('coverage', Query)
		return self
	@property
	def maximum_length(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""The maximum feature length."""
		self._enter('maximum_length', Query)
		return self
	@property
	def maximum_value(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""The maximum feature value.  Examples: null, null """
		self._enter('maximum_value', Query)
		return self
	@property
	def minimum_length(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""The minimum feature length."""
		self._enter('minimum_length', Query)
		return self
	@property
	def minimum_value(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""The minimum feature value.  Examples: null, null """
		self._enter('minimum_value', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerInstanceFeatureSummary':
		"""Type or category of the feature.  Allowable values: HAS_COVALENT_LINKAGE, HAS_METAL_COORDINATION_LINKAGE, MODELED_ATOMS, MOGUL_ANGLE_OUTLIER, MOGUL_ANGLE_OUTLIERS, MOGUL_BOND_OUTLIER, MOGUL_BOND_OUTLIERS, MOGUL_RING_OUTLIERS, MOGUL_TORSION_OUTLIERS, RSCC_OUTLIER, RSRZ_OUTLIER, STEREO_OUTLIER, STEREO_OUTLIERS """
		self._enter('type', Query)
		return self

class RcsbNonpolymerInstanceValidationScore(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def RSCC(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The real space correlation coefficient (RSCC) for the non-polymer entity instance.  Examples: null, null """
		self._enter('RSCC', Query)
		return self
	@property
	def RSR(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The real space R-value (RSR) for the non-polymer entity instance.  Examples: null, null """
		self._enter('RSR', Query)
		return self
	@property
	def alt_id(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""Alternate conformer identifier for the non-polymer entity instance."""
		self._enter('alt_id', Query)
		return self
	@property
	def average_occupancy(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The average heavy atom occupancy for coordinate records for the non-polymer entity instance.  Examples: null, null """
		self._enter('average_occupancy', Query)
		return self
	@property
	def completeness(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The reported fraction of atomic coordinate records for the non-polymer entity instance.  Examples: null, null """
		self._enter('completeness', Query)
		return self
	@property
	def intermolecular_clashes(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The number of intermolecular MolProbity clashes cacluated for reported atomic coordinate records."""
		self._enter('intermolecular_clashes', Query)
		return self
	@property
	def is_best_instance(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""This molecular instance is ranked as the best quality instance of this nonpolymer entity.  Allowable values: N, Y """
		self._enter('is_best_instance', Query)
		return self
	@property
	def is_subject_of_investigation(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""This molecular entity is identified as the subject of the current study.  Allowable values: N, Y """
		self._enter('is_subject_of_investigation', Query)
		return self
	@property
	def is_subject_of_investigation_provenance(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The provenance for the selection of the molecular entity identified as the subject of the current study.  Allowable values: Author, RCSB """
		self._enter('is_subject_of_investigation_provenance', Query)
		return self
	@property
	def mogul_angle_outliers(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""Number of bond angle outliers obtained from a CCDC Mogul survey of bond angles  in the CSD small    molecule crystal structure database. Outliers are defined as bond angles that have a Z-score    less than -2 or greater than 2."""
		self._enter('mogul_angle_outliers', Query)
		return self
	@property
	def mogul_angles_RMSZ(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The root-mean-square value of the Z-scores of bond angles for the non-polymer instance in degrees obtained from a CCDC Mogul survey of bond angles in the CSD small molecule crystal structure database.  Examples: null, null """
		self._enter('mogul_angles_RMSZ', Query)
		return self
	@property
	def mogul_bond_outliers(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""Number of bond distance outliers obtained from a CCDC Mogul survey of bond lengths in the CSD small    molecule crystal structure database.  Outliers are defined as bond distances that have a Z-score    less than -2 or greater than 2."""
		self._enter('mogul_bond_outliers', Query)
		return self
	@property
	def mogul_bonds_RMSZ(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The root-mean-square value of the Z-scores of bond lengths for the nonpolymer instance in Angstroms obtained from a CCDC Mogul survey of bond lengths in the CSD small molecule crystal structure database.  Examples: null, null """
		self._enter('mogul_bonds_RMSZ', Query)
		return self
	@property
	def natoms_eds(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The number of atoms in the non-polymer instance returned by the EDS software."""
		self._enter('natoms_eds', Query)
		return self
	@property
	def num_mogul_angles_RMSZ(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The number of bond angles compared to 'standard geometry' made using the Mogul program."""
		self._enter('num_mogul_angles_RMSZ', Query)
		return self
	@property
	def num_mogul_bonds_RMSZ(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The number of bond lengths compared to 'standard geometry' made using the Mogul program."""
		self._enter('num_mogul_bonds_RMSZ', Query)
		return self
	@property
	def ranking_model_fit(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The ranking of the model fit score component.  Examples: null, null """
		self._enter('ranking_model_fit', Query)
		return self
	@property
	def ranking_model_geometry(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The ranking of the model geometry score component.  Examples: null, null """
		self._enter('ranking_model_geometry', Query)
		return self
	@property
	def score_model_fit(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The value of the model fit score component.  Examples: null, null """
		self._enter('score_model_fit', Query)
		return self
	@property
	def score_model_geometry(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""The value of the model geometry score component.  Examples: null, null """
		self._enter('score_model_geometry', Query)
		return self
	@property
	def stereo_outliers(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""Number of stereochemical/chirality errors."""
		self._enter('stereo_outliers', Query)
		return self
	@property
	def type(self) -> 'RcsbNonpolymerInstanceValidationScore':
		"""Score type.  Allowable values: RCSB_LIGAND_QUALITY_SCORE_2021 """
		self._enter('type', Query)
		return self

class RcsbNonpolymerStructConn(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def connect_partner(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		""""""
		return self._enter('connect_partner', RcsbNonpolymerStructConnConnectPartner)
	@property
	def connect_target(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		""""""
		return self._enter('connect_target', RcsbNonpolymerStructConnConnectTarget)
	@property
	def connect_type(self) -> 'RcsbNonpolymerStructConn':
		"""The connection type.  Allowable values: covalent bond, disulfide bridge, hydrogen bond, ionic interaction, metal coordination, mismatched base pairs """
		self._enter('connect_type', Query)
		return self
	@property
	def description(self) -> 'RcsbNonpolymerStructConn':
		"""A description of special details of the connection.  Examples: Watson-Crick base pair """
		self._enter('description', Query)
		return self
	@property
	def dist_value(self) -> 'RcsbNonpolymerStructConn':
		"""Distance value for this contact."""
		self._enter('dist_value', Query)
		return self
	@property
	def id(self) -> 'RcsbNonpolymerStructConn':
		"""The value of _rcsb_nonpolymer_struct_conn.id is an identifier for connection.   Note that this item need not be a number; it can be any unique  identifier."""
		self._enter('id', Query)
		return self
	@property
	def ordinal_id(self) -> 'RcsbNonpolymerStructConn':
		"""The value of _rcsb_nonpolymer_struct_conn.id must uniquely identify a record in  the rcsb_nonpolymer_struct_conn list."""
		self._enter('ordinal_id', Query)
		return self
	@property
	def role(self) -> 'RcsbNonpolymerStructConn':
		"""The chemical or structural role of the interaction  Allowable values: C-Mannosylation, N-Glycosylation, O-Glycosylation, S-Glycosylation """
		self._enter('role', Query)
		return self
	@property
	def value_order(self) -> 'RcsbNonpolymerStructConn':
		"""The chemical bond order associated with the specified atoms in  this contact.  Allowable values: doub, quad, sing, trip """
		self._enter('value_order', Query)
		return self

class RcsbNonpolymerStructConnConnectPartner(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerStructConn':
		"""Return to parent (RcsbNonpolymerStructConn)"""
		return self._parent if self._parent else self
	@property
	def label_alt_id(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
		self._enter('label_alt_id', Query)
		return self
	@property
	def label_asym_id(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_atom_id(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _chem_comp_atom.atom_id in the  CHEM_COMP_ATOM category."""
		self._enter('label_atom_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self
	@property
	def label_seq_id(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_seq_id in the  ATOM_SITE category."""
		self._enter('label_seq_id', Query)
		return self
	@property
	def symmetry(self) -> 'RcsbNonpolymerStructConnConnectPartner':
		"""Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_nonpolymer_struct_conn.connect_partner_label* to generate the  partner in the structure connection.  Examples: 1_555, 7_645 """
		self._enter('symmetry', Query)
		return self

class RcsbNonpolymerStructConnConnectTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbNonpolymerStructConn':
		"""Return to parent (RcsbNonpolymerStructConn)"""
		return self._parent if self._parent else self
	@property
	def auth_asym_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_asym_id in the  ATOM_SITE category."""
		self._enter('auth_asym_id', Query)
		return self
	@property
	def auth_seq_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
		self._enter('auth_seq_id', Query)
		return self
	@property
	def label_alt_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
		self._enter('label_alt_id', Query)
		return self
	@property
	def label_asym_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_atom_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_atom_id in the  ATOM_SITE category."""
		self._enter('label_atom_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self
	@property
	def label_seq_id(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.connect_target_label_seq_id in the  ATOM_SITE category."""
		self._enter('label_seq_id', Query)
		return self
	@property
	def symmetry(self) -> 'RcsbNonpolymerStructConnConnectTarget':
		"""Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_nonpolymer_struct_conn.label* to generate the  target of the structure connection.  Examples: 1_555, 7_645 """
		self._enter('symmetry', Query)
		return self

class RcsbPfamContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePfam':
		"""Return to parent (CorePfam)"""
		return self._parent if self._parent else self
	@property
	def pfam_id(self) -> 'RcsbPfamContainerIdentifiers':
		"""Accession number of Pfam entry."""
		self._enter('pfam_id', Query)
		return self

class RcsbPolymerEntity(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'RcsbPolymerEntity':
		"""A description of special aspects of the entity."""
		self._enter('details', Query)
		return self
	@property
	def formula_weight(self) -> 'RcsbPolymerEntity':
		"""Formula mass (KDa) of the entity.  Examples: null, null """
		self._enter('formula_weight', Query)
		return self
	@property
	def pdbx_description(self) -> 'RcsbPolymerEntity':
		"""A description of the polymer entity.  Examples: Green fluorescent protein, 23S ribosomal RNA, NAD-dependent protein deacylase sirtuin-5, mitochondrial """
		self._enter('pdbx_description', Query)
		return self
	@property
	def pdbx_ec(self) -> 'RcsbPolymerEntity':
		"""Enzyme Commission (EC) number(s)  Examples: 2.7.7.7 """
		self._enter('pdbx_ec', Query)
		return self
	@property
	def pdbx_fragment(self) -> 'RcsbPolymerEntity':
		"""Polymer entity fragment description(s).  Examples: KLENOW FRAGMENT, REPLICASE OPERATOR HAIRPIN, C-TERMINAL DOMAIN """
		self._enter('pdbx_fragment', Query)
		return self
	@property
	def pdbx_mutation(self) -> 'RcsbPolymerEntity':
		"""Details about any polymer entity mutation(s).  Examples: Y31H, DEL(298-323) """
		self._enter('pdbx_mutation', Query)
		return self
	@property
	def pdbx_number_of_molecules(self) -> 'RcsbPolymerEntity':
		"""The number of molecules of the entity in the entry."""
		self._enter('pdbx_number_of_molecules', Query)
		return self
	@property
	def rcsb_ec_lineage(self) -> 'RcsbPolymerEntityRcsbEcLineage':
		""""""
		return self._enter('rcsb_ec_lineage', RcsbPolymerEntityRcsbEcLineage)
	@property
	def rcsb_enzyme_class_combined(self) -> 'RcsbPolymerEntityRcsbEnzymeClassCombined':
		""""""
		return self._enter('rcsb_enzyme_class_combined', RcsbPolymerEntityRcsbEnzymeClassCombined)
	@property
	def rcsb_macromolecular_names_combined(self) -> 'RcsbPolymerEntityRcsbMacromolecularNamesCombined':
		""""""
		return self._enter('rcsb_macromolecular_names_combined', RcsbPolymerEntityRcsbMacromolecularNamesCombined)
	@property
	def rcsb_multiple_source_flag(self) -> 'RcsbPolymerEntity':
		"""A code indicating the entity has multiple biological sources.  Allowable values: N, Y """
		self._enter('rcsb_multiple_source_flag', Query)
		return self
	@property
	def rcsb_polymer_name_combined(self) -> 'RcsbPolymerEntityRcsbPolymerNameCombined':
		""""""
		return self._enter('rcsb_polymer_name_combined', RcsbPolymerEntityRcsbPolymerNameCombined)
	@property
	def rcsb_source_part_count(self) -> 'RcsbPolymerEntity':
		"""The number of biological sources for the polymer entity. Multiple source contributions  may come from the same organism (taxonomy)."""
		self._enter('rcsb_source_part_count', Query)
		return self
	@property
	def rcsb_source_taxonomy_count(self) -> 'RcsbPolymerEntity':
		"""The number of distinct source taxonomies for the polymer entity. Commonly used to identify chimeric polymers."""
		self._enter('rcsb_source_taxonomy_count', Query)
		return self
	@property
	def src_method(self) -> 'RcsbPolymerEntity':
		"""The method by which the sample for the polymer entity was produced.  Entities isolated directly from natural sources (tissues, soil  samples etc.) are expected to have further information in the  ENTITY_SRC_NAT category. Entities isolated from genetically  manipulated sources are expected to have further information in  the ENTITY_SRC_GEN category.  Allowable values: man, nat, syn """
		self._enter('src_method', Query)
		return self

class RcsbPolymerEntityAlign(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def aligned_regions(self) -> 'RcsbPolymerEntityAlignAlignedRegions':
		""""""
		return self._enter('aligned_regions', RcsbPolymerEntityAlignAlignedRegions)
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityAlign':
		"""Code identifying the individual, organization or program that  assigned the reference sequence.  Examples: PDB, SIFTS, RCSB """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_database_accession(self) -> 'RcsbPolymerEntityAlign':
		"""Reference sequence accession code.  Examples: Q9HD40 """
		self._enter('reference_database_accession', Query)
		return self
	@property
	def reference_database_isoform(self) -> 'RcsbPolymerEntityAlign':
		"""Reference sequence isoform identifier.  Examples: P01116-2 """
		self._enter('reference_database_isoform', Query)
		return self
	@property
	def reference_database_name(self) -> 'RcsbPolymerEntityAlign':
		"""Reference sequence database name.  Allowable values: EMBL, GenBank, NDB, NORINE, PDB, PIR, PRF, RefSeq, UniProt """
		self._enter('reference_database_name', Query)
		return self

class RcsbPolymerEntityAlignAlignedRegions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityAlign':
		"""Return to parent (RcsbPolymerEntityAlign)"""
		return self._parent if self._parent else self
	@property
	def entity_beg_seq_id(self) -> 'RcsbPolymerEntityAlignAlignedRegions':
		"""An identifier for the monomer in the entity sequence at which this segment of the alignment begins."""
		self._enter('entity_beg_seq_id', Query)
		return self
	@property
	def length(self) -> 'RcsbPolymerEntityAlignAlignedRegions':
		"""The length of this segment of the alignment."""
		self._enter('length', Query)
		return self
	@property
	def ref_beg_seq_id(self) -> 'RcsbPolymerEntityAlignAlignedRegions':
		"""An identifier for the monomer in the reference sequence at which this segment of the alignment begins."""
		self._enter('ref_beg_seq_id', Query)
		return self

class RcsbPolymerEntityAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbPolymerEntityAnnotationAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbPolymerEntityAnnotationAdditionalProperties)
	@property
	def annotation_id(self) -> 'RcsbPolymerEntityAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbPolymerEntityAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbPolymerEntityAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbPolymerEntityAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbPolymerEntityAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbPolymerEntityAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: PDB, UniProt """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbPolymerEntityAnnotation':
		"""A type or category of the annotation.  Allowable values: CARD, GO, GlyCosmos, GlyGen, InterPro, MemProtMD, OPM, PDBTM, Pfam, mpstruc """
		self._enter('type', Query)
		return self

class RcsbPolymerEntityAnnotationAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityAnnotation':
		"""Return to parent (RcsbPolymerEntityAnnotation)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbPolymerEntityAnnotationAdditionalProperties':
		"""The additional property name.  Allowable values: CARD_ARO_CATEGORY, CARD_ARO_CVTERM_ID, CARD_ARO_DRUG_CLASS, CARD_ARO_RESISTANCE_MECHANISM """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbPolymerEntityAnnotationAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbPolymerEntityAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityAnnotation':
		"""Return to parent (RcsbPolymerEntityAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbPolymerEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbPolymerEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbPolymerEntityAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbPolymerEntityContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def asym_ids(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Instance identifiers corresponding to copies of the entity in this container."""
		self._enter('asym_ids', Query)
		return self
	@property
	def auth_asym_ids(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Author instance identifiers corresponding to copies of the entity in this container."""
		self._enter('auth_asym_ids', Query)
		return self
	@property
	def chem_comp_monomers(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Unique list of monomer chemical component identifiers in the polymer entity in this container."""
		self._enter('chem_comp_monomers', Query)
		return self
	@property
	def chem_comp_nstd_monomers(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Unique list of non-standard monomer chemical component identifiers in the polymer entity in this container."""
		self._enter('chem_comp_nstd_monomers', Query)
		return self
	@property
	def chem_ref_def_id(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""The chemical reference definition identifier for the entity in this container.  Examples: PRD_000010 """
		self._enter('chem_ref_def_id', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Entity identifier for the container.  Examples: 1, 2 """
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Entry identifier for the container.  Examples: 4HHB, 1KIP """
		self._enter('entry_id', Query)
		return self
	@property
	def prd_id(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""The BIRD identifier for the entity in this container.  Examples: PRD_000010 """
		self._enter('prd_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""A unique identifier for each object in this entity container formed by  an underscore separated concatenation of entry and entity identifiers.  Examples: 6EL3_1 """
		self._enter('rcsb_id', Query)
		return self
	@property
	def reference_sequence_identifiers(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		""""""
		return self._enter('reference_sequence_identifiers', RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers)
	@property
	def uniprot_ids(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Uniprot accession codes assigned to polymeric entities."""
		self._enter('uniprot_ids', Query)
		return self

class RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityContainerIdentifiers':
		"""Return to parent (RcsbPolymerEntityContainerIdentifiers)"""
		return self._parent if self._parent else self
	@property
	def database_accession(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		"""Reference database accession code  Examples: P01116, 55771382 """
		self._enter('database_accession', Query)
		return self
	@property
	def database_isoform(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		"""Reference database identifier for the sequence isoform  Examples: P01116-2 """
		self._enter('database_isoform', Query)
		return self
	@property
	def database_name(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		"""Reference database name  Allowable values: EMBL, GenBank, NDB, NORINE, PDB, PIR, PRF, RefSeq, UniProt """
		self._enter('database_name', Query)
		return self
	@property
	def entity_sequence_coverage(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		"""Indicates what fraction of this polymer entity sequence is covered by the reference sequence.  Examples: null, null """
		self._enter('entity_sequence_coverage', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		"""Source of the reference database assignment  Allowable values: PDB, RCSB, SIFTS, UniProt """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_sequence_coverage(self) -> 'RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers':
		"""Indicates what fraction of the reference sequence is covered by this polymer entity sequence.  Examples: null, null """
		self._enter('reference_sequence_coverage', Query)
		return self

class RcsbPolymerEntityFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbPolymerEntityFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbPolymerEntityFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbPolymerEntityFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbPolymerEntityFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbPolymerEntityFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'RcsbPolymerEntityFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', RcsbPolymerEntityFeatureFeaturePositions)
	@property
	def name(self) -> 'RcsbPolymerEntityFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityFeature':
		"""Code identifying the individual, organization or program that  assigned the feature.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_scheme(self) -> 'RcsbPolymerEntityFeature':
		"""Code residue coordinate system for the assigned feature.  Allowable values: NCBI, PDB entity, UniProt """
		self._enter('reference_scheme', Query)
		return self
	@property
	def type(self) -> 'RcsbPolymerEntityFeature':
		"""A type or category of the feature.  Allowable values: CARD_MODEL, IMGT_ANTIBODY_DESCRIPTION, IMGT_ANTIBODY_DOMAIN_NAME, IMGT_ANTIBODY_GENE_ALLELE_NAME, IMGT_ANTIBODY_ORGANISM_NAME, IMGT_ANTIBODY_PROTEIN_NAME, IMGT_ANTIBODY_RECEPTOR_DESCRIPTION, IMGT_ANTIBODY_RECEPTOR_TYPE, Pfam, SABDAB_ANTIBODY_ANTIGEN_NAME, SABDAB_ANTIBODY_NAME, SABDAB_ANTIBODY_TARGET, artifact, disorder, disorder_binding, hydropathy, modified_monomer, mutation """
		self._enter('type', Query)
		return self

class RcsbPolymerEntityFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityFeature':
		"""Return to parent (RcsbPolymerEntityFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbPolymerEntityFeatureAdditionalProperties':
		"""The additional property name.  Allowable values: CARD_MODEL_DESCRIPTION, CARD_MODEL_ORGANISM, PARENT_COMP_ID """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbPolymerEntityFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbPolymerEntityFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityFeature':
		"""Return to parent (RcsbPolymerEntityFeature)"""
		return self._parent if self._parent else self
	@property
	def beg_comp_id(self) -> 'RcsbPolymerEntityFeatureFeaturePositions':
		"""An identifier for the leading monomer corresponding to the feature assignment.  Examples: TRP, VAL """
		self._enter('beg_comp_id', Query)
		return self
	@property
	def beg_seq_id(self) -> 'RcsbPolymerEntityFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature begins."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'RcsbPolymerEntityFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature ends."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def value(self) -> 'RcsbPolymerEntityFeatureFeaturePositions':
		"""The value for the feature over this monomer segment.  Examples: null, null """
		self._enter('value', Query)
		return self
	@property
	def values(self) -> 'RcsbPolymerEntityFeatureFeaturePositions':
		"""The value(s) for the feature over this monomer segment."""
		self._enter('values', Query)
		return self

class RcsbPolymerEntityFeatureSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def count(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""The feature count."""
		self._enter('count', Query)
		return self
	@property
	def coverage(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""The fractional feature coverage relative to the full entity sequence.  For instance, the fraction of features such as mutations, artifacts or modified monomers  relative to the length of the entity sequence.  Examples: null, null """
		self._enter('coverage', Query)
		return self
	@property
	def maximum_length(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""The maximum feature length."""
		self._enter('maximum_length', Query)
		return self
	@property
	def maximum_value(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""The maximum feature value.  Examples: null, null """
		self._enter('maximum_value', Query)
		return self
	@property
	def minimum_length(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""The minimum feature length."""
		self._enter('minimum_length', Query)
		return self
	@property
	def minimum_value(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""The minimum feature value.  Examples: null, null """
		self._enter('minimum_value', Query)
		return self
	@property
	def type(self) -> 'RcsbPolymerEntityFeatureSummary':
		"""Type or category of the feature.  Allowable values: CARD_MODEL, IMGT_ANTIBODY_DESCRIPTION, IMGT_ANTIBODY_DOMAIN_NAME, IMGT_ANTIBODY_GENE_ALLELE_NAME, IMGT_ANTIBODY_ORGANISM_NAME, IMGT_ANTIBODY_PROTEIN_NAME, IMGT_ANTIBODY_RECEPTOR_DESCRIPTION, IMGT_ANTIBODY_RECEPTOR_TYPE, Pfam, SABDAB_ANTIBODY_ANTIGEN_NAME, SABDAB_ANTIBODY_NAME, SABDAB_ANTIBODY_TARGET, artifact, modified_monomer, mutation """
		self._enter('type', Query)
		return self

class RcsbPolymerEntityGroupMembersRankings(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupPolymerEntity':
		"""Return to parent (GroupPolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def group_members(self) -> 'RcsbPolymerEntityGroupMembersRankingsGroupMembers':
		""""""
		return self._enter('group_members', RcsbPolymerEntityGroupMembersRankingsGroupMembers)
	@property
	def ranking_criteria_type(self) -> 'RcsbPolymerEntityGroupMembersRankings':
		"""Defines ranking option applicable to group members  Allowable values: coverage """
		self._enter('ranking_criteria_type', Query)
		return self

class RcsbPolymerEntityGroupMembersRankingsGroupMembers(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityGroupMembersRankings':
		"""Return to parent (RcsbPolymerEntityGroupMembersRankings)"""
		return self._parent if self._parent else self
	@property
	def member_id(self) -> 'RcsbPolymerEntityGroupMembersRankingsGroupMembers':
		""""""
		self._enter('member_id', Query)
		return self
	@property
	def original_score(self) -> 'RcsbPolymerEntityGroupMembersRankingsGroupMembers':
		"""Quantifies the criteria used for ranking"""
		self._enter('original_score', Query)
		return self
	@property
	def rank(self) -> 'RcsbPolymerEntityGroupMembersRankingsGroupMembers':
		"""Reflects a relationship between group members such that, for any two members the first is ranked higher (smaller rank value) than the second"""
		self._enter('rank', Query)
		return self

class RcsbPolymerEntityGroupMembership(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def aggregation_method(self) -> 'RcsbPolymerEntityGroupMembership':
		"""Method used to establish group membership  Allowable values: matching_uniprot_accession, sequence_identity """
		self._enter('aggregation_method', Query)
		return self
	@property
	def aligned_regions(self) -> 'RcsbPolymerEntityGroupMembershipAlignedRegions':
		""""""
		return self._enter('aligned_regions', RcsbPolymerEntityGroupMembershipAlignedRegions)
	@property
	def group_id(self) -> 'RcsbPolymerEntityGroupMembership':
		"""A unique identifier for a group of entities  Examples: 1_100, P00003 """
		self._enter('group_id', Query)
		return self
	@property
	def similarity_cutoff(self) -> 'RcsbPolymerEntityGroupMembership':
		"""Degree of similarity expressed as a floating-point number"""
		self._enter('similarity_cutoff', Query)
		return self

class RcsbPolymerEntityGroupMembershipAlignedRegions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityGroupMembership':
		"""Return to parent (RcsbPolymerEntityGroupMembership)"""
		return self._parent if self._parent else self
	@property
	def entity_beg_seq_id(self) -> 'RcsbPolymerEntityGroupMembershipAlignedRegions':
		"""An identifier for the monomer in the entity sequence at which this segment of the alignment begins."""
		self._enter('entity_beg_seq_id', Query)
		return self
	@property
	def length(self) -> 'RcsbPolymerEntityGroupMembershipAlignedRegions':
		"""The length of this segment of the alignment."""
		self._enter('length', Query)
		return self
	@property
	def ref_beg_seq_id(self) -> 'RcsbPolymerEntityGroupMembershipAlignedRegions':
		"""An identifier for the monomer in the reference sequence at which this segment of the alignment begins."""
		self._enter('ref_beg_seq_id', Query)
		return self

class RcsbPolymerEntityGroupSequenceAlignment(QueryNode):
	""""""
	@property
	def end(self) -> 'GroupPolymerEntity':
		"""Return to parent (GroupPolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def abstract_reference(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentAbstractReference':
		"""Abstract reference where group members can be aligned to generate a MSA"""
		return self._enter('abstract_reference', RcsbPolymerEntityGroupSequenceAlignmentAbstractReference)
	@property
	def group_members_alignment(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment':
		"""Alignment with a core_entity canonical sequence"""
		return self._enter('group_members_alignment', RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment)

class RcsbPolymerEntityGroupSequenceAlignmentAbstractReference(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityGroupSequenceAlignment':
		"""Return to parent (RcsbPolymerEntityGroupSequenceAlignment)"""
		return self._parent if self._parent else self
	@property
	def length(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentAbstractReference':
		"""Abstract reference length"""
		self._enter('length', Query)
		return self
	@property
	def sequence(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentAbstractReference':
		"""Sequence that represents the abstract reference"""
		self._enter('sequence', Query)
		return self

class RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntityGroupSequenceAlignment':
		"""Return to parent (RcsbPolymerEntityGroupSequenceAlignment)"""
		return self._parent if self._parent else self
	@property
	def aligned_regions(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment':
		"""Alignment region encoded as a triplet [query_begin, target_begin, length]"""
		self._enter('aligned_regions', Query)
		return self
	@property
	def member_id(self) -> 'RcsbPolymerEntityGroupSequenceAlignmentGroupMembersAlignment':
		""""""
		self._enter('member_id', Query)
		return self
	@property
	def scores(self) -> 'GroupMembersAlignmentScores':
		"""Alignment scores"""
		return self._enter('scores', GroupMembersAlignmentScores)

class RcsbPolymerEntityInstanceContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntityInstance':
		"""Return to parent (CorePolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def asym_id(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		"""Instance identifier for this container."""
		self._enter('asym_id', Query)
		return self
	@property
	def auth_asym_id(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		"""Author instance identifier for this container."""
		self._enter('auth_asym_id', Query)
		return self
	@property
	def auth_to_entity_poly_seq_mapping(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		"""Residue index mappings between author provided and entity polymer sequence positions.   Author residue indices (auth_seq_num) include insertion codes when present.  The array indices correspond to the indices (1-based) of the deposited sample  sequence (entity_poly_seq). Unmodelled residues are represented with a '?' value."""
		self._enter('auth_to_entity_poly_seq_mapping', Query)
		return self
	@property
	def entity_id(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		"""Entity identifier for the container."""
		self._enter('entity_id', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		"""Entry identifier for the container."""
		self._enter('entry_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbPolymerEntityInstanceContainerIdentifiers':
		"""A unique identifier for each object in this entity instance container formed by  an 'dot' (.) separated concatenation of entry and entity instance identifiers.  Examples: 1KIP.A """
		self._enter('rcsb_id', Query)
		return self

class RcsbPolymerEntityKeywords(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def text(self) -> 'RcsbPolymerEntityKeywords':
		"""Keywords describing this polymer entity."""
		self._enter('text', Query)
		return self

class RcsbPolymerEntityNameCom(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbPolymerEntityNameCom':
		"""A common name for the polymer entity.  Examples: HIV protease monomer, hemoglobin alpha chain """
		self._enter('name', Query)
		return self

class RcsbPolymerEntityNameSys(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbPolymerEntityNameSys':
		"""The systematic name for the polymer entity."""
		self._enter('name', Query)
		return self
	@property
	def system(self) -> 'RcsbPolymerEntityNameSys':
		"""The system used to generate the systematic name of the polymer entity.  Examples: Chemical Abstracts conventions """
		self._enter('system', Query)
		return self

class RcsbPolymerEntityRcsbEcLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntity':
		"""Return to parent (RcsbPolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbPolymerEntityRcsbEcLineage':
		"""Members of the enzyme classification lineage as parent classification hierarchy depth (1-N)."""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbPolymerEntityRcsbEcLineage':
		"""Members of the enzyme classification lineage as parent classification codes.  Examples: 2, 2.7.1.153 """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbPolymerEntityRcsbEcLineage':
		"""Members of the enzyme classification lineage as parent classification names.  Examples: Transferases, phosphatidylinositol-4,5-bisphosphate 3-kinase """
		self._enter('name', Query)
		return self

class RcsbPolymerEntityRcsbEnzymeClassCombined(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntity':
		"""Return to parent (RcsbPolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbPolymerEntityRcsbEnzymeClassCombined':
		"""The enzyme classification hierarchy depth (1-N)."""
		self._enter('depth', Query)
		return self
	@property
	def ec(self) -> 'RcsbPolymerEntityRcsbEnzymeClassCombined':
		"""Combined list of enzyme class assignments."""
		self._enter('ec', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityRcsbEnzymeClassCombined':
		"""Combined list of enzyme class associated provenance sources.  Allowable values: PDB Primary Data, UniProt """
		self._enter('provenance_source', Query)
		return self

class RcsbPolymerEntityRcsbMacromolecularNamesCombined(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntity':
		"""Return to parent (RcsbPolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbPolymerEntityRcsbMacromolecularNamesCombined':
		"""Combined list of macromolecular names.  Examples: Lysozyme C, Plasmid recombination enzyme, Pyruvate carboxylase """
		self._enter('name', Query)
		return self
	@property
	def provenance_code(self) -> 'RcsbPolymerEntityRcsbMacromolecularNamesCombined':
		"""Combined list of macromolecular names associated provenance code.   ECO (https://github.com/evidenceontology/evidenceontology)"""
		self._enter('provenance_code', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityRcsbMacromolecularNamesCombined':
		"""Combined list of macromolecular names associated name source.  Allowable values: PDB Preferred Name, PDB Synonym """
		self._enter('provenance_source', Query)
		return self

class RcsbPolymerEntityRcsbPolymerNameCombined(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerEntity':
		"""Return to parent (RcsbPolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def names(self) -> 'RcsbPolymerEntityRcsbPolymerNameCombined':
		"""Protein name annotated by the UniProtKB or macromolecular name assigned by the PDB."""
		self._enter('names', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerEntityRcsbPolymerNameCombined':
		"""Provenance source for the combined protein names.  Allowable values: PDB Description, PDB Preferred Name, UniProt Name """
		self._enter('provenance_source', Query)
		return self

class RcsbPolymerInstanceAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntityInstance':
		"""Return to parent (CorePolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def annotation_id(self) -> 'RcsbPolymerInstanceAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbPolymerInstanceAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbPolymerInstanceAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbPolymerInstanceAnnotation':
		"""Identifies the version of the annotation assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbPolymerInstanceAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbPolymerInstanceAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbPolymerInstanceAnnotation':
		"""Ordinal identifier for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerInstanceAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation.  Examples: PDB """
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbPolymerInstanceAnnotation':
		"""A type or category of the annotation.  Allowable values: CATH, ECOD, GlyGen, SCOP, SCOP2 """
		self._enter('type', Query)
		return self

class RcsbPolymerInstanceAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerInstanceAnnotation':
		"""Return to parent (RcsbPolymerInstanceAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbPolymerInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbPolymerInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbPolymerInstanceAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbPolymerInstanceFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntityInstance':
		"""Return to parent (CorePolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbPolymerInstanceFeatureAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbPolymerInstanceFeatureAdditionalProperties)
	@property
	def assignment_version(self) -> 'RcsbPolymerInstanceFeature':
		"""Identifies the version of the feature assignment.  Examples: V4_0_2 """
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbPolymerInstanceFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbPolymerInstanceFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'RcsbPolymerInstanceFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', RcsbPolymerInstanceFeatureFeaturePositions)
	@property
	def name(self) -> 'RcsbPolymerInstanceFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def ordinal(self) -> 'RcsbPolymerInstanceFeature':
		"""Ordinal identifier for this category"""
		self._enter('ordinal', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbPolymerInstanceFeature':
		"""Code identifying the individual, organization or program that  assigned the feature.  Examples: CATH, SCOP """
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_scheme(self) -> 'RcsbPolymerInstanceFeature':
		"""Code residue coordinate system for the assigned feature.  Allowable values: NCBI, PDB entity, PDB entry, UniProt """
		self._enter('reference_scheme', Query)
		return self
	@property
	def type(self) -> 'RcsbPolymerInstanceFeature':
		"""A type or category of the feature.  Allowable values: ANGLE_OUTLIER, ANGLE_OUTLIERS, ASA, AVERAGE_OCCUPANCY, BEND, BINDING_SITE, BOND_OUTLIER, BOND_OUTLIERS, C-MANNOSYLATION_SITE, CATH, CHIRAL_OUTLIERS, CIS-PEPTIDE, CLASHES, ECOD, HELIX_P, HELX_LH_PP_P, HELX_RH_3T_P, HELX_RH_AL_P, HELX_RH_PI_P, LIGAND_COVALENT_LINKAGE, LIGAND_INTERACTION, LIGAND_METAL_COORDINATION_LINKAGE, MA_QA_METRIC_LOCAL_TYPE_CONTACT_PROBABILITY, MA_QA_METRIC_LOCAL_TYPE_DISTANCE, MA_QA_METRIC_LOCAL_TYPE_ENERGY, MA_QA_METRIC_LOCAL_TYPE_IPTM, MA_QA_METRIC_LOCAL_TYPE_NORMALIZED_SCORE, MA_QA_METRIC_LOCAL_TYPE_OTHER, MA_QA_METRIC_LOCAL_TYPE_PAE, MA_QA_METRIC_LOCAL_TYPE_PLDDT, MA_QA_METRIC_LOCAL_TYPE_PLDDT_ALL-ATOM, MA_QA_METRIC_LOCAL_TYPE_PLDDT_ALL-ATOM_[0,1], MA_QA_METRIC_LOCAL_TYPE_PLDDT_[0,1], MA_QA_METRIC_LOCAL_TYPE_PTM, MA_QA_METRIC_LOCAL_TYPE_ZSCORE, MEMBRANE_SEGMENT, MOGUL_ANGLE_OUTLIER, MOGUL_ANGLE_OUTLIERS, MOGUL_BOND_OUTLIER, MOGUL_BOND_OUTLIERS, MOGUL_RING_OUTLIERS, MOGUL_TORSION_OUTLIERS, N-GLYCOSYLATION_SITE, NATOMS_EDS, O-GLYCOSYLATION_SITE, OWAB, PLANE_OUTLIERS, Q_SCORE, RAMACHANDRAN_OUTLIER, ROTAMER_OUTLIER, RSCC, RSCC_OUTLIER, RSR, RSRZ, RSRZ_OUTLIER, S-GLYCOSYLATION_SITE, SABDAB_ANTIBODY_HEAVY_CHAIN_SUBCLASS, SABDAB_ANTIBODY_LIGHT_CHAIN_SUBCLASS, SABDAB_ANTIBODY_LIGHT_CHAIN_TYPE, SCOP, SCOP2B_SUPERFAMILY, SCOP2_FAMILY, SCOP2_SUPERFAMILY, SHEET, STEREO_OUTLIER, STRN, SYMM_CLASHES, TURN_TY1_P, UNASSIGNED_SEC_STRUCT, UNOBSERVED_ATOM_XYZ, UNOBSERVED_RESIDUE_XYZ, ZERO_OCCUPANCY_ATOM_XYZ, ZERO_OCCUPANCY_RESIDUE_XYZ """
		self._enter('type', Query)
		return self

class RcsbPolymerInstanceFeatureAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerInstanceFeature':
		"""Return to parent (RcsbPolymerInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbPolymerInstanceFeatureAdditionalProperties':
		"""The additional property name.  Allowable values: CATH_DOMAIN_ID, CATH_NAME, ECOD_DOMAIN_ID, ECOD_FAMILY_NAME, MODELCIF_MODEL_ID, OMEGA_ANGLE, PARTNER_ASYM_ID, PARTNER_BOND_DISTANCE, PARTNER_COMP_ID, PDB_MODEL_NUM, SCOP2_DOMAIN_ID, SCOP2_FAMILY_ID, SCOP2_FAMILY_NAME, SCOP2_SUPERFAMILY_ID, SCOP2_SUPERFAMILY_NAME, SCOP_DOMAIN_ID, SCOP_NAME, SCOP_SUN_ID, SHEET_SENSE """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbPolymerInstanceFeatureAdditionalProperties':
		"""The value(s) of the additional property."""
		self._enter('values', Query)
		return self

class RcsbPolymerInstanceFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerInstanceFeature':
		"""Return to parent (RcsbPolymerInstanceFeature)"""
		return self._parent if self._parent else self
	@property
	def beg_comp_id(self) -> 'RcsbPolymerInstanceFeatureFeaturePositions':
		"""An identifier for the monomer(s) corresponding to the feature assignment.  Examples: TRP, VAL """
		self._enter('beg_comp_id', Query)
		return self
	@property
	def beg_seq_id(self) -> 'RcsbPolymerInstanceFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature begins."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'RcsbPolymerInstanceFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature ends."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def value(self) -> 'RcsbPolymerInstanceFeatureFeaturePositions':
		"""The value of the feature over the monomer segment.  Examples: null, null """
		self._enter('value', Query)
		return self
	@property
	def values(self) -> 'RcsbPolymerInstanceFeatureFeaturePositions':
		"""The value(s) of the feature over the monomer segment."""
		self._enter('values', Query)
		return self

class RcsbPolymerInstanceFeatureSummary(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntityInstance':
		"""Return to parent (CorePolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def count(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""The feature count per polymer chain."""
		self._enter('count', Query)
		return self
	@property
	def coverage(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""The fractional feature coverage relative to the full entity sequence.  Examples: null, null """
		self._enter('coverage', Query)
		return self
	@property
	def maximum_length(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""The maximum feature length."""
		self._enter('maximum_length', Query)
		return self
	@property
	def maximum_value(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""The maximum feature value.  Examples: null, null """
		self._enter('maximum_value', Query)
		return self
	@property
	def minimum_length(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""The minimum feature length."""
		self._enter('minimum_length', Query)
		return self
	@property
	def minimum_value(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""The minimum feature value.  Examples: null, null """
		self._enter('minimum_value', Query)
		return self
	@property
	def type(self) -> 'RcsbPolymerInstanceFeatureSummary':
		"""Type or category of the feature.  Allowable values: ANGLE_OUTLIER, ANGLE_OUTLIERS, AVERAGE_OCCUPANCY, BEND, BINDING_SITE, BOND_OUTLIER, BOND_OUTLIERS, C-MANNOSYLATION_SITE, CATH, CHIRAL_OUTLIERS, CIS-PEPTIDE, CLASHES, ECOD, HELIX_P, HELX_LH_PP_P, HELX_RH_3T_P, HELX_RH_AL_P, HELX_RH_PI_P, LIGAND_COVALENT_LINKAGE, LIGAND_INTERACTION, LIGAND_METAL_COORDINATION_LINKAGE, MA_QA_METRIC_LOCAL_TYPE_CONTACT_PROBABILITY, MA_QA_METRIC_LOCAL_TYPE_DISTANCE, MA_QA_METRIC_LOCAL_TYPE_ENERGY, MA_QA_METRIC_LOCAL_TYPE_IPTM, MA_QA_METRIC_LOCAL_TYPE_NORMALIZED_SCORE, MA_QA_METRIC_LOCAL_TYPE_OTHER, MA_QA_METRIC_LOCAL_TYPE_PAE, MA_QA_METRIC_LOCAL_TYPE_PLDDT, MA_QA_METRIC_LOCAL_TYPE_PLDDT_ALL-ATOM, MA_QA_METRIC_LOCAL_TYPE_PLDDT_ALL-ATOM_[0,1], MA_QA_METRIC_LOCAL_TYPE_PLDDT_[0,1], MA_QA_METRIC_LOCAL_TYPE_PTM, MA_QA_METRIC_LOCAL_TYPE_ZSCORE, MEMBRANE_SEGMENT, MOGUL_ANGLE_OUTLIER, MOGUL_ANGLE_OUTLIERS, MOGUL_BOND_OUTLIER, MOGUL_BOND_OUTLIERS, MOGUL_RING_OUTLIERS, MOGUL_TORSION_OUTLIERS, N-GLYCOSYLATION_SITE, NATOMS_EDS, O-GLYCOSYLATION_SITE, OWAB, PLANE_OUTLIERS, Q_SCORE, RAMACHANDRAN_OUTLIER, ROTAMER_OUTLIER, RSCC, RSCC_OUTLIER, RSR, RSRZ, RSRZ_OUTLIER, S-GLYCOSYLATION_SITE, SABDAB_ANTIBODY_HEAVY_CHAIN_SUBCLASS, SABDAB_ANTIBODY_LIGHT_CHAIN_SUBCLASS, SABDAB_ANTIBODY_LIGHT_CHAIN_TYPE, SCOP, SCOP2B_SUPERFAMILY, SCOP2_FAMILY, SCOP2_SUPERFAMILY, SHEET, STEREO_OUTLIER, STRN, SYMM_CLASHES, TURN_TY1_P, UNASSIGNED_SEC_STRUCT, UNOBSERVED_ATOM_XYZ, UNOBSERVED_RESIDUE_XYZ, ZERO_OCCUPANCY_ATOM_XYZ, ZERO_OCCUPANCY_RESIDUE_XYZ """
		self._enter('type', Query)
		return self

class RcsbPolymerInstanceInfo(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntityInstance':
		"""Return to parent (CorePolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def modeled_residue_count(self) -> 'RcsbPolymerInstanceInfo':
		"""The number of modeled residues in the polymer instance."""
		self._enter('modeled_residue_count', Query)
		return self

class RcsbPolymerStructConn(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntityInstance':
		"""Return to parent (CorePolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def connect_partner(self) -> 'RcsbPolymerStructConnConnectPartner':
		""""""
		return self._enter('connect_partner', RcsbPolymerStructConnConnectPartner)
	@property
	def connect_target(self) -> 'RcsbPolymerStructConnConnectTarget':
		""""""
		return self._enter('connect_target', RcsbPolymerStructConnConnectTarget)
	@property
	def connect_type(self) -> 'RcsbPolymerStructConn':
		"""The connection type.  Allowable values: covalent bond, covalent modification of a nucleotide base, covalent modification of a nucleotide phosphate, covalent modification of a nucleotide sugar, covalent residue modification, disulfide bridge, hydrogen bond, ionic interaction, metal coordination, mismatched base pairs """
		self._enter('connect_type', Query)
		return self
	@property
	def description(self) -> 'RcsbPolymerStructConn':
		"""A description of special details of the connection.  Examples: Watson-Crick base pair """
		self._enter('description', Query)
		return self
	@property
	def dist_value(self) -> 'RcsbPolymerStructConn':
		"""Distance value for this contact."""
		self._enter('dist_value', Query)
		return self
	@property
	def id(self) -> 'RcsbPolymerStructConn':
		"""The value of _rcsb_polymer_struct_conn.id is an identifier for connection.   Note that this item need not be a number; it can be any unique  identifier."""
		self._enter('id', Query)
		return self
	@property
	def ordinal_id(self) -> 'RcsbPolymerStructConn':
		"""The value of _rcsb_polymer_struct_conn.id must uniquely identify a record in  the rcsb_polymer_struct_conn list."""
		self._enter('ordinal_id', Query)
		return self
	@property
	def role(self) -> 'RcsbPolymerStructConn':
		"""The chemical or structural role of the interaction  Allowable values: C-Mannosylation, N-Glycosylation, O-Glycosylation, S-Glycosylation """
		self._enter('role', Query)
		return self
	@property
	def value_order(self) -> 'RcsbPolymerStructConn':
		"""The chemical bond order associated with the specified atoms in  this contact.  Allowable values: doub, quad, sing, trip """
		self._enter('value_order', Query)
		return self

class RcsbPolymerStructConnConnectPartner(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerStructConn':
		"""Return to parent (RcsbPolymerStructConn)"""
		return self._parent if self._parent else self
	@property
	def label_alt_id(self) -> 'RcsbPolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
		self._enter('label_alt_id', Query)
		return self
	@property
	def label_asym_id(self) -> 'RcsbPolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_atom_id(self) -> 'RcsbPolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _chem_comp_atom.atom_id in the  CHEM_COMP_ATOM category."""
		self._enter('label_atom_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'RcsbPolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self
	@property
	def label_seq_id(self) -> 'RcsbPolymerStructConnConnectPartner':
		"""A component of the identifier for the partner in the structure  connection.   This data item is a pointer to _atom_site.label_seq_id in the  ATOM_SITE category."""
		self._enter('label_seq_id', Query)
		return self
	@property
	def symmetry(self) -> 'RcsbPolymerStructConnConnectPartner':
		"""Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_polymer_struct_conn.connect_partner_label* to generate the  partner in the structure connection.  Examples: 1_555, 7_645 """
		self._enter('symmetry', Query)
		return self

class RcsbPolymerStructConnConnectTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbPolymerStructConn':
		"""Return to parent (RcsbPolymerStructConn)"""
		return self._parent if self._parent else self
	@property
	def auth_asym_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_asym_id in the  ATOM_SITE category."""
		self._enter('auth_asym_id', Query)
		return self
	@property
	def auth_seq_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.auth_seq_id in the  ATOM_SITE category."""
		self._enter('auth_seq_id', Query)
		return self
	@property
	def label_alt_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_alt_id in the  ATOM_SITE category."""
		self._enter('label_alt_id', Query)
		return self
	@property
	def label_asym_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_asym_id in the  ATOM_SITE category."""
		self._enter('label_asym_id', Query)
		return self
	@property
	def label_atom_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_atom_id in the  ATOM_SITE category."""
		self._enter('label_atom_id', Query)
		return self
	@property
	def label_comp_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.label_comp_id in the  ATOM_SITE category."""
		self._enter('label_comp_id', Query)
		return self
	@property
	def label_seq_id(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""A component of the identifier for the target of the structure  connection.   This data item is a pointer to _atom_site.connect_target_label_seq_id in the  ATOM_SITE category."""
		self._enter('label_seq_id', Query)
		return self
	@property
	def symmetry(self) -> 'RcsbPolymerStructConnConnectTarget':
		"""Describes the symmetry operation that should be applied to the  atom set specified by _rcsb_polymer_struct_conn.label* to generate the  target of the structure connection.  Examples: 1_555, 7_645 """
		self._enter('symmetry', Query)
		return self

class RcsbPrimaryCitation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def book_id_ISBN(self) -> 'RcsbPrimaryCitation':
		"""The International Standard Book Number (ISBN) code assigned to  the book cited; relevant for books or book chapters."""
		self._enter('book_id_ISBN', Query)
		return self
	@property
	def book_publisher(self) -> 'RcsbPrimaryCitation':
		"""The name of the publisher of the citation; relevant  for books or book chapters.  Examples: John Wiley and Sons """
		self._enter('book_publisher', Query)
		return self
	@property
	def book_publisher_city(self) -> 'RcsbPrimaryCitation':
		"""The location of the publisher of the citation; relevant  for books or book chapters.  Examples: London """
		self._enter('book_publisher_city', Query)
		return self
	@property
	def book_title(self) -> 'RcsbPrimaryCitation':
		"""The title of the book in which the citation appeared; relevant  for books or book chapters."""
		self._enter('book_title', Query)
		return self
	@property
	def coordinate_linkage(self) -> 'RcsbPrimaryCitation':
		"""_rcsb_primary_citation.coordinate_linkage states whether this citation  is concerned with precisely the set of coordinates given in the  data block. If, for instance, the publication described the same  structure, but the coordinates had undergone further refinement  prior to the creation of the data block, the value of this data  item would be 'no'.  Allowable values: n, no, y, yes """
		self._enter('coordinate_linkage', Query)
		return self
	@property
	def country(self) -> 'RcsbPrimaryCitation':
		"""The country/region of publication; relevant for books  and book chapters."""
		self._enter('country', Query)
		return self
	@property
	def id(self) -> 'RcsbPrimaryCitation':
		"""The value of _rcsb_primary_citation.id must uniquely identify a record in the  CITATION list.   The _rcsb_primary_citation.id 'primary' should be used to indicate the  citation that the author(s) consider to be the most pertinent to  the contents of the data block.   Note that this item need not be a number; it can be any unique  identifier.  Examples: primary """
		self._enter('id', Query)
		return self
	@property
	def journal_abbrev(self) -> 'RcsbPrimaryCitation':
		"""Abbreviated name of the cited journal as given in the  Chemical Abstracts Service Source Index.  Examples: J.Mol.Biol., J. Mol. Biol. """
		self._enter('journal_abbrev', Query)
		return self
	@property
	def journal_id_ASTM(self) -> 'RcsbPrimaryCitation':
		"""The American Society for Testing and Materials (ASTM) code  assigned to the journal cited (also referred to as the CODEN  designator of the Chemical Abstracts Service); relevant for  journal articles."""
		self._enter('journal_id_ASTM', Query)
		return self
	@property
	def journal_id_CSD(self) -> 'RcsbPrimaryCitation':
		"""The Cambridge Structural Database (CSD) code assigned to the  journal cited; relevant for journal articles. This is also the  system used at the Protein Data Bank (PDB).  Examples: 0070 """
		self._enter('journal_id_CSD', Query)
		return self
	@property
	def journal_id_ISSN(self) -> 'RcsbPrimaryCitation':
		"""The International Standard Serial Number (ISSN) code assigned to  the journal cited; relevant for journal articles."""
		self._enter('journal_id_ISSN', Query)
		return self
	@property
	def journal_issue(self) -> 'RcsbPrimaryCitation':
		"""Issue number of the journal cited; relevant for journal  articles.  Examples: 2 """
		self._enter('journal_issue', Query)
		return self
	@property
	def journal_volume(self) -> 'RcsbPrimaryCitation':
		"""Volume number of the journal cited; relevant for journal  articles.  Examples: 174 """
		self._enter('journal_volume', Query)
		return self
	@property
	def language(self) -> 'RcsbPrimaryCitation':
		"""Language in which the cited article is written.  Examples: German """
		self._enter('language', Query)
		return self
	@property
	def page_first(self) -> 'RcsbPrimaryCitation':
		"""The first page of the citation; relevant for journal  articles, books and book chapters."""
		self._enter('page_first', Query)
		return self
	@property
	def page_last(self) -> 'RcsbPrimaryCitation':
		"""The last page of the citation; relevant for journal  articles, books and book chapters."""
		self._enter('page_last', Query)
		return self
	@property
	def pdbx_database_id_DOI(self) -> 'RcsbPrimaryCitation':
		"""Document Object Identifier used by doi.org to uniquely  specify bibliographic entry.  Examples: 10.2345/S1384107697000225 """
		self._enter('pdbx_database_id_DOI', Query)
		return self
	@property
	def pdbx_database_id_PubMed(self) -> 'RcsbPrimaryCitation':
		"""Ascession number used by PubMed to categorize a specific  bibliographic entry."""
		self._enter('pdbx_database_id_PubMed', Query)
		return self
	@property
	def rcsb_ORCID_identifiers(self) -> 'RcsbPrimaryCitation':
		"""The Open Researcher and Contributor ID (ORCID) identifiers for the citation authors."""
		self._enter('rcsb_ORCID_identifiers', Query)
		return self
	@property
	def rcsb_authors(self) -> 'RcsbPrimaryCitation':
		"""Names of the authors of the citation; relevant for journal  articles, books and book chapters.  Names are separated by vertical bars.   The family name(s), followed by a comma and including any  dynastic components, precedes the first name(s) or initial(s)."""
		self._enter('rcsb_authors', Query)
		return self
	@property
	def rcsb_journal_abbrev(self) -> 'RcsbPrimaryCitation':
		"""Normalized journal abbreviation.  Examples: Nat Struct Mol Biol """
		self._enter('rcsb_journal_abbrev', Query)
		return self
	@property
	def title(self) -> 'RcsbPrimaryCitation':
		"""The title of the citation; relevant for journal articles, books  and book chapters.  Examples: Structure of diferric duck ovotransferrin                                   at 2.35 Angstroms resolution. """
		self._enter('title', Query)
		return self
	@property
	def year(self) -> 'RcsbPrimaryCitation':
		"""The year of the citation; relevant for journal articles, books  and book chapters."""
		self._enter('year', Query)
		return self

class RcsbPubmedContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePubmed':
		"""Return to parent (CorePubmed)"""
		return self._parent if self._parent else self
	@property
	def pubmed_id(self) -> 'RcsbPubmedContainerIdentifiers':
		"""UID assigned to each PubMed record.  Examples: null """
		self._enter('pubmed_id', Query)
		return self

class RcsbPubmedMeshDescriptorsLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePubmed':
		"""Return to parent (CorePubmed)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbPubmedMeshDescriptorsLineage':
		"""Hierarchy depth."""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbPubmedMeshDescriptorsLineage':
		"""Identifier for MeSH classification term.  Examples: E01.370.225.500.388, H01.181 """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbPubmedMeshDescriptorsLineage':
		"""MeSH classification term.  Examples: Chemistry, Mammals, Therapeutic Uses """
		self._enter('name', Query)
		return self

class RcsbRelatedTargetReferences(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def aligned_target(self) -> 'RcsbRelatedTargetReferencesAlignedTarget':
		""""""
		return self._enter('aligned_target', RcsbRelatedTargetReferencesAlignedTarget)
	@property
	def related_resource_name(self) -> 'RcsbRelatedTargetReferences':
		"""The related target data resource name.  Allowable values: ChEMBL, DrugBank, Pharos """
		self._enter('related_resource_name', Query)
		return self
	@property
	def related_resource_version(self) -> 'RcsbRelatedTargetReferences':
		"""The version of the target data resource.  Examples: 6.11.0 """
		self._enter('related_resource_version', Query)
		return self
	@property
	def related_target_id(self) -> 'RcsbRelatedTargetReferences':
		"""An identifier for the target sequence in the related data resource."""
		self._enter('related_target_id', Query)
		return self
	@property
	def target_taxonomy_id(self) -> 'RcsbRelatedTargetReferences':
		"""NCBI Taxonomy identifier for the target organism.   Reference:   Wheeler DL, Chappey C, Lash AE, Leipe DD, Madden TL, Schuler GD,  Tatusova TA, Rapp BA (2000). Database resources of the National  Center for Biotechnology Information. Nucleic Acids Res 2000 Jan  1;28(1):10-4   Benson DA, Karsch-Mizrachi I, Lipman DJ, Ostell J, Rapp BA,  Wheeler DL (2000). GenBank. Nucleic Acids Res 2000 Jan 1;28(1):15-18."""
		self._enter('target_taxonomy_id', Query)
		return self

class RcsbRelatedTargetReferencesAlignedTarget(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbRelatedTargetReferences':
		"""Return to parent (RcsbRelatedTargetReferences)"""
		return self._parent if self._parent else self
	@property
	def entity_beg_seq_id(self) -> 'RcsbRelatedTargetReferencesAlignedTarget':
		"""The position of the monomer in the entity sequence at which the alignment begins."""
		self._enter('entity_beg_seq_id', Query)
		return self
	@property
	def length(self) -> 'RcsbRelatedTargetReferencesAlignedTarget':
		"""The length of the alignment."""
		self._enter('length', Query)
		return self
	@property
	def target_beg_seq_id(self) -> 'RcsbRelatedTargetReferencesAlignedTarget':
		"""The position of the monomer in the target sequence at which the alignment begins."""
		self._enter('target_beg_seq_id', Query)
		return self

class RcsbRepositoryHoldingsCurrent(QueryNode):
	""""""
	@property
	def end(self) -> 'CurrentEntry':
		"""Return to parent (CurrentEntry)"""
		return self._parent if self._parent else self
	@property
	def repository_content_types(self) -> 'RcsbRepositoryHoldingsCurrent':
		"""The list of content types associated with this entry.  Allowable values: 2fo-fc Map, Combined NMR data (NEF), Combined NMR data (NMR-STAR), FASTA sequence, Map Coefficients, NMR chemical shifts, NMR restraints V1, NMR restraints V2, assembly PDB, assembly mmCIF, entry PDB, entry PDB bundle, entry PDBML, entry mmCIF, fo-fc Map, structure factors, validation 2fo-fc coefficients, validation data mmCIF, validation fo-fc coefficients, validation report, validation slider image """
		self._enter('repository_content_types', Query)
		return self

class RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CurrentEntry':
		"""Return to parent (CurrentEntry)"""
		return self._parent if self._parent else self
	@property
	def assembly_ids(self) -> 'RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers':
		"""The assembly id codes."""
		self._enter('assembly_ids', Query)
		return self
	@property
	def entry_id(self) -> 'RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers':
		"""The PDB entry accession code.  Examples: 1KIP """
		self._enter('entry_id', Query)
		return self
	@property
	def rcsb_id(self) -> 'RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers':
		"""The RCSB entry identifier.  Examples: 1KIP """
		self._enter('rcsb_id', Query)
		return self
	@property
	def update_id(self) -> 'RcsbRepositoryHoldingsCurrentEntryContainerIdentifiers':
		"""Identifier for the current data exchange status record.  Examples: 2018_23 """
		self._enter('update_id', Query)
		return self

class RcsbSchemaContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreChemComp':
		"""Return to parent (CoreChemComp)"""
		return self._parent if self._parent else self
	@property
	def collection_name(self) -> 'RcsbSchemaContainerIdentifiers':
		"""Collection name associated with the data in the container."""
		self._enter('collection_name', Query)
		return self
	@property
	def collection_schema_version(self) -> 'RcsbSchemaContainerIdentifiers':
		"""Version string for the schema and collection."""
		self._enter('collection_schema_version', Query)
		return self
	@property
	def schema_name(self) -> 'RcsbSchemaContainerIdentifiers':
		"""Schema name associated with the data in the container."""
		self._enter('schema_name', Query)
		return self

class RcsbStructSymmetry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def clusters(self) -> 'RcsbStructSymmetryClusters':
		"""Clusters describe grouping of identical subunits."""
		return self._enter('clusters', RcsbStructSymmetryClusters)
	@property
	def kind(self) -> 'RcsbStructSymmetry':
		"""The granularity at which the symmetry calculation is performed. In 'Global Symmetry' all polymeric  subunits in assembly are used. In 'Local Symmetry' only a subset of polymeric subunits is considered.  In 'Pseudo Symmetry' the threshold for subunits similarity is relaxed.  Allowable values: Global Symmetry, Local Symmetry, Pseudo Symmetry """
		self._enter('kind', Query)
		return self
	@property
	def oligomeric_state(self) -> 'RcsbStructSymmetry':
		"""Oligomeric state refers to a composition of polymeric subunits in quaternary structure.  Quaternary structure may be composed either exclusively of several copies of identical subunits,  in which case they are termed homo-oligomers, or alternatively by at least one copy of different  subunits (hetero-oligomers). Quaternary structure composed of a single subunit is denoted as 'Monomer'.  Examples: Homo 2-mer, Homo 2-mer, Hetero 3-mer """
		self._enter('oligomeric_state', Query)
		return self
	@property
	def rotation_axes(self) -> 'RcsbStructSymmetryRotationAxes':
		"""The orientation of the principal rotation (symmetry) axis."""
		return self._enter('rotation_axes', RcsbStructSymmetryRotationAxes)
	@property
	def stoichiometry(self) -> 'RcsbStructSymmetry':
		"""Stoichiometry of a complex represents the quantitative description and composition of its subunits."""
		self._enter('stoichiometry', Query)
		return self
	@property
	def symbol(self) -> 'RcsbStructSymmetry':
		"""Symmetry symbol refers to point group or helical symmetry of identical polymeric subunits in Schoenflies notation.  Contains point group symbol (e.g., C2, C5, D2, T, O, I) or H for helical symmetry.  Examples: C1, D3, N """
		self._enter('symbol', Query)
		return self
	@property
	def type(self) -> 'RcsbStructSymmetry':
		"""Symmetry type refers to point group or helical symmetry of identical polymeric subunits.  Contains point group types (e.g. Cyclic, Dihedral) or Helical for helical symmetry.  Allowable values: Asymmetric, Cyclic, Dihedral, Helical, Icosahedral, Octahedral, Tetrahedral """
		self._enter('type', Query)
		return self

class RcsbStructSymmetryClusters(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbStructSymmetry':
		"""Return to parent (RcsbStructSymmetry)"""
		return self._parent if self._parent else self
	@property
	def avg_rmsd(self) -> 'RcsbStructSymmetryClusters':
		"""Average RMSD between members of a given cluster."""
		self._enter('avg_rmsd', Query)
		return self
	@property
	def members(self) -> 'ClustersMembers':
		"""Subunits that belong to the cluster, identified by asym_id and optionally by assembly operator id(s)."""
		return self._enter('members', ClustersMembers)

class RcsbStructSymmetryLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreAssembly':
		"""Return to parent (CoreAssembly)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbStructSymmetryLineage':
		"""Hierarchy depth."""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbStructSymmetryLineage':
		"""Automatically assigned ID to uniquely identify the symmetry term in the Protein Symmetry Browser.  Examples: Global Symmetry.Cyclic.C2.Homo 2-mer """
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbStructSymmetryLineage':
		"""A human-readable term describing protein symmetry.  Examples: Asymmetric, Global Symmetry, C1, Hetero 3-mer """
		self._enter('name', Query)
		return self

class RcsbStructSymmetryRotationAxes(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbStructSymmetry':
		"""Return to parent (RcsbStructSymmetry)"""
		return self._parent if self._parent else self
	@property
	def end(self) -> 'RcsbStructSymmetryRotationAxes':
		"""coordinate"""
		self._enter('end', Query)
		return self
	@property
	def order(self) -> 'RcsbStructSymmetryRotationAxes':
		"""The number of times (order of rotation) that a subunit can be repeated by a rotation operation,  being transformed into a new state indistinguishable from its starting state."""
		self._enter('order', Query)
		return self
	@property
	def start(self) -> 'RcsbStructSymmetryRotationAxes':
		"""coordinate"""
		self._enter('start', Query)
		return self

class RcsbTargetCofactors(QueryNode):
	""""""
	@property
	def end(self) -> 'CorePolymerEntity':
		"""Return to parent (CorePolymerEntity)"""
		return self._parent if self._parent else self
	@property
	def binding_assay_value(self) -> 'RcsbTargetCofactors':
		"""The value measured or determined by the assay.  Examples: null """
		self._enter('binding_assay_value', Query)
		return self
	@property
	def binding_assay_value_type(self) -> 'RcsbTargetCofactors':
		"""The type of measurement or value determined by the assay.  Allowable values: pAC50, pEC50, pIC50, pKd, pKi """
		self._enter('binding_assay_value_type', Query)
		return self
	@property
	def cofactor_InChIKey(self) -> 'RcsbTargetCofactors':
		"""Standard IUPAC International Chemical Identifier (InChI) descriptor key  for the cofactor.   InChI, the IUPAC International Chemical Identifier,  by Stephen R Heller, Alan McNaught, Igor Pletnev, Stephen Stein and Dmitrii Tchekhovskoi,  Journal of Cheminformatics, 2015, 7:23  Examples: BNOCDEBUFVJMQI-REOHCLBHSA-N """
		self._enter('cofactor_InChIKey', Query)
		return self
	@property
	def cofactor_SMILES(self) -> 'RcsbTargetCofactors':
		"""Simplified molecular-input line-entry system (SMILES) descriptor for the cofactor.     Weininger D (February 1988). 'SMILES, a chemical language and information system. 1.    Introduction to methodology and encoding rules'. Journal of Chemical Information and Modeling. 28 (1): 31-6.     Weininger D, Weininger A, Weininger JL (May 1989).    'SMILES. 2. Algorithm for generation of unique SMILES notation',    Journal of Chemical Information and Modeling. 29 (2): 97-101.  Examples: OC(=O)[CH](CF)O[P](O)(O)=O """
		self._enter('cofactor_SMILES', Query)
		return self
	@property
	def cofactor_chem_comp_id(self) -> 'RcsbTargetCofactors':
		"""The chemical component definition identifier for the cofactor.  Examples: 0Z3, CD9 """
		self._enter('cofactor_chem_comp_id', Query)
		return self
	@property
	def cofactor_description(self) -> 'RcsbTargetCofactors':
		"""The cofactor description.  Examples: A synthetic naphthoquinone without the isoprenoid side chain and biological activity,   but can be converted to active vitamin K2, menaquinone, after alkylation in vivo. """
		self._enter('cofactor_description', Query)
		return self
	@property
	def cofactor_name(self) -> 'RcsbTargetCofactors':
		"""The cofactor name.  Examples: Menadione """
		self._enter('cofactor_name', Query)
		return self
	@property
	def cofactor_prd_id(self) -> 'RcsbTargetCofactors':
		"""The BIRD definition identifier for the cofactor.  Examples: PRD_000010 """
		self._enter('cofactor_prd_id', Query)
		return self
	@property
	def cofactor_resource_id(self) -> 'RcsbTargetCofactors':
		"""Identifier for the cofactor assigned by the resource.  Examples: CHEMBL1987, DB00170 """
		self._enter('cofactor_resource_id', Query)
		return self
	@property
	def mechanism_of_action(self) -> 'RcsbTargetCofactors':
		"""Mechanism of action describes the biochemical interaction through which the  cofactor produces a pharmacological effect.  Examples: Menadione (vitamin K3) is involved as a cofactor in the posttranslational gamma-carboxylation of glutamic acid residues of certain proteins i n the body. These proteins include the vitamin K-dependent coagulation factors II (prothrombin), VII (proconvertin), IX (Christmas factor), X (Stuart factor), protein C, protein S, protein Zv and a growth-arrest-specific factor (Gas6). """
		self._enter('mechanism_of_action', Query)
		return self
	@property
	def neighbor_flag(self) -> 'RcsbTargetCofactors':
		"""A flag to indicate the cofactor is a structural neighbor of this  entity.  Allowable values: N, Y """
		self._enter('neighbor_flag', Query)
		return self
	@property
	def patent_nos(self) -> 'RcsbTargetCofactors':
		"""Patent numbers reporting the pharmacology or activity data."""
		self._enter('patent_nos', Query)
		return self
	@property
	def pubmed_ids(self) -> 'RcsbTargetCofactors':
		"""PubMed identifiers for literature supporting the pharmacology or activity data."""
		self._enter('pubmed_ids', Query)
		return self
	@property
	def resource_name(self) -> 'RcsbTargetCofactors':
		"""Resource providing target and cofactor data.  Allowable values: ChEMBL, DrugBank, Pharos """
		self._enter('resource_name', Query)
		return self
	@property
	def resource_version(self) -> 'RcsbTargetCofactors':
		"""Version of the information distributed by the data resource.  Examples: V4_0_2 """
		self._enter('resource_version', Query)
		return self
	@property
	def target_resource_id(self) -> 'RcsbTargetCofactors':
		"""Identifier for the target assigned by the resource.  Examples: P00734, CHEMBL2242 """
		self._enter('target_resource_id', Query)
		return self

class RcsbTargetNeighbors(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreNonpolymerEntityInstance':
		"""Return to parent (CoreNonpolymerEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def alt_id(self) -> 'RcsbTargetNeighbors':
		"""Alternate conformer identifier for the non-polymer entity instance."""
		self._enter('alt_id', Query)
		return self
	@property
	def atom_id(self) -> 'RcsbTargetNeighbors':
		"""The atom identifier for the non-polymer entity instance.  Examples: O1, N1, C1 """
		self._enter('atom_id', Query)
		return self
	@property
	def comp_id(self) -> 'RcsbTargetNeighbors':
		"""Component identifier for the non-polymer entity instance."""
		self._enter('comp_id', Query)
		return self
	@property
	def distance(self) -> 'RcsbTargetNeighbors':
		"""Distance value for this target interaction."""
		self._enter('distance', Query)
		return self
	@property
	def target_asym_id(self) -> 'RcsbTargetNeighbors':
		"""The entity instance identifier for the target of interaction.  Examples: A, B """
		self._enter('target_asym_id', Query)
		return self
	@property
	def target_atom_id(self) -> 'RcsbTargetNeighbors':
		"""The atom identifier for the target of interaction.  Examples: OG, OE1, CD1 """
		self._enter('target_atom_id', Query)
		return self
	@property
	def target_auth_seq_id(self) -> 'RcsbTargetNeighbors':
		"""The author residue index for the target of interaction."""
		self._enter('target_auth_seq_id', Query)
		return self
	@property
	def target_comp_id(self) -> 'RcsbTargetNeighbors':
		"""The chemical component identifier for the target of interaction.  Examples: ASN, TRP, SER """
		self._enter('target_comp_id', Query)
		return self
	@property
	def target_entity_id(self) -> 'RcsbTargetNeighbors':
		"""The entity identifier for the target of interaction.  Examples: 1, 2 """
		self._enter('target_entity_id', Query)
		return self
	@property
	def target_is_bound(self) -> 'RcsbTargetNeighbors':
		"""A flag to indicate the nature of the target interaction is covalent or metal-coordination.  Allowable values: N, Y """
		self._enter('target_is_bound', Query)
		return self
	@property
	def target_model_id(self) -> 'RcsbTargetNeighbors':
		"""Model identifier for the target of interaction."""
		self._enter('target_model_id', Query)
		return self
	@property
	def target_seq_id(self) -> 'RcsbTargetNeighbors':
		"""The sequence position for the target of interaction."""
		self._enter('target_seq_id', Query)
		return self

class RcsbUniprotAlignments(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def core_entity_alignments(self) -> 'RcsbUniprotAlignmentsCoreEntityAlignments':
		"""List of alignments with core_entity canonical sequences"""
		return self._enter('core_entity_alignments', RcsbUniprotAlignmentsCoreEntityAlignments)

class RcsbUniprotAlignmentsCoreEntityAlignments(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotAlignments':
		"""Return to parent (RcsbUniprotAlignments)"""
		return self._parent if self._parent else self
	@property
	def aligned_regions(self) -> 'CoreEntityAlignmentsAlignedRegions':
		"""Aligned region"""
		return self._enter('aligned_regions', CoreEntityAlignmentsAlignedRegions)
	@property
	def core_entity_identifiers(self) -> 'CoreEntityAlignmentsCoreEntityIdentifiers':
		"""core_entity identifiers"""
		return self._enter('core_entity_identifiers', CoreEntityAlignmentsCoreEntityIdentifiers)
	@property
	def scores(self) -> 'CoreEntityAlignmentsScores':
		"""Alignment scores"""
		return self._enter('scores', CoreEntityAlignmentsScores)

class RcsbUniprotAnnotation(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def additional_properties(self) -> 'RcsbUniprotAnnotationAdditionalProperties':
		""""""
		return self._enter('additional_properties', RcsbUniprotAnnotationAdditionalProperties)
	@property
	def annotation_id(self) -> 'RcsbUniprotAnnotation':
		"""An identifier for the annotation."""
		self._enter('annotation_id', Query)
		return self
	@property
	def annotation_lineage(self) -> 'RcsbUniprotAnnotationAnnotationLineage':
		""""""
		return self._enter('annotation_lineage', RcsbUniprotAnnotationAnnotationLineage)
	@property
	def assignment_version(self) -> 'RcsbUniprotAnnotation':
		"""Identifies the version of the annotation assignment."""
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbUniprotAnnotation':
		"""A description for the annotation."""
		self._enter('description', Query)
		return self
	@property
	def name(self) -> 'RcsbUniprotAnnotation':
		"""A name for the annotation."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbUniprotAnnotation':
		"""Code identifying the individual, organization or program that  assigned the annotation."""
		self._enter('provenance_source', Query)
		return self
	@property
	def type(self) -> 'RcsbUniprotAnnotation':
		"""A type or category of the annotation.  Allowable values: disease, phenotype, GO, InterPro """
		self._enter('type', Query)
		return self

class RcsbUniprotAnnotationAdditionalProperties(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotAnnotation':
		"""Return to parent (RcsbUniprotAnnotation)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'RcsbUniprotAnnotationAdditionalProperties':
		"""The additional property name  Allowable values: INTERPRO_TYPE """
		self._enter('name', Query)
		return self
	@property
	def values(self) -> 'RcsbUniprotAnnotationAdditionalProperties':
		"""The value(s) of the additional property"""
		self._enter('values', Query)
		return self

class RcsbUniprotAnnotationAnnotationLineage(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotAnnotation':
		"""Return to parent (RcsbUniprotAnnotation)"""
		return self._parent if self._parent else self
	@property
	def depth(self) -> 'RcsbUniprotAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent lineage depth (1-N)"""
		self._enter('depth', Query)
		return self
	@property
	def id(self) -> 'RcsbUniprotAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class identifiers."""
		self._enter('id', Query)
		return self
	@property
	def name(self) -> 'RcsbUniprotAnnotationAnnotationLineage':
		"""Members of the annotation lineage as parent class names."""
		self._enter('name', Query)
		return self

class RcsbUniprotContainerIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def reference_sequence_identifiers(self) -> 'RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers':
		""""""
		return self._enter('reference_sequence_identifiers', RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers)
	@property
	def uniprot_id(self) -> 'RcsbUniprotContainerIdentifiers':
		"""Primary accession number of a given UniProtKB entry."""
		self._enter('uniprot_id', Query)
		return self

class RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotContainerIdentifiers':
		"""Return to parent (RcsbUniprotContainerIdentifiers)"""
		return self._parent if self._parent else self
	@property
	def database_accession(self) -> 'RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers':
		"""Reference database accession code"""
		self._enter('database_accession', Query)
		return self
	@property
	def database_isoform(self) -> 'RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers':
		"""Reference database identifier for the sequence isoform"""
		self._enter('database_isoform', Query)
		return self
	@property
	def database_name(self) -> 'RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers':
		"""Reference database name"""
		self._enter('database_name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbUniprotContainerIdentifiersReferenceSequenceIdentifiers':
		"""Source of the reference database assignment"""
		self._enter('provenance_source', Query)
		return self

class RcsbUniprotExternalReference(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def provenance_source(self) -> 'RcsbUniprotExternalReference':
		""""""
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_id(self) -> 'RcsbUniprotExternalReference':
		""""""
		self._enter('reference_id', Query)
		return self
	@property
	def reference_name(self) -> 'RcsbUniprotExternalReference':
		"""Allowable values: IMPC, GTEX, PHAROS."""
		self._enter('reference_name', Query)
		return self

class RcsbUniprotFeature(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def assignment_version(self) -> 'RcsbUniprotFeature':
		"""Identifies the version of the feature assignment."""
		self._enter('assignment_version', Query)
		return self
	@property
	def description(self) -> 'RcsbUniprotFeature':
		"""A description for the feature."""
		self._enter('description', Query)
		return self
	@property
	def feature_id(self) -> 'RcsbUniprotFeature':
		"""An identifier for the feature."""
		self._enter('feature_id', Query)
		return self
	@property
	def feature_positions(self) -> 'RcsbUniprotFeatureFeaturePositions':
		""""""
		return self._enter('feature_positions', RcsbUniprotFeatureFeaturePositions)
	@property
	def name(self) -> 'RcsbUniprotFeature':
		"""A name for the feature."""
		self._enter('name', Query)
		return self
	@property
	def provenance_source(self) -> 'RcsbUniprotFeature':
		"""Code identifying the individual, organization or program that  assigned the feature."""
		self._enter('provenance_source', Query)
		return self
	@property
	def reference_scheme(self) -> 'RcsbUniprotFeature':
		"""Code residue coordinate system for the assigned feature."""
		self._enter('reference_scheme', Query)
		return self
	@property
	def type(self) -> 'RcsbUniprotFeature':
		"""A type or category of the feature.  Allowable values: ACTIVE_SITE, BINDING_SITE, CALCIUM_BINDING_REGION, CHAIN, COMPOSITIONALLY_BIASED_REGION, CROSS_LINK, DNA_BINDING_REGION, DOMAIN, GLYCOSYLATION_SITE, INITIATOR_METHIONINE, LIPID_MOIETY_BINDING_REGION, METAL_ION_BINDING_SITE, MODIFIED_RESIDUE, MUTAGENESIS_SITE, NON_CONSECUTIVE_RESIDUES, NON_TERMINAL_RESIDUE, NUCLEOTIDE_PHOSPHATE_BINDING_REGION, PEPTIDE, PROPEPTIDE, REGION_OF_INTEREST, REPEAT, NON_STANDARD_AMINO_ACID, SEQUENCE_CONFLICT, SEQUENCE_VARIANT, SHORT_SEQUENCE_MOTIF, SIGNAL_PEPTIDE, SITE, SPLICE_VARIANT, TOPOLOGICAL_DOMAIN, TRANSIT_PEPTIDE, TRANSMEMBRANE_REGION, UNSURE_RESIDUE, ZINC_FINGER_REGION, INTRAMEMBRANE_REGION """
		self._enter('type', Query)
		return self

class RcsbUniprotFeatureFeaturePositions(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotFeature':
		"""Return to parent (RcsbUniprotFeature)"""
		return self._parent if self._parent else self
	@property
	def beg_comp_id(self) -> 'RcsbUniprotFeatureFeaturePositions':
		"""An identifier for the monomer(s) corresponding to the feature assignment."""
		self._enter('beg_comp_id', Query)
		return self
	@property
	def beg_seq_id(self) -> 'RcsbUniprotFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature begins."""
		self._enter('beg_seq_id', Query)
		return self
	@property
	def end_seq_id(self) -> 'RcsbUniprotFeatureFeaturePositions':
		"""An identifier for the monomer at which this segment of the feature ends."""
		self._enter('end_seq_id', Query)
		return self
	@property
	def value(self) -> 'RcsbUniprotFeatureFeaturePositions':
		"""The value for the feature over this monomer segment."""
		self._enter('value', Query)
		return self
	@property
	def values(self) -> 'RcsbUniprotFeatureFeaturePositions':
		"""The value(s) for the feature over this monomer segment."""
		self._enter('values', Query)
		return self

class RcsbUniprotKeyword(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def id(self) -> 'RcsbUniprotKeyword':
		"""A unique keyword identifier.  Examples: KW-0275, KW-0597 """
		self._enter('id', Query)
		return self
	@property
	def value(self) -> 'RcsbUniprotKeyword':
		"""Human-readable keyword term.  Examples: Lipid metabolism, Phosphoprotein, Fatty acid biosynthesis """
		self._enter('value', Query)
		return self

class RcsbUniprotProtein(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreUniprot':
		"""Return to parent (CoreUniprot)"""
		return self._parent if self._parent else self
	@property
	def ec(self) -> 'RcsbUniprotProteinEc':
		"""Enzyme Commission (EC) number(s)."""
		return self._enter('ec', RcsbUniprotProteinEc)
	@property
	def function(self) -> 'RcsbUniprotProteinFunction':
		""""""
		return self._enter('function', RcsbUniprotProteinFunction)
	@property
	def gene(self) -> 'RcsbUniprotProteinGene':
		"""The name(s) of the gene(s) that code for the protein sequence(s) described in the entry."""
		return self._enter('gene', RcsbUniprotProteinGene)
	@property
	def name(self) -> 'RcsbUniprotProteinName':
		""""""
		return self._enter('name', RcsbUniprotProteinName)
	@property
	def sequence(self) -> 'RcsbUniprotProtein':
		"""Protein sequence data for canonical protein sequence."""
		self._enter('sequence', Query)
		return self
	@property
	def source_organism(self) -> 'RcsbUniprotProteinSourceOrganism':
		"""Taxonomy information on the organism that is the source of the protein sequence."""
		return self._enter('source_organism', RcsbUniprotProteinSourceOrganism)

class RcsbUniprotProteinEc(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotProtein':
		"""Return to parent (RcsbUniprotProtein)"""
		return self._parent if self._parent else self
	@property
	def number(self) -> 'RcsbUniprotProteinEc':
		""""""
		self._enter('number', Query)
		return self
	@property
	def provenance_code(self) -> 'RcsbUniprotProteinEc':
		"""Historical record of the data attribute."""
		self._enter('provenance_code', Query)
		return self

class RcsbUniprotProteinFunction(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotProtein':
		"""Return to parent (RcsbUniprotProtein)"""
		return self._parent if self._parent else self
	@property
	def details(self) -> 'RcsbUniprotProteinFunction':
		"""General function(s) of a protein."""
		self._enter('details', Query)
		return self
	@property
	def provenance_code(self) -> 'RcsbUniprotProteinFunction':
		"""Historical record of the data attribute."""
		self._enter('provenance_code', Query)
		return self

class RcsbUniprotProteinGene(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotProtein':
		"""Return to parent (RcsbUniprotProtein)"""
		return self._parent if self._parent else self
	@property
	def name(self) -> 'GeneName':
		""""""
		return self._enter('name', GeneName)

class RcsbUniprotProteinName(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotProtein':
		"""Return to parent (RcsbUniprotProtein)"""
		return self._parent if self._parent else self
	@property
	def provenance_code(self) -> 'RcsbUniprotProteinName':
		"""Historical record of the data attribute."""
		self._enter('provenance_code', Query)
		return self
	@property
	def value(self) -> 'RcsbUniprotProteinName':
		"""Name that allows to unambiguously identify a protein.  Examples: Hemoglobin alpha """
		self._enter('value', Query)
		return self

class RcsbUniprotProteinSourceOrganism(QueryNode):
	""""""
	@property
	def end(self) -> 'RcsbUniprotProtein':
		"""Return to parent (RcsbUniprotProtein)"""
		return self._parent if self._parent else self
	@property
	def provenance_code(self) -> 'RcsbUniprotProteinSourceOrganism':
		"""Historical record of the data attribute."""
		self._enter('provenance_code', Query)
		return self
	@property
	def scientific_name(self) -> 'RcsbUniprotProteinSourceOrganism':
		"""The scientific name of the organism in which a protein occurs."""
		self._enter('scientific_name', Query)
		return self
	@property
	def taxonomy_id(self) -> 'RcsbUniprotProteinSourceOrganism':
		"""NCBI Taxonomy identifier for the organism in which a protein occurs."""
		self._enter('taxonomy_id', Query)
		return self

class Refine(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def B_iso_max(self) -> 'Refine':
		"""The maximum isotropic displacement parameter (B value)  found in the coordinate set."""
		self._enter('B_iso_max', Query)
		return self
	@property
	def B_iso_mean(self) -> 'Refine':
		"""The mean isotropic displacement parameter (B value)  for the coordinate set."""
		self._enter('B_iso_mean', Query)
		return self
	@property
	def B_iso_min(self) -> 'Refine':
		"""The minimum isotropic displacement parameter (B value)  found in the coordinate set."""
		self._enter('B_iso_min', Query)
		return self
	@property
	def aniso_B_1_1(self) -> 'Refine':
		"""The [1][1] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
		self._enter('aniso_B_1_1', Query)
		return self
	@property
	def aniso_B_1_2(self) -> 'Refine':
		"""The [1][2] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
		self._enter('aniso_B_1_2', Query)
		return self
	@property
	def aniso_B_1_3(self) -> 'Refine':
		"""The [1][3] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
		self._enter('aniso_B_1_3', Query)
		return self
	@property
	def aniso_B_2_2(self) -> 'Refine':
		"""The [2][2] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
		self._enter('aniso_B_2_2', Query)
		return self
	@property
	def aniso_B_2_3(self) -> 'Refine':
		"""The [2][3] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
		self._enter('aniso_B_2_3', Query)
		return self
	@property
	def aniso_B_3_3(self) -> 'Refine':
		"""The [3][3] element of the matrix that defines the overall  anisotropic displacement model if one was refined for this  structure."""
		self._enter('aniso_B_3_3', Query)
		return self
	@property
	def correlation_coeff_Fo_to_Fc(self) -> 'Refine':
		"""The correlation coefficient between the observed and              calculated structure factors for reflections included in              the refinement.               The correlation coefficient is scale-independent and gives              an idea of the quality of the refined model.                            sum~i~(Fo~i~ Fc~i~ - <Fo><Fc>) R~corr~ = ------------------------------------------------------------           SQRT{sum~i~(Fo~i~)^2^-<Fo>^2^} SQRT{sum~i~(Fc~i~)^2^-<Fc>^2^}               Fo = observed structure factors              Fc = calculated structure factors              <>   denotes average value               summation is over reflections included in the refinement"""
		self._enter('correlation_coeff_Fo_to_Fc', Query)
		return self
	@property
	def correlation_coeff_Fo_to_Fc_free(self) -> 'Refine':
		"""The correlation coefficient between the observed and              calculated structure factors for reflections not included              in the refinement (free reflections).                The correlation coefficient is scale-independent and gives               an idea of the quality of the refined model.                            sum~i~(Fo~i~ Fc~i~ - <Fo><Fc>) R~corr~ = ------------------------------------------------------------           SQRT{sum~i~(Fo~i~)^2^-<Fo>^2^} SQRT{sum~i~(Fc~i~)^2^-<Fc>^2^}                Fo  = observed structure factors               Fc  = calculated structure factors               <>    denotes average value                summation is over reflections not included               in the refinement (free reflections)"""
		self._enter('correlation_coeff_Fo_to_Fc_free', Query)
		return self
	@property
	def details(self) -> 'Refine':
		"""Description of special aspects of the refinement process.  Examples: HYDROGENS HAVE BEEN ADDED IN THE RIDING POSITIONS """
		self._enter('details', Query)
		return self
	@property
	def ls_R_factor_R_free(self) -> 'Refine':
		"""Residual factor R for reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
		self._enter('ls_R_factor_R_free', Query)
		return self
	@property
	def ls_R_factor_R_free_error(self) -> 'Refine':
		"""The estimated error in _refine.ls_R_factor_R_free.  The method used to estimate the error is described in the  item _refine.ls_R_factor_R_free_error_details."""
		self._enter('ls_R_factor_R_free_error', Query)
		return self
	@property
	def ls_R_factor_R_free_error_details(self) -> 'Refine':
		"""Special aspects of the method used to estimated the error in  _refine.ls_R_factor_R_free."""
		self._enter('ls_R_factor_R_free_error_details', Query)
		return self
	@property
	def ls_R_factor_R_work(self) -> 'Refine':
		"""Residual factor R for reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the working  reflections (i.e. were included in the refinement)  when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.   _refine.ls_R_factor_obs should not be confused with  _refine.ls_R_factor_R_work; the former reports the results of a  refinement in which all observed reflections were used, the  latter a refinement in which a subset of the observed  reflections were excluded from refinement for the calculation  of a 'free' R factor. However, it would be meaningful to quote  both values if a 'free' R factor were calculated for most of  the refinement, but all of the observed reflections were used  in the final rounds of refinement; such a protocol should be  explained in _refine.details.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
		self._enter('ls_R_factor_R_work', Query)
		return self
	@property
	def ls_R_factor_all(self) -> 'Refine':
		"""Residual factor R for all reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
		self._enter('ls_R_factor_all', Query)
		return self
	@property
	def ls_R_factor_obs(self) -> 'Refine':
		"""Residual factor R for reflections that satisfy the resolution  limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion.   _refine.ls_R_factor_obs should not be confused with  _refine.ls_R_factor_R_work; the former reports the results of a  refinement in which all observed reflections were used, the  latter a refinement in which a subset of the observed  reflections were excluded from refinement for the calculation  of a 'free' R factor. However, it would be meaningful to quote  both values if a 'free' R factor were calculated for most of  the refinement, but all of the observed reflections were used  in the final rounds of refinement; such a protocol should be  explained in _refine.details.       sum|F~obs~ - F~calc~|  R = ---------------------           sum|F~obs~|   F~obs~  = the observed structure-factor amplitudes  F~calc~ = the calculated structure-factor amplitudes   sum is taken over the specified reflections"""
		self._enter('ls_R_factor_obs', Query)
		return self
	@property
	def ls_d_res_high(self) -> 'Refine':
		"""The smallest value for the interplanar spacings for the  reflection data used in the refinement in angstroms. This is  called the highest resolution."""
		self._enter('ls_d_res_high', Query)
		return self
	@property
	def ls_d_res_low(self) -> 'Refine':
		"""The largest value for the interplanar spacings for  the reflection data used in the refinement in angstroms.  This is called the lowest resolution."""
		self._enter('ls_d_res_low', Query)
		return self
	@property
	def ls_matrix_type(self) -> 'Refine':
		"""Type of matrix used to accumulate the least-squares derivatives.  Allowable values: atomblock, diagonal, full, fullcycle, sparse, userblock """
		self._enter('ls_matrix_type', Query)
		return self
	@property
	def ls_number_parameters(self) -> 'Refine':
		"""The number of parameters refined in the least-squares process.  If possible, this number should include some contribution from  the restrained parameters. The restrained parameters are  distinct from the constrained parameters (where one or more  parameters are linearly dependent on the refined value of  another). Least-squares restraints often depend on geometry or  energy considerations and this makes their direct contribution  to this number, and to the goodness-of-fit calculation,  difficult to assess."""
		self._enter('ls_number_parameters', Query)
		return self
	@property
	def ls_number_reflns_R_free(self) -> 'Refine':
		"""The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details."""
		self._enter('ls_number_reflns_R_free', Query)
		return self
	@property
	def ls_number_reflns_R_work(self) -> 'Refine':
		"""The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, and that were used as the working  reflections (i.e. were included in the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details."""
		self._enter('ls_number_reflns_R_work', Query)
		return self
	@property
	def ls_number_reflns_all(self) -> 'Refine':
		"""The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low."""
		self._enter('ls_number_reflns_all', Query)
		return self
	@property
	def ls_number_reflns_obs(self) -> 'Refine':
		"""The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion."""
		self._enter('ls_number_reflns_obs', Query)
		return self
	@property
	def ls_number_restraints(self) -> 'Refine':
		"""The number of restrained parameters. These are parameters which  are not directly dependent on another refined parameter.  Restrained parameters often involve geometry or energy  dependencies.  See also _atom_site.constraints and _atom_site.refinement_flags.  A general description of refinement constraints may appear in  _refine.details."""
		self._enter('ls_number_restraints', Query)
		return self
	@property
	def ls_percent_reflns_R_free(self) -> 'Refine':
		"""The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor,  expressed as a percentage of the number of geometrically  observable reflections that satisfy the resolution limits."""
		self._enter('ls_percent_reflns_R_free', Query)
		return self
	@property
	def ls_percent_reflns_obs(self) -> 'Refine':
		"""The number of reflections that satisfy the resolution limits  established by _refine.ls_d_res_high and _refine.ls_d_res_low  and the observation limit established by  _reflns.observed_criterion, expressed as a percentage of the  number of geometrically observable reflections that satisfy  the resolution limits."""
		self._enter('ls_percent_reflns_obs', Query)
		return self
	@property
	def ls_redundancy_reflns_all(self) -> 'Refine':
		"""The ratio of the total number of observations of the  reflections that satisfy the resolution limits established by  _refine.ls_d_res_high and _refine.ls_d_res_low to the number  of crystallographically unique reflections that satisfy the  same limits."""
		self._enter('ls_redundancy_reflns_all', Query)
		return self
	@property
	def ls_redundancy_reflns_obs(self) -> 'Refine':
		"""The ratio of the total number of observations of the  reflections that satisfy the resolution limits established by  _refine.ls_d_res_high and _refine.ls_d_res_low and the  observation limit established by _reflns.observed_criterion to  the number of crystallographically unique reflections that  satisfy the same limits."""
		self._enter('ls_redundancy_reflns_obs', Query)
		return self
	@property
	def ls_wR_factor_R_free(self) -> 'Refine':
		"""Weighted residual factor wR for reflections that satisfy the  resolution limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the test  reflections (i.e. were excluded from the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.        ( sum|w |Y~obs~ - Y~calc~|^2^| )^1/2^  wR = ( ---------------------------- )       (        sum|w Y~obs~^2^|      )   Y~obs~  = the observed amplitude specified by            _refine.ls_structure_factor_coef  Y~calc~ = the calculated amplitude specified by            _refine.ls_structure_factor_coef  w       = the least-squares weight   sum is taken over the specified reflections"""
		self._enter('ls_wR_factor_R_free', Query)
		return self
	@property
	def ls_wR_factor_R_work(self) -> 'Refine':
		"""Weighted residual factor wR for reflections that satisfy the  resolution limits established by _refine.ls_d_res_high and  _refine.ls_d_res_low and the observation limit established by  _reflns.observed_criterion, and that were used as the working  reflections (i.e. were included in the refinement) when the  refinement included the calculation of a 'free' R factor.  Details of how reflections were assigned to the working and  test sets are given in _reflns.R_free_details.        ( sum|w |Y~obs~ - Y~calc~|^2^| )^1/2^  wR = ( ---------------------------- )       (        sum|w Y~obs~^2^|      )   Y~obs~  = the observed amplitude specified by            _refine.ls_structure_factor_coef  Y~calc~ = the calculated amplitude specified by            _refine.ls_structure_factor_coef  w       = the least-squares weight   sum is taken over the specified reflections"""
		self._enter('ls_wR_factor_R_work', Query)
		return self
	@property
	def occupancy_max(self) -> 'Refine':
		"""The maximum value for occupancy found in the coordinate set."""
		self._enter('occupancy_max', Query)
		return self
	@property
	def occupancy_min(self) -> 'Refine':
		"""The minimum value for occupancy found in the coordinate set."""
		self._enter('occupancy_min', Query)
		return self
	@property
	def overall_FOM_free_R_set(self) -> 'Refine':
		"""Average figure of merit of phases of reflections not included  in the refinement.   This value is derived from the likelihood function.   FOM           = I~1~(X)/I~0~(X)   I~0~, I~1~     = zero- and first-order modified Bessel functions                  of the first kind  X              = sigma~A~ |E~o~| |E~c~|/SIGMA  E~o~, E~c~     = normalized observed and calculated structure                  factors  sigma~A~       = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                  estimated using maximum likelihood  Sigma~P~       = sum~{atoms in model}~ f^2^  Sigma~N~       = sum~{atoms in crystal}~ f^2^  f              = form factor of atoms  delta~x~       = expected error  SIGMA          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]  sigma~{E;exp}~ = uncertainties of normalized observed                  structure factors  epsilon       = multiplicity of the diffracting plane   Ref: Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).       Acta Cryst. D53, 240-255."""
		self._enter('overall_FOM_free_R_set', Query)
		return self
	@property
	def overall_FOM_work_R_set(self) -> 'Refine':
		"""Average figure of merit of phases of reflections included in  the refinement.   This value is derived from the likelihood function.   FOM           = I~1~(X)/I~0~(X)   I~0~, I~1~     = zero- and first-order modified Bessel functions                  of the first kind  X              = sigma~A~ |E~o~| |E~c~|/SIGMA  E~o~, E~c~     = normalized observed and calculated structure                  factors  sigma~A~       = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                  estimated using maximum likelihood  Sigma~P~       = sum~{atoms in model}~ f^2^  Sigma~N~       = sum~{atoms in crystal}~ f^2^  f              = form factor of atoms  delta~x~       = expected error  SIGMA          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]  sigma~{E;exp}~ = uncertainties of normalized observed                  structure factors  epsilon       = multiplicity of the diffracting plane   Ref: Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).       Acta Cryst. D53, 240-255."""
		self._enter('overall_FOM_work_R_set', Query)
		return self
	@property
	def overall_SU_B(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)            of the displacement parameters based on a maximum-likelihood            residual.             The overall standard uncertainty (sigma~B~)^2^ gives an idea            of the uncertainty in the B values of averagely defined            atoms (atoms with B values equal to the average B value).                                           N~a~ (sigma~B~)^2^ = 8 ----------------------------------------------                   sum~i~ {[1/Sigma - (E~o~)^2^ (1-m^2^)](SUM_AS)s^4^}             N~a~           = number of atoms            E~o~           = normalized structure factors            m              = figure of merit of phases of reflections                             included in the summation            s              = reciprocal-space vector             SUM_AS         = (sigma~A~)^2^/Sigma^2^            Sigma          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]            sigma~{E;exp}~  = experimental uncertainties of normalized                             structure factors            sigma~A~        = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                             estimated using maximum likelihood            Sigma~P~        = sum~{atoms in model}~ f^2^            Sigma~N~        = sum~{atoms in crystal}~ f^2^            f               = atom form factor            delta~x~        = expected error            epsilon         = multiplicity of diffracting plane             summation is over all reflections included in refinement             Ref: (sigma~A~ estimation) 'Refinement of macromolecular                 structures by the maximum-likelihood method',                 Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).                 Acta Cryst. D53, 240-255.                  (SU B estimation) Murshudov, G. N. & Dodson,                 E. J. (1997). Simplified error estimation a la                 Cruickshank in macromolecular crystallography.                 CCP4 Newsletter on Protein Crystallography, No. 33,                 January 1997, pp. 31-39.                 http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
		self._enter('overall_SU_B', Query)
		return self
	@property
	def overall_SU_ML(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)            of the positional parameters based on a maximum likelihood            residual.             The overall standard uncertainty (sigma~X~)^2^ gives an            idea of the uncertainty in the position of averagely            defined atoms (atoms with B values equal to average B value)                   3                         N~a~ (sigma~X~)^2^  = ---------------------------------------------------------                  8 pi^2^ sum~i~ {[1/Sigma - (E~o~)^2^ (1-m^2^)](SUM_AS)s^2^}             N~a~           = number of atoms            E~o~           = normalized structure factors            m              = figure of merit of phases of reflections                             included in the summation            s              = reciprocal-space vector             SUM_AS         = (sigma~A~)^2^/Sigma^2^            Sigma          = (sigma~{E;exp}~)^2^ + epsilon [1-(sigma~A~)^2^]            sigma~{E;exp}~  = experimental uncertainties of normalized                             structure factors            sigma~A~        = <cos 2 pi s delta~x~> SQRT(Sigma~P~/Sigma~N~)                             estimated using maximum likelihood            Sigma~P~        = sum~{atoms in model}~ f^2^            Sigma~N~        = sum~{atoms in crystal}~ f^2^            f               = atom form factor            delta~x~        = expected error            epsilon         = multiplicity of diffracting plane             summation is over all reflections included in refinement             Ref: (sigma_A estimation) 'Refinement of macromolecular                 structures by the maximum-likelihood method',                 Murshudov, G. N., Vagin, A. A. & Dodson, E. J. (1997).                 Acta Cryst. D53, 240-255.                  (SU ML estimation) Murshudov, G. N. & Dodson,                 E. J. (1997). Simplified error estimation a la                 Cruickshank in macromolecular crystallography.                 CCP4 Newsletter on Protein Crystallography, No. 33,                 January 1997, pp. 31-39.                 http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
		self._enter('overall_SU_ML', Query)
		return self
	@property
	def overall_SU_R_Cruickshank_DPI(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R value, expressed in a formalism known as the dispersion  precision indicator (DPI).   The overall standard uncertainty (sigma~B~) gives an idea  of the uncertainty in the B values of averagely defined  atoms (atoms with B values equal to the average B value).                          N~a~  (sigma~B~)^2^ = 0.65 ---------- (R~value~)^2^ (D~min~)^2^ C^-2/3^                       (N~o~-N~p~)    N~a~     = number of atoms included in refinement  N~o~     = number of observations  N~p~     = number of parameters refined  R~value~ = conventional crystallographic R value  D~min~   = maximum resolution  C        = completeness of data   Ref: Cruickshank, D. W. J. (1999). Acta Cryst. D55, 583-601.        Murshudov, G. N. & Dodson,       E. J. (1997). Simplified error estimation a la       Cruickshank in macromolecular crystallography.       CCP4 Newsletter on Protein Crystallography, No. 33,       January 1997, pp. 31-39.       http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
		self._enter('overall_SU_R_Cruickshank_DPI', Query)
		return self
	@property
	def overall_SU_R_free(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the free R value.   The overall standard uncertainty (sigma~B~) gives an idea  of the uncertainty in the B values of averagely defined  atoms (atoms with B values equal to the average B value).                          N~a~  (sigma~B~)^2^ = 0.65 ---------- (R~free~)^2^ (D~min~)^2^ C^-2/3^                       (N~o~-N~p~)    N~a~     = number of atoms included in refinement  N~o~     = number of observations  N~p~     = number of parameters refined  R~free~  = conventional free crystallographic R value calculated           using reflections not included in refinement  D~min~   = maximum resolution  C        = completeness of data   Ref: Cruickshank, D. W. J. (1999). Acta Cryst. D55, 583-601.        Murshudov, G. N. & Dodson,       E. J. (1997). Simplified error estimation a la       Cruickshank in macromolecular crystallography.       CCP4 Newsletter on Protein Crystallography, No. 33,       January 1997, pp. 31-39.       http://www.ccp4.ac.uk/newsletters/newsletter33/murshudov.html"""
		self._enter('overall_SU_R_free', Query)
		return self
	@property
	def pdbx_R_Free_selection_details(self) -> 'Refine':
		"""Details of the manner in which the cross validation  reflections were selected.  Examples: Random selection """
		self._enter('pdbx_R_Free_selection_details', Query)
		return self
	@property
	def pdbx_TLS_residual_ADP_flag(self) -> 'Refine':
		"""A flag for TLS refinements identifying the type of atomic displacement parameters stored  in _atom_site.B_iso_or_equiv.  Allowable values: LIKELY RESIDUAL, UNVERIFIED """
		self._enter('pdbx_TLS_residual_ADP_flag', Query)
		return self
	@property
	def pdbx_average_fsc_free(self) -> 'Refine':
		"""Average Fourier Shell Correlation (avgFSC) between model and  observed structure factors for reflections not included in refinement.   The average FSC is a measure of the agreement between observed  and calculated structure factors.                    sum(N~i~ FSC~free-i~)  avgFSC~free~   = ---------------------                   sum(N~i~)    N~i~          = the number of free reflections in the resolution shell i  FSC~free-i~   = FSC for free reflections in the i-th resolution shell calculated as:                  (sum(|F~o~| |F~c~| fom cos(phi~c~-phi~o~)))  FSC~free-i~  = -------------------------------------------                 (sum(|F~o~|^2^) (sum(|F~c~|^2^)))^1/2^   |F~o~|   = amplitude of observed structure factor  |F~c~|   = amplitude of calculated structure factor  phi~o~   = phase of observed structure factor  phi~c~   = phase of calculated structure factor  fom      = figure of merit of the experimental phases.   Summation of FSC~free-i~ is carried over all free reflections in the resolution shell.   Summation of avgFSC~free~ is carried over all resolution shells.    Ref:  Rosenthal P.B., Henderson R.        'Optimal determination of particle orientation, absolute hand,        and contrast loss in single-particle electron cryomicroscopy.        Journal of Molecular Biology. 2003;333(4):721-745, equation (A6)."""
		self._enter('pdbx_average_fsc_free', Query)
		return self
	@property
	def pdbx_average_fsc_overall(self) -> 'Refine':
		"""Overall average Fourier Shell Correlation (avgFSC) between model and  observed structure factors for all reflections.   The average FSC is a measure of the agreement between observed  and calculated structure factors.              sum(N~i~ FSC~i~)  avgFSC   = ----------------             sum(N~i~)    N~i~     = the number of all reflections in the resolution shell i  FSC~i~   = FSC for all reflections in the i-th resolution shell calculated as:             (sum(|F~o~| |F~c~| fom cos(phi~c~-phi~o~)))  FSC~i~  = -------------------------------------------            (sum(|F~o~|^2^) (sum(|F~c~|^2^)))^1/2^   |F~o~|   = amplitude of observed structure factor  |F~c~|   = amplitude of calculated structure factor  phi~o~   = phase of observed structure factor  phi~c~   = phase of calculated structure factor  fom      = figure of merit of the experimental phases.   Summation of FSC~i~ is carried over all reflections in the resolution shell.   Summation of avgFSC is carried over all resolution shells.    Ref:  Rosenthal P.B., Henderson R.        'Optimal determination of particle orientation, absolute hand,        and contrast loss in single-particle electron cryomicroscopy.        Journal of Molecular Biology. 2003;333(4):721-745, equation (A6)."""
		self._enter('pdbx_average_fsc_overall', Query)
		return self
	@property
	def pdbx_average_fsc_work(self) -> 'Refine':
		"""Average Fourier Shell Correlation (avgFSC) between model and  observed structure factors for reflections included in refinement.   The average FSC is a measure of the agreement between observed  and calculated structure factors.                    sum(N~i~ FSC~work-i~)  avgFSC~work~   = ---------------------                   sum(N~i~)    N~i~          = the number of working reflections in the resolution shell i  FSC~work-i~   = FSC for working reflections in the i-th resolution shell calculated as:                  (sum(|F~o~| |F~c~| fom cos(phi~c~-phi~o~)))  FSC~work-i~  = -------------------------------------------                 (sum(|F~o~|^2^) (sum(|F~c~|^2^)))^1/2^   |F~o~|   = amplitude of observed structure factor  |F~c~|   = amplitude of calculated structure factor  phi~o~   = phase of observed structure factor  phi~c~   = phase of calculated structure factor  fom      = figure of merit of the experimental phases.   Summation of FSC~work-i~ is carried over all working reflections in the resolution shell.   Summation of avgFSC~work~ is carried over all resolution shells.    Ref:  Rosenthal P.B., Henderson R.        'Optimal determination of particle orientation, absolute hand,        and contrast loss in single-particle electron cryomicroscopy.        Journal of Molecular Biology. 2003;333(4):721-745, equation (A6)."""
		self._enter('pdbx_average_fsc_work', Query)
		return self
	@property
	def pdbx_data_cutoff_high_absF(self) -> 'Refine':
		"""Value of F at 'high end' of data cutoff."""
		self._enter('pdbx_data_cutoff_high_absF', Query)
		return self
	@property
	def pdbx_data_cutoff_high_rms_absF(self) -> 'Refine':
		"""Value of RMS |F| used as high data cutoff.  Examples: null """
		self._enter('pdbx_data_cutoff_high_rms_absF', Query)
		return self
	@property
	def pdbx_data_cutoff_low_absF(self) -> 'Refine':
		"""Value of F at 'low end' of data cutoff.  Examples: null """
		self._enter('pdbx_data_cutoff_low_absF', Query)
		return self
	@property
	def pdbx_diffrn_id(self) -> 'Refine':
		"""An identifier for the diffraction data set used in this refinement.   Multiple diffraction data sets specified as a comma separated list."""
		self._enter('pdbx_diffrn_id', Query)
		return self
	@property
	def pdbx_isotropic_thermal_model(self) -> 'Refine':
		"""Whether the structure was refined with indvidual isotropic, anisotropic or overall temperature factor.  Examples: Isotropic, Overall """
		self._enter('pdbx_isotropic_thermal_model', Query)
		return self
	@property
	def pdbx_ls_cross_valid_method(self) -> 'Refine':
		"""Whether the cross validataion method was used through out or only at the end.  Examples: FREE R-VALUE """
		self._enter('pdbx_ls_cross_valid_method', Query)
		return self
	@property
	def pdbx_ls_sigma_F(self) -> 'Refine':
		"""Data cutoff (SIGMA(F))"""
		self._enter('pdbx_ls_sigma_F', Query)
		return self
	@property
	def pdbx_ls_sigma_Fsqd(self) -> 'Refine':
		"""Data cutoff (SIGMA(F^2))"""
		self._enter('pdbx_ls_sigma_Fsqd', Query)
		return self
	@property
	def pdbx_ls_sigma_I(self) -> 'Refine':
		"""Data cutoff (SIGMA(I))"""
		self._enter('pdbx_ls_sigma_I', Query)
		return self
	@property
	def pdbx_method_to_determine_struct(self) -> 'Refine':
		"""Method(s) used to determine the structure.  Examples: AB INITIO PHASING, DM, ISAS, ISIR, ISIRAS, MAD, MIR, MIRAS, MR, SIR, SIRAS """
		self._enter('pdbx_method_to_determine_struct', Query)
		return self
	@property
	def pdbx_overall_ESU_R(self) -> 'Refine':
		"""Overall estimated standard uncertainties of positional  parameters based on R value."""
		self._enter('pdbx_overall_ESU_R', Query)
		return self
	@property
	def pdbx_overall_ESU_R_Free(self) -> 'Refine':
		"""Overall estimated standard uncertainties of positional parameters based on R free value."""
		self._enter('pdbx_overall_ESU_R_Free', Query)
		return self
	@property
	def pdbx_overall_SU_R_Blow_DPI(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R value, expressed in a formalism known as the dispersion  precision indicator (DPI).   Ref: Blow, D (2002) Acta Cryst. D58, 792-797"""
		self._enter('pdbx_overall_SU_R_Blow_DPI', Query)
		return self
	@property
	def pdbx_overall_SU_R_free_Blow_DPI(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R-free value, expressed in a formalism known as the dispersion  precision indicator (DPI).   Ref: Blow, D (2002) Acta Cryst. D58, 792-797"""
		self._enter('pdbx_overall_SU_R_free_Blow_DPI', Query)
		return self
	@property
	def pdbx_overall_SU_R_free_Cruickshank_DPI(self) -> 'Refine':
		"""The overall standard uncertainty (estimated standard deviation)  of the displacement parameters based on the crystallographic  R-free value, expressed in a formalism known as the dispersion  precision indicator (DPI).   Ref: Cruickshank, D. W. J. (1999). Acta Cryst. D55, 583-601."""
		self._enter('pdbx_overall_SU_R_free_Cruickshank_DPI', Query)
		return self
	@property
	def pdbx_overall_phase_error(self) -> 'Refine':
		"""The overall phase error for all reflections after refinement using  the current refinement target.  Examples: null """
		self._enter('pdbx_overall_phase_error', Query)
		return self
	@property
	def pdbx_refine_id(self) -> 'Refine':
		"""This data item uniquely identifies a refinement within an entry.  _refine.pdbx_refine_id can be used to distinguish the results of  joint refinements."""
		self._enter('pdbx_refine_id', Query)
		return self
	@property
	def pdbx_solvent_ion_probe_radii(self) -> 'Refine':
		"""For bulk solvent mask calculation, the amount that the ionic radii of atoms, which can be ions, are increased used."""
		self._enter('pdbx_solvent_ion_probe_radii', Query)
		return self
	@property
	def pdbx_solvent_shrinkage_radii(self) -> 'Refine':
		"""For bulk solvent mask calculation, amount mask is shrunk after taking away atoms with new radii and a constant value assigned to this new region."""
		self._enter('pdbx_solvent_shrinkage_radii', Query)
		return self
	@property
	def pdbx_solvent_vdw_probe_radii(self) -> 'Refine':
		"""For bulk solvent mask calculation, the value by which the vdw radii of non-ion atoms (like carbon) are increased and used."""
		self._enter('pdbx_solvent_vdw_probe_radii', Query)
		return self
	@property
	def pdbx_starting_model(self) -> 'Refine':
		"""Starting model for refinement.  Starting model for  molecular replacement should refer to a previous  structure or experiment.  Examples: 1XYZ, 2XYZ, BDL001 """
		self._enter('pdbx_starting_model', Query)
		return self
	@property
	def pdbx_stereochem_target_val_spec_case(self) -> 'Refine':
		"""Special case of stereochemistry target values used in SHELXL refinement."""
		self._enter('pdbx_stereochem_target_val_spec_case', Query)
		return self
	@property
	def pdbx_stereochemistry_target_values(self) -> 'Refine':
		"""Stereochemistry target values used in refinement."""
		self._enter('pdbx_stereochemistry_target_values', Query)
		return self
	@property
	def solvent_model_details(self) -> 'Refine':
		"""Special aspects of the solvent model used during refinement."""
		self._enter('solvent_model_details', Query)
		return self
	@property
	def solvent_model_param_bsol(self) -> 'Refine':
		"""The value of the BSOL solvent-model parameter describing  the average isotropic displacement parameter of disordered  solvent atoms.   This is one of the two parameters (the other is  _refine.solvent_model_param_ksol) in Tronrud's method of  modelling the contribution of bulk solvent to the  scattering. The standard scale factor is modified according  to the expression       k0 exp(-B0 * s^2^)[1-KSOL * exp(-BSOL * s^2^)]   where k0 and B0 are the scale factors for the protein.   Ref: Tronrud, D. E. (1997). Methods Enzymol. 277, 243-268."""
		self._enter('solvent_model_param_bsol', Query)
		return self
	@property
	def solvent_model_param_ksol(self) -> 'Refine':
		"""The value of the KSOL solvent-model parameter describing  the ratio of the electron density in the bulk solvent to the  electron density in the molecular solute.   This is one of the two parameters (the other is  _refine.solvent_model_param_bsol) in Tronrud's method of  modelling the contribution of bulk solvent to the  scattering. The standard scale factor is modified according  to the expression       k0 exp(-B0 * s^2^)[1-KSOL * exp(-BSOL * s^2^)]   where k0 and B0 are the scale factors for the protein.   Ref: Tronrud, D. E. (1997). Methods Enzymol. 277, 243-268."""
		self._enter('solvent_model_param_ksol', Query)
		return self

class RefineAnalyze(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def Luzzati_coordinate_error_free(self) -> 'RefineAnalyze':
		"""The estimated coordinate error obtained from the plot of  the R value versus sin(theta)/lambda for the reflections  treated as a test set during refinement.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
		self._enter('Luzzati_coordinate_error_free', Query)
		return self
	@property
	def Luzzati_coordinate_error_obs(self) -> 'RefineAnalyze':
		"""The estimated coordinate error obtained from the plot of  the R value versus sin(theta)/lambda for reflections classified  as observed.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
		self._enter('Luzzati_coordinate_error_obs', Query)
		return self
	@property
	def Luzzati_d_res_low_free(self) -> 'RefineAnalyze':
		"""The value of the low-resolution cutoff used in constructing the  Luzzati plot for reflections treated as a test set during  refinement.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
		self._enter('Luzzati_d_res_low_free', Query)
		return self
	@property
	def Luzzati_d_res_low_obs(self) -> 'RefineAnalyze':
		"""The value of the low-resolution cutoff used in  constructing the Luzzati plot for reflections classified as  observed.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
		self._enter('Luzzati_d_res_low_obs', Query)
		return self
	@property
	def Luzzati_sigma_a_free(self) -> 'RefineAnalyze':
		"""The value of sigma~a~ used in constructing the Luzzati plot for  the reflections treated as a test set during refinement.  Details of the estimation of sigma~a~ can be specified  in _refine_analyze.Luzzati_sigma_a_free_details.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
		self._enter('Luzzati_sigma_a_free', Query)
		return self
	@property
	def Luzzati_sigma_a_obs(self) -> 'RefineAnalyze':
		"""The value of sigma~a~ used in constructing the Luzzati plot for  reflections classified as observed. Details of the  estimation of sigma~a~ can be specified in  _refine_analyze.Luzzati_sigma_a_obs_details.   Ref:  Luzzati, V. (1952). Traitement statistique des erreurs  dans la determination des structures cristallines. Acta  Cryst. 5, 802-810."""
		self._enter('Luzzati_sigma_a_obs', Query)
		return self
	@property
	def number_disordered_residues(self) -> 'RefineAnalyze':
		"""The number of discretely disordered residues in the refined  model."""
		self._enter('number_disordered_residues', Query)
		return self
	@property
	def occupancy_sum_hydrogen(self) -> 'RefineAnalyze':
		"""The sum of the occupancies of the hydrogen atoms in the refined  model."""
		self._enter('occupancy_sum_hydrogen', Query)
		return self
	@property
	def occupancy_sum_non_hydrogen(self) -> 'RefineAnalyze':
		"""The sum of the occupancies of the non-hydrogen atoms in the   refined model."""
		self._enter('occupancy_sum_non_hydrogen', Query)
		return self
	@property
	def pdbx_Luzzati_d_res_high_obs(self) -> 'RefineAnalyze':
		"""record the high resolution for calculating Luzzati statistics."""
		self._enter('pdbx_Luzzati_d_res_high_obs', Query)
		return self
	@property
	def pdbx_refine_id(self) -> 'RefineAnalyze':
		"""This data item uniquely identifies a refinement within an entry.  _refine_analyze.pdbx_refine_id can be used to distinguish the results  of joint refinements."""
		self._enter('pdbx_refine_id', Query)
		return self

class RefineHist(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def cycle_id(self) -> 'RefineHist':
		"""The value of _refine_hist.cycle_id must uniquely identify a  record in the REFINE_HIST list.   Note that this item need not be a number; it can be any unique  identifier."""
		self._enter('cycle_id', Query)
		return self
	@property
	def d_res_high(self) -> 'RefineHist':
		"""The lowest value for the interplanar spacings for the  reflection data for this cycle of refinement. This is called  the highest resolution."""
		self._enter('d_res_high', Query)
		return self
	@property
	def d_res_low(self) -> 'RefineHist':
		"""The highest value for the interplanar spacings for the  reflection data for this cycle of refinement. This is  called the lowest resolution."""
		self._enter('d_res_low', Query)
		return self
	@property
	def number_atoms_solvent(self) -> 'RefineHist':
		"""The number of solvent atoms that were included in the model at  this cycle of the refinement."""
		self._enter('number_atoms_solvent', Query)
		return self
	@property
	def number_atoms_total(self) -> 'RefineHist':
		"""The total number of atoms that were included in the model at  this cycle of the refinement."""
		self._enter('number_atoms_total', Query)
		return self
	@property
	def pdbx_B_iso_mean_ligand(self) -> 'RefineHist':
		"""Mean isotropic B-value for ligand molecules included in refinement."""
		self._enter('pdbx_B_iso_mean_ligand', Query)
		return self
	@property
	def pdbx_B_iso_mean_solvent(self) -> 'RefineHist':
		"""Mean isotropic B-value for solvent molecules included in refinement."""
		self._enter('pdbx_B_iso_mean_solvent', Query)
		return self
	@property
	def pdbx_number_atoms_ligand(self) -> 'RefineHist':
		"""Number of ligand atoms included in refinement"""
		self._enter('pdbx_number_atoms_ligand', Query)
		return self
	@property
	def pdbx_number_atoms_nucleic_acid(self) -> 'RefineHist':
		"""Number of nucleic atoms included in refinement"""
		self._enter('pdbx_number_atoms_nucleic_acid', Query)
		return self
	@property
	def pdbx_number_atoms_protein(self) -> 'RefineHist':
		"""Number of protein atoms included in refinement"""
		self._enter('pdbx_number_atoms_protein', Query)
		return self
	@property
	def pdbx_number_residues_total(self) -> 'RefineHist':
		"""Total number of polymer residues included in refinement."""
		self._enter('pdbx_number_residues_total', Query)
		return self
	@property
	def pdbx_refine_id(self) -> 'RefineHist':
		"""This data item uniquely identifies a refinement within an entry.  _refine_hist.pdbx_refine_id can be used to distinguish the results  of joint refinements."""
		self._enter('pdbx_refine_id', Query)
		return self

class RefineLsRestr(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def dev_ideal(self) -> 'RefineLsRestr':
		"""For the given parameter type, the root-mean-square deviation  between the ideal values used as restraints in the least-squares  refinement and the values obtained by refinement. For instance,  bond distances may deviate by 0.018 \%A (r.m.s.) from ideal  values in the current model."""
		self._enter('dev_ideal', Query)
		return self
	@property
	def dev_ideal_target(self) -> 'RefineLsRestr':
		"""For the given parameter type, the target root-mean-square  deviation between the ideal values used as restraints in the  least-squares refinement and the values obtained by refinement."""
		self._enter('dev_ideal_target', Query)
		return self
	@property
	def number(self) -> 'RefineLsRestr':
		"""The number of parameters of this type subjected to restraint in  least-squares refinement."""
		self._enter('number', Query)
		return self
	@property
	def pdbx_refine_id(self) -> 'RefineLsRestr':
		"""This data item uniquely identifies a refinement within an entry.  _refine_ls_restr.pdbx_refine_id can be used to distinguish the results  of joint refinements."""
		self._enter('pdbx_refine_id', Query)
		return self
	@property
	def pdbx_restraint_function(self) -> 'RefineLsRestr':
		"""The functional form of the restraint function used in the least-squares  refinement.  Examples: SINUSOIDAL, HARMONIC, SEMIHARMONIC """
		self._enter('pdbx_restraint_function', Query)
		return self
	@property
	def type(self) -> 'RefineLsRestr':
		"""The type of the parameter being restrained.  Explicit sets of data values are provided for the programs  PROTIN/PROLSQ (beginning with p_) and RESTRAIN (beginning with  RESTRAIN_). As computer programs change, these data values  are given as examples, not as an enumeration list. Computer  programs that convert a data block to a refinement table will  expect the exact form of the data values given here to be used.  Examples: p_bond_d, p_angle_d, p_planar_d, p_xhbond_d, p_xhangle_d, p_hydrog_d, p_special_d, p_planar, p_chiral, p_singtor_nbd, p_multtor_nbd, p_xyhbond_nbd, p_xhyhbond_nbd, p_special_tor, p_planar_tor, p_staggered_tor, p_orthonormal_tor, p_mcbond_it, p_mcangle_it, p_scbond_it, p_scangle_it, p_xhbond_it, p_xhangle_it, p_special_it, RESTRAIN_Distances < 2.12, RESTRAIN_Distances 2.12 < D < 2.625, RESTRAIN_Distances > 2.625, RESTRAIN_Peptide Planes, RESTRAIN_Ring and other planes, RESTRAIN_rms diffs for Uiso atoms at dist 1.2-1.4, RESTRAIN_rms diffs for Uiso atoms at dist 1.4-1.6, RESTRAIN_rms diffs for Uiso atoms at dist 1.8-2.0, RESTRAIN_rms diffs for Uiso atoms at dist 2.0-2.2, RESTRAIN_rms diffs for Uiso atoms at dist 2.2-2.4, RESTRAIN_rms diffs for Uiso atoms at dist >2.4 """
		self._enter('type', Query)
		return self
	@property
	def weight(self) -> 'RefineLsRestr':
		"""The weighting value applied to this type of restraint in  the least-squares refinement."""
		self._enter('weight', Query)
		return self

class Reflns(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def B_iso_Wilson_estimate(self) -> 'Reflns':
		"""The value of the overall isotropic displacement parameter  estimated from the slope of the Wilson plot."""
		self._enter('B_iso_Wilson_estimate', Query)
		return self
	@property
	def R_free_details(self) -> 'Reflns':
		"""A description of the method by which a subset of reflections was  selected for exclusion from refinement so as to be used in the  calculation of a 'free' R factor.  Examples: The data set was sorted with l varying most                                   rapidly and h varying least rapidly. Every                                   10th reflection in this sorted list was                                   excluded from refinement and included in the                                   calculation of a 'free' R factor. """
		self._enter('R_free_details', Query)
		return self
	@property
	def Rmerge_F_all(self) -> 'Reflns':
		"""Residual factor Rmerge for all reflections that satisfy the  resolution limits established by _reflns.d_resolution_high  and _reflns.d_resolution_low.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
		self._enter('Rmerge_F_all', Query)
		return self
	@property
	def Rmerge_F_obs(self) -> 'Reflns':
		"""Residual factor Rmerge for reflections that satisfy the  resolution limits established by _reflns.d_resolution_high  and _reflns.d_resolution_low and the observation limit  established by _reflns.observed_criterion.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
		self._enter('Rmerge_F_obs', Query)
		return self
	@property
	def d_resolution_high(self) -> 'Reflns':
		"""The smallest value in angstroms for the interplanar spacings  for the reflection data. This is called the highest resolution."""
		self._enter('d_resolution_high', Query)
		return self
	@property
	def d_resolution_low(self) -> 'Reflns':
		"""The largest value in angstroms for the interplanar spacings  for the reflection data. This is called the lowest resolution."""
		self._enter('d_resolution_low', Query)
		return self
	@property
	def data_reduction_details(self) -> 'Reflns':
		"""A description of special aspects of the data-reduction  procedures.  Examples: Merging and scaling based on only those                                   reflections with I > sig(I). """
		self._enter('data_reduction_details', Query)
		return self
	@property
	def data_reduction_method(self) -> 'Reflns':
		"""The method used for data reduction.   Note that this is not the computer program used, which is  described in the SOFTWARE category, but the method  itself.   This data item should be used to describe significant  methodological options used within the data-reduction programs.  Examples: Profile fitting by method of Kabsch (1987).                                   Scaling used spherical harmonic coefficients. """
		self._enter('data_reduction_method', Query)
		return self
	@property
	def details(self) -> 'Reflns':
		"""A description of reflection data not covered by other data  names. This should include details of the Friedel pairs."""
		self._enter('details', Query)
		return self
	@property
	def limit_h_max(self) -> 'Reflns':
		"""Maximum value of the Miller index h for the reflection data. This  need not have the same value as _diffrn_reflns.limit_h_max."""
		self._enter('limit_h_max', Query)
		return self
	@property
	def limit_h_min(self) -> 'Reflns':
		"""Minimum value of the Miller index h for the reflection data. This  need not have the same value as _diffrn_reflns.limit_h_min."""
		self._enter('limit_h_min', Query)
		return self
	@property
	def limit_k_max(self) -> 'Reflns':
		"""Maximum value of the Miller index k for the reflection data. This  need not have the same value as _diffrn_reflns.limit_k_max."""
		self._enter('limit_k_max', Query)
		return self
	@property
	def limit_k_min(self) -> 'Reflns':
		"""Minimum value of the Miller index k for the reflection data. This  need not have the same value as _diffrn_reflns.limit_k_min."""
		self._enter('limit_k_min', Query)
		return self
	@property
	def limit_l_max(self) -> 'Reflns':
		"""Maximum value of the Miller index l for the reflection data. This  need not have the same value as _diffrn_reflns.limit_l_max."""
		self._enter('limit_l_max', Query)
		return self
	@property
	def limit_l_min(self) -> 'Reflns':
		"""Minimum value of the Miller index l for the reflection data. This  need not have the same value as _diffrn_reflns.limit_l_min."""
		self._enter('limit_l_min', Query)
		return self
	@property
	def number_all(self) -> 'Reflns':
		"""The total number of reflections in the REFLN list (not the  DIFFRN_REFLN list). This number may contain Friedel-equivalent  reflections according to the nature of the structure and the  procedures used. The item _reflns.details describes the  reflection data."""
		self._enter('number_all', Query)
		return self
	@property
	def number_obs(self) -> 'Reflns':
		"""The number of reflections in the REFLN list (not the DIFFRN_REFLN  list) classified as observed (see _reflns.observed_criterion).  This number may contain Friedel-equivalent reflections according  to the nature of the structure and the procedures used."""
		self._enter('number_obs', Query)
		return self
	@property
	def observed_criterion(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'. This  criterion is usually expressed in terms of a sigma(I) or  sigma(F) threshold.  Examples: >2sigma(I) """
		self._enter('observed_criterion', Query)
		return self
	@property
	def observed_criterion_F_max(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'  expressed as an upper limit for the value of F."""
		self._enter('observed_criterion_F_max', Query)
		return self
	@property
	def observed_criterion_F_min(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'  expressed as a lower limit for the value of F."""
		self._enter('observed_criterion_F_min', Query)
		return self
	@property
	def observed_criterion_I_max(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'  expressed as an upper limit for the value of I."""
		self._enter('observed_criterion_I_max', Query)
		return self
	@property
	def observed_criterion_I_min(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'  expressed as a lower limit for the value of I."""
		self._enter('observed_criterion_I_min', Query)
		return self
	@property
	def observed_criterion_sigma_F(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'  expressed as a multiple of the value of sigma(F)."""
		self._enter('observed_criterion_sigma_F', Query)
		return self
	@property
	def observed_criterion_sigma_I(self) -> 'Reflns':
		"""The criterion used to classify a reflection as 'observed'  expressed as a multiple of the value of sigma(I)."""
		self._enter('observed_criterion_sigma_I', Query)
		return self
	@property
	def pdbx_CC_half(self) -> 'Reflns':
		"""The Pearson's correlation coefficient expressed as a decimal value               between the average intensities from randomly selected               half-datasets.  	      Ref: Karplus & Diederichs (2012), Science 336, 1030-33"""
		self._enter('pdbx_CC_half', Query)
		return self
	@property
	def pdbx_R_split(self) -> 'Reflns':
		"""R split measures the agreement between the sets of intensities created by merging               odd- and even-numbered images  from the overall data.  	      Ref: T. A. White, R. A. Kirian, A. V. Martin, A. Aquila, K. Nass, A. Barty               and H. N. Chapman (2012), J. Appl. Cryst. 45, 335-341"""
		self._enter('pdbx_R_split', Query)
		return self
	@property
	def pdbx_Rmerge_I_obs(self) -> 'Reflns':
		"""The R value for merging intensities satisfying the observed  criteria in this data set."""
		self._enter('pdbx_Rmerge_I_obs', Query)
		return self
	@property
	def pdbx_Rpim_I_all(self) -> 'Reflns':
		"""The precision-indicating merging R factor value Rpim,  for merging all intensities in this data set.          sum~i~ [1/(N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |  Rpim = --------------------------------------------------                       sum~i~ ( sum~j~ I~j~ )   I~j~   = the intensity of the jth observation of reflection i  <I~i~> = the mean of the intensities of all observations           of reflection i  N~i~   = the redundancy (the number of times reflection i           has been measured).   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection.   Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.       Biol. 4, 269-275.       Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.       30, 203-205.       Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
		self._enter('pdbx_Rpim_I_all', Query)
		return self
	@property
	def pdbx_Rrim_I_all(self) -> 'Reflns':
		"""The redundancy-independent merging R factor value Rrim,               also denoted Rmeas, for merging all intensities in this               data set.                       sum~i~ [N~i~/(N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |               Rrim = ----------------------------------------------------                                   sum~i~ ( sum~j~ I~j~ )                I~j~   = the intensity of the jth observation of reflection i               <I~i~> = the mean of the intensities of all observations of                        reflection i 	       N~i~   = the redundancy (the number of times reflection i                        has been measured).                sum~i~ is taken over all reflections               sum~j~ is taken over all observations of each reflection.                Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.                    Biol. 4, 269-275.                    Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.                    30, 203-205.                    Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
		self._enter('pdbx_Rrim_I_all', Query)
		return self
	@property
	def pdbx_Rsym_value(self) -> 'Reflns':
		"""The R sym value as a decimal number.  Examples: null """
		self._enter('pdbx_Rsym_value', Query)
		return self
	@property
	def pdbx_chi_squared(self) -> 'Reflns':
		"""Overall  Chi-squared statistic."""
		self._enter('pdbx_chi_squared', Query)
		return self
	@property
	def pdbx_diffrn_id(self) -> 'Reflns':
		"""An identifier for the diffraction data set for this set of summary statistics.   Multiple diffraction data sets entered as a comma separated list."""
		self._enter('pdbx_diffrn_id', Query)
		return self
	@property
	def pdbx_netI_over_av_sigmaI(self) -> 'Reflns':
		"""The ratio of the average intensity to the average uncertainty,  <I>/<sigma(I)>."""
		self._enter('pdbx_netI_over_av_sigmaI', Query)
		return self
	@property
	def pdbx_netI_over_sigmaI(self) -> 'Reflns':
		"""The mean of the ratio of the intensities to their  standard uncertainties, <I/sigma(I)>."""
		self._enter('pdbx_netI_over_sigmaI', Query)
		return self
	@property
	def pdbx_number_measured_all(self) -> 'Reflns':
		"""Total number of measured reflections."""
		self._enter('pdbx_number_measured_all', Query)
		return self
	@property
	def pdbx_ordinal(self) -> 'Reflns':
		"""An ordinal identifier for this set of reflection statistics."""
		self._enter('pdbx_ordinal', Query)
		return self
	@property
	def pdbx_redundancy(self) -> 'Reflns':
		"""Overall redundancy for this data set."""
		self._enter('pdbx_redundancy', Query)
		return self
	@property
	def pdbx_scaling_rejects(self) -> 'Reflns':
		"""Number of reflections rejected in scaling operations."""
		self._enter('pdbx_scaling_rejects', Query)
		return self
	@property
	def percent_possible_obs(self) -> 'Reflns':
		"""The percentage of geometrically possible reflections represented  by reflections that satisfy the resolution limits established  by _reflns.d_resolution_high and _reflns.d_resolution_low and  the observation limit established by  _reflns.observed_criterion."""
		self._enter('percent_possible_obs', Query)
		return self
	@property
	def phase_calculation_details(self) -> 'Reflns':
		"""The value of _reflns.phase_calculation_details describes a  special details about calculation of phases in _refln.phase_calc.  Examples: From model, NCS averaging, Solvent flipping, Solvent flattening, Multiple crystal averaging, Multiple phase modification, Other phase modification """
		self._enter('phase_calculation_details', Query)
		return self

class ReflnsShell(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def Rmerge_F_all(self) -> 'ReflnsShell':
		"""Residual factor Rmerge for all reflections that satisfy the  resolution limits established by _reflns_shell.d_res_high and  _reflns_shell.d_res_low.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
		self._enter('Rmerge_F_all', Query)
		return self
	@property
	def Rmerge_F_obs(self) -> 'ReflnsShell':
		"""Residual factor Rmerge for reflections that satisfy the  resolution limits established by _reflns_shell.d_res_high and  _reflns_shell.d_res_low and the observation criterion  established by _reflns.observed_criterion.               sum~i~(sum~j~|F~j~ - <F>|)  Rmerge(F) = --------------------------                   sum~i~(sum~j~<F>)   F~j~ = the amplitude of the jth observation of reflection i  <F>  = the mean of the amplitudes of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
		self._enter('Rmerge_F_obs', Query)
		return self
	@property
	def Rmerge_I_all(self) -> 'ReflnsShell':
		"""The value of Rmerge(I) for all reflections in a given shell.               sum~i~(sum~j~|I~j~ - <I>|)  Rmerge(I) = --------------------------                  sum~i~(sum~j~<I>)   I~j~ = the intensity of the jth observation of reflection i  <I>  = the mean of the intensities of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
		self._enter('Rmerge_I_all', Query)
		return self
	@property
	def Rmerge_I_obs(self) -> 'ReflnsShell':
		"""The value of Rmerge(I) for reflections classified as 'observed'  (see _reflns.observed_criterion) in a given shell.               sum~i~(sum~j~|I~j~ - <I>|)  Rmerge(I) = --------------------------                  sum~i~(sum~j~<I>)   I~j~ = the intensity of the jth observation of reflection i  <I>  = the mean of the intensities of all observations of         reflection i   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection"""
		self._enter('Rmerge_I_obs', Query)
		return self
	@property
	def d_res_high(self) -> 'ReflnsShell':
		"""The smallest value in angstroms for the interplanar spacings  for the reflections in this shell. This is called the highest  resolution."""
		self._enter('d_res_high', Query)
		return self
	@property
	def d_res_low(self) -> 'ReflnsShell':
		"""The highest value in angstroms for the interplanar spacings  for the reflections in this shell. This is called the lowest  resolution."""
		self._enter('d_res_low', Query)
		return self
	@property
	def meanI_over_sigI_all(self) -> 'ReflnsShell':
		"""The ratio of the mean of the intensities of all reflections  in this shell to the mean of the standard uncertainties of the  intensities of all reflections in this shell."""
		self._enter('meanI_over_sigI_all', Query)
		return self
	@property
	def meanI_over_sigI_obs(self) -> 'ReflnsShell':
		"""The ratio of the mean of the intensities of the reflections  classified as 'observed' (see _reflns.observed_criterion) in  this shell to the mean of the standard uncertainties of the  intensities of the 'observed' reflections in this  shell."""
		self._enter('meanI_over_sigI_obs', Query)
		return self
	@property
	def meanI_over_uI_all(self) -> 'ReflnsShell':
		"""The ratio of the mean of the intensities of all reflections  in this shell to the mean of the standard uncertainties of the  intensities of all reflections in this shell."""
		self._enter('meanI_over_uI_all', Query)
		return self
	@property
	def number_measured_all(self) -> 'ReflnsShell':
		"""The total number of reflections measured for this  shell."""
		self._enter('number_measured_all', Query)
		return self
	@property
	def number_measured_obs(self) -> 'ReflnsShell':
		"""The number of reflections classified as 'observed'  (see _reflns.observed_criterion) for this  shell."""
		self._enter('number_measured_obs', Query)
		return self
	@property
	def number_possible(self) -> 'ReflnsShell':
		"""The number of unique reflections it is possible to measure in  this shell."""
		self._enter('number_possible', Query)
		return self
	@property
	def number_unique_all(self) -> 'ReflnsShell':
		"""The total number of measured reflections which are symmetry-  unique after merging for this shell."""
		self._enter('number_unique_all', Query)
		return self
	@property
	def number_unique_obs(self) -> 'ReflnsShell':
		"""The total number of measured reflections classified as 'observed'  (see _reflns.observed_criterion) which are symmetry-unique  after merging for this shell."""
		self._enter('number_unique_obs', Query)
		return self
	@property
	def pdbx_CC_half(self) -> 'ReflnsShell':
		"""The Pearson's correlation coefficient expressed as a decimal value               between the average intensities from randomly selected               half-datasets within the resolution shell.  	      Ref: Karplus & Diederichs (2012), Science 336, 1030-33"""
		self._enter('pdbx_CC_half', Query)
		return self
	@property
	def pdbx_R_split(self) -> 'ReflnsShell':
		"""R split measures the agreement between the sets of intensities created by merging               odd- and even-numbered images from the data within the resolution shell.  	      Ref: T. A. White, R. A. Kirian, A. V. Martin, A. Aquila, K. Nass, 	      A. Barty and H. N. Chapman (2012), J. Appl. Cryst. 45, 335-341"""
		self._enter('pdbx_R_split', Query)
		return self
	@property
	def pdbx_Rpim_I_all(self) -> 'ReflnsShell':
		"""The precision-indicating merging R factor value Rpim,  for merging all intensities in a given shell.          sum~i~ [1/(N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |  Rpim = --------------------------------------------------                       sum~i~ ( sum~j~ I~j~ )   I~j~   = the intensity of the jth observation of reflection i  <I~i~> = the mean of the intensities of all observations of           reflection i  N~i~   = the redundancy (the number of times reflection i           has been measured).   sum~i~ is taken over all reflections  sum~j~ is taken over all observations of each reflection.   Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.       Biol. 4, 269-275.       Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.       30, 203-205.       Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
		self._enter('pdbx_Rpim_I_all', Query)
		return self
	@property
	def pdbx_Rrim_I_all(self) -> 'ReflnsShell':
		"""The redundancy-independent merging R factor value Rrim,               also denoted Rmeas, for merging all intensities in a               given shell.                       sum~i~ [N~i~ /( N~i~ - 1)]1/2^ sum~j~ | I~j~ - <I~i~> |               Rrim = --------------------------------------------------------                                    sum~i~ ( sum~j~ I~j~ )                I~j~   = the intensity of the jth observation of reflection i               <I~i~> = the mean of the intensities of all observations of                        reflection i 	      N~i~   = the redundancy (the number of times reflection i                        has been measured).                sum~i~ is taken over all reflections               sum~j~ is taken over all observations of each reflection.                Ref: Diederichs, K. & Karplus, P. A. (1997). Nature Struct.                    Biol. 4, 269-275.                    Weiss, M. S. & Hilgenfeld, R. (1997). J. Appl. Cryst.                    30, 203-205.                    Weiss, M. S. (2001). J. Appl. Cryst. 34, 130-135."""
		self._enter('pdbx_Rrim_I_all', Query)
		return self
	@property
	def pdbx_Rsym_value(self) -> 'ReflnsShell':
		"""R sym value in percent."""
		self._enter('pdbx_Rsym_value', Query)
		return self
	@property
	def pdbx_chi_squared(self) -> 'ReflnsShell':
		"""Chi-squared statistic for this resolution shell."""
		self._enter('pdbx_chi_squared', Query)
		return self
	@property
	def pdbx_diffrn_id(self) -> 'ReflnsShell':
		"""An identifier for the diffraction data set corresponding to this resolution shell.   Multiple diffraction data sets specified as a comma separated list."""
		self._enter('pdbx_diffrn_id', Query)
		return self
	@property
	def pdbx_netI_over_sigmaI_all(self) -> 'ReflnsShell':
		"""The mean of the ratio of the intensities to their  standard uncertainties of all reflections in the  resolution shell.   _reflns_shell.pdbx_netI_over_sigmaI_all =  <I/sigma(I)>"""
		self._enter('pdbx_netI_over_sigmaI_all', Query)
		return self
	@property
	def pdbx_netI_over_sigmaI_obs(self) -> 'ReflnsShell':
		"""The mean of the ratio of the intensities to their  standard uncertainties of observed reflections  (see _reflns.observed_criterion) in the resolution shell.   _reflns_shell.pdbx_netI_over_sigmaI_obs =  <I/sigma(I)>"""
		self._enter('pdbx_netI_over_sigmaI_obs', Query)
		return self
	@property
	def pdbx_ordinal(self) -> 'ReflnsShell':
		"""An ordinal identifier for this resolution shell."""
		self._enter('pdbx_ordinal', Query)
		return self
	@property
	def pdbx_redundancy(self) -> 'ReflnsShell':
		"""Redundancy for the current shell."""
		self._enter('pdbx_redundancy', Query)
		return self
	@property
	def pdbx_rejects(self) -> 'ReflnsShell':
		"""The number of rejected reflections in the resolution  shell.  Reflections may be rejected from scaling  by setting the observation criterion,  _reflns.observed_criterion."""
		self._enter('pdbx_rejects', Query)
		return self
	@property
	def percent_possible_all(self) -> 'ReflnsShell':
		"""The percentage of geometrically possible reflections represented  by all reflections measured for this shell."""
		self._enter('percent_possible_all', Query)
		return self
	@property
	def percent_possible_obs(self) -> 'ReflnsShell':
		"""The percentage of geometrically possible reflections represented  by reflections classified as 'observed' (see  _reflns.observed_criterion) for this shell."""
		self._enter('percent_possible_obs', Query)
		return self

class Software(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def citation_id(self) -> 'Software':
		"""This data item is a pointer to _citation.id in the CITATION  category."""
		self._enter('citation_id', Query)
		return self
	@property
	def classification(self) -> 'Software':
		"""The classification of the program according to its  major function.  Examples: data collection, data reduction, phasing, model building, refinement, validation, other """
		self._enter('classification', Query)
		return self
	@property
	def contact_author(self) -> 'Software':
		"""The recognized contact author of the software. This could be  the original author, someone who has modified the code or  someone who maintains the code.  It should be the person  most commonly associated with the code.  Examples: T. Alwyn Jones, Axel Brunger """
		self._enter('contact_author', Query)
		return self
	@property
	def contact_author_email(self) -> 'Software':
		"""The e-mail address of the person specified in  _software.contact_author.  Examples: bourne@sdsc.edu """
		self._enter('contact_author_email', Query)
		return self
	@property
	def date(self) -> 'Software':
		"""The date the software was released.  Examples: 1991-10-01, 1990-04-30 """
		self._enter('date', Query)
		return self
	@property
	def description(self) -> 'Software':
		"""Description of the software.  Examples: Uses method of restrained least squares """
		self._enter('description', Query)
		return self
	@property
	def language(self) -> 'Software':
		"""The major computing language in which the software is  coded.  Allowable values: Ada, Awk, Basic, C, C++, C/C++, Fortran, Fortran 77, Fortran 90, Fortran_77, Java, Java & Fortran, Other, Pascal, Perl, Python, Python/C++, Tcl, assembler, csh, ksh, sh """
		self._enter('language', Query)
		return self
	@property
	def location(self) -> 'Software':
		"""The URL for an Internet address at which  details of the software can be found.  Examples: http://rosebud.sdsc.edu/projects/pb/IUCr/software.html, ftp://ftp.sdsc.edu/pub/sdsc/biology/ """
		self._enter('location', Query)
		return self
	@property
	def name(self) -> 'Software':
		"""The name of the software.  Examples: Merlot, O, Xengen, X-plor """
		self._enter('name', Query)
		return self
	@property
	def os(self) -> 'Software':
		"""The name of the operating system under which the software  runs.  Examples: Ultrix, OpenVMS, DOS, Windows 95, Windows NT, Irix, HPUX, DEC Unix """
		self._enter('os', Query)
		return self
	@property
	def pdbx_ordinal(self) -> 'Software':
		"""An ordinal index for this category"""
		self._enter('pdbx_ordinal', Query)
		return self
	@property
	def type(self) -> 'Software':
		"""The classification of the software according to the most  common types.  Allowable values: filter, jiffy, library, other, package, program """
		self._enter('type', Query)
		return self
	@property
	def version(self) -> 'Software':
		"""The version of the software.  Examples: v1.0, beta, 3.1-2, unknown """
		self._enter('version', Query)
		return self

class Struct(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def pdbx_CASP_flag(self) -> 'Struct':
		"""The item indicates whether the entry is a CASP target, a CASD-NMR target,  or similar target participating in methods development experiments.  Allowable values: N, Y """
		self._enter('pdbx_CASP_flag', Query)
		return self
	@property
	def pdbx_descriptor(self) -> 'Struct':
		"""An automatically generated descriptor for an NDB structure or  the unstructured content of the PDB COMPND record.  Examples: Cytochrome b5, Regulatory protein RecX, Uridine kinase (E.C.2.7.1.48) """
		self._enter('pdbx_descriptor', Query)
		return self
	@property
	def pdbx_model_details(self) -> 'Struct':
		"""Text description of the methodology which produced this  model structure.  Examples: This model was produced from a 10 nanosecond Amber/MD simulation starting from PDB structure ID 1ABC. """
		self._enter('pdbx_model_details', Query)
		return self
	@property
	def pdbx_model_type_details(self) -> 'Struct':
		"""A description of the type of structure model.  Examples: MINIMIZED AVERAGE """
		self._enter('pdbx_model_type_details', Query)
		return self
	@property
	def title(self) -> 'Struct':
		"""A title for the data block. The author should attempt to convey  the essence of the structure archived in the CIF in the title,  and to distinguish this structural result from others.  Examples: T4 lysozyme mutant - S32A, Rhinovirus 16 polymerase elongation complex (r1_form), Crystal structure of the OXA-10 W154A mutant at pH 9.0, Mutant structure of Thermus thermophilus HB8 uridine-cytidine kinase, Crystal structure of xylanase from Trichoderma longibrachiatum """
		self._enter('title', Query)
		return self

class StructAsym(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreBranchedEntityInstance':
		"""Return to parent (CoreBranchedEntityInstance)"""
		return self._parent if self._parent else self
	@property
	def pdbx_PDB_id(self) -> 'StructAsym':
		"""This data item is a pointer to _atom_site.pdbx_PDB_strand_id the  ATOM_SITE category.  Examples: 1ABC """
		self._enter('pdbx_PDB_id', Query)
		return self
	@property
	def pdbx_alt_id(self) -> 'StructAsym':
		"""This data item is a pointer to _atom_site.ndb_alias_strand_id the  ATOM_SITE category."""
		self._enter('pdbx_alt_id', Query)
		return self
	@property
	def pdbx_order(self) -> 'StructAsym':
		"""This data item gives the order of the structural elements in the  ATOM_SITE category."""
		self._enter('pdbx_order', Query)
		return self
	@property
	def pdbx_type(self) -> 'StructAsym':
		"""This data item describes the general type of the structural elements  in the ATOM_SITE category.  Allowable values: ATOMN, ATOMP, ATOMS, HETAC, HETAD, HETAI, HETAIN, HETAS, HETIC """
		self._enter('pdbx_type', Query)
		return self

class StructKeywords(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def pdbx_keywords(self) -> 'StructKeywords':
		"""Terms characterizing the macromolecular structure.  Examples: DNA, RNA, T-RNA, DNA/RNA, RIBOZYME, PROTEIN/DNA, PROTEIN/RNA, PEPTIDE NUCLEIC ACID, PEPTIDE NUCLEIC ACID/DNA, DNA-BINDING PROTEIN, RNA-BINDING PROTEIN """
		self._enter('pdbx_keywords', Query)
		return self
	@property
	def text(self) -> 'StructKeywords':
		"""Keywords describing this structure.  Examples: Inhibitor, Complex, Isomerase..., serine protease, inhibited complex, high-resolution refinement """
		self._enter('text', Query)
		return self

class Symmetry(QueryNode):
	""""""
	@property
	def end(self) -> 'CoreEntry':
		"""Return to parent (CoreEntry)"""
		return self._parent if self._parent else self
	@property
	def Int_Tables_number(self) -> 'Symmetry':
		"""Space-group number from International Tables for Crystallography  Vol. A (2002)."""
		self._enter('Int_Tables_number', Query)
		return self
	@property
	def cell_setting(self) -> 'Symmetry':
		"""The cell settings for this space-group symmetry.  Allowable values: cubic, hexagonal, monoclinic, orthorhombic, rhombohedral, tetragonal, triclinic, trigonal """
		self._enter('cell_setting', Query)
		return self
	@property
	def pdbx_full_space_group_name_H_M(self) -> 'Symmetry':
		"""Used for PDB space group:   Example: 'C 1 2 1'  (instead of C 2)           'P 1 2 1'  (instead of P 2)           'P 1 21 1' (instead of P 21)           'P 1 1 21' (instead of P 21 -unique C axis)           'H 3'      (instead of R 3   -hexagonal)           'H 3 2'    (instead of R 3 2 -hexagonal)  Examples: Example: 'C 1 2 1'  (instead of C 2)            'P 1 2 1'  (instead of P 2)            'P 1 21 1' (instead of P 21)            'P 1 1 21' (instead of P 21 -unique C axis)            'H 3'      (instead of R 3   -hexagonal)            'H 3 2'    (instead of R 3 2 -hexagonal) """
		self._enter('pdbx_full_space_group_name_H_M', Query)
		return self
	@property
	def space_group_name_H_M(self) -> 'Symmetry':
		"""Hermann-Mauguin space-group symbol. Note that the  Hermann-Mauguin symbol does not necessarily contain complete  information about the symmetry and the space-group origin. If  used, always supply the FULL symbol from International Tables  for Crystallography Vol. A (2002) and indicate the origin and  the setting if it is not implicit. If there is any doubt that  the equivalent positions can be uniquely deduced from this  symbol, specify the  _symmetry_equiv.pos_as_xyz or  _symmetry.space_group_name_Hall  data items as well. Leave  spaces between symbols referring to  different axes.  Examples: A 1, A 1 2 1, A 2, B 1 1 2, B 2, B 2 21 2, C 2, C 1 2 1, C 21, C 1 21 1, C 2(A 112), C 2 2 2, C 2 2 21, C 4 21 2, F 2 2 2, F 2 3, F 4 2 2, F 4 3 2, F 41 3 2, I 1 2 1, I 1 21 1, I 2, I 2 2 2, I 2 3, I 21, I 21 3, I 21 21 21, I 4, I 4 2 2, I 4 3 2, I 41, I 41/a, I 41 2 2, I 41 3 2, P 1, P 1-, P 2, P 1 2 1, P 1 1 2, P 2 2 2, P 2 3, P 2 2 21, P 2 21 21, P 21, P 1 21 1, P 1 21/c 1, P 1 1 21, P 21(C), P 21 2 21, P 21 3, P 21 21 2, P 21 21 2 A, P 21 21 21, P 3, P 3 1 2, P 3 2 1, P 31, P 31 1 2, P 31 2 1, P 32, P 32 1 2, P 32 2 1, P 4, P 4 2 2, P 4 3 2, P 4 21 2, P 41, P 41 2 2, P 41 3 2, P 41 21 2, P 42, P 42 2 2, P 42 3 2, P 42 21 2, P 43, P 43 2 2, P 43 3 2, P 43 21 2, P 6, P 6 2 2, P 61, P 61 2 2, P 62, P 62 2 2, P 63, P 63 2 2, P 64, P 64 2 2, P 65, P 65 2 2, H 3, R 3, H 3 2, R 3 2 """
		self._enter('space_group_name_H_M', Query)
		return self
	@property
	def space_group_name_Hall(self) -> 'Symmetry':
		"""Space-group symbol as described by Hall (1981). This symbol  gives the space-group setting explicitly. Leave spaces between  the separate components of the symbol.   Ref: Hall, S. R. (1981). Acta Cryst. A37, 517-525; erratum  (1981) A37, 921.  Examples: -P 2ac 2n, -R 3 2', P 61 2 2 (0 0 -1) """
		self._enter('space_group_name_Hall', Query)
		return self

def QueryBuilder() -> Query:
	"""Initializes a new GraphQL query builder root."""
	return Query(name=None)
