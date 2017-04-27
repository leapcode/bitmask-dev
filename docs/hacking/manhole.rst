.. _manhole:

The manhole HowTo
-------------------------------------------------

Troubles with Bitmask Daemon? Don't panic! Just SSH into it

If you want to inspect the objects living in your application memory, in
realtime, you can ssh into it.

For that, you must add the following section to your ``bitmaskd.cfg``
configuration file::

  [manhole]
  user = bitmask
  passwd = <yoursecret>
  port = 22900


And then you can ssh into your application::

  ssh bitmask@localhost -p 22900

Did I mention how *awesome* twisted is?? ``:)``
