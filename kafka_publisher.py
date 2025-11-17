from confluent_kafka import Producer
import os
import json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


kafka_config = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL'),
    'sasl.mechanism': os.getenv('KAFKA_SASL_MECHANISM', 'SCRAM-SHA-256'),
    'sasl.username': os.getenv('KAFKA_SASL_USERNAME'),
    'sasl.password': os.getenv('KAFKA_SASL_PASSWORD'),
}

topic_name = os.getenv('KAFKA_TOPIC', 'tasks-topic')
kafka_enabled = False
producer = None


try:
    producer = Producer(kafka_config)
    kafka_enabled = True
    print("Redpanda/Kafka initialized successfully")
except Exception as e:
    print(f"Kafka not available: {e}")
    print(" API will work normally, but events won't be published")


def delivery_report(err, msg):
    """Callback for message delivery reports"""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Published event to {msg.topic()} [{msg.partition()}]')


def publish_task_event(event_type: str, task_id: str, task_data: Dict[str, Any]):
    """
    Publish task events to Kafka/Redpanda
    
    Args:
        event_type: One of "task.created"
        task_id: The task ID
        task_data: Task details (title, description, priority, status, etc.)
    """
    if not kafka_enabled:
        print(f"[Local Mode] {event_type} event for task {task_id} (not published)")
        return
    
    event = {
        "event_type": event_type,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "data": task_data
    }
    
    try:
        message_json = json.dumps(event)
        print(f"Publishing {event_type} to {topic_name}...")
        
        
        producer.produce(
            topic_name,
            key=task_id.encode('utf-8'),
            value=message_json.encode('utf-8'),
            callback=delivery_report
        )
        
        producer.poll(1)
        
    except Exception as e:
        print(f"Error publishing event: {e}")
        import traceback
        traceback.print_exc()


def flush_producer():
    """Flush any pending messages"""
    if producer:
        producer.flush(timeout=10)
