import ipaddress
import socket
import struct
from typing import  Any

QTYPE_MAP = {
    1: 'A',
    2: 'NS',
    5: 'CNAME',
    6: 'SOA',
    12: 'PTR',
    15: 'MX',
    16: 'TXT',
    28: 'AAAA',
    33: 'SRV',
    35: 'NAPTR',
    43: 'DS',
    46: 'RRSIG',
    47: 'NSEC',
    48: 'DNSKEY',
    257: 'CAA',
}
QCLASS_MAP = {
    1: 'IN',
    3: 'CH',
    4: 'HS',
}

def _parse_name(packet: bytes, offset: int) -> tuple[str, int]| None:
    labels = []
    jumped = False
    orig_offset = offset
    steps = 0
    # We'll compute the 'next_offset' to return (position after the name
    # in the original stream) only if we haven't jumped (compression).
    next_offset = offset

    while True:
        if steps > 255:
            return None
        steps += 1

        if offset >= len(packet):
            return None

        length = packet[offset]
        # Compression pointer
        if (length & 0xC0) == 0xC0:
            if offset + 1 >= len(packet):
                return None
            pointer = ((length & 0x3F) << 8) | packet[offset + 1]
            if not jumped:
                next_offset = offset + 2
                jumped = True
            offset = pointer
            continue
        # End of name
        if length == 0:
            if not jumped:
                next_offset = offset + 1
            break
        # Label
        offset += 1
        end = offset + length
        if end > len(packet):
            return None
        label = packet[offset:end].decode('ascii', errors='strict')
        labels.append(label)
        offset = end

    name = '.'.join(labels) if labels else '.'
    return name, next_offset

def _parse_header(packet: bytes) -> dict[str, Any]| None:
    if len(packet) < 12:
        return None

    (ident, flags, qdcount, ancount, nscount, arcount) = struct.unpack('>HHHHHH', packet[:12])

    qr = (flags >> 15) & 0x1
    opcode = (flags >> 11) & 0xF
    aa = (flags >> 10) & 0x1
    tc = (flags >> 9) & 0x1
    rd = (flags >> 8) & 0x1
    ra = (flags >> 7) & 0x1
    z = (flags >> 4) & 0x7  # must be zero in queries/responses per RFC
    rcode = flags & 0xF

    return {
        'id': ident,
        'flags_raw': flags,
        'qr': qr,            # 0=query, 1=response
        'opcode': opcode,
        'aa': aa,
        'tc': tc,
        'rd': rd,
        'ra': ra,
        'z': z,
        'rcode': rcode,
        'qdcount': qdcount,
        'ancount': ancount,
        'nscount': nscount,
        'arcount': arcount,
    }

def _parse_question(packet: bytes, offset: int) -> tuple[dict[str, Any], int]| None:
    _parsed = _parse_name(packet, offset)
    if _parsed is None:
        return None
    qname, offset = _parsed
    if offset + 4 > len(packet):
        return None
    qtype, qclass = struct.unpack('>HH', packet[offset:offset + 4])
    offset += 4
    return {
        'qname': qname,
        'qtype': QTYPE_MAP.get(qtype, qtype),
        'qclass': QCLASS_MAP.get(qclass, qclass),
        'qtype_raw': qtype,
        'qclass_raw': qclass,
    }, offset

