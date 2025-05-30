# Create the network 'jenkins'
docker network create jenkins

# Build the Jenkins BlueOcean Docker Image
docker build -t myjenkins-blueocean .

# Run the Container
docker run --name jenkins-blueocean --restart=on-failure --detach \
  --network jenkins --env DOCKER_HOST=tcp://docker:2376 \
  --env DOCKER_CERT_PATH=/certs/client --env DOCKER_TLS_VERIFY=1 \
  --publish 8080:8080 --publish 50000:50000 \
  --volume jenkins-data:/var/jenkins_home \
  --volume jenkins-docker-certs:/certs/client:ro \
  myjenkins-blueocean

# Get the Password
docker exec jenkins-blueocean cat /var/jenkins_home/secrets/initialAdminPassword

# Ingresar al contenedor
docker exec -it jenkins-blueocean bash
docker exec -u root -it jenkins-blueocean bash
apt update && apt upgrade -y
apt install python3 -y
python3 --version

# Ollama
docker build -f Dockerfile.ollama -t myollama .

# Ejecutar todo
## Comando basico:
docker-compose up

## Ejecutar en segundo plano (detached mode):
docker-compose up -d

docker-compose down
docker rmi thesis_project-ollama  # or whatever your image is named
docker-compose up --build

## Descargar modelo
docker exec -it ollama ollama pull deepseek-coder:6.7b

# Referencias
https://www.jenkins.io/doc/book/installing/docker/
https://www.youtube.com/watch?v=6YZvp2GwT0A&ab_channel=DevOpsJourney
https://github.com/devopsjourney1/jenkins-101