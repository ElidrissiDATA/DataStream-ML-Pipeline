import json
import logging
from kafka import KafkaConsumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    logging.info("Keyspace created successfully!")

def create_table(session):
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
            dob TIMESTAMP,
            registered_date TIMESTAMP,
            phone TEXT,
            picture TEXT
        );
    """)
    logging.info("Table created successfully!")

def insert_data(session, user_data):
    logging.info("Inserting data...")
    try:
        statement = SimpleStatement("""
            INSERT INTO spark_streams.created_users (id, first_name, last_name, gender, address,
                post_code, email, username, dob, registered_date, phone, picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        session.execute(statement, (
            uuid.UUID(user_data['id']),
            user_data['first_name'],
            user_data['last_name'],
            user_data['gender'],
            user_data['address'],
            user_data['post_code'],
            user_data['email'],
            user_data['username'],
            datetime.fromisoformat(user_data['dob'].replace('Z', '+00:00')),
            datetime.fromisoformat(user_data['registered_date'].replace('Z', '+00:00')),
            user_data['phone'],
            user_data['picture']
        ))
        logging.info(f"Data inserted for {user_data['first_name']} {user_data['last_name']}")

    except Exception as e:
        logging.error(f"Could not insert data due to: {e}")

def main():
    cluster = Cluster(['172.18.0.4'], port=9042)  # Vérifie l'adresse IP et le port
    session = cluster.connect()

    create_keyspace(session)
    create_table(session)

    consumer = KafkaConsumer(
        'Client_created',
        bootstrap_servers=['broker:29092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )

    for message in consumer:
        user_data = message.value
        insert_data(session, user_data)

if __name__ == "__main__":
    main()
