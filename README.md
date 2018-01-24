<h1 id="about">About</h1>
<p>This is Phonetoque, a tool for phonetic computation intended to serve language learning apps. What you see here is the data collection pipeline for Phonetoque.</p>
<h1 id="usage">Usage</h1>
<p>Everything is done through the <em><a href="http://manager.py">manager.py</a></em> script.</p>
<pre><code>   manager.py [-h] [--language LANGUAGE] [-i I] [-o O] [--conf CONF] script
   Options :
    --language		specify the language input and output data apply to
    --conf			which conf file to use, defaults to /scripts/script_config.yml
    -i				input file
    -o 				output file
    -h 				help
</code></pre>
<p>Available scripts are in <em>/scripts</em>. What options are required depend on the script.</p>
<h1 id="flask">Flask</h1>
<p>This project also includes a simple Flask API used to communicate with our database (currently an Mlab test instance). To run it:</p>
<pre><code>python Flask/mongo_connect.py
</code></pre>
<p>It should run on 127.0.0.1:5000 in debug mode. Make sure this is running whenever you want to run a script that interacts with the database.</p>
<h1 id="scripts">Scripts</h1>
<h2 id="scrape">Scrape</h2>
<pre><code>manager.py scrape [-h] --language LANGUAGE -i INPUT_FILE -o OUTPUT_FILE [--conf CONF]
</code></pre>
<p>Scrapes <em><a href="http://wikitionary.org">wikitionary.org</a></em> (in the appropriate language) for <a href="https://en.wikipedia.org/wiki/International_Phonetic_Alphabet">IPA</a> pronunciations of a list of words (given in input file, one per line) and writes them to output file in the following format:</p>
<pre><code>word pronunciation
word
word pronunciation pronunciation pronunciation
...
</code></pre>
<h2 id="topatgen">Topatgen</h2>
<pre><code>manager.py topatgen [-h] --language LANGUAGE -i INPUT_FILE -o OUTPUT_FILE [--conf CONF]
</code></pre>
<p>Processes pronunciation data to find pronunciations that are already broken into syllables and outputs known syllabified pronunciations in a format that is friendly to <a href="github.com/pgmmpk/pypatgen">pypatgen</a>. TODO document workflow for pypatgen</p>
<h2 id="post">Post</h2>
<pre><code>usage: post.py [-h] --language LANGUAGE -i INPUT_FILE [--conf CONF]
</code></pre>
<p>Posts word and pronunciation data to database (via the Flask API). You should have a trained syllabification dictionary for <a href="http://pyphen.org/">pyphen</a> for both your language and its IPA (see TODO above).</p>

