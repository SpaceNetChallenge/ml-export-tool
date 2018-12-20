# Using the official tensorflow serving image from docker hub as base image
FROM developmentseed/looking-glass:latest

# Installing NGINX, used to rever proxy the predictions from SageMaker to TF Serving
RUN apt-get update && apt-get install -y --no-install-recommends nginx git

# Copy NGINX configuration to the container
COPY nginx.conf /etc/nginx/nginx.conf

# starts NGINX and TF serving pointing to our model
ENTRYPOINT service nginx start | /usr/bin/tf_serving_entrypoint.sh