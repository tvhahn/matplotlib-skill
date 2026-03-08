Convert a web article to a podcast episode.

The user will provide a URL as $ARGUMENTS. Follow these steps:

1. Scrape the article directly to a file (keeps text out of context):
   ```
   uv run ~/Documents/podcast-tools/scrape-article.py <URL> > ~/Documents/podcast-tools/foldercast/library/articles/_draft.txt
   ```
2. Read only the first ~5 lines of `_draft.txt` to determine the article title. Generate a URL-safe filename: lowercase, replace spaces with hyphens, remove special characters, truncate to 80 chars. Then rename:
   ```
   mv ~/Documents/podcast-tools/foldercast/library/articles/_draft.txt ~/Documents/podcast-tools/foldercast/library/articles/<FILENAME>.txt
   ```
3. Copy the raw scraped file for debugging (before any edits):
   ```
   cp ~/Documents/podcast-tools/foldercast/library/articles/<FILENAME>.txt ~/Documents/podcast-tools/raw-articles/<FILENAME>.txt
   ```
4. Insert paragraph pauses so kokoro-tts adds a brief silence between paragraphs:
   ```
   python3 -c "
   import sys
   lines = open(sys.argv[1]).read().strip().split('\n')
   result = '\n...\n'.join(lines)
   open(sys.argv[1], 'w').write(result + '\n')
   " ~/Documents/podcast-tools/foldercast/library/articles/<FILENAME>.txt
   ```
5. Clean the text in-place using the **Edit tool** with targeted replacements. IMPORTANT: preserve the author's original wording — do NOT summarize, paraphrase, or rewrite.
   Read the file (use `offset`/`limit` to process in sections for very long articles). Make these mechanical edits:
   - Remove markdown link syntax `[text](url)` → keep just `text`
   - Remove image references, HTML tags, and code blocks
   - Replace abbreviations using `replace_all: true` for each:
     - `e.g.` → `for example`
     - `i.e.` → `that is`
     - `vs.` → `versus`
     - `etc.` → `and so on`
     - (and similar abbreviations that sound odd when spoken)
   - Preserve paragraph structure (blank lines between paragraphs)
   Each Edit call only puts the small old/new string pair in context, not the full article.
6. Run kokoro-tts via GPU Docker container to generate the audio file:
   ```
   docker run --rm --gpus all \
     -v ~/Documents/podcast-tools/kokoro-models:/models:ro \
     -v ~/Documents/podcast-tools/foldercast/library/articles:/output \
     kokoro-tts-gpu \
     /output/<FILENAME>.txt /output/<FILENAME>.mp3 \
     --model /models/kokoro-v1.0.onnx \
     --voices /models/voices-v1.0.bin \
     --voice af_heart --format mp3
   ```
   Use a timeout of 600000ms (10 minutes) for long articles.
7. Verify the output file exists and report its size
8. Regenerate the FolderCast RSS feed so the new episode appears:
   ```
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8123/feed/create/articles/
   ```
   A 200 response means the feed was updated successfully.
9. Tell the user the episode is live in FolderCast at http://localhost:8123 and will appear in Pocket Casts after a pull-to-refresh

## Config
- Audio output dir: ~/Documents/podcast-tools/foldercast/library/articles/
- Model: ~/Documents/podcast-tools/kokoro-models/kokoro-v1.0.onnx
- Voices: ~/Documents/podcast-tools/kokoro-models/voices-v1.0.bin
- Voice: af_heart
- Format: mp3
