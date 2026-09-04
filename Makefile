.PHONY: install pipeline data detect database test clean

install:
	python -m pip install -r requirements.txt

pipeline:
	python run_pipeline.py

data:
	python -m src.generate_data

database:
	python -m src.database

test:
	python -m unittest discover -s tests -v

clean:
	python scripts/clean_outputs.py

