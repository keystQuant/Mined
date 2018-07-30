#! /bin/bash

#### 로컬 환경에서 RabbitMQ만 실행시키기 ####

docker run -d \
  --name local-rabbit \
  -p 5672:5672 \
  --restart=unless-stopped \
  rabbitmq
