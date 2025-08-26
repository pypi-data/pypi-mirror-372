# pypi-verify-now

This is a trust-on-first-use (TOFU) solution to the problem of verifying the
build provenance of packages downloaded from PyPI, that is usable _now_ for
brave and/or impatient users that want to experiment with this _immediately or
even sooner_.

## Pre-abandonware

This tool is intended to **never** reach version 1.0. Instead, whenever Pip
starts verifying signatures client-side, this tool will go to version 99.9 and
be end-of-lifed.

## How-to and security considerations

First run the tool in TOFU mode with arguments supported by `pip lock` -- the
arguments will be passed on as-is to `pip-lock`, so you can use `-r` to process
a requirements file, or `--group` to verify packages specified by a PEP735
dependency group, or any other mechanism supported by pip as long as it
generates a lock file:

    TOFU=1 python -m pypi_verify_now --group build

This generates a file called `.provenance.txt`, which for each package lists the
repository URL that's expected to have signed it. If a package is signed, but its
originating repository URL is not recorded here, the package signature will not
be considered valid. The file is expected to be committed to source control, and
any changes to be reviewed.

After this, for example in a CI pipeline, create a build step that runs without TOFU:

    python -m pypi_verify_now --group build

If this ever fails the build, one of the following things happened:

1. A package is being signed from a different URL
2. A package has started uploading signatures to PyPI, but the repo URL isn't yet known
3. A package is no longer signed, but was expected to be signed in `.provenance.txt`
4. A malicious package was somehow uploaded to PyPI

All of these will fail the build. The `.provenance.txt` will need to be updated
in some way.  Removing failing packages from `.provenance.txt` and re-running
with `TOFU=1` will make the tool happy, but ONLY the user can review the
validity of the resulting changes to `.provenance.txt`. If this manual review
doesn't happen, I'm don't think the resulting security posture is meaningfully
better.

## Configuration

Three settings can be configured through passing in environment variables:

- **TOFU=1** (default 0): set to '1' to generate an updated version of the
  provenance file
- **STRICT=1** (default 0): set to '1' to fail if any package is missing a
  signature (unlikely to be usable currently in 2025Q3)
- **FILENAME=...** (default .provenance.txt): path to file where for each
  dependency originating repository URL is configured

## Security warning

For my use case, today, I think this is good enough, or at least better than no
signature verification. My understanding of security, OIDC and SigStore is more
than zero, but still limited. See the license text; "PROVIDED AS-IS" etc.

I expect the PyPA/pip developers to spend a lot more time thinking about this
problem and tackle nuances that I haven't thought about, and that this process
understandably takes longer than the few hours I spent banging out this script,
so it's advisable to evaluate risks accordingly.

### TOC/TOU

There's a Time-of-check/Time-of-use (TOC/TOU) vulnerability. In the small
window between TOC and TOU, this tool could verify one set of packages, and
because Pip can't (yet) install from a lock file, Pip will do the dependency
resolution again, possibly installing a slightly different set of packages.

## Links

- https://docs.pypi.org/trusted-publishers/
- https://docs.pypi.org/attestations/
- https://peps.python.org/pep-0740/ - PEP 740 - Index support for digital attestations
- https://peps.python.org/pep-0751/ - PEP 751 - A file format to record Python dependencies for installation reproducibility
- https://discuss.python.org/t/ideas-for-client-side-package-provenance-checks/64679
- https://blog.trailofbits.com/2024/11/14/attestations-a-new-generation-of-signatures-on-pypi/
- https://docs.pypi.org/api/integrity/

Talk from PyCon 2025:

- https://us.pycon.org/2025/schedule/presentation/76/
- https://yossarian.net/res/pub/pycon-2025.pdf
- https://www.youtube.com/watch?v=MsY5k1wLJpI
