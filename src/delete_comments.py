import re

def remove_comments_from_solidity(solidity_file_path):
    # Read the Solidity file
    with open(solidity_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regular expression to match single-line and multi-line comments
    # Single-line comments: '//' to end of line
    # Multi-line comments: '/*' to '*/' across multiple lines
    pattern = r"""
        //.*?$           # Match single-line comments
        |               # OR
        /\*[\s\S]*?\*/  # Match multi-line comments
    """

    # Remove the matched patterns (comments) from the content
    updated_content = re.sub(pattern, '', content, flags=re.MULTILINE | re.VERBOSE | re.DOTALL)
    
    # Write the updated content back to the file
    with open(solidity_file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

# Example usage
solidity_file_path = 'ext_changed.sol'  # Replace with your file path
remove_comments_from_solidity(solidity_file_path)
print("Comments removed from:", solidity_file_path)

