export GOPATH=/srv/go
export CGO_CPPFLAGS="-I/usr/include"
export CGO_LDFLAGS="-L/usr/lib -L/usr/lib/z86_64-linux-gnu -lzmq -lpthread -lsodium -lrt -lstdc++ -lm -lc -lgcc"

echo "[+] building systray deps"
go get -a 0xacab.org/leap/bitmask-systray
cd /src/leap && git clone --depth 1 --single-branch --branch master https://0xacab.org/leap/bitmask-systray
echo "[+] building systray"
cd bitmask-systray && go build .
cp -r /src/leap/bitmask-systray/bitmask-systray /dist
