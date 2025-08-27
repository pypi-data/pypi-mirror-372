# We have multiple modules under the `furiosa` namespace,
# so the namespace should have no `__init__.py`.
# We still need type stubs, so we do have a `furiosa` directory in this crate
# and this unfortunately confuses maturin and it thinks this is a mixed Rust-Python project.
# Maturin then complains about a missing `__init__.py` and refuses to build.
#
# This file works around this issue, because while this is not documented,
# the current version of maturin does skip the check if `__init__.pyi` does exist:
# https://github.com/PyO3/maturin/blob/7a32907/src/project_layout.rs#L382
