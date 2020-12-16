
all:
	hugo server -D

install:
	hugo --baseURL="http://localhost/" -D
	sudo cp -r public/* /var/www/html/	
	@echo http://localhost/

remote:
	hugo --baseURL="https://shuishen-cang.github.io/" -D
	@echo https://shuishen-cang.github.io/

	

clean:
	rm -rf public