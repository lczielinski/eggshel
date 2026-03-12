.PHONY: clean docker benchmarks

TIMEOUT ?= 300
JOBS_FLAG = $(if $(JOBS),-j $(JOBS),)

clean:
	find benchmarks -name "*.results" -delete

docker:
	docker build -t eggshel .
	docker run -it --rm eggshel

benchmarks:
	python3 -m eggshel -f benchmarks/*.txt -t $(TIMEOUT) $(JOBS_FLAG)
