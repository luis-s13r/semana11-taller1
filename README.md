# Taller S11: AWS S3 / Serverless

Ejemplo autónomo de las tres funciones del ejercicio propuesto. Si ya tienes un `serverless.yml`, **no lo reemplaces**: añade las nuevas funciones bajo tu bloque `functions:` y los permisos adecuados a la función IAM/rol que ya utiliza tu proyecto.

## Archivos
- `handler.py`: tres lambdas Python con boto3.
- `serverless.yml`: ejemplo completo para proyecto nuevo.

## Pasos
1. En una terminal con AWS configurado, ejecuta `aws sts get-caller-identity`, `node -v`, `npx serverless --version`.
2. Despliega: `npx serverless deploy --stage dev`.
3. Guarda el dominio y la ruta indicados por Serverless.
4. Despliega: `npx serverless deploy --stage test` y `npx serverless deploy --stage prod`.

**Nombres de buckets:** deben ser globalmente únicos y comenzar con `taller11-` por la política IAM de ejemplo. Usa algo como `taller11-<identificador-unico>-dev` (solo minúsculas, dígitos y guiones; reemplaza los signos de menor/mayor y el texto). Si tu entorno académico utiliza un rol IAM preexistente, configura ese rol según tu profesor; la política de este ejemplo no se adjunta automáticamente a roles existentes.

**Importante:** por simplicidad las rutas del ejemplo no tienen autenticación. No las dejes accesibles públicamente cuando acabes las pruebas. Una API de producción debe usar autorizador/clave API y permisos restrictivos. El despliegue y los recursos de AWS pueden generar costos.

## curl (reemplaza BASE y BUCKET)

BASE="https://TU_API_ID.execute-api.us-east-1.amazonaws.com/dev"
BUCKET="taller11-tuidentificador-dev"

```bash
curl -i -X POST "$BASE/s3/crear-bucket" -H 'Content-Type: application/json' -d "{\"bucket\":\"$BUCKET\"}"
curl -i -X POST "$BASE/s3/crear-directorio" -H 'Content-Type: application/json' -d "{\"bucket\":\"$BUCKET\",\"directorio\":\"evidencias\"}"
curl -i -X POST "$BASE/s3/subir-archivo" -H 'Content-Type: application/json' -d "{\"bucket\":\"$BUCKET\",\"directorio\":\"evidencias\",\"nombre_archivo\":\"hola.txt\",\"contenido_base64\":\"SG9sYSBBV1M=\",\"content_type\":\"text/plain\"}"
```

## Para verificar en AWS CLI

```bash
aws s3 ls
aws s3 ls "s3://$BUCKET/" --recursive
```

## Evidencias
Capturas de: despliegue dev/test/prod, curl ejecutando las tres rutas, Postman ejecutando las tres rutas, bucket y carpeta y archivo en consola S3, y funciones en Lambda/API Gateway. Pega las capturas en Word o PPT y entrega según el aula/PDF.
