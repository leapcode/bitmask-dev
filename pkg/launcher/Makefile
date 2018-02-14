CC = gcc
CFLAGS = -g -Wall -no-pie -fstack-protector-strong
STRIP = strip

default: bitmask

bitmask.o: bitmask-launcher.c
	$(CC) $(CFLAGS) -c bitmask-launcher.c -o bitmask.o

bitmask: bitmask.o
	$(CC) $(CFLAGS) bitmask.o -o bitmask
	$(STRIP) bitmask
clean:
	-rm -f bitmask.o
	-rm -f bitmask
