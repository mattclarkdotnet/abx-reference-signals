# Updating the collection

Keep original recordings separate from subsequent filtering, channel expansion
and sequence assembly. Retain the generation scripts, recipes and measured
results so someone else can understand and reproduce a release.

## Update the file guide and plots

From the repository's top-level directory, after setting up
[the Python environment](scripted/README.md#set-up-the-tools), run:

```sh
uv run --locked python scripted/src/catalogue_readme.py
uv run --locked --group docs python scripted/src/plot_waveforms.py
```

The first command updates `FILES.md` and the README's marked download table from
`catalogue.json`. Edit the generator when changing those generated sections.
The second creates the 2000-pixel-wide PNGs in `docs/waveforms/` from the actual
WAV samples. It checks file hashes and that every channel variant contains the
same samples before sharing one illustration across variants. It leaves audio
unchanged. Inspect the plots for readable labels and clipping before publication.

## Publish a release

Set the version, GitHub repository and release tag in
`scripted/recipes/reference-v1.json` for the collection you are publishing. Rebuild
the outputs, run [validation and script tests](validation/README.md), regenerate
the file guide and plots, and update the README's release baseline and release
page link.

Commit the matching recordings, recipes, generation code, catalogue, checksums,
lockfile and reports before creating the release tag. Publish the six WAVs,
catalogue, checksums, licences, file guide and measurements as GitHub Release
assets. Keep existing release tags and audio assets unchanged; changed audio
belongs in a new release.

Run `uv run --locked python validation/src/verify_downloads.py` after upload to
check that every public asset can be fetched anonymously and matches the local
bytes. Ordinary documentation corrections can be published on the default
branch without changing the audio release.
