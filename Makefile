FILE ?= 

.PHONY: run
run:
	@echo "Running $(FILE)..."
	@egglog src/definitions.egg src/context.egg src/operations.egg src/share.egg examples/$(FILE).egg