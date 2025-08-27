r'''
 _     _____ _   _ _____   _____ _   _  ____ ___  ____  _____ ____  ____
| |   | ____| \ | |__  /  | ____| \ | |/ ___/ _ \|  _ \| ____|  _ \/ ___|
| |   |  _| |  \| | / /   |  _| |  \| | |  | | | | | | |  _| | |_) \___ \
| |___| |___| |\  |/ /_   | |___| |\  | |__| |_| | |_| | |___|  _ < ___) |
|_____|_____|_| \_/____|  |_____|_| \_|\____\___/|____/|_____|_| \_|____/


BiSS Flash Tool - HEX/DIF Data Transmission Module

This module provides functionality to read HEX/DIF files and transmit the data to a BiSS device.
It handles parsing, organizing data into pages/banks, and communication with the BiSS interface.

Key Features:
- Parses standard Intel HEX format files with LENZ-specific extensions
- Supports Differential Index Table (DIF) CSV files
- Organizes data into banks and pages according to BiSS specifications
- Implements CRC verification and retry mechanisms
- Provides progress tracking during data transmission

Modules:
    - os: Operating system interfaces
    - sys: System-specific parameters and functions
    - logging: Event logging system
    - time: Time access and conversions
    - numpy: Array processing for DIF files
    - colorama: Cross-platform colored terminal text
    - libs.lib_progress: Progress bar utilities
    - lib_flashtool: BiSS FlashTool interface library

Classes:
    - HexRecord: Represents a single record from a HEX file

Functions:
    - read_hex_file: Reads and parses a HEX file into HexRecord objects
    - parse_hex_file: Extracts data, CRC, and page numbers from HEX records
    - organize_data_into_pages: Structures data into pages/banks for transmission
    - send_data_to_device: Transmits organized data to the BiSS device
    - send_hex: Main function for HEX file transmission
    - send_dif: Main function for DIF file transmission

Usage:
    For HEX files:
        send_hex("input_file.hex")

    For DIF files:
        send_dif("input_file.csv")

Author:
    LENZ ENCODERS, 2020-2025
'''

from os import path
import sys
import logging
from typing import List, Tuple, Generator
import struct
import binascii
from csv import reader
import colorama  # for Windows
import numpy as np
from ..biss.registers import BiSSBank
colorama.init()  # for Windows

# Constants
START_PAGE = 1
END_PAGE = 60
FILL_BYTE = 'FF'

logger = logging.getLogger(__name__)


class HexRecord:
    """Represents a single record from an Intel HEX format file with LENZ extensions.

    The LENZ extended HEX format includes additional record types for CRC and page information
    while maintaining compatibility with standard Intel HEX format.

    Attributes:
        byte_count (int): The number of data bytes in the record (0-255).
        address (int): The 16-bit starting address for the data (0x0000-0xFFFF).
        record_type (int): The type of the HEX record (0x00-0x05).
        data (bytearray): The actual data bytes contained in the record.

    LENZ Encrypted Record Types                         Common Record Types:
        0x00: Data record
        0x01: End of File record
        0x02: Unused                                    (Extended Segment Address record)
        0x03: CRC of the page data record               (Start Segment Address record)
        0x04: Page record in format (:02000004<page><64B blocks count>XX)
        0x05: Unused                                    (Start Linear Address record)
    """

    def __init__(self, byte_count: int, address: int, record_type: int, data: bytearray) -> None:
        """Initializes a new HexRecord instance.

        Args:
            byte_count: The count of data bytes in this record. Must be between 0 and 255.
            address: The starting memory address for this record's data. 16-bit value.
            record_type: The type of HEX record. Common values are 0x00-0x05.
            data: The actual data bytes contained in this record. Length must match byte_count.

        Raises:
            ValueError: If byte_count doesn't match data length or values are out of valid ranges.
        """
        if byte_count != len(data):
            raise ValueError(f"Byte count {byte_count} doesn't match data length {len(data)} {data}")
        if not 0 <= byte_count <= 255:
            raise ValueError(f"Byte count {byte_count} must be between 0 and 255")
        if not 0 <= address <= 0xFFFF:
            raise ValueError(f"Address {hex(address)} must be between 0x0000 and 0xFFFF")
        if not 0 <= record_type <= 5:
            raise ValueError(f"Record type {hex(record_type)} must be between 0x00 and 0x05")

        self.byte_count = byte_count
        self.address = address
        self.record_type = record_type
        self.data = data

    def __str__(self) -> str:
        """Returns a human-readable string representation of the HEX record.

        Returns:
            A formatted string showing all record fields in hexadecimal notation.
        """
        return (f"HexRecord(type=0x{self.record_type:02X}, "
                f"address=0x{self.address:04X}, "
                f"bytes={self.byte_count}, "
                f"data={bytes(self.data).hex().upper()})")

    def to_hex_line(self) -> str:
        """Converts the record back to Intel HEX format string.

        Calculates the checksum and formats all fields according to the HEX specification.

        Returns:
            A string in Intel HEX format (e.g., ':10010000214601360121470136007EFE09D2190140')

        Raises:
            ValueError: If the record contains invalid data that can't be properly formatted.
        """
        if not self.data and self.record_type != 0x01:  # EOF record can have 0 bytes
            raise ValueError("Data records must contain at least one byte of data")

        # Calculate checksum: sum of all bytes mod 256, then two's complement
        checksum = self.calculate_checksum()

        hex_line = (f":{self.byte_count:02X}{self.address:04X}{self.record_type:02X}"
                    f"{self.data.hex().upper()}{checksum:02X}")
        return hex_line

    def calculate_checksum(self) -> int:
        """Calculate hex record checksum"""
        checksum = self.byte_count
        checksum += (self.address >> 8) & 0xFF  # High byte of address
        checksum += self.address & 0xFF         # Low byte of address
        checksum += self.record_type
        checksum += sum(self.data)
        return (~checksum + 1) & 0xFF       # Two's complement

    @classmethod
    def create_extended_address(cls, page: int) -> 'HexRecord':
        """Factory method for extended address records."""
        upper_bits = (page >> 5) & 0xFF
        return cls(
            byte_count=2,
            address=0x0000,
            record_type=0x04,
            data=bytearray([0x08, upper_bits])  # 08 indicates address upper bits
        )

    @classmethod
    def create_crc_record(cls, crc_value: int) -> 'HexRecord':
        """Factory method for CRC32 records."""
        return cls(
            byte_count=4,
            address=0x0000,
            record_type=0x03,  # CRC record type
            data=bytearray(crc_value.to_bytes(4, 'big'))
        )

    @classmethod
    def from_line(cls, line: str) -> 'HexRecord':
        """Parse an Intel HEX line into a HexRecord object."""
        # if not line.startswith(':'):
        #     raise ValueError(f"Invalid HEX line: {line}")
        if line.startswith(':'):
            line = line[1:].strip()  # Remove ':' and trailing whitespace
        byte_count = int(line[0:2], 16)
        address = int(line[2:6], 16)
        record_type = int(line[6:8], 16)
        data_end = 8 + byte_count * 2
        data_hex = line[8:data_end]
        data = [int(data_hex[i:i+2], 16) for i in range(0, len(data_hex), 2)]
        checksum = int(line[data_end:data_end+2], 16)

        record = cls(byte_count, address, record_type, data)
        # Optional: Verify checksum
        if record.calculate_checksum() != checksum:
            raise ValueError(f"Checksum mismatch in line: {line}, calculated: {record.calculate_checksum()}")
        return record


