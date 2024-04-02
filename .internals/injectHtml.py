import argparse
import csv
from ast import literal_eval
import time
import os
import shutil

LIST_ITEM_INJECT_NAME = '$[item]$'

def process():
    # process inject data
    data = []
    headers = []
    with open(args.csvPath,newline='') as csvFile:
        reader  = csv.reader(csvFile, delimiter=",")
        for i, name in enumerate(next(reader)):
            item = {'name':name,'type':str}
            if(name.find('[]',0,2)!=-1):
                item['name'] = name[2:len(name)]
                item['type'] = list
            headers.append(item)
        print(headers)

        for i, row in enumerate(reader):
            if len(headers) != len(row):
                raise Exception(f'line {i}: argument size not align with headers')
            item = {}
            for j, header in enumerate(headers):
                item[header['name']] = row[j] if(header['type']!=list) else literal_eval(row[j])
            print(item)
            data.append(item)

    # copy template
    template = ''
    with open(args.templatePath) as templateFile:
        for line in templateFile.readlines():
            template += args.indent + line
    print(template)
    
    # inject file
    injectOpenTag = f'<!--@{args.injectName}@-->'
    injectCloseTag = f'<!--@/{args.injectName}@-->'
    print(injectOpenTag)
    tmpPath = f'injectHtml-temp-{time.time()}'
    with open(args.injectPath) as injectFile:
        with open(tmpPath,'w') as tmpFile:
            isInjecting = False
            for line in injectFile.readlines():
                if line.find(injectOpenTag)!=-1:
                    # inject line
                    tmpFile.writelines(line)
                    isInjecting = True
                    for item in data:
                        injectTxt = template
                        for header in headers:
                            if(header['type']!=list):
                                injectTxt = injectTxt.replace(f'$[{header['name']}]$', item[header['name']])
                            else:
                                # inject list item
                                listOpen = f'{args.indent}$[{header['name']}]$'
                                listClose = f'$[/{header['name']}]$'
                                listItemOpenIndex = injectTxt.find(listOpen)
                                print(listItemOpenIndex,listOpen)
                                if listItemOpenIndex==-1:
                                    continue
                                listItemOpenIndex = listItemOpenIndex + len(listOpen)

                                listItemCloseIndex = injectTxt.find(listClose)
                                print(listItemCloseIndex,listClose)
                                if listItemCloseIndex==-1:
                                    continue

                                listItemTemplate = injectTxt[listItemOpenIndex:listItemCloseIndex]
                                print(listItemTemplate)
                                listTxt = ''
                                for listItem in item[header['name']]:
                                    listTxt += args.indent + listItemTemplate.replace(LIST_ITEM_INJECT_NAME,f'{listItem}') + '\n'
                                
                                injectTxt = injectTxt.replace(injectTxt[listItemOpenIndex-len(listOpen):listItemCloseIndex+len(listClose)], listTxt)
                        tmpFile.writelines(injectTxt)
                elif isInjecting is True:
                    # remove line
                    if line.find(injectCloseTag)!=-1:
                        tmpFile.writelines(line)
                        isInjecting = False
                else:
                    # copy line
                    tmpFile.writelines(line)

    print(injectCloseTag)
    # replace
    shutil.move(os.path.join(tmpPath), os.path.join(args.outputPath))

def main():
    parser = argparse.ArgumentParser(description='inject template html with csv data to output html')
    parser.add_argument('-c','--data', action='store', dest='csvPath', default='project.csv', type=str, help='Input: csv file path')
    parser.add_argument('-t','--template', action='store', dest='templatePath', default='template.html', type=str, help='Input: template file')
    parser.add_argument('-i','--input', action='store', dest='injectPath', default='inject-example.html', type=str, help='Input: html for inject template')
    parser.add_argument('-o','--output', action='store', dest='outputPath', default='output.html', type=str, help='Output: processed input file after injection')
    parser.add_argument('-n','--inject-name', action='store', dest='injectName', default='template-inject', type=str, help='name to locate injection place')
    parser.add_argument('-s','--indent', action='store', dest='indent', default='          ', type=str, help='name to locate injection place')
    global args 
    args = parser.parse_args()
    print(args)
    process()

if __name__=="__main__": 
    main() 