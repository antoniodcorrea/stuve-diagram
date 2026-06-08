# LOCATION is required: make LOCATION="Madrid España" today
guard-location:
	@if [ -z "$(LOCATION)" ]; then \
		echo 'LOCATION is required, e.g. make LOCATION="Flugplatz Speck-Fehraltorf" today'; \
		exit 1; \
	fi

# Optional: HOUR=14 (one of 06 08 10 12 14 16 18 20 22; default 08)
today: guard-location
	python -m src.stuve --today --location "$(LOCATION)" $(if $(HOUR),--hour $(HOUR))

tomorrow: guard-location
	python -m src.stuve --tomorrow --location "$(LOCATION)" $(if $(HOUR),--hour $(HOUR))

test:
	python -m pytest
