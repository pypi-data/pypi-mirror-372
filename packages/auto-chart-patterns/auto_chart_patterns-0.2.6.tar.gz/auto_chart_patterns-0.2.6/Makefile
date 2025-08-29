.PHONY: build test upload clean

build:
	python -m build

test:
	hatch env run test

upload:
	python -m twine upload --skip-existing dist/*

clean:
	rm -rf dist/ build/ *.egg-info/

# Upload to test PyPI
upload-test:
	python -m twine upload --skip-existing --repository testpypi dist/*