def _parse_rdata(packet: bytes, rtype: int, rclass: int, rdata: bytes, msg: bytes, start_of_msg: int) -> Any:
    # rclass usually IN (1); not strictly used for parsing except context
    try:
        if rtype == 1:  # A
            return str(ipaddress.IPv4Address(rdata))
        if rtype == 28:  # AAAA
            return str(ipaddress.IPv6Address(rdata))
        if rtype in (2, 5, 12):  # NS, CNAME, PTR
            parsed_name = _parse_name(msg, start_of_msg)
            if parsed_name is None:
                return None
            name, _ = parsed_name
            return name
        if rtype == 15:  # MX
            if len(rdata) < 2:
                return None
            pref = struct.unpack('>H', rdata[:2])[0]
            parsed_name =  _parse_name(msg, start_of_msg + 2)
            if parsed_name is None:
                return None
            name, _ = parsed_name
            return {'preference': pref, 'exchange': name}
        if rtype == 16:  # TXT (one or more length-prefixed strings)
            texts = []
            i = 0
            while i < len(rdata):
                ln = rdata[i]
                i += 1
                if i + ln > len(rdata):
                    return None
                texts.append(rdata[i:i + ln].decode('utf-8', errors='replace'))
                i += ln
            return texts
        if rtype == 33:  # SRV
            if len(rdata) < 6:
                return None
            prio, weight, port = struct.unpack('>HHH', rdata[:6])
            parsed_name = _parse_name(msg, start_of_msg + 6)
            if parsed_name is None:
                return None
            target, _ = parsed_name
            return {'priority': prio, 'weight': weight, 'port': port, 'target': target}
        if rtype == 6:  # SOA
            parsed_name = _parse_name(msg, start_of_msg)
            if parsed_name is None:
                return None
            mname, p1 = parsed_name
            parsed_name = _parse_name(msg, p1)
            if parsed_name is None:
                return None
            rname, p2 = parsed_name
            
            if p2 + 20 > len(msg):
                return None
            serial, refresh, retry, expire, minimum = struct.unpack('>IIIII', msg[p2:p2 + 20])
            return {
                'mname': mname,
                'rname': rname,
                'serial': serial,
                'refresh': refresh,
                'retry': retry,
                'expire': expire,
                'minimum': minimum,
            }
        # Default: return raw bytes hex
        return rdata.hex()
    except Exception:
        # If name parsing within RDATA needs message-relative offsets, we use start_of_msg.
        # Any failure falls back to raw hex to avoid crashing on unknown/complex types.
        return rdata.hex()

def _parse_rr(packet: bytes, offset: int) -> tuple[dict[str, Any], int]| None:
    parsed_name = _parse_name(packet, offset)
    if parsed_name is None:
        return None
    name, offset = parsed_name
    if offset + 10 > len(packet):
        return None
    rtype, rclass, ttl, rdlength = struct.unpack('>HHIH', packet[offset:offset + 10])
    offset += 10
    if offset + rdlength > len(packet):
        return None
    rdata = packet[offset:offset + rdlength]
    # For name-compressed fields inside RDATA, pass message and RDATA start offset.
    parsed = _parse_rdata(packet, rtype, rclass, rdata, packet, offset)
    if parsed is None:
        return None
    rr = {
        'name': name,
        'type': QTYPE_MAP.get(rtype, rtype),
        'class': QCLASS_MAP.get(rclass, rclass),
        'type_raw': rtype,
        'class_raw': rclass,
        'ttl': ttl,
        'rdlength': rdlength,
        'rdata': parsed,
        'rdata_raw': rdata.hex(),
    }
    offset += rdlength
    return rr, offset

def parse_dns_message(packet: bytes) -> dict[str, Any]| None:
    '''Parse a single DNS message (without the TCP 2-byte length).'''
    hdr = _parse_header(packet)
    if hdr is None:
        return None
    offset = 12
    questions = []
    for _ in range(hdr['qdcount']):
        _q =_parse_question(packet, offset)
        if _q is None:
            return None
        q, offset = _q
        questions.append(q)
    answers = []
    for _ in range(hdr['ancount']):
        parsed_rr = _parse_rr(packet, offset)
        if parsed_rr is None:
            return None
        rr, offset = parsed_rr
        answers.append(rr)
    authorities = []
    for _ in range(hdr['nscount']):
        parsed_rr = _parse_rr(packet, offset)
        if parsed_rr is None:
            return None
        rr, offset = parsed_rr
        authorities.append(rr)
    additionals = []
    for _ in range(hdr['arcount']):
        parsed_rr = _parse_rr(packet, offset)
        if parsed_rr is None:
            return None
        rr, offset = parsed_rr
        additionals.append(rr)
    return {
        'header': hdr,
        'questions': questions,
        'answers': answers,
        'authorities': authorities,
        'additionals': additionals,
        'message_size': len(packet),
    }

def decode_dns_over_tcp_stream(stream: bytes) -> list[dict[str, Any]]| None:
    '''
    Decode one or more DNS-over-TCP messages from a bytes stream.
    Each message is prefixed with a 2-byte big-endian length.
    '''
    i = 0
    messages = []
    L = len(stream)
    while i + 2 <= L:
        msg_len = int.from_bytes(stream[i:i + 2], 'big')
        i += 2
        if i + msg_len > L:
            return None
        msg = stream[i:i + msg_len]
        i += msg_len
        parsed = parse_dns_message(msg)
        if parsed is None:
            return None
        messages.append(parsed)
    return messages


def hex_to_ip(hex_str: str) -> str | None:
    try:
        if len(hex_str) != 8:
            return hex_str
        raw_bytes = bytes.fromhex(hex_str)
        return str(ipaddress.IPv4Address(raw_bytes))
    except Exception as e:
        return None
