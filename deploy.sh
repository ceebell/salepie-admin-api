# $ docker service create \
#     --name=myservice \
#     --mount type=volume,source=test-data,target=/somewhere \
#     nginx:alpine

# myservice

# $ docker service update \
#     --mount-add type=volume,source=other-volume,target=/somewhere-else \
#     myservice

# myservice

# $ docker service update --mount-rm /somewhere myservice

# myservice


# https://docs.docker.com/storage/volumes/

# $ docker service create \
#     --mount 'type=volume,src=<VOLUME-NAME>,dst=<CONTAINER-PATH>,volume-driver=local,volume-opt=type=nfs,volume-opt=device=<nfs-server>:<nfs-path>,"volume-opt=o=addr=<nfs-address>,vers=4,soft,timeo=180,bg,tcp,rw"'
#     --name myservice \
#     <IMAGE>


# $ docker volume inspect my-vol

# $ docker service create -d \
#   --replicas=4 \
#   --name devtest-service \
#   --mount source=myvol2,target=/app \
#   nginx:latest


docker build  . -f Dockerfile -t apiimage:2

sudo docker service create   --name apiimage   --replicas=1  --mount source=thelogs,target=/Users/belliecee/testlog  -d -p 8079:80  apiimage:2