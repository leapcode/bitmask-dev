:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

.. _mail:

Bitmask Mail
================================
*decentralized and secure mail delivery and synchronization*

This is the documentation for the ``leap.mail`` module. It is a `twisted`_
module, hanging from the ``leap.bitmask`` namespace, that allows to receive, process, send and access existing messages using the `LEAP`_ platform.

One way to use this library is to let it launch two standard mail services,
``smtp`` and ``imap``, that run as local proxies and interact with a remote
``LEAP`` provider that offers *a soledad syncronization endpoint* and receives 
the outgoing email. This is what `Bitmask`_ client does.

From the mail release 0.4.0 on, it's also possible to use a protocol-agnostic email
public API, so that third party mail clients can manipulate the data layer. This
is what the awesome MUA in the `Pixelated`_ project is using.

From release 0.10 on, the Bitmask Bundles will also ship a branded version of
the Pixelated User Agent, that will be served locally. This will be one of the
recommended ways of accessing the user emails. The other will be Thunderbird, by
using the `Bitmask Thunderbird Extension`_.

Note that this used to be a standalone python package, under the ``leap.mail``
namespace. It was merged into bitmask repo, so it now lives in the
``leap.bitmask.mail`` namespace. The `legacy repo`_ will no longer be updated.

.. _`twisted`: https://twistedmatrix.com/trac/
.. _`LEAP`: https://leap.se/en/docs
.. _`Bitmask`: https://bitmask.net/en/features#email
.. _`Pixelated`: https://pixelated-project.org/
.. _`legacy repo`: https://github.com/leapcode/leap_mail/
.. _`Bitmask Thunderbird Extension`: https://addons.mozilla.org/en-US/thunderbird/addon/bitmask/

How does Bitmask Mail work?
----------------------------

All the underlying data storage and sync is handled by a library called
`soledad`_, which handles encryption, storage and sync. Based on `u1db`_,
documents are stored locally as local ``sqlcipher`` tables, and syncs against
the soledad sync service in the provider.

OpenPGP key generation, discovery, validation, and keyring management are
handled by the ``leap.bitmask.keymanager`` module.


.. _`Soledad`: https://leap.se/en/docs/design/soledad
.. _`u1db`: https://en.wikipedia.org/wiki/U1DB

The life cycle of a LEAP Email
------------------------------

See :ref:`the life cycle of a leap email <mail_journey>` for an overview of the life cycle
of an email through ``LEAP`` providers.


Data model
--------------------

.. TODO clear document types documentation.

The data model at the present moment consists of several *document types* that
split email into different documents that are stored in ``Soledad``. The idea
behind this is to keep clear the separation between *mutable* and *inmutable*
parts, and still being able to reconstruct arbitrarily nested email structures
easily.

Authentication
---------------------

Currently, IMAP and SMTP are twisted services that are binded to ``localhost``.
These services be initialized by the bitmask.core daemon, but they are not tied
to any user session. When an use attempts to log in to those services, a
``twisted.cred`` pluggable authentication plugin will try to lookup a ``mail
token`` that is stored inside the soledad encrypted storage.

From within the cli, you can get the mail token once you are authenticated
with::

  bitmaskctl mail get_token

When launched, the bitmaskd daemon writes the tokens for each account to a file
inside the folder named ``/tmp/bitmask_tokens``, and this is where the
Thunderbird Extension reads them from.


Pixelated user agent
----------------------

From the 0.9.5 release, bundles are shipping the Pixelated User Agent. Until
some merge requests (dealing with packaging of the js resources) are merged
upstream, you will need to install pixelated user agent from leap's repo::

  pip install pixelated_www pixelated_user_agent --find-links https://downloads.leap.se/libs/pixelated/

Pixelated also needs a couple of extra dependencies::

  pip install whoosh chardet requests==2.11.1




Mail development resources
--------------------------

Some old notes that might help you while developing or debugging bitmask mail
issues.

.. toctree::

   hacking

