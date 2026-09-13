# Fixing "Some Are Rigid" After smimport — The Proper Way

You ran `smimport('Gearbox_Design.xml')` (R2025b) and found that parts that
should rotate show up connected by **Rigid Transform** blocks — i.e. welded.
This guide explains why it happens, which rigid connections in YOUR gearbox
are actually correct, and gives both proper fixes:

- **Fix A (proper, permanent)** — fix the SolidWorks assembly so the next
  export imports with the right joints automatically.
- **Fix B (patch, in MATLAB)** — replace the wrong rigid connections with
  Revolute Joints in the imported model (manually or with `fix_rigid_joints.m`).

---

## 1. Why smimport makes things rigid

smimport converts every SolidWorks mate set into exactly one of:

| SolidWorks situation | Simscape result |
|---|---|
| Component **marked Fixed** (or a subassembly fixed by default) | Rigid Transform to world/casing |
| Mates that leave **1 rotational DOF** (one Concentric + one Coincident to housing) | **Revolute Joint** (Z = shaft axis) |
| Mates that leave **0 DOF** (extra Concentric, Width, Lock, Angle, or a SW *Gear Mate*) | **Rigid Transform** — over-constrained = welded |
| Two parts bolted together (rigid by design) | Rigid Transform — correct! |

The three classic causes of "should rotate but is rigid":

1. The component was **Fixed** in the assembly (the first part you insert
   into a SolidWorks assembly is auto-fixed — sometimes it's a shaft, not the
   casing!). Also every subassembly you insert comes in as Fixed unless set
   otherwise.
2. The mate set **over-constrains** the shaft (e.g. two Concentric mates to
   two different housings, a Width/lock mate, or a SolidWorks *Gear mate* —
   gear mates do NOT export as joints).
3. The shaft is a **subassembly whose members were fixed** inside the
   subassembly file itself.

---

## 2. Which rigid connections in YOUR gearbox are CORRECT

Your assembly (`Gearbox_Design`): casing, 4 rotating shaft units, handle +
grip on the output shaft, two Gear 3 (Arm) parts. The correct joint layout is
exactly **4 Revolute Joints** — one per shaft unit, all to the casing:

| Shaft unit (must be ONE rigid body internally, and ONE Revolute to casing) | Parts that are rigidly bonded inside (correct!) |
|---|---|
| **J1 — motor input** | `pinion 1 (motor)` + `27mm shaft` |
| **J2 — intermediate A** | `gear 1` + `20mm shaft` + `Pinion 2` |
| **J3 — intermediate B** | `Gear 2` + `30mm shaft` + `Pinion 3` |
| **J4 — output / arm pivot** | `Gear 3 (Arm)` + `Gear 3 (Arm)-1/-2` + `90mm shaft` + `minishaft` + `handle` + `grip` (+ your boom arm) |

So in the imported model:

- **Rigid Transform between gear ↔ its own shaft ↔ handle = CORRECT.** Don't touch these.
- **Rigid Transform between a shaft unit and the casing = WRONG** — it must be a Revolute Joint.
- **J4 is your arm pivot** — if it's rigid, the gate can't open at all.

Everything else (meshing, 70:1) is added later with 3 **Gear Constraint**
blocks (see `SIMSCAPE_SOLIDWORKS_GUIDE.md` Part 4).

---

## 3. Identify the bad blocks (2 minutes, in R2025b)

1. Open your imported model.
2. **Debug → Diagnostics → Simscape Multibody → Multibody Model Report**
   (or press the **Model Report** button in the Mechanics Explorer toolbar).
3. Open the report's **Joints** section: it lists every joint and the DOF it
   provides. **Any shaft with no revolute entry = welded = bad.**
4. Quickest programmatic listing — in the Command Window:

```matlab
fix_rigid_joints('Gearbox_Design', 'list')   % or your imported model's name
```

   This prints every Rigid Transform block together with the two blocks it
   welds, so you can instantly see which ones join shaft→casing (bad) versus
   gear→shaft (good).

---

## 4. Fix A (proper, permanent) — repair the SolidWorks mates, re-export

Do this once and every future export imports perfectly.

1. Open the assembly in SolidWorks. In the FeatureManager, expand **Mate** and
   the components tree.
2. For each of the 4 shaft units (see table in §2):
   - Right-click the top item of the unit (e.g. `20mm shaft`) → if the icon
     shows **(f) Fixed**, right-click → **Float**.
   - Expand each subassembly (e.g. a shaft unit saved as a sub-assembly):
     open its own file and make sure nothing inside except the intended
     static parts is Fixed.
