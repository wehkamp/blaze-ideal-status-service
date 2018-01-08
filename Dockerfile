FROM wehkamp/alpine:3.5

ARG tag
ENTRYPOINT ["python", "-m", "exporter"]
EXPOSE 5000
ENV FLASK_APP=/exporter/exporter/app.py

RUN LAYER=build \
  && apk add -U python py-pip \
  && pip install prometheus_client requests apscheduler Flask \
  && rm -rf /var/cache/apk/* \
  && rm -rf ~/.cache/pip

ADD ./exporter /exporter

LABEL blaze.service.id="prometheus-ideal-exporter" \
      blaze.service.name="blaze-prometheus-ideal-exporter" \
      blaze.service.version="${tag}" \
      blaze.service.team="Tooling" \
      blaze.service.description="Monitoring for ideal-status.nl" \
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
