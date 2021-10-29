#Set Image
FROM python:3.6.4

#Set Working Dir
WORKDIR /code


#Copy Depedencies and files
COPY requirements.txt .
COPY src/ .


#Update pip
RUN pip install --upgrade pip

#Install Depedencies
RUN pip install -r requirements.txt


# command to run on container start
CMD [ "python", "/code/app.py" ]

