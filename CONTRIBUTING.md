# Updating the collection

Keep original recordings separate from filtering, channel expansion and sequence
assembly. Retain recipes, generation code and measured results for each release.

## Update the file guide and plots

Set up the [Python environment](scripted/README.md#set-up-the-tools), then run
from the repository's top-level directory:

```sh
uv run --locked python scripted/src/catalogue_readme.py
uv run --locked --group docs python scripted/src/plot_waveforms.py
```

The first command generates `FILES.md` and the README download table from
`catalogue.json`. Edit the generator to change those sections.

The second creates 2000-pixel-wide PNGs in `docs/waveforms/` using Matplotlib from
the optional `docs` dependency group. Plots use the WAV samples: overviews retain
minimum and maximum values in each interval, and close-ups show individual
samples. The script checks hashes and channel equality before sharing a plot
across variants. Review labels, spacing and clipping before publication.

## Publish a release

Set the version, repository and release tag in `scripted/recipes/reference-v1.json`.
Generate the files, run [validation and tests](validation/README.md), and update
the file guide, plots, [generation baseline](scripted/README.md#release-generation-baseline)
and README release link.

Commit the recordings, recipes, code, catalogue, checksums, lockfile and reports,
then tag that commit. Publish the six WAVs, catalogue, checksums, licences, file
guide and measurements as GitHub Release assets. Use a new release for changed
audio; preserve existing release tags and assets.

Run `uv run --locked python validation/src/verify_downloads.py` after upload.
Publish documentation corrections on the default branch.
