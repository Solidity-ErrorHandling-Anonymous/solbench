import re

def detect_enum_type_conversion_lines(solidity_code):
    pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*=\s*([a-zA-Z_]\w*)\([^)]*\)\s*;', re.IGNORECASE)
    matches = pattern.finditer(solidity_code)

    enum_type_conversion_lines = []

    for match in matches:
        start, end = match.span()
        line_number = solidity_code.count('\n', 0, start) + 1
        enum_type_conversion_lines.append((line_number, solidity_code.splitlines()[line_number-1]))

    return enum_type_conversion_lines

def detect_variable_division_lines(solidity_code):
    pattern = re.compile(r'(\w+)\s*\/\s*(\w+)', re.IGNORECASE)
    matches = pattern.finditer(solidity_code)

    variable_division_lines = []

    for match in matches:
        if match.group(1).isalpha() and match.group(2).isalpha():
            variable_division_lines.append(match.group())

    return variable_division_lines

def detect_pop_lines(solidity_code):
    pattern = re.compile(r'\.pop\(\)', re.IGNORECASE)
    matches = pattern.finditer(solidity_code)

    return matches

def detect_array_allocations(solidity_code):
    pattern = re.compile(r'\bnew\s+(\w+)\s*\[\s*\]', re.IGNORECASE)
    matches = pattern.finditer(solidity_code)

    return matches

def detect_contract_creation(solidity_code):
    pattern = re.compile(r'\b(\w+)\s*=\s*new\s+(\w+)\s*\(([^)]*)\)\s*;', re.IGNORECASE)
    matches = pattern.finditer(solidity_code)

    contract_creation_lines = []

    for match in matches:
        start, end = match.span()
        line_number = solidity_code.count('\n', 0, start) + 1
        contract_creation_lines.append((line_number, solidity_code.splitlines()[line_number-1]))

    return contract_creation_lines
    
def detect_address_arguments(solidity_code):
    pattern = re.compile(r'\bfunction\s+\w+\s*\([^)]*\baddress\s+(\w+)\s*(?:,|\))', re.IGNORECASE)
    matches = pattern.finditer(solidity_code)

    address_arguments_lines = []

    for match in matches:
        start, end = match.span()
        line_number = solidity_code.count('\n', 0, start) + 1
        address_arguments_lines.append((line_number, solidity_code.splitlines()[line_number-1]))

    return address_arguments_lines
    
def detect_external_call_functions(solidity_code):
    external_call_patterns = [
        re.compile(r'\b\w+\.\w+\b', re.IGNORECASE),
        re.compile(r'(\b\w+\.\w+\("[^"]*"\))', re.IGNORECASE),  # This case is for the string into the parenthesis
        # re.compile(r'\b.*\s*\(.*\)\s*.*\b', re.IGNORECASE),
        # re.compile(r'\bcall\s*\(.*\)\s*external\b', re.IGNORECASE),
        # re.compile(r'\bdelegatecall\s*\(.*\)\s*external\b', re.IGNORECASE),
        # re.compile(r'\bstaticcall\s*\(.*\)\s*external\b', re.IGNORECASE),
    ]

    detected_functions = []

    for pattern in external_call_patterns:
        matches = pattern.finditer(solidity_code)
        for match in matches:
            start, end = match.span()
            line_number = solidity_code.count('\n', 0, start) + 1
            line_content = solidity_code.splitlines()[line_number-1]
            
            if ".pop" not in line_content:
                detected_functions.append((line_number, line_content))

    return detected_functions

if __name__ == "__main__":
    # Example Solidity code
    solidity_code = """
    function externalCallExample(address _target) external {
        _target.call{value: msg.value}("");
    }

    function delegateCallExample(address _target) external {
        _target.delegatecall("");
    }

    function staticCallExample(address _target) external {
        _target.staticcall("");
    }
    function createNewContract() public {
       MyNewContract newContract = new MyNewContract();
       deployedContract = address(newContract);
   }
   uint256[] public dynamicArray;
   uint256[5] public fixedArray;

   function allocateDynamicArray() public {
       uint256[] memory newArray = new uint256[](10);
   }

   function allocateFixedArray() public {
       uint256[3] memory newArray = new uint256[](3);
   }
   uint256[] public myArray;

   function popFromMyArray() public {
       myArray.pop();
   }
   enum Color { Red, Green, Blue }
   Color public selectedColor;

   function convertEnum() public {
       uint256 convertedValue = uint256(selectedColor);
       int64 convertedInt = int64(selectedColor);
       string convertedString = string(selectedColor);
   }

   function someFunction() public {
       // Some other code
       myArray.pop();
       // More code
   }
   function performDivision() public view returns (uint256) {
       return numerator / denominator;
   }
   function someFunction() public pure {
       // Some other code
       uint256 result = 10 / 5;
       uint256 anotherResult = a / b;
       // More code
  }
   """

    detected_functions = detect_external_call_functions(solidity_code)

    if detected_functions:
        print("Lines with external functions call:")
        for line_number, line_content in detected_functions:
            print(f" - Line {line_number}: {line_content}")
    else:
        print("No lines with function arguments containing 'address' keyword detected.")

    detected_arguments = detect_address_arguments(solidity_code)

    if detected_arguments:
        print("Lines with function arguments containing 'address' keyword:")
        for line_number, line_content in detected_arguments:
            print(f" - Line {line_number}: {line_content}")
    else:
        print("No lines with function arguments containing 'address' keyword detected.")
        
    detected_contract_creation = detect_contract_creation(solidity_code)

    if detected_contract_creation:
        print("Lines with new contract creations detected:")
        for line_number, line_content in detected_contract_creation:
            print(f" - Line {line_number}: {line_content}")
    else:
        print("No lines with new contract creations detected.")
        
    detected_allocations = detect_array_allocations(solidity_code)

    if detected_allocations:
        print("Detected array allocations:")
        for match in detected_allocations:
            start, end = match.span()
            allocated_line = solidity_code[:end].count('\n') + 1
            print(f" - Line {allocated_line}: {solidity_code.splitlines()[allocated_line-1]}")
    else:
        print("No array allocations detected.")

    detected_pop_lines = detect_pop_lines(solidity_code)

    if detected_pop_lines:
        print("Lines with .pop() detected:")
        for match in detected_pop_lines:
            start, end = match.span()
            line_number = solidity_code.count('\n', 0, start) + 1
            print(f" - Line {line_number}: {solidity_code.splitlines()[line_number-1]}")
    else:
        print
   
    detected_variable_division_lines = detect_variable_division_lines(solidity_code)

    if detected_variable_division_lines:
        print("Lines with division using variables detected:")
        for line in detected_variable_division_lines:
            print(f" - {line}")
    else:
        print("No lines with division using variables detected.")

    detected_enum_type_conversion_lines = detect_enum_type_conversion_lines(solidity_code)

    if detected_enum_type_conversion_lines:
        print("Lines with enum type conversions detected:")
        for line_number, line_content in detected_enum_type_conversion_lines:
            print(f" - Line {line_number}: {line_content}")
    else:
        print("No lines with enum type conversions detected.")


