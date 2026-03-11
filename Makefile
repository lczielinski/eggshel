.PHONY: clean examples benchmarks
clean:
	find benchmarks -name "*.results" -delete

examples:
	python3 -m eggshel -f benchmarks/examples.txt

# benchmarks:
# 	python3 -m eggshel -f benchmarks/benchmarks.txt
