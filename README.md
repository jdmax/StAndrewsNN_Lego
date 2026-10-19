# St. Andrew's Episcopal Church, Newport News: minifig-scale LEGO nave

An interactive, step-by-step building guide for a LEGO model of the nave of St. Andrew's Episcopal Church in Newport News, Virginia.

**View it:** open `index.html`, or browse the GitHub Pages site for this repository.

- About 10,900 pieces on eight 32 x 32 baseplates (51 x 102 cm), 135 build steps
- Lift-off roof modules to show the interior: pews, chancel, reredos, choir loft and glulam ribs
- `st_andrews_nave.mpd`: the model in LDraw format. Opens in BrickLink Studio, LDView or LeoCAD, with one submodel per section
- `st_andrews_bricklink.xml`: parts list for a BrickLink wanted list (Wanted > Upload)

## Publishing with GitHub Pages

1. Put these files at the root of a repository (keep `.nojekyll`).
2. Settings > Pages > Build and deployment: Source "Deploy from a branch", branch `main`, folder `/ (root)`.
3. The site appears at `https://<your-user>.github.io/<repo>/` after a minute or two.

The page loads three.js from public CDNs and needs no build step.

## Regenerating the model

`generator/` holds the Python that designs the model on a stud grid and writes the LDraw file and page.
It needs `numpy` and a copy of the LDraw parts library (set `ROOT` in `ldlib.py`).

```
python3 build.py         # design + collision check
python3 check.py         # every part clutched to the baseplates?
python3 verify_ldraw.py  # placements match the real part geometry
python3 export.py        # writes out/*.mpd, out/*.xml, out/data.json
python3 make_page.py     # writes out/st_andrews_build.html
```

Dimensions come from a photo-based massing model and are estimates.
LEGO is a trademark of the LEGO Group, which does not sponsor or endorse this project.
