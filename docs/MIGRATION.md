
# Migrating from QCSchema v1 -> v2

This project ships two QCSchema families:

- `qcelemental/models/v1/` — QCSchema v1 (longstanding). These classes use the Pydantic v1
  API through Pydantic's compatibility layer (`from pydantic.v1 import ...`).
- `qcelemental/models/v2/` — QCSchema v2. These classes are native Pydantic v2
  models and have slightly different data layouts and validation semantics. Why a new layout?
  - Make subschema more re-useable and composible
  - Standardize naming and field availability to be more predictable
  - Bring visible change to accompany the Pydantic v2 transition

- This guide is AI generated and edited with some care. But a better guide is the [cheat sheet](docs/qcschema_cheatsheet_9Jan2026.pdf).

---

## TODO Immediately

- Accept that any QCSchema v1 won't work with Python 3.14 . But QCElemental >=0.50 will work fine with Python 3.14 *until* you try to instantiate a
  v1 model; that is, imports, periodic table, physical constants, QCSchema v2 are all fine.
- At Python <3.14, QCElemental v0.50 should work perfectly well with your codes without changes. If it doesn't, please file an issue.

## Soonish

- Change any `from qcelemental.models.somefile import SomeQCSchemaClass` or `from qcelemental.models import SomeQCSchemaClass` to `from
  qcelemental.models.v1 import SomeQCSchemaClass`. Never use `somefile`-style imports again.
- Change your `SomeQCSchemaClass.dict()`, `.json()`, and `.copy()` to `.model_dump()`, `.model_dump_json()`, and `.model_copy()`.
  Both v1 and v2 classes define both sets, but the latter set is the Pydantic v2 way and will quench a lot of warnings.

## Migrating to v2

