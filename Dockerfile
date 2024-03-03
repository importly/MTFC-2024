# Use the latest official AWS Lambda Python 3.6 runtime image
FROM public.ecr.aws/lambda/python:3.6

# Working directory
WORKDIR /var/task

# Copy your project files into the container (replace './your-project' if needed)
COPY . /var/task/

# Install necessary packages
RUN pip install torch==1.4.0 transformers==2.11.0 attrdict

