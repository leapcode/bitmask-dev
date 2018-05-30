RiseupVPN
---------

This is the Snap package for RiseupVPN.

In the future, this snap very likely will be maintained in its own repo, and
here we might maintain a snap package for the Bitmask client.

At the moment, RiseupVPN has two main components:

- A headless build of bitmask-vpn. This lives in the bitmask-dev repo, it's written
  in python twisted, and it uses an entrypoint called "anonvpn". This
  entrypoint launches the bitmaskd backend, and tries to launch the
  bitmask-systray too.

- A minimalistic systray, written in golang. This lives in the bitmask-systray repo.


Releasing
---------
From the snap dashboard, you can see the revisions that are built. Up to now,
the revisions are not automatically released (this might change soon).

To publish them, click on "release" from the dashboard, and assign a channel to them.

By convention, if you release to a channel, please release the revision to all the lower channels too.
(For example, if you release a particular revision to "candidate", release it
also to "beta" and "edge"). 

Do note that the builds for different architectures do have different revision
numbers, so when releasing you have to repeat the steps for each platform that we're building for.

From the command line:

  snapcraft login
  snapcraft status riseup-vpn

  # let's publish amd64 to candidate channel and the channels below
  snapcraft release riseupv-vpn 15 candidate
  snapcraft release riseupv-vpn 15 beta
  snapcraft release riseupv-vpn 15 edge

  # and now the i386 build
  snapcraft release riseupv-vpn 14 candidate
  snapcraft release riseupv-vpn 14 beta
  snapcraft release riseupv-vpn 14 edge



Testing
-------

To install a snap published on a specific channel, indicate the channel from the commandline:

  snap install riseup-vpn --classic --edge
  snap install riseup-vpn --classic --beta
  snap install riseup-vpn --classic --candidate
