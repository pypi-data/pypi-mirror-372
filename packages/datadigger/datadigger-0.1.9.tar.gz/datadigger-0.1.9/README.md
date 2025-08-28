# datadigger

`datadigger` is a Python package designed to simplify text processing tasks, such as extracting, manipulating, and saving text data from various sources. It includes utility functions for working with text, handling files (e.g., reading/writing CSV), interacting with HTML elements via BeautifulSoup, and performing operations like string standardization, element extraction with CSS selectors, and more. 

---

## ✨ Key Features

- 📝 **String manipulation**: Clean, standardize, and sanitize text.  
- 📂 **File handling**: Read/write CSV, TXT, and other files with optional headers and delimiters.  
- 🌐 **HTML parsing**: Extract text or attributes using **CSS selectors** or **XPath**.  
- 📦 **JSON utilities**: Access deeply nested values and normalize data.  
- 🧹 **Flexible error handling**: Graceful behavior with missing/invalid inputs.  

---

## 📦 Installation

Install via **pip**:

```bash
pip install datadigger


# ================================================================
1. Create a Directory

from datadigger import create_directory
# Creates a directory if it doesn't already exist.


# Example 1: Creating a new directory
create_directory("new_folder")

# Example 2: Creating nested directories
create_directory("parent_folder/sub_folder")

# ================================================================
2. Standardize a String

from datadigger import standardized_string
# This function standardizes the input string by removing escape sequences like \n, \t, and \r, removing HTML tags, collapsing multiple spaces, and trimming leading/trailing spaces.


# Example 1: Standardize a string with newlines, tabs, and HTML tags
input_string_1 = "<html><body>  Hello \nWorld!  \tThis is a test.  </body></html>"
print("Standardized String 1:", standardized_string(input_string_1))

# Example 2: Input string with multiple spaces and line breaks
input_string_2 = "  This   is   a  \n\n   string   with  spaces and \t tabs.  "
print("Standardized String 2:", standardized_string(input_string_2))

# Example 3: Pass an empty string
input_string_3 = ""
print("Standardized String 3:", standardized_string(input_string_3))

# Example 4: Pass None (invalid input)
input_string_4 = None
print("Standardized String 4:", standardized_string(input_string_4))

================================================================
3. Remove Common Elements

from datadigger import remove_common_elements

# Example 1: Lists
print(remove_common_elements([1, 2, 3, 4, 5], [3, 4, 6]))
# Output: [1, 2, 5]

# Example 2: Set + Tuple
print(remove_common_elements({1, 2, 3, 4, 5}, (3, 4, 6)))
# Output: {1, 2, 5}

# Example 3: Missing arguments
print(remove_common_elements([1, 2], None))
# Output: "Value not passed for: remove_by"

print(remove_common_elements(None, None))
# Output: "Value not passed for: remove_in, remove_by"


================================================================
4. Save to CSV

from datadigger import save_to_csv

list_data = [[1, 'Alice', 23], [2, 'Bob', 30], [3, 'Charlie', 25]]
column_header_list = ['ID', 'Name', 'Age']
output_file_path = 'output_data.csv'

# Default separator (comma)
save_to_csv(list_data, column_header_list, output_file_path)

# Tab separator
save_to_csv(list_data, column_header_list, output_file_path, sep="\t")

# Semicolon separator
save_to_csv(list_data, column_header_list, output_file_path, sep=";")

Output (default, sep=","):
ID,Name,Age
1,Alice,23
2,Bob,30
3,Charlie,25

Output (sep="\t"):
ID  Name    Age
1   Alice   23
2   Bob 30
3   Charlie 25



================================================================
5. Read CSV

from datadigger import read_csv

csv_file_path = 'data.csv'
get_value_by_col_name = 'URL'
filter_col_name = 'Category'
include_filter_col_values = ['Tech']

result = read_csv(csv_file_path, get_value_by_col_name, filter_col_name, include_filter_col_values)
print(result)

Sample CSV

Category,URL
Tech,https://tech1.com
Tech,https://tech2.com
Science,https://science1.com

Result

['https://tech1.com', 'https://tech2.com']

================================================================
6. Extract JSON Content

from datadigger import get_json_content

json_data = {"user": {"name": "John", "age": 30}}
keys = ["user", "name"]

print(get_json_content(json_data, keys))
# Output: "John"

================================================================
7. Extract with CSS Selectors

from bs4 import BeautifulSoup
from datadigger import get_selector_content

html_content = """
<html>
  <body>
    <div class="example">Example Text</div>
    <a href="https://example.com">Link</a>
  </body>
</html>
"""
soup_obj = BeautifulSoup(html_content, "html.parser")

print(get_selector_content(soup_obj=soup_obj, css_selector_ele=".example"))
# [<div class="example">Example Text</div>]

print(get_selector_content(soup_obj=soup_obj, css_selector=".example"))
# "Example Text"

print(get_selector_content(soup_obj=soup_obj, css_selector="a", attr="href"))
# "https://example.com"

print(get_selector_content(soup_obj))
# "Example Text Link"


================================================================
8. Extract with XPath

from datadigger import get_xpath_content
from lxml import etree

html_content = """
<html>
    <body>
        <div>
            <h1>Welcome to My Website</h1>
            <p class="description">This is a paragraph.</p>
            <a href="http://example.com" id="example-link">Click here</a>
        </div>
    </body>
</html>
"""

tree = etree.HTML(html_content)

print(get_xpath_content(tree, xpath="//h1"))
# "Welcome to My Website"

print(get_xpath_content(tree, xpath="//a[@id='example-link']", attr="href"))
# "http://example.com"

print(get_xpath_content(tree, xpath="//a", attr="id"))
# "example-link"


================================================================
9. Save & Read Files

from datadigger import save_file, read_file

# Save file
save_file("output", "This is a new file.", "example.txt")  
save_file("output", "Appending content.", "example.txt", mode="a")  
save_file("output", "Special characters: äöüß", "example_latin1.txt", encoding="latin-1")  

# Read file
content = read_file("output/example.txt")
print(content)



