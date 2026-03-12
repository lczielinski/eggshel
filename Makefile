.PHONY: clean docker benchmarks benchmarks-full

clean:
	find benchmarks -name "*.results" -delete

docker:
	docker build -t eggshel .
	docker run -it --rm eggshel

benchmarks:
	python3 -m eggshel -f benchmarks/*.txt -t 300

benchmarks-full:
	python3 -m eggshel -f benchmarks/*.txt -t 3600
