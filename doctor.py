#!/usr/bin/env python3
import argparse,pathlib,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--target',type=pathlib.Path,required=True);p.add_argument('--runtime',choices=['files','fast','motion'],default='files');a=p.parse_args();r=a.target.expanduser();bad=[]
for n in ['reels-studio','reels-editor','motion-studio']:
 if not (r/n/'SKILL.md').is_file():bad.append('Missing skill '+n)
if a.runtime!='files':
 for n in ['ffmpeg','ffprobe']+(['node'] if a.runtime=='motion' else ['whisper-cli']):
  if not shutil.which(n):bad.append('Missing executable on PATH: '+n)
if a.runtime=='fast':
 py=r/'reels-editor/.venv/bin/python'
 if not py.is_file() or subprocess.run([str(py),'-c','import stable_whisper,PIL,numpy'],capture_output=True).returncode:bad.append('Run reels-editor/scripts/setup_fast.sh')
 if not (r/'reels-editor/models/active.bin').is_file():bad.append('Missing transcription model; run setup_fast.sh')
 if shutil.which('ffmpeg') and ' ass ' not in subprocess.run(['ffmpeg','-hide_banner','-filters'],capture_output=True,text=True).stdout:bad.append('FFmpeg on PATH lacks ass; use ffmpeg-full')
if bad:print('\n'.join(bad));sys.exit(1)
print('Checks passed:',a.runtime,'(not a substitute for reviewing a final video)')
