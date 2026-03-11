.PHONY: clean examples
clean:
	find benchmarks examples -name "*.egg" -delete

examples:
	python3 -m eggshel -f examples/examples.txt

benchmarks:
	python3 -m eggshel -f benchmarks/benchmarks.txt