def read_hex_file(filepath: str) -> List[HexRecord]:
    """Reads and parses an Intel HEX file into HexRecord objects.

    Args:
        filepath: Path to the HEX file to read

    Returns:
        List of HexRecord objects representing the file contents

    Raises:
        SystemExit: If file not found or parsing errors occur
    """
    if not path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    hex_records = []
    try:
        with open(filepath, mode='r',  encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    record = HexRecord.from_line(line)
                    hex_records.append(record)
    except (ValueError, IndexError) as e:
        print(f"Error parsing HEX file {filepath}: {e}")
        sys.exit(1)
    except OSError as err:
        print(f"OS error: {err}")
        sys.exit(1)

    return hex_records


def calculate_checksum(hex_data: str) -> int:
    """Calculate Intel HEX-style checksum for a hex string.

    Args:
        hex_data: Hex string without leading ':' or ending checksum

    Returns:
        Checksum byte (0-255)

    Example:
        >>> calculate_checksum("10010000214601360121470136007EFE09D21901")
        64
    """
    bytes_data = bytearray.fromhex(hex_data)
    return (- ((sum(bytes_data)) % 256)) % 256


def parse_hex_file(file_path: str) -> Tuple[List[int], List[int], List[HexRecord]]:
    """
    Parses the provided HEX file and extracts necessary data, including CRC and page number.

    Args:
        file_path (str): The path to the input HEX file.

    Returns:
        tuple: A tuple containing:
            - List[int]: CRC values extracted from the HEX file.
            - int: The page number extracted from the HEX file.
            - bytearray: The extracted data from the HEX file.

    Raises:
        ValueError: If the page number or CRC is not found in the HEX file.
    """
    try:
        records = read_hex_file(file_path)
    except Exception as e:
        raise ValueError(f"Error reading HEX file: {e}") from e

    crc_values = []    # 0x03 records
    page_numbers = []  # 0x04 records
    data_records = []  # 0x00 records

    for record in records:
        if record.record_type == 0x00:  # Data record
            # Create new record with bank information
            data_with_bank = bytearray(record.data)
            next_bank = ((record.address % 0x00A0) % 0x20) + (BiSSBank.BISS_USERBANK_START + 1)  # starting 6th bank
            data_with_bank.append(next_bank)

            modified_record = HexRecord(
                byte_count=record.byte_count + 1,
                address=record.address,
                record_type=record.record_type,
                data=data_with_bank
            )
            data_records.append(modified_record)
        elif record.record_type == 0x03:  # CRC record
            crc_values.append(int.from_bytes(record.data, 'big'))
        elif record.record_type == 0x04:  # Page record
            page_numbers.append(record.data[0])

    if not page_numbers:
        raise ValueError("Page number not found in HEX file")
    if not crc_values:
        raise ValueError("CRC not found in HEX file")

    return crc_values, page_numbers, data_records


def organize_data_into_pages(data_records: List[HexRecord]) -> List[List[bytes]]:
    """Organizes data records into pages according to bank configuration.

    Args:
        data_records: List of data records to organize

    Returns:
        Nested list structure where:
        - Outer list represents pages
        - Inner lists contain bank data (bytes) for each page
    """
    pages = []
    current_page = []
    current_bank_data = bytearray()

    for record in data_records:
        current_bank_data.extend(record.data)

        while len(current_bank_data) >= BiSSBank.REGISTER_PLUS_BSEL_SIZE:
            bank = current_bank_data[:BiSSBank.REGISTER_PLUS_BSEL_SIZE]
            current_bank_data = current_bank_data[BiSSBank.REGISTER_PLUS_BSEL_SIZE:]

            if len(current_page) >= BiSSBank.BANKS_PER_PAGE:
                pages.append(current_page)
                current_page = []
            current_page.append(bank)

    if current_page:
        pages.append(current_page)

    return pages


def reverse_endian(byte_list: list, word_size: int = 4) -> list:
    """
    Reverse the endianness of the given byte list based on the word size.

    Args:
        byte_list (List[int]): The list of bytes to reverse.
        word_size (int, optional): The word size in bytes (e.g., 1, 2, or 4). Defaults to 4.

    Returns:
        List[int]: A new list of bytes with the endianness reversed.
    """
    if word_size != 0:
        reversed_bytes = []
        for i in range(0, len(byte_list), word_size):
            reversed_bytes.extend(byte_list[i:i + word_size][::-1])
        return reversed_bytes
    return byte_list


def get_nonce(filename: str) -> list:
    """
    Retrieve the nonce values from a binary file.

    Args:
        filename (str): The base filename (without extension) of the nonce file.

    Returns:
        List[int]: A list of 32-bit unsigned integers representing the nonces.
    """
    nonce_filepath = f"{filename}_nonce.bin"
    with open(nonce_filepath, "rb") as f:
        file_content = f.read()
    # Iterate over the file content in chunks of 4 bytes
    return [struct.unpack(">I", file_content[i:i + 4])[0]
            for i in range(0, len(file_content), 4)]


def dif_to_biss_hex(dif_table: np.ndarray, filename: str, start_page: int = 22) -> None:
    """ TODO rewrite using HexRecord class
    Convert a difference table to a LENZ HEX file format and write it to a file.

    This function generates a HEX file from a numpy array (`DifTable`) containing
    difference data, formatting it according to Intel HEX standards. It pads the input
    data to a minimum length of 64 bytes, organizes it into 64-byte data records,
    calculates CRC values, and writes the result to the specified file.
    The resulting HEX file is ready to upload to LENZ BiSS devices.

    Args:
        DifTable (np.ndarray): A numpy array of integers representing difference data.
            Must be convertible to 8-bit signed integers (np.byte).
        filename (str): The path to the output HEX file where the data will be written.

    Returns:
        None: The function writes directly to the file and does not return a value.

    HEX File Structure:
        :02000004<page><64B blocks count>XX  (Page number and 64B blocks count)
        :<len><addr>00<data>XX  (Multiple data records)
        :04000003<CRC>XX  (CRC32 record)
        :00000001FF  (EOF marker)
    """
    PAGENUMBER_RECORD_TYPE = '04'
    DATA_RECORD_TYPE = '00'
    CRC_RECORD_TYPE = '03'
    EOF_RECORD = ":00000001FF"
    BLOCK_SIZE = 64

    if not isinstance(dif_table, np.ndarray):
        raise TypeError("Input must be numpy array")

    # logger.info('Encrypting calibration data with ciph')
    # Convert to numpy array and pad if needed
    dif_data = np.array(dif_table, dtype=np.byte)
    if len(dif_data) < BLOCK_SIZE:
        dif_data = np.append(dif_data, np.zeros(BLOCK_SIZE - len(dif_data), dtype=np.byte))
    l_dif = len(dif_data)
    logger.info('Converting %s dif to HEX (padded to %s bytes)', len(dif_table), l_dif)

    # Prepare header page record
    start_block = start_page << 5
    page_record = f'020000{PAGENUMBER_RECORD_TYPE}{start_page:02X}{((l_dif // BLOCK_SIZE) - 1):02X}'

    # Generate HEX data output
    hexdataout = [f':{page_record}{calculate_checksum(page_record):02X}']

    for block_num, i in enumerate(range(0, l_dif, BLOCK_SIZE)):
        block = dif_data[i:i + BLOCK_SIZE]
        address = start_block + block_num
        data_hex = block.tobytes().hex().upper()

        # Build record
        data_record = f"{BLOCK_SIZE:02X}{address >> 8:02X}{address & 0xFF:02X}{DATA_RECORD_TYPE}{data_hex}"
        hexdataout.append(f":{data_record}{calculate_checksum(data_record):02X}")

    # Add CRC32 record
    crc_record = f"040000{CRC_RECORD_TYPE}{binascii.crc32(dif_data):08X}"
    hexdataout.append(f":{crc_record}{calculate_checksum(crc_record):02X}")

    # Add EOF
    hexdataout.append(EOF_RECORD)

    try:
        with open(filename, "w") as output:
            for row in hexdataout:
                output.write(row.upper() + '\n')
    except IOError as e:
        raise IOError(f"Failed to write to {filename}: {e}")
    logger.info('Output hex: %s', filename)


def dec2hex(nr: int) -> str:
    """
    Converts an integer to a hexadecimal string of even length.

    Converts the given integer to its hexadecimal string representation,
    ensuring that the result has an even number of characters by prepending a '0' if necessary.

    Args:
        nr (int): The integer to convert to hexadecimal.

    Returns:
        str: The hexadecimal string representation of 'nr' with even length.

    Examples:
        >>> dec2hex(15)
        '0f'
        >>> dec2hex(255)
        'ff'
        >>> dec2hex(4095)
        '0fff'
    """
    h = format(int(nr), 'x')
    return '0' + h if len(h) % 2 else h


def dec2hex4(nr: int) -> str:
    """
    Converts an integer to a hexadecimal string of at least 4 characters, padding with zeros as necessary.

    The function ensures the resulting hexadecimal string has a minimum length of 4 characters by
    prepending zeros. If the hex string is longer than 4 characters, it may add additional zeros
    based on the length modulo operation.

    Args:
        nr (int): The integer to convert to hexadecimal.

    Returns:
        str: The hexadecimal string representation of 'nr', padded to at least 4 characters.

    Examples:
        >>> dec2hex4(15)
        '000f'
        >>> dec2hex4(255)
        '00ff'
        >>> dec2hex4(4095)
        '0fff'
        >>> dec2hex4(65535)
        'ffff'
    """
    h = format(int(nr), 'x')
    return '0' * (4 - len(h) % 5) + h


def dec2dec4(nr: int) -> str:
    """
    Converts an integer to a decimal string of at least 4 digits, padding with zeros as necessary.

    The function ensures the resulting decimal string has a minimum length of 4 digits by
    prepending zeros. If the number is greater than 9999, it prepends a '0'.

    Args:
        nr (int): The integer to convert to a decimal string.

    Returns:
        str: The decimal string representation of 'nr', padded to at least 4 digits.

    Examples:
        >>> dec2dec4(15)
        '0015'
        >>> dec2dec4(123)
        '0123'
        >>> dec2dec4(12345)
        '012345'
    """
    h = format(int(nr), '')
    if nr > 9999:
        return '0' + h
    return '0' * (4 - len(h) % 5) + h


def bytes_to_hex_str(byte_array: bytes) -> str:
    """
    Converts a bytes object to a hexadecimal string representation.

    Each byte in the input bytes object is converted to its two-digit uppercase hexadecimal equivalent.
    The resulting string is a concatenation of these hexadecimal values.

    Args:
        byte_array (bytes): The bytes object to convert.

    Returns:
        str: A string containing the hexadecimal representation of the input bytes.

    Example:
        >>> data = b'\\x01\\x02\\x0A\\xFF'
        >>> hex_str = bytes_to_hex_str(data)
        >>> print(hex_str)
        '01020AFF'
    """
    return ''.join(f'{byte:02X}' for byte in byte_array)


def generate_hex_line(address: int, command: int, data: list) -> str:
    """
    Generate a formatted hex line for communication with a device.

    Args:
        address (int): The 16-bit address field.
        command (int): The command byte.
        data (List[int]): A list of data bytes to include in the hex line.

    Returns:
        str: The formatted hex line string, including the starting ':' and checksum.
    """
    size = len(data)
    size_hex = f"{size:02X}"
    address_hex = f"{address:04X}"
    command_hex = f"{command:02X}"
    data_hex = bytes_to_hex_str(data)
    hex_line = f":{size_hex}{address_hex}{command_hex}{data_hex}"
    crc = calculate_checksum(hex_line[1:])  # Exclude the starting ":"
    crc_hex = f"{crc:02X}"
    hex_line_with_crc = hex_line + crc_hex
    return hex_line_with_crc


def generate_byte_line(address: int, command: int, data: list) -> bytes:
    """
    Generate a byte array for sending commands to a device.

    Args:
        address (int): The starting address for the command.
        command (int): The command code.
        data (List[int]): A list of data bytes to include in the command.

    Returns:
        bytes: A byte array representing the command, ready to be sent over a serial port.
    """
    size = len(data)
    size_hex = f"{size:02X}"
    address_hex = f"{address:04X}"
    command_hex = f"{command:02X}"
    # logger.debug(f"Using {data} to generate hex line")
    data_hex = bytes_to_hex_str(data)
    hex_line = f":{size_hex}{address_hex}{command_hex}{data_hex}"
    crc = calculate_checksum(hex_line[1:])  # Exclude the starting ":"
    crc_hex = f"{crc:02X}"
    hex_line_with_crc = hex_line + crc_hex
    # logger.debug(f"Hex line with crc - {hex_line_with_crc}")
    return bytes.fromhex(hex_line_with_crc[1:])


def _pad_and_recalculate_checksum(row_data: str) -> str:
    """
    Pads an Intel HEX data row to 16 bytes and recalculates its checksum.

    Args:
        row_data (str): An Intel HEX data row string without ':'.

    Returns:
        str: The modified data row, padded to 16 bytes with an updated checksum.

    """
    data_length = int(row_data[:2], 16)     # :10... - length
    if data_length < 16:
        padding_needed = 16 - data_length   # Calculate padding
        address = row_data[2:6]
        data_field = row_data[8:-2] + FILL_BYTE * padding_needed
        checksum = 0x10 + int(address[:2], 16) + int(address[2:], 16) + sum(bytearray.fromhex(data_field))
        checksum = (-checksum) & 0xFF
        row_data = f"10{address}00{data_field}{checksum:02X}"
    return row_data


def _create_dummy_data_row(address: str, fill: str = FILL_BYTE) -> str:
    """
    Creates a dummy Intel HEX data row filled with a specified byte.

    The address is incremented by 16 bytes to create the next sequential address.

    Args:
        address (str): The starting address for the row, as a 4-character hex string.
        fill (str, optional): The fill byte in hex format (default is 'FF').

    Returns:
        Complete Intel HEX record string (without ':') with:
        - Length: 16 bytes (0x10)
        - Type: 00 (data)
        - Data: 16 bytes of fill value
        - Valid checksum
    """
    address = int(address, 16) + 16  # Increment address
    dummy_data_row = f"10{address:04X}00{fill * 16}"
    checksum = 0x10 + (address >> 8) + (address & 0xFF)
    checksum = (-checksum) & 0xFF
    return dummy_data_row + f"{checksum:02X}"


def _prep_data_rows(df: List[str], section_id: int, base_offset: int,
                    prep_bytes: List[bytes]) -> List[str]:
    """
    Prepares data rows for HEX file processing with encryption.

    Args:
        df: List of HEX file rows
        section_id: Section identifier for the data block
        base_offset: Base address offset for the section
        prep_bytes: List of bytes for XOR processing

    Returns:
        List of processed HEX records ready for output
    """
    hexdataout = []
    temp_data = []
    flashend = False
    row = 2
    len_df = len(df)
    start_adr = int(df[row-1][2:6], 16)
    block_num = (int(df[row-1][2:6], 16) - start_adr) // 64

    # Create header record
    data = [2, 0, 0, 4, section_id, 63]
    data.append((-sum(data)) % 256)
    temp_hex = [dec2hex(x) for x in data]
    hexdataout.append(":" + "".join(temp_hex))

    # Process data blocks
    while not flashend:
        if row + 5 < len_df:
            temp_hexr = []
            if all(int(df[row+i][6:8]) == 0 for i in range(-1, 3)):
                for i in range(-1, 3):
                    temp_hexr.append(df[row+i][8:-2])
                temp_hexr = "".join(temp_hexr)
                temp_data.append(temp_hexr)
                block_num = (int(df[row-1][2:6], 16) - start_adr) // 64
                temp_hexrb = bytes.fromhex(temp_hexr)
                temp_proc = bytes(a ^ b for a, b in zip(temp_hexrb, prep_bytes[block_num]))
                temp_hexc = f"40{dec2hex4(block_num + base_offset)}00{temp_proc.hex()}"
                crc = sum(int(temp_hexc[i:i+2], 16) for i in range(0, len(temp_hexc), 2))
                temp_hexc += dec2hex((-crc) & 0xFF)
                hexdataout.append(":" + temp_hexc)
                row += 4
        else:
            flashend = True
        if block_num == 255:
            flashend = True

    # Process remaining data
    temp_hex = []
    if block_num < 255:
        for i in range(-1, 4):
            if int(df[row+i][6:8]) == 0:
                temp_hex.append(df[row+i][8:-2])
            else:
                temp_hex = "".join(temp_hex)

                temp_data.append(temp_hex)
                block_num = (int(df[row-1][2:6], 16) - start_adr) // 64
                temp_hexrb = bytes.fromhex(temp_hex)
                temp_proc = bytes(a ^ b for a, b in zip(temp_hexrb, prep_bytes[block_num]))
                temp_hexc = f"40{dec2hex4(block_num + base_offset)}00{temp_proc.hex()}"
                crc = sum(int(temp_hexc[i:i+2], 16) for i in range(0, len(temp_hexc), 2))
                temp_hexc += dec2hex((-crc) & 0xFF)
                hexdataout.append(":" + temp_hexc)
                break

    # Add CRC32 footer
    temp_data = "".join(temp_data)
    temp_hex = '04000003' + dec2hex(binascii.crc32(binascii.a2b_hex(temp_data)))
    crc = int(temp_hex[0:2], 16)
    for i in range(2, len(temp_hex), 2):
        crc = crc + int(temp_hex[i:i+2], 16)
    temp_hex = temp_hex + dec2hex((-crc) % 256)
    hexdataout.append(":" + temp_hex)

    # Update header with final block count
    data = [2, 0, 0, 4, section_id, (int(hexdataout[-2][5:7], 16) - int(hexdataout[1][5:7], 16)) % 256]
    data.append((-sum(data)) % 256)
    hexdataout[0] = ":" + "".join(dec2hex(x) for x in data)
    return hexdataout


def _readhex(filepath: str) -> list[str]:
    """TODO get rid of this function, replace with read_hex_file()
    Reads an Intel HEX file and returns a list of hex record strings.

    Opens the specified HEX file, reads its contents, and extracts the hex record strings
    (excluding the initial colon ':' in each line). Each line is expected to be an Intel HEX
    record starting with ':'.

    Args:
        filepath (str): The path to the HEX file.

    Returns:
        List[str]: A list of hex record strings from the file.

    Raises:
        SystemExit: If the file does not exist or cannot be opened.

    Example:
        >>> records = readhex('difftable.hex')
        >>> print(records[0])
        '-73'
    """
    try:
        if not path.exists(filepath):
            print("File not found!")
            sys.exit(1)
    except OSError as err:
        print(f'OS error! {err}')
        sys.exit(1)
    with open(filepath, mode='r',  encoding='utf-8') as file:
        filereader = reader(file, delimiter=':')
        dataframe = [row[1] for row in filereader if len(row) > 1]
    return dataframe


def dif2hex(DifTable: bytes, filename: str, start_page: int) -> None:
    """
    Convert a Diff table to Intel HEX format and save to a file.

    This function takes a byte array representing a Diff table, converts it to Intel HEX format
    with proper address handling and checksums, and writes the result to the specified file.
    The output includes extended address records, data records, a CRC32 record, and an end-of-file record.

    Args:
        DifTable: The input byte array containing the data to be converted.
        filename: The path of the output file where the HEX data will be written.
        start_page: The starting page number used to calculate the initial address offset.
                    Each page is 2048 bytes (0x800).

    Returns:
        None: The function writes the result to a file but doesn't return anything.

    The function handles:
    - 64KB address boundary crossing with extended address records
    - Proper checksum calculation for all record types
    - Generation of data records with 16 bytes per line (standard HEX format)
    - Addition of a CRC32 record (type 0x03) at the end of the file
    - Proper end-of-file marker

    Example:
        >>> data = bytes([0x01, 0x02, 0x03, 0x04])
        >>> dif2hex(data, "output.hex", 24)
        # Creates output.hex with the converted data
    """
    CRC_RECORD_TYPE = '03'
    lower_addr = 0x800 * start_page  # (0x800 = 2048) bytes -- page size
    upper_addr = 0x0800  # Initial upper address
    base_addr = (upper_addr << 16) | lower_addr
    data = bytearray(DifTable)
    hex_file_content = []
    current_upper_addr = upper_addr

    # Initial extended address record
    extended_addr_record = f":02000004{current_upper_addr:04X}{((~(2 + 4 + (current_upper_addr >> 8) + (current_upper_addr & 0xFF)) + 1) & 0xFF):02X}"
    hex_file_content.append(extended_addr_record)

    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        byte_count = len(chunk)
        addr = base_addr + i
        new_upper_addr = (addr >> 16) & 0xFFFF

        # Check 64 KB boundary
        if new_upper_addr != current_upper_addr:
            current_upper_addr = new_upper_addr
            extended_addr_record = f":02000004{current_upper_addr:04X}{((~(2 + 4 + (current_upper_addr >> 8) + (current_upper_addr & 0xFF)) + 1) & 0xFF):02X}"
            hex_file_content.append(extended_addr_record)

        record_type = 0
        address_field = addr & 0xFFFF  # Lower 16 bits of address
        checksum = byte_count + (address_field >> 8) + (address_field & 0xFF) + record_type + sum(chunk)
        data_record = f":{byte_count:02X}{address_field:04X}{record_type:02X}" + \
                      ''.join(f"{b:02X}" for b in chunk) + \
                      f"{(256 - checksum % 256) % 256:02X}"
        hex_file_content.append(data_record)

    crc_record = f"040000{CRC_RECORD_TYPE}{binascii.crc32(data):08X}"
    hex_file_content.append(f":{crc_record}{calculate_checksum(crc_record):02X}")
    hex_file_content.append(":00000001FF")

    with open(filename, "w") as output:
        for row in hex_file_content:
            output.write(str(row).upper() + '\n')


def prep_hex(filepath: str, section_id: int, count: int, desc: str) -> None:
    """
    Main function to prepare HEX file for firmware update.

    Args:
        filepath: Path to the input HEX file to be processed
        section_id: Memory section identifier (used to calculate base address)
        count: Number of bytes in the section that need hash protection
        desc: Description tag used to locate the hash file (format: lenz_hash_{desc}.bin)

    Returns:
        None: Writes the processed output to <input_filename>_op.hex

    Raises:
        FileNotFoundError: If either the input HEX file or hash binary file doesn't exist
        IOError: If there are file access/permission issues
    """
    try:
        inputhexfile = _readhex(filepath)
    except FileNotFoundError:
        sys.stderr.write(f"Error: File '{filepath}' not found.\n")
        sys.exit(1)
    except IOError as e:
        sys.stderr.write(f"IO error: {e}\n")
        sys.exit(1)

    print("Input hexfile:", filepath)
    filename, _ = path.splitext(filepath)
    hash_bytes = []
    base_offset = section_id << 5
    hash_filename = f'lenz_hash_{desc}.bin'
    try:
        with open(hash_filename, "rb") as f:
            for _ in range(base_offset, base_offset + ((count >> 6) or 1)):
                hash_bytes.append(f.read(64))

    except FileNotFoundError:
        sys.stderr.write(f"Error: Hash file '{hash_filename}' not found.\n")
        sys.exit(1)
    except IOError as e:
        sys.stderr.write(f"Error reading hash file: {e}\n")
        sys.exit(1)

    hexdata = []
    fullhexdataout = []
    hexdata_parts = (len(inputhexfile) - 4) // 128 + 1
    rawhexdata = []

    for i in range(hexdata_parts):
        hexdatarow = []
        hexdatarow.append(inputhexfile[0])
        for j in range(i * 128, (i + 1) * 128):
            if j + 4 > len(inputhexfile):
                break
            row_data = inputhexfile[j + 1]
            hexdatarow.append(_pad_and_recalculate_checksum(row_data))
            rawhexdata.append(row_data[8:-2])
        if i == hexdata_parts - 1:
            while len(hexdatarow) < 129:
                hexdatarow.append(_create_dummy_data_row(hexdatarow[-1][2:6]))

        hexdatarow.append(inputhexfile[len(inputhexfile)-2])
        hexdatarow.append(inputhexfile[len(inputhexfile)-1])
        hexdata.append(hexdatarow)

    for part in range(hexdata_parts):
        df = hexdata[part]
        section_id = int(df[0][10:12], 16) << 5 | int(df[1][2:6], 16) >> 11
        base_offset = section_id << 5
        hexdataout = _prep_data_rows(df, section_id, base_offset, hash_bytes[part << 5:])
        fullhexdataout.append(hexdataout)

    fullhexdataout[-1].append(":00000001FF")

    output_filepath = f"{filename}_op.hex"
    try:
        with open(output_filepath, "w") as output:
            print("Successfully generated output:", output_filepath)
            for hexdataout in fullhexdataout:
                for cell in hexdataout:
                    output.write(cell.upper() + '\n')
    except Exception as e:
        sys.stderr.write(f"Error writing output file: {e}\n")
        sys.exit(1)


class HexFileProcessor:
    """
    Processes Intel HEX format files for FlashTool programming.

    Key Features:
        Parses standard HEX files and extracts data segments
        Splits firmware into configurable page-sized chunks (default 2KB)
        Generates CRC32 checksums for each chunk
        Creates metadata structures for firmware management
        Maintains original HEX record structure in output

    Usage:
        Initialize processor
        Parse input HEX file (parse_hex_file())
        Generate processed output (split_with_crc())
        Write output to new HEX file
    """

    def __init__(self):
        """
        Initialize the HEX file processor with empty state.
        """
        self.current_extended_address = 0
        self.data_segments = []
        self.bootloader_segments = []
        self.original_records = []

    def parse_hex_file(self, filename: str, is_bootloader: bool = False) -> List[Tuple[int, bytearray]]:
        """
        Parse an Intel HEX file and extract addressable data segments.

        Args:
            filename: Path to input HEX file

        Returns:
            List of (address, data) tuples representing contiguous memory blocks

        Processes:
            Standard data records (0x00)
            Extended address records (0x04)
            End-of-file markers (0x01)
            Skips unsupported record types

        Note: Preserves original records for accurate output generation.
        """
        segments = self.bootloader_segments if is_bootloader else self.data_segments

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line.startswith(':'):
                    continue

                record = HexRecord.from_line(line)
                if not is_bootloader:
                    self.original_records.append(record)

                if record.record_type == 0x04:  # Extended linear address
                    self.current_extended_address = (record.data[0] << 24) | (record.data[1] << 16)
                elif record.record_type == 0x00:  # Data record
                    full_address = self.current_extended_address + record.address
                    segments.append((full_address, record.data))
                elif record.record_type == 0x01:  # EOF
                    break

        return segments

    def _combine_segments(self, segments: List[Tuple[int, bytearray]], chunk_size: int) -> Tuple[bytearray, int, int]:
        """
        Combine memory segments into a contiguous block, pad to chunk alignment, and calculate CRC/length.

        Args:
            segments: List of (address, data) tuples representing discontinuous memory segments
            chunk_size: The alignment size for padding (typically flash page size)

        Returns:
            Tuple containing:
            - combined_data: Contiguous bytearray with padding
            - crc: Calculated CRC32 checksum of the combined data
            - length_pages: Total length in chunks/pages (rounded up)

        Process:
            1. Handles empty input case
            2. Creates contiguous block by filling gaps with 0xFF (erased flash value)
            3. Adds padding at end to meet chunk size alignment
            4. Calculates CRC32 checksum of the entire block
            5. Computes size in chunks/pages (rounding up partial chunks)
        """
        if not segments:
            return bytearray(), 0xFFFFFFFF, 0

        combined_data = bytearray()
        current_address = segments[0][0]

        for addr, data in segments:
            expected_addr = current_address + len(combined_data)
            if addr != expected_addr:
                padding_len = addr - expected_addr
                combined_data.extend(b'\xFF' * padding_len)
            combined_data.extend(data)

        if len(combined_data) % chunk_size != 0:
            padding = chunk_size - (len(combined_data) % chunk_size)
            combined_data.extend(b'\xFF' * padding)

        crc = binascii.crc32(combined_data) & 0xFFFFFFFF
        length_pages = len(combined_data) // chunk_size
        if len(combined_data) % chunk_size != 0:
            length_pages += 1

        return combined_data, crc, length_pages

    def generate_first_page(
        self,
        program_crc: int,
        program_version: int,
        program_length: int,
        bootloader_crc: int,
        bootloader_version: int,
        bootloader_length: int,
        page_size: int = 2048,
        program_date: int = int('202507'),
        bootloader_date: int = int('202507'),
    ) -> bytearray:
        """
        Generate metadata page for firmware management.

        Args:
            program_crc: CRC32 of entire program data
            program_version: Version number (e.g., 0x00000100 for v1.0)
            program_length: Program length in pages
            bootloader_*: Corresponding bootloader metadata
            page_size: Flash page size in bytes (default 2048)

        Returns:
            bytearray containing:
            - 64-byte metadata structure
            - 1984-byte padding (0xFF)

        Metadata Structure (64 bytes):
        Offset  Field                     Type
        0x00    ProgramCRC32              uint32
        0x04    ProgramDate (timestamp)   uint32
        0x08    ProgramVersion            uint32
        0x0C    ProgramLen (pages)        uint32
        0x10    BootloaderCRC32           uint32
        0x14    BootloaderDate           uint32
        0x18    BootloaderVersion        uint32
        0x1C    BootloaderLen            uint32
        0x20    ProgramCurrentPageCRC32  uint32
        0x24    BootloaderCurrentPageCRC uint32
        """
        page = bytearray([0xFF] * page_size)

        # Pack the UartBank1_t structure into the first 64 bytes
        metadata = struct.pack(
            "<IIIIIIIIII",  # Little-endian, 10x uint32
            program_crc,                # ProgramCRC32 (0x00)
            program_date,              # ProgramDate (0x04)
            program_version,            # ProgramVersion (0x08)
            program_length,             # ProgramLen (0x0C) - теперь uint32 вместо uint16
            bootloader_crc,             # BootloaderCRC32 (0x10)
            bootloader_date,            # BootloaderDate (0x14)
            bootloader_version,         # BootloaderVersion (0x18)
            bootloader_length,          # BootloaderLen (0x1C)
            0x00000000,                # ProgramCurrentPageCRC32 (0x20) - заполнится позже
            0x00000000                 # BootloaderCurrentPageCRC32 (0x24) - заполнится позже
        )

        page[0:len(metadata)] = metadata

        page[12] = program_length & 0xFFFFFFFF        # PROGRAM_LENGTH_ADR
        page[28] = bootloader_length & 0xFFFFFFFF      # BOOTLOADER_LENGTH_ADR

        page_crc = binascii.crc32(page) & 0xFFFFFFFF
        page[32:36] = struct.pack("<I", page_crc)  # PROGRAM_CURPAGE_CRC_ADR

        return page

    def split_with_crc(
        self,
        chunk_size: int = 2048,
        metadata: bool = True,
        program_version: int = 0x00000100,
        bootloader_version: int = 0x00000100,
        program_date: int = int('202507'),
        bootloader_date: int = int('202507'),
    ) -> List[str]:
        """
        Process firmware data into page-aligned chunks with CRCs.

        Args:
            chunk_size: Flash page size (default 2048 bytes)
            metadata: Whether to prepend metadata page

        Returns:
            List of HEX format strings ready for file writing

        Processing Steps:
        1. Combine all data segments into contiguous block
        2. Handle address gaps with 0xFF padding
        3. Add page alignment padding if needed
        4. Calculate overall program CRC32
        5. Generate metadata page (optional)
        6. Split into chunks with individual CRCs
        7. Generate HEX records
        """
        program_data, program_crc, program_length = self._combine_segments(self.data_segments, chunk_size)

        if self.bootloader_segments:
            bootloader_data, bootloader_crc, bootloader_length = self._combine_segments(
                self.bootloader_segments, chunk_size)
        else:
            bootloader_data = bytearray()
            bootloader_crc = 0xFFFFFFFF
            bootloader_length = 0

        if metadata:
            metadata_page = self.generate_first_page(
                program_crc=program_crc,
                program_version=program_version,
                program_length=program_length,
                bootloader_crc=bootloader_crc,
                bootloader_version=bootloader_version,
                bootloader_length=bootloader_length,
                program_date=program_date,
                bootloader_date=bootloader_date,
            )

            combined_data = metadata_page + program_data + bootloader_data
            current_address = self.data_segments[0][0] - len(metadata_page)
        else:
            combined_data = program_data + bootloader_data
            current_address = self.data_segments[0][0]

        chunks = []
        for i in range(0, len(combined_data), chunk_size):
            chunk_data = combined_data[i:i + chunk_size]
            crc = binascii.crc32(chunk_data) & 0xFFFFFFFF
            chunks.append((current_address + i, chunk_data, crc))

        return self._generate_hex_output(chunks)

    def _generate_hex_output(self, chunks: List[Tuple[int, bytearray, int]]) -> List[str]:
        """
        Generate final HEX file output from processed chunks.

        Args:
            chunks: List of (address, data, crc) tuples

        Returns:
            List of HEX format strings

        Maintains:
        - Original extended address records
        - Data records split into 16-byte lines
        - CRC records after each chunk
        - Proper EOF termination
        """
        output = []

        for record in self.original_records:
            if record.record_type in {0x04}:
                if isinstance(record.data, list):
                    record.data = bytearray(record.data)
                output.append(record.to_hex_line())

        for address, data, crc in chunks:
            remaining_data = data
            current_offset = 0

            while remaining_data:
                chunk = remaining_data[:16]
                rec_address = (address + current_offset) & 0xFFFF
                data_rec = HexRecord(
                    byte_count=len(chunk),
                    address=rec_address,
                    record_type=0x00,
                    data=chunk
                )
                output.append(data_rec.to_hex_line())
                remaining_data = remaining_data[16:]
                current_offset += 16

            output.append(HexRecord.create_crc_record(crc).to_hex_line())

        eof_rec = HexRecord(byte_count=0, address=0, record_type=0x01, data=bytearray())
        output.append(eof_rec.to_hex_line())

        return output


class HexBlockExtractor:
    """
    Extracts and processes blocks of data from Intel HEX files for FlashTool.

    This class handles:
    - Parsing HEX file records
    - Combining discontinuous memory segments into contiguous blocks
    - Tracking CRC values associated with each block
    - Managing extended address segments
    - Yielding complete blocks with their metadata
    """
    def __init__(self):
        """Initialize the HEX block extractor with empty state."""
        self.current_extended_addr = 0x00000000
        self.current_block_data = bytearray()
        self.current_block_start = 0
        self.crc_records = []
        self.data_records = []

    def process_hex_file(self, filename: str) -> Generator[Tuple[int, bytes, int], None, None]:
        """Main processing method that reads a HEX file and yields data blocks.

        Args:
            filename: Path to the Intel HEX format file

        Yields:
            Tuples containing:
            - block_start: Starting address of the block
            - block_data: Binary data contained in the block
            - block_crc: CRC32 checksum associated with the block

        Note:
            Processes the file line by line and handles the final block if exists.
        """
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line.startswith(':'):
                    continue

                record = self._parse_hex_line(line)
                for block in self._process_record(record):
                    yield block

        # Process the last block if exists
        if self.current_block_data:
            yield self._finalize_block()

    def _parse_hex_line(self, line: str) -> dict:
        """Parse a single line of HEX file into its components.

        Args:
            line: A single line from HEX file (e.g., ':10010000214601360121470136007EFE09D2190140')

        Returns:
            Dictionary containing:
            - byte_count: Number of data bytes in record
            - address: 16-bit offset address
            - record_type: HEX record type (0x00=data, 0x04=extended address, etc.)
            - data: Raw bytes contained in record
            - checksum: Record checksum byte

        Raises:
            ValueError: If line format is invalid
        """
        byte_count = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        data = bytes.fromhex(line[9:9+byte_count*2])
        checksum = int(line[9+byte_count*2:], 16)

        return {
            'byte_count': byte_count,
            'address': address,
            'record_type': record_type,
            'data': data,
            'checksum': checksum
        }

    def _process_record(self, record: dict) -> Generator[Tuple[int, bytes, int], None, None]:
        """Process a single parsed HEX record and manage block construction.

        Args:
            record: Parsed HEX record dictionary from _parse_hex_line()

        Yields:
            Completed blocks when encountering CRC records or address changes

        Handles:
        - Extended address records (type 0x04): Updates current addressing
        - Data records (type 0x00): Accumulates data into current block
        - CRC records (type 0x03): Triggers block completion and yield
        """
        if record['record_type'] == 0x04:  # Extended Linear Address
            self.current_extended_addr = (record['data'][0] << 24 | record['data'][1] << 16)
        elif record['record_type'] == 0x00:  # Data Record
            full_addr = self.current_extended_addr + record['address']

            # Initialize new block if needed
            if not self.current_block_data:
                self.current_block_start = full_addr

            self.current_block_data.extend(record['data'])
        elif record['record_type'] == 0x03:  # CRC Record
            crc_value = int.from_bytes(record['data'], 'big')
            self.crc_records.append((self.current_block_start, crc_value))

            # Yield the completed block
            if self.current_block_data:
                yield self._finalize_block()

    def _finalize_block(self) -> Tuple[int, bytes, int]:
        """Package the current block of data and prepare for new block.

        Returns:
            Tuple containing:
            - Starting address of the completed block
            - Binary data of the block
            - Associated CRC32 checksum (0 if none available)

        Note:
            Clears current block buffers after packaging the data.
        """
        block_data = bytes(self.current_block_data)
        block_crc = self.crc_records.pop(0)[1] if self.crc_records else 0

        # Reset for next block
        self.current_block_data = bytearray()

        return (self.current_block_start, block_data, block_crc)
