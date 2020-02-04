cd frontend/ && docker build -t burningion/k8s-distributed-tracing-frontend:1.1 . && cd ..
cd users/ && docker build -t burningion/k8s-distributed-tracing-users:1.1 . && cd ..
cd sensors/ && docker build -t burningion/k8s-distributed-tracing-sensors:1.1 . && cd ..
cd pumps/ && docker build -t burningion/k8s-distributed-tracing-pumps:1.1 . && cd ..
