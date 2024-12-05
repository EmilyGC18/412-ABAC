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
                subjects[attributes[0]]['uid'] = attributes[0] 
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
                # print(all_attributes)
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
                cons = cons.replace(")","").replace(";","")

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
    # for subj, info in subjects.items():
    #     print(f"{subj}: {info}\n")

    # for res, info in resources.items():
    #     print(f"{res}: {info}\n")
    
    # for rule in rules:
    #     print(f"{rule}\n")


def checkConstraint(user, res, constraint):
    if(bool(constraint)): ## if content in 'constraints'...
        split = constraint.split(",") ## multiple conditions
        for el in split:
            if("=" in el): ##if there are spaces in the string I can split by the '=' symbol
                holder = el.split("=")
                if(holder[0] not in user or holder[1] not in res):
                    return False
                elif(user[holder[0]] not in res[holder[1]]):
                    return False
            else:
                el = el.lstrip()
                holder = el.split(" ")
                if(holder[0] not in user):
                    return False
                if(holder[2] not in res):
                    return False
                if(holder[1] == "["): ## in 
                    if(not set(user[holder[0]]).intersection(set(res[holder[2]]))): ## sub is single value, res is mulitple values
                        return False
                elif(holder[1] == "]"): ## contains
                    if(res[holder[2]] not in user[holder[0]]): ## sub is multiple values, res is single value
                        return False
                elif(holder[1] == ">"): ## super set
                    if(not set(user[holder[0]]).issuperset(set(res[holder[2]]))): ## both sub and res are multi-valued
                        return False
    return True

def checkTargetCon(condition, target):
    # condition == r['subCond'] or r['resCond'] ... same logic for both
    if(bool(condition)): ## if content in 'condition'...
        param = ""
        for p in set(condition).intersection(set(target)): ## finds what attribute the rule is looking for in the subject
            param = p
            print(target[param])    
            if(param == ""): ## if not intersection, no matching attribute
                return False ## exit loop
            if(target[param] not in condition[param]): ## if target does not possess the rule's desired attribute
                return False ## next rule
    return True

def verifyReqs(subjects, resources, rules, requests):
    with open(requests, 'r') as f:
        for line in f:
            parts = line.split(",")
            req_user = parts[0]
            req_res = parts[1]
            req_action = parts[2].replace("\n","")
            permission = "DENY" ##default to DENY, only PERMIT when all contraints met
            for r in rules:
                ## Subjects
                if(req_user not in subjects): ## check if subject exists
                    break ## if not found, DENY
                if(not checkTargetCon(r['subCond'], subjects[req_user])): ## if 'subCond' unsatisfied...
                    continue ## next rule
                
                ## Resources
                if(req_res not in resources): ## check if resource exists
                    break ## if not found, DENY
                if(not checkTargetCon(r['resCond'], resources[req_res])): ## if 'resCond' unsatisfied...
                    continue ## next rule
                
                ## Constraint
                if(not checkConstraint(subjects[req_user], resources[req_res], r['constraints'])): ## if constraints unsatisfied...
                    continue ## next rule
                
                ##Action
                if(req_action in r['actions']): ## 'perm' only changes if all other constraints met
                    permission = "PERMIT"
                    break ## exit rule search once satisfactory rule found
            print(f"{line.replace("\n","")} - {permission}\n") ## print request result once rule found OR out of rules to check
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
    rules = []
    
    if(opt == "-e"):
        setupAttr(subjects, resources, rules, abac_filename)
        verifyReqs(subjects, resources, rules, sys.argv[3])
        # request_filename = sys.argv[3]
    elif(opt == "-a"):
        setupAttr(subjects, resources, rules, abac_filename)
        heatmap()
    elif(opt == "-b"):
        setupAttr(subjects, resources, rules, abac_filename)
        barGraph()

main()

# if __name__ == "__main__":
#     subjects = {}  # dictionary to store parsed user attributes
#     resources = {}  # dictionary to store parsed resource attributes
#     rules = []  # list to store parsed rules

#     abac_file = "university.abac" 

#     setupAttr(subjects, resources, rules, abac_file)

#     print("\nFinal Subjects Dictionary:")
#     for subj, attributes in subjects.items():
#         print(f"{subj}: {attributes}")

#     print("\nFinal Resources Dictionary:")
#     for res, attributes in resources.items():
#         print(f"{res}: {attributes}")

#     print("\nFinal Rules List:")
#     for rule in rules:
#     print(rule)
