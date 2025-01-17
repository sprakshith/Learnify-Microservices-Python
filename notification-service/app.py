import os
import json
import threading
from flask import Flask, request
from kafka import KafkaProducer, KafkaConsumer

app = Flask(__name__)

kafka_producer = KafkaProducer(
    bootstrap_servers=os.environ.get('BOOTSTRAP_SERVERS'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


@app.route('/api/v1/notifications/courses/general-announcement', methods=['POST'])
def send_general_announcement():
    kafka_producer.send('general-announcement-notification', request.json)
    return 'Notification sent to general-announcement-notification topic', 200


@app.route('/api/v1/notifications/courses/created', methods=['POST'])
def send_course_created():
    kafka_producer.send('course-created-notification', request.json)
    return 'Notification sent to course-created-notification topic', 200


@app.route('/api/v1/notifications/courses/updated', methods=['POST'])
def send_course_updated():
    kafka_producer.send('course-updated-notification', request.json)
    return 'Notification sent to course-updated-notification topic', 200


@app.route('/api/v1/notifications/courses/enrolled', methods=['POST'])
def send_course_enrolled():
    kafka_producer.send('course-enrolled-notification', request.json)
    return 'Notification sent to course-enrolled-notification topic', 200


def consume_messages(topic, group_id):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=os.environ.get('BOOTSTRAP_SERVERS'),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print(f"Listening for messages on {topic}...")

    for message in consumer:
        print(f"Received message from {topic} topic: {message.value}")


def start_consumers():
    topics = {
        'general-announcement-notification': 'general-announcement-group',
        'course-created-notification': 'course-created-group',
        'course-updated-notification': 'course-updated-group',
        'course-enrolled-notification': 'course-enrolled-group'
    }

    threads = []

    for topic, group_id in topics.items():
        print(f"Creating thread for topic: {topic}")

        thread = threading.Thread(target=consume_messages, args=(topic, group_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    print("Starting Kafka consumers...")
    threading.Thread(target=start_consumers).start()

    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000)
