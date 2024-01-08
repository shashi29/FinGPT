import psycopg2

conn = psycopg2.connect(host="independent-way-410316:us-central1:collaborativedocsdb-test",
                        port="5432", 
                        user="postgres",
                        dbname="collaborativedocsdb_test",
                        password="a55zWlt:CYtAi|FB(|jJSpRA90N}")

conn.set_session(autocommit=True) # Set autocommit to True

cur = conn.cursor()

cur.execute("SELECT * FROM Boards;") 
# Replace with your actual user data
# new_user_data = {
#     "name": "admin",
#     "email": "test@example.com",
#     "password": "admin",  # Make sure to hash the password
#     "client_number": "001",
#     "customer_number": "12345",
# }

# # Insert the new user into the Users table
cur.execute(
    """
    INSERT INTO Users (name, email, password, client_number, customer_number)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, name, email, client_number, customer_number;
    """,
    (
        new_user_data["name"],
        new_user_data["email"],
        new_user_data["password"],
        new_user_data["client_number"],
        new_user_data["customer_number"],
    ),
)

results = cur.fetchall()

# Display the inserted user's information
print("User inserted successfully:")
#print(dict(zip(["id", "name", "email", "client_number", "customer_number"], results)))

print(results)
cur.close()
conn.close()