import base64
import binascii
import json
import os

import boto3
from botocore.exceptions import ClientError, ParamValidationError

REGION = os.environ.get("AWS_REGION", "us-east-1")
s3 = boto3.client("s3", region_name=REGION)


def response(status, data):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data, ensure_ascii=False),
    }


def parse_body(event):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body) if isinstance(body, str) else body


def aws_error(exc):
    err = exc.response.get("Error", {})
    code = err.get("Code", "AWS_ERROR")
    status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 500)
    return response(status if status >= 400 else 500, {"ok": False, "error": code, "mensaje": err.get("Message", "Error de AWS")})


def crear_bucket(event, context):
    try:
        data = parse_body(event)
        bucket = data["bucket"].strip()
        if not bucket:
            return response(400, {"ok": False, "mensaje": "bucket es obligatorio"})
        params = {"Bucket": bucket}
        if REGION != "us-east-1":
            params["CreateBucketConfiguration"] = {"LocationConstraint": REGION}
        s3.create_bucket(**params)
        return response(201, {"ok": True, "bucket": bucket, "region": REGION})
    except (KeyError, ValueError, TypeError, json.JSONDecodeError, ParamValidationError) as e:
        return response(400, {"ok": False, "mensaje": str(e)})
    except ClientError as e:
        return aws_error(e)


def crear_directorio(event, context):
    try:
        data = parse_body(event)
        bucket = data["bucket"].strip()
        directorio = data["directorio"].strip().strip("/")
        if not bucket or not directorio or ".." in directorio.split("/"):
            return response(400, {"ok": False, "mensaje": "bucket o directorio invalido"})
        key = directorio + "/"
        # En S3 no hay carpetas reales: se crea un objeto vacio cuya clave acaba en '/'.
        s3.put_object(Bucket=bucket, Key=key, Body=b"")
        return response(201, {"ok": True, "bucket": bucket, "directorio": key})
    except (KeyError, ValueError, TypeError, json.JSONDecodeError, ParamValidationError) as e:
        return response(400, {"ok": False, "mensaje": str(e)})
    except ClientError as e:
        return aws_error(e)


def subir_archivo(event, context):
    try:
        data = parse_body(event)
        bucket = data["bucket"].strip()
        directorio = data["directorio"].strip().strip("/")
        nombre = data["nombre_archivo"].strip()
        contenido = data["contenido_base64"]
        if not bucket or not directorio or not nombre or "/" in nombre or "\\" in nombre or ".." in directorio.split("/"):
            return response(400, {"ok": False, "mensaje": "Ruta de archivo invalida"})
        contenido_bytes = base64.b64decode(contenido, validate=True)
        if len(contenido_bytes) > 3 * 1024 * 1024:
            return response(413, {"ok": False, "mensaje": "Archivo demasiado grande para este ejemplo (maximo 3 MiB)"})
        key = directorio + "/" + nombre
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=contenido_bytes,
            ContentType=data.get("content_type", "application/octet-stream"),
        )
        return response(201, {"ok": True, "bucket": bucket, "archivo": key, "bytes": len(contenido_bytes)})
    except (KeyError, ValueError, TypeError, binascii.Error, json.JSONDecodeError, ParamValidationError) as e:
        return response(400, {"ok": False, "mensaje": str(e)})
    except ClientError as e:
        return aws_error(e)
