0.0.19 (2025-08-28)
===================

New Features
------------

- Stray light models generate more quickly using less memory (`#568 <https://github.com/punch-mission/punchbowl/pull/568>`__)
- Speeds up pointing determination by pre-computing a KDTree of distances instead of doing a search over all points. (`#570 <https://github.com/punch-mission/punchbowl/pull/570>`__)


Bug Fixes
---------

- Fix LQ CTM to run from Q* input files. (`#563 <https://github.com/punch-mission/punchbowl/pull/563>`__)
- Set DATE for stray light models (`#568 <https://github.com/punch-mission/punchbowl/pull/568>`__)
- Avoid crash in reprojection if input pixels map to NaN in output frame (`#569 <https://github.com/punch-mission/punchbowl/pull/569>`__)


Documentation
-------------

- Consolidates old and new changelogs. (`#585 <https://github.com/punch-mission/punchbowl/pull/585>`__)


Internal Changes
----------------

- Speed up L1_early if not alignment or Q file is needed (`#562 <https://github.com/punch-mission/punchbowl/pull/562>`__)
- `estimate_stray_light` reports file paths that cause loading errors. (`#564 <https://github.com/punch-mission/punchbowl/pull/564>`__)


0.0.18 (2025-08-06)
===================

Breaking Changes
----------------

- Where flows allowed an input file to be provided as a ``Callable`` that returned the required file, those flows now expect an object subclassing `DataLoader`. (`#538 <https://github.com/punch-mission/punchbowl/pull/538>`__)
- The L1 flow has been split into 'early' and 'late' phases. Early writes an X{MZPR} file and, for clear inputs, a QR file. Late writes a CR or P{MZP}. (`#554 <https://github.com/punch-mission/punchbowl/pull/554>`__)
- In stray light subtraction, mismatches in observatory or polarization state are now an error, not a warning. (`#554 <https://github.com/punch-mission/punchbowl/pull/554>`__)


New Features
------------

- Stray light models have their date_obs set to the provided reference time and require much less RAM to generate. (`#538 <https://github.com/punch-mission/punchbowl/pull/538>`__)
- Implements second order square root decoding table, using the technique from DeForest et al 2022. (`#550 <https://github.com/punch-mission/punchbowl/pull/550>`__)
- Stray light models can be interpolated or extrapolated to the image time. It will use either DATE-AVG, DATE-BEG, or DATE-END of the stray light models as the reference time for the models, so that in the quickpunch case, a 6-hour isn't extrapolated for days. (`#554 <https://github.com/punch-mission/punchbowl/pull/554>`__)
- Stray light models are written with DATE-OBS set to the reference time, DATE-AVG  set to the mean of the input files' DATE-OBS, and DATE-{BEG,END} set to the earliest/latest input DATE-OBS. (`#554 <https://github.com/punch-mission/punchbowl/pull/554>`__)


Bug Fixes
---------

- Skips PCA testing on macOS and improves git handling of test temporary sample files. (`#546 <https://github.com/punch-mission/punchbowl/pull/546>`__)
- The PSF dilation was too small and resulting in artifacts. This expands it from 1 to 3 dilations. (`#547 <https://github.com/punch-mission/punchbowl/pull/547>`__)
- Provenance wasn't getting populated. This makes sure it's fully filled for all products. (`#551 <https://github.com/punch-mission/punchbowl/pull/551>`__)
- NFI pointing was consistently failing. This improves it by changing the alignment search parameters and allowing astrometry.net to fail by falling back on the spacecraft WCS. (`#557 <https://github.com/punch-mission/punchbowl/pull/557>`__)


Documentation
-------------

- Improves the documentation about file versions. (`#553 <https://github.com/punch-mission/punchbowl/pull/553>`__)
- Updates data query example notebook to streamline download and execution. (`#556 <https://github.com/punch-mission/punchbowl/pull/556>`__)


Internal Changes
----------------

