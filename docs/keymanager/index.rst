.. _keymanager:

=================
Keymanager
=================

Keymanager is the Bitmask component that does key management, including generation,
discovery and validation. It is, esentially, a `nicknym`_ client that uses `Soledad`_
as its storage layer.

Keymanager handles the creation of a OpenPGP transparently in user's behalf. When
bootstrapping a new account, keymanager will generate a new key pair. The key
pair is stored encrypted inside soledad (and therefore able to be synced by
other replicas). After generating it, the public key is sent to the provider,
which will replace any prior keys for the same address in its database.

To discover keys for other users, the `nicknym`_ client in keymanager will query
the nicknym server associated with user's provider, and will process the keys
that the server returns. This query has the following form::

  https://nicknym.test.bitmask.net:6425?address=user@example.com

It is up to the the provider's service to determine the sources for the keys.

Keymanager currently implements all the levels defined in the `Transitional Key
Validation`_ spec, although the mechanisms for validation currently in place
only reach level 2 of what's contemplated in the spec.


.. _nicknym: https://leap.se/en/docs/design/nicknym
.. _Soledad: https://leap.se/en/docs/design/soledad
.. _'transitional key validation': https://leap.se/en/docs/design/transitional-key-validation

Sources of public keys
----------------------

Currently Bitmask can discover new public keys from different sources:

* Keys attached to incoming emails. Simple *.asc* attachments with the keys will be
  taken into account, like the ones produced by enigmail.

* OpenPGP header in incoming emails. The only field taken into account is the *url*
  and it will only be used if it's an *https* address from the same domain as the senders email address.

* When sending emails, if the recipient key is not known, Bitmask will ask for the key to its nicknym provider. The nicknym provider will try to discover the key from other nicknym providers. If provider discovery does not bring any results, the key will be fetched from the sks key servers. Note that this *sks discovery mechanism is probably going to be removed at some time in the future as it provides too many unused keys*.

Other methods are planned to be added in the future, like discovery from signatures in emails, headers (autocrypt spec) or other kind of key servers.  


Key expiration dates
--------------------

KeyManager creates the OpenPGP key with the default expiration of gnupg, that currently is 2 years after the key creation. We want keys with expiration date, to be able to roll new ones if the key material get lost.

We will reduce the default expiration lenght in the future. That will require the rest of OpenPGP ecosystem to have good refresh mechanisms for keys, situation that is improving in the last years.

KeyManager extends one year the expiration date automatically two months before the key gets expired.


Implementation: using Soledad Documents
---------------------------------------

KeyManager uses two types of Soledad Documents for the keyring:

* key document, that stores each gpg key.

* active document, that relates an address to its corresponding key.


Each key can have 0 or more active documents with a different email address
each:

::

  .-------------.          .-------------.
  | foo@foo.com |          | bar@bar.com |
  '-------------'          '-------------'
         |                        |     
         |      .-----------.     |     
         |      |           |     |     
         |      |    key    |     |     
         '----->|           |<----'
                |           |     
                '-----------'


Fields in a key document:

* uids

* fingerprint

* key_data

* private. bool marking if the key is private or public

* length

* expiry_date

* refreshed_at

* version = 1

* type = "OpenPGPKey"

* tags = ["keymanager-key"]


Fields in an active document:

* address

* fingerprint

* private

* validation

* last_audited_at

* encr_used

* sign_used

* version = 1

* type = "OpenPGPKey-active"

* tags = ["keymanager-active"]


The meaning of validation, encr_used and sign_used is related to the `Transitional Key Validation`_

.. _Transitional Key Validation: https://leap.se/en/docs/design/transitional-key-validation
