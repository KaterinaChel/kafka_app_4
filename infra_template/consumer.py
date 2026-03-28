from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import json


sr_config = {'url': 'http://schema-registry:8081'}
schema_registry_client = SchemaRegistryClient(sr_config)


avro_deserializer = AvroDeserializer(schema_registry_client)


consumer_config = {
    'bootstrap.servers': 'kafka-0:9092',
    'group.id': 'python-consumer-group-2',
    'auto.offset.reset': 'earliest',
    "fetch.min.bytes": 10, #минимальный размер накопленных сообщений в топике для забора
    "fetch.wait.max.ms": 1000, #максимальное время (в миллисекундах), которое брокер будет ждать накопления данных
    'key.deserializer': avro_deserializer,
    'value.deserializer': avro_deserializer
}

consumer = DeserializingConsumer(consumer_config)

topics = ['customers.public.users', 'customers.public.orders']
consumer.subscribe(topics)

print("--- Ожидание данных из Kafka... (Ctrl+C для выхода) ---")

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Ошибка: {msg.error()}")
            continue

        # Вывод данных
        topic = msg.topic()
        value = msg.value()
        
        #payload = value.get('after') if value else None

        print(f"\n[TOPIC: {topic}]")
        if value is not None:
            print("ПОЛНОЕ СООБЩЕНИЕ:")
            print(json.dumps(value, indent=2, ensure_ascii=False))
        else:
            print("Сообщение пустое (Tombstone)")

except KeyboardInterrupt:
    print("\nОстановка...")
finally:
    consumer.close()