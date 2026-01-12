import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from ._core import (
    _get_entry,
    _get_entry_by_sequence,
    _get_uid,
    _get_uid_by_sequence, 
)    

MAX_WORKERS = os.cpu_count()

def get_entries(
    pdb_ids,
    ligands=None,
    search_method="first",
    filter_affinity_nulls: bool = True,
    max_workers=MAX_WORKERS,
    auto_mutate: bool = False,
    **mutation_kwargs,
):
    if ligands is None:
        ligands = [None] * len(pdb_ids)

    entries = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        rcsb_futures = {
            executor.submit(
                _get_entry,
                pdb_id,
                ligand,
                search_method,
                filter_affinity_nulls,
                auto_mutate,
                **mutation_kwargs,
            ): pdb_id
            for pdb_id, ligand in zip(pdb_ids, ligands)
        }
        for future in as_completed(rcsb_futures):
            pdb_id = rcsb_futures[future]
            try:
                entries[pdb_id] = future.result()
            except Exception as e:
                entries[pdb_id] = {"error": str(e)}
    return entries


def get_entries_by_sequence(
    pdb_ids: list[str],
    ref_seqs: list[str],
    ligands=None,
    search_method="first",
    filter_affinity_nulls: bool = True,
    max_workers=MAX_WORKERS,
    auto_mutate: bool = False,
    **mutation_kwargs,
):
    if ligands is None:
        ligands = [None] * len(pdb_ids)

    entries = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        rcsb_futures = {
            executor.submit(
                _get_entry_by_sequence,
                pdb_id,
                ref_seq,
                ligand,
                search_method,
                filter_affinity_nulls,
                auto_mutate,
                **mutation_kwargs,
            ): pdb_id
            for pdb_id, ref_seq, ligand in zip(pdb_ids, ref_seqs, ligands)
        }
        for future in as_completed(rcsb_futures):
            pdb_id = rcsb_futures[future]
            try:
                entries[pdb_id] = future.result()
            except Exception as e:
                entries[pdb_id] = {"error": str(e)}
    return entries


def get_uids_by_sequence(pdb_ids, ref_seqs, *, max_workers=MAX_WORKERS):
    entries = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        rcsb_futures = {
            executor.submit(_get_uid_by_sequence, pdb_id, ref_seq): pdb_id
            for pdb_id, ref_seq in zip(pdb_ids, ref_seqs)
        }
        for future in as_completed(rcsb_futures):
            pdb_id = rcsb_futures[future]
            try:
                entries[pdb_id] = future.result()
            except Exception as e:
                entries[pdb_id] = {"error": str(e)}
    return entries


def get_uids(pdb_ids, *, search_method="first", max_workers=MAX_WORKERS):
    entries = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        rcsb_futures = {
            executor.submit(_get_uid, pdb_id, search_method): pdb_id
            for pdb_id in pdb_ids
        }
        for future in as_completed(rcsb_futures):
            pdb_id = rcsb_futures[future]
            try:
                entries[pdb_id] = future.result()
            except Exception as e:
                entries[pdb_id] = {"error": str(e)}
    return entries

if __name__ == "__main__":
    def _multiple_rcsb(auto_mutate):
        pdbs = [
            "1AON", "1BVK", "1COV", "1D66", "1E0W", "1EB6", "1FAS", "1GFL", "1HHP", "1IMQ",  
            "1JSP", "1K8U", "1L2Y", "1M17", "1NKB", "1OHR", "1P38", "1QFU", "1R6J", "1S72",  
            "1TUP", "1UCL", "1V05", "1WLA", "1XNL", "1YCR", "1Z8F", "2A5I", "2BTF", "2C1W",  
            "2DUR", "2E2D", "2FQM", "2GTP", "2HYY", "2I4V", "2J0R", "2K39", "2LZM", "2MTS",  
            "2N2M", "2O9G", "2PQR", "2Q24", "2R8H", "2SNA", "2TGA", "2UUI", "2V3H", "2W0C",  
            "2XWV", "2YVZ", "2ZYS", "3A6J", "3B2A", "3CRO", "3D66", "3E1M", "3FBI", "3G6F",  
            "3HMX", "3I3W", "3J9W", "3KCB", "3LIS", "3M0M", "3NHH", "3OAS", "3PQR", "3Q7Z",  
            "3R73", "3S7I", "3T5O", "3UOQ", "3VLI", "3WJ0", "3X4J", "3Y2A", "3Z1G", "4A3D",  
            "4BWR", "4CXS", "4D0P", "4EMT", "4F4L", "4GNE", "4HWP", "4I2B", "4J8Y", "4KBP",  
            "4L5P", "4M9E", "4N92", "4O8A", "4P4T", "4QZV", "4RPS", "4SXX", "4T9W", "4UHE" 
        ]
        entries = get_entries(pdbs,auto_mutate=auto_mutate, search_method="ligand")
        # entries =get_multiple_uniprot(pdbs)
        print(entries)

        gmu = get_uids_by_sequence
        entries = gmu(["1aqc"], ["MEDLIDGIIFAANYLGSTQLLSDKTPSKNVRMMQAQEAVSRIKMAQKLMTEVDLFILTQRIKVLNADTQETMMDHPLRTISYIADIGNIVVLMARRRYKMICHVFESEDAQLIAQSIGQAFSVAYQEFLR"])
        print(entries)
