
all:
	hugo server --buildDrafts

install:
	hugo --baseURL="http://localhost/" -d docs --buildDrafts
	sudo cp -r docs/* /var/www/html/	
	@echo http://localhost/

remote:clean
	hugo --baseURL="https://shuishen-cang.github.io/" -d docs
	git add .
	git commit -m "updates $(date)"
	git push origin main
	@echo https://shuishen-cang.github.io/


clean:
	rm -rf docs public