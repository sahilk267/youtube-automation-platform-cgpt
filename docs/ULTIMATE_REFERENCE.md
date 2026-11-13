# Ultimate v3 Edition — exact reconstruction from Git

**Why an overlay?** Launch v3, Ultimate v3 and Combined v3 are separate versioned *design documents*, but must share a **single runtime application**. A byte-level comparison of original 250-file Ultimate and Combined v3 ZIPs found only **six changed files, one Ultimate-only file, and one Combined-only file**. Duplicating hundreds of unchanged files would make future maintenance confusing.

- Combined full design snapshot: [`spec/combined-v3/`](../spec/combined-v3/)
- Launch design snapshot: [`spec/launch-v3/`](../spec/launch-v3/)
- Ultimate exact changed/added source files: [`spec/ultimate-v3-overlay/`](../spec/ultimate-v3-overlay/)
- Ultimate overlay manifest: [`spec/ultimate-v3-overlay/DELTA_MANIFEST.json`](../spec/ultimate-v3-overlay/DELTA_MANIFEST.json) with SHA-256 hashes **for all 250 expected Ultimate files**.

### Reconstruct the exact historical Ultimate specification

From root of a Git clone with Python 3.12:


default output is Git-ignored under `outputs/`:

```powershell
py -3.12 tools\materialize_ultimate.py
```

Or explicit folder:

```powershell
py -3.12 tools\materialize_ultimate.py --output .\outputs\ultimate-v3-design
```

The tool copies Combined spec files, removes Combined-only migration plan, replaces edition-specific documents/registries, and then **hash-verifies every one of the 250 Ultimate files** against the original Ultimate ZIP snapshot. It fails rather than silently accepting altered/missing files.

This does **not** rebuild the old 394KB Ultimate ZIP byte-for-byte (ZIP compression/entry order may differ); it reconstructs its full **file contents**. It is a specification, NOT 12 runnable applications or automatic AI video engines. The canonical Python runtime stays in root `app/`.
