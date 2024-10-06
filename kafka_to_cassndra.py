import json
import logging
import uuid
from kafka import KafkaConsumer
from cassandra.cluster import Cluster

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_cassandra_connection():
    try:
        # Connecting to the Cassandra cluster
        cluster = Cluster(['localhost'])  # Changez 'localhost' si nécessaire
        session = cluster.connect()
        logging.info("Connected to Cassandra successfully!")
        return session
    except Exception as e:
        logging.error(f"Could not create Cassandra connection due to {e}")
        return None

def create_keyspace(session):
    try:
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS spark_streams
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
        """)
        logging.info("Keyspace created successfully!")
    except Exception as e:
        logging.error(f"Could not create keyspace due to {e}")

def create_table(session):
    try:
        session.execute("""
            CREATE TABLE IF NOT EXISTS spark_streams.created_users (
                id UUID PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                gender TEXT, 
                address TEXT,
                post_code TEXT,
                email TEXT,
                username TEXT,
                registered_date TEXT,
                phone TEXT,
                picture TEXT
            );
        """)
        logging.info("Table created successfully!")
    except Exception as e:
        logging.error(f"Could not create table due to {e}")

def insert_data(session, **kwargs):
    logging.info("Inserting data...")

    user_id = uuid.uuid4()  # Generate a new UUID for the user
    try:
        session.execute("""
            INSERT INTO spark_streams.created_users(id, first_name, last_name, gender, address, 
                post_code, email, username, registered_date, phone, picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, kwargs['first_name'], kwargs['last_name'], kwargs['gender'],
              kwargs['address'], kwargs['post_code'], kwargs['email'],
              kwargs['username'], kwargs['registered_date'], kwargs['phone'], kwargs['picture']))
        logging.info(f"Data inserted for {kwargs['first_name']} {kwargs['last_name']}")

    except Exception as e:
        logging.error(f'Could not insert data due to {e}')

def consume_data():
    session = create_cassandra_connection()

    if session is not None:
        create_keyspace(session)
        create_table(session)

        # Kafka consumer configuration
        consumer = KafkaConsumer(
            'users_created',  # Topic to consume
            bootstrap_servers=['localhost:9092'],  # Changez 'localhost' si nécessaire
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group'  # Ajouter un ID de groupe pour la gestion des offsets
        )

        logging.info("Starting to consume messages from Kafka...")
        # Consume messages from Kafka
        try:
            for message in consumer:
                user_data = message.value
                insert_data(session, **user_data)
        except Exception as e:
            logging.error("Error consuming messages from Kafka:", exc_info=True)
        finally:
            consumer.close()

        # Clean up
        session.shutdown()
        logging.info("Cassandra session closed.")

if __name__ == "__main__":
    consume_data()

