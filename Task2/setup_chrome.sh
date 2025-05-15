# Create a tools directory
mkdir -p ~/chrome-tools && cd ~/chrome-tools

# Download Chrome and ChromeDriver
wget https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.94/linux64/chrome-linux64.zip
wget https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.94/linux64/chromedriver-linux64.zip

# Unzip
unzip chrome-linux64.zip
unzip chromedriver-linux64.zip

# Move binaries to known locations
sudo mv chrome-linux64 /opt/chrome
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
sudo ln -sf /opt/chrome/chrome /usr/bin/google-chrome
