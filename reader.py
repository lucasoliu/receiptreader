import requests
import json
import base64
import re
import sys
import config

key = config.key
input_file = sys.argv[1]
with open(input_file, 'rb') as image:
    contents = image.read()
encoded_string = base64.b64encode(contents).decode('UTF-8')
body = {
  "requests":[
    {
      "image":{
        "content": encoded_string
      },
      "features":[
        {
          "type":"TEXT_DETECTION"
        }
      ]
    }
  ]
}
json_body = json.dumps(body)
r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=" + key, json_body)

"""Store boundingPoly of each price in pricePolys"""
dict = json.loads(r.text)
description = dict['responses'][0]['textAnnotations'][0]['description']
prices = re.findall('\d+\.\d{2}', description)
pricePolys = {}
for elem in dict['responses'][0]['textAnnotations']:
    if elem['description'] in prices:
        pricePolys[elem['description']] = elem['boundingPoly']['vertices']

"""Match items to prices and store in itemPrices"""
itemPrices = {}
for elem in dict['responses'][0]['textAnnotations']:
    for vertex in elem['boundingPoly']['vertices']:
        for price in pricePolys:
            for poly in pricePolys[price]:
                if vertex['y'] in range(poly['y'] - 2, poly['y'] + 2):
                    itemPrices[elem['description'].lower()] = price

"""Return price + tax portion for user input dish"""
userInput = input("Enter your dish or Q to quit: ")
while userInput != 'Q':
    for item in userInput.split():
        if item.lower() in itemPrices:
            total = round(float(itemPrices[item.lower()]) + (float(itemPrices[item.lower()]) / float(itemPrices["total"])) * float(itemPrices["tax"]), 2)
            print("Your total plus tax is: " + str(total))
            break
    userInput = input("Enter another dish or Q to quit: ")
