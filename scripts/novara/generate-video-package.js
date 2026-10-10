const fs = require('node:fs/promises');

const API_KEY = process.env.GEMINI_API_KEY;
const MODEL = process.env.GEMINI_MODEL || 'gemini-3.8-flash';
const INPUT = 'artifacts/novara-research.md';

if (!API_KEY) {
  console.error('Missing GEMINI_API_KEY. Add it in GitHub repository Settings > Secrets and variables > Actions.');
  process.exit(1);
}

async function main() {
  const research = await fs.readFile(INPUT, 'utf8');
  const prompt = `
You are the original content producer for NOVARA, a global science, technology, AI, future, education and human-body knowledge YouTube Shorts channel.

Use the attached YouTube trend research only to understand topics and viewer curiosity. Do NOT copy video titles word-for-word, scripts, distinctive phrasing, or creators' creative choices. Pick one promising topic and make a genuinely original explainer.

Create one approximately 40-second YouTube Short with exactly four scenes of about 10 seconds each.
- Narration: natural conversational Urdu in Urdu script, easy for Pakistani and international Urdu-speaking viewers to understand.
- Visual prompts: written in English for Google Flow. Each scene prompt must be specific, cinematic, visually strong, and suitable for a vertical 9:16 video. Avoid brand logos, copyrighted characters, and visible text that may render incorrectly. Mention continuity of the same visual style across all scenes.
- Each scene must include a separate Urdu voiceover line that can realistically fit within 10 seconds.
- Structure: immediate curiosity hook; clear explanation; surprising but accurate detail; satisfying ending with NOVARA and a natural subscribe/share call-to-action.
- Keep claims scientifically responsible. Do not invent numbers, studies, medical diagnoses, or breaking-news claims. For health content, do not diagnose viewers or imply that symptoms always mean a disease. If a claim needs verification, mark it for human fact-checking rather than presenting it as certain.
- Produce a title, description in English and Urdu, 8-15 relevant hashtags, and a pinned comment that invites a genuine audience response.
- Do not promise virality or guaranteed views.
- Return ONLY valid JSON, no Markdown fences, using this structure:
{
  "topic": "string",
  "why_this_topic": "short string",
  "fact_check_notes": ["string"],
  "title": "string",
  "description": "string",
  "hashtags": ["string"],
  "pinned_comment": "string",
  "scenes": [
    {"scene": 1, "duration_seconds": 10, "visual_prompt_en": "string", "voiceover_urdu": "string", "on_screen_text_en": "short string"}
  ],
  "final_review_checklist": ["string"]
}
There must be exactly 4 scenes. Scene 4 must end with NOVARA and a subscribe/share call-to-action in the Urdu narration. Do not claim that the generated package has been medically or scientifically verified.

YOUTUBE TREND RESEARCH:
${research}
`;

  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-goog-api-key': API_KEY,
    },
    body: JSON.stringify({
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: 'application/json',
        temperature: 0.8,
        maxOutputTokens: 5000,
      },
    }),
    signal: AbortSignal.timeout(90000),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.error?.message || `HTTP ${response.status}`;
    throw new Error(`Gemini generation failed: ${message}`);
  }

  const text = payload.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('').trim();
  if (!text) throw new Error('Gemini returned no text. Check the API key and model access.');

  let pkg;
  try {
    pkg = JSON.parse(text);
  } catch {
    throw new Error('Gemini did not return valid JSON. Run the workflow again; no output package was saved.');
  }

  if (!Array.isArray(pkg.scenes) || pkg.scenes.length !== 4) {
    throw new Error('Generated package must contain exactly 4 scenes. Run the workflow again.');
  }

  const lines = [
    '# NOVARA — Original Short Video Package',
    '',
    `**Topic:** ${pkg.topic || 'Not provided'}`,
    '',
    `**Why this topic:** ${pkg.why_this_topic || 'Not provided'}`,
    '',
    '## Title',
    '',
    pkg.title || '',
    '',
    '## Description',
    '',
    pkg.description || '',
    '',
    '## Hashtags',
    '',
    (pkg.hashtags || []).join(' '),
    '',
    '## Pinned comment',
    '',
    pkg.pinned_comment || '',
    '',
    '## Scenes — English Google Flow prompts + Urdu narration',
    '',
  ];

  for (const scene of pkg.scenes) {
    lines.push(
      `### Scene ${scene.scene} — ${scene.duration_seconds} seconds`,
      '',
      '**Google Flow visual prompt (English)**',
      '',
      scene.visual_prompt_en || '',
      '',
      '**Urdu narration**',
      '',
      scene.voiceover_urdu || '',
      '',
      `**On-screen text (English):** ${scene.on_screen_text_en || ''}`,
      '',
    );
  }

  lines.push('## Fact-check notes', '', ...(pkg.fact_check_notes || []).map((note) => `- ${note}`), '', '## Before publishing', '', ...(pkg.final_review_checklist || []).map((item) => `- [ ] ${item}`), '', '> AI-generated draft. Verify factual claims, check Urdu pronunciation and scene timing, watch the complete export, and review rights before publishing. This workflow does not create a video or upload to YouTube.', '');

  await fs.writeFile('artifacts/novara-video-package.md', lines.join('\n'), 'utf8');
  await fs.writeFile('artifacts/novara-video-package.json', JSON.stringify(pkg, null, 2), 'utf8');
  console.log('Created artifacts/novara-video-package.md and artifacts/novara-video-package.json');
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
