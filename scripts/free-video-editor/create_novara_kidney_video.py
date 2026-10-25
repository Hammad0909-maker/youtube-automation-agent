#!/usr/bin/env python3
"""Create NOVARA's kidney-warning explainer using free Pillow, eSpeak and FFmpeg."""
import argparse, subprocess, tempfile, textwrap
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W,H=1280,720
OUTLINE=(51,197,183); WHITE=(243,248,250); AMBER=(255,184,90); MUTED=(170,194,204)
SCENES=[
("5 SILENT KIDNEY WARNING SIGNS","Your kidneys can lose much of their filtering ability without causing a single ache in your back. Chronic kidney disease can develop silently for years, with few or no obvious symptoms. But sometimes, your body gives subtle clues that something isn't right. Here are five warning signs you shouldn't ignore—and stay until the end to discover two important tests that can detect kidney problems early."),
("SIGN 1 • PERSISTENT PUFFY EYES","Sign number one: Persistent puffiness around your eyes, especially in the morning. Occasional puffiness can result from poor sleep, allergies, or other common causes. But persistent swelling, particularly around your eyes or in your feet and ankles, deserves attention. When the kidneys' filtering barriers become damaged, they can allow albumin—a protein normally retained in your blood—to leak into your urine. When blood protein levels fall, fluid can accumulate in body tissues, sometimes causing noticeable puffiness. Puffy eyes alone don't prove you have kidney disease. But persistent, unexplained swelling is worth discussing with a healthcare professional."),
("SIGN 2 • PERSISTENT FOAMY URINE","Sign number two: Foamy urine that keeps happening. A few bubbles are usually nothing to worry about. A fast stream or concentrated urine can create them naturally. But persistent, dense foam can sometimes indicate protein leaking into your urine. Think of healthy kidneys like an ultra-fine kitchen strainer. They allow waste products to pass through while retaining essential proteins, including albumin. When this microscopic filtration barrier becomes damaged, protein can slip through into your urine. This is called albuminuria, and it can be an early sign of kidney disease—even when you feel perfectly normal. Remember, foam alone cannot tell you whether protein is present. A urine albumin-to-creatinine ratio test, known as uACR, can check for abnormal albumin leakage."),
("SIGN 3 • PERSISTENT, UNEXPLAINED ITCHING","Sign number three: Persistent itching without an obvious cause. Dry skin, allergies, and common skin conditions are frequent causes of itching. But advanced kidney disease can also cause persistent itching, sometimes across large areas of the body. When kidney function declines significantly, the body's balance of minerals and other substances can change. Inflammation and changes in how nerves process sensations may also contribute. The result can be uncomfortable itching without an obvious explanation. Itching alone is not a reliable way to identify kidney disease. But if it persists, particularly alongside swelling, unusual fatigue, or other concerning symptoms, speak with a healthcare professional. And there's another important clue to understand: what happens when your kidneys struggle to clear waste from your bloodstream?"),
("SIGN 4 • METALLIC TASTE OR UNUSUAL BREATH","When the kidneys struggle to clear waste, it doesn't just affect processes throughout the body. In advanced disease, waste products can also affect your mouth and breath. Sign number four: A persistent metallic taste or ammonia-like breath. Dental problems, medications, infections, and acid reflux can all cause these changes. But when kidney function becomes severely reduced, urea can accumulate in the blood. Urea entering saliva can be converted into ammonia, contributing to an unpleasant taste or ammonia-like breath. A strange taste after one meal doesn't mean kidney disease. But persistent, unexplained changes deserve medical attention, especially when other symptoms are present. Sometimes, the warning isn't pain. It's a change you barely notice."),
("SIGN 5 • UNEXPLAINED FATIGUE","And when kidney function declines, oxygen delivery can become another problem. Sign number five: Fatigue that doesn't seem to go away. If you constantly feel exhausted, even after sleeping, don't automatically blame your busy schedule. Healthy kidneys produce a hormone called erythropoietin, or EPO. It signals your bone marrow to produce red blood cells, which carry oxygen throughout your body. As kidney disease advances, the kidneys may produce less EPO. This can contribute to anemia, leaving you feeling weak, tired, dizzy, or unable to concentrate. Some people with kidney disease also experience restless legs, although this symptom has many possible causes. Fatigue doesn't automatically mean kidney damage. But persistent exhaustion deserves investigation, particularly if you have diabetes, high blood pressure, or other kidney disease risk factors."),
("TWO IMPORTANT KIDNEY TESTS","The good news is that you don't have to wait for symptoms to appear before checking your kidney health. The first important test is eGFR, which stands for estimated glomerular filtration rate. It uses your blood creatinine level and other information to estimate how effectively your kidneys filter blood."),
("eGFR  |  uACR",""),
("TWO IMPORTANT KIDNEY TESTS","The second test is uACR, the urine albumin-to-creatinine ratio. It checks whether albumin, an important blood protein, is leaking into your urine. This matters because albumin leakage can occur even when your eGFR is still within the normal range. If you have diabetes, high blood pressure, cardiovascular disease, or a family history of kidney disease, ask your healthcare professional whether screening is appropriate. One abnormal result doesn't automatically confirm chronic kidney disease. Doctors interpret results in context, and the condition generally involves abnormalities that persist for at least three months."),
("HOW TO PROTECT YOUR KIDNEYS","So, what can you do to protect your kidneys? Keep your blood pressure and blood sugar under control. Stay physically active, eat a balanced diet, and drink enough water for your individual needs. Certain common pain relievers, like ibuprofen or naproxen, can temporarily clamp down on blood flow to your kidneys—a risk that jumps if you are dehydrated or already managing kidney concerns. That is why avoiding frequent, unguided use is essential for protecting your long-term filtration. And don't assume that drinking excessive amounts of water will repair damaged kidneys. Some people with advanced kidney disease actually need to limit their fluid intake under medical supervision. Small, consistent habits can make a meaningful difference to your long-term health."),
("NOVARA • SCIENCE-BACKED ANSWERS. BETTER HEALTH.","Your kidneys can struggle long before you feel seriously ill. Recognize the warning signs. Don't ignore persistent changes. And when appropriate, get tested. Subscribe to NOVARA for more science-backed answers to everyday health questions. Your body deserves to understand the truth.")
]
DISCLAIMER="This video is for educational purposes only and does not replace professional medical advice, diagnosis, or treatment. These symptoms can have many causes and do not independently establish kidney disease. Consult a qualified healthcare professional if you experience persistent symptoms or have concerns about your kidney health."