- The ``on_completion`` debugging hook is only set if debugging is enabled, avoiding log messages after every Task run when debugging isn't enabled. (`#538 <https://github.com/punch-mission/punchbowl/pull/538>`__)
- The filler WCS written in stray light models is now a valid, though arbitrary, WCS. (`#538 <https://github.com/punch-mission/punchbowl/pull/538>`__)
- Turns off ruff's EM101 check. (`#558 <https://github.com/punch-mission/punchbowl/pull/558>`__)
- Speedups to alignment and to de-spiking with many flows running at once. (`#559 <https://github.com/punch-mission/punchbowl/pull/559>`__)
- Disables Prefect task result caching (`#560 <https://github.com/punch-mission/punchbowl/pull/560>`__)

Version 0.0.17: July 23, 2025
=============================

- Adds docs button to view source in https://github.com/punch-mission/punchbowl/pull/526
- Fixes constant deficient pixel map creation in https://github.com/punch-mission/punchbowl/pull/522
- Adds a quickfix for parsing input filenames for the calibration CLI tool in https://github.com/punch-mission/punchbowl/pull/516
- Adds docstring to PSF function in https://github.com/punch-mission/punchbowl/pull/519
- Reduces memory usage of stray light model generation in https://github.com/punch-mission/punchbowl/pull/525
- Updates vignetting calibration command in https://github.com/punch-mission/punchbowl/pull/523
- Implements rolling stray light models in https://github.com/punch-mission/punchbowl/pull/531
- Add Limit/LimitSet classes in LQ PCA; support batched PCA; add seam blending for quartered PCA in https://github.com/punch-mission/punchbowl/pull/529
- Changed docstring in vignette.py #503 and transpose in destreak.py #487 in https://github.com/punch-mission/punchbowl/pull/530
- Output stray light models as NDCubes in https://github.com/punch-mission/punchbowl/pull/533
- Rewrites pointing refinement in https://github.com/punch-mission/punchbowl/pull/524
- Only pull file version from first file for LQ in https://github.com/punch-mission/punchbowl/pull/534/

Version 0.0.16: July 3, 2025
============================

- Fixed vignetting docstring in https://github.com/punch-mission/punchbowl/pull/510
- Relabels CCD halves in https://github.com/punch-mission/punchbowl/pull/493
- Adds documentation for data versions and anomalies in https://github.com/punch-mission/punchbowl/pull/495
- Separates LQ CNN and CTM into separate flows in https://github.com/punch-mission/punchbowl/pull/507
- Avoid incorrectly coping some metadata from L0 to L1, and update PIPEVRSN in https://github.com/punch-mission/punchbowl/pull/508
- Avoids mutating input cubes in `write_ndcube_to_fits` in https://github.com/punch-mission/punchbowl/pull/502
- Ensures inf values in uncertainty layers roundtrip through compression in https://github.com/punch-mission/punchbowl/pull/506
- Allow writing out L1s with stray light included in https://github.com/punch-mission/punchbowl/pull/509
- Unified L2 clear and polarized flows in https://github.com/punch-mission/punchbowl/pull/513
- Sets FILEVRSN in L2 flow in https://github.com/punch-mission/punchbowl/pull/514
- Removes unused prefect test decorator in https://github.com/punch-mission/punchbowl/pull/515
- Creates calibration creation CLI and adds hash functions as needed in https://github.com/punch-mission/punchbowl/pull/497

Version 0.0.15: June 4, 2025
============================

- Restricts the mask for NFI pointing refinement in https://github.com/punch-mission/punchbowl/pull/486
- Removes VAN product code from documentation in https://github.com/punch-mission/punchbowl/pull/489
- Changes default float writing dtype to 32 bit instead of 64 bit in https://github.com/punch-mission/punchbowl/pull/485

Version 0.0.14: June 3, 2025
============================

- Adds DOI for level 0 data products in https://github.com/punch-mission/punchbowl/pull/481
- Many processing improvements in https://github.com/punch-mission/punchbowl/pull/482

Version 0.0.13: May 22, 2025
============================

