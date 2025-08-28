_B=False
_A=True
import argparse,os
from pathlib import Path
from typing import Any
import python_minifier,yaml
from localstack_obfuscator.custom_patches import patch
CONFIG_FILE_NAME='obfuscator.yml'
def root_code_dir():return Path(__file__).resolve().parent
def mkdir(path):path.mkdir(parents=_A,exist_ok=_A)
def run(cmd):os.system(cmd)
def copy_target_code(src_dir,build_dir,target_dir_name,remove=None):
	F=target_dir_name;D=remove;C=build_dir;A=src_dir;print(f"Copying target code from {A} to {C} while excluding patterns: {D}");B=C/F;mkdir(B)
	if D:G=' ! -wholename '.join(f"'./{A}'"for A in D);E=f"cd {A} && find -type f ! -wholename {G} \\\n                    -exec cp --parents {{}} {B} \\;"
	else:E=f"cd {A} && find -type f -exec cp --parents {{}} {B} \\;"
	print(f"Copying {A} to {B} with command: {E}");run(E);return C/F
def apply_python_minifier_patches():
	import ast as B;from python_minifier.transforms.remove_annotations import RemoveAnnotations as A
	def C(node):
		E='dataclasses';D=node;C='dataclass'
		if not isinstance(D.parent,B.ClassDef):return _B
		if len(D.parent.decorator_list)==0:return _B
		for A in D.parent.decorator_list:
			if isinstance(A,B.Name)and A.id==C:return _A
			elif isinstance(A,B.Call)and isinstance(A.func,B.Name)and A.func.id==C:return _A
			elif isinstance(A,B.Attribute)and A.attr==C and A.value.id==E:return _A
			elif isinstance(A,B.Call)and isinstance(A.func,B.Attribute)and A.func.attr==C and A.func.value.id==E:return _A
		return _B
	if not hasattr(A.visit_AnnAssign,'_ls_patched'):
		@patch(A.visit_AnnAssign)
		def D(fn,self,node):
			E='annotation';A=node
			if isinstance(A,B.AnnAssign):
				D=getattr(A,E,None);C=fn(self,A);F=getattr(C,E,None)
				if isinstance(F,B.Constant)and isinstance(D,B.Subscript|B.Name):C.annotation=D
				return C
			return fn(self,A)
		A.visit_AnnAssign._ls_patched=_A
def load_file(path):
	with path.open('r')as A:return A.read()
def save_file(path,content):
	with path.open('w')as A:return A.write(content)
def load_config(config_path):
	try:
		with config_path.open('r')as A:return yaml.safe_load(A)
	except FileNotFoundError:print(f"No {CONFIG_FILE_NAME} file found in target directory");return{}
def obfuscate(src_dir,config_file):
	B=src_dir;B=B.resolve();A=load_config(config_file)
	if A.get('custom_patches',_B):apply_python_minifier_patches()
	F=B/A.get('build_dir','build');G=A.get('target_dir',B.name);H=A.get('minify',{});I=A.get('exclude',[]);J=A.get('remove',[]);E=copy_target_code(B,F,G,remove=J);print(f"Starting obfuscation in {E}...")
	for(K,N,L)in os.walk(E):
		for C in L:
			if C in I or not C.endswith('.py'):continue
			D=Path(K)/C;print(f"Obfuscating {D}");M=python_minifier.minify(load_file(D),**H);save_file(D,M)
	print('Done!')
def main():A=argparse.ArgumentParser(description='Obfuscate LocalStack proprietary code base');A.add_argument('src_dir',type=str,help='Source directory to obfuscate');A.add_argument('--config',type=str,default=CONFIG_FILE_NAME,help='Configuration file');B=A.parse_args();obfuscate(Path(B.src_dir),Path(B.config))
if __name__=='__main__':main()