def make_slide(path,title,index):
    y=np.linspace(0,1,H)[:,None,None]
    a=np.array([8,20,37],dtype=np.float32)[None,None,:]
    b=np.array([10,53,67],dtype=np.float32)[None,None,:]
    im=Image.fromarray(np.broadcast_to(a*(1-y)+b*y,(H,W,3)).astype('uint8').copy())
    d=ImageDraw.Draw(im)
    bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    d.text((60,35),'NOVARA • SCIENCE-BACKED HEALTH',font=ImageFont.truetype(bold,22),fill=OUTLINE)
    d.text((60,90),title,font=ImageFont.truetype(bold,35),fill=WHITE)
    d.line((60,150,1220,150),fill=OUTLINE,width=3)
    # stylized kidney pair
    for cx,cy in [(360,390),(500,390)]:
        d.ellipse((cx-62,cy-92,cx+62,cy+92),fill=(140,61,75),outline=(237,139,145),width=4)
        d.ellipse((cx+5,cy-48,cx+83,cy+49),fill=(10,45,58))
        d.line((cx+8,cy-12,cx+53,cy-12),fill=(90,178,229),width=10)
        d.line((cx+8,cy+15,cx+53,cy+15),fill=(235,96,105),width=10)
    rounded=(660,235,1190,550)
    d.rounded_rectangle(rounded,radius=22,fill=(5,18,32),outline=OUTLINE,width=3)
    info={
      1:("FILTERING","Blood filtration can decline","before obvious symptoms appear."),
      2:("ALBUMIN","A blood protein can leak","through a damaged filter."),
      3:("FOAM IS NOT A TEST","Persistent foam can have","several possible causes."),
      4:("ITCHING","Advanced kidney disease is","one possible cause."),
      5:("UREA → AMMONIA","Severe kidney dysfunction can","affect taste and breath."),
      6:("EPO → RED BLOOD CELLS","Kidney disease can contribute","to anemia and fatigue."),
      7:("eGFR","HOW WELL YOUR KIDNEYS FILTER",""),
      8:("eGFR","HOW WELL YOUR KIDNEYS FILTER","uACR — WHETHER ALBUMIN IS LEAKING"),
      9:("uACR","CHECKS FOR ALBUMIN LEAKAGE",""),
      10:("PROTECT YOUR KIDNEYS","Control blood pressure and sugar","Use medicines only as directed."),
      11:("NOVARA","SCIENCE-BACKED ANSWERS.","BETTER HEALTH.")
    }.get(index,("KIDNEY HEALTH","Understand the warning signs","Talk to a qualified professional."))
    d.text((700,280),info[0],font=ImageFont.truetype(bold,30),fill=AMBER)
    d.text((700,355),info[1],font=ImageFont.truetype(reg,22),fill=WHITE)
    if info[2]: d.text((700,405),info[2],font=ImageFont.truetype(reg,22),fill=WHITE)
    d.text((60,625),'Illustrative explainer • Not a diagnostic test',font=ImageFont.truetype(reg,18),fill=MUTED)
    d.text((970,675),'NOVARA • KNOW YOUR BODY',font=ImageFont.truetype(bold,15),fill=MUTED)
    im.save(path,quality=90)

