:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

.. _bitmask_core:

============
Bitmask Core
============

The bitmask core daemon can be launched like this::

  bitmaskd

The command-line program ``bitmaskctl`` and the GUI will launch the
daemon when needed.

Starting the REST service
=========================

If configured to do so, the bitmask core will expose all of the commands
throught a REST API. In bitmaskd.cfg::

  [services]
  web = True


Global API Authentication
=========================

To avoid some kind of attacks, the Bitmask API is protected by a global
authentication token.

The JS API receives this value when the initial entrypoint is loaded for the
first time, in the anchor part of the url.

To authenticate any request to the API, the ``X-Bitmask-Auth`` header has to be
added to it, set to the single value that is initialized during the bitmask
deaemon startup::

  curl -X POST http://localhost:7070/API/mail/status
  unauthorized:bad auth token

  curl -X POST http://localhost:7070/API/mail/status -H 'X-Bitmask-Auth: fae20706aa4f4f98ac0e67996787a370'
  {"result": {"status": "on", "childrenStatus": {"smtp": {"status": "on", "error": null}, "imap": {"status": "on", "error": null}}, "error": null}, "error": null}

This token can be found in ``.config/leap/authtoken``


API Authentication (this section not implemented yet)
======================================================

By default, the resources in the API are protected by an authentication token.

The rationale is that, since the Bitmask core can be used simultaneously by
several users, no single user should be able to interfere with others by
querying for sensible information or disrupting other users' interaction with
running services.

Therefore, there's a small white list of resources that do not
need authentication, based on which is the subset of the API that needs to
provide functionality for the creation of new accounts (the first-run wizard
from the UI perspective).

The local authentication token is sent back in the response for an
authentication call.

This local session token is different from the remote SRP token, although both
are returned together. In the case that the remote SRP authentication with the
provider fails (or with no network connectivity), the backend **should** signal
the error but equally return a local authentication token (this is not
implemented yet, but needs to be done to support an offline mode of operation).

To authenticate any request to the API, the ``Authorization`` header has to be
added to it. You need to pass a ``Token`` field, with a value equal to the
concatenation of the username and the local session token , base64-encoded::


   $ curl -X POST localhost:7070/API/core/stop
   $ Unauthorized

   >>> import base64                                                                                           
   >>> base64.b64encode('user@provider.org:52dac27fcf633b1dba58')
   'dXNlckBwcm92aWRlci5vcmc6NTJkYWMyN2ZjZjYzM2IxZGJhNTg='

   $ curl -X POST localhost:7070/API/core/stop -H 'Authorization: Token dXNlckBwcm92aWRlci5vcmc6NTJkYWMyN2ZjZjYzM2IxZGJhNTg='
   $ {'shutdown': 'ok'}


Resources
========= 

Following is a list of currently available resources and a brief description of
each one. For details click on the resource name.

**By default, all the resources need authentication**. An asterisk next to it
means that it does not need an authentication header.

+------------------------------------+---------------------------------+
| Resource                           | Description                     |
+====================================+=================================+
| ``POST`` :ref:`cmd_core_version` * | Get Bitmask Core Version Info   |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_core_stats` *   | Get Stats about Bitmask Usage   |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_core_status`    | Get Bitmask Status              |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_core_stop`      | Stop Bitmask Core               |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_prov_list` *    | List all providers              |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_prov_create` *  | Create a new provider           |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_prov_read` *    | Get info about a provider       |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_prov_del`       | Delete a given provider         |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_user_list`      | List all users                  |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_user_active`    | Get active user                 |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_user_create` *  | Create a new user               |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_user_update`    | Change the user password        |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_user_auth` *    | Authenticate an user            |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_user_logout`    | End session for an user         |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_keys_list`      | Get all known keys for an user  |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_keys_insert`    | Insert a new key                |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_keys_del`       | Delete a given key              |
+------------------------------------+---------------------------------+
| ``POST`` :ref:`cmd_keys_export`    | Export keys                     |
+------------------------------------+---------------------------------+

.. _cmd_parameters:

Passing parameters
------------------

In all the cases that need data passed as parameter, those will be passed as
JSON-encoded data to the POST.

.. _cmd_core_version:

/core/version
-------------
**POST /core/version**

  Get Bitmask Core Version Info

  **Example request**::

        curl -X POST localhost:7070/API/core/version 

 
  **Example response**::

   {
      "error": null,
      "result":
          {
             "version_core": "0.9.3+185.g59ee6c29.dirty"
          }
   }


.. _cmd_core_stats:

/core/stats
-----------
**POST /core/stats**

  Get Stats about Bitmask Usage

.. _cmd_core_status:

/core/status
------------
**POST /core/status**

  Get Bitmask status

.. _cmd_core_stop:

/core/stop
----------
**POST /core/stop**

  Stop Bitmask core (daemon shutdown).

.. _cmd_prov_list:

/bonafide/provider/list
-----------------------
**POST /bonafide/provider/list**

  List all known providers.

.. _cmd_prov_create:

/bonafide/provider/create
--------------------------
**POST /bonafide/provider**

  Create a new provider.

.. _cmd_prov_read:

