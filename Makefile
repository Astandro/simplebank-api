# Makefile for Delivery Service API

# Start Docker Compose services
run:
	docker-compose up -d

# Stop Docker Compose services
stop:
	docker-compose down

# View Docker Compose logs
logs:
	docker-compose logs -f

# Seed the database (this can be customized)
seed:
	docker-compose exec api python app/seed.py
