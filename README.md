# 🚀 Thumbnail service 🚀
## 👷👷‍♀️ Arquitectura 👷👷‍♀️

_Tenemos un trigger que es disparado cuando cargamos una imagen, este invoca una funcion lambda la cual transforma la imagen y crea una miniatura, la cual posteriormente es almacenada en un bucket de S3, luego se almacena informacion necesaria de la imagen y el proceso en general. Toda esta informacion estara expuesta mediante el servicio de API Gateway para que usuarios puedan acceder a las imagenes y la informacion._

![Architecture Draw](/doc/ArchitectureDraw.png "Architecture Draw")

---
### _Project based in AWS cloud provider_
### _Sebas Ayala_ 😉