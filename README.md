# SLO Workshop

This repo will be used as support material for the 2019 Dash Workshop: Ensuring Reliability with SLOs.

It is based on a micro-service application designed for the 2018 Dash Workshop: Distributing Tracing with APM. You can use a live environment hosted on Katacoda here, or you can work locally on your machine using `docker-compose` (as long as the SLO feature has been enabled for your Datadog account).

# Prerequisites

Using the credentials given to you at the begining of the workshop, connect to [app.datadoghq.com](app.datadoghq.com), navigate to `Integrations / APIs` and copy the key under `API Keys`.

Then connect to the Katacoda environment here.

# Running the Application

Follow the instructions in Katacoda, or simply run:

```bash
$ POSTGRES_USER=postgres POSTGRES_PASSWORD=<pg password> DD_API_KEY=<api key> docker-compose up
```

You can open the web app at `http://localhost:5000`, create some pumps, and look at your Datadog traces to see the distributed traces.
