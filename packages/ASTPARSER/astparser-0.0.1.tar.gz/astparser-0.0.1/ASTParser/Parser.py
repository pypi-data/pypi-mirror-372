import json
import traceback
from tree_sitter import Language , Parser
import tree_sitter_javascript as ts_js
import tree_sitter_typescript as ts_tys
from utils import detect_js_or_ts


class ASTParser:
    def __init__(self):
        try:
            print("[ASTParser] Initializing...")
            self.js_lang = Language(ts_js.language())
            self.ts_lang = Language(ts_tys.language_tsx())
            print("[ASTParser] Initialized")
        except Exception as e:
            print("[ASTParser Init Error]")
            traceback.print_exc()
            raise e
    
    def node_to_dict(self, node, code) -> dict:
        return {
                "type": node.type,
                "start": node.start_point,
                "end": node.end_point,
                "text": code[node.start_byte:node.end_byte].decode("utf8", errors="ignore"),
                "children": [self.node_to_dict(child, code) for child in node.children]
            }

    def parse(self, code: str, language: str) -> dict:
        try:
            if isinstance(code,str) or isinstance(language,str):
                raise ValueError("The Code and the language are not structured in the required format")
            
            print(f"[ASTParser] Parsing code in {language}")
            lang = self.js_lang if language.endswith(".js") else self.ts_lang
            parser = Parser(lang)
            tree = parser.parse(bytes(code, "utf8"))
            print("[ASTParser] Parsing complete")
            ast_dict = self.node_to_dict(tree.root_node, bytes(code, "utf8"))
            return json.dumps(ast_dict)      
        
        except Exception as e:
            print("[ASTParser Parse Error]")
            traceback.print_exc()
            raise e
        
    def ast_build_checker(self, file_path: str, code_str: str) -> str:
        try:
            lang = detect_js_or_ts(file_path)
            ast_code = self.parse(code_str, lang)
            return ast_code
        except Exception as e:
            print(f"The building of the AST failed: {e}")
            traceback.print_exc()
            raise e
     