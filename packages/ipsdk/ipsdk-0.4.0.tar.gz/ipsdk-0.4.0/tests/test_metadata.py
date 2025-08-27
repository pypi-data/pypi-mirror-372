# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ipsdk import metadata


def test_exists():
    for item in ("author", "version", "name"):
        assert getattr(metadata, item) is not None
        assert isinstance(getattr(metadata, item), str)
