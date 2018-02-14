/*
 * bitmask-launcher.c
 *
 * part of the bitmask bundle.
 * execute main entrypoint in a child folder inside the bundle.
 *
 * (c) LEAP Encryption Access Project, 2016-2018.
 * License: GPL.
 *
*/

#include <unistd.h>
#include <stdlib.h>
#include <libgen.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#define MAXBUFSIZE 1024

char* const lib = "/lib";
char* const entrypoint = "bitmask";
char* const linkname = "/proc/self/exe";

int main(int argc, char *argv[])
{
    char buf[MAXBUFSIZE];
    char pth[MAXBUFSIZE];
    char *dirc, *dname;

    argv[0] = entrypoint;
    buf[0] = 0;
    pth[0] = 0;

    readlink(linkname, buf, MAXBUFSIZE);

    dirc = strdup(buf);
    dname = dirname(dirc);
    strncat(pth, dname, strlen(dname));
    strncat(pth, lib, strlen(lib));

    if (chdir(pth) < 0)
    {
        fprintf(stderr, "error: %s\n", strerror(errno));
    }
    execv(entrypoint, argv);
}
