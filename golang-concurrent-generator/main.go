package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"

	log "github.com/Sirupsen/logrus"

	httptrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/net/http"
	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

// Define a type for a handler that provides tracing parameters as well
type tracedHandler func(tracer.Span, *log.Entry, http.ResponseWriter, *http.Request)
type Message struct {
	Concurrent int    `json:"concurrent"`
	Total      int    `json:"total"`
	URL        string `json:"url"`
}

func postWithContext(ctx context.Context, url, contentType string, body io.Reader) (*http.Request, error) {
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", contentType)
	if ctx != nil {
		req = req.WithContext(ctx)
	}
	return req, nil
}

func getWithContext(ctx context.Context, url string) (*http.Request, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	return req, nil
}

// Write a wrapper function that does the magic preparation before calling the traced handler.
// This returns a function that is suitable for passing to mux.HandleFunc
func withSpanAndLogger(t tracedHandler) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		span, _ := tracer.SpanFromContext(r.Context())
		traceID := span.Context().TraceID()
		spanID := span.Context().SpanID()
		entry := log.WithFields(log.Fields{
			"dd.trace_id": traceID,
			"dd.span_id":  spanID,
		})
		t(span, entry, w, r)
	}
}

func getURL(req *http.Request, c *http.Client, ch chan<- string) {
	resp, err := c.Do(req)
	if err != nil {
		return
	}
	body, _ := ioutil.ReadAll(resp.Body)
	ch <- fmt.Sprintf(string(body))
}

func getConcurrent(span tracer.Span, l *log.Entry, w http.ResponseWriter, r *http.Request) {
	var m Message
	err := json.NewDecoder(r.Body).Decode(&m)
	if err != nil {
		http.Error(w, err.Error(), 400)
		return
	}
	// set a tag for the current path
	span.SetTag("url.request", m)

	// log with matching trace ID
	l.WithFields(log.Fields{
		"concurrent-requests": m.Concurrent,
		"total-requests":      m.Total,
		"URL":                 m.URL,
	}).Info("root url called with %d concurrent requests", m.Concurrent)

	tr := &http.Transport{
		MaxConnsPerHost: m.Concurrent,
	}

	tracedClient := httptrace.WrapClient(&http.Client{Transport: tr})

	ch := make(chan string)
	for i := 0; i < m.Total; i++ {
		req, err := getWithContext(r.Context(), m.URL)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		go getURL(req, tracedClient, ch)
	}

	for i := 0; i < m.Total; i++ {
		l.WithFields(log.Fields{
			"message": <-ch,
		}).Info("root url called with ", m.Total)
	}

	message := fmt.Sprintf("%d concurrent requests done for a total of %d", m.Concurrent, m.Total)
	w.Write([]byte(message))
}

func getConcurrentRandom(span tracer.Span, l *log.Entry, w http.ResponseWriter, r *http.Request) {
	// log with matching trace ID
	l.WithFields(log.Fields{
		"concurrent-requests": 20,
		"total-requests":      100,
		"URL":                 "users",
	}).Info("random user url called with 20 concurrent requests")

	tr := &http.Transport{
		MaxConnsPerHost: 20,
	}

	tracedClient := httptrace.WrapClient(&http.Client{Transport: tr})

	sensorsURL := "http://" + os.Getenv("NODE_API_SERVICE_HOST") + os.Getenv("NODE_SERVICE_PORT_HTTP")

	ch := make(chan string)
	for i := 0; i < 100; i++ {
		req, err := getWithContext(r.Context(), sensorsURL+"/users/1")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		go getURL(req, tracedClient, ch)
	}

	for i := 0; i < 100; i++ {
		l.WithFields(log.Fields{
			"message": <-ch,
		}).Info("random user url called with 20 concurrent")
	}

	message := fmt.Sprintf("20 concurrent requests done for a total of 100 random user requests")
	w.Write([]byte(message))
}

func sayPong(span tracer.Span, l *log.Entry, w http.ResponseWriter, r *http.Request) {
	l.Info("Ping / Pong request called")

	w.Write([]byte("pong"))
}

func main() {
	log.SetFormatter(&log.JSONFormatter{})
	log.Info("starting up")

	// start the tracer with zero or more options
	tracer.Start()
	defer tracer.Stop()

	mux := httptrace.NewServeMux(httptrace.WithServiceName("frontend-go-service"), httptrace.WithAnalytics(true)) // init the http tracer
	mux.HandleFunc("/generate_requests", withSpanAndLogger(getConcurrent))
	mux.HandleFunc("/generate_requests_user", withSpanAndLogger(getConcurrentRandom))
	mux.HandleFunc("/", withSpanAndLogger(sayPong)) // use the tracer to handle the urls

	err := http.ListenAndServe(":8080", mux) // set listen port
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
