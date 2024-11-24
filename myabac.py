import sys

def setupAttr(subjects, resources, rules, abac_filename):
    with open(abac_filename, 'r') as f:
        for line in f:
            if(line.startswith("#")):
                # if the line starts with a # then it is irrelevant, skip it
                continue
            elif(line.startswith("userAttrib")):
                # if line starts with userAttrb, load into subjects dict
                all_attributes = line[11:-2]
                attributes = all_attributes.split(", ")
                subjects[attributes[0]] = {}
                for attr in attributes[1:]:
                    key = attr.split('=')[0]
                    value = attr.split('=')[1]
                    if(value.startswith('{')):
                        attr_list = value[1:-1].split(" ")
                        subjects[attributes[0]][key] = attr_list
                    else:
                        subjects[attributes[0]][key] = value
            elif(line.startswith("resourceAttrib")):
                # if line starts with resourceAtrrib, load into resources dict
                all_attributes = line[15:-2]
                print(all_attributes)
                attributes = all_attributes.split(", ")

                resources[attributes[0]] = {}
                for attr in attributes[1:]:
                    key = attr.split('=')[0]
                    value = attr.split('=')[1]
                    if(value.startswith('{')):
                        attr_list = value[1:-1].split(" ")
                        resources[attributes[0]][key] = attr_list
                    else:
                        resources[attributes[0]][key] = value

            elif(line.startswith("rule")):
                # if line starts with rule, load into rules dict
                # emily do stuff here !
                print(line)
    # the below lines are for printing the dictionary, helps get an idea of the structure
    for subj, info in subjects.items():
        print(f"{subj}: {info}\n")

    for res, info in resources.items():
        print(f"{res}: {info}\n")


def verifyReqs():
    # porker
    return -1

def heatmap():
    # goos
    return -1

def barGraph():
    # goos pt2
    return -1

def main():
    opt = sys.argv[1]

    abac_filename = sys.argv[2]

    subjects = {}
    resources = {}
    rules = {}

    if(opt == "-e"):
        setupAttr(subjects, resources, rules, abac_filename)
        verifyReqs()
        # request_filename = sys.argv[3]
    elif(opt == "-a"):
        setupAttr(subjects, resources, rules, abac_filename)
        heatmap()
    elif(opt == "-b"):
        setupAttr(subjects, resources, rules, abac_filename)
        barGraph()
    
if __name__ == "__main__":
    main()
