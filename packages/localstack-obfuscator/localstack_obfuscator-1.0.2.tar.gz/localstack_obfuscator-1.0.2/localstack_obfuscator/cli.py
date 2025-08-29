_B=False
_A=True
import argparse,fnmatch,os,shutil
from pathlib import Path
import python_minifier,yaml
from localstack_obfuscator.custom_patches import patch
CONFIG_FILE_NAME='obfuscator.yml'
def root_code_dir():return Path(__file__).resolve().parent
def mkdir(path):path.mkdir(parents=_A,exist_ok=_A)
def run(cmd):os.system(cmd)
def copy_target_code(src_dir,build_dir,target_dir_name,remove=None):
	D=remove;C=build_dir;A=src_dir;print(f"Copying target code from {A} to {C} while excluding patterns: {D}");B=C/target_dir_name;mkdir(B);G=[A.replace('\\','').replace('/*','')for A in D]or[]
	def E(current_dir,names):
		E=Path(current_dir);F=E.relative_to(A);D=[]
		for B in names:
			if E==A and B==C.name:D.append(B);continue
			H=(F/B).as_posix()if F.parts else B
			if any(fnmatch.fnmatch(H,A)for A in G):D.append(B);continue
		return D
	print(f"Copying {A} to {B} with Python copy");shutil.copytree(A,B,dirs_exist_ok=_A,ignore=E);return B
def apply_python_minifier_patches():
	import ast as A;from python_minifier.ast_annotation import get_parent as C;from python_minifier.transforms.remove_annotations import RemoveAnnotations as B
	if not hasattr(B.visit_AnnAssign,'_ls_patched'):
		def F(node):
			D=node
			if not isinstance(C(D),A.ClassDef):return _B
			if len(C(D).bases)==0:return _B
			E=['NamedTuple','TypedDict','BaseModel']
			for B in C(D).bases:
				if isinstance(B,A.Name)and B.id in E:return _A
				elif isinstance(B,A.Attribute)and B.attr in E:return _A
			return _B
		@patch(B.visit_AnnAssign)
		def D(fn,self,node):
			E='annotation';B=node
			if F(B):return B
			if isinstance(B,A.AnnAssign):
				D=getattr(B,E,None);C=fn(self,B);G=getattr(C,E,None)
				if isinstance(G,A.Constant)and isinstance(D,A.Subscript|A.Name|A.BinOp):C.annotation=D
				return C
			return fn(self,B)
		B.visit_AnnAssign._ls_patched=_A
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