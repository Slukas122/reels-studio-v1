#!/usr/bin/env python3
"""Transcript-led local reel editing with alignment on the edited audio."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import wave
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = Path('/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg')
FFPROBE = Path('/opt/homebrew/opt/ffmpeg-full/bin/ffprobe')
ALIGN_MODEL = 'small'
TEXT_MODEL = ROOT / 'models' / 'active.bin'


def executable(path: Path, fallback: str) -> str:
    found = str(path) if path.is_file() else shutil.which(fallback)
    if not found:
        raise RuntimeError(f'Missing {fallback}; run {ROOT / "scripts/setup_fast.sh"}')
    return found


def run(args: list[str], cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def probe(path: Path) -> dict:
    proc = subprocess.run([executable(FFPROBE, 'ffprobe'), '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def duration(path: Path) -> float:
    return float(probe(path)['format']['duration'])


def model(name: str):
    try:
        import stable_whisper
    except ImportError as exc:
        raise RuntimeError(f'Missing stable-ts; run {ROOT / "scripts/setup_fast.sh"} and use its .venv/bin/python') from exc
    return stable_whisper.load_model(name, device='cpu')


def high_quality_transcript(audio: Path, base: Path) -> str:
    if not TEXT_MODEL.is_file():
        raise RuntimeError(f'High-quality Czech model is missing: {TEXT_MODEL}. Run setup.sh')
    cli = executable(Path('/opt/homebrew/bin/whisper-cli'), 'whisper-cli')
    proc = subprocess.run([cli, '-m', str(TEXT_MODEL), '-f', str(audio), '-l', 'cs', '-oj', '-of', str(base), '-nt', '-np'], capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f'whisper-cli failed: {proc.stderr[-1000:]}')
    data = read_json(Path(str(base) + '.json'))
    text = ' '.join(str(item['text']).strip() for item in data.get('transcription', []))
    if not text.strip():
        raise RuntimeError('High-quality recognizer produced no Czech text')
    return text.strip()


def words_from_result(result) -> list[dict]:
    return [{'text': str(w.word).strip(), 'start': round(float(w.start), 3), 'end': round(float(w.end), 3)} for s in result.segments for w in s.words if str(w.word).strip()]


def source_audio(source: Path, target: Path) -> None:
    run([executable(FFMPEG, 'ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), '-map', '0:a:0', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(target)])


def profile_path(client: str) -> Path:
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,100}', client):
        raise ValueError('Client must be a lowercase domain or slug')
    return ROOT / 'profiles' / f'{client}.json'


def inspect(source: Path, project: Path, client: str | None = None) -> None:
    if not source.is_file():
        raise ValueError(f'Source does not exist: {source}')
    if project.exists() and any(project.iterdir()):
        raise ValueError(f'Project directory must be empty: {project}')
    project.mkdir(parents=True, exist_ok=True)
    media = probe(source)
    if not any(s['codec_type'] == 'audio' for s in media['streams']):
        raise ValueError('A spoken reel requires an audio stream')
    write_json(project / 'media.json', media)
    source_audio(source, project / 'source.wav')
    started = time.monotonic()
    result = model(ALIGN_MODEL).transcribe(str(project / 'source.wav'), language='cs', verbose=False)
    words = words_from_result(result)
    rough_text = ' '.join(w['text'] for w in words)
    accurate_text = high_quality_transcript(project / 'source.wav', project / 'source-text')
    write_json(project / 'transcript.json', {'language': 'cs', 'duration': duration(source), 'roughWords': words, 'roughText': rough_text, 'text': accurate_text, 'textModel': 'whisper.cpp large-v3', 'timingModel': ALIGN_MODEL, 'transcriptionSeconds': round(time.monotonic() - started, 2)})
    plan = {'source': str(source), 'language': 'cs', 'spokenText': '', 'segments': [], 'style': {'fontFamily': 'Arial', 'textColor': 'FFFFFF', 'accentColor': 'FFE07A', 'outlineColor': '101010', 'fontSize': 72}}
    if client:
        path = profile_path(client)
        if path.is_file():
            profile = read_json(path)
            if profile.get('status') == 'approved':
                plan['style'].update(profile.get('style') or {})
                plan['client'] = client
                shutil.copy2(path, project / 'client-profile.json')
            else:
                print(f'Client profile is not approved; using neutral style: {path}')
        else:
            print(f'Client profile not found; using neutral style: {path}')
    write_json(project / 'plan.json', plan)
    print(f'Transcript: {project / "transcript.json"}')
    print(f'Edit plan: {project / "plan.json"}')


def validate_plan(project: Path) -> tuple[dict, Path, list[dict], float]:
    plan = read_json(project / 'plan.json')
    source = Path(plan.get('source', '')).expanduser().resolve()
    if not source.is_file():
        raise ValueError('plan.source must be an existing absolute video path')
    if plan.get('language') != 'cs':
        raise ValueError('This version supports Czech speech and captions only')
    segments = plan.get('segments')
    if not isinstance(segments, list) or not segments:
        raise ValueError('Plan needs at least one selected segment')
    if len(segments) > 16:
        raise ValueError('At most 16 segments per reel')
    source_length = duration(source)
    output_length = 0.0
    for idx, s in enumerate(segments):
        start, end = float(s['start']), float(s['end'])
        if not all(map(math.isfinite, (start, end))) or start < 0 or end - start < 0.4 or end > source_length + 0.03:
            raise ValueError(f'Invalid segment {idx + 1}: {start}–{end}')
        focus = float(s.get('focusX', 0.5))
        if not 0 <= focus <= 1:
            raise ValueError(f'focusX outside 0–1 in segment {idx + 1}')
        zoom = float(s.get('zoom', 1.0))
        if not math.isfinite(zoom) or not 1.0 <= zoom <= 1.25:
            raise ValueError(f'zoom must be 1.0–1.25 in segment {idx + 1}')
        output_length += end - start
    if output_length > 90:
        raise ValueError('Reel exceeds 90 seconds; select a focused excerpt')
    if not str(plan.get('spokenText', '')).strip():
        raise ValueError('plan.spokenText must contain the exact speech retained in the edit')
    return plan, source, segments, output_length


def frames(project: Path) -> None:
    plan, source, segments, _ = validate_plan(project)
    folder = project / 'frames'
    folder.mkdir(exist_ok=True)
    ffmpeg = executable(FFMPEG, 'ffmpeg')
    made = []
    for idx, s in enumerate(segments, 1):
        for label, at in [('start', float(s['start']) + 0.15), ('middle', (float(s['start']) + float(s['end'])) / 2), ('end', float(s['end']) - 0.15)]:
            dest = folder / f'{idx:02d}-{label}.jpg'
            run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{at:.3f}', '-i', str(source), '-frames:v', '1', '-vf', 'scale=360:-2', str(dest)])
            made.append(dest)
    from PIL import Image, ImageDraw
    images = [Image.open(p).convert('RGB') for p in made]
    cell_w, cell_h = 380, max(im.height for im in images) + 42
    sheet = Image.new('RGB', (cell_w * 3, cell_h * len(segments)), '#191919')
    draw = ImageDraw.Draw(sheet)
    for i, im in enumerate(images):
        x, y = (i % 3) * cell_w + 10, (i // 3) * cell_h + 28
        sheet.paste(im, (x, y))
        draw.text((x, y - 20), made[i].stem, fill='white')
    sheet.save(folder / 'contact-sheet.jpg', quality=88)
    print(folder / 'contact-sheet.jpg')


def edited_audio(source: Path, segments: list[dict], output: Path) -> None:
    filters = []
    for idx, s in enumerate(segments):
        filters.append(f'[0:a]atrim=start={float(s["start"]):.3f}:end={float(s["end"]):.3f},asetpts=PTS-STARTPTS[a{idx}]')
    filters.append(''.join(f'[a{i}]' for i in range(len(segments))) + f'concat=n={len(segments)}:v=0:a=1[out]')
    run([executable(FFMPEG, 'ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), '-filter_complex', ';'.join(filters), '-map', '[out]', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(output)])


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text.casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()


def align_audio(audio: Path, expected: str) -> tuple[list[dict], dict]:
    heard_text = high_quality_transcript(audio, audio.parent / 'edited-text')
    similarity = SequenceMatcher(None, normalize(expected).split(), normalize(heard_text).split(), autojunk=False).ratio()
    char_similarity = SequenceMatcher(None, normalize(expected), normalize(heard_text), autojunk=False).ratio()
    if similarity < 0.78 or char_similarity < 0.88:
        raise ValueError(f'Edited audio differs from spokenText (ASR word similarity {similarity:.2f}, character similarity {char_similarity:.2f}). Review the cut and exact wording. Heard: {heard_text}')
    result = model(ALIGN_MODEL).align(str(audio), expected, language='cs', verbose=False)
    words = words_from_result(result)
    total = duration(audio)
    if not words or len(words) < len(expected.split()) * 0.85:
        raise ValueError('Alignment omitted too many words')
    zero = sum(w['end'] - w['start'] < 0.04 for w in words)
    zero_content = [w['text'] for w in words if w['end'] - w['start'] < 0.04 and len(normalize(w['text'])) > 4]
    if zero > max(4, len(words) * 0.12) or zero_content:
        raise ValueError(f'Alignment has {zero} near-zero-duration words; review transcript or use a better model')
    if any(w['start'] < 0 or w['end'] > total + 0.1 or w['end'] < w['start'] for w in words):
        raise ValueError('Aligned word times fall outside edited audio')
    for word in words:
        word['start'] = min(word['start'], total)
        word['end'] = min(word['end'], total)
    return words, {'asrWordSimilarity': round(similarity, 3), 'asrCharacterSimilarity': round(char_similarity, 3), 'asrHeard': heard_text, 'alignedWords': len(words), 'nearZeroWords': zero, 'nearZeroContentWords': zero_content}


def ass_color(rgb: str) -> str:
    rgb = rgb.lstrip('#')
    if not re.fullmatch(r'[0-9a-fA-F]{6}', rgb):
        raise ValueError(f'Invalid RGB color: {rgb}')
    return f'&H00{rgb[4:6]}{rgb[2:4]}{rgb[0:2]}&'


def ass_text(value: str) -> str:
    return value.replace('\\', ' ').replace('{', '(').replace('}', ')').replace('\n', ' ')


def ass_time(seconds: float) -> str:
    cs = max(0, int(round(seconds * 100)))
    h, remainder = divmod(cs, 360000)
    m, remainder = divmod(remainder, 6000)
    s, cent = divmod(remainder, 100)
    return f'{h}:{m:02d}:{s:02d}.{cent:02d}'


def srt_time(seconds: float) -> str:
    ms = max(0, int(round(seconds * 1000)))
    h, remainder = divmod(ms, 3600000)
    m, remainder = divmod(remainder, 60000)
    s, milli = divmod(remainder, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{milli:03d}'


def caption_groups(words: list[dict]) -> list[list[dict]]:
    groups, group = [], []
    for word in words:
        if group and (len(group) >= 4 or word['start'] - group[-1]['end'] > 0.3 or len(' '.join(w['text'] for w in group + [word])) > 29 or group[-1]['text'].endswith(('.', '?', '!', '…'))):
            groups.append(group)
            group = []
        group.append(word)
    if group:
        groups.append(group)
    return groups


def captions(output: Path, words: list[dict], style: dict, segments: list[dict] | None = None, effects: dict | None = None) -> None:
    segments = segments or []
    effects = effects or {}
    speech_duration = sum(float(segment['end']) - float(segment['start']) for segment in segments) if segments else words[-1]['end']
    family = style.get('fontFamily', 'Arial').replace(',', ' ')
    font_size = int(style.get('fontSize', 72))
    if not 38 <= font_size <= 110:
        raise ValueError('fontSize must be 38–110')
    white = ass_color(style.get('textColor', 'FFFFFF'))
    accent = ass_color(style.get('accentColor', 'FFD35A'))
    outline = ass_color(style.get('outlineColor', '101010'))
    header = '[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
    header += f'Style: Reel,{family},{font_size},{white},{accent},{outline},&H70000000&,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,370,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    if effects.get('labels'):
        header = header.replace('\n\n[Events]', f'\nStyle: Tag,{family},54,{white},{accent},{outline},&H700B101B&,-1,0,0,0,100,100,0,0,3,1,0,8,65,65,180,1\n\n[Events]')
    events = []
    srt = []
    groups = caption_groups(words)
    for group_index, group in enumerate(groups):
        for i, word in enumerate(group):
            if word['end'] - word['start'] < 0.04:
                continue
            next_start = group[i + 1]['start'] if i + 1 < len(group) else (groups[group_index + 1][0]['start'] if group_index + 1 < len(groups) else word['end'] + 0.10)
            start = max(0, word['start'])
            end = min(next_start, word['end'] + 0.10, speech_duration)
            if end - start < 0.04:
                continue
            chunks = []
            for j, item in enumerate(group):
                txt = ass_text(item['text'])
                chunks.append(f'{{\\c{accent}}}{txt}{{\\c{white}}}' if i == j else txt)
            events.append(f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Reel,,0,0,0,,{" ".join(chunks)}')
        srt.append((group[0]['start'], min(group[-1]['end'] + 0.1, speech_duration), ' '.join(w['text'] for w in group)))
    if effects.get('labels'):
        labels = effects['labels']
        if not isinstance(labels, list) or len(labels) != len(segments):
            raise ValueError('effects.labels must contain one label per segment')
        at = 0.0
        for segment, label in zip(segments, labels):
            span = float(segment['end']) - float(segment['start'])
            if label:
                events.append(f'Dialogue: 1,{ass_time(at)},{ass_time(at + min(2.2, span))},Tag,,0,0,0,,{ass_text(str(label))}')
            at += span
    (output / 'captions.ass').write_text(header + '\n'.join(events) + '\n', encoding='utf-8')
    (output / 'captions.srt').write_text(''.join(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n' for i, (a, b, text) in enumerate(srt, 1)), encoding='utf-8')


def make_cut_sounds(segments: list[dict], output: Path) -> Path:
    """Create restrained, local transition accents at the actual edit points."""
    rate = 48000
    total = sum(float(s['end']) - float(s['start']) for s in segments)
    samples = np.zeros(int((total + 0.2) * rate), dtype=np.float32)
    rng = np.random.default_rng(42)
    at = 0.0
    for index, segment in enumerate(segments):
        if index:
            count = int(0.16 * rate)
            t = np.arange(count, dtype=np.float32) / rate
            noise = rng.standard_normal(count).astype(np.float32)
            # Moving average removes brittle high frequency hiss.
            noise = np.convolve(noise, np.ones(18, dtype=np.float32) / 18, mode='same')
            whoosh = noise * np.sin(np.pi * t / 0.16) ** 2 * 0.13
            pop = np.sin(2 * np.pi * (130 * t + 210 * t * t)) * np.exp(-t * 38) * 0.09
            start = max(0, int((at - 0.055) * rate))
            samples[start:start + count] += whoosh[:min(count, len(samples) - start)] + pop[:min(count, len(samples) - start)]
        at += float(segment['end']) - float(segment['start'])
    target = output / 'cut-sounds.wav'
    with wave.open(str(target), 'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(rate)
        file.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())
    return target


def make_story_cards(cards: list[dict], output: Path) -> list[Path]:
    """Render editorial cards locally; no external images, font service or model needed."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    regular = bold = str(ROOT / 'assets/fonts/Inter.ttf')
    folder = output / 'cards'
    folder.mkdir(exist_ok=True)
    made = []
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise ValueError('Each story card must be an object')
        title = str(card.get('title', '')).strip()
        detail = str(card.get('detail', '')).strip()
        if not title or len(title) > 80 or len(detail) > 130:
            raise ValueError('Story card requires a short title and detail')
        w, h = 1080, 1920
        image = Image.new('RGB', (w, h), '#101522')
        draw = ImageDraw.Draw(image)
        for y in range(h):
            p = y / h
            draw.line((0, y, w, y), fill=(int(14 + 6*p), int(20 + 8*p), int(36 + 12*p)))
        # Soft light gives depth while leaving text legible.
        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((530, 245, 1320, 1060), fill=(252, 72, 103, 90))
        glow = glow.filter(ImageFilter.GaussianBlur(130))
        image = Image.alpha_composite(image.convert('RGBA'), glow)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((68, 90, 545, 155), radius=32, fill='#283247')
        draw.ellipse((88, 110, 110, 132), fill='#FF5870')
        draw.text((127, 109), 'FOTKA NA COMMONS', font=ImageFont.truetype(bold, 27), fill='#F5F6FA')
        draw.text((70, 228), f'{index:02d}', font=ImageFont.truetype(bold, 190), fill='#394153')
        draw.rounded_rectangle((64, 465, 1016, 1330), radius=55, fill='#F6F7FA')
        draw.rounded_rectangle((111, 518, 247, 654), radius=34, fill='#FF5870')
        # Simple vector upload/photo glyph.
        cx, cy = 179, 586
        draw.line((cx, cy + 25, cx, cy - 24), fill='white', width=10)
        draw.line((cx - 19, cy - 6, cx, cy - 26, cx + 19, cy - 6), fill='white', width=10, joint='curve')
        draw.line((cx - 28, cy + 35, cx + 28, cy + 35), fill='white', width=9)
        draw.text((113, 701), 'KROK' if index else 'RYCHLÝ NÁVOD', font=ImageFont.truetype(bold, 32), fill='#EF5169')
        title_font = ImageFont.truetype(bold, 88 if len(title) < 38 else 76)
        # Wrap to the card width while preserving explicitly authored line breaks.
        lines = []
        for paragraph in title.split('\n'):
            line = ''
            for word in paragraph.split():
                candidate = (line + ' ' + word).strip()
                if line and draw.textbbox((0, 0), candidate, font=title_font)[2] > 825:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            if line:
                lines.append(line)
        if len(lines) > 3:
            raise ValueError(f'Story card title too long: {title}')
        y = 771
        for line in lines:
            draw.text((108, y), line, font=title_font, fill='#172033')
            y += 104
        if detail:
            detail_font = ImageFont.truetype(regular, 43)
            y = max(y + 42, 1110)
            for line in detail.split('\n'):
                draw.text((112, y), line, font=detail_font, fill='#5E697C')
                y += 55
        # Timeline is part of the composition, separate from spoken captions.
        for dot in range(len(cards)):
            x = 70 + dot * 77
            draw.rounded_rectangle((x, 1407, x + (55 if dot == index else 41), 1422), radius=7, fill='#FF5870' if dot == index else '#566078')
        path = folder / f'card-{index + 1:02d}.png'
        image.convert('RGB').save(path, optimize=True)
        made.append(path)
    return made


