start-ui:
    sudo docker-compose -f docker-compose.test.yml up --build
stop-ui:
    sudo docker-compose -f docker-compose.test.yml down 
spawn-local:
    yarn local
start-dev:
    sudo docker-compose -f docker-compose.test.yml up --build
    npx prisma studio
spawn-prisma:
    npx prisma studio
watch-images:
    watch sudo docker images -a 
show-containers:
    sudo docker ps -a




