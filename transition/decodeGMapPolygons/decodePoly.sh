#!/bin/bash

case `uname` in
  CYGWIN*)
    CP=$( echo `dirname $0`/*.jar . | sed 's/ /;/g')
    ;;
  *)
    CP=$( echo `dirname $0`/*.jar . | sed 's/ /:/g')
esac

# Find Java
if [ "$JAVA_HOME" = "" ] ; then
    JAVA="java -server"
else
    JAVA="$JAVA_HOME/bin/java -server"
fi

# Set Java options
if [ "$JAVA_OPTIONS" = "" ] ; then
    JAVA_OPTIONS="-Xms250M -Xmx250M"
fi

echo $CP

$JAVA $JAVA_OPTIONS -cp $CP:$CLASSPATH org.geo.core.utils.DecodeGeoPoly $@
