.PHONY: clean docker benchmarks benchmarks-full

TIMEOUT ?= 300

clean:
	find benchmarks -name "*.results" -delete

docker:
	docker build -t eggshel .
	docker run -it --rm eggshel

benchmarks:
	python3 -m eggshel -f benchmarks/*.txt -t $(TIMEOUT)
