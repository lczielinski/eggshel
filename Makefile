.PHONY: clean examples
clean:
	find benchmarks examples -name "*.egg" -delete

examples:
	bash eggshel.sh examples/examples.txt
