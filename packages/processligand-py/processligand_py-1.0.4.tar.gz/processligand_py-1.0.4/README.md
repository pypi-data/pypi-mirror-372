# ProcessLigand as a Python Package

A Python package designed to prepare arguments and run `ProcessLigand`.

---

## Example usage:

```
from processligandpy import run_processligand

# For a ligand
result_ligand = run_processligand(file_path='path/to/target_or_ligand', atom_index=90000)

# For a target:
# result_target = run_processligand(file_path='path/to/target_or_ligand', target=True)

# Using arguments:
# result = run_processligand(file_path='path/to/target_or_ligand', atom_index=1)

# Expanding the result:
output = result_ligand.stdout
error = result_ligand.stderr
returncode = result_ligand.returncode
file_path_dict = result_ligand.file_path_dict
```

---

## Arguments

### Required Argument

| Arg         | Description                                        |
|:------------|:---------------------------------------------------|
| `file_path` | Input file (not listed in the provided dictionary) |

### Optional Arguments

| Flag         | Value Type            | Description                                                 |
|:-------------|:----------------------|:------------------------------------------------------------|
| `target`     | `<BOOL>`              | Parse a target                                              |
| `v`          | `<INT>`               | Verbose level (0 prints nothing. 1 prints everything)       |
| `o`          | `<STR>`               | Output base filename                                        |
| `e`          | `<STR>`               | Residue to extract                                          |
| `c`          | `<STR>`               | Convert molecule to specified format                        |
| `atom_index` | `<INT>`               | Starting atom index                                         |
| `res_name`   | `<STR>`               | 3-char ligand code                                          |
| `res_chain`  | `<CHAR>`              | Ligand chain                                                |
| `res_number` | `<INT>`               | Ligand number                                               |
| `force_gpa`  | `<INT>`               | Force reference atom                                        |
| `force_pcg`  | `<FLOAT FLOAT FLOAT>` | Force protein center of geometry                            |
| `d`          | `<BOOL>`              | Deletes tmp files created when converting inout to mol2     |
| `pf`         | `<BOOL>`              | Prints a line containing the filepath to every written file |
| `hf`         | `<BOOL>`              | Include hydrogen flexible bonds                             |
| `wh`         | `<BOOL>`              | Add hydrogen atoms in output                                |
| `ref`        | `<BOOL>`              | Output final PDB from IC                                    |
| `gen3D`      | `<BOOL>`              | Generate 3D conformation                                    |


---

### Raises

| Exception            | Description                                    |
|:---------------------|:-----------------------------------------------|
| `FileNotFoundError`  | If the required input file 'f' does not exist. |
| `ProcessLigandError` | If the external process fails to execute.      |

---
### Returns

| Type                  | Description                                                                     |
|:----------------------|:--------------------------------------------------------------------------------|
| `ProcessLigandResult` | A namedtuple containing `stdout`, `stderr`, `returncode`, and `file_path_dict`. |
