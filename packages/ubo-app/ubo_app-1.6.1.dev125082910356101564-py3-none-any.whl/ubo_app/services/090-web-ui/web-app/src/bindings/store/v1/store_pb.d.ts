import * as jspb from 'google-protobuf'

import * as google_protobuf_any_pb from 'google-protobuf/google/protobuf/any_pb'; // proto import: "google/protobuf/any.proto"
import * as ubo_v1_ubo_pb from '../../ubo/v1/ubo_pb'; // proto import: "ubo/v1/ubo.proto"


export class DispatchActionRequest extends jspb.Message {
  getAction(): ubo_v1_ubo_pb.Action | undefined;
  setAction(value?: ubo_v1_ubo_pb.Action): DispatchActionRequest;
  hasAction(): boolean;
  clearAction(): DispatchActionRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DispatchActionRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DispatchActionRequest): DispatchActionRequest.AsObject;
  static serializeBinaryToWriter(message: DispatchActionRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DispatchActionRequest;
  static deserializeBinaryFromReader(message: DispatchActionRequest, reader: jspb.BinaryReader): DispatchActionRequest;
}

export namespace DispatchActionRequest {
  export type AsObject = {
    action?: ubo_v1_ubo_pb.Action.AsObject,
  }
}

export class DispatchEventRequest extends jspb.Message {
  getEvent(): ubo_v1_ubo_pb.Event | undefined;
  setEvent(value?: ubo_v1_ubo_pb.Event): DispatchEventRequest;
  hasEvent(): boolean;
  clearEvent(): DispatchEventRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DispatchEventRequest.AsObject;
  static toObject(includeInstance: boolean, msg: DispatchEventRequest): DispatchEventRequest.AsObject;
  static serializeBinaryToWriter(message: DispatchEventRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DispatchEventRequest;
  static deserializeBinaryFromReader(message: DispatchEventRequest, reader: jspb.BinaryReader): DispatchEventRequest;
}

export namespace DispatchEventRequest {
  export type AsObject = {
    event?: ubo_v1_ubo_pb.Event.AsObject,
  }
}

export class DispatchActionResponse extends jspb.Message {
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DispatchActionResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DispatchActionResponse): DispatchActionResponse.AsObject;
  static serializeBinaryToWriter(message: DispatchActionResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DispatchActionResponse;
  static deserializeBinaryFromReader(message: DispatchActionResponse, reader: jspb.BinaryReader): DispatchActionResponse;
}

export namespace DispatchActionResponse {
  export type AsObject = {
  }
}

export class DispatchEventResponse extends jspb.Message {
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DispatchEventResponse.AsObject;
  static toObject(includeInstance: boolean, msg: DispatchEventResponse): DispatchEventResponse.AsObject;
  static serializeBinaryToWriter(message: DispatchEventResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DispatchEventResponse;
  static deserializeBinaryFromReader(message: DispatchEventResponse, reader: jspb.BinaryReader): DispatchEventResponse;
}

export namespace DispatchEventResponse {
  export type AsObject = {
  }
}

export class SubscribeEventRequest extends jspb.Message {
  getEvent(): ubo_v1_ubo_pb.Event | undefined;
  setEvent(value?: ubo_v1_ubo_pb.Event): SubscribeEventRequest;
  hasEvent(): boolean;
  clearEvent(): SubscribeEventRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SubscribeEventRequest.AsObject;
  static toObject(includeInstance: boolean, msg: SubscribeEventRequest): SubscribeEventRequest.AsObject;
  static serializeBinaryToWriter(message: SubscribeEventRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SubscribeEventRequest;
  static deserializeBinaryFromReader(message: SubscribeEventRequest, reader: jspb.BinaryReader): SubscribeEventRequest;
}

export namespace SubscribeEventRequest {
  export type AsObject = {
    event?: ubo_v1_ubo_pb.Event.AsObject,
  }
}

export class SubscribeEventResponse extends jspb.Message {
  getEvent(): ubo_v1_ubo_pb.Event | undefined;
  setEvent(value?: ubo_v1_ubo_pb.Event): SubscribeEventResponse;
  hasEvent(): boolean;
  clearEvent(): SubscribeEventResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SubscribeEventResponse.AsObject;
  static toObject(includeInstance: boolean, msg: SubscribeEventResponse): SubscribeEventResponse.AsObject;
  static serializeBinaryToWriter(message: SubscribeEventResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SubscribeEventResponse;
  static deserializeBinaryFromReader(message: SubscribeEventResponse, reader: jspb.BinaryReader): SubscribeEventResponse;
}

export namespace SubscribeEventResponse {
  export type AsObject = {
    event?: ubo_v1_ubo_pb.Event.AsObject,
  }
}

export class SubscribeStoreRequest extends jspb.Message {
  getSelectorsList(): Array<string>;
  setSelectorsList(value: Array<string>): SubscribeStoreRequest;
  clearSelectorsList(): SubscribeStoreRequest;
  addSelectors(value: string, index?: number): SubscribeStoreRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SubscribeStoreRequest.AsObject;
  static toObject(includeInstance: boolean, msg: SubscribeStoreRequest): SubscribeStoreRequest.AsObject;
  static serializeBinaryToWriter(message: SubscribeStoreRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SubscribeStoreRequest;
  static deserializeBinaryFromReader(message: SubscribeStoreRequest, reader: jspb.BinaryReader): SubscribeStoreRequest;
}

export namespace SubscribeStoreRequest {
  export type AsObject = {
    selectorsList: Array<string>,
  }
}

export class SubscribeStoreResponse extends jspb.Message {
  getResultsList(): Array<google_protobuf_any_pb.Any>;
  setResultsList(value: Array<google_protobuf_any_pb.Any>): SubscribeStoreResponse;
  clearResultsList(): SubscribeStoreResponse;
  addResults(value?: google_protobuf_any_pb.Any, index?: number): google_protobuf_any_pb.Any;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SubscribeStoreResponse.AsObject;
  static toObject(includeInstance: boolean, msg: SubscribeStoreResponse): SubscribeStoreResponse.AsObject;
  static serializeBinaryToWriter(message: SubscribeStoreResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SubscribeStoreResponse;
  static deserializeBinaryFromReader(message: SubscribeStoreResponse, reader: jspb.BinaryReader): SubscribeStoreResponse;
}

export namespace SubscribeStoreResponse {
  export type AsObject = {
    resultsList: Array<google_protobuf_any_pb.Any.AsObject>,
  }
}

