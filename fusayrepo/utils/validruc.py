
def is_valid_ecuadorian(id_number):
    if len(id_number) == 10:
        return validate_ecuadorian_cedula(id_number)
    elif len(id_number) == 13:
        return validate_ecuadorian_ruc(id_number)
    else:
        return False


def validate_ecuadorian_cedula(cedula):
    # Check if the cédula has exactly 10 digits
    if len(cedula) != 10 or not cedula.isdigit():
        return False

    # Extract the province code and personal number
    province_code = int(cedula[:2])
    check_digit = int(cedula[9])

    # Provinces codes range from 1 to 24, plus 30 for foreigners
    if not (1 <= province_code <= 24 or province_code == 30):
        return False

    # Coefficients for the first 9 digits
    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]

    total = 0

    # Calculate the sum of products according to the algorithm
    for i in range(9):
        product = int(cedula[i]) * coefficients[i]
        if product >= 10:
            product -= 9
        total += product

    # Calculate the check digit
    computed_check_digit = 10 - (total % 10)
    if computed_check_digit == 10:
        computed_check_digit = 0

    # Check if the computed check digit matches the given check digit
    return computed_check_digit == check_digit


def validate_ecuadorian_ruc(ruc):
    if len(ruc) != 13 or not ruc.isdigit():
        return False

    # Extract the first 10 digits for cédula validation
    cedula = ruc[:10]

    # Extract the type of RUC
    ruc_type = int(ruc[2])

    # Validate based on the type of RUC
    if ruc_type in [0, 1, 2, 3, 4, 5]:  # Natural Person RUC
        return validate_ecuadorian_cedula(cedula) and ruc[10:] == "001"
    elif ruc_type == 6:  # Public Institution RUC
        return validate_public_institution_ruc(ruc)
    elif ruc_type == 9:  # Private Company RUC
        return validate_private_company_ruc(ruc)
    else:
        return False


def validate_public_institution_ruc(ruc):
    # Validate RUC for public institutions (first two digits are province code, next six are unique, 0001)
    if ruc[9:13] != "0001":
        return False

    # Validate the first 9 digits using specific coefficients
    coefficients = [3, 2, 7, 6, 5, 4, 3, 2, 0]

    total = 0

    # Calculate the sum of products
    for i in range(9):
        total += int(ruc[i]) * coefficients[i]

    # Calculate the check digit
    computed_check_digit = 11 - (total % 11)
    if computed_check_digit == 11:
        computed_check_digit = 0

    # Check if the computed check digit matches the given check digit
    return int(ruc[8]) == computed_check_digit


def validate_private_company_ruc(ruc):
    # Validate RUC for private companies (first two digits are province code, next six are unique, 001)
    if ruc[10:13] != "001":
        return False

    # Validate the first 9 digits using specific coefficients
    # 08/01/2025 se comenta esta validación ya que el sri ha hecho en la generacion de rucs para sociedades
    """
    coefficients = [4, 3, 2, 7, 6, 5, 4, 3, 2]

    total = 0

    # Calculate the sum of products
    for i in range(9):
        total += int(ruc[i]) * coefficients[i]

    # Calculate the check digit
    computed_check_digit = 11 - (total % 11)
    if computed_check_digit == 11:
        computed_check_digit = 0
    
    
    # Check if the computed check digit matches the given check digit
    return int(ruc[9]) == computed_check_digit
    """
    return True
