#!/bin/bash

# This is the solver --- needs to be obtained from https://www.hsl.rl.ac.uk/ipopt/
COINHSL=$PWD/coinhsl-archive-2014.04.17.tar.gz

if test -f "$COINHSL"; then
    echo "$COINHSL exists."
else
    echo "$COINHSL does not exist. Visit https://www.hsl.rl.ac.uk/download/coinhsl-archive/2014.01.17 and place a copy of the solver here."
    exit 1
fi


# This regards Ipopt and its dependencies
VERSION=3.13.4
INSTALLDIR=$PWD/local



git clone https://github.com/coin-or-tools/ThirdParty-HSL.git
cd ThirdParty-HSL
mkdir -p coinhsl
tar xzf ${COINHSL} -C coinhsl --strip-components 1
./configure --prefix=$INSTALLDIR
make install -j

git clone https://github.com/coin-or-tools/ThirdParty-ASL.git
cd ThirdParty-ASL
./get.ASL
./configure --prefix=${INSTALLDIR}
make install -j
cd -

wget -c https://github.com/coin-or/Ipopt/archive/releases/${VERSION}.tar.gz -O - | tar -xz
cd Ipopt-releases-${VERSION}
./configure --prefix=${INSTALLDIR} --with-asl=1 --with-asl-cflags="-I${INSTALLDIR}/include/coin-or/asl" -with-asl-lflags="-L${INSTALLDIR}/lib -lcoinasl" --with-hsl=1 --with-hsl-cflags="-I${INSTALLDIR}/include/coin-or/hsl" -with-hsl-lflags="-L${INSTALLDIR}/lib -lcoinhsl"
make install -j
cd -

echo "Done. Set environment: export PATH=${INSTALLDIR}/bin:\$PATH"
echo "export PATH=${INSTALLDIR}/bin:\$PATH" > setupIpopt.sh

exit 0
