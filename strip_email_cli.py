#!/usr/bin/python

# CLI for Talon script
# https://github.com/mailgun/talon
#
# Usage:
#   python strip_email_cli.py 'abc1'

import sys
import talon
from talon import quotations
from talon.signature.bruteforce import extract_signature

def main(argv):

  if len(sys.argv) != 2:
    print 'Wrong number of arguments provided!'
    print 'Usage: '
    print '    python strip_email_cli.py \'<email_text>\''
    sys.exit(2)

  talon.init()
  email_text = sys.argv[1]

  strip_quotations = quotations.extract_from(email_text, 'text/plain')
  strip_signature  = extract_signature(strip_quotations)[0]
  
  print strip_signature
  sys.exit()

if __name__ == "__main__":
  main(sys.argv[1:])