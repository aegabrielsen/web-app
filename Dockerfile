FROM python:3.8.2
# Set the home directory to /root
ENV HOME=/root
# cd into the home directory
WORKDIR /root

# Copy all app files into the image
COPY . .

# Download dependancies
RUN pip3 install -r requirements.txt

# Allow port 8000 to be accessed
# from outside the container
EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
# Run the app
RUN chmod +x /wait
CMD /wait && python3 -u manage.py

# Copy entrypoint script
#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

# Set entrypoint
#ENTRYPOINT ["/entrypoint.sh"]
