
all:
	hugo server -D

install:
	hugo --baseURL="http://localhost/" -D
	sudo cp -r public/* /var/www/html/	
	@echo http://localhost/

remote:clean
	hugo --baseURL="https://shuishen-cang.github.io/" -d docs
	git add .
	git commit -m "updates $(date)"
	git push origin main
	@echo https://shuishen-cang.github.io/


clean:
	rm -rf public