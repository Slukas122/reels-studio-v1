#!/usr/bin/env python3
"""Install the V1 bundle without overwriting existing skills."""
import argparse, pathlib, shutil, sys
ROOT=pathlib.Path(__file__).resolve().parent
NAMES=('reels-studio','reels-editor','motion-studio')
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',type=pathlib.Path,help='Skills directory; default ~/.codex/skills');p.add_argument('--claude',action='store_true',help='Use ~/.claude/skills');a=p.parse_args()
 dest=(a.target or pathlib.Path.home()/('.claude' if a.claude else '.codex')/'skills').expanduser().resolve()
 conflicts=[str(dest/n) for n in NAMES if (dest/n).exists()]
 if conflicts:sys.exit('Nothing changed. Existing skills: '+', '.join(conflicts)+'\nBack them up/move them first, or choose --target DIRECTORY.')
 dest.mkdir(parents=True,exist_ok=True)
 sources={'reels-studio':ROOT,'reels-editor':ROOT/'dependencies/reels-editor','motion-studio':ROOT/'dependencies/motion-studio'}
 for n,src in sources.items():
  if not (src/'SKILL.md').is_file():sys.exit('Incomplete bundle: '+str(src))
 created=[]
 try:
  for n,src in sources.items():
   created.append(dest/n)
   if n=='reels-studio':
    (dest/n).mkdir()
    for f in ['SKILL.md','agents','references','scripts']:
     s=src/f;d=dest/n/f
     shutil.copytree(s,d) if s.is_dir() else shutil.copy2(s,d)
   else:shutil.copytree(src,dest/n,ignore=shutil.ignore_patterns('.venv','node_modules','models','__pycache__','.DS_Store'))
 except Exception:
  for d in created:
   if d.exists():shutil.rmtree(d)
  raise
 print('Installed V1 and both companion skills in',dest)
 print('Runtime setup: see README.md. Restart/reload your agent to discover the skills.')
if __name__=='__main__':main()
