#!/usr/bin/python

usagestring = r'''
simpmarkup filename [type] [preamblefile]

simpmarkup converts an outline file, with (sim)ple (p)resentation (markup), to a latex(beamer) file.
Inputs : filename is the input file with the simple presentation markup
         [type] is the optional argument that is used to distinguish the outline levels
         [preamblefile] is the optional preamble file

The outline file can be either from vimoutliner or emacs-org.
Supported values for [type] is either t (for tab) or *.

The simple markup rules are :

1. Headings are frames
2. Children are nested lists (itemize)
'''

defaultbeamerpreamble = r'''
\documentclass[11pt]{beamer}

% General packages
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{graphicx}
\usepackage{subfigure}

\usetheme{Boadilla}
\setbeamersize{text margin left=0.4cm}
\setbeamersize{text margin right=0.4cm}
\setbeamertemplate{headline}{}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{footline}{}
\setbeamertemplate{itemize items}[circle]

\newcommand{\ceiling}[1]{\left\lceil{#1}\right\rceil}
\newcommand{\floor}[1]{\left\lfloor{#1}\right\rfloor}
\newcommand{\nfrac}[2]{\left( \frac{#1}{#2} \right)}
\newcommand{\brac}[1]{\left\{ #1 \right\}}
\newcommand{\bras}[1]{\left[ #1 \right]}
\newcommand{\brap}[1]{\left( #1 \right)}
'''

import sys, os
import re

if len(sys.argv) > 4 or len(sys.argv) == 1:
    print usagestring
    sys.exit(-1)

inputfile = sys.argv[1]

typeoutline = "*"
beamerpreamble = defaultbeamerpreamble

if len(sys.argv) == 3:
    if sys.argv[2] == "*": 
        typeoutline = "*"
    elif sys.argv[2] == "t":
        typeoutline = "\t"
    else: # can be a preamble file then
        try:
            preamblefile = open(sys.argv[2], "r")
            beamerpreamble = "".join(preamblefile.readlines())
            preamblefile.close()
        except IOError:
            print "Using default preamble !"
            pass

if len(sys.argv) == 4:
    if sys.argv[2] == "*": 
        typeoutline = "*"
    elif sys.argv[2] == "t":
        typeoutline = "\t"
    else: 
        print "Unknown type !"
        sys.exit(-1)

    try:
        preamblefile = open(sys.argv[3], "r")
        beamerpreamble = "".join(preamblefile.readlines())
        preamblefile.close()
    except IOError:
        print "Using default preamble !"
        pass


inpFile = open(inputfile, "r")

extension = inputfile.find(".")
outputfile = inputfile[:extension] + ".tex"

outFile = open(outputfile + ".tmp", "w")

endl = "\n"

outFile.write(beamerpreamble)
outFile.write(endl)

outFile.write(r"\begin{document}" + endl)

framelevel = 1 # frames start at this outline level

special = False
environ = []
environlevel = []


for inputline in inpFile.readlines():
    inputline = inputline.replace(endl,"")

    titleextract = re.findall('^###', inputline) # titles start with ### in the first column
    if len(titleextract) > 0: # valid title
        title = inputline[3:]
        title = title.strip()
        outFile.write(r"\begin{frame}" + endl)
        outFile.write(r"\title{" + title + "}" + endl)
        outFile.write(r"\maketitle" + endl)
        outFile.write(r"\end{frame}" + endl)

    if typeoutline == "*":
        outlinelevelextract = re.findall('^\*+', inputline) # match only the outline markers at the beginning of the line
    else:
        outlinelevelextract = re.findall('^\t+', inputline)

    if len(outlinelevelextract) > 0: # this is a valid line, process further
        outlinelevelstring = outlinelevelextract[0] # this is the string of ***
        outlinelevel = len(outlinelevelstring) # this is the level 
        outlinelevelpos = inputline.find(outlinelevelstring) # this is where the string starts
        inputline = inputline[0:outlinelevelpos] + inputline[outlinelevelpos + outlinelevel:] # this is the rest of the line
        inputline = inputline.strip() # remove leading whitespace

        if special == True:
            lastlevel = environlevel[-1]
            tempoutlinelevel = outlinelevel
            while tempoutlinelevel <= lastlevel: # should try to close all environments upto last level
                special = False
                environlevel.pop()
                tenviron = environ.pop()
                if tenviron == "frame":
                    outFile.write(r"\end{itemize}" + endl) # ugly hack
                outFile.write(r"\end{" + tenviron + "}" + endl)
                tempoutlinelevel = tempoutlinelevel + 1
                
        if outlinelevel == framelevel:
            special = True
            environ.append("frame")
            environlevel.append(framelevel)

            outFile.write(r"\begin{frame}" + endl)
            outFile.write(r"\frametitle{" + inputline + "}" + endl)
            outFile.write(r"\begin{itemize}" + endl) # ugly hack

        if outlinelevel > framelevel:
            special = True
            environ.append("itemize")
            environlevel.append(outlinelevel)
            
            outFile.write(r"\item " + inputline + endl)
            outFile.write(r"\begin{itemize}" + endl)


# close all environments
while len(environlevel) > 0: # should try to close all environments upto last level
    environlevel.pop()
    tenviron = environ.pop()
    if tenviron == "frame":
        outFile.write(r"\end{itemize}" + endl) # ugly hack
    outFile.write(r"\end{" + tenviron + "}" + endl)
        
outFile.write(r"\end{document}" + endl)
outFile.close()
inpFile.close()

# Parse output file again to remove empty itemize lists

outFile1 = open(outputfile + ".tmp", "r")
outFile2 = open(outputfile, "w")

hold = False

for line in outFile1.readlines():
    line = line.replace("\n","")

    if hold == True:
        if line == r"\end{itemize}": # we have a empty list
            hold = False
            continue
        else:
            outFile2.write(r"\begin{itemize}" + endl)
            hold = False

    if line == r"\begin{itemize}": # this may be an empty list
        hold = True

    if hold == False:
        outFile2.write(line + endl)

outFile1.close()
outFile2.close()

            

    


                    

    
