#!/bin/bash
# run as bill-calculator/packaging/package.sh from directory above bill-calculator
NAME=bill-calculator
VERSION=0.5
REL=13
VERS=${NAME}-${VERSION}

if [ ! -d bill-calculator ]; then
   echo 'package.sh is expecting to be executed as bill-calculator/packaging/package.sh' >&2
   exit 1
fi

# Create rpm build environment
echo "%_topdir ${HOME}/rpm" > ~/.rpmmacros
echo "%_tmppath /tmp" >> ~/.rpmmacros
rm -rf ~/rpm
mkdir -p ~/rpm/BUILD ~/rpm/RPMS ~/rpm/SOURCES ~/rpm/SPECS ~/rpm/SRPMS
sed -e "s/__VERSION__/${VERSION}/g" -e "s/__RELEASE__/${REL}/g" ./bill-calculator/packaging/bill-calculator.spec >  ~/rpm/SPECS/bill-calculator.spec

# Package product for rpmbuild
mv ./bill-calculator ./${VERS}
tar --exclude="*.pyc" --exclude="*.pyo" --exclude=".*" --exclude="packaging" --exclude="*.log" -cf ${VERS}.tar -v ${VERS}
mv ./${VERS} ./bill-calculator
gzip ${VERS}.tar
mv ${VERS}.tar.gz ~/rpm/SOURCES/

# Create rpmbuild
rpmbuild -bb ~/rpm/SPECS/bill-calculator.spec || exit 1
cp ~/rpm/RPMS/noarch/${VERS}-${REL}.noarch.rpm ./bill-calculator/packaging

# Tag 
TVER="v${VERSION}-${REL}"  
cd bill-calculator/
git tag  -m ${TVER} -a ${TVER}
git push origin ${TVER}
