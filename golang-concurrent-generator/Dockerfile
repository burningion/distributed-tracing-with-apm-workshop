  FROM golang:1.12-alpine as builder
  RUN apk add --no-cache ca-certificates git && \
  wget -qO/go/bin/dep https://github.com/golang/dep/releases/download/v0.5.0/dep-linux-amd64 && \
  chmod +x /go/bin/dep

  ENV PROJECT github.com/burningion/go-concurrent-service
  WORKDIR /go/src/$PROJECT

  # restore dependencies
  COPY Gopkg.* ./
  RUN dep ensure --vendor-only -v
  COPY . .
  RUN go install .

  FROM alpine as release
  RUN apk add --no-cache ca-certificates \
  busybox-extras net-tools bind-tools
  WORKDIR /frontend
  COPY --from=builder /go/bin/go-concurrent-service /frontend/go-concurrent-service
  #COPY ./templates ./templates
  #COPY ./static ./static
  EXPOSE 8080
  ENTRYPOINT ["/frontend/go-concurrent-service"]
