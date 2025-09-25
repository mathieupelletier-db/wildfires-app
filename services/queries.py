import services.lakebase as lakebase
from databricks.sdk import WorkspaceClient

# Configuration
local_service_principal_name = 'local-service-principal'
group_name = '2025_vibe_coding'
instance_name = 'mpelletier-demo'
LAKEBASE_DB_NAME = 'databricks_postgres'
user_email = 'mathieu.pelletier@databricks.com'

# Create workspace client
w = WorkspaceClient(profile="adb-984752964297111")

# Get the database instance
instance = w.database.get_database_instance(instance_name)

# Create connection
conn = lakebase.create_lakebase_connection(wc=w, instance=instance, db_name=LAKEBASE_DB_NAME, user=user_email)
conn.set_isolation_level(0)

try:
    with conn.cursor() as cursor:
        # Execute the query
        cursor.execute("SELECT * FROM public.airports_geom")
        
        # Fetch and display results
        results = cursor.fetchall()
        
        if results:
            print(f"Found {len(results)} airports:")
            print("-" * 50)
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            print(" | ".join(column_names))
            print("-" * 50)
            
            # Display results (limit to first 10 for readability)
            for i, row in enumerate(results[:10]):
                print(" | ".join(str(cell) for cell in row))
            
            if len(results) > 10:
                print(f"... and {len(results) - 10} more rows")
        else:
            print("No airports found in the database")
            
except Exception as e:
    print(f"Error executing query: {e}")
finally:
    conn.close()
