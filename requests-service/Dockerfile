# Usamos una imagen base de Go
FROM golang:1.24-alpine

# Seteamos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos del proyecto al contenedor
COPY go.mod go.sum ./
RUN go mod download

# Copiamos el código fuente al contenedor
COPY . .

# Exponemos el puerto donde corre el servicio
EXPOSE 5018

# Comando para iniciar la aplicación
CMD ["go", "run", "main.go"]