- F-corona detrending, fixes for L2 FILEVRSN and DATE-OBS, and use header's gain and exposure time in https://github.com/punch-mission/punchbowl/pull/455
- Suppress CROTA warnings in load_ndcube_from_fits in https://github.com/punch-mission/punchbowl/pull/456
- Corrects the sign in p angle when converting between helio and celestial in https://github.com/punch-mission/punchbowl/pull/454
- Changes to astroscrappy for despiking in https://github.com/punch-mission/punchbowl/pull/462
- Supports floating-point COMPBITS values in https://github.com/punch-mission/punchbowl/pull/461
- Adds data overview documentation in https://github.com/punch-mission/punchbowl/pull/458
- Flags uncertainty of saturated pixels in https://github.com/punch-mission/punchbowl/pull/471
- Prepares changes for QuickPUNCH creation in https://github.com/punch-mission/punchbowl/pull/473/f
- Improve documentation for despiking in https://github.com/punch-mission/punchbowl/pull/470
- Manages square root decoding table value overflow in https://github.com/punch-mission/punchbowl/pull/469
- LQ PCA filtering, fix for NormalizedMetadata str values, and LQ FILEVRSN propagation in https://github.com/punch-mission/punchbowl/pull/472

Version 0.0.12: May 12, 2025
============================

- L1 speedups, L2 reprojection fix, and accepting ints for `float` fields in `NormalizedMetadata` in https://github.com/punch-mission/punchbowl/pull/435
- Allows custom path for ffmpeg in quicklook movies in https://github.com/punch-mission/punchbowl/pull/438
- Allows L1 calibration files to be passed in as callables in https://github.com/punch-mission/punchbowl/pull/426
- Speedups to L1 production in https://github.com/punch-mission/punchbowl/pull/426
- Adds metadata to output jpeg2000 files in https://github.com/punch-mission/punchbowl/pull/433
- Checks for square root decompression in L1 processing in https://github.com/punch-mission/punchbowl/pull/434
- Modifies metadata for header / unit compliance in https://github.com/punch-mission/punchbowl/pull/427
- Updates L0 header generation in https://github.com/punch-mission/punchbowl/pull/444
- Doesn't set SC location for F-corona models, improvements to msb_to_dn and compute_noise, and F-corona modeling improvements in https://github.com/punch-mission/punchbowl/pull/441
- Sets quicklook images to grayscale by default, with a flag for color rendering in https://github.com/punch-mission/punchbowl/pull/447

Version 0.0.11: Apr 14, 2025
============================

- Changes error message for default overwriting in https://github.com/punch-mission/punchbowl/pull/420
- Updates code to match new regularizepsf version in https://github.com/punch-mission/punchbowl/pull/413
- Adds the scale factor to the square root decoding in https://github.com/punch-mission/punchbowl/pull/418
- Standardize square root decoding in https://github.com/punch-mission/punchbowl/pull/421
- Fixes to ensure vignetting correction runs in https://github.com/punch-mission/punchbowl/pull/423
- Adds square root decoding example notebook in https://github.com/punch-mission/punchbowl/pull/425

Version 0.0.10: Apr 2, 2025
===========================

- Changes so that vignetting is a separate step in the pipeline.
- Switches to use Prefect Dask Task Runner in https://github.com/punch-mission/punchbowl/pull/387
- Changes level 0.5 to level H in https://github.com/punch-mission/punchbowl/pull/388
- Fixes WCS conversions in https://github.com/punch-mission/punchbowl/pull/390
- Parallelize F corona model building in https://github.com/punch-mission/punchbowl/pull/392
- Fixes starfield polarization; checks times are in UTC in https://github.com/punch-mission/punchbowl/pull/328#pullrequestreview-2726230483
- Fixes issues with calibration metadata in https://github.com/punch-mission/punchbowl/pull/404
- Adds quicklook movie generation in https://github.com/punch-mission/punchbowl/pull/391
- Computes gain on two detector halves separately in https://github.com/punch-mission/punchbowl/pull/406
- Fixes a keyword typo in omniheader in https://github.com/punch-mission/punchbowl/pull/407
- Creates a uses a custom PUNCH flow in prefect in https://github.com/punch-mission/punchbowl/pull/409
- Changes default of NDCube writing to prohibit overwriting in https://github.com/punch-mission/punchbowl/pull/408

Version 0.0.9: Feb 28, 2025
===========================

