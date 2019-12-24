# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: health_checker.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='health_checker.proto',
  package='health_checker',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x14health_checker.proto\x12\x0ehealth_checker\"i\n\x10HealthCheckerMsg\x12$\n\x04ping\x18\x01 \x01(\x0b\x32\x14.health_checker.PingH\x00\x12$\n\x04pong\x18\x02 \x01(\x0b\x32\x14.health_checker.PongH\x00\x42\t\n\x07message\"\x15\n\x04Ping\x12\r\n\x05nonce\x18\x01 \x01(\r\"\x15\n\x04Pong\x12\r\n\x05nonce\x18\x01 \x01(\rb\x06proto3')
)




_HEALTHCHECKERMSG = _descriptor.Descriptor(
  name='HealthCheckerMsg',
  full_name='health_checker.HealthCheckerMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ping', full_name='health_checker.HealthCheckerMsg.ping', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pong', full_name='health_checker.HealthCheckerMsg.pong', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='health_checker.HealthCheckerMsg.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=40,
  serialized_end=145,
)


_PING = _descriptor.Descriptor(
  name='Ping',
  full_name='health_checker.Ping',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='nonce', full_name='health_checker.Ping.nonce', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=147,
  serialized_end=168,
)


_PONG = _descriptor.Descriptor(
  name='Pong',
  full_name='health_checker.Pong',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='nonce', full_name='health_checker.Pong.nonce', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=170,
  serialized_end=191,
)

_HEALTHCHECKERMSG.fields_by_name['ping'].message_type = _PING
_HEALTHCHECKERMSG.fields_by_name['pong'].message_type = _PONG
_HEALTHCHECKERMSG.oneofs_by_name['message'].fields.append(
  _HEALTHCHECKERMSG.fields_by_name['ping'])
_HEALTHCHECKERMSG.fields_by_name['ping'].containing_oneof = _HEALTHCHECKERMSG.oneofs_by_name['message']
_HEALTHCHECKERMSG.oneofs_by_name['message'].fields.append(
  _HEALTHCHECKERMSG.fields_by_name['pong'])
_HEALTHCHECKERMSG.fields_by_name['pong'].containing_oneof = _HEALTHCHECKERMSG.oneofs_by_name['message']
DESCRIPTOR.message_types_by_name['HealthCheckerMsg'] = _HEALTHCHECKERMSG
DESCRIPTOR.message_types_by_name['Ping'] = _PING
DESCRIPTOR.message_types_by_name['Pong'] = _PONG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

HealthCheckerMsg = _reflection.GeneratedProtocolMessageType('HealthCheckerMsg', (_message.Message,), {
  'DESCRIPTOR' : _HEALTHCHECKERMSG,
  '__module__' : 'health_checker_pb2'
  # @@protoc_insertion_point(class_scope:health_checker.HealthCheckerMsg)
  })
_sym_db.RegisterMessage(HealthCheckerMsg)

Ping = _reflection.GeneratedProtocolMessageType('Ping', (_message.Message,), {
  'DESCRIPTOR' : _PING,
  '__module__' : 'health_checker_pb2'
  # @@protoc_insertion_point(class_scope:health_checker.Ping)
  })
_sym_db.RegisterMessage(Ping)

Pong = _reflection.GeneratedProtocolMessageType('Pong', (_message.Message,), {
  'DESCRIPTOR' : _PONG,
  '__module__' : 'health_checker_pb2'
  # @@protoc_insertion_point(class_scope:health_checker.Pong)
  })
_sym_db.RegisterMessage(Pong)


# @@protoc_insertion_point(module_scope)