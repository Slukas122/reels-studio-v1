# Text fit and final-frame checks

Text is approved by its rendered bounds, not by character count alone. This applies to subtitles, question cards, names, titles, statistics, CTA buttons and animated text at every phase of entry and exit.

1. Define the usable rectangle after the platform UI mask and any protected face, hand, product or data area. Use the actual target format and check each target app.
2. Measure the exact copy in the final font, weight, size and letter spacing. Include Czech diacritics, punctuation, line height, stroke/shadow and every label inside the same component. Use the longest real title or name, not a placeholder. If text is dynamic, measure all variants.
3. Wrap at word boundaries. Keep Czech one-letter prepositions and conjunctions with the following word; keep numbers with units. Limit lines by the visual hierarchy. If the block exceeds the rectangle, shorten editorial copy without changing meaning, increase its container, move it, or reduce type only while still readable at phone size. Never let automatic shrink make a card technically fit but practically illegible.
4. Check both the internal box (`text + padding <= component`) and external position (`component <= safe rectangle`). A background box cannot hide overflow. A style that has no background still needs a measured text rectangle.
5. Anchor timed graphics to source word IDs or stable edit events when the renderer supports them. After any recut, regenerate timings and inspect the final composition; absolute seconds can drift.
6. From the final encoded MP4, inspect frames with the longest text, every layout, animated extremes, and a phone-size interface-mask preview. Check the actual full phrase, not only the first frame of an animation. Re-export after a fix and recheck the affected frames.

For a fixed card, `../scripts/check_text_fit.py` measures its exact text against a box using the final font file, font size, padding and line limit. It returns a failing exit code for overflow. Measure every dynamic copy variant; this preflight does not replace final-frame inspection because browser font rendering, animation, shadows and platform UI can still change the visible result.

For spoken captions, group by sense and breath as well as width. Avoid an isolated final word if it can remain with the preceding phrase without crowding. Subtitle text must match audible words and align to the **final edited audio**. Editorial cards may paraphrase a sourced idea, but must not masquerade as a subtitle or direct quote.
