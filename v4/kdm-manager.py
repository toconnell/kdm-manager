"""

    Runs the app from the CLI via Flask dev server.

"""

import os

from app import app

if __name__ == '__main__':

    # sanity check dev SSL
    for ssl_file in [app.config['DEV_SSL_CERT'], app.config['DEV_SSL_KEY']]:
        if not os.path.isfile(ssl_file):
            err = 'Dev server cannot start without a valid %s file!'
            raise FileNotFoundError(err % ssl_file)

    print(' * API: %s' % app.config['API']['url'])  # prints during CLI init

    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        ssl_context=(
            app.config['DEV_SSL_CERT'],
            app.config['DEV_SSL_KEY']
        ),
    )
