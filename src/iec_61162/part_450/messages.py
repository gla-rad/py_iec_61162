# -*- coding: utf-8 -*-
"""
IEC 61162-450 Messages Module.

This module contains classes and functions for representing, generating [and
parsing] messages compliant with the IEC 61162-450:2018 standard.

Created on Tue Oct 26 16:40:43 2021

@author: Jan Safar
"""

# =============================================================================
# %% Import Statements
# =============================================================================
from iec_61162.part_1.sentences import iec_checksum

# =============================================================================
# %% Helper Functions
# =============================================================================


# =============================================================================
# %% Message Definitions
# =============================================================================
class IEC61162450Message:
    """
    Class to represent IEC 61162-450 encapuslated sentence messages.

    For simplicity, each Message is assumed to consist of only one
    IEC 61162-450 TAG block and one IEC 61162-1 like sentence.

    Parameters
    ----------
    i_sentence : int
        Sentence order within a group.
    n_sentences : int
        Number of sentences in a group.
    group_id : int
        Group code as per IEC 61162-450 (1-99).
    source_id : str
        Source identification as per IEC 61162-450.
    sentence : vdes.ais.presentation_layer.sentence.
        IEC 61162-1 like sentence.

    """
    def __init__(
            self,
            i_sentence,
            n_sentences,
            group_id,
            source_id,
            sentence):
        self.i_sentence = i_sentence
        self.n_sentences = n_sentences
        self.group_id = group_id
        self.source_id = source_id
        self.sentence = sentence

    @property
    def string(self):
        """
        Return the contents of the Message as a string.

        Formatting is as per IEC 61162-450.

        Returns
        -------
        s : str
            Sentence string.

        """
        tag = "g:{:d}-{:d}-{:d},s:{:s}".format(
            self.i_sentence,
            self.n_sentences,
            self.group_id,
            self.source_id)

        tag_checksum = iec_checksum(tag)

        s = "\\{:s}*{:>02X}\\{:s}".format(
            tag,
            tag_checksum,
            self.sentence.string)

        return s


class IEC61162450TestMessage:
    """
    Class to represent an IEC 61162-450 test message.

    Allows the message string to be defined directly rather than by specifying
    different parameters individually.

    Parameters
    ----------
    string : str
        Message string.

    """
    def __init__(self, string):
        self.string = string


# =============================================================================
# %% Message Generation
# =============================================================================
class MessageGenerator:
    """
    IEC 61162-450 Message generator.

    Parameters
    ----------
    source_id : str
        Source identification as per IEC 61162-450.

    """
    def __init__(self, source_id):
        self.source_id = source_id

        self.group_id = 0

    def generate_msg(self, sentences):
        """
        Generate IEC 61162-450 messages encapsulating 61162-1-like sentences.

        Parameters
        ----------
        sentences : list of lists of iec_61162.part_1.sentences.<ccc>Sentence
            IEC 61162-1 like sentences. Contiguous sentences of the same type
            should be grouped in separate lists. A list of lists must be used
            even if a single sentence is passed.

            For example:

            [[TSA Sentence], [VDM Sentence 1 of 2, VDM Sentence 2 of 2]] or

            [[Single BBM Sentence]].

            The nested list structure is used by the Processor to set the
            grouping control parameter code 'g' in the IEC messages.

        Returns
        -------
        messages : list of iec_61162.part_450.IEC61162450Message
            IEC 61162-450 embedded sentence messages.

        """
        messages = []

        for group in sentences:
            self.group_id += 1
            if self.group_id > 99:
                self.group_id = 1

            i_sentence = 1
            n_sentences = len(group)

            for sentence in group:
                iec_msg = IEC61162450Message(
                    i_sentence=i_sentence,
                    n_sentences=n_sentences,
                    group_id=self.group_id,
                    source_id=self.source_id,
                    sentence=sentence)

                i_sentence += 1

                messages += [iec_msg]

        return messages


# =============================================================================
# %% Message Parsing
# =============================================================================


# =============================================================================
# %% Quick & Dirty Testing
# =============================================================================
if __name__=='__main__':
    from iec_61162.part_1.sentences import SentenceGenerator
    from bitstring import BitStream

    # Sample data
    ais_payload_bs = BitStream("0x123456789ABCDEF"*15)

    # Initialise an IEC 61162-1 Sentence Generator
    sg = SentenceGenerator()

    # Generate some sentences
    sentences = sg.generate_bbm(
        asm_payload_bs=ais_payload_bs,
        channel=1,
        msg_id=8)

    # Initialise an IEC 61162-450 Message Generator
    mg = MessageGenerator(source_id="GR0001")

    # Generate some messages
    iec_messages = mg.generate_msg(sentences)

    for iec_msg in iec_messages:
        print(iec_msg.string)
