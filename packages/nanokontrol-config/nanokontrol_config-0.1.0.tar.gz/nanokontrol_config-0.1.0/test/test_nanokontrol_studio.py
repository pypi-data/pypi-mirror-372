#!/usr/bin/env python3

""" """

from nanokontrol_config.nanokontrol_studio import (
    GlobalConfig,
    GlobalConfigMessage,
    SceneConfig,
    SysexMessage,
    NanoKontrolSysexMessage,
    DeviceConnection,
    DeviceInquiryRequestMessage,
    DeviceInquiryReplyMessage,
    RequestGlobalConfigMessage,
    SetSceneNumberMessage,
    RequestCurrentSceneConfigMessage,
    SceneConfigMessage,
)
from itertools import batched


def test_messages():
    payload = bytes.fromhex(
        "51 "
        "70 00 00 01 00 7F 7F 7F "
        "01 7F 6E 6E 6E 6E 4B 4F "
        "00 4E 54 52 4F 4C 20 53 "
        "00 74 75 64 69 6F 00 00 "
        "40 00 00 00 00 00 00 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "61 7F 00 01 00 00 7F 7F "
        "43 7F 7F 04 00 02 00 7F "
        "67 7F 7F 7F 00 00 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "03 7F 7F"
    )

    m = GlobalConfigMessage(midi_channel=5, payload=payload)
    repacked = GlobalConfigMessage.pack_7b(m.unpacked)
    assert repacked == payload[1:-3]
    assert SysexMessage.from_raw(m.serialized()) == m


def test_config():
    def dump(d):
        for chunk in batched(enumerate(d), 8):
            print(NanoKontrolSysexMessage.formatted(chunk))

    c = SceneConfig.default(0)
    serialized = c.serialize()
    # dump(serialized)
    print(len(serialized))


def test_global_config_roundtrip():
    with DeviceConnection("nanoKONTROL Studio") as connection:
        reply = connection.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        device_inquiry_reply = reply[-1]
        midi_channel = device_inquiry_reply.midi_channel()

        reply = connection.get_reply(
            RequestGlobalConfigMessage(midi_channel=midi_channel)
        )
        assert isinstance(reply[0], GlobalConfigMessage)
        global_config_message = reply[0]
        # global_config_message.dump()
        global_config = GlobalConfig.from_raw(global_config_message.unpacked)
        # global_config.dump()
        # print(global_config.serialize())
        new_global_config_message = GlobalConfigMessage(
            midi_channel=midi_channel, unpacked=global_config.serialize()
        )
        # new_global_config_message.dump()
        assert (
            global_config_message.unpacked[36:]
            == global_config.serialize()[36:]
        )
        assert (
            156
            == len(new_global_config_message.serialized())
            == len(global_config_message.serialized())
        )
        # assert new_global_config_message.payload() == global_config_message.payload()
        assert (
            148
            == len(new_global_config_message.payload())
            == len(global_config_message.payload())
        )


def test_scene_roundtrip():
    with DeviceConnection("nanoKONTROL Studio") as connection:
        reply = connection.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        device_inquiry_reply = reply[-1]
        midi_channel = device_inquiry_reply.midi_channel()

        reply = connection.get_reply(
            SetSceneNumberMessage(midi_channel=midi_channel, scene_number=0)
        )

        reply = connection.get_reply(DeviceInquiryRequestMessage())

        reply = connection.get_reply(
            RequestCurrentSceneConfigMessage(midi_channel=midi_channel)
        )
        assert isinstance(reply[0], SceneConfigMessage)
        scene_data_message = reply[0]
        # scene_data_message.dump()

        scene_config = SceneConfig.from_raw(scene_data_message.unpacked)

        reply = connection.get_reply(DeviceInquiryRequestMessage())

        new_scene_data_message = SceneConfigMessage(
            midi_channel=midi_channel, unpacked=scene_config.serialize()
        )
        # print()
        # new_scene_data_message.dump()
        assert scene_data_message.unpacked == scene_config.serialize()
        assert new_scene_data_message.payload() == scene_data_message.payload()


if __name__ == "__main__":
    test_messages()
    test_config()
    test_global_config_roundtrip()
    test_scene_roundtrip()
