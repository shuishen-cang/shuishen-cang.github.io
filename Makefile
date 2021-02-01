
all: pyset
	hugo server --buildDrafts -d docs

install: pyset
	hugo --baseURL="http://localhost/" -d docs --buildDrafts
	sudo cp -r docs/* /var/www/html/	
	@echo http://localhost/

remote:clean pyset
	hugo --baseURL="https://shuishen-cang.github.io/" -d docs
	git add .
	git commit -m "updates $(date)"
	git push origin main
	@echo https://shuishen-cang.github.io/

pyset:
	python3 convert.py

clean:
	rm -rf docs public resources