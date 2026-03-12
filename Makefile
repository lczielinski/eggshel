.PHONY: clean docker benchmarks

clean:
	find benchmarks -name "*.results" -delete

docker:
	docker build -t eggshel . 
	docker run -it --rm eggshel

benchmarks:
	python3 -m eggshel -f benchmarks/dotprod.txt benchmarks/examples.txt
