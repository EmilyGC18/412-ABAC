import sys

def setupAttr(subjects, resources, rules, abac_filename):
    with open(abac_filename, 'r') as f:
    for line in f:
        if(line.startswith("#")):
            # if the line starts with a # then it is irrelevant, skip it
            continue
        elif(line.startswith("userAttrib")):
            # if line starts with userAttrb, load into subjects dict

        elif(line.startswith("resourceAttrib")):
            # if line starts with resourceAtrrib, load into resources dict
        elif(line.startswith("rule")):
            # if line starts with rule, load into rules dict
            # emily do stuff here !
    

def verifyReqs():
    # porker
    return -1

def heatmap():
    # goos
    return -1

def barGraph():
    # good pt2
    return -1

def main():
    opt = sys.argv[1]

    abac_filename = sys.argv[2]
    request_filename = sys.argv[3]

    subjects = {}
    resources = {}
    rules = {}

    if(opt == "-e"):
        setupAttr(subjects, resources, rules, abac_filename)
        verifyReqs()
    elif(opt == "-a"):
        setupAttr(subjects, resources, rules, abac_filename)
        heatmap()
    elif(opt == "-b"):
        setupAttr(subjects, resources, rules, abac_filename)
        barGraph()
    
if __name__ == "__main__":
    main()
