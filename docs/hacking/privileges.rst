.. _privileges:

Privilege handling
==================

For launching VPN and the firewall, Bitmask needs to run with administrative
privileges.  In linux, ``bitmask_root`` is the component that runs with root
privileges. We currently depend on ``pkexec`` and ``polkit`` to execute it as
root. In order to do that, Bitmask needs to put some policykit helper files in a
place that is root-writeable.

If you have installed Bitmask from some distro package, these folders should be
already in place. If you're running the Bitmask bundles, the first time you will
be prompted to authenticate to allow these helpers to be copied over (or any
time that these helpers change).

However, if you're running bitmask in a headless environment, you will want to
copy the helpers manually, without involving pkexec. To do that, use::

  sudo `which bitmask_helpers` install 

You can also uninstall them::

  sudo `which bitmask_helpers` uninstall 
