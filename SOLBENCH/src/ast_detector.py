import subprocess
import json

def compile_contract(sol_file_path, output_file_path):
    """ Compile contract and return AST, store stdout to a file """
    try:
        # Run solc to compile the contract and retrieve the AST
        result = subprocess.run(
            ['solc', '--ast-compact-json', sol_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if there are compilation errors and handle them
        if result.stderr:
            print("Compilation Warnings/Errors:", result.stderr)

        # Write stdout to a file if it is not empty
        if result.stdout:
            with open(output_file_path, 'w') as file:
                file.write(result.stdout)
            print(f"Output written to {output_file_path}")
        
        # Return the stdout to further parse it in another function
        return result.stdout
    except Exception as e:
        print("Error compiling the contract:", e)
        return None

def analyze_ast_from_file(file_path):
    """ Open the AST JSON file, skip non-JSON content, and analyze for specific keywords """
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()

            json_start_index = file_content.find('{')
            if json_start_index == -1:
                print("No JSON data found in file.")
                return

            json_content = file_content[json_start_index:]
            ast = json.loads(json_content)

        keywords = ['require', 'assert', 'revert', 'try', 'catch']
        findings, keyword_counts = find_keywords(ast, keywords)  # Correctly unpack both values

        if findings:
            print("Occurrences of keywords:")
            for keyword, location in findings:
                print(f"{keyword} found at location: {location}")
        else:
            print("No occurrences of specified keywords found.")

        # Print total counts for each keyword
        print("\nKeyword Summary:")
        for keyword in keyword_counts:
            print(f"Total {keyword}: {keyword_counts[keyword]}")

    except json.JSONDecodeError as json_err:
        print("JSON parsing error:", json_err)
    except FileNotFoundError:
        print("File not found error:", file_path)
    except Exception as e:
        print("Error reading or analyzing the AST file:", e)



def find_keywords(node, keywords):
    """ Recursively search the AST for specified keywords and count their occurrences """
    matches = []
    keyword_counts = {keyword: 0 for keyword in keywords}  # Initialize count for each keyword

    if isinstance(node, dict):
        # Check if this node contains a keyword in its 'name' attribute
        if 'name' in node and node['name'] in keywords:
            matches.append((node['name'], node.get('src', 'No src provided')))
            keyword_counts[node['name']] += 1  # Increment count for this keyword

        # Recursively search in each value of the dictionary
        for value in node.values():
            child_matches, child_counts = find_keywords(value, keywords)
            matches.extend(child_matches)
            for key in keyword_counts:
                keyword_counts[key] += child_counts[key]  # Aggregate counts from child nodes

    elif isinstance(node, list):
        # Recursively search each item in the list
        for item in node:
            child_matches, child_counts = find_keywords(item, keywords)
            matches.extend(child_matches)
            for key in keyword_counts:
                keyword_counts[key] += child_counts[key]  # Aggregate counts from child nodes

    return matches, keyword_counts




def main():
    contract_path = '../dataset/sample/0xfd1d97f0d8b100a9df095b40a13520af13df7ec1.sol'
    output_path = './out.json'

    # Compile the contract and get the AST
    stdout_data = compile_contract(contract_path, output_path)
    if stdout_data is None:
        print("Failed to get AST.")
    else:
        print("AST successfully retrieved and saved.")
        analyze_ast_from_file(output_path)

if __name__ == "__main__":
    main()
