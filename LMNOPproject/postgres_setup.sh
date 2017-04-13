#!/bin/bash
source ../venv/bin/activate
export POSTGRES_LMNOP_USER_PASSWORD=lmnop
export DYLD_FALLBACK_LIBRARY_PATH=/Library/PostgreSQL/9.5/lib
sudo ln -s /Library/PosgreSQL/9.5/lib/libssl.1.0.0.dylib /usr/local/lib
sudo ln -s /Library/PosgreSQL/9.5/lib/libcrypto.1.0.0.dylib /usr/local/lib
