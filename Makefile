.PHONY: clean docker benchmarks

JOBS_FLAG = $(if $(JOBS),-j $(JOBS),)

clean:
	find benchmarks -name "*.results" -delete

docker:
	docker build -t eggshel .
	docker run -it --rm eggshel

small:
	python3 -m eggshel -f benchmarks/*.txt $(JOBS_FLAG)

medium:
	python3 -m eggshel -f benchmarks/med/*.txt -j 1

large:
	python3 -m eggshel -f benchmarks/large/*.txt -j 1