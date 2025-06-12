cd /Users/luc/Desktop/Data-Weekly-Digest

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

/usr/bin/env python3 email_creation.py

chmod +x /home/luc/Desktop/Data-Weekly-Digest/run_archie_digest.sh