- Note that Pydantic *does not* allow nesting Pydantic API v1 and v2 models. So prepare to overhaul all QCSchema operations at once.
- To offer both v1 and v2 interfaces to a project, convert to v2 internally and accept v1 & v2 at the "schema wrapper" or interface level, form the v1 or v2
  object (there's a QCEngine function that can be called or copied), call `convert_v(2)` on it, rewrite all of the project's internal schema usage to
v2, return control to the schema wrapper, call `convert_v(return_version)`, and return. This is how QCEngine and Psi4 work.
- To test both v1 and v2 interfaces, there are `schema_versions` pytest fixtures that can parametrize your tests for both versions.
- `convert_v` is robust enough to go back and forth as projects need.

---

### Core/common models

- `Molecule`
  - `schema_version`: v1 uses `Literal[2]` (effectively always `2`); v2 uses `Literal[3]` with stricter validation
  - Note: `Molecule.schema_version` is intentionally one ahead of the general “QCSchema vN” numbering scheme
  - Layout: no structural/layout change at v0.50
  - Behavior: v2 normalizes `symbols` to title case; `extras` defaults to `{}`; `provenance` default is validated into a dict.
  - `convert_v()` available

- `BasisSet` / `basis` (module name changes)
  - v2 makes `schema_name`/`schema_version` explicit and stricter, and conversion utilities handle `basis` supplied as a `BasisSet` object (not only a string)
  - `BasisSet.schema_name` is standardized to `qcschema_basis_set` and is now a `Literal[...]`
  - `convert_v()` available

- `FailedOperation`
  - v2 adds `schema_name` and `schema_version = 2` and enforces `success = False`
  - `extras` default changed from `None` → `{}` in both versions; code that depended on `None` must be updated
  - `convert_v()` available

#### General changes across models

- Schema naming & validation
  - Many v2 models use `Literal` `schema_name`/`schema_version` and validate them strictly; v2 may reject payloads that were previously accepted with incorrect version stamps
  - `schema_name` values are now systematic and many have changed; most v2 classes carry an explicit `schema_name`
  - In this schema family, `schema_version` is generally present on Input/Result models, plus `Molecule`, `BasisSet`, and `FailedOperation`

- Prefer `convert_v()`
  - Many models expose `.convert_v(target_version)` for v1↔v2 conversion; use it rather than hand-mapping fields

- Import/runtime compatibility across Python versions
  - The package provides visible, non-destructive warnings and placeholder behavior such that importing `qcelemental.models.v1` succeeds, but
    instantiating v1 models raises a clear `RuntimeError` on Python versions >=3.14.


---

# AtomicResultProtocols (v1) → AtomicProtocols (v2)

## Changes
- **Rename**
  - v1: `AtomicResultProtocols`
  - v2: `AtomicProtocols`
- **Schema identity added**
  - v1 protocols have no schema marker.
  - v2 adds `schema_name: Literal["qcschema_atomic_protocols"]`.
- **Fields are the same**
  - `wavefunction`, `stdout`, `error_correction`, `native_files` are unchanged in meaning and defaults.

## Migration tips
- Update imports/type refs:
  - `AtomicResultProtocols` → `AtomicProtocols`
- If you introspect JSON payloads, expect a new `"schema_name": "qcschema_atomic_protocols"` field inside protocols.

---

# AtomicSpecification (new in v2) vs “spec fields on AtomicInput” (v1)

## Changes
- **New model introduced in v2**
  - v2 creates `AtomicSpecification` and moves all “how to run it” knobs there.
- **New/explicit fields**
  - `schema_name: "qcschema_atomic_specification"` (no longer the same as `AtomicInput`)
  - `program: str` (new; not present in v1 AtomicInput) (not yet acted on by QCEngine at v0.50)
- **Moved fields (from v1 AtomicInput)**
  - v1 `AtomicInput.driver` → v2 `AtomicSpecification.driver`
  - v1 `AtomicInput.model` → v2 `AtomicSpecification.model`
  - v1 `AtomicInput.keywords` → v2 `AtomicSpecification.keywords`
  - v1 `AtomicInput.protocols` (AtomicResultProtocols) → v2 `AtomicSpecification.protocols` (AtomicProtocols)
  - v1 `AtomicInput.extras` → v2 `AtomicSpecification.extras`

## Migration tips
- When building v2 atomic computations, treat `AtomicSpecification` as the primary reusable object:
  - build spec once, reuse it across multiple molecules in `AtomicInput` or in `Optimization`,
    `TorsionDrive`, or `ManyBody` tasks, too.
- Since fields rearrange between v1 and v2 and `AtomicInput`, `AtomicSpecification`, and `QCInputSpecification`, though the latter
  two have a `convert_v() connection`, it's more sensible to use `AtomicInput.convert_v()` to avoid losing fields.


---

# AtomicInput (v1) → AtomicInput (v2)

## Changes
- **Schema name and version changed and tightened**
  - v1: `schema_name` is a regex accepting `qc_schema_input` and `qcschema_input`; `schema_version` is an `int` defaulting to `1`.
  - v2: `schema_name: Literal["qcschema_atomic_input"]`; `schema_version: Literal[2]`.
- **Structural change: specification container**
  - v1: atomic “run configuration” fields are on the input: `driver`, `model`, `keywords`, `protocols`, `extras`.
  - v2: all of that moves into `AtomicInput.specification: AtomicSpecification`.
- **Removed fields (from AtomicInput envelope)**
  - v2 `AtomicInput` no longer has `driver`, `model`, `keywords`, `protocols`, `extras` at the top level.
- **Conversion v2 → v1 is explicit and illustrates the mapping**
  - v2 → v1 conversion:
    - converts molecule via `self.molecule.convert_v(1)`
    - lifts `driver`, `model`, `keywords`, `protocols`, `extras` out of `specification`
    - drops `specification.program` and `specification.schema_name`

## Migration tips
- Update field accesses:
  - `inp.driver` → `inp.specification.driver`
  - `inp.model` → `inp.specification.model`
  - `inp.keywords` → `inp.specification.keywords`
  - `inp.protocols` → `inp.specification.protocols`
  - `inp.extras` → `inp.specification.extras`
- When constructing:
  - **Old (v1)**:
    - `AtomicInput(molecule=..., driver=..., model=..., keywords=..., protocols=..., extras=...)`
  - **New (v2)**:
    - `AtomicInput(molecule=..., specification=AtomicSpecification(driver=..., model=..., keywords=..., protocols=..., extras=..., program=...))`
  - If you have v1 objects or dicts, the preferred way to get a v2 is through `convert_v(2)` as that will handle any changes as v2 converges
    at v0.60 .

---

# AtomicResult (v1) → AtomicResult (v2)

## Changes
- **No more inheritance**
  - v1: `class AtomicResult(AtomicInput)` — result contains all input fields by inheritance.
  - v2: `class AtomicResult(ProtoModel)` — result is independent and embeds the input as `input_data: AtomicInput`.
- **Schema name and version changed**
  - v1: `schema_name: Literal["qcschema_output"]` with a validator that *accepts input schema names and coerces them to output*.
  - v2: `schema_name: Literal["qcschema_atomic_result"]`; `schema_version: Literal[2]`. No coercion.
- **Input snapshot is explicit**
  - v2 adds `input_data: AtomicInput` and keeps a separate `molecule` field:
    - `input_data.molecule` = input frame
    - `AtomicResult.molecule` = result frame/orientation
- **Error/failure representation changes**
  - v1: `success: bool` and optional `error: ComputeError`.
  - v2: `success: Literal[True]` and **no `error` field** (failures go through `FailedOperation` elsewhere).
- **Extras split**
  - v1: extras are inherited from input (`AtomicInput.extras`) and there’s no separate result extras.
  - v2: `AtomicResult.extras` exists independently of input extras.
  - v2→v1 conversion explicitly **merges** extras:
    - `{**input_data.extras, **result.extras}` (result wins on key conflicts).

## Migration tips
- Replace inheritance-based access with `input_data` access:
  - **Old (v1)**: `res.driver`, `res.model`, `res.keywords`, `res.protocols`, `res.extras`
  - **New (v2)**:
    - `res.input_data.specification.driver`
    - `res.input_data.specification.model`
    - `res.input_data.specification.keywords`
    - `res.input_data.specification.protocols`
    - input extras: `res.input_data.specification.extras`
    - result extras: `res.extras`
- Update failure handling:
  - Stop expecting `AtomicResult.success=False` or `AtomicResult.error`.
  - If you currently emit “failed AtomicResult objects”, you’ll need to emit/handle `FailedOperation` instead.
- If you relied on passing `schema_name="qcschema_input"` into a result and letting it coerce:
  - that’s gone; use the correct v2 result schema name (`qcschema_atomic_result`) explicitly.
- Conversion
  - Be aware of extras merge on down-conversion: if you convert v2 results to v1, result extras override input extras on key collisions.
  - Be aware of potential loss on up-conversion: if you convert v1 results to v2, molecule and extras separation between Input and Result
    aren't available. Molecule will be duplicated and extras assigned to Result unless `convert_v(2, external_input_data=...)` used.


---

# AtomicResultProperties (v1) → AtomicProperties (v2)

## Changes
- **Rename**
  - v1: `AtomicResultProperties`
  - v2: `AtomicProperties`
- **Schema identity added**
  - v1: no `schema_name` field on properties.
  - v2: adds `schema_name: Literal["qcschema_atomic_properties"]`.
- **Field set is effectively the same**
  - All the calcinfo/canonical/method-property fields you showed are still present with the same names and semantics.

## Migration tips
- If you referenced the class name in type checks or imports, update:
  - `AtomicResultProperties` → `AtomicProperties`
- If you have code that expects to see no schema marker on properties, note that v2 now emits:
  - `"schema_name": "qcschema_atomic_properties"`

---

# WavefunctionProperties (v1) → WavefunctionProperties (v2)

## Changes
- **Schema identity added**
  - v1: no `schema_name`.
  - v2: `schema_name: Literal["qcschema_wavefunction_properties"]`.
- **Convert_v added**
  - v2 provides `convert_v(1)` and explicitly converts embedded `basis` via `basis.convert_v(1)`.
- **Serialization semantics clarified**
  - v2 comments that WfnProp skips unset fields, but BasisSet serialization differs vs v1 (this can matter if consumers compare exact JSON outputs).
- **Validators and field set are otherwise effectively the same**
  - Same “restricted” logic, same shape validators, same “return_results index points to stored array” constraint.

## Migration tips
- Expect `schema_name` to appear in serialized wavefunction payloads.
- If downstream depends on exact JSON “unset field skipping” behavior, regression-test wavefunction serialization; v2 notes imply subtle differences particularly around nested BasisSet defaults/unset fields.
- When converting v2 → v1, wavefunction basis is converted to the v1 form explicitly; if you had basis-as-string assumptions, this is now more structured.

---

## Atomic family: path mapping cheat sheet

### v1 AtomicInput → v2 AtomicInput
- `driver` → `specification.driver`
- `model` → `specification.model`
- `keywords` → `specification.keywords`
- `protocols` → `specification.protocols`
- `extras` → `specification.extras`
- *(new)* `specification.program`

### v1 AtomicResult → v2 AtomicResult
- inherited input fields → `input_data` (and most knobs under `input_data.specification`)
- result molecule frame stays at top-level `molecule`
- `success: bool` → `success: Literal[True]`
- `error` removed


# Optimization & TorsionDrive (v1 ↔ v2) migration diff
*(Migration-focused; minimal attention to Pydantic API syntax.)*

---

# OptimizationProtocols (v1) ↔ OptimizationProtocols (v2)

## Changes
- **Schema identity added in v2**
  - v1: no `schema_name`
  - v2: `schema_name: Literal["qcschema_optimization_protocols"]`
- **Field rename**
  - v1: `trajectory: TrajectoryProtocolEnum` (default `all`)
  - v2: `trajectory_results: TrajectoryProtocolEnum` (default `none`)
- **Conversion** available
  - `convert_v()` handles the rename

## Migration tips
- Update access:
  - `protocols.trajectory` → `protocols.trajectory_results`
- Watch the **default change**:
  - v1 default keeps full trajectory (`all`)
  - v2 default keeps **none** (`none`)
  - If you relied on v1 default behavior, set `trajectory_results="all"` explicitly in v2.

---

# OptimizationSpecification (v1) ↔ OptimizationSpecification (v2)

## Changes
- **v2 is now the “real” optimization spec**
  - v1 `OptimizationSpecification` actually only used by `TorsionDriveInput.optimization_spec`
  - v2 `OptimizationSpecification` now reuseable by `OptimizationInput.specification` and `TorsionDriveSpecification.specification`.
- **Schema markers**
  - v1: `schema_name: regex "qcschema_optimization_specification"; `schema_version: Literal[1]`
  - v2: `schema_name: Literal["qcschema_optimization_specification"]` (no explicit schema_version field)
- **Field changes**
  - Procedure/program rename for (CMS/QCEngine) optimizer: v1: `procedure` v2: `program`
  - v2 `OptimizationSpecification` has `extras`; v1 spec didn’t.
  - **Nesting introduced**
    - v2 adds `specification: AtomicSpecification` (how to run gradients).
    - v1 had no nested “gradient spec” in `OptimizationSpecification`; instead, TorsionDrive separately carried a gradient spec.

## Migration tips
- Expect the gradient compute description to live at:
  - `opt_spec.specification` (generally an `AtomicSpecification` but any single point can work like a MBE)
- Like v1 `QCInputSpecification` and v2 `AtomicSpecification`, `OptimizationSpecification` is very different between versions.
  There is a `convert_v`, but acting on `Input` objects is recommended.

---

# OptimizationInput (v1) ↔ OptimizationInput (v2)

## Changes
- **Schema name/version tightened**
  - v1: `schema_name` regex for "qcschema_optimization_input", `schema_version=1`, extra `hash_index`
  - v2: `schema_name: Literal["qcschema_optimization_input"]`, `schema_version: Literal[2]`, **no `hash_index`**
- **Structural consolidation**
  - v1 top-level fields:
    - `keywords`, `extras`, `protocols`, `input_specification: QCInputSpecification`, `initial_molecule`
  - v2 top-level fields:
    - `specification: OptimizationSpecification`, `initial_molecule`
  - i.e., v2 moves `keywords/extras/protocols` into the `OptimizationSpecification` object.
- **Where the atomic spec lives** (usually gradient)
  - v1: `OptimizationInput.input_specification: QCInputSpecification`
  - v2: `OptimizationInput.specification.specification: AtomicSpecification`
- **Where “optimizer program” lives**
  - v1: often stored as `keywords["program"]` (by convention)
  - v2: optimizer program is a dedicated field at `OptimizationSpecification.program`
  - v2→v1 conversion stores atomic-spec program back into `keywords["program"]`

## Migration tips
- Update access paths:
  - v1 `opt_in.keywords` → v2 `opt_in.specification.keywords`
  - v1 `opt_in.protocols` → v2 `opt_in.specification.protocols`
  - v1 `opt_in.extras` → v2 `opt_in.specification.extras`
  - v1 `opt_in.input_specification` → v2 `opt_in.specification.specification`
- If you used `keywords["program"]` in v1:
  - In v2, set `opt_in.specification.specification.program` (gradient producer) explicitly; don’t rely on the old convention.
- Use `convert_v` to handle all these details.

---

# OptimizationProperties (v2 only)

## Changes
- **New model in v2**
  - `schema_name: "qcschema_optimization_properties"`
  - Canonical summary values including:
    - `return_energy`, `return_gradient`, `optimization_iterations`, `final_rms_force`, plus `nuclear_repulsion_energy`
- v1 had no dedicated `OptimizationProperties` model; those summary values were often derivable from `energies` and last trajectory point.

## Migration tips
- Prefer reading summary values from `OptimizationResult.properties` for the final geometry of the trajectory instead of accessing from lists:
  - `properties.return_energy` (final energy)
  - `properties.return_gradient` (final gradient when available)
  - `properties.optimization_iterations`

---

# OptimizationResult (v1) ↔ OptimizationResult (v2)

## Changes
- **No inheritance in v2**
  - v1: `OptimizationResult(OptimizationInput)` merges input fields directly into result.
  - v2: `OptimizationResult` has explicit `input_data: OptimizationInput` plus independent result fields.
- **Schema identity tightened**
  - v1: `schema_name` "qcschema_optimization_output"; schema_version inherited from input
  - v2: `schema_name: Literal["qcschema_optimization_result"]` (different), `schema_version: Literal[2]`
- **Failure semantics**
  - v1: `success: bool` and optional `error: ComputeError`
  - v2: `success: Literal[True]`, **no `error` field** (failures expected via `FailedOperation`)
  - let us know if you think a lack of False/error will be a problem.
- **Trajectory and energies are re-modeled**
  - v1:
    - `energies: List[float]` (per-step energies) (always present)
    - `trajectory: List[AtomicResult]` (controlled by protocol "trajectory"; default "all")
  - v2:
    - `trajectory_properties: List[AtomicProperties]` (per-step energies and other abridged properties)
    - `trajectory_results: List[AtomicResult]` (controlled by protocol "trajectory_results"; default "none")
- **Properties added**
  - v2 adds `properties: OptimizationProperties` (summary)
- **native_files added**
  - v2 adds `native_files: Dict[str, Any]` (placeholder; “no protocol at present”)
- **convert_v() function available**
  - Like `AtomicResult`, v1 -> v2 may need external_input_data argument to separate extras
  - For v2 -> v1, default protocol won't preserve enough info to reconstruct default protocol for `trajectory`

## Migration tips
- Update field usage:
  - `trajectory` → `trajectory_results` (note protocol default change to store less data)
  - `energies` → `[prop.return_energy for prop in trajectory_properties]` (or use `properties.return_energy` for final)
- Update access to input context:
  - v1: `opt_res.keywords`, `opt_res.protocols`, `opt_res.input_specification`
  - v2: `opt_res.input_data.specification.keywords`, `.protocols`, `.specification` (nested atomic spec)
- If you previously expected partial trajectories by default:
  - In v2, the default is **none**; set `input_data.specification.protocols.trajectory_results="all"` (or other) explicitly.

---

# TorsionDriveProtocols (v2 only)

## Changes
- New protocol model:
  - `schema_name: "qcschema_torsion_drive_protocols"`
  - `scan_results` protocol to save what had been `optimization_history` (v1) and now `scan_results` field (v2)

## Migration tips
- If you need to support v2 → v1 conversion without losing optimization history:
  - set `scan_results="all"`

---

# TDKeywords (v1) → TorsionDriveKeywords (v2)

## Changes
- **Rename**
  - v1: `TDKeywords`
  - v2: `TorsionDriveKeywords`
- **Schema identity added**
  - v2 keywords add `schema_name: "qcschema_torsion_drive_keywords"`
- Field set is otherwise the same (dihedrals/grid settings/etc).

## Migration tips
- Update imports/type checks:
  - `TDKeywords` → `TorsionDriveKeywords`

---

# TorsionDriveSpecification (v2 only)

## Changes
- New v2 spec layer:
  - `schema_name: "qcschema_torsion_drive_specification"`
  - `program` (lowercased)
  - `keywords` (TorsionDriveKeywords)
  - `protocols` (TorsionDriveProtocols)
  - `extras`
  - `specification: OptimizationSpecification` for geometry opt (which itself nests an AtomicSpecification for gradient)

## Migration tips
- Treat torsion drive as a fully nested spec stack:
  - `TorsionDriveSpecification` → `OptimizationSpecification` → `AtomicSpecification`

---

# TorsionDriveInput (v1) ↔ TorsionDriveInput (v2)

## Changes
- **Schema name/version tightened**
  - v1: schema_name "qcschema_torsion_drive_input", `schema_version=1`
  - v2: `schema_name: Literal["qcschema_torsion_drive_input"]`, `schema_version: Literal[2]`
- **Structural consolidation**
  - v1 top-level fields:
    - `keywords: TDKeywords`
    - `extras`
    - `input_specification: QCInputSpecification`
    - `optimization_spec: OptimizationSpecification`
    - `initial_molecule: List[Molecule]`
  - v2 top-level fields:
    - `initial_molecule: List[Molecule]`
    - `specification: TorsionDriveSpecification`
- **Conversion available convert_v()**

## Migration tips
- Update access paths:
  - v1 `td_in.keywords` → v2 `td_in.specification.keywords`
  - v1 `td_in.extras` → v2 `td_in.specification.extras`
  - v1 `td_in.optimization_spec` → v2 `td_in.specification.specification`
  - v1 `td_in.input_specification` → v2 `td_in.specification.specification.specification`
- If you rely on torsion-drive-specific protocols (scan opt history retention):
  - In v2, set them on `td_in.specification.protocols.scan_results = 'all'`.

---

# TorsionDriveProperties (v2 only)

## Changes
- Placeholder properties model:
  - `schema_name: "qcschema_torsion_drive_properties"`
  - currently includes `calcinfo_ngrid` and is designed for expansion.

## Migration tips
- Prefer reading `calcinfo_ngrid` from `TorsionDriveResult.properties.calcinfo_ngrid` instead of computing it from dict sizes.

---

# TorsionDriveResult (v1) ↔ TorsionDriveResult (v2)

## Changes
- **No inheritance in v2**
  - v1: `TorsionDriveResult(TorsionDriveInput)` merges input fields into result.
  - v2: `TorsionDriveResult` has explicit `input_data: TorsionDriveInput` plus independent result fields.
- **Schema identity tightened**
  - v1: schema_name: "qcschema_torsion_drive_output" ; schema_version inherited from input
  - v2: `schema_name: Literal["qcschema_torsion_drive_result"]` (different), `schema_version: Literal[2]`
- **Failure semantics**
  - v1: `success: bool` and optional `error: ComputeError`
  - v2: `success: Literal[True]`, no `error` field
- **Result field renames / restructuring**
  - v1:
    - `final_molecules: Dict[str, Molecule]`
    - `final_energies: Dict[str, float]`
    - `optimization_history: Dict[str, List[OptimizationResult]]`
  - v2:
    - `final_molecules: Dict[str, Molecule]` (still present)
    - `scan_properties: Dict[str, OptimizationProperties]` (replaces `final_energies` and expands)
    - `scan_results: Dict[str, List[OptimizationResult]]` (replaces `optimization_history`) (controlled by protocol)
- **native_files added**
  - v2 adds a placeholder `native_files` dict.
- **convert_v() available (but v2 → v1 requires all history for full fidelity)**

## Migration tips
- Update field usage:
  - `optimization_history` → `scan_results`
  - `final_energies` → `scan_properties[grid_id].return_energy`
- If you need v1-compatible exports:
  - set `td_in.specification.protocols.scan_results = "all"` before generating results.
- Update access to input context:
  - v1: `td_res.keywords`, `td_res.optimization_spec`, `td_res.input_specification`
  - v2: go through `td_res.input_data.specification...` (and then down the nested spec chain)







