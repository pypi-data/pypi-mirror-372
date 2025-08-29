# Data adapter
Входной слой поступления данных от приборов или других источников

Примерный флоу данных от прибора такой:
- данные поступают от прибора в балансирощик данных 
- попадают в сервис юдп
- сервис юдп отправляет пакет в очередь в виде сообщения, оформляя сообщение в нужную структуру, выдавая идентификатор конкретному запросу
- воркер разбора конкретного протокола разбирает пакет
- воркер рассылает в распределитель сообщение уже с распаршенными данными, если они валидны, так же отправляет его же в сбор метаданных
- воркер метаданных сохраняет логи по конкретному прибору
- воркер распределителя отправляет сообщение в нужную интеграцию
- воркер интеграции конкретного провайдера читает из очереди и отправляет в нужный сервис

____

## Сервисы

Сервис это библиотека, сервис это то что в рантайме всегда 

### data_gateway__broker__amqp
сервис брокера очередей сообщений

### data_gateway__device_smp__udp_server
сервис приложения, написанный на GO. слушает порт UDP и отправляет в очередь на разбор пакета. Технически ему не важен протокол. Ожидает сообщения из очереди с айди сообщения запроса. так же слушает очередь прибора для отправки к конкретному прибору

### data_gateway__balancer
Балансировщик нагрузки. 

ВСЕ ВНЕШНИЕ ПОРТЫ ДОЛЖНЫ ПРОБРАСЫВАТЬСЯ ЧЕРЕЗ НЕГО

### mon_*
`mon__metrics__aggregator`, `mon__metrics__dashboard`, `mon__process_explorer__server`, `mon__process_explorer__container`, `mon__log__aggregator`

сервисы сбора аналитических данных


____

## Переменные среды для деплоя
`DD_API_KEY` - api ключ datadog

`DH_PARAM` - для шифрования в nginx

`SSH_ID_RSA` - приватный ключ доступа на сервер для развертывания

`{CI_BRANCH}_DATABASE_ENDPOINT` - эндпоинт для коннекта к базе данных. Содержит в себе юзернейм, пароль и название самой базы данных
`{CI_BRANCH}_APPLICATION_BROKER_ENDPOINT` - эндпоинт для коннекта к броокеру сообщений (rabbitmq). Содержит в себе юзернейм и пароль 

## Глобальные зависимости
- ubuntu 20.04
- bash
- make
- python `3.8.6`
- pyenv
- pipenv
- docker-compose `1.27.4`
- docker `19.03.13`

## Команды 

### обновление репозитория до последнего состояния в ветке
```bash
make cleanup
```
Это обновит пакеты и почистит все необходимое 

### Запуск локально
```bash
make up
```
Запустит все необходимые контейнеры

### Тестовая нагрузка на сервисы

нагрузит воркер СМП одним тестовым сообщением. добавит его в очередь
```bash
make worker_SMP_load
```

нагрузит воркер СМП одним реальным сообщением от прибора. добавит его в очередь
```bash
make worker_SMP_load_real_raw_data
```

нагрузит воркер распределителя интеграции
```bash
make integration_router_load
```

```bash
make load_UDP_SMP_getset
```

```bash
make DEV_load_UDP_SMP_getset
```
### Системные команды
```bash
make update-ci-images
```

### Работа с Grafana

В данный момент графана крутится на 4011 порту, т.е. дабы получить туда доступ, то небходимо, например, перейти по адресу 192.168.10.92:4011

Рабочих дашборда 2 - Docker and system monitoring && RabbitMQ-Overview
#### Docker and system monitoring 
На данном дашборде указаныф все метрики по серверу и контейнерам, кол-во свободного дискового пространства, ЦПУ. RAM, SWAP и т.д. как для сервера, так и для контейнера
Алерты приходяи при превышении пороговых значений по ЦПУ, RAM, Disc Space, а также если кол-во контейнеров падает ниже 14 (необходима ручная подстройка, если в какой-то момент добавятся ещё сервисы)

#### RabbitMQ-Overview
Дублирует админку RabbitMQ с точки зрения сбора показателей

# KAFKA
Если речь идёт о наших сертификатах - всё описано в файле  kafka_ssl_startup.sh и kafka_generate_client_ssl.sh
Это создание сертификатов как серверных, так и клиентскихз с использованием нашего CA севрера


