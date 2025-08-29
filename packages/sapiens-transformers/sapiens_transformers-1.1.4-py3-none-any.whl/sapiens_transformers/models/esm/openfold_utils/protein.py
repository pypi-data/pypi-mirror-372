"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import dataclasses
import re
import string
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple
import numpy as np
from . import residue_constants
FeatureDict = Mapping[str, np.ndarray]
ModelOutput = Mapping[str, Any]
PICO_TO_ANGSTROM = 0.01
@dataclasses.dataclass(frozen=True)
class Protein:
    atom_positions: np.ndarray
    aatype: np.ndarray
    atom_mask: np.ndarray
    residue_index: np.ndarray
    b_factors: np.ndarray
    chain_index: Optional[np.ndarray] = None
    remark: Optional[str] = None
    parents: Optional[Sequence[str]] = None
    parents_chain_index: Optional[Sequence[int]] = None
def from_proteinnet_string(proteinnet_str: str) -> Protein:
    tag_re = r"(\[[A-Z]+\]\n)"
    tags: List[str] = [tag.strip() for tag in re.split(tag_re, proteinnet_str) if len(tag) > 0]
    groups: Iterator[Tuple[str, List[str]]] = zip(tags[0::2], [l.split("\n") for l in tags[1::2]])
    atoms: List[str] = ["N", "CA", "C"]
    aatype = None
    atom_positions = None
    atom_mask = None
    for g in groups:
        if "[PRIMARY]" == g[0]:
            seq = g[1][0].strip()
            for i in range(len(seq)):
                if seq[i] not in residue_constants.restypes: seq[i] = "X"
            aatype = np.array([residue_constants.restype_order.get(res_symbol, residue_constants.restype_num) for res_symbol in seq])
        elif "[TERTIARY]" == g[0]:
            tertiary: List[List[float]] = []
            for axis in range(3): tertiary.append(list(map(float, g[1][axis].split())))
            tertiary_np = np.array(tertiary)
            atom_positions = np.zeros((len(tertiary[0]) // 3, residue_constants.atom_type_num, 3)).astype(np.float32)
            for i, atom in enumerate(atoms): atom_positions[:, residue_constants.atom_order[atom], :] = np.transpose(tertiary_np[:, i::3])
            atom_positions *= PICO_TO_ANGSTROM
        elif "[MASK]" == g[0]:
            mask = np.array(list(map({"-": 0, "+": 1}.get, g[1][0].strip())))
            atom_mask = np.zeros((len(mask), residue_constants.atom_type_num)).astype(np.float32)
            for i, atom in enumerate(atoms): atom_mask[:, residue_constants.atom_order[atom]] = 1
            atom_mask *= mask[..., None]
    assert aatype is not None
    return Protein(atom_positions=atom_positions, atom_mask=atom_mask, aatype=aatype, residue_index=np.arange(len(aatype)), b_factors=None)
def get_pdb_headers(prot: Protein, chain_id: int = 0) -> List[str]:
    pdb_headers: List[str] = []
    remark = prot.remark
    if remark is not None: pdb_headers.append(f"REMARK {remark}")
    parents = prot.parents
    parents_chain_index = prot.parents_chain_index
    if parents is not None and parents_chain_index is not None: parents = [p for i, p in zip(parents_chain_index, parents) if i == chain_id]
    if parents is None or len(parents) == 0: parents = ["N/A"]
    pdb_headers.append(f"PARENT {' '.join(parents)}")
    return pdb_headers
def add_pdb_headers(prot: Protein, pdb_str: str) -> str:
    out_pdb_lines: List[str] = []
    lines = pdb_str.split("\n")
    remark = prot.remark
    if remark is not None: out_pdb_lines.append(f"REMARK {remark}")
    parents_per_chain: List[List[str]]
    if prot.parents is not None and len(prot.parents) > 0:
        parents_per_chain = []
        if prot.parents_chain_index is not None:
            parent_dict: Dict[str, List[str]] = {}
            for p, i in zip(prot.parents, prot.parents_chain_index):
                parent_dict.setdefault(str(i), [])
                parent_dict[str(i)].append(p)
            max_idx = max([int(chain_idx) for chain_idx in parent_dict])
            for i in range(max_idx + 1):
                chain_parents = parent_dict.get(str(i), ["N/A"])
                parents_per_chain.append(chain_parents)
        else: parents_per_chain.append(list(prot.parents))
    else: parents_per_chain = [["N/A"]]
    def make_parent_line(p: Sequence[str]) -> str: return f"PARENT {' '.join(p)}"
    out_pdb_lines.append(make_parent_line(parents_per_chain[0]))
    chain_counter = 0
    for i, l in enumerate(lines):
        if "PARENT" not in l and "REMARK" not in l: out_pdb_lines.append(l)
        if "TER" in l and "END" not in lines[i + 1]:
            chain_counter += 1
            if not chain_counter >= len(parents_per_chain): chain_parents = parents_per_chain[chain_counter]
            else: chain_parents = ["N/A"]
            out_pdb_lines.append(make_parent_line(chain_parents))
    return "\n".join(out_pdb_lines)
def to_pdb(prot: Protein) -> str:
    restypes = residue_constants.restypes + ["X"]
    def res_1to3(r: int) -> str: return residue_constants.restype_1to3.get(restypes[r], "UNK")
    atom_types = residue_constants.atom_types
    pdb_lines: List[str] = []
    atom_mask = prot.atom_mask
    aatype = prot.aatype
    atom_positions = prot.atom_positions
    residue_index = prot.residue_index.astype(np.int32)
    b_factors = prot.b_factors
    chain_index = prot.chain_index
    if np.any(aatype > residue_constants.restype_num): raise ValueError("Invalid aatypes.")
    headers = get_pdb_headers(prot)
    if len(headers) > 0: pdb_lines.extend(headers)
    n = aatype.shape[0]
    atom_index = 1
    prev_chain_index = 0
    chain_tags = string.ascii_uppercase
    chain_tag = None
    for i in range(n):
        res_name_3 = res_1to3(aatype[i])
        for atom_name, pos, mask, b_factor in zip(atom_types, atom_positions[i], atom_mask[i], b_factors[i]):
            if mask < 0.5: continue
            record_type = "ATOM"
            name = atom_name if len(atom_name) == 4 else f" {atom_name}"
            alt_loc = ""
            insertion_code = ""
            occupancy = 1.00
            element = atom_name[0]
            charge = ""
            chain_tag = "A"
            if chain_index is not None: chain_tag = chain_tags[chain_index[i]]
            atom_line = (f"{record_type:<6}{atom_index:>5} {name:<4}{alt_loc:>1}{res_name_3:>3} {chain_tag:>1}{residue_index[i]:>4}{insertion_code:>1} {pos[0]:>8.3f}{pos[1]:>8.3f}{pos[2]:>8.3f}{occupancy:>6.2f}{b_factor:>6.2f} {element:>2}{charge:>2}")
            pdb_lines.append(atom_line)
            atom_index += 1
        should_terminate = i == n - 1
        if chain_index is not None:
            if i != n - 1 and chain_index[i + 1] != prev_chain_index:
                should_terminate = True
                prev_chain_index = chain_index[i + 1]
        if should_terminate:
            chain_end = "TER"
            chain_termination_line = (f"{chain_end:<6}{atom_index:>5} {res_1to3(aatype[i]):>3} {chain_tag:>1}{residue_index[i]:>4}")
            pdb_lines.append(chain_termination_line)
            atom_index += 1
            if i != n - 1: pdb_lines.extend(get_pdb_headers(prot, prev_chain_index))
    pdb_lines.append("END")
    pdb_lines.append("")
    return "\n".join(pdb_lines)
def ideal_atom_mask(prot: Protein) -> np.ndarray: return residue_constants.STANDARD_ATOM_MASK[prot.aatype]
def from_prediction(features: FeatureDict, result: ModelOutput, b_factors: Optional[np.ndarray] = None, chain_index: Optional[np.ndarray] = None, remark: Optional[str] = None,
parents: Optional[Sequence[str]] = None, parents_chain_index: Optional[Sequence[int]] = None) -> Protein:
    return Protein(aatype=features["aatype"], atom_positions=result["final_atom_positions"], atom_mask=result["final_atom_mask"], residue_index=features["residue_index"] + 1,
    b_factors=b_factors if b_factors is not None else np.zeros_like(result["final_atom_mask"]), chain_index=chain_index, remark=remark, parents=parents, parents_chain_index=parents_chain_index)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
