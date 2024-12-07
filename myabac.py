import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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

def heatmap(subjects,resources,rules):
    attributesArray = []
    attributesSArray = []
    attributesRArray = []
    attributesArray1 = []
    attributesSArray1 = []
    attributesRArray1 = []
    # goes through all attributes in the subject attributes
    for currentSub in subjects:
        for value in subjects[currentSub]:
            if value not in attributesSArray:
                attributesSArray.append(value)
    # goes through all attributes in the resource attributes
    for currentRes in resources:
        for value in resources[currentRes]:
            if value not in attributesRArray:
                attributesRArray.append(value)
    #puts all the attributes together regardless if there is dupes
    attributesArray=attributesRArray+attributesSArray
    #for the names on the graph
    # goes through all attributes in the subject attributes
    for currentSub in subjects:
        for value in subjects[currentSub]:
            if "S_"+value not in attributesSArray1:
                attributesSArray1.append("S_"+value)
    # goes through all attributes in the resource attributes
    for currentRes in resources:
        for value in resources[currentRes]:
            if "R_"+value not in attributesRArray1:
                attributesRArray1.append("R_"+value)
    #puts all the attributes together regardless if there is dupes
    attributesArray1=attributesRArray1+attributesSArray1
    #sets size and names of x/y axis of heatmap
    num_rules = len(rules)  
    num_attributes = len(attributesArray)  
    rules1 = [f"Rule {i+1}" for i in range(num_rules)]  
    attributes=[f"{i}" for i in attributesArray]
    attributes1=[f"{i}" for i in attributesArray1]#sets the names on the hmap
    permissions = np.zeros((num_rules, num_attributes), dtype=int) 
    #this finds the permissions to the specific rule and attr
    for currentAtr in attributesArray:
        for currentRul in rules:
            for currentSec in currentRul:
                if currentAtr in currentRul[currentSec]:
                    if currentSec in ['constraints']:#for situation of constraints made problems before
                        permissions[list(rules).index(currentRul), list(attributesArray).index(currentAtr)] = len(currentRul['actions'])
                        
                    else:#checks everything else
                        yNum = list(currentRul).index(currentSec)-1
                        if(yNum==-1):
                            yNum=list(attributesArray).index(currentAtr)
                        permissions[list(rules).index(currentRul), yNum] = len(currentRul['actions'])
    check3 = ""
    seen = set()
    for num in attributesArray:#checks for dupes in attributes
        if num in seen:
            check3 = num
        seen.add(num)
    if bool(check3):#if there is dupes make them equal the same in the heatmap
        indices = [i for i, attr in enumerate(attributes) if attr == check3]
        values = permissions[:, list(attributesArray).index(check3)]
        for postion in indices:
            permissions[:, postion] = values
        
    create_heatmap(rules1, attributes1, permissions)
        
    return -1
def create_heatmap(rules, attributes, permissions, bins=(10, 15)):#overall heatmap making 
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        permissions,  # Permission values as the heatmap data
        cmap="viridis",  
        cbar_kws={'label': 'Permissions'}, 
        xticklabels=attributes,  # x-axis labels (attributes)
        yticklabels=rules,  # y-axis labels (rules)
        annot=True,  
        fmt="d",  
    )

    # Axis labels and title
    plt.title(f"Permissions Heatmap")
    plt.xlabel("Attributes")
    plt.ylabel("Rules")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.gca().invert_yaxis()
    plt.show()

def barGraph(subjects,resources,rules):
    attributesArray = []
    attributesSArray = []
    attributesRArray = []
    attributesArray1 = []
    attributesSArray1 = []
    attributesRArray1 = []
    values=[]
    #this is specifically for the names in the graph
    # goes through all attributes in the subject attributes
    for currentSub in subjects:
        for value in subjects[currentSub]:
            if "S_"+value not in attributesSArray:
                attributesSArray.append("S_"+value)
    # goes through all attributes in the resource attributes
    for currentRes in resources:
        for value in resources[currentRes]:
            if "R_"+value not in attributesRArray:
                attributesRArray.append("R_"+value)
    #puts all the attributes together regardless if there is dupes
    attributesArray=attributesRArray+attributesSArray
    # goes through all attributes in the subject attributes
    for currentSub in subjects:
        for value in subjects[currentSub]:
            if value not in attributesSArray1:
                attributesSArray1.append(value)
    # goes through all attributes in the resource attributes
    for currentRes in resources:
        for value in resources[currentRes]:
            if value not in attributesRArray1:
                attributesRArray1.append(value)
    #puts all the attributes together regardless if there is dupes
    attributesArray1=attributesRArray1+attributesSArray1
    num = 0
    for currentAtr in attributesArray1:
        for currentRul in rules:
            for currentSec in currentRul:
                if currentAtr in currentRul[currentSec]:
                    num = num+1
        values.append(num)
        num = 0

   # Generate random resource values for the subjects
    
    # Call the function
    create_bar(attributesArray, values)

    return -1

def create_bar(subjects, resources):
   
    # Sort data for top 10 most resources
    sorted_data_most = sorted(zip(resources, subjects), reverse=True, key=lambda x: x[0])
    top_resources, top_subjects = zip(*sorted_data_most[:10])

    # Sort data for top 10 least resources
    sorted_data_least = sorted(zip(resources, subjects), key=lambda x: x[0])
    least_resources, least_subjects = zip(*sorted_data_least[:10])

    # Create subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    # Plot Top 10 Most Resources
    axes[0].bar(top_subjects, top_resources, color='skyblue', alpha=0.8)
    axes[0].set_title("Top 10 Most Subjects", fontsize=14)
    axes[0].set_xlabel("Subjects", fontsize=12)
    axes[0].set_ylabel("Resources", fontsize=12)
    axes[0].tick_params(axis='x', rotation=45, labelsize=10)

    # Add value annotations
    for bar, resource in zip(axes[0].containers[0], top_resources):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(resource),
            ha='center', va='bottom', fontsize=9
        )

    # Plot Top 10 Least Resources
    axes[1].bar(least_subjects, least_resources, color='lightcoral', alpha=0.8)
    axes[1].set_title("Top 10 Least Subjects", fontsize=14)
    axes[1].set_xlabel("Subjects", fontsize=12)
    axes[1].tick_params(axis='x', rotation=45, labelsize=10)

    # Add value annotations
    for bar, resource in zip(axes[1].containers[0], least_resources):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(resource),
            ha='center', va='bottom', fontsize=9
        )

    # Adjust layout
    plt.tight_layout()
    plt.show()

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
        heatmap(subjects,resources,rules)
    elif(opt == "-b"):
        setupAttr(subjects, resources, rules, abac_filename)
        barGraph(subjects,resources,rules)

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
