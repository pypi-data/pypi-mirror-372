import configparser
import sys
import argparse

from .ipxact2hdlCommon import ipxactParser
from .ipxact2hdlCommon import ipxact2otherGenerator
from .ipxact2hdlCommon import cAddressBlock
from .ipxact2hdlCommon import mdAddressBlock
from .ipxact2hdlCommon import rstAddressBlock
from .ipxact2hdlCommon import systemVerilogAddressBlock
from .ipxact2hdlCommon import vhdlAddressBlock
from .ipxact2hdlCommon import DEFAULT_INI
from .validate import validate

def main_c():
    parser = argparse.ArgumentParser(description='ipxact2c')
    parser.add_argument('-s', '--srcFile', help='ipxact xml input file', required=True)
    parser.add_argument('-d', '--destDir', help="write generated file to dir", required=True)
    parser.add_argument('-c', '--config', help="configuration ini file")

    args, unknown_args = parser.parse_known_args()

    if not validate(args.srcFile):
        print(f"{args.srcFile} doesn't validate")
        sys.exit(1)

    config = configparser.ConfigParser()
    if args.config:
        config.read_dict(DEFAULT_INI)
        config.read(args.config)
    else:
        config.read_dict(DEFAULT_INI)

    e = ipxactParser(args.srcFile, config)
    document = e.returnDocument()
    generator = ipxact2otherGenerator(args.destDir, config)
    generator.generate(cAddressBlock, document)

def main_md():
    parser = argparse.ArgumentParser(description='ipxact2md')
    parser.add_argument('-s', '--srcFile', help='ipxact xml input file', required=True)
    parser.add_argument('-d', '--destDir', help="write generated file to dir", required=True)
    parser.add_argument('-c', '--config', help="configuration ini file")

    args, _ = parser.parse_known_args()

    if not validate(args.srcFile):
        print(f"{args.srcFile} doesn't validate")
        sys.exit(1)

    config = configparser.ConfigParser()
    if args.config:
        config.read_dict(DEFAULT_INI)
        config.read(args.config)
    else:
        config.read_dict(DEFAULT_INI)

    e = ipxactParser(args.srcFile, config)
    document = e.returnDocument()
    generator = ipxact2otherGenerator(args.destDir, config)
    generator.generate(mdAddressBlock, document)

def main_rst():
    parser = argparse.ArgumentParser(description='ipxact2rst')
    parser.add_argument('-s', '--srcFile', help='ipxact xml input file', required=True)
    parser.add_argument('-d', '--destDir', help="write generated file to dir", required=True)
    parser.add_argument('-c', '--config', help="configuration ini file")

    args, _ = parser.parse_known_args()

    if not validate(args.srcFile):
        print(f"{args.srcFile} doesn't validate")
        sys.exit(1)

    config = configparser.ConfigParser()
    if args.config:
        config.read_dict(DEFAULT_INI)
        config.read(args.config)
    else:
        config.read_dict(DEFAULT_INI)

    e = ipxactParser(args.srcFile, config)
    document = e.returnDocument()
    generator = ipxact2otherGenerator(args.destDir, config)
    generator.generate(rstAddressBlock, document)

def main_systemverilog():
    parser = argparse.ArgumentParser(description='ipxact2systemverilog')
    parser.add_argument('-s', '--srcFile', help='ipxact xml input file', required=True)
    parser.add_argument('-d', '--destDir', help="write generated file to dir", required=True)
    parser.add_argument('-c', '--config', help="configuration ini file")

    args, _ = parser.parse_known_args()

    if not validate(args.srcFile):
        print(f"{args.srcFile} doesn't validate")
        sys.exit(1)

    config = configparser.ConfigParser()
    if args.config:
        config.read_dict(DEFAULT_INI)
        config.read(args.config)
    else: 
        config.read_dict(DEFAULT_INI)

    e = ipxactParser(args.srcFile, config)
    document = e.returnDocument()
    generator = ipxact2otherGenerator(args.destDir, config)
    generator.generate(systemVerilogAddressBlock, document)

def main_vhdl():
    parser = argparse.ArgumentParser(description='ipxact2vhdl')
    parser.add_argument('-s', '--srcFile', help='ipxact xml input file', required=True)
    parser.add_argument('-d', '--destDir', help="write generated file to dir", required=True)
    parser.add_argument('-c', '--config', help="configuration ini file")

    args, _ = parser.parse_known_args()

    if not validate(args.srcFile):
        print(f"{args.srcFile} doesn't validate")
        sys.exit(1)

    config = configparser.ConfigParser()
    if args.config:
        config.read_dict(DEFAULT_INI)
        config.read(args.config)
    else:
        config.read_dict(DEFAULT_INI)

    e = ipxactParser(args.srcFile, config)
    document = e.returnDocument()
    generator = ipxact2otherGenerator(args.destDir, config)
    generator.generate(vhdlAddressBlock, document)