def run(cmd): subprocess.run(cmd,check=True)
def duration(p):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],text=True).strip())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',default='rendered/novara-kidney-warning-signs.mp4')
    ap.add_argument('--workdir',default='rendered/assets')
    a=ap.parse_args()
    for cmd in ('ffmpeg','ffprobe','espeak'):
        if not __import__('shutil').which(cmd): raise SystemExit(f'Missing required tool: {cmd}')
    out=Path(a.output).resolve(); work=Path(a.workdir).resolve(); work.mkdir(parents=True,exist_ok=True)
    images=[]; audios=[]; durations=[]
    for i,(title,spoken) in enumerate(SCENES,1):
        img=work/f'scene-{i:02d}.jpg'; make_slide(img,title,i); images.append(img)
        wav=work/f'voice-{i:02d}.wav'; audios.append(wav)
        if spoken: run(['espeak','-v','en-us','-s','165','-p','44','-a','170','-w',str(wav),spoken])
        else: run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','anullsrc=r=22050:cl=mono','-t','2','-acodec','pcm_s16le',str(wav)])
        durations.append(2.0 if not spoken else duration(wav))
    disc=work/'medical-disclaimer.jpg'; make_slide(disc,'MEDICAL DISCLAIMER',12)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); lines=[]
        for img,dur in zip(images,durations): lines += [f"file '{img.as_posix()}'\n",f'duration {dur:.6f}\n']
        lines += [f"file '{disc.as_posix()}'\n",'duration 7.000000\n',f"file '{disc.as_posix()}'\n"]
        listing=td/'images.txt'; listing.write_text(''.join(lines))
        video=td/'video.mp4'; total=sum(durations)+7
        run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p','-r','12','-t',str(total),'-an','-c:v','libx264','-preset','ultrafast','-crf','25',str(video)])
        normalized=[]
        for i,wav in enumerate(audios):
            dst=td/f'a{i:02d}.wav'; normalized.append(dst)
            run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-ar','22050','-ac','1','-c:a','pcm_s16le',str(dst)])
        alist=td/'audio.txt'; alist.write_text(''.join(f"file '{p.as_posix()}'\n" for p in normalized))
        wav=td/'narration.wav'; run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(alist),'-c:a','pcm_s16le',str(wav)])
        full=td/'full.m4a'; run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-f','lavfi','-t','7','-i','anullsrc=r=22050:cl=mono','-filter_complex','[0:a][1:a]concat=n=2:v=0:a=1[a]','-map','[a]','-c:a','aac','-b:a','128k',str(full)])
        out.parent.mkdir(parents=True,exist_ok=True)
        run(['ffmpeg','-y','-loglevel','error','-i',str(video),'-i',str(full),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(out)])
    print(f'Created {out} ({duration(out):.1f}s)')
if __name__=='__main__': main()
