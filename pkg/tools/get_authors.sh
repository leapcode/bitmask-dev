#!/bin/sh
#
# To de-duplicate dontibutors who committed with different email addresses / names you can link
# ~/.mailmap to the .mailmap in the `secrets` repo.
# You need to tell git where to find it:
#
#     git config --global mailmap.file ~/.mailmap
#
# After this just run `./get_authors.sh`.

git log --use-mailmap --format='%aN <%aE>' | awk '{arr[$0]++} END{for (i in arr){print arr[i], i;}}' | sort -rn | cut -d' ' -f2- | sort
