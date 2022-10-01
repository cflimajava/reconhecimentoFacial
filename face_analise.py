import json

import boto3

s3 = boto3.resource('s3')
client = boto3.client('rekognition')


def detecta_faces():
    return client.index_faces(
        CollectionId='faces',
        DetectionAttributes=['DEFAULT'],
        ExternalImageId='TEMPORARIA',
        Image={
            'S3Object': {
                'Bucket': 'clf-bucket',
                'Name': '_analise_2.png',
            }
        }
    )


def get_imageId_dectectadas(img_encontradas):
    ids = []
    for img in range(len(img_encontradas['FaceRecords'])):
        ids.append(img_encontradas['FaceRecords'][img]['Face']['FaceId'])
    return ids


def compara_imagens(img_detectadas):
    img_comparadas = []
    for ids in img_detectadas:
        img_comparadas.append(
            client.search_faces(
                CollectionId='faces',
                FaceId=ids,
                FaceMatchThreshold=95,
                MaxFaces=10,
            )
        )
    return img_comparadas

def gera_dados_json(img_comparadas):
    dados_json=[]
    for face_matches in img_comparadas:
        if(len(face_matches.get('FaceMatches')) >= 1):
            perfil = dict(nome=face_matches['FaceMatches'][0]['Face']['ExternalImageId'],
                          faceMatch=round(face_matches['FaceMatches'][0]['Similarity'], 2))
            dados_json.append(perfil)
    return dados_json

def publica_dados(faces_conhecidas):
    arquivo = s3.Object('cfl-site', 'dados.json')
    arquivo.put(Body=json.dumps(faces_conhecidas))

def exclui_imagens_temporarias(lista_id_imagens_temporarias):
    client.delete_faces(
        CollectionId='faces',
        FaceIds=lista_id_imagens_temporarias
    )

def main(event, context):
    faces_detectadas = detecta_faces()
    img_ids = get_imageId_dectectadas(faces_detectadas)
    img_comparadas = compara_imagens(img_ids)
    faces_conhecidas = gera_dados_json(img_comparadas)
    publica_dados(faces_conhecidas)
    exclui_imagens_temporarias(img_ids)
    print(json.dumps(faces_conhecidas, indent=4))
