package main

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"

	log "github.com/Sirupsen/logrus"

	httptrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/net/http"
	"gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

// Define a type for a handler that provides tracing parameters as well
type tracedHandler func(tracer.Span, *log.Entry, http.ResponseWriter, *http.Request)
type Message struct {
	Content string `json:"content"`
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

func sayHelloSuper(span tracer.Span, l *log.Entry, w http.ResponseWriter, r *http.Request) {
	message := r.URL.Path

	// set a tag for the current path
	span.SetTag("url.path", message)

	message = strings.TrimPrefix(message, "/")

	// log with matching trace ID
	l.WithFields(log.Fields{
		"message": message,
	}).Info("root url called with " + message)

	js := Message{Content: message}
	jsonValue, _ := json.Marshal(js)

	req, err := postWithContext(r.Context(), "http://super-service:8081/super", "application/json", bytes.NewBuffer(jsonValue))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	tr := &http.Transport{
		MaxConnsPerHost: 10,
	}

	tracedClient := httptrace.WrapClient(&http.Client{Transport: tr})
	resp, err := tracedClient.Do(req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	defer resp.Body.Close()

	rjs := Message{}
	err = json.NewDecoder(resp.Body).Decode(&rjs)
	if err != nil {
		http.Error(w, err.Error(), 400)
		return
	}

	message = "Hello " + rjs.Content

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
	mux.HandleFunc("/generate_requests", withSpanAndLogger(sayPong))
	mux.HandleFunc("/generate_requests_user", withSpanAndLogger(sayPong))
	mux.HandleFunc("/", withSpanAndLogger(sayHelloSuper)) // use the tracer to handle the urls

	err := http.ListenAndServe(":8080", mux) // set listen port
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
