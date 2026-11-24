# CAD downloads

The full STEP is 173,412,748 bytes. The repository contains the complete compressed archive in nine numbered parts under [parts](parts/). Download the repository source ZIP from **Code → Download ZIP** and extract it, or clone the repository. From that local directory, run:

```sh
python tools/get_cad.py --output downloads
```

This verifies all parts, reconstructs the standard ZIP and extracts the verified STEP into `downloads/`. The [manifest](manifest.json) lists byte counts and SHA-256 hashes. Upload the extracted STEP to Fusion. The Python tool uses only the standard library and requires Python 3.11 or later.

## Panel DXFs

- [Stock side, front/rear, and top outlines](stock-panel-dxf/)
- [Solid middle divider](solid-middle-divider.dxf), derived from the 372 × 232.4 mm stock top outside contour with the dryer openings removed. Use 3 mm acrylic as the modeled material thickness.

The full assembly contains the printable accessory and hardware geometry. Use `tools/export_option.py` to export a standalone STEP of one optional subassembly. Check the fit notes before fabrication.
