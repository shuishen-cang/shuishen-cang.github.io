
all:
	hugo server -D

install:
	hugo --baseURL="http://localhost/" -D
	sudo cp -r public/* /var/www/html/	
	@echo http://localhost/

remote:
	hugo --baseURL="shuishen-cang.github.io/" -D
	@echo shuishen-cang.github.io

	

clean:
	rm -rf public