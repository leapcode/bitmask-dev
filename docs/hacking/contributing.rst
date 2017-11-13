:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

.. _contributing:

Contributing
============

This project adheres to the `Contributor Covenant 1.2`_. By participating you
are expected to uphold this code. Please report unacceptable behavior to
info@leap.se.

* Fork the code at https://0xacab.org/leap/bitmask-dev. New users may be
  limited in how many forks they can have, so if this is a problem for you,
  file a `support ticket`_ or fork the code from the `github mirror`_.
* Create a merge request on `0xacab`_. If you  forked from the
  `github mirror`_, create your pull request there. They will be subject to
  code review.
* Please base your branch for master, and keep it rebased when you push.
* After review, please squash your commits.

.. _`Contributor Covenant 1.2`: http://contributor-covenant.org/version/1/2/0
.. _`support ticket`: https://0xacab.org/riseup/0xacab/issues
.. _`github mirror`: https://github.com/leapcode/bitmask-dev
.. _`0xacab`: https://0xacab.org/leap/bitmask-dev


Coding conventions
---------------------------------

* Follow pep8 for all the python code.
* Git messages should be informative.
* There is a pre-commit hook ready to be used in the ``docs/hooks`` folder,
  alongside some other hooks to do autopep8 on each commit.

.. include:: ../hooks/leap-commit-template.README
   :literal:

Dependencies
----------------------------------

We try hard not to introduce any new dependencies at this moment. If you really
have to, the packages bitmask depends on have to be specified *both* in the
setup.py and the pip requirements file.

Don't introduce any pinning in the setup.py file, they should go in the
requirements files (mainly ``pkg/requirements.pip``).


Signing your commits
---------------------------------

For contributors with commit access, you **should** sign all your commits. If
you are merging some code from external contributors, you should sign their
commits.

For handy alias for sign and signoff commits from external contributors add to
your gitconfig::

  [alias]
  # Usage: git signoff-rebase [base-commit]
  signoff-rebase = "!GIT_SEQUENCE_EDITOR='sed -i -re s/^pick/e/' sh -c 'git rebase -i $1 && while test -f .git/rebase-merge/interactive; do git commit --amend --signoff --no-edit && git rebase --continue; done' -"

Merging code
---------------------------------

We avoid merge commits into master, they make a very messy history. Put this
in your gitconfig to only allow the merges that can be resolved as a
fast-forward::

  [merge]
  ff = only
