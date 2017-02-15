#!/usr/bin/python

# Web wrapper for Talon script
# https://github.com/mailgun/talon
#
# Start server:
#   python strip_email_web.py 8888 &> strip_email_web.log
#
# Usage:
#   curl -X POST -d text=abc1 http://0.0.0.0:8888/

import web
import talon
from talon import quotations
from talon.signature.bruteforce import extract_signature

talon.init()

urls = (
  '/', 'index'
)

class index:
  def POST(self):
    email_text = web.input()['text']
    strip_quotations  = quotations.extract_from(email_text, 'text/plain')
    strip_signature   = extract_signature(strip_quotations)[0]
    return strip_signature

if __name__ == "__main__": 
  app = web.application(urls, globals())
  app.run()
