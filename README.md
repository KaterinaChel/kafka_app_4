# kafka_app_4
Интеграция с БД Postgres с помощью kafka connector
Назначение модулей:

Kafka-connect - Инструмкент для интеграции с внешними системами (в данном случае Postgres)
Debezium source connector - Загрузка данных из внешней базы в топик кафка
Consumer - Чтение данных из топика кафка(Можно вместо этого если позволяет система и не нужен кастом сконфигурировать Debezium synk connector)
Prometheus - сбор и хранения логов
Grafana - построение дашбордов
Postgres - База данных на которую подписываемся и читаем изменения данных WAL (конкретно таблицы users и orders)
Docker Compose - конфигурация контейнеров и взаимосвязей



Загрузка конфигов и Проверка работоспособности:

--Положить конфиг с настройками дебез

curl -X POST -H "Content-Type: application/json" --data "@postgres-source.json" http://localhost:8083/connectors

	  
--Создание и наполнение таблиц postgres
	  
docker exec -it postgres psql -U postgres-user -d customers
	  
	  
CREATE TABLE users (id SERIAL PRIMARY KEY,name VARCHAR(100),email VARCHAR(100),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE orders (id SERIAL PRIMARY KEY,user_id INT REFERENCES users(id),product_name VARCHAR(100),quantity INT,order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP); 

INSERT INTO users (id, name, email,created_at) SELECT i, 'Name_' || i || '_' || substring('abcdefghijklmnopqrstuvwxyz', (random() * 26)::integer + 1, 1), i || '_' || substring('abcdefghijklmnopqrstuvwxyz' || '@gmail.com', (random() * 26)::integer + 1, 1),now() - (random() * (interval '30 days')) FROM generate_series(1, 9000000) AS i;

INSERT INTO orders (user_id, product_name, quantity, order_date) SELECT (SELECT id FROM users ORDER BY random() LIMIT 1),'Product_' || (random()*10)::int,(random()*5 + 1)::int,now() - (random() * interval '30 days') FROM generate_series(1, 3000000);  


--Проверить состояние коннектора 

curl http://localhost:8083/connectors/pg-connector/status

{"name":"pg-connector","connector":{"state":"RUNNING","worker_id":"localhost:8083"},"tasks":[{"id":0,"state":"RUNNING","worker_id":"localhost:8083"}],"type":"source"}

--Вывести в консоль данные от консьюмера 
docker-compose logs -f python-consumer


--Убедитесь, что коннектор начал выдавать метрики. В браузере введите ссылку http://localhost:9876/metrics

--Убедитесь что у Prometheus есть доступ к kafka-connect-host. Перейдите в Prometheus. Для этого в браузере введите ссылку http://localhost:9090 (status-targets)

Проверьте интеграцию с Grafana. 
 a. Перейдите в Grafana — в браузере введите ссылку http://localhost:3000
 b. Загрузить JSON с настройками графиков
 c. Взаимодействие с базой (удалим данные и загрузим вновь, чтобы посмотреть активность на графиках):
   - docker exec -it postgres psql -U postgres-user -d customers
   - truncate table orders;
   - INSERT INTO orders (user_id, product_name, quantity, order_date) SELECT (SELECT id FROM users ORDER BY random() LIMIT 1),'Product_' || (random()*10)::int,(random()*5 + 1)::int,now() - (random() * interval '30 days') FROM generate_series(1, 3000000); 