* adds zspike blurring and parameterization by @lowderchris in https://github.com/punch-mission/punchbowl/pull/345
* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci in https://github.com/punch-mission/punchbowl/pull/349
* rename PUNCH io module by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/350
* Adds sphinx gallery by @lowderchris in https://github.com/punch-mission/punchbowl/pull/352
* make binder work by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/356
* Configure binder by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/357
* Rename example gallery by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/358
* Update binder.yaml by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/360
* Separate quick punch by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/361
* specify codecov path by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/362
* Update issue templates by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/364
* Update README.md by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/365
* update copyright year by @jmbhughes in https://github.com/punch-mission/punchbowl/pull/367

Version 0.0.8: Dec 19, 2024
===========================

- Fix stellar by @jmbhughes in #344
- Updates for V4 RFR2 by @jmbhughes in #346

Version 0.0.7: Dec 11, 2024
===========================

- Reproject starfield sample and uncertainty in one fell swoop by @svank in #323
- PUNCH user guide by @lowderchris in #316
- Unpack uncertainties faster by @svank in #324
- Make mosaics faster w/ bounding boxes by @svank in #326
- Ignore warnings in unpacking uncertainty by @svank in #329
- Be a little more accurate/safe with bounding boxes by @svank in #327
- Fully implement previous change to bounding boxes by @svank in #332
- adds thresholding to spike value replacement by @lowderchris in #331
- Metadata check by @lowderchris in #330
- Fixes merging, improves f corona modeling by @jmbhughes in #333
- adds DOI badge by @lowderchris in #334
- Turn velocity plot test into a figure test by @svank in #325
- Better f corona by @svank in #335
- Document python tutorials by @lowderchris in #336
- Change despike settings by @svank in #338
- WCS array shape by @lowderchris in #337
- adds wcs keywords to ignore to prevent duplication by @lowderchris in #340
- Create starfield estimates that are less distorted by @svank in #339
- remove broken link by @jmbhughes in #341
- adds file provenance extname and test by @lowderchris in #342
- Quicklook generation by @jmbhughes in #343

Version 0.0.6: Nov 22, 2024
===========================

- Improve calculation of pixel areas by @svank in #306
- November 17th Mega Update by @jmbhughes in #310
- Confirm l2 l3 tests by @jmbhughes in #311
- flow tracking by @lowderchris in #308
- Update .pre-commit-config.yaml by @jmbhughes in #315
- Reusable celestial reprojections by @svank in #309
- Large prep for End2End by @jmbhughes in #317
- fix import by @jmbhughes in #318
- When generating WCSes, set NAXIS/array_shape/etc. by @svank in #320
- Faster star subtraction by @svank in #319
- Updated Level2/polarization by @s0larish in #322

Version 0.0.5: Nov 13, 2024
===========================

- automatically converts metafields by @jmbhughes in #305

Version 0.0.4: Nov 13, 2024
===========================

- add debug mode by @jmbhughes in #290
- fix call of remove starfield by @jmbhughes in #292
- copy over estimate stray light by @jmbhughes in #294
- update low noise generation by @jmbhughes in #295
- Improve f corona flow generation by @jmbhughes in #296
- adds visualization core by @jmbhughes in #297
- flips quicklook data vertically to the expected spatial orientation by @lowderchris in #300
- Prep work for secondary starfield removal, plus fix for F-corona estimation by @svank in #301
- Work fast! Clean up many issues. by @jmbhughes in #302
- adds new get method to normmeta by @jmbhughes in #304

Version 0.0.3: Nov 2, 2024
==========================

- Fixes figure in intro.rst by @jmbhughes in #281
- add file hashing by @jmbhughes in #276
- Delete docs/requirements.txt by @jmbhughes in #284
- Delete .github/workflows/docs.yaml by @jmbhughes in #285
- fix versions in docs by @jmbhughes in #286
- Adds polarref keyword by @jmbhughes in #277
- add new f corona model generation algorithm by @jmbhughes in #287
- update psf to new regularizepsf by @jmbhughes in #289

Version 0.0.2: Nov 1, 2024
==========================

- Bug fix

Version 0.0.1: Nov 1, 2024
==========================

- First release
