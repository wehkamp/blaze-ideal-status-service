from __future__ import print_function

import requests
import json
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response
from flask import abort
from prometheus_client.exposition import generate_latest
from prometheus_client.core import GaugeMetricFamily

IDEAL_JSON_URL = ('https://www.ideal-status.nl' +
                  '/static/sepa_issuers_current_lite.json')
SERVICE_PORT = os.environ.get('SERVICE_PORT', 5000)

logging.basicConfig(level=logging.os.environ.get('LOG_LEVEL', 'INFO'))
app = Flask(__name__)


class RegistryMock(object):
    def __init__(self, metrics):
        self.metrics = metrics

    def collect(self):
        for metric in self.metrics:
            yield metric


def update_latest():
    global latest_metrics
    app_metrics = {
        'success_rate': GaugeMetricFamily(
            'ideal_issuer_successes_total',
            'Success rate for iDeal issuer',
            labels=[
                'bank_name',
                'bank_code'
                ]
            ),
        'error_rate': GaugeMetricFamily(
            'ideal_issuer_errors_total',
            'Error rate for iDeal issuer',
            labels=[
                'bank_name',
                'bank_code'
                ]
            )
        }
    r = requests.get(IDEAL_JSON_URL)
    body = json.loads(r.content.decode('UTF-8'))
    for bank in body['rows']:
        bank_name, bank_code, rate_success, rate_error = None, None, None, None
        for data in bank['c']:
            d = data
            if d['p']['className'] == 'issuers_current_bank_name':
                bank_name = d['v']
            elif d['p']['className'] == 'issuers_current_bank_code':
                bank_code = d['v']
            elif d['p']['className'] == 'issuers_current_rate_success':
                rate_success = float(d['v'])*100
            elif d['p']['className'] == 'issuers_current_rate_error':
                rate_error = float(d['v'])*100
        app_metrics['success_rate'].add_metric(
                [bank_name, bank_code], rate_success)
        app_metrics['error_rate'].add_metric(
                [bank_name, bank_code], rate_error)

    latest_metrics = generate_latest(RegistryMock(app_metrics.values()))


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
