import os
from pyvis.network import Network
import esprima

directory = "/Users/apgur/Desktop/project-tool/mern-marketplace"

def extract_dependencies(node):
    dependencies = []
    if node.type == 'VariableDeclaration':
        for declarations in node.declarations:
            if declarations.init and declarations.init.type == 'CallExpression' and declarations.init.callee.type == 'Identifier' and declarations.init.callee.name == 'require':
                dependencies.append(declarations.init.arguments[0].value)
    elif node.type == 'ImportDeclaration':
        for specifier in node.specifiers:
            if specifier.type == 'ImportDefaultSpecifier':
                dependencies.append(node.source.value)
    return dependencies

def parse_js_file(file_path):
    with open(file_path, 'r') as file:
        try:
            js_code = file.read()
            try:
                return esprima.parseModule(js_code, {"jsx": True})
            except Exception as error:
                print(f"Error parsing JavaScriptCode from {file_path}", error)
        except Exception as error:
            print("Error parsing .js files", error)

def is_js_file(filename):
    return filename.endswith(".js")


js_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if is_js_file(file)]

depend_list = []

# Extract dependencies from JavaScript files
for js_file in js_files:
    try:
        fileName_with_extension = os.path.basename(js_file)
        ast = parse_js_file(js_file)
        dependency = []
        for node in ast.body:
            dependency.extend(extract_dependencies(node))
            dependency = [i for i in dependency if i]
            dependency_set = set(dependency)
    except Exception as e:
        print(f"Error parsing {js_file}: {e}")
        continue

    depend_list.append({
        "filename": js_file,
        "scriptName": fileName_with_extension,
        "dependencies": list(dependency_set)
    })

# Creating a dependency graph
dependency_graph = Network(notebook=True, cdn_resources="remote", height="750px", width="100%", bgcolor="black",
                           directed=True,font_color="white", select_menu=True)
for item in depend_list:
    script_name = item["scriptName"]
    path = item["filename"]
    dependency_graph.add_node(script_name, title=path)
    for dependency in item["dependencies"]:
        # Extract just the filename without extension
        dependency = os.path.splitext(os.path.basename(dependency))[0]
        dependency_graph.add_node(dependency, border="highlight")  # Add dependency node
        dependency_graph.add_edge(dependency,script_name,  title="edge", weight=10, color="white",arrowsize=0.1)

# Visualize the dependency graph using Pyvis
dependency_graph.toggle_physics(True)
dependency_graph.show_buttons(filter_=['physics'])
dependency_graph.show('graph.html')