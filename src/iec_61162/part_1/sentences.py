# -*- coding: utf-8 -*-
"""
IEC 61162-1 Sentence Module.

This module contains classes and function for representing, generating [and
parsing] presenation interface sentences compliant with the IEC 61162-1:2016
standard.

Created on Thu Jan 11 16:17:08 2018

@author: Jan Safar
"""

# =============================================================================
# %% Import Statements
# =============================================================================
# Built-in Modules ------------------------------------------------------------
from math import ceil

# Third-party Modules ---------------------------------------------------------
from bitstring import BitStream

# Local Modules ---------------------------------------------------------------

# =============================================================================
# %% Helper Functions
# =============================================================================
def iec_checksum(data):
    """
    Calculate the NMEA/IEC 61162-1 style checksum.

    A leading '$' or '!' character is ignored.

    Parameters
    ----------
    data : str
        The data over which the checksum is calculated. Must not include the
        '*' delimiter.

    Returns
    -------
    checksum : int
        Checksum.

    """
    if data[0] in ["$", "!"]:
        d = data[1:]
    else:
        d = data

    checksum = 0x00
    for c in d:
        checksum ^= ord(c)

    return checksum

def iec_ascii_6b_to_8b(bs):
    """
    Converts a 6-bit ASCII-encoded bitstream to an 8-bit ASCII-encoded string.

    Intended for use in IEC 61162-1 sentence encoding.

    TODO: Add some input testing to see if the bitstring len is divisible
    by 6

    Parameters
    ----------
    bs : bitstring.BitStream
        Bitstream to convert.

    Returns
    -------
    str
        8-bit ASCII encoded string.

    """
    n_char = len(bs) // 6

    bs.pos = 0
    char_lst = bs.readlist(n_char*'uint:6, ')

    char_lst[:] = [char + 48 if char < 40 else char + 56 for char in char_lst]

    return "".join(map(chr, char_lst))

# =============================================================================
# %% Sentence Definitions
# =============================================================================
class BBMSentence:
    """
    BBM Sentence: AIS binary broadcast message.

    Parameters
    ----------
    n_sentences : int
        Total number of sentences needed to transfer the message (1-9).
    i_sentence : int
        Sentence number (1-9).
    sequential_id : int
        Sequential message identifier (0-9).
    channel : int
        AIS channel for broadcast of the message (0-3).

        - 0: No preference
        - 1: Channel A / AIS 1
        - 2: Channel B / AIS 2
        - 3: Both channels.
    msg_id : int
        Message ID as per Rec. ITU-R M.1371.
    payload : str
        Encapsulated data (the Binary Data portion of the message).
    n_fill_bits : int
        Number of fill bits (0-5).
    talker_id : str, optional
        Talker ID. The default is "AI".

    """
    formatter_code = "BBM"

    def __init__(
            self,
            n_sentences,
            i_sentence,
            sequential_id,
            channel,
            msg_id,
            payload,
            n_fill_bits,
            talker_id="AI"):

        self.n_sentences = n_sentences
        self.i_sentence = i_sentence
        self.sequential_id = sequential_id
        self.channel = channel
        self.msg_id = msg_id
        self.payload = payload
        self.n_fill_bits = n_fill_bits
        self.talker_id = talker_id

    @property
    def string(self):
        """
        Returns
        -------
        s : str
            Sentence string, formatted as per IEC 61162-1.

        """
        s = "!{:s}{:s},{:d},{:d},{:d},{:d},{:d},{:s},{:d}".format(
            self.talker_id,
            self.formatter_code,
            self.n_sentences,
            self.i_sentence,
            self.sequential_id,
            self.channel,
            self.msg_id,
            self.payload,
            self.n_fill_bits)

        checksum = iec_checksum(s)
        s += "*" + "{:>02X}".format(checksum) + "\r\n"

        return s


