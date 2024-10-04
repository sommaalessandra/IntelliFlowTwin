from django.db import models
import json
import mongoengine as me
from bson import ObjectId
from mongoengine import Document, StringField, DictField, FloatField, EmbeddedDocument, EmbeddedDocumentField, ListField, PointField

# Create your models here.
class Simulator(models.Model):
    configurationPath = models.CharField(max_length=255)
    routeFilePath = models.CharField(max_length=255)

class Misuration(models.Model):
    entity_id = models.CharField(max_length=255)
    time_index = models.DateTimeField()
    trafficflow = models.IntegerField()
    class Meta:
        db_table = 'mtopeniot.etdevice'
        managed = False



class DeviceID(EmbeddedDocument):
    id = StringField()  # Qui sarà 'urn:ngsi-ld:Device:TL26'
    type = StringField()  # Tipo come 'https://uri.etsi.org/ngsi-ld/default-context/Device'
    servicePath = StringField()  # Qui sarà '/'

# Metadata embedded document per i metadati come observedAt
class Metadata(EmbeddedDocument):
    observedAt = FloatField()

# Attributo embedded document per i vari attributi come trafficFlow, location, ecc.
class Attribute(EmbeddedDocument):
    value = DictField()  # Qui può essere un valore complesso, quindi DictField è meglio
    type = StringField()
    md = EmbeddedDocumentField(Metadata)
    creDate = FloatField()
    modDate = FloatField()

# Modello principale Device
class Device(Document):
    _id = EmbeddedDocumentField(DeviceID)
    attrNames = ListField(StringField())  # Lista di stringhe
    # attrs = DictField(EmbeddedDocumentField(Attribute))  # Usa EmbeddedDocument per gli attributi
    attrs = DictField()
    creDate = FloatField()
    modDate = FloatField()
    lastCorrelator = StringField()  # Aggiungi il campo lastCorrelator qui
    meta = {
        'collection': 'entities'
    }


# class Device(me.Document):
#     _id = me.ObjectIdField(primary_key=True, default=ObjectId)
#     name = me.StringField(max_length=100)
#     description = me.StringField()
#
#     meta = {
#         'collection': 'nome_della_tua_collection',  # Specifica la collection
#     }
#
#     def __str__(self):
#         return self.name



