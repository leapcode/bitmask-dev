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

#define MAXBUFFSIZE 1024

char* const lib = "/lib";
char* const entrypoint = "app";
char* const linkname = "/proc/self/exe";

int main(int argc, char *argv[])
{
    char buf[MAXBUFFSIZE];
    char pth[MAXBUFFSIZE];
    char *dirc, *dname;
	const size_t bufsize = MAXBUFFSIZE + 1;

    argv[0] = entrypoint;
    buf[0] = 0;
    pth[0] = 0;

    readlink(linkname, buf, bufsize - 1);

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