class VDMSentence:
    """
    VDM Sentence: AIS VHF data-link message.

    Parameters
    ----------
    n_sentences : int
        Total number of sentences needed to transfer the message (1-9).
    i_sentence : int
        Sentence number (1-9).
    sequential_id : int
        Sequential message identifier (0-9).
    channel : str
        AIS channel ('A' or 'B').
    payload : str
        Encapsulated AIS message, formatted as per Rec. ITU-R M.1371 and
        encoded as per IEC 61162-1 (up to 60 characters; under certain
        circumstances can support up to 62 characters).
    n_fill_bits : int
        Number of fill bits (0-5).
    talker_id : str, optional
        Talker ID. The default is "AI".

    """
    formatter_code = "VDM"

    def __init__(
            self,
            n_sentences,
            i_sentence,
            sequential_id,
            channel,
            payload,
            n_fill_bits,
            talker_id="AI"):

        self.n_sentences = n_sentences
        self.i_sentence = i_sentence
        self.sequential_id = sequential_id
        self.channel = channel
        self.payload = payload
        self.n_fill_bits = n_fill_bits
        self.talker_id = talker_id

    @property
    def string(self):
        """
        Returns
        -------
        s : str
            Sentence string, formatted as per IEC 61162-1.

        """
        s = "!{:s}{:s},{:d},{:d},{:d},{:s},{:s},{:d}".format(
            self.talker_id,
            self.formatter_code,
            self.n_sentences,
            self.i_sentence,
            self.sequential_id,
            self.channel,
            self.payload,
            self.n_fill_bits)

        checksum = iec_checksum(s)
        s += "*" + "{:>02X}".format(checksum) + "\r\n"

        return s


# =============================================================================
# %% Sentence Generation
# =============================================================================
def ais_msg_bs_to_vdm_sentences(
        msg_bs,
        sequential_id,
        channel,
        talker_id="AI"):
    """
    Encapsulate an AIS message bitstream in a VDM sentence.

    Parameters
    ----------
    msg_bs : bitstring.BitStream
        AIS message bitstream, formatted as per Rec. ITU-R M.1371.
    sequential_id : int
        Sequential message identifier (0-9).
    channel : str
        AIS channel ('A' or 'B').
    talker_id : str, optional
        Talker ID. The default is "AI".

    Returns
    -------
    sentences : list of VDMSentence
        List of VDM sentences encapsulating the AIS message bitsream.

    """
    n_bits = len(msg_bs)
    n_fill_bits = int((6 - (n_bits % 6)) % 6)

    msg_bs += BitStream(n_fill_bits)

    payload = iec_ascii_6b_to_8b(msg_bs)

    # Split into multiple sentences if necessary and add NMEA/IEC armouring
    i_sentence = 1
    payload_offset = 0

    # Maximum number of characters in a payload for the VDM sentence;
    # Assuming the max number of characters per sentence is 82 (as per
    # IEC 61162-1) and that all sentence fields are populated (no null
    # fields).
    # Can be up to 62 under certain circumstances.
    max_payload_char =  60

    n_sentences = ceil(len(payload) / max_payload_char)

    sentences = []
    while i_sentence <= n_sentences:

        # FIXME: n_fill_bits should probably be 0 for all sentences but the
        # last one.
        vdm_sentence = VDMSentence(
            n_sentences=n_sentences,
            i_sentence=i_sentence,
            sequential_id=sequential_id,
            channel=channel,
            payload=payload[payload_offset:(payload_offset + max_payload_char)],
            n_fill_bits=n_fill_bits,
            talker_id=talker_id)

        i_sentence += 1

        payload_offset += max_payload_char

        sentences += [vdm_sentence]

    return sentences

