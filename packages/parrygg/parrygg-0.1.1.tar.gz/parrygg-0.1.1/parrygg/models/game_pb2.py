
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'models/game.proto')
_sym_db = _symbol_database.Default()
from ..models import image_pb2 as models_dot_image__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11models/game.proto\x12\x0eparrygg.models\x1a\x12models/image.proto"\\\n\x04Game\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12%\n\x06images\x18\x04 \x03(\x0b2\x15.parrygg.models.Image"\x1c\n\x0cGameMutation\x12\x0c\n\x04name\x18\x01 \x01(\tB\x18\n\x14gg.parry.grpc.modelsP\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.game_pb2', _globals)
if (not _descriptor._USE_C_DESCRIPTORS):
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x14gg.parry.grpc.modelsP\x01'
    _globals['_GAME']._serialized_start = 57
    _globals['_GAME']._serialized_end = 149
    _globals['_GAMEMUTATION']._serialized_start = 151
    _globals['_GAMEMUTATION']._serialized_end = 179
