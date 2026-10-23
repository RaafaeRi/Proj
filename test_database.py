from main import scrapeInternships
from database import saveInternshipsToDatabase, getConnection

internships = scrapeInternships()

saveInternshipsToDatabase(internships)

connection = getConnection()

result = connection.execute(
    "SELECT COUNT(*) FROM internships"
).fetchone()

print(f"Internships stored in database: {result[0]}")

connection.close()