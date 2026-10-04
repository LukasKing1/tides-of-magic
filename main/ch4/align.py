import subprocess, json, sys, re
from pocketsphinx import Decoder
def align(f, txt):
    txt=re.sub(r"[^a-z' ]"," ",txt.lower()); txt=re.sub(r"\s+"," ",txt).strip()
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    d=Decoder(samprate=16000, bestpath=False); d.set_align_text(txt)
    d.start_utt(); d.process_raw(raw, full_utt=True); d.end_utt()
    return [(re.sub(r'\(\d\)','',s.word), s.start_frame/100, s.end_frame/100) for s in d.seg()]
if __name__=='__main__':
    sys.path.insert(0,'/home/claude/main'); import script_v2 as S
    T={it[0]:it[3] for n,t,items in S.CH for it in items}
    out={}
    for i in sys.argv[1:]:
        out[i]=align(f'/home/claude/main/audio/{i}.mp3', T[i])
        print(i, ' '.join(f'{w}@{a:.2f}' for w,a,b in out[i] if w!='<sil>'))
    json.dump(out,open('/home/claude/main/ch4/align.json','w'))
