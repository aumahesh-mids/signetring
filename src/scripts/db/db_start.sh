# Create a PostgreSQL instance
docker run --name ta-postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=ta \
  -p 5432:5432 \
  -d postgres

sleep 60

python trustedauthority/app/init_db.py

python trustedauthority/app/util/generate_trusted_authority_keys.py