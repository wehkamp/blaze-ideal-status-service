FROM wehkamp/alpine:3.9

ARG tag
ENTRYPOINT ["python3", "-m", "exporter"]
EXPOSE 5000
ENV FLASK_APP=/exporter/exporter/app.py

RUN LAYER=build \
  && apk add -U python3 py3-pip \
  && pip3 install prometheus_client requests apscheduler Flask \
  && rm -rf /var/cache/apk/* \
  && rm -rf ~/.cache/pip

ADD ./exporter /exporter

LABEL blaze.service.id="blaze-ideal-status-service" \
      blaze.service.name="ideal-status" \
      blaze.service.version="${tag}" \
      blaze.service.team="Tooling" \
      blaze.service.main-language="python" \
      blaze.service.description="Monitoring for iDeal platform status" \
      blaze.service.features.health-check.enabled="true" \
      blaze.service.features.health-check.endpoint="/status" \
      blaze.service.features.metrics.enabled="true" \
      blaze.service.deployment.cpu="0.1" \
      blaze.service.deployment.memory="50" \
      blaze.service.deployment.minimum-instances="1" \
      blaze.service.deployment.internal-port="5000" \
      blaze.service.deployment.promotion.accept.manual-step="false" \
      blaze.service.deployment.promotion.prod.manual-step="false" \
      blaze.service.routing.consumer.exposed="false" \
      blaze.service.routing.trusted.exposed="false"  
