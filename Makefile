.PHONY: data features train submit cv clean setup

setup:
	pip install -r requirements.txt

data:
	python src/data/download.py

features:
	python scripts/run_pipeline.py --step features

train:
	python scripts/run_pipeline.py --step train

submit:
	python scripts/run_submission.py

cv:
	python scripts/run_cv.py

clean:
	rm -rf data/interim/* data/processed/* models/*.pkl models/*.joblib
