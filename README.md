## Applied Machine Learning Vorlesung

### Build and run the docker container 

- first start the redis server 
- if you want to use docker to test the api you have to create a docker network then define it during the run phase 
- then define the needed ENV to start the api
---
        docker build --tag api-aml .

        docker run -it -p 8080:5000 --name api-aml 
            -e REDIS_HOST=some-redis \
            -e REDIS_PORT=prot \
            -e REDIS_PASSWORD=redis-password \
            api-aml
---



### Interfaces

- GET /song?id="": this will loud the json data for the song with the id and send it back to the application 

