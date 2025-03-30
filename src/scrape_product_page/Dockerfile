FROM public.ecr.aws/sam/build-python3.13:latest-x86_64

# Install dependencies
RUN dnf install -y -q atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip \
    wget > /dev/null

# Define Chrome and ChromeDriver versions
ENV CHROME_VERSION=134.0.6998.90
ENV CHROME_DRIVER_VERSION=134.0.6998.90

# Download and install Chrome
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chrome-linux64.zip" && \
    unzip -q chrome-linux64.zip && \
    mkdir -p /opt/google/chrome && \
    mv chrome-linux64/* /opt/google/chrome/ && \
    ln -sf /opt/google/chrome/chrome /usr/bin/google-chrome && \
    chmod +x /opt/google/chrome/chrome && \
    rm -rf chrome-linux64 chrome-linux64.zip

# Download and install ChromeDriver
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_DRIVER_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip -q chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64 chromedriver-linux64.zip

RUN google-chrome --version && chromedriver --version

# Copy function code and install dependencies
COPY app.py ./
COPY requirements.txt ./
RUN pip install -q -r requirements.txt

# Set the CMD to your handler
CMD [ "app.lambda_handler" ]