# Platform interface and usable canvas

Design the **whole 9:16 picture** for the viewer, then protect only the elements that must be read or recognized. Footage, atmosphere, textures and color may fill the canvas behind app controls. Do not shrink the entire video into a narrow central card to satisfy a generic safe rectangle.

## Choose the delivery strategy

1. Record every actual placement: TikTok organic or ad, Instagram Reels organic or ad, Facebook Reels organic or ad, and YouTube Shorts if requested. The same app can use different controls in different placements.
2. Before layout, obtain current official templates or inspect a current in-app publishing preview for each placement. Record the date, link or screenshot and the planned profile/description length. If those are unavailable, use the script's clearly labeled **editorial fallback masks** as a rough starting point, not as platform specifications.
3. For one shared export, keep essential text and the key subject clear in **every** target preview. Use the free space around irregular controls; do not automatically use the smallest enclosing rectangle. If that compromise makes the design weak, render platform-specific graphic positions or crops from the same edit and deliver clearly named variants.
4. Keep backgrounds full bleed. Use the largest scale, line length and subject framing that pass each target preview. Only the essential element's actual visible bounds need protection, including animation frames.

What counts as essential: headings, captions, numbers, claims, CTA, date/source credits, logo, face, product and the action that proves the point. For example, a video of a rover can extend under the right icons, but the rover's critical movement should stay visible. Do not solve overlap merely by making text too small to read on a phone.

## Required final-export check

1. Sample the **encoded final MP4**, not only source stills. Include the opening, each distinct layout, the longest caption, the ending and moments where the subject moves toward a control.
2. Apply a separate interface overlay for TikTok, Instagram Reels and Facebook Reels. When no current official or in-app overlay is available, run `python3 scripts/preview_platform_ui.py final.mp4 --platform tiktok instagram facebook --out ui-check.jpg`. The bundled profiles are editable planning approximations. For a real posting account, replace them with captured/applicable UI using `--profiles`.
3. Inspect every platform at phone size. If any essential content is obscured, adjust its layer or crop and rerender. Check the new **final** MP4 again. If a shared layout becomes cramped, make platform variants rather than leaving large unused bars.
4. Record the target placements, source of each overlay, caption assumptions, frames checked and any unresolved limitation in the project notes. A posting preview in the destination app is the final placement check.

TikTok says its safe zone varies with dimensions, caption length and extra formats: https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads?lang=en-GB . Meta offers a Reels safe-zone checker for Facebook and Instagram: https://www.facebook.com/business/ads/facebook-instagram-reels-ads . YouTube Shorts provides visual guides in its editor: https://support.google.com/youtube/answer/16215842?hl=en-GB . These sources support checking each interface; none makes a single fixed rectangle universally safe.
