# iDeal exporter for Prometheus

Scrapes the iDeal availability API every 1 minute and exposes the uptime percentage of _issuers_ and _acquirers_ as prometheus metrics.

Example metrics exposed:

```
ideal_issuer_availability{bank_name="ABN AMRO"} 99.86
ideal_issuer_availability{bank_name="ASN Bank"} 100.0
ideal_issuer_availability{bank_name="bunq"} 97.63
ideal_issuer_availability{bank_name="Handelsbanken"} 100.0
ideal_issuer_availability{bank_name="ING"} 100.0
ideal_issuer_availability{bank_name="Knab"} 100.0
ideal_issuer_availability{bank_name="Moneyou"} 100.0
ideal_issuer_availability{bank_name="Rabobank"} 100.0
ideal_issuer_availability{bank_name="RegioBank"} 100.0
ideal_issuer_availability{bank_name="SNS Bank"} 100.0
ideal_issuer_availability{bank_name="Triodos Bank"} 100.0
ideal_issuer_availability{bank_name="Van Lanschot"} 100.0
ideal_acquirer_availability{bank_name="ABN AMRO"} 100.0
ideal_acquirer_availability{bank_name="BNG Bank"} 100.0
ideal_acquirer_availability{bank_name="BNP Paribas"} 100.0
ideal_acquirer_availability{bank_name="Deutsche Bank NL"} 100.0
ideal_acquirer_availability{bank_name="deVolksbank"} 100.0
ideal_acquirer_availability{bank_name="ING"} 100.0
ideal_acquirer_availability{bank_name="ING Maxcode QA"} 100.0
ideal_acquirer_availability{bank_name="NWB Bank"} 100.0
ideal_acquirer_availability{bank_name="RABO"} 100.0
ideal_acquirer_availability{bank_name="Rabobank Worldline QA"} 100.0
```

### Future work

The upstream API also returns a single status message, indicating possible problems. This can be used as event to inform our internal downstream services more specifically:

```json
{
  "Message": "",
  "AllGreen": true,
  "AllGreenMessage": "Momenteel zijn alle banken beschikbaar. U kunt betalen met iDEAL"
}
```

Failure situation:

```json
{
  "Message": "Heeft u als ondernemer (webwinkel) een iDEAL-contract bij ING, dan kunt u geen iDEAL-betalingen laten doen.<br />Laat uw klanten het nogmaals proberen of bied een andere betaalmethode aan.",
  "AllGreen": false,
}
```
