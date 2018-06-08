RiseupVPN
---------

This is the Snap package for RiseupVPN. RiseupVPN is a specialized build of
bitmask, that lacks client authentication and is preconfigured to use a single
provider (riseup.net).

In the future, this snap very likely will be maintained in its own repo, and
here we will maintain a snap package for the generic Bitmask client.

At the moment, RiseupVPN has two main components:

- A headless build of bitmask-vpn. This lives in the bitmask-dev repo, it's written
  in twisted + python, and it uses an entrypoint called "anonvpn". This
  entrypoint launches the bitmaskd backend, and tries to launch the
  bitmask-systray too.

- A minimalistic systray, written in golang. This lives in the bitmask-systray repo.


Building
---------

First of all, make sure that the version in the snapcraft.yaml file matches what we're building.
We're following the convention of adding +git to any build that comes after a tag.

Launchpad does up 4 daily builds if code is modified in bitmask-dev repo. We're
building for amd64, i386 and arm8.
If you need to force a build, trigger it by editing the version string in the
snapcraft.yaml file.

For local builds, you can use 'make snap_in_docker'. This builds in a docker
container (provided by snapcraft/snapcore). At this moment, this image is based
in xenial - therefore, a special tag is needed for the gtk3 libs in go.


Releasing
---------

From the snap dashboard, you can see the revisions that are built.
By default, we have riseupvpn-builds configured to upload builds to beta and
edge channels. If you are going to be pushing to edge manually regularly,
please configure the automated builds to push just to beta for some time and
push your builds to edge channel.

To publish a snap, click on "release" from the dashboard, and assign a channel to them.

By convention, if you release to a channel, please release the revision to all
the lower channels too.  (For example, if you release a particular revision to
"candidate", release it also to "beta" and "edge"). 

Do note that the automated builds for different architectures do have different revision
numbers, so when releasing you have to repeat the steps for each platform that
we're building for.

From the command line:

  snapcraft login
  snapcraft status riseup-vpn

  # if we've built a release manually, we have to push it first. it gives us a
  # revision number that we use in the next step.

  snapcraft push riseup-vpn_0.10.6+git_amd64.snap 
  Preparing to push '/home/kali/leap/bitmask-dev/riseup-vpn_0.10.6+git_amd64.snap' to the store.
  Found cached source snap /home/kali/.cache/snapcraft/projects/riseup-vpn/snap_hashes/amd64/b5e9d106c823e3c83fce1ef81ad95d68c33fcada859eeb98233fc766863d39205c192fe5ee53def71c43886e40d3ab5b.
  Generating xdelta3 delta for riseup-vpn_0.10.6+git_amd64.snap.
  Pushing delta /home/kali/leap/bitmask-dev/riseup-vpn_0.10.6+git_amd64.snap.xdelta3.
  Pushing riseup-vpn_0.10.6+git_amd64.snap.xdelta3 [=================================================] 100%
  Processing...|                                                                                                                                                                 
  Ready to release!
  Revision 20 of 'riseup-vpn' created.

  # otherwise I assume that you're just trying to release something
  # that was already built and automatically uploaded.

  # let's publish amd64 to candidate channel and the channels below
  snapcraft release riseupv-vpn 20 candidate
  snapcraft release riseupv-vpn 20 beta
  snapcraft release riseupv-vpn 20 edge

  # and now the i386 build
  snapcraft release riseupv-vpn 19 candidate
  snapcraft release riseupv-vpn 19 beta
  snapcraft release riseupv-vpn 19 edge


Testing
-------

To install a snap published on a specific channel, indicate the channel from the commandline:

  snap install riseup-vpn --classic --edge
  snap install riseup-vpn --classic --beta
  snap install riseup-vpn --classic --candidate
