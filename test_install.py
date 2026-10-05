import pathlib,subprocess,sys,tempfile,unittest
R=pathlib.Path(__file__).resolve().parent
class InstallTest(unittest.TestCase):
 def test_clean_install_and_conflict(self):
  with tempfile.TemporaryDirectory() as t:
   target=pathlib.Path(t)/'skills'
   cmd=[sys.executable,str(R/'install.py'),'--target',str(target)]
   subprocess.run(cmd,check=True,capture_output=True)
   subprocess.run([sys.executable,str(R/'doctor.py'),'--target',str(target)],check=True,capture_output=True)
   source=(R/'SKILL.md').read_bytes();self.assertEqual(source,(target/'reels-studio/SKILL.md').read_bytes())
   marker=target/'reels-editor/keep.txt';marker.write_text('keep')
   self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
   self.assertEqual(marker.read_text(),'keep')
 def test_no_personal_motion_branding(self):
  for p in (R/'dependencies/motion-studio').rglob('*'):
   if p.is_file() and p.suffix in ['.md','.html','.js','.mjs','.py']:
    s=p.read_text().lower()
    for bad in ['zaujaloma','zaujalo ma ai','martin gregor','martin.jpg','/users/lukassmola']:
     self.assertNotIn(bad,s,str(p))
if __name__=='__main__':unittest.main()
