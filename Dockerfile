#
# Build stage - repackage spring boot application
#
FROM maven:3.8.3-openjdk-17-slim AS builder
COPY src /home/app/src
COPY pom.xml /home/app/
RUN mvn -f /home/app/pom.xml clean package spring-boot:repackage

#
# Package stage - use jar from previous stage, add jupyter notebook and start
#
FROM openjdk:17.0.1-jdk-slim

# copy the built target jar from the previous stage
COPY --from=builder /home/app/target/api-0.0.1.jar /usr/local/lib/api.jar

# add conda env for jupyter notebook
COPY --from=continuumio/anaconda3 / /
RUN apt-get update
RUN apt-get -y install curl 
RUN apt-get -y install texlive-xetex

# copy static resources for jupyter
COPY src/main/resources /usr/local/resources

# start the server
WORKDIR /home/app
EXPOSE 8080
ENTRYPOINT ["java","-jar","/usr/local/lib/api.jar"]