3. Mates audit per shaft unit — it must have **exactly**:
   - **1 × Concentric** mate: shaft's cylindrical surface ↔ casing bore.
   - **1 × Coincident** (or Distance) mate: shaft shoulder ↔ casing face.
   - **Nothing else to the casing.** In particular **delete**: second
     Concentric mates, Width, Lock, Angle mates against the housing, and any
     SolidWorks **Gear mate** (the meshing ratio is added in Simscape with
     Gear Constraint blocks — it must not be in the CAD mates).
4. Within each shaft unit, keep gear/shaft bonded (Concentric + Coincident
   to the shaft, plus a key/pin mate — those are fine rigid).
5. **Rebuild (Ctrl+Q)**, check no yellow/red mate errors, **Save**, then
   re-export: **Tools → Simscape Multibody Link → Export → Simscape Multibody**
   (details in `SIMSCAPE_SOLIDWORKS_GUIDE.md` Part 2).
6. Re-import in R2025b: `smimport('Gearbox_Design.xml')`. You should now
   count exactly **4 Revolute Joint** blocks (plus 3 Gear Constraints you add
   per Part 4 of the guide).

> Keep the Multibody Link add-in version matched to your MATLAB release
> (R2025b add-in for R2025b). A mismatch is the other top source of broken
> imports — check **Tools → Add-Ins → Simscape Multibody Link** version against
> `ver` in MATLAB.

## 5. Fix B (patch now, in MATLAB) — turn the bad rigids into Revolute Joints

### 5a. Manual (click-by-click, best for understanding)

For each bad Rigid Transform (shaft-unit ↔ casing):

1. **Delete the Rigid Transform block** (click it, press Delete).
   Note the two frame lines that were connected (which block each side came
   from) — hover a port to see names, or use the `'list'` mode output.
2. Open the Library Browser → **Simscape → Multibody → Joints** → drag a
   **Revolute Joint** into the model near the old block.
3. Connect **L** to the frame line from the casing side, **R** to the frame
   line from the shaft-unit side (L/R order only flips the sign convention —
   be consistent and verify direction after running, §6).
4. Open the Revolute Joint block → **Internal Mechanics**: leave off.
   → **State Targets**: check **Specify Position Target**, value `0` — this
   starts the shaft at the exported (closed) pose, avoiding a "jump" at t=0.
5. **Axis check (critical):** the joint rotates about the frame **Z axis**
   (or the axis selected in the block's **Axis** dropdown if your release
   shows one). The shaft's rotation axis in the exported frames is whatever
   direction the Concentric mate defined. Verify: connect the joint, run the
   model once with Mechanics Explorer open, select the joint → its **Z**
   (blue) axis must lie **along the shaft axis**. If it doesn't:
   insert a **Rigid Transform** between the casing frame and **L** with
   Rotation Method = *Standard Axis*, choose the axis/angle that maps the
   shaft direction onto +Z (e.g. 90° about Y maps X→Z), and Translation
   Method = *None*. Repeat on **R** side with the inverse if needed.
6. Repeat for every bad rigid. For your gate the mandatory one is **J4**
   (output/arm pivot) — J1–J3 also need to be revolute or the gearbox won't
   turn (all 4 are required before adding the Gear Constraints).
7. Then re-add the 3 **Gear Constraint** blocks exactly as in
   `SIMSCAPE_SOLIDWORKS_GUIDE.md` Part 4 (they couple the 4 revolute joints
   into the 70:1 train).

### 5b. Automated (helper script)

```matlab
% 1) see everything that is welded, and what it welds:
fix_rigid_joints('Gearbox_Design', 'list')

% 2) convert the bad ones (name from the list, axis = shaft direction in frames):
fix_rigid_joints('Gearbox_Design', 'fix', ...
                 {'Rigid Transform 17', 'X'; 'Rigid Transform 23', 'X'})
```

The script swaps each listed Rigid Transform for a Revolute Joint, rewires
the same two frame connections, tries to set the rotation axis, saves a copy
(`<model>_fixed.slx`) and prints per-joint next steps. If the axis cannot be
set programmatically it tells you exactly which block to double-click and
what to set (step 5a.5).

## 6. After fixing — 3-minute verification

1. Run the model (nothing actuated yet): **Mechanics Explorer** must show
   `4 DOF` in the status bar (4 revolute joints). If it shows more, something
   got disconnected; fewer = still welded somewhere.
2. Grab the output shaft in Mechanics Explorer (select its revolute joint →
   **Animation** → drag the position slider): the whole arm unit must swing.
3. Then wire actuation + Gear Constraints per
   `SIMSCAPE_SOLIDWORKS_GUIDE.md` Parts 4–5.
4. Direction check: if the arm swings the wrong way for positive torque, swap
   the joint's L/R or add a −1 gain before the joint torque input.
