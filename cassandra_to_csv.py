from cassandra.cluster import Cluster
import pandas as pd

# Connexion à Cassandra
cluster = Cluster(['localhost'])
session = cluster.connect('spark_streams')

# Exécution de la requête
query = "SELECT * FROM created_users"
rows = session.execute(query)

# Conversion en DataFrame pandas
df = pd.DataFrame(rows)

# Affichage du DataFrame
print(df)
df.to_csv('C:/Users/mohamed/bigdata/projet/created_users.csv', index=False)
print('bien telecharge')
# Fermeture de la connexion
cluster.shutdown()


