#!/bin/sh

# This script must be executed from the package folder it is located in
# i18ndude should be available in current $PATH (eg by running
# ``export PATH=$PATH:$BUILDOUT_DIR/bin`` when i18ndude is located in your buildout's bin directory)

# msginit --locale=en --input=../../$domain.pot


PACKAGE="./src/collective/notices"


DOMAIN="collective.notices"

i18ndude rebuild-pot --pot ${PACKAGE}/locales/${DOMAIN}.pot --create ${DOMAIN} --merge ${PACKAGE}/locales/${DOMAIN}-manual.pot $PACKAGE

for file in `find ${PACKAGE}/locales -name ${DOMAIN}.po`
do
    echo Syncing $file ...
    i18ndude sync --pot ${PACKAGE}/locales/${DOMAIN}.pot $file
    #msgfmt -o `dirname $file`/`basename $file .po`.mo $file --no-hash
done