/bonafide/provider/read
-----------------------
**POST /bonafide/provider/read**

  Get info about a given provider.

  **Example request**::

  
        curl -X POST localhost:7070/API/bonafide/provider/read -d '["dev.bitmask.net"]'

 
  **Example response**::

   {
   "error": null,         
        "result": {
        "api_uri": "https://api.dev.bitmask.net:4430",
        "api_version": "1",          
        "ca_cert_fingerprint": "SHA256: 0f17c033115f6b76ff67871872303ff65034efe7dd1b910062ca323eb4da5c7e",
        "ca_cert_uri": "https://dev.bitmask.net/ca.crt",
        "default_language": "es",
        "description": {               
            "en": "Bitmask is a project of LEAP",
        }, 
        "domain": "dev.bitmask.net",
        "enrollment_policy": "open",
        "languages": [
            "es"
        ],
        "name": {
            "en": "Bitmask"
        },
        "service": {
            "allow_anonymous": false,
            "allow_free": true,
            "allow_limited_bandwidth": false,
            "allow_paid": false,
            "allow_registration": true,
            "allow_unlimited_bandwidth": true,
            "bandwidth_limit": 102400,
            "default_service_level": 1,
            "levels": {
                "1": {
                    "description": "Please donate.",
                    "name": "free"
                }
            }
        },
        "services": [
            "mx",
            "openvpn"
        ]
    }
   }

 
  **Form parameters**:
        * ``domain`` *(required)* - domain to obtain the info for.

.. _cmd_prov_del:

/bonafide/provider/delete
-------------------------
**POST /bonafide/provider/delete**

  Delete a given provider.


.. _cmd_user_list:

/bonafide/user/list
-------------------
**POST /bonafide/user/list**

  List all the users known to the local backend. 

  **Form parameters**:

  **Status codes**:
        * ``200`` - no error

.. _cmd_user_active:

/bonafide/user/active
---------------------
**POST /bonafide/user/active**

  Get the active user.

.. _cmd_user_create:

/bonafide/user/create
---------------------
**POST /bonafide/user/create**

  Create a new user.

  **Form parameters**:
        * ``username`` *(required)* - in the form user@provider.
        * ``pass`` *(required)* - the username passphrase
        * ``invitecode`` *(optional)* - an optional invitecode, to be used if
          the provider requires it for creating a new account.
        * ``autoconf`` *(optional)* - whether to autoconfigure the provider, if
          we have not seen it before.

  **Status codes**:
        * ``200`` - no error

.. _cmd_user_update:

/bonafide/user/update
---------------------
**POST /bonafide/user/update**

  Change the user password.

  **Form parameters**:
        * ``username`` *(required)* - in the form user@provider
        * ``oldpass`` *(required)* - current password
        * ``newpass`` *(required)* - new password

  **Status codes**:
        * ``200`` - no error

.. _cmd_user_auth:

/bonafide/user/authenticate
---------------------------
**POST /bonafide/user/authenticate**

  Authenticate an user.

  **Form parameters**:

        * ``username`` *(required)* - in the form user@provider
        * ``pass`` *(required)* - passphrase
        * ``autoconf`` *(optional)* - whether to autoconfigure the provider, if
          we don't have seen it before.

  **Status codes**:
        * ``200`` - no error

.. _cmd_user_logout:

/bonafide/user/logout
---------------------
**POST /bonafide/user/logout**

  Logs out an user, and destroys its local session.

.. _cmd_keys_list:

/mail/status
-----------------------
**POST /mail/status

  Get the status of the mail service

  **Example request**::


        curl -X POST localhost:7070/API/mail/status -d '["foobar@mail.bitmask.net"]'


  **Example response**::


   {
     "result": {
       "status": "on",
       "keys": "found",
       "unread": 5,
       "childrenStatus": {
         "keymanager": {
           "status": "on",
           "keys": "found",
           "error": null
         },
         "smtp": {
           "status": "on",
           "error": null
         },
         "incoming": {
           "status": "on",
           "unread": 5,
           "error": null
         },
         "imap": {
           "status": "on",
           "error": null
         }
       },
       "error": null
     },
     "error": null
   }


  **Form parameters**:
        * ``address`` *(required)* - the email address of the account.

  **Values**:

  The possible values for ``status`` are:
       * ``on``
       * ``off``
       * ``starting``
       * ``stopping``
       * ``failed``

  The possible values for the ``keys`` field are:
        * ``null`` - nothing is known about the private key status.
        * ``sync`` - syncing soledad to see if there is a private key.
        * ``generating`` - creating a new private key as none was found.
        * ``found`` - there is a valid private key in KeyManager.


.. _cmd_prov_del:

/keys/list
-------------------
**POST /keys/list**

  Get all keys for an user.

.. _cmd_keys_insert:

/keys/insert/
-------------------
**POST /keys/insert**

  Insert a new key for an user.

.. _cmd_keys_del:

/keys/delete/
-------------------
**POST /keys/delete**

  Delete a key for an user.

.. _cmd_keys_export:

/keys/export/
-------------------
**POST /keys/export**

  Export keys for an user.


