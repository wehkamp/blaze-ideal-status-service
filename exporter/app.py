import requests
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response
from flask import abort
from logging.config import dictConfig, logging
from prometheus_client.exposition import generate_latest
from prometheus_client.core import GaugeMetricFamily


SERVICE_PORT = os.environ.get('SERVICE_PORT', 5000)

dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(levelname)s] %(module)s: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default'
            }
        },
        'root': {
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'handlers': ['wsgi']
        }
    })
logging.info('Logging environment ready')
logging.debug('Operating with level DEBUG enabled')
app = Flask(__name__)


class RegistryMock(object):
    def __init__(self, metrics):
        self.metrics = metrics

    def collect(self):
        for metric in self.metrics:
            yield metric


def update_latest():
    global latest_metrics
    metrics = {
        'ideal_issuer_availability': GaugeMetricFamily(
            'ideal_issuer_availability',
            'Availability of iDeal issuer, in percentage',
            labels=['bank_name']
        ),
        'ideal_acquirer_availability': GaugeMetricFamily(
            'ideal_acquirer_availability',
            'Availability of iDeal acquirer, in percentage',
            labels=['bank_name']
        ),
    }

    urls = [('ideal_acquirer_', 'https://beschikbaarheid.ideal.nl/api/api/GetAcquirers', 'Acquirers'),
            ('ideal_issuer_', 'https://beschikbaarheid.ideal.nl/api/api/GetIssuers', 'Issuers')]

    for m in urls:
        name = "{prefix}availability".format(prefix=m[0])
        url = m[1]
        search = m[2]
        r = requests.get(url).json()
        msg = r['Message']
        if msg:
            logging.info(msg)

        issuers = r[search]
        _ = list(map(lambda x: metrics[name].add_metric([x['BankName']], x['Percent'].replace(',', '.')), issuers))

    latest_metrics = generate_latest(RegistryMock(metrics.values()))


@app.route("/")
def home():
    abort(400)


@app.route("/status")
def status():
    return "OK"


@app.route("/metrics")
def metrics():
    return Response(latest_metrics, mimetype='text/plain')


def run():
    update_latest()

    scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})
    scheduler.add_job(update_latest, 'interval', seconds=60)
    scheduler.start()

    try:
        app.run(host="0.0.0.0", port=SERVICE_PORT, threaded=True)
    finally:
        scheduler.shutdown()
