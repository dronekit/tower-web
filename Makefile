.PHONY: all bundle

bundle:
	rm -rf wheelhouse
	pip wheel -r ./requirements.txt --build-option="--plat-name=py27"

deploy:
	rsync -avz --exclude="*.pyc" --exclude=".git" --delete --exclude="env" ./ solo:/log/realtimeearth