def asm_payload_bs_to_bbm_sentences(
        bs,
        sequential_id,
        channel,
        msg_id,
        talker_id="AI"):
    """
    Encapsulate an ASM payload bitstream in a BBM sentence(s).

    Parameters
    ----------
    bs : bitstring.BitStream
        ASM payload bitstream (the Binary Data portion of the message).
    sequential_id : int
        Sequential message identifier (0-9).
    channel : int
        AIS channel for broadcast of the message (0-3).

        - 0: No preference
        - 1: Channel A / AIS 1
        - 2: Channel B / AIS 2
        - 3: Both channels.
    msg_id : int
        Message ID as per Rec. ITU-R M.1371.
    talker_id : str, optional
        Talker ID. The default is "AI".

    Returns
    -------
    sentences : list of vdes.ais.presentation_layer.sentences.BBMSentence
        List of BBM sentences encapsulating the ASM payload bitstream.

    """
    n_bits = len(bs)
    n_fill_bits = int((6 - (n_bits % 6)) % 6)

    bs += BitStream(n_fill_bits)

    # Convert the payload bitstream to a string of 8-bit ASCII characters
    payload = iec_ascii_6b_to_8b(bs)

    # Split into multiple sentences if necessary and add NMEA/IEC armouring
    i_sentence = 1
    payload_offset = 0
    # Maximum number of characters per payload for the BBM sentence;
    # Assuming the max number of characters per sentence is 82 (as per
    # IEC 61162-1) and that all sentence fields are populated (no null
    # fields).
    # Can be up to 60 if the follow-on sentences if fields 4 and 5 are
    # set to null.
    # Note: IEC 61162-1 states (apparently mistakenly) that this should be
    # 58, not 57.
    max_payload_char =  57
    n_sentences = ceil(len(payload) / max_payload_char)

    sentences = []
    while i_sentence <= n_sentences:

        bbm_sentence = BBMSentence(
            n_sentences=n_sentences,
            i_sentence=i_sentence,
            sequential_id=sequential_id,
            channel=channel,
            msg_id=msg_id,
            payload=payload[payload_offset:(payload_offset + max_payload_char)],
            n_fill_bits=n_fill_bits,
            talker_id=talker_id)

        i_sentence += 1

        payload_offset += max_payload_char

        sentences += [bbm_sentence]

    return sentences


class SentenceGenerator:
    """
    IEC 61162-1 Sentence Generator.

    For multi-sentence messages, the generator automatically assigns
    an appropriate Sequential ID.

    Parameters
    ----------
    talker_id : str, optional
        Talker ID. The default is "AI".

    """
    def __init__(self, talker_id="AI"):
        self.talker_id = talker_id

        self.vdm_sequential_id = self.bbm_sequential_id = 0

    def generate_bbm(
            self,
            asm_payload_bs,
            channel,
            msg_id):
        """
        Generate BBM sentence(s) encapsulating an ASM payload.

        Parameters
        ----------
        asm_payload_bs : bitstring.BitStream
            ASM payload (the Binary Data portion of an ASM), formatted as per
            the IALA Catalogue of ASM or similar.
        channel : int
            AIS channel for broadcast of the message (0-3).

            - 0: No preference
            - 1: Channel A / AIS 1
            - 2: Channel B / AIS 2
            - 3: Both channels.
        msg_id : int
            Message ID as per Rec. ITU-R M.1371.

        Returns
        -------
        list of lists of vdes.ais.presentation_layer.sentences.BBMSentence
            List of lists of BBM sentences encapsulating the ASM payload.

        """
        # Generate the BBM Sentence(s)
        bbm_sentences = asm_payload_bs_to_bbm_sentences(
            bs=asm_payload_bs,
            sequential_id=self.bbm_sequential_id,
            channel=channel,
            msg_id=msg_id,
            talker_id=self.talker_id)

        # If this is a multi-sentence message, increase the sequential ID
        if len(bbm_sentences) > 1:
            self.bbm_sequential_id = (self.bbm_sequential_id + 1) % 10

        return [bbm_sentences]


# =============================================================================
# %% Sentence Parsing
# =============================================================================


# =============================================================================
# %% Quick & Dirty Testing
# =============================================================================
if __name__=='__main__':
    vdm_sentence = VDMSentence(
        n_sentences=1,
        i_sentence=1,
        sequential_id=0,
        channel="A",
        payload="Beam me up - Scotty",
        n_fill_bits=5)

    print(vdm_sentence.string)

    bbm_sentence = BBMSentence(
        n_sentences=1,
        i_sentence=1,
        sequential_id=0,
        channel=1,
        msg_id=8,
        payload="Beam me up - Scotty",
        n_fill_bits=5)

    print(bbm_sentence.string)

    # Sample data
    asm_payload_bs = BitStream("0x123456789ABCDEF"*15)

    # Initialise the Sentence Generator
    sg = SentenceGenerator()

    # Generate some sentences
    sentence_groups = sg.generate_bbm(asm_payload_bs, channel=1, msg_id=8)

    for group in sentence_groups:
        for sentence in group:
            print(sentence.string)
