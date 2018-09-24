# Distributed Tracing with APM Workshop

This will be a follow up repo to my [2018 Dash APM Workshop](https://github.com/burningion/dash-apm-workshop), incorporating feedback from the event.

Specifically, this will add:

* Starting with Automatic Instrumentation, and a more complex example program
* More live traffic, to see Trace Search (announced at DASH)
* Debugging a bigger, more complex system, to showcase a more real world use case
* More Datadog UI usage
* More relevant examples and names for traces
* More realistic errors 
* ... and should also work in Windows.

In the meantime, unless otherwise noted, this repository is a work in progress. 

If you've stumbled upon it and have feedback, or have something you'd  like to see, feel free to create an issue.

# Running the Application

![Water Sensor App](https://github.com/burningion/distributed-tracing-with-apm-workshop/raw/master/images/dashboard.png)

You'll need to have a Datadog account with APM and logging enabled. A free trial should work to play with.

```bash
$ POSTGRES_USER=postgres POSTGRES_PASSWORD=<pg password> DD_API_KEY=<api key> docker-compose up
```

You can open the web app at `http://localhost:5000`, create some pumps, and look at your Datadog traces to see the distributed traces.

The frontend of the app is a React node app using [Material UI](https://material-ui.com/). It lives in the `single-page-frontend` folder. You can start it up for development with a:

```bash
$ npm install
$ npm start
```

It should connect to the running frontend API container, allowing for easier development. When you're finished making changes, you can do a `npm build`, and then copy the javascript from the `build` subdirectory into the Flask frontend app.

# Ideas for Live Debugging via Tracing

These are some ideas, that have yet to be implemented:

* A bad deploy that triggers a problem, breaking parts of API
* Introducing latency in a service in the middle of the request lifecycle
* Introducing a traffic spike / poison payload downstream
