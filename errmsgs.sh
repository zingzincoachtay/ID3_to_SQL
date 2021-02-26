#!/bin/sh

#perl -0pe 's/Error Mismatch TCON: ((.+)(\.\w{3,4}))\n\s+>>>(.+)/mv --backup=numbered "\1" "\2 - \4\3"/g' $1

perl -0pe 's/Error.+?: ((.+\/\d{1,2} \- )([^\/]+?)( \- [^\/]+))\n\s+>>>(.+)/mv --backup=numbered "\1" "\2\5\4"/g' $1