Следующий блок посвящён генерации SSL ключей для kafka. Основным источником информации послужили [туториал один](https://www.vertica.com/docs/9.2.x/HTML/Content/Authoring/KafkaIntegrationGuide/TLS-SSL/KafkaTLS-SSLExamplePart1CreateRootCA.htm?TocPath=Integrating%20with%20Apache%20Kafka|Using%20TLS%2FSSL%20Encryption%20with%20Kafka|_____5 "Тык один") и [туториал два](https://www.vertica.com/docs/9.2.x/HTML/Content/Authoring/KafkaIntegrationGuide/TLS-SSL/KafkaTLS-SSLExamplePart3ConfigureKafka.htm?tocpath=Integrating%20with%20Apache%20Kafka%7CUsing%20TLS%2FSSL%20Encryption%20with%20Kafka%7C_____7 "Тык два")
А также личный опыт

Для генерации калючей, необходимы `keytool` и `openssl`
Первым шагом - необходимо сгенерировать CA  ключ (приватный) 
```bash
openssl genrsa -out root.key
```
и самим же его подписать
```bash
openssl req -new -x509 -key root.key -out root.crt
```
 и для безопасности
 ```bash
chmod 600 root.key
chmod 644 root.crt
 ```
Запомним эти два ключа, они нам ещё пригодятся

---

Для простоты использования и копирования, в дальнейшщих командах используется переменная `DOMAIN`, в которой лежит URL, на котором будет в будущем торчать KAFKA

Создаём хранилище сертификатов. Оно одно для всех брокеров Kafka. В нашем случае, там должен лежать только CA сертификат
```bash
keytool -keystore kafka.truststore.jks -alias CARoot -import -file root.crt
```
>Use the fully-qualified domain name (FQDN)
 
Создаём хранилище ключей для брокера, их может быть много, так что длоя каждого брокера оно должно быть своё
На вопрос 
>What is your first and last name?

Отвечаем DNS именем 
```bash
keytool -keystore kafka01.keystore.jks -alias $DOMAIN -validity 365 -genkey -keyalg RSA -ext SAN=DNS:$DOMAIN
```

Достаём из хранилища сертификат брокера...
```bash
keytool -keystore kafka01.keystore.jks -alias $DOMAIN -certreq -file kafka01.unsigned.crt
```
...подписываем его нашим CA сертификатом...
```bash
openssl x509 -req -CA root.crt -CAkey root.key -in kafka01.unsigned.crt -out kafka01.signed.crt -days 365 -CAcreateserial
```
...и кладём сертификат брокера обратно в его хранилище, вместе с CA сертификатом
```bash
keytool -keystore kafka01.keystore.jks -alias CARoot -import -file root.crt
keytool -keystore kafka01.keystore.jks -alias $DOMAIN -import -file kafka01.signed.crt
```

В сухом остатке, для корректной работы SSL, нам нобходимы только пароли, а также truestore & keystore(s)

---

И генерация Ключей для клиента. Надеюсь, вы ещё не потеряли ваши CA ключи, они вам сейчас понадобятся
Начинаем генерацию клиентского интерфейса с генерации  RSA 2048 ключа в паре с сертификатом (Всё это добро сразу кладётся в хранилище)

```bash
keytool -keystore kafka.keystore.jks -alias localhost -genkeypair -keyalg rsa
```
Достаём неподписаный ключ из хранилища и полдписываем его CA сертифифкатом
```bash
keytool -keystore kafka.keystore.jks -alias localhost -certreq -file cert-req-file
openssl x509 -req -CA root.crt -CAkey root.key -in cert-req-file  -out certificate.pem -days 365 -CAcreateserial
```

Для авторизации по SSL вам, как клиенту, понадобится ещё и приватник, так что и его достаём из хранилища
```bash
keytool -importkeystore -srckeystore kafka.keystore.jks -srcalias localhost -destalias notebook -destkeystore client.p12 -deststoretype PKCS12
openssl pkcs12 -in client.p12 -nodes -nocerts -out ca-key
```



### Именование сервисов
`%prefix%__%pod_name%__%pod_service_name%`

* %**prefix**%
  * mon - мониторинг, вспомогательный сервис
  * service - приложение, которое работает автономно, обрабатывает запросы или работает в фоне
  * manager - приложение, которое запускается только ради команды, затем гаснет  
* %**pod_name**%
  * data_logger
  * integration
  * integration_*
     * mts
  * device_*
     * ncp_smp
     * smp
     * water5
  * communication
* %**pod_service_name**%
  * *_%semantic_name%_worker
     * push
     * pull
     * chrono
  * *_%transport_protocol%_server
  * *_%semantic_name%_db
     * state
     * cache
     * common
  * *_api
  * *_web
  * *_app
  * broker


### Работа с Kubernetes

Т.к. удалённо все наши сервисы уже работают в кубере, надол уметь с ним работать. Минимально я вам уже рассказал про то, как оно изнутри
рабоатет и как писать конфиги, то сейчас  о полезных командах

Выдаёт список подов/сервисов/секретов/деплойментов одного неймспейса:
```bash
kubectl get pods/svc/secrets/deployments
```
В любую команду, связанную с сервисами, деплойментами. подами или секретами можно докинуть ключ `-A` или `--all-namespaces` для получения списка подов со всех неймспейсов
или `-n <namespace>` `--namespace=<namespace>` для пролучения списка подов с конкретного неймспейса
Выдаёт список нейсмспейсов
```bash
kubectl get namespaces
```

ВЫдаёт конфиг конкретного пода (перемнные проброшенные, контейнера и их порты)
```bash
kubectl describe pod <pod_name>
```
Меняет рабочий неймспейс на тот, что вы уукажите
```bash
kubectl config set-context --current --namespace=<namespace>
```
Заходим внутрь пода
```bash
kubectl exec -it <pod_name> -- /bin/bash
```
Получение логов пода
```bash
kubectl logs <pod_name>
```
