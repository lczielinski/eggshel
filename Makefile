.PHONY: clean examples benchmarks
clean:
	find benchmarks -name "*.results" -delete

docker:
	docker build -t eggshel . 
	docker run -it --rm eggshel

examples:
	python3 -m eggshel -f benchmarks/examples.txt

# benchmarks:
# 	python3 -m eggshel -f benchmarks/benchmarks.txt
