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
                 # parse rules (rule(subCond; resCond; acts; cons))
                 
                rule_body = line[5:-1]  # removing 'rule(' and ')'

                # spliting the rule into its components (subCond, resCond, acts, cons)
                subCond, resCond, acts, cons = rule_body.split("; ")

                # parse actions into a set
                actions = set(acts[1:-1].split(" "))  # removing the curly braces and split values

                # parse subject and resource conditions directly here.
                sub_conditions = {}
                if subCond.strip():
                    for cond in subCond.split(", "):
                        if "[" in cond:  
                            attr, values = cond.split(" [ ")
                            sub_conditions[attr] = set(values[1:-1].split(" "))  # set
                        elif "]" in cond:  
                            attr, value = cond.split(" ] ")
                            sub_conditions[attr] = value  # storing the single value

                res_conditions = {}
                if resCond.strip():
                    for cond in resCond.split(", "):
                        if "[" in cond:  
                            attr, values = cond.split(" [ ")
                            res_conditions[attr] = set(values[1:-1].split(" "))  
                        elif "]" in cond:  
                            attr, value = cond.split(" ] ")
                            res_conditions[attr] = value 

                # storing the parsed rule as a dictionary and add it to the rules list.
                rule = {
                    "subCond": sub_conditions,  # subjects
                    "resCond": res_conditions,  # resources
                    "actions": actions,         # allowed actions
                    "constraints": cons         # rule
                }
                rules.append(rule)  # adding the rule to the list of rules
                
    # the below lines are for printing the dictionary, helps get an idea of the structure
    for subj, info in subjects.items():
        print(f"{subj}: {info}\n")

    for res, info in resources.items():
        print(f"{res}: {info}\n")
    
    for rule in rules:
        print(f"{rule}\n")


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
