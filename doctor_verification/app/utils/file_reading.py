def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return str(e)
    
def format_data(input_data):
    print(input_data)
    transformed_data = {
        "customerId": str(input_data["customerId"]),
        "fatherOrHusbandName": "",
        "name": "",
        "permanentAddress": "",
        "qualification": "",
        "qualificationYear": "",
        "registrationNo": "",
        "stateMedicalCouncil": "",
        "universityName": "",
        "yearOfInfo": ""
    }

    modal_data = input_data["modal_data"]["data"]

    for item in modal_data:
        if len(item) > 1:  
            if item[0] == "Father/Husband Name":
                transformed_data["fatherOrHusbandName"] = item[1]
            elif item[0] == "Name":
                transformed_data["name"] = item[1]
            elif item[0] == "Permanent Address":
                transformed_data["permanentAddress"] = item[1]
            elif item[0] == "Qualification":
                transformed_data["qualification"] = item[1]
            elif len(item) > 3 and item[2] == "Qualification Year": 
                transformed_data["qualificationYear"] = item[3]
            elif item[0] == "Registration No":
                transformed_data["registrationNo"] = item[1]
            elif len(item) > 3 and item[2] == "State Medical Council":  
                transformed_data["stateMedicalCouncil"] = item[3]
            elif item[0] == "University Name":
                transformed_data["universityName"] = item[1]
            elif len(item) > 3 and item[2] == "Year of Info":  
                transformed_data["yearOfInfo"] = item[3]

    return transformed_data