def render_video(source: Path, segments: list[dict], edited_wav: Path, output: Path, style: dict, effects: dict) -> None:
    filters = []
    inputs = [executable(FFMPEG, 'ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), '-i', str(edited_wav)]
    sfx_index = None
    if effects.get('cutSounds') and len(segments) > 1:
        sfx_index = 2
        inputs += ['-i', str(make_cut_sounds(segments, output))]
    cards = effects.get('cards')
    if cards:
        if not isinstance(cards, list) or len(cards) != len(segments):
            raise ValueError('effects.cards must contain one card per segment')
        card_paths = make_story_cards(cards, output)
        first_card_input = 3 if sfx_index is not None else 2
        for idx, (s, path) in enumerate(zip(segments, card_paths)):
            span = float(s['end']) - float(s['start'])
            inputs += ['-loop', '1', '-framerate', '30', '-t', f'{span:.3f}', '-i', str(path)]
            filters.append(f'[{first_card_input + idx}:v]trim=duration={span:.3f},setpts=PTS-STARTPTS,fps=30,format=yuv420p[v{idx}]')
    else:
        for idx, s in enumerate(segments):
            focus = float(s.get('focusX', 0.5))
            zoom = float(s.get('zoom', 1.0))
            width = int(math.ceil(1080 * zoom / 2) * 2)
            height = int(math.ceil(1920 * zoom / 2) * 2)
            filters.append(f'[0:v]trim=start={float(s["start"]):.3f}:end={float(s["end"]):.3f},setpts=PTS-STARTPTS,scale={width}:{height}:force_original_aspect_ratio=increase,crop=1080:1920:x=(iw-1080)*{focus:.4f}:y=(ih-1920)/2,setsar=1,fps=30,format=yuv420p[v{idx}]')
    post = ''
    if style.get('maskSourceCaptions'):
        post = ',drawbox=x=80:y=1330:w=920:h=270:color=black@0.88:t=fill'
    if effects.get('colorGrade'):
        post += ',eq=contrast=1.07:saturation=1.12'
    if effects.get('cutFlashes'):
        at = 0.0
        for segment in segments[:-1]:
            at += float(segment['end']) - float(segment['start'])
            post += f",drawbox=x=0:y=0:w=iw:h=ih:color=white@0.28:t=fill:enable='between(t,{at:.3f},{at + .067:.3f})'"
            accent_hex = str(style.get('accentColor', 'FFD35A')).lstrip('#')
            ass_color(accent_hex)
            post += f",drawbox=x=0:y=0:w=22:h=ih:color=0x{accent_hex}@0.9:t=fill:enable='between(t,{at:.3f},{at + .22:.3f})'"
    filters.append(''.join(f'[v{i}]' for i in range(len(segments))) + f'concat=n={len(segments)}:v=1:a=0{post},ass=filename=captions.ass[v]')
    if sfx_index is not None:
        filters.append('[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[voice]')
        filters.append(f'[voice][{sfx_index}:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]')
    else:
        filters.append('[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]')
    run(inputs + ['-filter_complex', ';'.join(filters), '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', 'reel.mp4'], cwd=output)


def audio_lag(reference: Path, rendered: Path, output: Path) -> tuple[float, float]:
    sample_rate = 2000
    check = output / 'render-check.wav'
    reference_check = output / 'reference-check.wav'
    run([executable(FFMPEG, 'ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(reference), '-t', '8', '-ar', str(sample_rate), '-ac', '1', '-c:a', 'pcm_s16le', str(reference_check)])
    run([executable(FFMPEG, 'ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(rendered), '-t', '8', '-vn', '-ar', str(sample_rate), '-ac', '1', '-c:a', 'pcm_s16le', str(check)])
    def samples(path):
        with wave.open(str(path), 'rb') as w:
            return np.frombuffer(w.readframes(min(w.getnframes(), sample_rate * 8)), dtype=np.int16).astype(np.float32)
    a = samples(reference_check)[::2]
    b = samples(check)[::2]
    length = min(len(a), len(b))
    a, b = a[:length], b[:length]
    a -= a.mean(); b -= b.mean()
    max_shift = 250
    scores = []
    for shift in range(-max_shift, max_shift + 1):
        if shift >= 0:
            x, y = a[shift:], b[:length-shift]
        else:
            x, y = a[:length+shift], b[-shift:]
        denom = np.linalg.norm(x) * np.linalg.norm(y)
        scores.append(float(np.dot(x, y) / denom) if denom else 0.0)
    best = int(np.argmax(scores)) - max_shift
    return round(best / (sample_rate / 2), 3), round(scores[best + max_shift], 3)


def qa(project: Path, expected: float, alignment: dict, timings: dict) -> None:
    output = project / 'output'
    path = output / 'reel.mp4'
    media = probe(path)
    streams = media['streams']
    video = next(s for s in streams if s['codec_type'] == 'video')
    has_audio = any(s['codec_type'] == 'audio' for s in streams)
    actual = duration(path)
    lag, correlation = audio_lag(output / 'edited.wav', path, output)
    issues = []
    events = []
    for line in (output / 'captions.ass').read_text(encoding='utf-8').splitlines():
        if line.startswith('Dialogue: 0,'):
            parts = line.split(',', 3)
            def parse_ass(value: str) -> float:
                h, m, rest = value.split(':')
                return int(h) * 3600 + int(m) * 60 + float(rest)
            events.append((parse_ass(parts[1]), parse_ass(parts[2])))
    if any(events[i][0] < events[i - 1][1] - 0.005 for i in range(1, len(events))):
        issues.append('overlapping caption events')
    if any(end > actual + 0.02 for _, end in events):
        issues.append('caption extends past final video frame')
    if (video['width'], video['height']) != (1080, 1920): issues.append('wrong dimensions')
    if not has_audio: issues.append('missing audio')
    if abs(actual - expected) > 0.35: issues.append('unexpected duration')
    if abs(lag) > 0.12 or correlation < 0.65: issues.append('rendered audio does not match aligned cut')
    report = {'passedTechnicalQa': not issues, 'issues': issues, 'durationSeconds': actual, 'expectedSeconds': expected, 'audioLagSeconds': lag, 'audioCorrelation': correlation, 'alignment': alignment, 'timingsSeconds': timings}
    write_json(output / 'qa.json', report)
    if issues: raise ValueError(f'Technical QA failed: {issues}')


def render(project: Path) -> None:
    started = time.monotonic()
    plan, source, segments, expected = validate_plan(project)
    output = project / 'output'
    output.mkdir(exist_ok=True)
    edited_audio(source, segments, output / 'edited.wav')
    cut_seconds = time.monotonic() - started
    words, alignment = align_audio(output / 'edited.wav', plan['spokenText'])
    align_seconds = time.monotonic() - started - cut_seconds
    write_json(output / 'aligned-words.json', words)
    captions(output, words, plan.get('style') or {}, segments, plan.get('effects') or {})
    render_video(source, segments, output / 'edited.wav', output, plan.get('style') or {}, plan.get('effects') or {})
    render_seconds = time.monotonic() - started - cut_seconds - align_seconds
    qa(project, expected, alignment, {'cutAudio': round(cut_seconds, 2), 'align': round(align_seconds, 2), 'render': round(render_seconds, 2), 'total': round(time.monotonic() - started, 2)})
    print(output / 'reel.mp4')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('inspect'); a.add_argument('source', type=Path); a.add_argument('--project', type=Path, required=True); a.add_argument('--client')
    for name in ('frames', 'render'):
        p = sub.add_parser(name); p.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    try:
        if args.cmd == 'inspect': inspect(args.source.expanduser().resolve(), project, args.client)
        elif args.cmd == 'frames': frames(project)
        else: render(project)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
