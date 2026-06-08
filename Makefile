# LOCATION is required: make LOCATION="Madrid España" today
guard-location:
	@if [ -z "$(LOCATION)" ]; then \
		echo 'LOCATION is required, e.g. make LOCATION="Flugplatz Speck-Fehraltorf" today'; \
		exit 1; \
	fi

today: guard-location
	python -m src.stuve --today --location "$(LOCATION)"

tomorrow: guard-location
	python -m src.stuve --tomorrow --location "$(LOCATION)"

test:
	python -m pytest
