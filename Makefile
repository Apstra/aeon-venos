all:
	python setup.py sdist

clean:
	python setup.py clean
	rm -rf dist/
	rm -rf build/
	find . -name '*.egg-info' | xargs rm -rf
