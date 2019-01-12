import ssl
import sys

from api import application

if __name__ == "__main__":

    if sys.argv[1] == 'dev':
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(
            '/etc/letsencrypt/live/api.thewatcher.io/fullchain.pem',
            '/etc/letsencrypt/live/api.thewatcher.io/privkey.pem',
        )
        application.run(
            port=8013,
            host="0.0.0.0",
            debug = True,
            ssl_context=context
        )
        sys.exit()

    application.run()
