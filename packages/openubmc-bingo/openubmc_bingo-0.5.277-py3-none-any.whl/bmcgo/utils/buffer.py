#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Huawei Technologies Co., Ltd. 2025. All rights reserved.

MAX_BUFFER_LENGTH = 4 * 1024 * 1024 * 1024


class BufferOverflowException(Exception):
    def __init__(self, message="The data to be input to buffer is out of range."):
        super().__init__(message)

    def get_class_name(self):
        return "BufferOverflowException"


class Buffer:
    def __init__(self, buf_len: int, little_endian: bool = True):
        if buf_len > MAX_BUFFER_LENGTH:
            self.buf = bytearray(MAX_BUFFER_LENGTH)
        elif buf_len > 0:
            self.buf = bytearray(buf_len)
        else:
            raise ValueError(f"Invalid buffer length: buf_len={buf_len}")
        self.size = len(self.buf)
        self.pos = 0
        self.marker = -1
        self.bo = little_endian

    def capacity(self):
        # 字节缓冲区容量
        return self.size

    def position(self):
        # 此缓冲区当前输入位置
        return self.pos

    def set_position(self, new_pos: int):
        # 设置此缓冲区输入位置
        if new_pos > self.size or new_pos < 0:
            raise ValueError("Position out of range")
        self.pos = new_pos

    def put(self, b: bytearray):
        # 将字节数组写入当前位置的缓冲区并递增位置
        if len(b) > self.size - self.pos:
            raise BufferOverflowException()
        if self.bo:
            self.buf[self.pos:self.pos + len(b)] = b
        else:
            self.buf[self.pos:self.pos + len(b)] = b[::-1]
        self.pos += len(b)

    def put_uint8(self, v: int):
        # 按当前字节顺序将1字节无符号整数写入此缓冲区，位置递增1
        if self.size - self.pos < 1:
            raise BufferOverflowException()
        self.buf[self.pos] = v
        self.pos += 1

    def put_uint16(self, v: int):
        # 按当前字节顺序将一个2字节无符号整数写入此缓冲区，位置递增2
        if self.size - self.pos < 2:
            raise BufferOverflowException()
        n = v
        start = self.pos
        for i in range(2):
            if self.bo:
                self.buf[self.pos] = n & 0xFF
            else:
                self.buf[start + 1 - i] = n & 0xFF
            n >>= 8
            self.pos += 1

    def put_uint32(self, v: int):
        #按当前字节顺序将一个4字节无符号整数写入此缓冲区，位置递增4
        if self.size - self.pos < 4:
            raise BufferOverflowException()
        n = v
        start = self.pos
        for i in range(4):
            if self.bo:
                self.buf[self.pos] = n & 0xFF
            else:
                self.buf[start + 3 - i] = n & 0xFF
            n >>= 8
            self.pos += 1

    def put_uint64(self, v: int):
        # 按当前字节顺序将一个8字节无符号整数写入此缓冲区，位置递增8
        if self.size - self.pos < 8:
            raise BufferOverflowException()
        n = v
        if self.bo:
            self.put_uint32(n & 0xFFFFFFFF)
            self.put_uint32(n >> 32) 
        else:
            start = self.pos
            for i in range(8):
                self.buf[start + 7 - i] = n & 0xFF
                n >>= 8
                self.pos += 1

    def mark(self):
        # 将此缓冲区的标记设置在其位置
        self.marker = self.pos
        return self

    def reset(self):
        # 将此缓冲区的位置重置为先前标记的位置
        if self.marker < 0:
            raise BufferOverflowException("The marker of buffer is invalid.")
        self.pos = self.marker
        return self
    
    def clean(self):
        # 重置此缓冲区位置及标志位
        self.pos = 0
        self.marker = -1
        return self

    def array(self):
        # 返回缓冲区的字节数组
        return self.buf 


def round_up_data_size(data_size: int) -> int:
    # 对齐数据字节量为8的倍数
    return ((data_size + 7) // 8) * 8
