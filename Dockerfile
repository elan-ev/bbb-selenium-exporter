FROM docker.io/library/debian:buster-slim

RUN apt update -qq \
    && apt upgrade -qqy \
    && apt install -qqy curl unzip sudo python3-setuptools

RUN curl -s -O https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -qqy ./google-chrome-stable_current_amd64.deb \
    && rm ./google-chrome-stable_current_amd64.deb

RUN curl -O "https://chromedriver.storage.googleapis.com/$(curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /bin/chromedriver \
	 && rm chromedriver_linux64.zip

ADD README.md setup.py /
ADD bbb_selenium_exporter /bbb_selenium_exporter
RUN python3 setup.py install
RUN mkdir -p /etc/bbb-selenium-exporter/ \
    && echo 'test-install.blindsidenetworks.com 8cd8ef52e8e101574e400365b55e11a6' > /etc/bbb-selenium-exporter/targets

RUN useradd --create-home selenium
USER selenium

EXPOSE 9123
CMD bbb-selenium-exporter
