.. _release-checklist:

Bitmask Release Checklist
=========================

New resources
-------------
If there are new resources in the qt app (icons), you need to make sure that they've been included in the packaged resource.
You'll need to install ``pyqt5-dev-tools``, and execute ``make qt-resources``.

CI check
--------
* [ ] Check that all tests are passing!
* [ ] Fix any broken tests.

Version bumps and Tagging
-------------------------
* [ ] Update pkg/next-release
* [ ] Update release-notes.rst in leap.bitmask if needed.
* [ ] Update version in bitmask_client/pkg/linux/bitmask-root if needed.

* [ ] Tag everything. Should be done for the following packages, in order:
* [ ] 1. leap.common
* [ ] 3. leap.soledad
* [ ] 5. leap.bitmask
* [ ] 6. leap.mx

* [ ] git fetch origin
* [ ] git tag -l, and see the latest tagged version (unless it's not a minor version bump, in which case, just bump to it)
* [ ] export version: export RELEASE=0.9.0
* [ ] (maybe) cherry-pick specific commits
* [ ] (maybe) add special fixes for this release
* [ ] Review pkg/requirements.pip for everything, update if needed (that's why the order).
  - See whatever has been introduced in changes/VERSION_COMPAT
  - Reset changes/VERSION_COMPAT
  - Bump all the leap-requirements altogether.
* [ ] git commit -am "Update requirements file"
* [ ] git commit -S -m "[pkg] Update changelog"
* [ ] git tag --sign $RELEASE -m "Tag version $RELEASE"
* If everything went ok, push the tag.
* [ ] cd ui && make dist-build && make dist-upload

Bundles
-------
* [ ] Build and upload bundles:
      [ ] make bundle_in_docker
* [ ] Sign: make pyinst-sign
* [ ] Upload bundle and signature to downloads.leap.se/client/<os>/Bitmask-<os>-<ver>.(tar.bz2,dmg,zip)
* [ ] make pyinst-upload
* [ ] Update symbolic link for latest upload and signature:
* [ ] ~/public/client/Bitmask-<os>-latest
* [ ] ~/public/client/Bitmask-<os>-latest.asc

Debian packages
---------------
* [ ] update changelog
* [ ] upload staging packages to release component

Pypi upload
---------------
* [ ]  python setup.py sdist upload --sign -i kali@leap.se -r pypi

Announcing
---------------
* [ ] Announce (use release-notes.rst)
 * [ ] Mail leap@lists.riseup.net
 * [ ] Twitter
 * [ ] Gnusocial
 * [ ] Post in leap.se
