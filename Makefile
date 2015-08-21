
release:
ifndef VERSION
	$(error VERSION is undefined)
endif

	git checkout -b ${VERSION}-release master

	sed -i '' -e "s/version='[^']*'/version='${VERSION}'/" setup.py
	git add setup.py
	git commit -m "Tagging version ${VERSION}"

	#git tag ${VERSION}
	#git push origin ${VERSION}

	# Package and upload to pypi
	#python setup.py sdist register upload

	git checkout master
	git merge --ff ${VERSION}-release
	git push origin master
	git branch -D ${VERSION}-release
